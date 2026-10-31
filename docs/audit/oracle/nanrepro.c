#include <stdio.h>
#include "muse_softfloat.h"
int main(void) {
    msf_flags_t f; unsigned long long r;
    f = 0; r = msf16_from_f32(0xff800001u, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf16_from_f32(0xff800001 -sNaN payload 1)           -> %04llx flags=%02x\n", r, f);
    f = 0; r = msf16_from_f32(0xffc00001u, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf16_from_f32(0xffc00001 -qNaN payload 1)           -> %04llx flags=%02x\n", r, f);
    f = 0; r = msf32_from_f64(0xfff0000000000001ull, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf32_from_f64(0xfff0000000000001 -sNaN payload 1)   -> %08llx flags=%02x\n", r, f);
    f = 0; r = msf32_from_f64(0xfff8000000000001ull, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf32_from_f64(0xfff8000000000001 -qNaN payload 1)   -> %08llx flags=%02x\n", r, f);
    f = 0; r = msf32_from_f64(0xfff0000020000000ull, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf32_from_f64(0xfff0000020000000 -sNaN payload 2^29) -> %08llx flags=%02x\n", r, f);
    f = 0; r = msf16_add_f32_f32(0xff800001u, 0x3f800000u, MSF_ROUND_TIES_TO_EVEN, &f); printf("msf16_add_f32_f32(-sNaN payload 1, 1.0)             -> %04llx flags=%02x\n", r, f);
    return 0;
}
