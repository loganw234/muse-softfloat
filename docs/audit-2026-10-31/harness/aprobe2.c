#include <stdio.h>
#include "muse_softfloat.h"
int main(void){
    msf_flags_t f; unsigned r;
    f = 0; r = msf16_from_f32(0xff800001u, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf16_from_f32(ff800001 -sNaN, payload lost) -> %04x flags=%02x\n", r, (unsigned)f);
    f = 0; r = msf16_from_f32(0xff802000u, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf16_from_f32(ff802000 -sNaN, payload kept) -> %04x flags=%02x\n", r, (unsigned)f);
    f = 0; r = msf32_from_f64(0xfff0000000000001ull, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf32_from_f64(fff0000000000001 -sNaN) -> %08x flags=%02x\n", r, (unsigned)f);
    f = 0; r = msf16_from_f32(0xffc00001u, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf16_from_f32(ffc00001 -qNaN) -> %04x flags=%02x\n", r, (unsigned)f);
    return 0; }
