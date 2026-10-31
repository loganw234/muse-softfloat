/* f16c.c - cross-check msf16_from_f32 (all 2^32 binary32 inputs, one
 * rounding mode per process) and msf32_from_f16 (all 65536 inputs)
 * against the host's F16C instructions (VCVTPS2PH imm rounding,
 * VCVTPH2PS). NaN results compared by class; flags compared exactly. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <fenv.h>
#include <immintrin.h>
#include "muse_softfloat.h"
#pragma STDC FENV_ACCESS ON

static unsigned host_flags(void){
    int f = fetestexcept(FE_ALL_EXCEPT); unsigned m = 0;
    if (f & FE_INVALID) m |= MSF_FLAG_INVALID;
    if (f & FE_DIVBYZERO) m |= MSF_FLAG_DIVISION_BY_ZERO;
    if (f & FE_OVERFLOW) m |= MSF_FLAG_OVERFLOW;
    if (f & FE_UNDERFLOW) m |= MSF_FLAG_UNDERFLOW;
    if (f & FE_INEXACT) m |= MSF_FLAG_INEXACT;
    return m;
}
static float u2f(uint32_t u){ float f; memcpy(&f,&u,4); return f; }
static uint32_t f2u(float f){ uint32_t u; memcpy(&u,&f,4); return u; }
static int isnan16(uint16_t u){ return ((u>>10)&0x1f)==0x1f && (u&0x3ff); }
static int isnan32(uint32_t u){ return ((u>>23)&0xff)==0xff && (u&0x7fffff); }

/* imm8: 0 nearest, 1 down (toward -inf), 2 up (toward +inf), 3 truncate */
static inline uint16_t cvt(float f, int mode){
    switch (mode) {
    case 0: return (uint16_t)_cvtss_sh(f, 0);
    case 1: return (uint16_t)_cvtss_sh(f, 3);   /* tz */
    case 2: return (uint16_t)_cvtss_sh(f, 2);   /* tp */
    default: return (uint16_t)_cvtss_sh(f, 1);  /* tn */
    }
}
static const char *mode_names[4] = { "te", "tz", "tp", "tn" };

int main(int argc, char **argv){
    if (argc < 4) { fprintf(stderr, "usage: f16c mode start end\n"); return 2; }
    int mode = atoi(argv[1]); uint64_t start = strtoull(argv[2],0,0), end = strtoull(argv[3],0,0);
    long bad = 0, n = 0, shown = 0;
    volatile float vf;
    if (mode == 0) {
        /* exact widening: all 65536 binary16 encodings, msf32_from_f16 vs VCVTPH2PS */
        long wbad = 0;
        for (uint32_t h = 0; h < 65536u; h++) {
            msf_flags_t mf = 0; feclearexcept(FE_ALL_EXCEPT);
            vf = _cvtsh_ss((unsigned short)h); unsigned hf = host_flags(); uint32_t hr = f2u(vf);
            uint32_t mr = msf32_from_f16((msf16_t)h, MSF_ROUND_TIES_TO_EVEN, &mf);
            int ok = (isnan32(hr) || isnan32(mr)) ? (isnan32(hr) && isnan32(mr) && hf == mf) : (hr == mr && hf == mf);
            if (!ok) { if (wbad < 8) printf("  MISMATCH widen h=%04x host=%08x/%02x msf=%08x/%02x\n", h, hr, hf, mr, mf); wbad++; }
        }
        printf("f16->f32 widen: n=65536 mismatches=%ld\n", wbad);
        bad += wbad;
    }
    for (uint64_t a = start; a < end; a++) {
        msf_flags_t mf = 0; feclearexcept(FE_ALL_EXCEPT);
        uint16_t hr = cvt(u2f((uint32_t)a), mode); unsigned hf = host_flags();
        uint16_t mr = msf16_from_f32((msf32_t)a, (msf_rounding_t)mode, &mf);
        int ok = (isnan16(hr) || isnan16(mr)) ? (isnan16(hr) && isnan16(mr) && hf == mf) : (hr == mr && hf == mf);
        n++;
        if (!ok) { if (shown < 8) { printf("  MISMATCH narrow %s a=%08x host=%04x/%02x msf=%04x/%02x\n", mode_names[mode], (unsigned)a, hr, hf, mr, mf); shown++; } bad++; }
    }
    printf("f32->f16 narrow mode=%s range=[%#llx,%#llx) n=%ld mismatches=%ld -> %s\n", mode_names[mode], (unsigned long long)start, (unsigned long long)end, n, bad, bad ? "MISMATCHES" : "ALL AGREE");
    return bad ? 1 : 0;
}
