/* aeabi_selftest_main.c - AEABI compat validation firmware.
 *
 * Runs the full board selftest (ias15_selftest.c) once USB CDC is
 * up and prints AEABI-RESULT PASS/FAIL. The lead runs this BEFORE
 * the IAS15 demo firmware trusts any board hash: it proves the
 * AEABI comparison/arithmetic contract on silicon, the same order
 * the host proof used (shim validated before trust). Integer/hex
 * output only. */
#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "ias15_selftest.h"

int main(void)
{
    pico_unique_board_id_t id;
    unsigned long long checks = 0, fails = 0;
    int rc, i;

    stdio_init_all();
    while (!stdio_usb_connected()) {
        sleep_ms(50);
    }
    sleep_ms(200);
    pico_get_unique_board_id(&id);
    printf("MSF-AEABI-SELFTEST 1 ID ");
    for (i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
        printf("%02x", id.id[i]);
    }
    printf("\n");
    rc = msf_aeabi_selftest(1, &checks, &fails);
    printf("AEABI-RESULT %s checks=%llu failures=%llu\n",
           rc == 0 ? "PASS" : "FAIL", checks, fails);
    for (;;) {
        sleep_ms(1000);
    }
}
