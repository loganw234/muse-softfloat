/* msf_led.h - onboard-LED activity indicator for board firmware.
 *
 * Owner-requested: blink the onboard LED while a firmware is
 * doing work so a row of boards shows which are running.
 * msf_led_busy() derives its phase from the 1 MHz timer
 * (250 ms half-period, ~2 Hz), so the blink rate does not
 * depend on how often work loops call it; msf_led_idle()
 * turns the LED off. GPIO writes only - no effect on any
 * computed value, hash, or protocol byte. Where a firmware
 * times a region (IAS15 RATE blocks, bench loops), calls are
 * placed outside the timed region, next to the printing the
 * timing already excludes. On a board definition without
 * PICO_DEFAULT_LED_PIN every call is a no-op.
 */
#ifndef MSF_LED_H
#define MSF_LED_H

#include "pico/stdlib.h"
#include "hardware/gpio.h"

static inline void msf_led_init(void)
{
#ifdef PICO_DEFAULT_LED_PIN
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
    gpio_put(PICO_DEFAULT_LED_PIN, 0);
#endif
}

static inline void msf_led_busy(void)
{
#ifdef PICO_DEFAULT_LED_PIN
    gpio_put(PICO_DEFAULT_LED_PIN,
             (time_us_64() / 250000u) & 1u);
#endif
}

static inline void msf_led_idle(void)
{
#ifdef PICO_DEFAULT_LED_PIN
    gpio_put(PICO_DEFAULT_LED_PIN, 0);
#endif
}

#endif /* MSF_LED_H */
