/* hwcore.h - audit oracle helpers: x86-64 SSE/AVX hardware as the reference.
 * Scratch-only audit code; not part of the project. */
#ifndef HWCORE_H
#define HWCORE_H
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "muse_softfloat.h"

typedef struct { uint64_t r; uint32_t fl; int skip; } Res;

/* ---------- PRNG ---------- */
static uint64_t S[4] = {0x9E3779B97F4A7C15ull, 0xD1B54A32D192ED03ull, 0xABCDEF0123456789ull, 0x0F1E2D3C4B5A6978ull};
static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static inline uint64_t rnd(void) {
    uint64_t r = rotl(S[1] * 5, 7) * 9, t = S[1] << 17;
    S[2] ^= S[0]; S[3] ^= S[1]; S[1] ^= S[2]; S[0] ^= S[3]; S[2] ^= t; S[3] = rotl(S[3], 45);
    return r;
}
static void seed(uint64_t s) { for (int i = 0; i < 4; i++) { s += 0x9E3779B97F4A7C15ull; uint64_t z = s; z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull; z = (z ^ (z >> 27)) * 0x94D049BB133111EBull; S[i] = z ^ (z >> 31); } }

/* ---------- formats ---------- */
typedef struct { int w, eb, mb, bias; uint64_t sign, emask, mmask, qbit, all; } Fmt;
static const Fmt FM16 = {16, 5, 10, 15, 0x8000ull, 0x7C00ull, 0x3FFull, 0x200ull, 0xFFFFull};
static const Fmt FM32 = {32, 8, 23, 127, 0x80000000ull, 0x7F800000ull, 0x7FFFFFull, 0x400000ull, 0xFFFFFFFFull};
static const Fmt FM64 = {64, 11, 52, 1023, 1ull << 63, 0x7FF0000000000000ull, 0xFFFFFFFFFFFFFull, 1ull << 51, ~0ull};
static inline const Fmt *FMT(int w) { return w == 16 ? &FM16 : w == 32 ? &FM32 : &FM64; }
static inline int b_isnan(const Fmt *f, uint64_t x) { return (x & f->emask) == f->emask && (x & f->mmask); }
static inline int b_issnan(const Fmt *f, uint64_t x) { return b_isnan(f, x) && !(x & f->qbit); }
static inline int b_isinf(const Fmt *f, uint64_t x) { return (x & ~f->sign & f->all) == f->emask; }
static inline int b_iszero(const Fmt *f, uint64_t x) { return (x & ~f->sign & f->all) == 0; }
static inline uint64_t b_defnan(const Fmt *f) { return f->emask | f->qbit; }
/* NaN carried across formats, quieted, keeping the most significant trailing bits */
static inline uint64_t b_nanconv(const Fmt *s, const Fmt *d, uint64_t x) {
    uint64_t sg = (x & s->sign) ? d->sign : 0, m = (x & s->mmask) | s->qbit;
    if (d->mb >= s->mb) m <<= (d->mb - s->mb); else m >>= (s->mb - d->mb);
    return sg | d->emask | (m & d->mmask) | d->qbit;
}

static inline uint64_t d2u(double d) { uint64_t u; memcpy(&u, &d, 8); return u; }
static inline double u2d(uint64_t u) { double d; memcpy(&d, &u, 8); return d; }
static inline uint32_t f2u(float f) { uint32_t u; memcpy(&u, &f, 4); return u; }
static inline float u2f(uint32_t u) { float f; memcpy(&f, &u, 4); return f; }

/* exact value of a non-NaN encoding as a double */
static inline double h2d(uint64_t h) {
    int s = (h >> 15) & 1, e = (h >> 10) & 31, m = h & 1023; double v;
    if (e == 0) v = ldexp((double)m, -24); else if (e == 31) v = m ? NAN : INFINITY; else v = ldexp((double)(m | 1024), e - 25);
    return s ? -v : v;
}
static inline double b2d(int w, uint64_t x) { return w == 16 ? h2d(x) : w == 32 ? (double)u2f((uint32_t)x) : u2d(x); }

/* ---------- hardware windows (MXCSR) ---------- */
/* library modes: 0 RNE, 1 RTZ, 2 RUP, 3 RDN, 4 RNA. MXCSR RC: 00 RNE, 01 RDN, 10 RUP, 11 RTZ */
static const uint32_t RCBITS[4] = {0, 3, 2, 1};
static inline void hw_begin(int m) { uint32_t v = 0x1F80u | (RCBITS[m] << 13); __asm__ volatile("ldmxcsr %0" ::"m"(v) : "memory"); }
static inline uint32_t hw_end(void) {
    uint32_t v; __asm__ volatile("stmxcsr %0" : "=m"(v)::"memory");
    uint32_t f = 0;
    if (v & 1) f |= MSF_FLAG_INVALID; if (v & 4) f |= MSF_FLAG_DIVISION_BY_ZERO; if (v & 8) f |= MSF_FLAG_OVERFLOW;
    if (v & 16) f |= MSF_FLAG_UNDERFLOW; if (v & 32) f |= MSF_FLAG_INEXACT;
    uint32_t d = 0x1F80u; __asm__ volatile("ldmxcsr %0" ::"m"(d) : "memory");
    return f;
}
static inline double hadd(double a, double b) { __asm__ volatile("addsd %1, %0" : "+x"(a) : "x"(b)); return a; }
static inline double hsub(double a, double b) { __asm__ volatile("subsd %1, %0" : "+x"(a) : "x"(b)); return a; }
static inline double hmul(double a, double b) { __asm__ volatile("mulsd %1, %0" : "+x"(a) : "x"(b)); return a; }
static inline double hdiv(double a, double b) { __asm__ volatile("divsd %1, %0" : "+x"(a) : "x"(b)); return a; }
static inline double hsqrt(double a) { double r = 0; __asm__ volatile("sqrtsd %1, %0" : "+x"(r) : "x"(a)); return r; }
static inline double hfma(double a, double b, double c) { __asm__ volatile("vfmadd213sd %2, %1, %0" : "+x"(a) : "x"(b), "x"(c)); return a; }
static inline float hcvt_d2f(double a) { float r = 0; __asm__ volatile("cvtsd2ss %1, %0" : "+x"(r) : "x"(a)); return r; }
static inline uint16_t hcvt_f2h(float a) {
    uint32_t r; float z = 0;
    __asm__ volatile("vxorps %1, %1, %1\n\tvmovss %2, %1, %1\n\tvcvtps2ph $4, %1, %1\n\tvmovd %1, %0" : "=r"(r), "+x"(z) : "x"(a));
    return (uint16_t)r;
}
#define HROUND(IMM) static inline double hround_##IMM(double a) { double r = 0; __asm__ volatile("roundsd $" #IMM ", %1, %0" : "+x"(r) : "x"(a)); return r; }
HROUND(4) HROUND(8) HROUND(9) HROUND(10) HROUND(11)
static inline double hcvt_i64(int64_t x) { double r = 0; __asm__ volatile("cvtsi2sdq %1, %0" : "+x"(r) : "r"(x)); return r; }
static inline double hcvt_u64(uint64_t x) { double r = 0; __asm__ volatile("vcvtusi2sdq %1, %0, %0" : "+x"(r) : "r"(x)); return r; }

/* Round a double intermediate v (exact, or rounded-to-odd with >= 2 extra bits)
 * to destination width w in library mode m (0..4). */
static uint64_t round_from_double(double v, int w, int m, uint32_t *fl) {
    if (w == 64) { *fl = 0; return d2u(v); }
    if (m == 4) {
        uint32_t flo, fhi;
        uint64_t lo = round_from_double(v, w, 1, &flo);
        uint64_t hi = round_from_double(v, w, signbit(v) ? 3 : 2, &fhi);
        if (lo == hi) { *fl = flo; return lo; }
        double mid = (b2d(w, lo) + b2d(w, hi)) * 0.5;
        if (v == mid) { *fl = fhi; return hi; }
        return round_from_double(v, w, 0, fl);
    }
    if (w == 32) { hw_begin(m); float f = hcvt_d2f(v); *fl = hw_end(); return f2u(f); }
    hw_begin(1); float f = hcvt_d2f(v); uint32_t f1 = hw_end();
    uint32_t fb = f2u(f); if (f1 & MSF_FLAG_INEXACT) fb |= 1;
    hw_begin(m); uint16_t h = hcvt_f2h(u2f(fb)); *fl = hw_end();
    return h;
}
static inline double odd(double r, uint32_t fl) { return (fl & MSF_FLAG_INEXACT) ? u2d(d2u(r) | 1) : r; }

/* ---------- generators ---------- */
static uint64_t gen_special(const Fmt *f) {
    uint64_t emax = f->emask >> f->mb, m;
    uint64_t es[] = {0, 0, 1, 2, emax - 1, emax - 2, emax, emax, (uint64_t)f->bias, (uint64_t)f->bias - 1, (uint64_t)f->bias + 1};
    uint64_t e = es[rnd() % 11];
    switch (rnd() % 8) {
    case 0: m = 0; break; case 1: m = 1; break; case 2: m = f->mmask; break; case 3: m = f->mmask - 1; break;
    case 4: m = f->qbit; break; case 5: m = f->qbit | 1; break; case 6: m = f->qbit - 1; break; default: m = rnd() & f->mmask;
    }
    return ((rnd() & 1) ? f->sign : 0) | (e << f->mb) | m;
}
static uint64_t gen_val(const Fmt *f) {
    uint64_t emax = f->emask >> f->mb, sg = (rnd() & 1) ? f->sign : 0, e, m = rnd() & f->mmask;
    switch (rnd() % 12) {
    case 0: case 1: return rnd() & f->all;
    case 2: case 3: return gen_special(f);
    case 4: e = (uint64_t)(f->bias > 20 ? f->bias - 20 : 1) + rnd() % 41; break;
    case 5: e = (uint64_t)(f->bias > 20 ? f->bias - 20 : 1) + rnd() % 41; m = 0; for (int k = rnd() % 4; k > 0; k--) m |= 1ull << (rnd() % f->mb); break;
    case 6: e = (uint64_t)(f->bias > 20 ? f->bias - 20 : 1) + rnd() % 41; m = f->mmask; for (int k = rnd() % 4; k > 0; k--) m &= ~(1ull << (rnd() % f->mb)); break;
    case 7: e = rnd() % emax; break;
    case 8: e = 0; if (rnd() & 1) { m = 0; for (int k = 1 + rnd() % 3; k > 0; k--) m |= 1ull << (rnd() % f->mb); } break;
    case 9: e = emax - 1 - rnd() % 4; break;
    case 10: e = 1 + rnd() % (f->mb + 3); break;
    default: { /* small integer or half-integer */
        int64_t n = (int64_t)(rnd() % (1u << (rnd() % 24 + 1))); double v = (double)n * ldexp(1.0, (int)(rnd() % 5) - 2);
        if (f->w == 64) return sg | d2u(v);
        uint32_t fl; return sg | round_from_double(v, f->w, 0, &fl);
    }
    }
    return (sg | (e << f->mb) | (m & f->mmask)) & f->all;
}
/* second operand correlated with the first */
static uint64_t gen_rel(const Fmt *f, uint64_t a) {
    uint64_t sg = (rnd() & 1) ? f->sign : 0;
    switch (rnd() % 8) {
    case 0: case 1: return gen_val(f);
    case 2: return ((a ^ f->sign) + (rnd() % 9) - 4) & f->all;               /* near -a: cancellation */
    case 3: return (a + (rnd() % 9) - 4) & f->all;                            /* near a */
    case 4: { int64_t ea = (int64_t)((a & f->emask) >> f->mb); int64_t d = (int64_t)(rnd() % (2 * f->mb + 8)) - (f->mb + 4);
              int64_t e = ea + d; uint64_t emax = f->emask >> f->mb; if (e < 0) e = 0; if (e >= (int64_t)emax) e = emax - 1;
              return sg | ((uint64_t)e << f->mb) | (rnd() & f->mmask); }
    case 5: return gen_special(f);
    case 6: return a ^ (rnd() & 1 ? f->sign : 0);
    default: return (a & ~f->mmask) | (rnd() & f->mmask);
    }
}
static const char *MN[5] = {"te", "tz", "tp", "tn", "ta"};
#endif
