/* trig_exhaustive.c - host differential harness for the
 * sinPi/cosPi bundle (SF-1 Step 2c gates; NOT part of the
 * shipped library and never linked into it).
 *
 * The decider is MPFR: the exact input is reconstructed from
 * its bit pattern, mpfr_sinpi/mpfr_cospi evaluate it at
 * working precision P (RNDN), the value is bracketed by two
 * nextabove/nextbelow steps (MPFR's correctly rounded result
 * errs by at most half an ulp at P), and both bracket ends
 * are narrowed to the destination format in all four modes
 * with the proven recipe (mpfr_set at precision p +
 * mpfr_check_range + mpfr_subnormalize under per-format
 * emin/emax, zero guard; Step 0b and the Step 2b spike
 * Section 1). Agreement of bits and flags at both ends
 * decides; otherwise P escalates 160 -> 384 -> 768 (decide
 * mode starts at 640 for the mpfr640-trig provenance family).
 * Flags are computed here from first principles (inexact =
 * narrowing discarded a nonzero tail; underflow = inexact
 * and the unbounded-exponent prec-p rounding is below
 * 2^emin, tininess after rounding); MPFR exception flags are
 * never read. Specials (NaN, infinity, zero, exact integers
 * and half-integers) are decided from the settled 9.2.1 table
 * in the ledger design entry, implemented here independently
 * of the kernel. For negative inputs the decider may use the
 * exact odd/even symmetry of sinPi/cosPi (with raw-decider
 * audits on a stride sample); the kernel is always invoked
 * on the original signed encoding in every mode.
 *
 * Modes:
 *   f16                  exhaustive binary16 finite sweep
 *   f32 LO HI            binary32 encodings in [LO, HI)
 *   f64seed SEED COUNT   seeded finite binary64 patterns
 *   wc sin|cos FILE      binary64 inputs from a .wc file
 *                        (mechanical token parse only)
 *   decide               stdin "msf16_sin_pi 3c00" lines;
 *                        stdout bits+flags for te tz tp tn
 * Exit status is nonzero on any mismatch, decider-undecided
 * input, audit failure, or final-undecided kernel hit.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <mpfr.h>
#include "../include/muse_softfloat.h"

#ifdef MSF_TRIG_TEST_COUNTERS
extern uint64_t msf_trig_stage_hits[3];
extern uint64_t msf_trig_final_undecided;
#endif

typedef struct {
    const char *name;
    int w;         /* total bits */
    int p;         /* precision */
    int t;         /* trailing bits */
    int bias;
    int emin;      /* format emin */
    long mpf_emin; /* proven MPFR narrowing bounds */
    long mpf_emax;
} fmt_t;

static const fmt_t FMTS[3] = {
    { "f16", 16, 11, 10, 15, -14, -23, 16 },
    { "f32", 32, 24, 23, 127, -126, -148, 128 },
    { "f64", 64, 53, 52, 1023, -1022, -1073, 1024 },
};

static const mpfr_rnd_t RND[4] = { MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU, MPFR_RNDD };
/* public mode order te, tz, tp, tn matches msf_rounding_t */
static const char *RM_NAME[4] = { "te", "tz", "tp", "tn" };

static uint64_t g_checked, g_mismatch, g_escal, g_undecided;
static uint64_t g_audit, g_audit_fail, g_special;

static void decode_bits(const fmt_t *f, uint64_t bits, int *sign,
                        uint64_t *sig, int *exp2, int *cls)
{
    /* cls: 0 zero, 1 finite nonzero, 2 inf, 3 qnan, 4 snan.
     * finite: value = sig * 2^exp2 (sig without sign). */
    uint64_t ef = (bits >> f->t) & ((1ULL << (f->w - 1 - f->t)) - 1ULL);
    uint64_t frac = bits & ((1ULL << f->t) - 1ULL);
    uint64_t emaxf = (1ULL << (f->w - 1 - f->t)) - 1ULL;
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

static uint64_t one_bits(const fmt_t *f, int sign)
{
    return ((uint64_t)sign << (f->w - 1))
         | ((uint64_t)(unsigned)f->bias << f->t);
}

/* Decide specials from the settled table. Returns 1 when the
 * input is special (NaN/inf/zero/integer/half-integer) and
 * fills rb[4]/rf[4]; 0 otherwise. */
static int decide_special(const fmt_t *f, int is_cos, uint64_t bits,
                          uint64_t rb[4], uint32_t rf[4])
{
    int sign, exp2, cls, i;
    uint64_t sig;
    uint64_t emaxf = (1ULL << (f->w - 1 - f->t)) - 1ULL;
    decode_bits(f, bits, &sign, &sig, &exp2, &cls);
    for (i = 0; i < 4; i++) {
        rf[i] = 0u;
    }
    if (cls == 3 || cls == 4) {
        uint64_t r = bits | (1ULL << (f->t - 1));
        for (i = 0; i < 4; i++) {
            rb[i] = r;
            rf[i] = cls == 4 ? 0x01u : 0u;
        }
        return 1;
    }
    if (cls == 2) {
        uint64_t r = (emaxf << f->t) | (1ULL << (f->t - 1));
        for (i = 0; i < 4; i++) {
            rb[i] = r;
            rf[i] = 0x01u;
        }
        return 1;
    }
    if (cls == 0) {
        for (i = 0; i < 4; i++) {
            rb[i] = is_cos ? one_bits(f, 0)
                           : ((uint64_t)sign << (f->w - 1));
        }
        return 1;
    }
    /* finite nonzero: integer iff exp2 >= 0 or low -exp2 bits
     * of sig are zero; half-integer iff exactly the bit above
     * that field is the single fractional bit. */
    {
        int is_int = 0, is_half = 0;
        uint64_t ival = 0;
        if (exp2 >= 0) {
            is_int = 1;
            ival = exp2 == 0 ? sig : 0u; /* parity only needed */
            if (is_cos) {
                int par = exp2 == 0 ? (int)(sig & 1u) : 0;
                for (i = 0; i < 4; i++) rb[i] = one_bits(f, par);
            } else {
                for (i = 0; i < 4; i++)
                    rb[i] = (uint64_t)sign << (f->w - 1);
            }
            return 1;
        }
        {
            int k = -exp2;
            if (k < 64) {
                uint64_t rem = sig & ((1ULL << k) - 1ULL);
                ival = sig >> k;
                is_int = rem == 0u;
                is_half = rem == (1ULL << (k - 1));
            }
        }
        if (is_int) {
            if (is_cos) {
                for (i = 0; i < 4; i++) rb[i] = one_bits(f, (int)(ival & 1u));
            } else {
                for (i = 0; i < 4; i++)
                    rb[i] = (uint64_t)sign << (f->w - 1);
            }
            return 1;
        }
        if (is_half) {
            if (is_cos) {
                for (i = 0; i < 4; i++) rb[i] = 0u; /* +0 all modes */
            } else {
                for (i = 0; i < 4; i++)
                    rb[i] = one_bits(f, sign ^ (int)(ival & 1u));
            }
            return 1;
        }
    }
    return 0;
}

/* Exact nonnegative integer held in an mpfr (prec >= 64) to
 * uint64_t; mpfr_get_ui alone truncates to the 32-bit
 * unsigned long of this host's C library. */
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

/* Narrow exact-ish mpfr value v (|v| <= 1 in this harness) to
 * format f under public mode rm. Bits to *rb, flags to *rf. */
static void narrow(const fmt_t *f, mpfr_t v, int rm,
                   uint64_t *rb, uint32_t *rf)
{
    /* cached work variables (single-threaded harness) */
    static mpfr_t r, w, tmp;
    static int cur_p = 0;
    int tern, inexact, tiny;
    uint64_t sign_bit;
    if (cur_p != f->p) {
        if (cur_p != 0) {
            mpfr_clear(r);
            mpfr_clear(w);
            mpfr_clear(tmp);
        }
        mpfr_init2(r, (mpfr_prec_t)f->p);
        mpfr_init2(w, (mpfr_prec_t)f->p);
        mpfr_init2(tmp, 128);
        cur_p = f->p;
    }
    /* unbounded-exponent rounding first (tininess judge) */
    mpfr_set(w, v, RND[rm]);
    mpfr_set_si_2exp(tmp, 1, f->emin, MPFR_RNDN);
    tiny = mpfr_cmpabs(w, tmp) < 0;
    mpfr_set_emin(f->mpf_emin);
    mpfr_set_emax(f->mpf_emax);
    tern = mpfr_set(r, v, RND[rm]);
    tern = mpfr_check_range(r, tern, RND[rm]);
    if (!mpfr_zero_p(r) && !mpfr_inf_p(r) && !mpfr_nan_p(r)) {
        tern = mpfr_subnormalize(r, tern, RND[rm]);
    }
    mpfr_set_emin(mpfr_get_emin_min());
    mpfr_set_emax(mpfr_get_emax_max());
    inexact = tern != 0;
    sign_bit = (uint64_t)(mpfr_signbit(r) != 0) << (f->w - 1);
    if (mpfr_zero_p(r)) {
        *rb = sign_bit;
    } else {
        long e = (long)mpfr_get_exp(r) - 1; /* value in [2^e, 2^(e+1)) */
        mpfr_abs(tmp, r, MPFR_RNDN);
        if (e >= f->emin) {
            uint64_t m;
            mpfr_mul_2si(tmp, tmp, (long)(f->t) - (long)e, MPFR_RNDN);
            m = get_u64_from_int(tmp);
            *rb = sign_bit
                | ((uint64_t)(unsigned long)(e + f->bias) << f->t)
                | (m - (1ULL << f->t));
        } else {
            uint64_t m;
            mpfr_mul_2si(tmp, tmp, -(long)(f->emin - f->t), MPFR_RNDN);
            m = get_u64_from_int(tmp);
            *rb = sign_bit | m;
        }
    }
    *rf = (inexact ? 0x10u : 0u) | ((inexact && tiny) ? 0x08u : 0u);
}

/* MPFR-decide one non-special finite input at starting
 * precision p0 (symmetry NOT applied here). Returns 0 on
 * success, -1 when even the widest bracket is undecided. */
static int decide_mpfr_raw(const fmt_t *f, int is_cos, uint64_t bits,
                           long p0, uint64_t rb[4], uint32_t rf[4])
{
    /* final precision must resolve 1-|y| for the saturation
     * family: smallest binary64 input gives delta ~ 2^-2145 */
    static const long ESC[4] = { 384, 768, 1536, 2560 };
    int sign, exp2, cls, attempt, rm;
    uint64_t sig;
    decode_bits(f, bits, &sign, &sig, &exp2, &cls);
    for (attempt = 0; attempt < 5; attempt++) {
        long prec = attempt == 0 ? p0 : ESC[attempt - 1];
        static mpfr_t x, y, ylo, yhi;
        static long cur_prec = 0;
        int ok = 1;
        if (attempt > 0) {
            g_escal++;
        }
        if (cur_prec != prec) {
            if (cur_prec != 0) {
                mpfr_clear(x);
                mpfr_clear(y);
                mpfr_clear(ylo);
                mpfr_clear(yhi);
            }
            mpfr_init2(x, (mpfr_prec_t)prec);
            mpfr_init2(y, (mpfr_prec_t)prec);
            mpfr_init2(ylo, (mpfr_prec_t)prec);
            mpfr_init2(yhi, (mpfr_prec_t)prec);
            cur_prec = prec;
        }
        mpfr_set_ui(x, (unsigned long)sig, MPFR_RNDN);
        if (sig >> 32) {
            /* set_ui took only the low word on 32-bit ulong */
            mpfr_set_ui(ylo, (unsigned long)(sig >> 32), MPFR_RNDN);
            mpfr_mul_2si(ylo, ylo, 32, MPFR_RNDN);
            mpfr_add(x, x, ylo, MPFR_RNDN);
        }
        mpfr_mul_2si(x, x, exp2, MPFR_RNDN);
        if (sign) {
            mpfr_neg(x, x, MPFR_RNDN);
        }
        if (is_cos) {
            mpfr_cospi(y, x, MPFR_RNDN);
        } else {
            mpfr_sinpi(y, x, MPFR_RNDN);
        }
        mpfr_set(ylo, y, MPFR_RNDN);
        mpfr_nextbelow(ylo);
        mpfr_nextbelow(ylo);
        mpfr_set(yhi, y, MPFR_RNDN);
        mpfr_nextabove(yhi);
        mpfr_nextabove(yhi);
        if (f->w == 16) {
            for (rm = 0; rm < 4 && ok; rm++) {
                uint64_t blo, bhi;
                uint32_t flo, fhi;
                narrow(f, ylo, rm, &blo, &flo);
                narrow(f, yhi, rm, &bhi, &fhi);
                if (blo != bhi || flo != fhi) {
                    ok = 0;
                } else {
                    rb[rm] = blo;
                    rf[rm] = flo;
                }
            }
        } else {
            /* Fast narrow: MPFR converts the bracket ends to
             * the C type of the format (correctly rounded,
             * subnormals included). Bits agreement decides;
             * flags follow: inexact unless the delivered value
             * could still be the exact value inside the bracket
             * (then escalate precision); subnormal-scale
             * deliveries take flags from the recipe narrow. */
            uint64_t minnorm = (uint64_t)1u << f->t;
            for (rm = 0; rm < 4 && ok; rm++) {
                uint64_t blo = 0u, bhi = 0u, mag;
                if (f->w == 32) {
                    float a = mpfr_get_flt(ylo, RND[rm]);
                    float b = mpfr_get_flt(yhi, RND[rm]);
                    memcpy(&blo, &a, 4);
                    memcpy(&bhi, &b, 4);
                    blo &= 0xffffffffULL;
                    bhi &= 0xffffffffULL;
                } else {
                    double a = mpfr_get_d(ylo, RND[rm]);
                    double b = mpfr_get_d(yhi, RND[rm]);
                    memcpy(&blo, &a, 8);
                    memcpy(&bhi, &b, 8);
                }
                if (blo != bhi) {
                    ok = 0;
                    break;
                }
                mag = blo & ((1ULL << (f->w - 1)) - 1ULL);
                if (mag <= minnorm) {
                    uint64_t nlo, nhi;
                    uint32_t flo, fhi;
                    narrow(f, ylo, rm, &nlo, &flo);
                    narrow(f, yhi, rm, &nhi, &fhi);
                    if (nlo != nhi || flo != fhi || nlo != blo) {
                        ok = 0;
                        break;
                    }
                    rb[rm] = blo;
                    rf[rm] = flo;
                } else {
                    static mpfr_t dv;
                    static int dvin = 0;
                    if (!dvin) { mpfr_init2(dv, 128); dvin = 1; }
                    if (f->w == 32) {
                        float a;
                        uint32_t t32 = (uint32_t)blo;
                        memcpy(&a, &t32, 4);
                        mpfr_set_flt(dv, a, MPFR_RNDN);
                    } else {
                        double a;
                        memcpy(&a, &blo, 8);
                        mpfr_set_d(dv, a, MPFR_RNDN);
                    }
                    if (mpfr_cmp(dv, ylo) >= 0 && mpfr_cmp(dv, yhi) <= 0) {
                        ok = 0; /* delivered could be exact: escalate */
                        break;
                    }
                    rb[rm] = blo;
                    rf[rm] = 0x10u;
                }
            }
        }
        if (ok) {
            return 0;
        }
    }
    return -1;
}

/* Full decider: specials, then MPFR with exact odd/even
 * symmetry for negative inputs (audited by caller stride). */
static int decide(const fmt_t *f, int is_cos, uint64_t bits, long p0,
                  uint64_t rb[4], uint32_t rf[4])
{
    if (decide_special(f, is_cos, bits, rb, rf)) {
        g_special++;
        return 0;
    }
    if ((bits >> (f->w - 1)) & 1u) {
        uint64_t pb[4];
        uint32_t pf[4];
        uint64_t pos = bits & ~(1ULL << (f->w - 1));
        if (decide_mpfr_raw(f, is_cos, pos, p0, pb, pf) != 0) {
            return -1;
        }
        if (is_cos) {
            memcpy(rb, pb, sizeof pb);
            memcpy(rf, pf, sizeof pf);
        } else {
            /* odd: -f(x) with tp<->tn exchanged */
            static const int SWAP[4] = { 0, 1, 3, 2 };
            int rm;
            for (rm = 0; rm < 4; rm++) {
                rb[rm] = pb[SWAP[rm]] ^ (1ULL << (f->w - 1));
                rf[rm] = pf[SWAP[rm]];
            }
        }
        return 0;
    }
    return decide_mpfr_raw(f, is_cos, bits, p0, rb, rf);
}

static uint64_t kernel_call(int fi, int is_cos, uint64_t bits, int rm,
                            msf_flags_t *fl)
{
    *fl = 0u;
    switch (fi) {
    case 0:
        return is_cos ? msf16_cos_pi((msf16_t)bits, (msf_rounding_t)rm, fl)
                      : msf16_sin_pi((msf16_t)bits, (msf_rounding_t)rm, fl);
    case 1:
        return is_cos ? msf32_cos_pi((msf32_t)bits, (msf_rounding_t)rm, fl)
                      : msf32_sin_pi((msf32_t)bits, (msf_rounding_t)rm, fl);
    default:
        return is_cos ? msf64_cos_pi((msf64_t)bits, (msf_rounding_t)rm, fl)
                      : msf64_sin_pi((msf64_t)bits, (msf_rounding_t)rm, fl);
    }
}

static uint64_t g_audit_seq;
#define AUDIT_STRIDE 999983ULL

static void check_with_expected(int fi, int is_cos, uint64_t bits,
                                const uint64_t rb[4], const uint32_t rf[4])
{
    const fmt_t *f = &FMTS[fi];
    int rm;
    for (rm = 0; rm < 4; rm++) {
        msf_flags_t fl;
        uint64_t got = kernel_call(fi, is_cos, bits, rm, &fl);
        g_checked++;
        if (got != rb[rm] || (uint32_t)fl != rf[rm]) {
            g_mismatch++;
            if (g_mismatch <= 20) {
                printf("MISMATCH %s %s %s in=%016llx got=%016llx/%02x "
                       "want=%016llx/%02x\n",
                       f->name, is_cos ? "cosPi" : "sinPi", RM_NAME[rm],
                       (unsigned long long)bits,
                       (unsigned long long)got, (unsigned)fl,
                       (unsigned long long)rb[rm], (unsigned)rf[rm]);
            }
        }
    }
}

static void check_one(int fi, int is_cos, uint64_t bits, long p0)
{
    const fmt_t *f = &FMTS[fi];
    uint64_t rb[4];
    uint32_t rf[4];
    if (decide(f, is_cos, bits, p0, rb, rf) != 0) {
        g_undecided++;
        if (g_undecided <= 20) {
            printf("UNDECIDED %s %s %016llx\n", f->name,
                   is_cos ? "cosPi" : "sinPi",
                   (unsigned long long)bits);
        }
        return;
    }
    /* stride audit of the symmetry shortcut with raw MPFR;
     * specials are decided by table in both paths and the raw
     * bracket cannot represent their exact zeros, so audit
     * only non-special inputs */
    {
        uint64_t sb[4];
        uint32_t sf[4];
        int special = decide_special(f, is_cos, bits, sb, sf);
        if (!special && ((bits >> (f->w - 1)) & 1u)
            && (++g_audit_seq % AUDIT_STRIDE) == 0) {
        uint64_t ab[4];
        uint32_t af[4];
        g_audit++;
        if (decide_mpfr_raw(f, is_cos, bits, 384, ab, af) != 0
            || memcmp(ab, rb, sizeof ab) != 0
            || memcmp(af, rf, sizeof af) != 0) {
            g_audit_fail++;
            printf("AUDIT-FAIL %s %s %016llx\n", f->name,
                   is_cos ? "cosPi" : "sinPi",
                   (unsigned long long)bits);
        }
        }
    }
    check_with_expected(fi, is_cos, bits, rb, rf);
}

/* Binary32 magnitude pair: decide the positive encoding once
 * (MPFR), derive the negative twin by the exact odd/even
 * symmetry, kernel-check both encodings in all modes. The
 * specials live inside decide(); symmetry transforms there
 * apply only to non-specials, so for special magnitudes the
 * negative twin is decided on its own encoding instead. */
static void check_pair32(int is_cos, uint64_t mag, long p0)
{
    const fmt_t *f = &FMTS[1];
    uint64_t rb[4], nb[4];
    uint32_t rf[4], nf[4];
    int special = decide_special(f, is_cos, mag, rb, rf);
    if (special) {
        g_special++;
    } else if (decide_mpfr_raw(f, is_cos, mag, p0, rb, rf) != 0) {
        g_undecided++;
        if (g_undecided <= 20) {
            printf("UNDECIDED f32 %s %016llx\n",
                   is_cos ? "cosPi" : "sinPi", (unsigned long long)mag);
        }
        return;
    }
    check_with_expected(1, is_cos, mag, rb, rf);
    if (mag == 0) {
        /* -0 is its own special; decide directly */
        check_one(1, is_cos, 0x80000000ULL, p0);
        return;
    }
    if (special) {
        if (decide(f, is_cos, mag | 0x80000000ULL, p0, nb, nf) != 0) {
            g_undecided++;
            return;
        }
    } else if (is_cos) {
        memcpy(nb, rb, sizeof nb);
        memcpy(nf, rf, sizeof nf);
    } else {
        static const int SWAP[4] = { 0, 1, 3, 2 };
        int rm;
        for (rm = 0; rm < 4; rm++) {
            nb[rm] = rb[SWAP[rm]] ^ 0x80000000ULL;
            nf[rm] = rf[SWAP[rm]];
        }
    }
    /* stride audit of the symmetry transform with raw MPFR */
    if (!special && (++g_audit_seq % AUDIT_STRIDE) == 0) {
        uint64_t ab[4];
        uint32_t af[4];
        g_audit++;
        if (decide_mpfr_raw(f, is_cos, mag | 0x80000000ULL, 384, ab, af) != 0
            || memcmp(ab, nb, sizeof ab) != 0
            || memcmp(af, nf, sizeof af) != 0) {
            g_audit_fail++;
            printf("AUDIT-FAIL f32 %s %016llx\n",
                   is_cos ? "cosPi" : "sinPi", (unsigned long long)mag);
        }
    }
    check_with_expected(1, is_cos, mag | 0x80000000ULL, nb, nf);
}

static int is_finite_bits(const fmt_t *f, uint64_t bits)
{
    uint64_t ef = (bits >> f->t) & ((1ULL << (f->w - 1 - f->t)) - 1ULL);
    return ef != (1ULL << (f->w - 1 - f->t)) - 1ULL;
}

static int summary(const char *what)
{
    int bad = g_mismatch != 0 || g_undecided != 0 || g_audit_fail != 0;
#ifdef MSF_TRIG_TEST_COUNTERS
    printf("counters: stage hits %llu/%llu/%llu final_undecided=%llu\n",
           (unsigned long long)msf_trig_stage_hits[0],
           (unsigned long long)msf_trig_stage_hits[1],
           (unsigned long long)msf_trig_stage_hits[2],
           (unsigned long long)msf_trig_final_undecided);
    if (msf_trig_final_undecided != 0) {
        bad = 1;
    }
#endif
    printf("%s: checked=%llu mismatches=%llu undecided=%llu "
           "decider_escalations=%llu specials=%llu audits=%llu "
           "audit_fail=%llu -> %s\n",
           what,
           (unsigned long long)g_checked,
           (unsigned long long)g_mismatch,
           (unsigned long long)g_undecided,
           (unsigned long long)g_escal,
           (unsigned long long)g_special,
           (unsigned long long)g_audit,
           (unsigned long long)g_audit_fail,
           bad ? "FAIL" : "PASS");
    return bad ? 1 : 0;
}

static int run_wc(int is_cos, const char *path, const char *dump_path)
{
    FILE *fh = fopen(path, "r");
    FILE *dump = NULL;
    char line[512];
    uint64_t ntok = 0, nnonfinite = 0, nunparsed = 0, ninexact = 0;
    int rc;
    if (fh == NULL) {
        fprintf(stderr, "wc: cannot open %s\n", path);
        return 2;
    }
    if (dump_path != NULL) {
        dump = fopen(dump_path, "w");
        if (dump == NULL) {
            fprintf(stderr, "wc: cannot open dump %s\n", dump_path);
            fclose(fh);
            return 2;
        }
    }
    printf("wc %s from %s (mechanical parse; MPFR re-decides)\n",
           is_cos ? "cosPi" : "sinPi", path);
    while (fgets(line, sizeof line, fh) != NULL) {
        char *hash = strchr(line, '#');
        char tok[256];
        if (hash != NULL) {
            *hash = '\0';
        }
        if (sscanf(line, "%255s", tok) != 1) {
            continue;
        }
        ntok++;
        {
            /* The token denotes its correctly rounded nearest
             * binary64 (the float.fromhex / strtod reading the
             * Step 2b census used); parse at high precision,
             * then narrow ties-to-even. */
            mpfr_t v;
            char *end = NULL;
            uint64_t rb;
            uint32_t rf;
            mpfr_init2(v, 4096);
            mpfr_strtofr(v, tok, &end, 0, MPFR_RNDN);
            if (end == tok || *end != '\0') {
                nunparsed++; /* counted only; token never printed */
                mpfr_clear(v);
                continue;
            }
            if (mpfr_nan_p(v) || mpfr_inf_p(v)) {
                nnonfinite++;
                mpfr_clear(v);
                continue;
            }
            {
                mpfr_t lim;
                mpfr_init2(lim, 64);
                mpfr_set_si_2exp(lim, 1, 1024, MPFR_RNDN);
                if (mpfr_cmpabs(v, lim) >= 0) {
                    nnonfinite++; /* rounds to infinity */
                    mpfr_clear(lim);
                    mpfr_clear(v);
                    continue;
                }
                mpfr_clear(lim);
            }
            narrow(&FMTS[2], v, 0, &rb, &rf);
            if (rf != 0u) {
                ninexact++; /* token rounded to its binary64 */
            }
            mpfr_clear(v);
            if (((rb >> 52) & 0x7ffu) == 0x7ffu) {
                nnonfinite++;
                continue;
            }
            if (dump != NULL) {
                fprintf(dump, "%016llx\n", (unsigned long long)rb);
            }
            check_one(2, is_cos, rb, 320);
        }
    }
    fclose(fh);
    if (dump != NULL) {
        fclose(dump);
    }
    printf("wc tokens=%llu unparsed=%llu nonfinite_skipped=%llu "
           "inexact_tokens=%llu\n",
           (unsigned long long)ntok,
           (unsigned long long)nunparsed,
           (unsigned long long)nnonfinite,
           (unsigned long long)ninexact);
    rc = summary(is_cos ? "wc cosPi f64" : "wc sinPi f64");
    return rc;
}

static const fmt_t *fmt_from_op(const char *op, int *fi, int *is_cos)
{
    if (strncmp(op, "msf16_", 6) == 0) { *fi = 0; }
    else if (strncmp(op, "msf32_", 6) == 0) { *fi = 1; }
    else if (strncmp(op, "msf64_", 6) == 0) { *fi = 2; }
    else { return NULL; }
    if (strcmp(op + 6, "sin_pi") == 0) { *is_cos = 0; }
    else if (strcmp(op + 6, "cos_pi") == 0) { *is_cos = 1; }
    else { return NULL; }
    return &FMTS[*fi];
}

static int run_decide(void)
{
    char op[64], hex[32];
    while (scanf("%63s %31s", op, hex) == 2) {
        int fi = 0, is_cos = 0, rm;
        const fmt_t *f = fmt_from_op(op, &fi, &is_cos);
        uint64_t bits, rb[4];
        uint32_t rf[4];
        if (f == NULL) {
            printf("BADOP %s\n", op);
            return 2;
        }
        bits = strtoull(hex, NULL, 16);
        if (decide(f, is_cos, bits, 640, rb, rf) != 0) {
            printf("UNDECIDED %s %s\n", op, hex);
            return 1;
        }
        printf("%s %s", op, hex);
        for (rm = 0; rm < 4; rm++) {
            printf(" %llx %02x", (unsigned long long)rb[rm],
                   (unsigned)rf[rm]);
        }
        printf("\n");
        fflush(stdout);
    }
    return 0;
}

static uint64_t rng_state;
static uint64_t rng_next(void)
{
    uint64_t z = (rng_state += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: trig_exhaustive "
                "f16|f32 LO HI|f64seed SEED N|wc sin|cos FILE|decide\n");
        return 2;
    }
    printf("mpfr %s\n", mpfr_get_version());
    if (strcmp(argv[1], "f16") == 0) {
        uint64_t bits;
        for (bits = 0; bits < 0x10000u; bits++) {
            if (!is_finite_bits(&FMTS[0], bits)) {
                continue;
            }
            check_one(0, 0, bits, 160);
            check_one(0, 1, bits, 160);
        }
        return summary("f16 exhaustive");
    }
    if (strcmp(argv[1], "f32") == 0 && argc == 4) {
        /* LO..HI is a magnitude range (sign bit clear); each
         * shard checks both signs of every finite magnitude. */
        uint64_t lo = strtoull(argv[2], NULL, 0);
        uint64_t hi = strtoull(argv[3], NULL, 0);
        uint64_t mag;
        printf("f32 shard magnitudes [%llu, %llu) both signs\n",
               (unsigned long long)lo, (unsigned long long)hi);
        for (mag = lo; mag < hi; mag++) {
            if (!is_finite_bits(&FMTS[1], mag)) {
                continue;
            }
            check_pair32(0, mag, 96);
            check_pair32(1, mag, 96);
            if (g_mismatch > 100000u) {
                printf("f32 shard: aborting after 100000 mismatches\n");
                return summary("f32 shard (aborted)");
            }
        }
        return summary("f32 shard");
    }
    if (strcmp(argv[1], "f64seed") == 0 && argc == 4) {
        uint64_t count = strtoull(argv[3], NULL, 0);
        uint64_t i;
        rng_state = strtoull(argv[2], NULL, 0);
        printf("f64 seeded: seed=%s per-function count target %llu\n",
               argv[2], (unsigned long long)count);
        for (i = 0; i < count; ) {
            uint64_t bits = rng_next();
            if (!is_finite_bits(&FMTS[2], bits)) {
                continue;
            }
            check_one(2, 0, bits, 160);
            check_one(2, 1, bits, 160);
            i++;
        }
        return summary("f64 seeded");
    }
    if (strcmp(argv[1], "wc") == 0 && (argc == 4 || argc == 5)) {
        return run_wc(strcmp(argv[2], "cos") == 0, argv[3],
                      argc == 5 ? argv[4] : NULL);
    }
    if (strcmp(argv[1], "decide") == 0) {
        return run_decide();
    }
    fprintf(stderr, "bad mode\n");
    return 2;
}

