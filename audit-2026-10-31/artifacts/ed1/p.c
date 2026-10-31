#include <stdio.h>
#include <stdint.h>
#include "muse_softfloat.h"
#include "softfloat.h"
int main(void){
    msf_flags_t fl;
    uint64_t snan_neg = 0xFFF0000000000001ull;   /* -sNaN binary64, payload 1 (vanishes when narrowed to binary32) */
    uint64_t qnan_neg = 0xFFF8000000000001ull;   /* -qNaN binary64 */
    fl=0; uint32_t r1 = msf32_from_f64(snan_neg, MSF_ROUND_TIES_TO_EVEN, &fl); printf("msf32_from_f64(-sNaN 0xFFF0000000000001) = %08x flags=%02x\n", r1, fl);
    fl=0; uint32_t r2 = msf32_from_f64(qnan_neg, MSF_ROUND_TIES_TO_EVEN, &fl); printf("msf32_from_f64(-qNaN 0xFFF8000000000001) = %08x flags=%02x\n", r2, fl);
    softfloat_exceptionFlags=0; softfloat_roundingMode=softfloat_round_near_even; float64_t a; a.v=snan_neg; float32_t b=f64_to_f32(a); printf("Berkeley f64_to_f32(-sNaN)               = %08x bflags=%02x\n", b.v, softfloat_exceptionFlags);
    softfloat_exceptionFlags=0; a.v=qnan_neg; b=f64_to_f32(a); printf("Berkeley f64_to_f32(-qNaN)               = %08x bflags=%02x\n", b.v, softfloat_exceptionFlags);
    return 0; }
