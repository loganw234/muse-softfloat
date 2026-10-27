/* hello_main.c - interposition hello (SF-0 Section 6 item 7).
 *
 * Proves one --wrap route end-to-end on silicon: compiler calls to
 * copysignf/copysign resolve to compat/msf_wrap.c over the gated
 * core, and per-core wrapper state obeys the SF-0 3.4 contract
 * (isolated between cores; shared between thread and IRQ execution
 * on the same core; save/restore round-trips through core flag ops).
 */
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "pico/unique_id.h"
#include "../compat/msf_wrap.h"

static volatile uint32_t g_irq_hits = 0;
static int g_fail = 0;

#define CHECK(cond) do { \
    printf("hello %s: %s\n", (cond) ? "PASS" : "FAIL", #cond); \
    if (!(cond)) { g_fail++; } \
} while (0)

static uint32_t bits_of_f(float x) { uint32_t u; memcpy(&u, &x, 4); return u; }
static uint64_t bits_of_d(double x) { uint64_t u; memcpy(&u, &x, 8); return u; }

/* runtime values, so calls cannot be constant-folded away */
static float in_f(uint32_t bits) { float f; memcpy(&f, &bits, 4); return f; }
static double in_d(uint64_t bits) { double d; memcpy(&d, &bits, 8); return d; }

static bool irq_cb(repeating_timer_t *t)
{
    (void)t;
    g_irq_hits++;
    msf_wrap_selftest_raise(MSF_FLAG_DIVISION_BY_ZERO);
    return true;
}

static void core1_main(void)
{
    uint32_t before = msf_wrap_state()->flags;
    msf_wrap_selftest_raise(MSF_FLAG_OVERFLOW);
    uint32_t after = msf_wrap_state()->flags;
    multicore_fifo_push_blocking(before);
    multicore_fifo_push_blocking(after);
    for (;;) {
        tight_loop_contents();
    }
}

int main(void)
{
    pico_unique_board_id_t id;
    repeating_timer_t timer;
    volatile float sink_f = 0.0f;
    uint32_t core1_before, core1_after, mine_after_core1;
    msf_saved_flags_t saved;

    stdio_init_all();
    while (!stdio_usb_connected()) {
        sleep_ms(50);
    }
    sleep_ms(200);
    pico_get_unique_board_id(&id);
    printf("MSF-HELLO 1 ID ");
    for (int i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
        printf("%02x", id.id[i]);
    }
    printf(" core%u\n", get_core_num());

    /* --wrap resolution + core bit-exactness through C arithmetic types */
    CHECK(bits_of_f(copysignf(in_f(0x3fc00000u), in_f(0xbf800000u))) == 0xbfc00000u);
    CHECK(bits_of_f(copysignf(in_f(0xffc00001u), in_f(0x00000000u))) == 0x7fc00001u);
    CHECK(bits_of_d(copysign(in_d(0x3ff8000000000000ULL),
                             in_d(0xbff0000000000000ULL))) == 0xbff8000000000000ULL);
    CHECK(bits_of_d(copysign(in_d(0xfff0000000000001ULL),
                             in_d(0x0000000000000000ULL))) == 0x7ff0000000000001ULL);

    /* cross-core isolation */
    msf_wrap_selftest_raise(MSF_FLAG_INEXACT);
    multicore_launch_core1(core1_main);
    core1_before = multicore_fifo_pop_blocking();
    core1_after = multicore_fifo_pop_blocking();
    mine_after_core1 = msf_wrap_state()->flags;
    CHECK(core1_before == 0u);
    CHECK(core1_after == MSF_FLAG_OVERFLOW);
    CHECK(mine_after_core1 == MSF_FLAG_INEXACT);

    /* same-core IRQ interleaving: the contract says state is shared
     * on one core (observed and reported, never hidden). */
    add_repeating_timer_us(2000, irq_cb, NULL, &timer);
    {
        uint32_t i;
        for (i = 0; i < 200000u && g_irq_hits == 0u; i++) {
            sink_f += copysignf(in_f(0x3f800000u + i), in_f(0xbf800000u));
        }
    }
    cancel_repeating_timer(&timer);
    printf("hello note: irq_hits=%lu sink=%08lx flags=%02lx\n",
           (unsigned long)g_irq_hits, (unsigned long)bits_of_f(sink_f),
           (unsigned long)msf_wrap_state()->flags);
    CHECK(g_irq_hits > 0u);
    CHECK((msf_wrap_state()->flags & MSF_FLAG_DIVISION_BY_ZERO) != 0u);

    /* save/restore round-trip through the core flag operations */
    saved = msf_save_all_flags(&msf_wrap_state()->flags);
    msf_lower_flags(&msf_wrap_state()->flags, MSF_FLAGS_ALL);
    CHECK(msf_wrap_state()->flags == 0u);
    CHECK(msf_test_saved_flags(saved, MSF_FLAG_INEXACT) == 1);
    msf_restore_flags(&msf_wrap_state()->flags, saved, MSF_FLAGS_ALL);
    CHECK((msf_wrap_state()->flags & MSF_FLAG_INEXACT) != 0u);

    printf("HELLO-RESULT %s failures=%d\n", g_fail == 0 ? "PASS" : "FAIL", g_fail);
    for (;;) {
        sleep_ms(1000);
    }
}
