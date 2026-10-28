/* alg_decider.c - host MPFR decider + differential harness
 * for the SF-2 algebraic bundle's rSqrt rows (test-only; NOT
 * part of the shipped library and never linked into it).
 *
 * Finite positive inputs are decided by the proven Step 0b
 * operation recipe: per-format precision and emin/emax
 * (binary16 11/-23/16, binary32 24/-148/128, binary64
 * 53/-1073/1024, set and read back), the operand set exactly
 * from its decoded significand at format precision (it fits
 * by construction), mpfr_rec_sqrt under the four MPFR
 * rounding modes, then mpfr_subnormalize skipped on
 * zero/inf/NaN intermediates. Flags are derived, never
 * transcribed from MPFR: inexact iff the final ternary is
 * nonzero. Overflow and underflow are unattainable for
 * rSqrt (result range strictly interior at every format);
 * a zero/inf/NaN intermediate on a finite positive input is
 * a recipe violation and aborts the run rather than being
 * averaged away. MPFR exception flags are never read.
 *
 * Specials are table-decided here from the settled 9.2.1
 * cells (ledger/parcel-w5alg1.md design entry), implemented
 * independently of the kernel: signed zeros give the signed
 * pole infinity + divideByZero (the rSqrt(-0) = -inf cell is
 * fenced - executed MPFR gives +inf there, measured by the
 * SF-2 algebraic study, so this cell never comes from an
 * MPFR call); +inf gives +0; negative operands give the
 * default quiet NaN + invalid; NaNs follow the SF-0 2.5
 * matrix (payload preserved, quieted; invalid iff
 * signaling).
 *
 * The fifth attribute (roundTiesToAway) is printed equal to
 * ties-to-even: raw MPFR RNDNA is prohibited as a general
 * mode and is not used. This is sound only where exact ties
 * are unattainable (true for rSqrt - a midpoint's reciprocal
 * square cannot be an integer significand), and the vector
 * generator refuses any case where its independent exact
 * integer decider disagrees on the ta column, so the
 * equality is verified per case, never assumed globally.
 *
 * Modes:
 *   decide              stdin "msf16_r_sqrt 3c00" lines;
 *                       stdout: op in, then bits+flags for
 *                       te tz tp tn ta
 *   f16                 exhaustive binary16 differential:
 *                       all 65,536 encodings x 5 modes,
 *                       kernel vs this decider, count printed
 *   seeded FMT SEED N   seeded finite-positive binary32/64
 *                       encodings, kernel vs decider x5
 * Exit status is nonzero on any mismatch, undecided case,
 * or recipe violation.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <mpfr.h>
#include "../include/muse_softfloat.h"

typedef struct {
    const char *name;
    int w;
    int p;
    int t;
    int bias;
    int emin;
    int emax;
    long mpf_emin;
    long mpf_emax;
} fmt_t;

static const fmt_t FMTS[3] = {
    { "f16", 16, 11, 10, 15, -14, 15, -23, 16 },
    { "f32", 32, 24, 23, 127, -126, 127, -148, 128 },
    { "f64", 64, 53, 52, 1023, -1022, 1023, -1073, 1024 },
};

static const mpfr_rnd_t RND[4] = { MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU, MPFR_RNDD };
static const char *RM_NAME[5] = { "te", "tz", "tp", "tn", "ta" };

#define FL_INVALID 0x01u
#define FL_DIVZERO 0x02u
#define FL_INEXACT 0x10u

static uint64_t g_checked, g_mismatch;

static void decode_bits(const fmt_t *f, uint64_t bits, int *sign,
                        uint64_t *sig, int *exp2, int *cls)
{
    /* cls: 0 zero, 1 finite nonzero, 2 inf, 3 qnan, 4 snan */
    int ew = f->w - 1 - f->t;
    uint64_t ef = (bits >> f->t) & ((1ULL << ew) - 1ULL);
    uint64_t frac = bits & ((1ULL << f->t) - 1ULL);
    uint64_t emaxf = (1ULL << ew) - 1ULL;
    *sign = (int)(bits >> (f->w - 1)) & 1;
    if (ef == emaxf) {
        *sig = frac;
        *exp2 = 0;
        *cls = frac == 0 ? 2 : ((frac >> (f->t - 1)) & 1 ? 3 : 4);
    } else if (ef == 0) {
        *sig = frac;
        *exp2 = f->emin - f->t;
        *cls = frac == 0 ? 0 : 1;
    } else {
        *sig = frac | (1ULL << f->t);
        *exp2 = (int)ef - f->bias - f->t;
        *cls = 1;
    }
}

static uint64_t inf_bits(const fmt_t *f, int sign)
{
    uint64_t emaxf = (1ULL << (f->w - 1 - f->t)) - 1ULL;
    return ((uint64_t)sign << (f->w - 1)) | (emaxf << f->t);
}

/* Returns 1 when the input is a table cell (fills rb/rf x5). */
static int decide_special(const fmt_t *f, uint64_t bits,
                          uint64_t rb[5], uint32_t rf[5])
{
    int sign, exp2, cls, i;
    uint64_t sig, r;
    uint32_t fl;
    decode_bits(f, bits, &sign, &sig, &exp2, &cls);
    (void)sig;
    (void)exp2;
    if (cls == 3 || cls == 4) {
        r = bits | (1ULL << (f->t - 1));
        fl = cls == 4 ? FL_INVALID : 0u;
    } else if (cls == 0) {
        r = inf_bits(f, sign);
        fl = FL_DIVZERO;
    } else if (cls == 2 && !sign) {
        r = 0u;
        fl = 0u;
    } else if (cls == 2 || sign) {
        r = inf_bits(f, 0) | (1ULL << (f->t - 1)); /* default qNaN */
        fl = FL_INVALID;
    } else {
        return 0; /* finite positive: the MPFR path */
    }
    for (i = 0; i < 5; i++) {
        rb[i] = r;
        rf[i] = fl;
    }
    return 1;
}

/* Exact nonnegative integer in an mpfr to uint64_t, split at
 * 2^32 because this host's unsigned long is 32 bits. */
static uint64_t get_u64_from_int(mpfr_t v)
{
    static mpfr_t q;
    static int qin = 0;
    uint64_t hi, lo;
    if (!qin) {
        mpfr_init2(q, 128);
        qin = 1;
    }
    mpfr_mul_2si(q, v, -32, MPFR_RNDZ);
    mpfr_trunc(q, q);
    hi = (uint64_t)mpfr_get_ui(q, MPFR_RNDZ);
    mpfr_mul_2si(q, q, 32, MPFR_RNDZ);
    mpfr_sub(q, v, q, MPFR_RNDZ);
    lo = (uint64_t)mpfr_get_ui(q, MPFR_RNDZ);
    return (hi << 32) | lo;
}

static uint64_t extract_bits(const fmt_t *f, mpfr_t r)
{
    static mpfr_t tmp;
    static int in = 0;
    long e;
    uint64_t m;
    if (!in) {
        mpfr_init2(tmp, 128);
        in = 1;
    }
    e = (long)mpfr_get_exp(r) - 1; /* |r| in [2^e, 2^(e+1)) */
    if (e < f->emin || e > f->emax) {
        fprintf(stderr, "RECIPE VIOLATION: result exponent %ld outside "
                "[%d,%d] for %s\n", e, f->emin, f->emax, f->name);
        exit(3);
    }
    mpfr_abs(tmp, r, MPFR_RNDN);
    mpfr_mul_2si(tmp, tmp, (long)f->t - e, MPFR_RNDN);
    m = get_u64_from_int(tmp);
    return ((uint64_t)(unsigned long)(e + f->bias) << f->t)
         | (m - (1ULL << f->t));
}

static mpfr_t g_x, g_r, g_tmp;
static int g_prec = 0;
static long g_emin = 1, g_emax = 0;

static void decider_setup(const fmt_t *f)
{
    if (g_prec != f->p) {
        if (g_prec != 0) {
            mpfr_clear(g_x);
            mpfr_clear(g_r);
            mpfr_clear(g_tmp);
        }
        mpfr_init2(g_x, (mpfr_prec_t)f->p);
        mpfr_init2(g_r, (mpfr_prec_t)f->p);
        mpfr_init2(g_tmp, (mpfr_prec_t)f->p);
        g_prec = f->p;
    }
    if (g_emin != f->mpf_emin || g_emax != f->mpf_emax) {
        mpfr_set_emin(f->mpf_emin);
        mpfr_set_emax(f->mpf_emax);
        if (mpfr_get_emin() != f->mpf_emin
                || mpfr_get_emax() != f->mpf_emax) {
            fprintf(stderr, "emin/emax readback failed for %s\n", f->name);
            exit(3);
        }
        g_emin = f->mpf_emin;
        g_emax = f->mpf_emax;
    }
}

/* Decide one finite positive encoding for te/tz/tp/tn (+ta=te). */
static void decide_mpfr(const fmt_t *f, uint64_t bits,
                        uint64_t rb[5], uint32_t rf[5])
{
    int sign, exp2, cls, rm;
    uint64_t sig;
    decode_bits(f, bits, &sign, &sig, &exp2, &cls);
    decider_setup(f);
    mpfr_set_ui(g_x, (unsigned long)(sig & 0xffffffffULL), MPFR_RNDN);
    if (sig >> 32) {
        mpfr_set_ui(g_tmp, (unsigned long)(sig >> 32), MPFR_RNDN);
        mpfr_mul_2si(g_tmp, g_tmp, 32, MPFR_RNDN);
        mpfr_add(g_x, g_x, g_tmp, MPFR_RNDN);
    }
    mpfr_mul_2si(g_x, g_x, exp2, MPFR_RNDN);
    for (rm = 0; rm < 4; rm++) {
        int tern = mpfr_rec_sqrt(g_r, g_x, RND[rm]);
        if (mpfr_nan_p(g_r) || mpfr_inf_p(g_r) || mpfr_zero_p(g_r)) {
            fprintf(stderr, "RECIPE VIOLATION: %s in=%016llx rm=%s "
                    "intermediate not finite nonzero\n",
                    f->name, (unsigned long long)bits, RM_NAME[rm]);
            exit(3);
        }
        tern = mpfr_subnormalize(g_r, tern, RND[rm]);
        rb[rm] = extract_bits(f, g_r);
        rf[rm] = tern != 0 ? FL_INEXACT : 0u;
    }
    rb[4] = rb[0];
    rf[4] = rf[0];
}

static void decide(const fmt_t *f, uint64_t bits,
                   uint64_t rb[5], uint32_t rf[5])
{
    if (!decide_special(f, bits, rb, rf)) {
        decide_mpfr(f, bits, rb, rf);
    }
}

static uint64_t kernel_call(int fi, uint64_t bits, int rm,
                            msf_flags_t *fl)
{
    *fl = 0u;
    switch (fi) {
    case 0: return msf16_r_sqrt((msf16_t)bits, (msf_rounding_t)rm, fl);
    case 1: return msf32_r_sqrt((msf32_t)bits, (msf_rounding_t)rm, fl);
    default: return msf64_r_sqrt(bits, (msf_rounding_t)rm, fl);
    }
}

static void check_one(int fi, uint64_t bits)
{
    const fmt_t *f = &FMTS[fi];
    uint64_t rb[5];
    uint32_t rf[5];
    int rm;
    decide(f, bits, rb, rf);
    for (rm = 0; rm < 5; rm++) {
        msf_flags_t fl;
        uint64_t got = kernel_call(fi, bits, rm, &fl);
        uint64_t mask = f->w >= 64 ? ~0ULL : ((1ULL << f->w) - 1ULL);
        g_checked++;
        if ((got & mask) != rb[rm] || (uint32_t)fl != rf[rm]) {
            g_mismatch++;
            if (g_mismatch <= 20) {
                printf("MISMATCH %s rSqrt %s in=%016llx got=%016llx/%02x "
                       "want=%016llx/%02x\n", f->name, RM_NAME[rm],
                       (unsigned long long)bits,
                       (unsigned long long)(got & mask), (unsigned)fl,
                       (unsigned long long)rb[rm], (unsigned)rf[rm]);
            }
        }
    }
}

static int fmt_of_op(const char *op)
{
    if (strcmp(op, "msf16_r_sqrt") == 0) return 0;
    if (strcmp(op, "msf32_r_sqrt") == 0) return 1;
    if (strcmp(op, "msf64_r_sqrt") == 0) return 2;
    return -1;
}

static uint64_t rng_state;
static uint64_t rng_next(void)
{
    uint64_t x = rng_state;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    rng_state = x;
    return x * 0x2545F4914F6CDD1DULL;
}

int main(int argc, char **argv)
{
    setvbuf(stdout, NULL, _IOFBF, 1u << 20);
    if (argc >= 2 && strcmp(argv[1], "decide") == 0) {
        char op[64], tok[64];
        while (scanf("%63s %63s", op, tok) == 2) {
            int fi = fmt_of_op(op);
            uint64_t rb[5];
            uint32_t rf[5];
            int i;
            if (fi < 0) {
                fprintf(stderr, "unknown op %s\n", op);
                return 2;
            }
            decide(&FMTS[fi], strtoull(tok, NULL, 16), rb, rf);
            printf("%s %s", op, tok);
            for (i = 0; i < 5; i++) {
                printf(" %llx %02x", (unsigned long long)rb[i],
                       (unsigned)rf[i]);
            }
            printf("\n");
        }
        return 0;
    }
    if (argc >= 2 && strcmp(argv[1], "f16") == 0) {
        uint64_t bits;
        for (bits = 0; bits < 65536ULL; bits++) {
            check_one(0, bits);
        }
        printf("F16-EXHAUSTIVE rSqrt: checked=%llu mismatches=%llu %s\n",
               (unsigned long long)g_checked,
               (unsigned long long)g_mismatch,
               g_mismatch == 0 && g_checked == 327680ULL
                   ? "PASS" : "FAIL");
        return g_mismatch == 0 && g_checked == 327680ULL ? 0 : 1;
    }
    if (argc >= 5 && strcmp(argv[1], "seeded") == 0) {
        int fi = strcmp(argv[2], "f32") == 0 ? 1
               : strcmp(argv[2], "f64") == 0 ? 2 : -1;
        uint64_t count, done = 0;
        const fmt_t *f;
        if (fi < 0) {
            fprintf(stderr, "seeded needs f32|f64\n");
            return 2;
        }
        f = &FMTS[fi];
        rng_state = strtoull(argv[3], NULL, 0) | 1ULL;
        count = strtoull(argv[4], NULL, 0);
        while (done < count) {
            uint64_t bits = rng_next();
            int ew = f->w - 1 - f->t;
            uint64_t emaxf = (1ULL << ew) - 1ULL;
            if (f->w == 32) {
                bits &= 0xffffffffULL;
            }
            bits &= ~(1ULL << (f->w - 1)); /* positive */
            if (((bits >> f->t) & emaxf) == emaxf) {
                continue; /* finite only: the MPFR path */
            }
            check_one(fi, bits);
            done++;
        }
        printf("SEEDED-%s rSqrt: inputs=%llu checked=%llu "
               "mismatches=%llu %s\n", f->name,
               (unsigned long long)done,
               (unsigned long long)g_checked,
               (unsigned long long)g_mismatch,
               g_mismatch == 0 ? "PASS" : "FAIL");
        return g_mismatch == 0 ? 0 : 1;
    }
    fprintf(stderr, "usage: alg_decider decide|f16|seeded f32|f64 SEED N\n");
    return 2;
}
