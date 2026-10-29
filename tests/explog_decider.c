/* explog_decider.c - independent MPFR decider for the
 * exp2/exp2m1 bundle (SF-2 Step 3a gates; NOT part of the
 * shipped library). Included by tests/explog_exhaustive.c.
 *
 * Method (trig_exhaustive.c idiom, five modes): the exact
 * input is reconstructed from its bit pattern,
 * mpfr_exp2/mpfr_exp2m1 evaluate it at working precision P
 * (RNDN), the value is bracketed by two nextabove/nextbelow
 * steps, and both bracket ends are narrowed to the
 * destination format in all FIVE public modes by a
 * first-principles integer-grid narrow (scaled integer +
 * fraction compared against 1/2; ties-to-even reads the
 * integer parity, ties-to-away rounds the half up in
 * magnitude - raw MPFR RNDNA is never used, per SF-2
 * Sec. 2). Agreement of bits and flags at both ends
 * decides; otherwise P escalates 384 -> 768 -> 1536 ->
 * 3072 (adaptive precision: bracket narrowing is immune to
 * the fixed-precision collapse near attractors that the
 * SF-2 spike Sec. 2.4 measured, because a collapsed value
 * straddles the grid point and directed ends disagree).
 * Flags are first principles (inexact = nonzero discarded
 * tail at the delivered grid; overflow = the unbounded
 * prec-p rounding exceeds the largest finite, delivery by
 * mode, inexact attached; underflow = inexact and the
 * unbounded prec-p rounding lies below 2^emin, tininess
 * after rounding); MPFR exception flags are never read.
 * Specials and every integer input (the exact/tie table of
 * ledger/parcel-w5exp2.md Sec. 3) are decided here from the
 * settled Clause 9.2 table and exact dyadic construction,
 * independently of the kernel. Structural far-cut
 * shortcuts exist only with >= 60 bits of margin beyond
 * every kernel threshold (proxy exact values narrowed by
 * the same grid) and are counted; the exp2m1 saturation
 * strip and every boundary neighbourhood always take the
 * full bracket - no foreign oracle is executed anywhere
 * (the spike Sec. 5 named fence: MPFR decides). Stride
 * audits cross-check grid-narrowed bits against
 * mpfr_get_flt/mpfr_get_d (binary32/64, four MPFR modes).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <mpfr.h>
#include "../include/muse_softfloat.h"

typedef struct {
    const char *name;
    int w, p, t, bias, emin, emax;
} xfmt_t;

static const xfmt_t XFMTS[3] = {
    { "f16", 16, 11, 10, 15, -14, 15 },
    { "f32", 32, 24, 23, 127, -126, 127 },
    { "f64", 64, 53, 52, 1023, -1022, 1023 },
};

/* public mode order te tz tp tn ta == msf_rounding_t */
static const char *XRM_NAME[5] = { "te", "tz", "tp", "tn", "ta" };
/* function ids: Step 3a pair + Step 3b pair (extension) */
static const char *XFN_NAME[4] = { "exp2", "exp2m1", "log2", "log2p1" };
static const mpfr_rnd_t XRND[4] = { MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU,
                                    MPFR_RNDD };

static uint64_t g_x_escal, g_x_undecided, g_x_special, g_x_shortcut;
static uint64_t g_x_audit, g_x_audit_fail, g_x_audit_seq;
#define X_AUDIT_STRIDE 99991ULL

static void x_decode(const xfmt_t *f, uint64_t bits, int *sign,
                     uint64_t *sig, int *exp2, int *cls)
{
    /* cls: 0 zero, 1 finite nonzero, 2 inf, 3 qnan, 4 snan */
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

static int x_bitlen(uint64_t v)
{
    int n = 0;
    while (v != 0u) {
        n++;
        v >>= 1;
    }
    return n;
}

/* Exact nonnegative integer in an mpfr to uint64_t without
 * relying on a 64-bit unsigned long (host is 32-bit ulong). */
static uint64_t x_get_u64(mpfr_t v)
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

/* Round exact |a| (a >= 0) on the grid of spacing 2^g.
 * Writes the rounded integer multiple count to *iu (the
 * result is *iu * 2^g; caller guarantees *iu < 2^64), and
 * sets *inexact. Mode rm is a magnitude rounding with the
 * result sign given separately for directed modes. */
static void x_round_grid(mpfr_t a, long g, int sign, int rm,
                         uint64_t *iu, int *inexact)
{
    static mpfr_t sc, iv, fr, half;
    static long cur_prec = 0;
    int cmp, inc = 0, nonzero;
    long need = (long)mpfr_get_prec(a) + 64;
    if (cur_prec < need) {
        if (cur_prec != 0) {
            mpfr_clear(sc);
            mpfr_clear(iv);
            mpfr_clear(fr);
        } else {
            mpfr_init2(half, 64);
            mpfr_set_si_2exp(half, 1, -1, MPFR_RNDN);
        }
        mpfr_init2(sc, (mpfr_prec_t)need);
        mpfr_init2(iv, (mpfr_prec_t)need);
        mpfr_init2(fr, (mpfr_prec_t)need);
        cur_prec = need;
    }
    mpfr_mul_2si(sc, a, -g, MPFR_RNDN);
    mpfr_trunc(iv, sc);
    mpfr_sub(fr, sc, iv, MPFR_RNDN);
    nonzero = !mpfr_zero_p(fr);
    cmp = mpfr_cmp(fr, half);
    *iu = x_get_u64(iv);
    switch (rm) {
    case 0: /* ties to even */
        inc = cmp > 0 || (cmp == 0 && (*iu & 1u));
        break;
    case 1: /* toward zero */
        inc = 0;
        break;
    case 2: /* toward positive */
        inc = !sign && nonzero;
        break;
    case 3: /* toward negative */
        inc = sign && nonzero;
        break;
    default: /* ties to away */
        inc = cmp >= 0;
        break;
    }
    if (inc) {
        *iu += 1u;
    }
    *inexact = nonzero;
}

/* Narrow the exact mpfr value v to format f under public
 * mode rm (0..4). Bits to *rb, Clause 7 flags to *rf. */
static void x_narrow(const xfmt_t *f, mpfr_t v, int rm,
                     uint64_t *rb, uint32_t *rf)
{
    static mpfr_t a;
    static long cur_prec = 0;
    int sign, inexact = 0, tiny = 0;
    long e, g;
    uint64_t iu = 0u, sign_bit;
    long need = (long)mpfr_get_prec(v) + 64;
    if (cur_prec < need) {
        if (cur_prec != 0) {
            mpfr_clear(a);
        }
        mpfr_init2(a, (mpfr_prec_t)need);
        cur_prec = need;
    }
    sign = mpfr_signbit(v) != 0;
    sign_bit = (uint64_t)sign << (f->w - 1);
    mpfr_abs(a, v, MPFR_RNDN);
    if (mpfr_zero_p(a)) {
        *rb = sign_bit;
        *rf = 0u;
        return;
    }
    e = (long)mpfr_get_exp(a) - 1; /* |v| in [2^e, 2^(e+1)) */
    g = e >= f->emin ? e - (f->p - 1) : (long)f->emin - (f->p - 1);
    x_round_grid(a, g, sign, rm, &iu, &inexact);
    if (e < f->emin) {
        /* tininess judge: unbounded prec-p rounding */
        uint64_t iuu = 0u;
        int ixu = 0;
        long topu;
        x_round_grid(a, e - (f->p - 1), sign, rm, &iuu, &ixu);
        topu = iuu == 0u ? e - 1
                         : (e - (f->p - 1)) + x_bitlen(iuu) - 1;
        tiny = topu < f->emin;
    }
    if (iu >= (1ULL << f->p)) { /* binade carry: iu == 2^p */
        iu >>= 1;
        g += 1;
    }
    if (iu != 0u) {
        long top = g + x_bitlen(iu) - 1;
        if (top > f->emax) {
            int to_inf = rm == 0 || rm == 4
                      || (rm == 2 && !sign) || (rm == 3 && sign);
            uint64_t emaxf = (1ULL << (f->w - 1 - f->t)) - 1ULL;
            if (to_inf) {
                *rb = sign_bit | (emaxf << f->t);
            } else {
                *rb = sign_bit | ((emaxf - 1u) << f->t)
                    | ((1ULL << f->t) - 1ULL);
            }
            *rf = 0x04u | 0x10u;
            return;
        }
    }
    if (iu >= (1ULL << (f->p - 1))) {
        long eunb = g + (f->p - 1);
        *rb = sign_bit | ((uint64_t)(unsigned long)(eunb + f->bias) << f->t)
            | (iu - (1ULL << (f->p - 1)));
    } else {
        *rb = sign_bit | iu;
    }
    *rf = (inexact ? 0x10u : 0u) | ((inexact && tiny) ? 0x08u : 0u);
}

/* Narrow a proxy exact value given as sign * 2^e (plus, for
 * the saturation proxy, an exact 1 - 2^-m form when
 * oneminus_m > 0: value = -(1 - 2^-m)). */
static void x_narrow_pow2(const xfmt_t *f, int sign, long e, int rm,
                          uint64_t *rb, uint32_t *rf)
{
    static mpfr_t v;
    static int init = 0;
    if (!init) {
        mpfr_init2(v, 256);
        init = 1;
    }
    mpfr_set_si_2exp(v, sign ? -1 : 1, (mpfr_exp_t)e, MPFR_RNDN);
    x_narrow(f, v, rm, rb, rf);
}

static void x_narrow_oneminus(const xfmt_t *f, long m, int rm,
                              uint64_t *rb, uint32_t *rf)
{
    static mpfr_t v;
    static int init = 0;
    if (!init) {
        mpfr_init2(v, 256);
        init = 1;
    }
    mpfr_set_ui_2exp(v, 1u, (mpfr_exp_t)m, MPFR_RNDN);
    mpfr_sub_ui(v, v, 1u, MPFR_RNDN);
    mpfr_mul_2si(v, v, (mpfr_exp_t)-m, MPFR_RNDN);
    mpfr_neg(v, v, MPFR_RNDN);
    x_narrow(f, v, rm, rb, rf);
}

/* Step 3b decided table (log2 fn=2, log2p1 fn=3): Clause
 * 9.2 specials/domain/poles and the power-of-two exacts of
 * ledger/parcel-w5log2.md Secs. 2-3, decided independently
 * of the kernel (log2 powers by sig test; log2p1 powers by
 * exact common-exponent integer test on (sig, exp2)). The
 * default qNaN here is inf|qbit positive (generated
 * MSF_F*_DEFAULT_QNAN, verified). No far-cut shortcuts. */
static int x_decide_table_log(const xfmt_t *f, int is_p1, uint64_t bits,
                              uint64_t rb[5], uint32_t rf[5],
                              int *via_shortcut)
{
    int sign, exp2, cls, rm;
    uint64_t sig;
    uint64_t emaxf = (1ULL << (f->w - 1 - f->t)) - 1ULL;
    uint64_t inf = emaxf << f->t;
    uint64_t sbit, qnan_def = inf | (1ULL << (f->t - 1));
    x_decode(f, bits, &sign, &sig, &exp2, &cls);
    *via_shortcut = 0;
    sbit = (uint64_t)sign << (f->w - 1);
    for (rm = 0; rm < 5; rm++) {
        rb[rm] = 0u;
        rf[rm] = 0u;
    }
    if (cls == 3 || cls == 4) {
        uint64_t r = bits | (1ULL << (f->t - 1));
        for (rm = 0; rm < 5; rm++) {
            rb[rm] = r;
            rf[rm] = cls == 4 ? 0x01u : 0u;
        }
        return 1;
    }
    if (cls == 2) {
        for (rm = 0; rm < 5; rm++) {
            rb[rm] = sign ? qnan_def : inf;
            rf[rm] = sign ? 0x01u : 0u;
        }
        return 1;
    }
    if (cls == 0) {
        for (rm = 0; rm < 5; rm++) {
            if (!is_p1) {
                rb[rm] = (1ULL << (f->w - 1)) | inf;
                rf[rm] = 0x02u;
            } else {
                rb[rm] = sbit;
            }
        }
        return 1;
    }
    if (!is_p1 && sign) {
        for (rm = 0; rm < 5; rm++) {
            rb[rm] = qnan_def;
            rf[rm] = 0x01u;
        }
        return 1;
    }
    if (is_p1 && sign) {
        /* |x| vs 1 exactly: top = floor(log2|x|) */
        long top = (long)exp2 + x_bitlen(sig) - 1;
        int gt1 = top >= 1;
        int eq1 = 0;
        if (top == 0) {
            eq1 = exp2 <= 0 && -exp2 < 64
               && sig == (1ULL << (unsigned)-exp2);
            gt1 = !eq1;
        }
        if (gt1) {
            for (rm = 0; rm < 5; rm++) {
                rb[rm] = qnan_def;
                rf[rm] = 0x01u;
            }
            return 1;
        }
        if (eq1) {
            for (rm = 0; rm < 5; rm++) {
                rb[rm] = (1ULL << (f->w - 1)) | inf;
                rf[rm] = 0x02u;
            }
            return 1;
        }
    }
    /* power-of-two exacts: result integer K */
    {
        long kk = 0;
        int is_pow = 0;
        if (!is_p1) {
            if ((sig & (sig - 1u)) == 0u) {
                is_pow = 1;
                kk = (long)exp2 + x_bitlen(sig) - 1;
            }
        } else {
            /* Exact integer test: w = 1+x is a power of two.
             * x = +-sig*2^exp2 (sig < 2^53). By cases on the
             * common-exponent integer N with w = N*2^exp2:
             * x>0,exp2>=0: w = sig*2^exp2+1 is a power only
             * for exp2==0 and sig+1 a power (else odd > 1).
             * exp2<0, -exp2<64: N = 2^-exp2 +- sig in u64.
             * exp2<0, -exp2>=64: |x| <= 2^-11 puts w strictly
             * between consecutive powers around 1: never. */
            if (!sign && exp2 >= 0) {
                if (exp2 == 0 && ((sig + 1u) & sig) == 0u) {
                    is_pow = 1;
                    kk = x_bitlen(sig);
                }
            } else if (exp2 < 0 && -exp2 < 64) {
                uint64_t nn = (1ULL << (unsigned)-exp2);
                nn = sign ? nn - sig : nn + sig;
                if (nn != 0u && (nn & (nn - 1u)) == 0u) {
                    is_pow = 1;
                    kk = (long)exp2 + x_bitlen(nn) - 1;
                }
            }
        }
        if (is_pow) {
            static mpfr_t kv;
            static int kinit = 0;
            if (!kinit) {
                mpfr_init2(kv, 256);
                kinit = 1;
            }
            mpfr_set_si(kv, kk, MPFR_RNDN);
            for (rm = 0; rm < 5; rm++) {
                x_narrow(f, kv, rm, &rb[rm], &rf[rm]);
            }
            return 1;
        }
    }
    (void)sbit;
    return 0;
}

/* Decided table: NaN/inf/zero specials, far-cut structural
 * proxies (>= 60 bits beyond kernel thresholds), and all
 * integer inputs by exact dyadic construction. Returns 1
 * and fills rb[5]/rf[5] when decided here. */
static int x_decide_table(const xfmt_t *f, int fn, uint64_t bits,
                          uint64_t rb[5], uint32_t rf[5], int *via_shortcut)
{
    int is_m1 = fn == 1;
    int sign, exp2, cls, rm;
    if (fn >= 2) {
        return x_decide_table_log(f, fn == 3, bits, rb, rf, via_shortcut);
    }
    uint64_t sig;
    uint64_t emaxf = (1ULL << (f->w - 1 - f->t)) - 1ULL;
    long etie = (long)f->emin - f->p;
    x_decode(f, bits, &sign, &sig, &exp2, &cls);
    *via_shortcut = 0;
    for (rm = 0; rm < 5; rm++) {
        rb[rm] = 0u;
        rf[rm] = 0u;
    }
    if (cls == 3 || cls == 4) {
        uint64_t r = bits | (1ULL << (f->t - 1));
        for (rm = 0; rm < 5; rm++) {
            rb[rm] = r;
            rf[rm] = cls == 4 ? 0x01u : 0u;
        }
        return 1;
    }
    if (cls == 2) {
        uint64_t r;
        if (!sign) {
            r = emaxf << f->t;
        } else if (is_m1) {
            r = (1ULL << (f->w - 1)) | ((uint64_t)(unsigned)f->bias << f->t);
        } else {
            r = 0u;
        }
        for (rm = 0; rm < 5; rm++) {
            rb[rm] = r;
        }
        return 1;
    }
    if (cls == 0) {
        uint64_t r = is_m1 ? ((uint64_t)sign << (f->w - 1))
                           : ((uint64_t)(unsigned)f->bias << f->t);
        for (rm = 0; rm < 5; rm++) {
            rb[rm] = r;
        }
        return 1;
    }
    /* finite nonzero. top = floor(log2|x|). */
    {
        long top = (long)exp2 + x_bitlen(sig) - 1;
        int is_int = 0;
        int64_t nval = 0;
        if (exp2 >= 0) {
            is_int = 1;
            if (top < 62) {
                nval = (int64_t)(sig << (unsigned)exp2);
            }
        } else if (-exp2 < 64) {
            uint64_t rem = sig & ((1ULL << (unsigned)-exp2) - 1ULL);
            is_int = rem == 0u;
            nval = (int64_t)(sig >> (unsigned)-exp2);
        }
        /* Far cuts first (they also cover huge integers).
         * Thresholds are on top = floor(log2|x|) and put the
         * result at least 64 exponent bits beyond every
         * kernel threshold (kernel cuts: x >= emax+2 <= 1025,
         * x < emin-p >= -1075, x < -(p+1) >= -54), so a proxy
         * exact value narrowed by the same grid is a sound
         * decision and a kernel cut off-by-one still faces
         * the full bracket in between:
         *   x >= 2048 (top >= 11): result >= 2^2048, proxy
         *     2^(emax+2);
         *   exp2, x <= -2048: result <= 2^-2048, proxy
         *     2^(etie-2) (< u/2 at every format);
         *   exp2m1, x <= -256 (top >= 8): result within
         *     2^-256 of -1, proxy -(1 - 2^-(p+8)). */
        if ((!sign && top >= 11)
            || (sign && !is_m1 && top >= 11)
            || (sign && is_m1 && top >= 8)) {
            for (rm = 0; rm < 5; rm++) {
                if (!sign) {
                    x_narrow_pow2(f, 0, (long)f->emax + 2, rm,
                                  &rb[rm], &rf[rm]);
                } else if (!is_m1) {
                    x_narrow_pow2(f, 0, etie - 2, rm, &rb[rm], &rf[rm]);
                } else {
                    x_narrow_oneminus(f, (long)f->p + 8, rm,
                                      &rb[rm], &rf[rm]);
                }
            }
            *via_shortcut = 1;
            return 1;
        }
        if (is_int) {
            static mpfr_t dv;
            static long dvprec = 0;
            long n = sign ? -(long)nval : (long)nval;
            long need = (n < 0 ? -n : n) + 8;
            if (need < 128) {
                need = 128;
            }
            if (dvprec < need) {
                if (dvprec != 0) {
                    mpfr_clear(dv);
                }
                mpfr_init2(dv, (mpfr_prec_t)need);
                dvprec = need;
            }
            if (!is_m1) {
                mpfr_set_si_2exp(dv, 1, (mpfr_exp_t)n, MPFR_RNDN);
            } else if (n >= 0) {
                mpfr_set_ui_2exp(dv, 1u, (mpfr_exp_t)n, MPFR_RNDN);
                if (n > 0) {
                    mpfr_sub_ui(dv, dv, 1u, MPFR_RNDN);
                }
            } else {
                mpfr_set_ui_2exp(dv, 1u, (mpfr_exp_t)-n, MPFR_RNDN);
                mpfr_sub_ui(dv, dv, 1u, MPFR_RNDN);
                mpfr_mul_2si(dv, dv, (mpfr_exp_t)n, MPFR_RNDN);
                mpfr_neg(dv, dv, MPFR_RNDN);
            }
            for (rm = 0; rm < 5; rm++) {
                x_narrow(f, dv, rm, &rb[rm], &rf[rm]);
            }
            return 1;
        }

    }
    return 0;
}

/* MPFR bracket decision for one finite non-table input.
 * Returns 0 decided, -1 undecided at the widest precision. */
static int x_decide_mpfr(const xfmt_t *f, int fn, uint64_t bits,
                         long p0, uint64_t rb[5], uint32_t rf[5])
{
    int is_m1 = fn == 1;
    static const long ESC[4] = { 384, 768, 1536, 3072 };
    int sign, exp2, cls, attempt, rm;
    uint64_t sig;
    x_decode(f, bits, &sign, &sig, &exp2, &cls);
    for (attempt = 0; attempt < 5; attempt++) {
        long prec = attempt == 0 ? p0 : ESC[attempt - 1];
        static mpfr_t x, y, ylo, yhi;
        static long cur_prec = 0;
        int ok = 1;
        if (attempt > 0) {
            g_x_escal++;
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
            mpfr_set_ui(ylo, (unsigned long)(sig >> 32), MPFR_RNDN);
            mpfr_mul_2si(ylo, ylo, 32, MPFR_RNDN);
            mpfr_add(x, x, ylo, MPFR_RNDN);
        }
        mpfr_mul_2si(x, x, exp2, MPFR_RNDN);
        if (sign) {
            mpfr_neg(x, x, MPFR_RNDN);
        }
        /* Near-1 composition for tiny exp2 inputs: the
         * direct value 1 + m collapses onto 1 at working
         * precision when |m| < 2^-prec (spike Sec. 2.4), so
         * bracket m = exp2m1(x) relatively and compose the
         * ends 1 + m_end exactly in a wide workspace. */
        int compose1 = fn == 0
            && ((long)exp2 + x_bitlen(sig) - 1) <= -9;
        if (fn == 2) {
            mpfr_log2(y, x, MPFR_RNDN);
        } else if (fn == 3) {
            mpfr_log2p1(y, x, MPFR_RNDN);
        } else if (is_m1 || compose1) {
            mpfr_exp2m1(y, x, MPFR_RNDN);
        } else {
            mpfr_exp2(y, x, MPFR_RNDN);
        }
        if (mpfr_nan_p(y) || mpfr_inf_p(y)) {
            return -1;
        }
        mpfr_set(ylo, y, MPFR_RNDN);
        mpfr_nextbelow(ylo);
        mpfr_nextbelow(ylo);
        mpfr_set(yhi, y, MPFR_RNDN);
        mpfr_nextabove(yhi);
        mpfr_nextabove(yhi);
        if (compose1) {
            static mpfr_t clo, chi;
            static int cinit = 0;
            if (!cinit) {
                mpfr_init2(clo, 4224);
                mpfr_init2(chi, 4224);
                cinit = 1;
            }
            /* 1 + end is exact at 4224 bits: end span from
             * 2^0 to 2^(e-prec+1) is at most 1075+3072 bits. */
            mpfr_add_ui(clo, ylo, 1u, MPFR_RNDN);
            mpfr_add_ui(chi, yhi, 1u, MPFR_RNDN);
            for (rm = 0; rm < 5 && ok; rm++) {
                uint64_t blo, bhi;
                uint32_t flo, fhi;
                x_narrow(f, clo, rm, &blo, &flo);
                x_narrow(f, chi, rm, &bhi, &fhi);
                if (blo != bhi || flo != fhi) {
                    ok = 0;
                } else {
                    rb[rm] = blo;
                    rf[rm] = flo;
                }
            }
            if (ok) {
                return 0;
            }
            continue;
        }
        for (rm = 0; rm < 5 && ok; rm++) {
            uint64_t blo, bhi;
            uint32_t flo, fhi;
            x_narrow(f, ylo, rm, &blo, &flo);
            x_narrow(f, yhi, rm, &bhi, &fhi);
            if (blo != bhi || flo != fhi) {
#ifdef X_DEBUG_ESCAL
                static int dbg = 0;
                if (attempt == 0 && dbg < 10) {
                    dbg++;
                    printf("ESCAL %s in=%016llx rm=%d blo=%016llx/%02x "
                           "bhi=%016llx/%02x\n",
                           XFN_NAME[fn],
                           (unsigned long long)bits, rm,
                           (unsigned long long)blo, (unsigned)flo,
                           (unsigned long long)bhi, (unsigned)fhi);
                }
#endif
                ok = 0;
            } else {
                rb[rm] = blo;
                rf[rm] = flo;
            }
        }
        if (ok) {
            /* stride audit: grid narrow vs MPFR conversion */
            if (f->w != 16 && (++g_x_audit_seq % X_AUDIT_STRIDE) == 0) {
                g_x_audit++;
                for (rm = 0; rm < 4; rm++) {
                    uint64_t cv = 0u;
                    if (f->w == 32) {
                        float a = mpfr_get_flt(y, XRND[rm]);
                        memcpy(&cv, &a, 4);
                        cv &= 0xffffffffULL;
                    } else {
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdouble-promotion"
                        double a = mpfr_get_d(y, XRND[rm]);
                        memcpy(&cv, &a, 8);
#pragma GCC diagnostic pop
                    }
                    if (cv != rb[rm]) {
                        g_x_audit_fail++;
                        printf("X-AUDIT-FAIL %s %s %s in=%016llx "
                               "grid=%016llx conv=%016llx\n",
                               f->name, XFN_NAME[fn],
                               XRM_NAME[rm],
                               (unsigned long long)bits,
                               (unsigned long long)rb[rm],
                               (unsigned long long)cv);
                    }
                }
            }
            return 0;
        }
    }
    g_x_undecided++;
    return -1;
}

/* Full decider for one input. 0 = decided. */
static int explog_expected(int fi, int fn, uint64_t bits, long p0,
                           uint64_t rb[5], uint32_t rf[5])
{
    const xfmt_t *f = &XFMTS[fi];
    int via = 0;
    if (x_decide_table(f, fn, bits, rb, rf, &via)) {
        if (via) {
            g_x_shortcut++;
        } else {
            g_x_special++;
        }
        return 0;
    }
    return x_decide_mpfr(f, fn, bits, p0, rb, rf);
}
