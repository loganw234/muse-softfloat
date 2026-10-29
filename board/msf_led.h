/* msf_led.h - onboard-LED activity indicator for board firmware.
 *
 * Owner-requested: blink the onboard LED while a firmware is
 * doing work so a row of boards shows which are running.
 * msf_led_busy() derives its phase from the 1 MHz timer
 * (250 ms half-period, ~2 Hz), so the blink rate does not
 * depend on how often work loops call it; msf_led_idle()
 * turns the LED off. Where a firmware times a region (IAS15
 * RATE blocks, bench loops), calls are placed outside the
 * timed region, next to the printing the timing already
 * excludes. No effect on any computed value, hash, or
 * protocol byte.
 *
 * Two LED wirings, both driven from one firmware image (the
 * bench has both board types, and a board type cannot be
 * detected at runtime):
 *   - Raspberry Pi Pico: plain LED on PICO_DEFAULT_LED_PIN
 *     (GP25), GPIO writes.
 *   - RP2040-Zero (the clones): one WS2812 RGB LED on GP16.
 *     Driven by a minimal PIO program below (WS2812 800 kHz
 *     timing: 1.25 us bit period split 10 state-machine
 *     cycles, 3 high for a 0 bit, 6 high for a 1 bit; GRB,
 *     MSB first; a new frame is sent only when the blink
 *     phase changes, so the line idles low and the latch
 *     gap is the inter-call time). On a Pico GP16 is an
 *     unconnected header pin, so the frames are harmless;
 *     on a Zero GP25 has no LED. If the PIO program or a
 *     state machine is unavailable the WS2812 path is
 *     silently skipped.
 *
 * Include from exactly one translation unit per firmware
 * (the state below is per-TU static).
 */
#ifndef MSF_LED_H
#define MSF_LED_H

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/gpio.h"
#include "hardware/pio.h"

#define MSF_LED_WS2812_PIN 16u
/* dim green: GRB with G=24 of 255 (full blast is painful) */
#define MSF_LED_WS2812_GRB 0x180000u

static int g_msf_led_sm = -1;      /* WS2812 state machine, -1 = none */
static int g_msf_led_ws_state = -1; /* last WS2812 output: 0/1, -1 = unsent */

static inline void msf_led_ws2812_init(void)
{
    /* Program (loaded at offset 0; jmp targets are absolute):
     *   0: out x, 1     side 0 [3]   ; low 4 cycles, next bit -> x
     *   1: jmp !x, 3    side 1 [2]   ; high 3 cycles
     *   2: jmp 0        side 1 [2]   ; 1 bit: high 3 more (6 total)
     *   3: jmp 0        side 0 [2]   ; 0 bit: low 3 more (7 total)
     * 10 SM cycles per bit at 8 MHz = 1.25 us (800 kHz). */
    const uint16_t prog[4] = {
        (uint16_t)(pio_encode_out(pio_x, 1) | pio_encode_sideset(1, 0)
                   | pio_encode_delay(3)),
        (uint16_t)(pio_encode_jmp_not_x(3) | pio_encode_sideset(1, 1)
                   | pio_encode_delay(2)),
        (uint16_t)(pio_encode_jmp(0) | pio_encode_sideset(1, 1)
                   | pio_encode_delay(2)),
        (uint16_t)(pio_encode_jmp(0) | pio_encode_sideset(1, 0)
                   | pio_encode_delay(2)),
    };
    const pio_program_t ws_prog = {
        .instructions = prog, .length = 4, .origin = 0,
    };
    pio_sm_config c;
    uint32_t hz, div_int, rem;
    int sm;

    if (!pio_can_add_program_at_offset(pio0, &ws_prog, 0)) {
        return;
    }
    sm = pio_claim_unused_sm(pio0, false);
    if (sm < 0) {
        return;
    }
    pio_add_program_at_offset(pio0, &ws_prog, 0);
    pio_gpio_init(pio0, MSF_LED_WS2812_PIN);
    pio_sm_set_consecutive_pindirs(pio0, (uint)sm, MSF_LED_WS2812_PIN, 1, true);
    c = pio_get_default_sm_config();
    sm_config_set_wrap(&c, 0, 3);
    sm_config_set_sideset(&c, 1, false, false);
    sm_config_set_sideset_pins(&c, MSF_LED_WS2812_PIN);
    sm_config_set_out_shift(&c, false, true, 24);
    sm_config_set_fifo_join(&c, PIO_FIFO_JOIN_TX);
    hz = clock_get_hz(clk_sys);
    div_int = hz / 8000000u;
    rem = hz - div_int * 8000000u;
    sm_config_set_clkdiv_int_frac(&c, (uint16_t)div_int,
                                  (uint8_t)((rem * 256u) / 8000000u));
    pio_sm_init(pio0, (uint)sm, 0, &c);
    pio_sm_set_enabled(pio0, (uint)sm, true);
    g_msf_led_sm = sm;
    g_msf_led_ws_state = -1;
}

static inline void msf_led_apply(uint on)
{
#ifdef PICO_DEFAULT_LED_PIN
    gpio_put(PICO_DEFAULT_LED_PIN, on);
#endif
    if (g_msf_led_sm >= 0 && (int)on != g_msf_led_ws_state) {
        g_msf_led_ws_state = (int)on;
        pio_sm_put_blocking(pio0, (uint)g_msf_led_sm,
                            (on ? MSF_LED_WS2812_GRB : 0u) << 8);
    }
}

static inline void msf_led_init(void)
{
#ifdef PICO_DEFAULT_LED_PIN
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
    gpio_put(PICO_DEFAULT_LED_PIN, 0);
#endif
    msf_led_ws2812_init();
    msf_led_apply(0);
}

static inline void msf_led_busy(void)
{
    msf_led_apply((uint)((time_us_64() / 250000u) & 1u));
}

static inline void msf_led_idle(void)
{
    msf_led_apply(0);
}

#endif /* MSF_LED_H */
