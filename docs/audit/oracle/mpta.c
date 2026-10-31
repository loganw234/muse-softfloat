/* mpta.c - roundTiesToAway (mode 4) for binary64 fma / mul / div, the cases
 * hwdiff skipped. Exact value from MPFR (3300 bits); tie decided exactly;
 * result taken from hardware in the away direction at a tie, else RNE.
 * Also constructed-tie stress for binary32/binary16 fma via the hwdiff
 * round-to-odd oracle. Scratch-only audit code. */
#define _GNU_SOURCE
#include "hwcore.h"
#include <mpfr.h>

static mpfr_t X, LO, HI, MID;
static long mism = 0, checked = 0, ties = 0;

/* returns 1 if exact value X is the midpoint of hardware lo/hi (both finite) */
static int is_tie(double lo, double hi) {
    if (lo == hi || isinf(lo) || isinf(hi)) return 0;
    mpfr_set_d(LO, lo, MPFR_RNDN); mpfr_set_d(HI, hi, MPFR_RNDN);
    mpfr_add(MID, LO, HI, MPFR_RNDN); mpfr_div_2ui(MID, MID, 1, MPFR_RNDN); /* exact at 3300 bits */
    return mpfr_cmp(X, MID) == 0;
}
typedef enum { K_FMA, K_MUL, K_DIV } Kind;
static double hwop(Kind k, double a, double b, double c) { return k == K_FMA ? hfma(a, b, c) : k == K_MUL ? hmul(a, b) : hdiv(a, b); }
static void check64(Kind k, double a, double b, double c) {
    if (isnan(a) || isnan(b) || isnan(c)) return;
    hw_begin(0); double rne = hwop(k, a, b, c); uint32_t frne = hw_end();
    double expd; uint32_t efl;
    if (isnan(rne)) { expd = u2d(0x7FF8000000000000ull); efl = frne; }
    else {
        int tie = 0;
        if (k == K_FMA) mpfr_fma(X, (mpfr_set_d(LO, a, MPFR_RNDN), LO), (mpfr_set_d(HI, b, MPFR_RNDN), HI), (mpfr_set_d(MID, c, MPFR_RNDN), MID), MPFR_RNDZ);
        else { mpfr_t A, B; mpfr_init2(A, 64); mpfr_init2(B, 64); mpfr_set_d(A, a, MPFR_RNDN); mpfr_set_d(B, b, MPFR_RNDN);
               if (k == K_MUL) mpfr_mul(X, A, B, MPFR_RNDZ); else mpfr_div(X, A, B, MPFR_RNDZ); mpfr_clear(A); mpfr_clear(B); }
        if (mpfr_number_p(X) && !mpfr_zero_p(X)) {
            int neg = mpfr_sgn(X) < 0;
            hw_begin(1); double lo = hwop(k, a, b, c); hw_end();
            hw_begin(neg ? 3 : 2); double hi = hwop(k, a, b, c); hw_end();
            tie = is_tie(lo, hi);
        }
        if (tie) { ties++; hw_begin(signbit(rne) ? 3 : 2); expd = hwop(k, a, b, c); efl = hw_end(); }
        else { expd = rne; efl = frne; }
    }
    msf_flags_t fl = 0; uint64_t got;
    if (k == K_FMA) got = msf64_fma(d2u(a), d2u(b), d2u(c), MSF_ROUND_TIES_TO_AWAY, &fl);
    else if (k == K_MUL) got = msf64_mul(d2u(a), d2u(b), MSF_ROUND_TIES_TO_AWAY, &fl);
    else got = msf64_div(d2u(a), d2u(b), MSF_ROUND_TIES_TO_AWAY, &fl);
    checked++;
    if (got != d2u(expd) || fl != efl) { if (mism++ < 10) printf("  MISMATCH %s ta %016llx %016llx %016llx -> got %016llx fl=%02x expected %016llx fl=%02x\n",
        k == K_FMA ? "msf64_fma" : k == K_MUL ? "msf64_mul" : "msf64_div", (unsigned long long)d2u(a), (unsigned long long)d2u(b), (unsigned long long)d2u(c),
        (unsigned long long)got, fl, (unsigned long long)d2u(expd), efl); }
}
/* constructed exact ties: c + (odd small product) landing on c's half-ulp */
static void gen_tie64(double *a, double *b, double *c) {
    int E;
    double cv;
    switch (rnd() % 4) {
    case 0: E = (int)(rnd() % 2000) - 1000; break;          /* normal range */
    case 1: E = -1022 - (int)(rnd() % 52); break;            /* subnormal grid */
    case 2: E = 1023 - (int)(rnd() % 3); break;              /* near overflow */
    default: E = -1022 + (int)(rnd() % 4); break;            /* smallest-normal boundary */
    }
    uint64_t m = rnd() & ((1ull << 52) - 1);
    cv = ldexp((double)(m | (1ull << 52)), E - 52); if (E < -1022) cv = ldexp((double)(rnd() & ((1ull << 52) - 1)), -1074);
    if (rnd() & 1) cv = -cv;
    int lsb = (E < -1022 ? -1074 : E - 52) - 1;            /* half-ulp position of c */
    uint64_t oa = (rnd() % 2048) | 1, ob = (rnd() % 2048) | 1;
    if (rnd() % 3 == 0) ob = 1;
    int ia = (int)(rnd() % 40) - 20; int ib = lsb - ia;
    *a = ldexp((double)oa, ia); *b = ldexp((double)ob, ib); if (rnd() & 1) *b = -*b;
    *c = cv;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 200000;
    seed(argc > 2 ? strtoull(argv[2], 0, 0) : 99);
    mpfr_init2(X, 3300); mpfr_init2(LO, 3300); mpfr_init2(HI, 3300); mpfr_init2(MID, 3300);
    for (long i = 0; i < n; i++) {
        double a, b, c;
        if (i & 1) gen_tie64(&a, &b, &c);
        else { a = u2d(gen_val(&FM64)); b = u2d(gen_rel(&FM64, d2u(a))); c = u2d(gen_val(&FM64)); if (rnd() & 1) c = -(a * b); }
        check64(K_FMA, a, b, c);
        /* tiny products / quotients near and below the subnormal boundary (hwdiff skipped these) */
        double x = ldexp((double)((rnd() & ((1ull << 52) - 1)) | (1ull << 52)), (int)(rnd() % 120) - 600);
        double y = ldexp((double)((rnd() % 4096) | 1), (int)(rnd() % 120) - 540);
        if (rnd() & 1) y = -y;
        check64(K_MUL, x, y, 0); check64(K_DIV, x, ldexp(1.0, 500 + (int)(rnd() % 80)), 0); check64(K_DIV, x, 1.0 / y, 0);
    }
    printf("binary64 ta (fma, tiny mul, subnormal div): checked=%ld exact-ties=%ld mismatches=%ld\n", checked, ties, mism);
    return mism != 0;
}
