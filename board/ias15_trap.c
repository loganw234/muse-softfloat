/* ias15_trap.c - board implementation of the compat trap sink.
 * A wrapped binary reaching an unimplemented libm name has left
 * the proven surface: name it on CDC and stop, never approximate
 * (SF-0 Sec.11). Linked by every firmware target that links
 * compat/msf_aeabi.c. */
#include <stdio.h>
#include "pico/stdlib.h"
#include "../compat/msf_aeabi.h"

void msf_aeabi_trap(const char *name)
{
    printf("MSF-TRAP %s\n", name);
    for (;;) {
        sleep_ms(1000);
    }
}
