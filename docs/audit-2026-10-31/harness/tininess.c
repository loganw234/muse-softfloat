/* Directed probe: does the host SSE unit detect tininess before or after
 * rounding, and does msf64_mul agree? Product (1-2^-27)*2^-511 x
 * (1+2^-27)*2^-511 = (1-2^-54)*2^-1022: with an unbounded exponent range it
 * rounds (ties-to-even) to 2^-1022 exactly, so it is NOT tiny after
 * rounding but IS tiny before rounding. Delivered result 2^-1022, inexact. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <fenv.h>
#include <math.h>
#include "muse_softfloat.h"
#pragma STDC FENV_ACCESS ON
static uint64_t d2u(double d){ uint64_t u; memcpy(&u,&d,8); return u; }
int main(void){
    volatile double a = ldexp(1.0 - ldexp(1.0,-27), -511);
    volatile double b = ldexp(1.0 + ldexp(1.0,-27), -511);
    const char *mn[4] = {"te","tz","tp","tn"}; int hm[4] = {FE_TONEAREST, FE_TOWARDZERO, FE_UPWARD, FE_DOWNWARD};
    for (int m = 0; m < 4; m++) {
        fesetround(hm[m]); feclearexcept(FE_ALL_EXCEPT);
        volatile double r = a * b;
        int f = fetestexcept(FE_ALL_EXCEPT);
        msf_flags_t mf = 0; uint64_t mr = msf64_mul(d2u(a), d2u(b), (msf_rounding_t)m, &mf);
        printf("%s host=%016llx underflow=%d inexact=%d | msf=%016llx underflow=%d inexact=%d\n", mn[m],
               (unsigned long long)d2u(r), (f & FE_UNDERFLOW)!=0, (f & FE_INEXACT)!=0,
               (unsigned long long)mr, (mf & MSF_FLAG_UNDERFLOW)!=0, (mf & MSF_FLAG_INEXACT)!=0);
    }
    /* float version: (1-2^-12)*2^-63 x (1+2^-12)*2^-63 = (1-2^-24)*2^-126 */
    volatile float fa = ldexpf(1.0f - ldexpf(1.0f,-12), -63), fb = ldexpf(1.0f + ldexpf(1.0f,-12), -63);
    fesetround(FE_TONEAREST); feclearexcept(FE_ALL_EXCEPT);
    volatile float fr = fa * fb; int f = fetestexcept(FE_ALL_EXCEPT);
    uint32_t ua, ub; memcpy(&ua,(const void*)&fa,4); memcpy(&ub,(const void*)&fb,4); uint32_t ur; memcpy(&ur,(const void*)&fr,4);
    msf_flags_t mf = 0; uint32_t mr = msf32_mul(ua, ub, MSF_ROUND_TIES_TO_EVEN, &mf);
    printf("f32 te host=%08x underflow=%d inexact=%d | msf=%08x underflow=%d inexact=%d\n", ur, (f&FE_UNDERFLOW)!=0, (f&FE_INEXACT)!=0, mr, (mf&MSF_FLAG_UNDERFLOW)!=0, (mf&MSF_FLAG_INEXACT)!=0);
    return 0;
}
