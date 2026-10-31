/* hostdiff.c - independent differential check of muse-softfloat's
 * binary32/binary64 core against the host SSE2/AVX FPU inside the
 * SF-0 4.2 envelope (x86-64, FLT_EVAL_METHOD 0, -ffp-contract=off,
 * four hardware modes, NaNs compared by class only). Flags compared
 * exactly. Written by the auditor, independent of the project's own
 * generators. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <fenv.h>
#include <math.h>
#include <stdlib.h>
#include "muse_softfloat.h"
#pragma STDC FENV_ACCESS ON

static uint64_t rng = 0x9E3779B97F4A7C15ull;
static uint64_t r64(void){ rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng * 0x2545F4914F6CDD1Dull; }
static const int host_modes[4] = { FE_TONEAREST, FE_TOWARDZERO, FE_UPWARD, FE_DOWNWARD };
static const int msf_modes[4] = { MSF_ROUND_TIES_TO_EVEN, MSF_ROUND_TOWARD_ZERO, MSF_ROUND_TOWARD_POSITIVE, MSF_ROUND_TOWARD_NEGATIVE };
static const char *mode_names[4] = { "te", "tz", "tp", "tn" };

static unsigned host_flags(void){
    int f = fetestexcept(FE_ALL_EXCEPT); unsigned m = 0;
    if (f & FE_INVALID) m |= MSF_FLAG_INVALID;
    if (f & FE_DIVBYZERO) m |= MSF_FLAG_DIVISION_BY_ZERO;
    if (f & FE_OVERFLOW) m |= MSF_FLAG_OVERFLOW;
    if (f & FE_UNDERFLOW) m |= MSF_FLAG_UNDERFLOW;
    if (f & FE_INEXACT) m |= MSF_FLAG_INEXACT;
    return m;
}
static uint64_t d2u(double d){ uint64_t u; memcpy(&u,&d,8); return u; }
static double u2d(uint64_t u){ double d; memcpy(&d,&u,8); return d; }
static uint32_t f2u(float f){ uint32_t u; memcpy(&u,&f,4); return u; }
static float u2f(uint32_t u){ float f; memcpy(&f,&u,4); return f; }
static int isnan64(uint64_t u){ return ((u>>52)&0x7ff)==0x7ff && (u&0xfffffffffffffull); }
static int isnan32(uint32_t u){ return ((u>>23)&0xff)==0xff && (u&0x7fffff); }

static const uint64_t spec64[] = { 0, 0x8000000000000000ull, 0x7ff0000000000000ull, 0xfff0000000000000ull,
  0x7ff8000000000000ull, 0xfff8000000000000ull, 0x7ff0000000000001ull, 0x7ff4000000000000ull,
  0x3ff0000000000000ull, 0xbff0000000000000ull, 0x4000000000000000ull, 0x3fe0000000000000ull,
  0x7fefffffffffffffull, 0xffefffffffffffffull, 0x0010000000000000ull, 0x8010000000000000ull,
  0x0000000000000001ull, 0x8000000000000001ull, 0x000fffffffffffffull, 0x3ff8000000000000ull,
  0x4330000000000000ull, 0x43e0000000000000ull, 0xc3e0000000000000ull, 0x41e0000000000000ull,
  0x41dfffffffc00000ull, 0xc1e0000000000000ull, 0x43f0000000000000ull, 0x3fdfffffffffffffull, 0x3fe0000000000001ull };
static const uint32_t spec32[] = { 0, 0x80000000u, 0x7f800000u, 0xff800000u, 0x7fc00000u, 0xffc00000u, 0x7f800001u, 0x7fa00000u,
  0x3f800000u, 0xbf800000u, 0x40000000u, 0x3f000000u, 0x7f7fffffu, 0xff7fffffu, 0x00800000u, 0x80800000u, 0x00000001u, 0x80000001u,
  0x007fffffu, 0x3fc00000u, 0x4b000000u, 0x5f000000u, 0xdf000000u, 0x4f000000u, 0x4effffffu, 0xcf000000u, 0x5f800000u, 0x3effffffu, 0x3f000001u };

static uint64_t gen64(int cls, uint64_t rel){
    uint64_t r = r64();
    switch (cls & 3) {
    case 0: return r;
    case 1: { uint64_t e = (r >> 52) & 0x7ff; uint64_t sel = r64() % 5;
              if (sel==0) e = (r64() % 64);            /* tiny / subnormal */
              else if (sel==1) e = 2046 - (r64() % 64); /* near overflow */
              else if (sel==2) e = 1023 + (int)(r64()%120) - 60; /* near 1 */
              else if (sel==3) e = 1023 + 52 + (int)(r64()%16) - 8; /* integer boundary 2^52 */
              else e = 1023 + 31 + (int)(r64()%8) - 4; /* near 2^31 */
              return (r & 0x800fffffffffffffull) | (e << 52); }
    case 2: return spec64[r64() % (sizeof spec64 / sizeof spec64[0])];
    default: { int64_t e = (int64_t)((rel >> 52) & 0x7ff) + (int64_t)(r64() % 7) - 3;
              if (e < 0) e = 0; if (e > 2047) e = 2047;
              return (r & 0x800fffffffffffffull) | ((uint64_t)e << 52); }
    }
}
static uint32_t gen32(int cls, uint32_t rel){
    uint32_t r = (uint32_t)r64();
    switch (cls & 3) {
    case 0: return r;
    case 1: { uint32_t e = (r >> 23) & 0xff; uint32_t sel = r64() % 5;
              if (sel==0) e = (r64() % 16);
              else if (sel==1) e = 254 - (r64() % 16);
              else if (sel==2) e = 127 + (int)(r64()%40) - 20;
              else if (sel==3) e = 127 + 23 + (int)(r64()%8) - 4;
              else e = 127 + 31 + (int)(r64()%8) - 4;
              return (r & 0x807fffffu) | (e << 23); }
    case 2: return spec32[r64() % (sizeof spec32 / sizeof spec32[0])];
    default: { int e = (int)((rel >> 23) & 0xff) + (int)(r64() % 7) - 3;
              if (e < 0) e = 0; if (e > 255) e = 255;
              return (r & 0x807fffffu) | ((uint32_t)e << 23); }
    }
}

static long total_cases = 0, total_bad = 0;
static void report(const char *op, const char *mode, long n, long bad, long nanbits_diff){
    total_cases += n; total_bad += bad;
    printf("%-28s %s n=%ld mismatches=%ld%s\n", op, mode, n, bad,
           nanbits_diff ? "" : "");
    fflush(stdout);
}
#define SHOW_LIMIT 6
#define MISMATCH64(op, mode, a, b, c, hr, hf, mr, mf) do { if (bad < SHOW_LIMIT) printf("  MISMATCH %s %s a=%016llx b=%016llx c=%016llx host=%016llx/%02x msf=%016llx/%02x\n", op, mode, (unsigned long long)(a),(unsigned long long)(b),(unsigned long long)(c),(unsigned long long)(hr),(unsigned)(hf),(unsigned long long)(mr),(unsigned)(mf)); bad++; } while(0)
#define MISMATCH32(op, mode, a, b, c, hr, hf, mr, mf) do { if (bad < SHOW_LIMIT) printf("  MISMATCH %s %s a=%08x b=%08x c=%08x host=%08x/%02x msf=%08x/%02x\n", op, mode, (unsigned)(a),(unsigned)(b),(unsigned)(c),(unsigned)(hr),(unsigned)(hf),(unsigned)(mr),(unsigned)(mf)); bad++; } while(0)

static int same64(uint64_t h, uint64_t m){ if (isnan64(h) || isnan64(m)) return isnan64(h) && isnan64(m); return h == m; }
static int same32(uint32_t h, uint32_t m){ if (isnan32(h) || isnan32(m)) return isnan32(h) && isnan32(m); return h == m; }

typedef enum { OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_SQRT, OP_FMA, OP_RINT, OP_D2F, OP_F2D, OP_I32, OP_U32, OP_I64, OP_U64, OP_TOI32, OP_TOI64, OP_TOU32, OP_TOU64, OP_QLT, OP_QEQ, OP_SLT, OP_SLE } opk;
static const char *opname[] = {"add","sub","mul","div","sqrt","fma","round_to_integral_exact","from_f64(narrow)","from_f32(widen)","from_i32","from_u32","from_i64","from_u64","to_i32_exact_toward_zero","to_i64_exact_toward_zero","to_u32_exact_toward_zero","to_u64_exact_toward_zero","compare_quiet_less","compare_quiet_equal","compare_signaling_less","compare_signaling_less_equal"};

static void run64(opk op, int mi, long n){
    long bad = 0, i;
    volatile double va, vb, vc; volatile double vr; volatile float vrf; volatile int32_t vi32; volatile int64_t vi64; volatile uint32_t vu32; volatile uint64_t vu64; volatile int vp;
    volatile int32_t si32; volatile int64_t si64; volatile uint32_t su32; volatile uint64_t su64;
    char name[64]; snprintf(name, sizeof name, "f64 %s", opname[op]);
    for (i = 0; i < n; i++) {
        int cls = (int)(i & 3);
        uint64_t a = gen64(cls, 0), b = gen64((int)(r64()&3), a), c;
        msf_flags_t mf = 0; unsigned hf; uint64_t hr = 0, mr = 0; int rm = msf_modes[mi];
        fesetround(host_modes[mi]);
        feclearexcept(FE_ALL_EXCEPT);
        switch (op) {
        case OP_ADD: va=u2d(a); vb=u2d(b); vr = va + vb; hf=host_flags(); hr=d2u(vr); mr = msf64_add(a,b,rm,&mf); break;
        case OP_SUB: va=u2d(a); vb=u2d(b); vr = va - vb; hf=host_flags(); hr=d2u(vr); mr = msf64_sub(a,b,rm,&mf); break;
        case OP_MUL: va=u2d(a); vb=u2d(b); vr = va * vb; hf=host_flags(); hr=d2u(vr); mr = msf64_mul(a,b,rm,&mf); break;
        case OP_DIV: va=u2d(a); vb=u2d(b); vr = va / vb; hf=host_flags(); hr=d2u(vr); mr = msf64_div(a,b,rm,&mf); break;
        case OP_SQRT: va=u2d(a); vr = __builtin_sqrt(va); hf=host_flags(); hr=d2u(vr); mr = msf64_sqrt(a,rm,&mf); b=0; break;
        case OP_FMA: { uint64_t pe = ((a>>52)&0x7ff) + ((b>>52)&0x7ff); if (pe > 1023) pe -= 1023; else pe = 1; if (pe > 2046) pe = 2046;
                       c = gen64((int)(r64()&3), (pe<<52)); va=u2d(a); vb=u2d(b); vc=u2d(c); vr = __builtin_fma(va,vb,vc); hf=host_flags(); hr=d2u(vr); mr = msf64_fma(a,b,c,rm,&mf);
                       if (!(same64(hr,mr) && hf==mf)) { MISMATCH64(name, mode_names[mi], a,b,c,hr,hf,mr,mf); } continue; }
        case OP_RINT: va=u2d(a); vr = __builtin_rint(va); hf=host_flags(); hr=d2u(vr); mr = msf64_round_to_integral_exact(a,rm,&mf); b=0; break;
        case OP_D2F: va=u2d(a); vrf = (float)va; hf=host_flags(); hr=f2u(vrf); mr = msf32_from_f64(a,rm,&mf); b=0;
                     if (!(same32((uint32_t)hr,(uint32_t)mr) && hf==mf)) { MISMATCH64(name, mode_names[mi], a,0,0,hr,hf,mr,mf); } continue;
        case OP_I32: si32=(int32_t)a; vr=(double)si32; hf=host_flags(); hr=d2u(vr); mr=msf64_from_i32((int32_t)a,rm,&mf); b=0; break;
        case OP_U32: su32=(uint32_t)a; vr=(double)su32; hf=host_flags(); hr=d2u(vr); mr=msf64_from_u32((uint32_t)a,rm,&mf); b=0; break;
        case OP_I64: si64=(int64_t)a; vr=(double)si64; hf=host_flags(); hr=d2u(vr); mr=msf64_from_i64((int64_t)a,rm,&mf); b=0; break;
        case OP_U64: su64=a; vr=(double)su64; hf=host_flags(); hr=d2u(vr); mr=msf64_from_u64(a,rm,&mf); b=0; break;
        case OP_TOI32: { va=u2d(a); vi32=(int32_t)va; hf=host_flags(); int32_t m=msf64_to_i32_exact_toward_zero(a,&mf);
                         int ok = (hf & MSF_FLAG_INVALID) ? ((mf & MSF_FLAG_INVALID) != 0) : (vi32==m && hf==mf);
                         if (!ok) { MISMATCH64(name, mode_names[mi], a,0,0,(uint64_t)(uint32_t)vi32,hf,(uint64_t)(uint32_t)m,mf); } continue; }
        case OP_TOI64: { va=u2d(a); vi64=(int64_t)va; hf=host_flags(); int64_t m=msf64_to_i64_exact_toward_zero(a,&mf);
                         int ok = (hf & MSF_FLAG_INVALID) ? ((mf & MSF_FLAG_INVALID) != 0) : (vi64==m && hf==mf);
                         if (!ok) { MISMATCH64(name, mode_names[mi], a,0,0,(uint64_t)vi64,hf,(uint64_t)m,mf); } continue; }
        case OP_TOU32: { va=u2d(a); if (!(va > -1.0 && va < 4294967296.0)) continue; vu32=(uint32_t)va; hf=host_flags(); uint32_t m=msf64_to_u32_exact_toward_zero(a,&mf);
                         if (!(vu32==m && hf==mf)) { MISMATCH64(name, mode_names[mi], a,0,0,(uint64_t)vu32,hf,(uint64_t)m,mf); } continue; }
        case OP_TOU64: { va=u2d(a); if (!(va > -1.0 && va < 18446744073709551616.0)) continue; vu64=(uint64_t)va; hf=host_flags(); uint64_t m=msf64_to_u64_exact_toward_zero(a,&mf);
                         if (!(vu64==m && hf==mf)) { MISMATCH64(name, mode_names[mi], a,0,0,vu64,hf,m,mf); } continue; }
        case OP_QLT: va=u2d(a); vb=u2d(b); vp = __builtin_isless(va,vb); hf=host_flags(); hr=(uint64_t)vp; mr=(uint64_t)msf64_compare_quiet_less(a,b,&mf); if (!(hr==mr && hf==mf)) MISMATCH64(name, mode_names[mi], a,b,0,hr,hf,mr,mf); continue;
        case OP_QEQ: va=u2d(a); vb=u2d(b); vp = (va==vb); hf=host_flags(); hr=(uint64_t)vp; mr=(uint64_t)msf64_compare_quiet_equal(a,b,&mf); if (!(hr==mr && hf==mf)) MISMATCH64(name, mode_names[mi], a,b,0,hr,hf,mr,mf); continue;
        case OP_SLT: va=u2d(a); vb=u2d(b); vp = (va<vb); hf=host_flags(); hr=(uint64_t)vp; mr=(uint64_t)msf64_compare_signaling_less(a,b,&mf); if (!(hr==mr && hf==mf)) MISMATCH64(name, mode_names[mi], a,b,0,hr,hf,mr,mf); continue;
        case OP_SLE: va=u2d(a); vb=u2d(b); vp = (va<=vb); hf=host_flags(); hr=(uint64_t)vp; mr=(uint64_t)msf64_compare_signaling_less_equal(a,b,&mf); if (!(hr==mr && hf==mf)) MISMATCH64(name, mode_names[mi], a,b,0,hr,hf,mr,mf); continue;
        default: continue;
        }
        if (!(same64(hr,mr) && hf==mf)) { MISMATCH64(name, mode_names[mi], a,b,0,hr,hf,mr,mf); }
    }
    report(name, mode_names[mi], n, bad, 0);
}

static void run32(opk op, int mi, long n){
    long bad = 0, i;
    volatile float va, vb, vc; volatile float vr; volatile double vrd; volatile int32_t vi32; volatile int64_t vi64; volatile uint32_t vu32; volatile uint64_t vu64; volatile int vp;
    volatile int32_t si32; volatile int64_t si64; volatile uint32_t su32; volatile uint64_t su64;
    char name[64]; snprintf(name, sizeof name, "f32 %s", opname[op]);
    for (i = 0; i < n; i++) {
        int cls = (int)(i & 3);
        uint32_t a = gen32(cls, 0), b = gen32((int)(r64()&3), a), c;
        msf_flags_t mf = 0; unsigned hf; uint32_t hr = 0, mr = 0; int rm = msf_modes[mi];
        fesetround(host_modes[mi]);
        feclearexcept(FE_ALL_EXCEPT);
        switch (op) {
        case OP_ADD: va=u2f(a); vb=u2f(b); vr = va + vb; hf=host_flags(); hr=f2u(vr); mr = msf32_add(a,b,rm,&mf); break;
        case OP_SUB: va=u2f(a); vb=u2f(b); vr = va - vb; hf=host_flags(); hr=f2u(vr); mr = msf32_sub(a,b,rm,&mf); break;
        case OP_MUL: va=u2f(a); vb=u2f(b); vr = va * vb; hf=host_flags(); hr=f2u(vr); mr = msf32_mul(a,b,rm,&mf); break;
        case OP_DIV: va=u2f(a); vb=u2f(b); vr = va / vb; hf=host_flags(); hr=f2u(vr); mr = msf32_div(a,b,rm,&mf); break;
        case OP_SQRT: va=u2f(a); vr = __builtin_sqrtf(va); hf=host_flags(); hr=f2u(vr); mr = msf32_sqrt(a,rm,&mf); b=0; break;
        case OP_FMA: { uint32_t pe = ((a>>23)&0xff) + ((b>>23)&0xff); if (pe > 127) pe -= 127; else pe = 1; if (pe > 254) pe = 254;
                       c = gen32((int)(r64()&3), (pe<<23)); va=u2f(a); vb=u2f(b); vc=u2f(c); vr = __builtin_fmaf(va,vb,vc); hf=host_flags(); hr=f2u(vr); mr = msf32_fma(a,b,c,rm,&mf);
                       if (!(same32(hr,mr) && hf==mf)) { MISMATCH32(name, mode_names[mi], a,b,c,hr,hf,mr,mf); } continue; }
        case OP_RINT: va=u2f(a); vr = __builtin_rintf(va); hf=host_flags(); hr=f2u(vr); mr = msf32_round_to_integral_exact(a,rm,&mf); b=0; break;
        case OP_F2D: va=u2f(a); vrd = (double)va; hf=host_flags(); { uint64_t h64=d2u(vrd); uint64_t m64=msf64_from_f32(a,rm,&mf);
                     if (!(same64(h64,m64) && hf==mf)) { MISMATCH64(name, mode_names[mi], (uint64_t)a,0,0,h64,hf,m64,mf); } } continue;
        case OP_I32: si32=(int32_t)a; vr=(float)si32; hf=host_flags(); hr=f2u(vr); mr=msf32_from_i32((int32_t)a,rm,&mf); b=0; break;
        case OP_U32: su32=a; vr=(float)su32; hf=host_flags(); hr=f2u(vr); mr=msf32_from_u32(a,rm,&mf); b=0; break;
        case OP_I64: { uint64_t w = r64(); si64=(int64_t)w; vr=(float)si64; hf=host_flags(); hr=f2u(vr); mr=msf32_from_i64((int64_t)w,rm,&mf); a=(uint32_t)w; b=(uint32_t)(w>>32); break; }
        case OP_U64: { uint64_t w = r64(); su64=w; vr=(float)su64; hf=host_flags(); hr=f2u(vr); mr=msf32_from_u64(w,rm,&mf); a=(uint32_t)w; b=(uint32_t)(w>>32); break; }
        case OP_TOI32: { va=u2f(a); vi32=(int32_t)va; hf=host_flags(); int32_t m=msf32_to_i32_exact_toward_zero(a,&mf);
                         int ok = (hf & MSF_FLAG_INVALID) ? ((mf & MSF_FLAG_INVALID) != 0) : (vi32==m && hf==mf);
                         if (!ok) { MISMATCH32(name, mode_names[mi], a,0,0,(uint32_t)vi32,hf,(uint32_t)m,mf); } continue; }
        case OP_TOI64: { va=u2f(a); vi64=(int64_t)va; hf=host_flags(); int64_t m=msf32_to_i64_exact_toward_zero(a,&mf);
                         int ok = (hf & MSF_FLAG_INVALID) ? ((mf & MSF_FLAG_INVALID) != 0) : (vi64==m && hf==mf);
                         if (!ok) { MISMATCH64(name, mode_names[mi], (uint64_t)a,0,0,(uint64_t)vi64,hf,(uint64_t)m,mf); } continue; }
        case OP_TOU32: { va=u2f(a); if (!(va > -1.0f && va < 4294967296.0f)) continue; vu32=(uint32_t)va; hf=host_flags(); uint32_t m=msf32_to_u32_exact_toward_zero(a,&mf);
                         if (!(vu32==m && hf==mf)) { MISMATCH32(name, mode_names[mi], a,0,0,vu32,hf,m,mf); } continue; }
        case OP_TOU64: { va=u2f(a); if (!(va > -1.0f && va < 18446744073709551616.0f)) continue; vu64=(uint64_t)va; hf=host_flags(); uint64_t m=msf32_to_u64_exact_toward_zero(a,&mf);
                         if (!(vu64==m && hf==mf)) { MISMATCH64(name, mode_names[mi], (uint64_t)a,0,0,vu64,hf,m,mf); } continue; }
        case OP_QLT: va=u2f(a); vb=u2f(b); vp = __builtin_isless(va,vb); hf=host_flags(); hr=(uint32_t)vp; mr=(uint32_t)msf32_compare_quiet_less(a,b,&mf); if (!(hr==mr && hf==mf)) MISMATCH32(name, mode_names[mi], a,b,0,hr,hf,mr,mf); continue;
        case OP_QEQ: va=u2f(a); vb=u2f(b); vp = (va==vb); hf=host_flags(); hr=(uint32_t)vp; mr=(uint32_t)msf32_compare_quiet_equal(a,b,&mf); if (!(hr==mr && hf==mf)) MISMATCH32(name, mode_names[mi], a,b,0,hr,hf,mr,mf); continue;
        case OP_SLT: va=u2f(a); vb=u2f(b); vp = (va<vb); hf=host_flags(); hr=(uint32_t)vp; mr=(uint32_t)msf32_compare_signaling_less(a,b,&mf); if (!(hr==mr && hf==mf)) MISMATCH32(name, mode_names[mi], a,b,0,hr,hf,mr,mf); continue;
        case OP_SLE: va=u2f(a); vb=u2f(b); vp = (va<=vb); hf=host_flags(); hr=(uint32_t)vp; mr=(uint32_t)msf32_compare_signaling_less_equal(a,b,&mf); if (!(hr==mr && hf==mf)) MISMATCH32(name, mode_names[mi], a,b,0,hr,hf,mr,mf); continue;
        default: continue;
        }
        if (!(same32(hr,mr) && hf==mf)) { MISMATCH32(name, mode_names[mi], a,b,0,hr,hf,mr,mf); }
    }
    report(name, mode_names[mi], n, bad, 0);
}

int main(int argc, char **argv){
    long n = argc > 1 ? atol(argv[1]) : 1000000;
    if (argc > 2) rng = strtoull(argv[2], 0, 0);
    printf("hostdiff: FLT_EVAL_METHOD=%d n_per_op_mode=%ld seed=%llx\n", __FLT_EVAL_METHOD__, n, (unsigned long long)rng);
    opk ops64[] = { OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_SQRT, OP_FMA, OP_RINT, OP_D2F, OP_I32, OP_U32, OP_I64, OP_U64, OP_TOI32, OP_TOI64, OP_TOU32, OP_TOU64, OP_QLT, OP_QEQ, OP_SLT, OP_SLE };
    opk ops32[] = { OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_SQRT, OP_FMA, OP_RINT, OP_F2D, OP_I32, OP_U32, OP_I64, OP_U64, OP_TOI32, OP_TOI64, OP_TOU32, OP_TOU64, OP_QLT, OP_QEQ, OP_SLT, OP_SLE };
    for (unsigned k = 0; k < sizeof ops64 / sizeof ops64[0]; k++) for (int mi = 0; mi < 4; mi++) run64(ops64[k], mi, n);
    for (unsigned k = 0; k < sizeof ops32 / sizeof ops32[0]; k++) for (int mi = 0; mi < 4; mi++) run32(ops32[k], mi, n);
    fesetround(FE_TONEAREST);
    printf("hostdiff TOTAL cases=%ld mismatches=%ld -> %s\n", total_cases, total_bad, total_bad ? "MISMATCHES" : "ALL AGREE");
    return total_bad ? 1 : 0;
}
