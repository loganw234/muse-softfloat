#include <stdio.h>
#include "muse_softfloat.h"
int main(void) {
    /* 1 + 1.5*2^-23: exactly halfway between 1+2^-23 and 1+2^-22 -> te gives 3f800002, a tie */
    int rms[] = {0, 1, 2, 3, 4, 5, 6, 7, 100, -1};
    for (int i = 0; i < 10; i++) {
        msf_flags_t f = 0;
        msf32_t r = msf32_add(0x3f800000u, 0x34400000u, (msf_rounding_t)rms[i], &f);
        msf_flags_t f2 = 0;
        msf32_t r2 = msf32_add(0x3f800000u, 0x34600000u, (msf_rounding_t)rms[i], &f2); /* 1 + 1.75*2^-23: above the tie */
        printf("rm=%4d  tie-case=%08x flags=%02x   above-tie=%08x\n", rms[i], r, f, r2);
    }
    return 0;
}
