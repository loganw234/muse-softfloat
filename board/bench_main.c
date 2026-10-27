/* bench_main.c - benchmark skeleton (SF-0 Section 6 item 9).
 *
 * Placement/clock-labelled cycle and size reporting for the P0
 * exemplar operations plus the SDK-harness baselines (bootrom via
 * the default pico flavour, libgcc via the compiler flavour, chosen
 * at build time by MSF_BENCH_FLAVOUR). SKELETON ONLY: no performance
 * claim is made from these numbers (SF-0 Sections 5.1, 8).
 * Cortex-M0+ has no cycle counter; cycles are derived from the
 * microsecond timer and the measured system clock.
 */
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "hardware/clocks.h"
#include "../include/muse_softfloat.h"
#include "../src/msf_internal.h"

#ifndef MSF_FLAVOUR_NAME
#define MSF_FLAVOUR_NAME "pico(default: ROM-routed)"
#endif

#define ITERS 200000u

static volatile uint64_t g_sink = 0;

static void report(const char *name, uint32_t iters, uint64_t us, uint32_t hz)
{
    uint64_t ns_per = (us * 1000u) / iters;
    uint64_t cyc_x100 = (us * (uint64_t)hz) / (iters * 10000u);
    printf("BENCH %s iters=%lu total_us=%llu ns_per_op=%llu cycles_per_op_x100=%llu\n",
           name, (unsigned long)iters, (unsigned long long)us,
           (unsigned long long)ns_per, (unsigned long long)cyc_x100);
}

#define BENCH(name, body) do { \
    uint32_t i_; \
    uint64_t t0_ = time_us_64(); \
    for (i_ = 0; i_ < ITERS; i_++) { body; } \
    report(name, ITERS, time_us_64() - t0_, hz); \
} while (0)

int main(void)
{
    pico_unique_board_id_t id;
    uint32_t hz;
    msf_u128_t sig = msf_u128_from_u64(0x123456789abcdef0ULL);
    volatile float fa = 1.5f, fb = 2.25f;
    volatile double da = 1.5, db = 2.25;

    stdio_init_all();
    while (!stdio_usb_connected()) {
        sleep_ms(50);
    }
    sleep_ms(200);
    hz = clock_get_hz(clk_sys);
    pico_get_unique_board_id(&id);
    printf("MSF-BENCH 1 ID ");
    for (int i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
        printf("%02x", id.id[i]);
    }
    printf(" flavour=%s clk_sys_hz=%lu placement=flash(xip,cached) clock=default\n",
           MSF_FLAVOUR_NAME, (unsigned long)hz);
    printf("note: skeleton only - no performance claim (SF-0 6 item 9)\n");

    BENCH("msf16_class", g_sink += (uint64_t)msf16_class((msf16_t)i_));
    BENCH("msf32_is_signaling", g_sink += (uint64_t)msf32_is_signaling((msf32_t)(i_ * 2654435761u)));
    BENCH("msf64_copy_sign", g_sink += msf64_copy_sign((msf64_t)i_, (msf64_t)(i_ << 1)));
    BENCH("msf_pack_f64(exemplar)", {
        msf_flags_t fl = 0;
        g_sink += msf_pack_f64(0, -60 + (int32_t)(i_ & 127u), sig, 1,
                               MSF_IROUND_TIES_TO_EVEN, &fl);
        g_sink += fl;
    });
    BENCH("sdk-flavour float add (baseline)", fa = fa + fb);
    BENCH("sdk-flavour double add (baseline)", da = da + db);
    g_sink += (uint64_t)(fa == fa) + (uint64_t)(da == db);
    printf("BENCH-DONE sink=%016llx\n", (unsigned long long)g_sink);
    for (;;) {
        sleep_ms(1000);
    }
}
