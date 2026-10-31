/* mpt2.c - Tier 2 spot differential: muse-softfloat sinPi/cosPi/exp2/exp2m1/
 * log2/log2p1/rSqrt/hypot vs MPFR 4.2 emulating binary32/binary64 (subnormals
 * via mpfr_subnormalize; IEEE flags derived: inexact from ternary, overflow from
 * MPFR, underflow = tiny-after-rounding (unbounded-exponent rounding below
 * 2^emin) AND inexact). Modes te/tz/tp/tn. Finite non-special inputs only
 * (specials are table-driven in the project and checked by review).
 * Scratch-only audit code. */
#define _GNU_SOURCE
#include "hwcore.h"
#include <mpfr.h>

typedef enum { SINPI, COSPI, EXP2, EXP2M1, LOG2, LOG2P1, RSQRT, HYPOT, NFN } Fn;
static const char *FN[] = {"sin_pi", "cos_pi", "exp2", "exp2m1", "log2", "log2p1", "r_sqrt", "hypot"};
static const mpfr_rnd_t RM[4] = {MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU, MPFR_RNDD};

static int mpfr_eval(Fn f, mpfr_t r, mpfr_t x, mpfr_t y, mpfr_rnd_t rnd) {
    switch (f) {
    case SINPI: return mpfr_sinpi(r, x, rnd);
    case COSPI: return mpfr_cospi(r, x, rnd);
    case EXP2: return mpfr_exp2(r, x, rnd);
    case EXP2M1: return mpfr_exp2m1(r, x, rnd);
    case LOG2: return mpfr_log2(r, x, rnd);
    case LOG2P1: return mpfr_log2p1(r, x, rnd);
    case RSQRT: return mpfr_rec_sqrt(r, x, rnd);
    default: return mpfr_hypot(r, x, y, rnd);
    }
}
/* IEEE result in format (p, emin_normal, emax) for library mode m (0..3) */
static uint64_t ieee(Fn f, double xd, double yd, int w, int m, uint32_t *fl) {
    int p = w == 64 ? 53 : 24, emin = w == 64 ? -1022 : -126, emax = w == 64 ? 1023 : 127;
    mpfr_rnd_t rnd = RM[m];
    mpfr_t x, y, r, u;
    mpfr_inits2(64, x, y, (mpfr_ptr)0); mpfr_set_d(x, xd, MPFR_RNDN); mpfr_set_d(y, yd, MPFR_RNDN);
    mpfr_init2(r, p); mpfr_init2(u, p);
    /* unbounded-exponent rounding for tininess */
    mpfr_set_emin(mpfr_get_emin_min()); mpfr_set_emax(mpfr_get_emax_max());
    int tu = mpfr_eval(f, u, x, y, rnd);
    /* IEEE format emulation */
    mpfr_set_emin(emin - p + 2); mpfr_set_emax(emax + 1);
    mpfr_clear_flags();
    int t = mpfr_eval(f, r, x, y, rnd);
    t = mpfr_check_range(r, t, rnd);
    t = mpfr_subnormalize(r, t, rnd);
    int ovf = mpfr_overflow_p();
    mpfr_set_emin(mpfr_get_emin_min()); mpfr_set_emax(mpfr_get_emax_max());
    *fl = 0;
    if (t != 0) *fl |= MSF_FLAG_INEXACT;
    if (ovf) *fl |= MSF_FLAG_OVERFLOW | MSF_FLAG_INEXACT;
    if (t != 0 && (mpfr_zero_p(u) /* exact result nonzero but below even MPFR's widest range: tiny */ || (mpfr_number_p(u) && mpfr_get_exp(u) - 1 < emin))) *fl |= MSF_FLAG_UNDERFLOW; /* |u| < 2^emin */
    (void)tu;
    uint64_t bits;
    if (w == 64) { double d = mpfr_get_d(r, MPFR_RNDN); bits = d2u(d); }
    else { float fz = mpfr_get_flt(r, MPFR_RNDN); bits = f2u(fz); }
    mpfr_clears(x, y, r, u, (mpfr_ptr)0);
    return bits;
}
static double pick(Fn f, int w) {
    double v; uint64_t b;
    int k = (int)(rnd() % 6);
    switch (f) {
    case SINPI: case COSPI:
        if (k == 0) return ldexp((double)(int64_t)(rnd() % 4096) - 2048, -1) + ldexp((double)((int64_t)(rnd() % 2001) - 1000), -(int)(rnd() % 50) - 3);
        if (k == 1) return ldexp(1.0, -(int)(rnd() % 1000)) * ((rnd() & 1) ? 1 : -1);
        if (k == 2) return ldexp((double)(rnd() >> 11), (int)(rnd() % 30) - 60);
        break;
    case EXP2:
        if (k <= 2) return ((double)(int64_t)(rnd() % 2200000) - 1150000) / 1000.0 + ldexp((double)(int64_t)(rnd() % 1000) - 500, -40);
        break;
    case EXP2M1: case LOG2P1:
        if (k <= 1) return ldexp((double)(rnd() >> 11), -(int)(rnd() % 1100)) * ((rnd() & 1) ? 1 : -1) * 0x1p-53;
        if (k == 2) return ldexp((double)(rnd() >> 11), (int)(rnd() % 20) - 70);
        break;
    case LOG2:
        if (k <= 1) return 1.0 + ldexp((double)(int64_t)(rnd() % 2000001) - 1000000, -(int)(rnd() % 50) - 20);
        break;
    default: break;
    }
    b = gen_val(w == 64 ? &FM64 : &FM32);
    v = b2d(w, b);
    return v;
}
int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 20000;
    seed(argc > 2 ? strtoull(argv[2], 0, 0) : 5);
    long tot = 0, mism = 0;
    for (int w = 32; w <= 64; w += 32) for (int f = 0; f < NFN; f++) {
        long fm = 0, fc = 0;
        for (long i = 0; i < n; i++) {
            double x = pick((Fn)f, w), y = (f == HYPOT) ? b2d(w, gen_val(w == 64 ? &FM64 : &FM32)) : 0;
            if (w == 32) { x = (double)(float)x; y = (double)(float)y; }
            if (!isfinite(x) || !isfinite(y) || x == 0 || (f == HYPOT && y == 0)) continue;
            if ((f == LOG2 || f == RSQRT) && x < 0) x = -x;
            if (f == LOG2P1 && x <= -1) continue;
            if ((f == SINPI || f == COSPI) && fabs(x) >= 0x1p52) continue; /* integers: specials-like, sign rules table-driven */
            for (int m = 0; m < 4; m++) {
                uint32_t efl; uint64_t exp = ieee((Fn)f, x, y, w, m, &efl);
                msf_flags_t fl = 0; uint64_t got = 0;
                uint64_t xb = (w == 64) ? d2u(x) : f2u((float)x), yb = (w == 64) ? d2u(y) : f2u((float)y);
                if (w == 64) {
                    switch (f) { case SINPI: got = msf64_sin_pi(xb, m, &fl); break; case COSPI: got = msf64_cos_pi(xb, m, &fl); break;
                    case EXP2: got = msf64_exp2(xb, m, &fl); break; case EXP2M1: got = msf64_exp2m1(xb, m, &fl); break;
                    case LOG2: got = msf64_log2(xb, m, &fl); break; case LOG2P1: got = msf64_log2p1(xb, m, &fl); break;
                    case RSQRT: got = msf64_r_sqrt(xb, m, &fl); break; default: got = msf64_hypot(xb, yb, m, &fl); }
                } else {
                    switch (f) { case SINPI: got = msf32_sin_pi((msf32_t)xb, m, &fl); break; case COSPI: got = msf32_cos_pi((msf32_t)xb, m, &fl); break;
                    case EXP2: got = msf32_exp2((msf32_t)xb, m, &fl); break; case EXP2M1: got = msf32_exp2m1((msf32_t)xb, m, &fl); break;
                    case LOG2: got = msf32_log2((msf32_t)xb, m, &fl); break; case LOG2P1: got = msf32_log2p1((msf32_t)xb, m, &fl); break;
                    case RSQRT: got = msf32_r_sqrt((msf32_t)xb, m, &fl); break; default: got = msf32_hypot((msf32_t)xb, (msf32_t)yb, m, &fl); }
                }
                fc++;
                if (got != exp || fl != efl) { if (fm < 4) printf("  MISMATCH msf%d_%s %s x=%016llx y=%016llx -> got %llx fl=%02x expected %llx fl=%02x\n", w, FN[f], MN[m],
                    (unsigned long long)xb, (unsigned long long)yb, (unsigned long long)got, fl, (unsigned long long)exp, efl); fm++; }
            }
        }
        printf("msf%d_%-7s checked=%ld mismatches=%ld\n", w, FN[f], fc, fm); fflush(stdout);
        tot += fc; mism += fm;
    }
    printf("TOTAL checked=%ld mismatches=%ld\n", tot, mism);
    return mism != 0;
}
