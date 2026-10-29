/* msf_math.c - Clause 9.2 sinPi/cosPi, correctly rounded in
 * all four attributes at binary16/32/64 (SF-1 Step 2c).
 *
 * Design record: ledger/parcel-w4trig.md (design entry).
 * Reduction is exact integer work: decode, split |x| into
 * integer and fraction by shifts, take the nearest-integer
 * remainder r with |r| <= 1/2, fold to t in [0, 1/4]. Integer
 * and half-integer inputs are exact branches (their zero
 * signs are the 9.2.1 cells settled in the design entry:
 * sinPi at an integer delivers a zero with the sign of x,
 * cosPi at a half-integer delivers +0 in every mode). The
 * kernel sees u = pi*t in [0, pi/4] only.
 *
 * Kernel values are positive wide values: W-bit normalized
 * significands over 32-bit limbs (value = M * 2^(e-(W-1)),
 * top bit of M set), each stage evaluating one truncating
 * approximation A with proven relative error bound Ek
 * (MSF_TRIG_EK_EXP, generator-derived). Constants come from
 * the generated floor table (msf_trig_tables.h). Sin-shaped
 * results evaluate u * S(z); cos-shaped results evaluate
 * delta = 1 - cos(u) = (z/2) * D(z) and form 1 - delta
 * exactly at pack scale, z = u^2, S/D the Taylor series in
 * z with alternating tails inside Ek. Three Ziv stages
 * (W = 160, 256, 384) pack the endpoints A - Ek and A + Ek
 * through the shared pack; agreement of result bits and
 * flags decides. Outside the exact branches the true
 * result is irrational (Niven: rational sine/cosine at a
 * rational multiple of pi lies in {0, +-1/2, +-1}, and
 * +-1/2 needs a non-dyadic argument), so inexact always
 * accompanies a kernel result.
 */
#include "msf_internal.h"
#include "msf_decode.h"
#include "msf_trig_tables.h"
#include "msf_explog_tables.h"

#ifdef MSF_TRIG_TEST_COUNTERS
/* Test-only escalation instrumentation. Never defined in a
 * build whose results are quoted as the shipped library. */
uint64_t msf_trig_stage_hits[3];
uint64_t msf_trig_final_undecided;
#define TRIG_COUNT_STAGE(s) (msf_trig_stage_hits[s]++)
#define TRIG_COUNT_FINAL() (msf_trig_final_undecided++)
#else
#define TRIG_COUNT_STAGE(s) ((void)0)
#define TRIG_COUNT_FINAL() ((void)0)
#endif

#ifdef MSF_TRIG_FORCE_START
#define TRIG_START_STAGE MSF_TRIG_FORCE_START
#else
#define TRIG_START_STAGE 0
#endif

typedef struct wf {
    uint32_t m[MSF_TRIG_MAXL];
    int32_t e;
} wf_t;

#define TRIG_BIGL 40

static int wf_is_zero(const wf_t *a, int n)
{
    int i;
    for (i = 0; i < n; i++) {
        if (a->m[i] != 0u) {
            return 0;
        }
    }
    return 1;
}

static void wf_set_zero(wf_t *a)
{
    int i;
    for (i = 0; i < MSF_TRIG_MAXL; i++) {
        a->m[i] = 0u;
    }
    a->e = 0;
}

static uint32_t big_limb(const uint32_t *big, int nbig, int32_t idx)
{
    if (idx < 0 || idx >= nbig) {
        return 0u;
    }
    return big[idx];
}

/* 32 bits of big starting at bit position bitpos (may be
 * negative; out-of-range bits read as zero). */
static uint32_t big_bits32(const uint32_t *big, int nbig, int32_t bitpos)
{
    int32_t li;
    int off;
    uint32_t w;
    if (bitpos >= 0) {
        li = bitpos >> 5;
        off = (int)(bitpos & 31);
    } else {
        li = -((int32_t)((-bitpos + 31) >> 5));
        off = (int)(bitpos - li * 32);
    }
    w = big_limb(big, nbig, li) >> off;
    if (off != 0) {
        w |= big_limb(big, nbig, li + 1) << (32 - off);
    }
    return w;
}

static int clz32(uint32_t x)
{
    int n = 0;
    if (x == 0u) {
        return 32;
    }
    if ((x >> 16) == 0u) { n += 16; x <<= 16; }
    if ((x >> 24) == 0u) { n += 8; x <<= 8; }
    if ((x >> 28) == 0u) { n += 4; x <<= 4; }
    if ((x >> 30) == 0u) { n += 2; x <<= 2; }
    n -= (int)(x >> 31);
    return n;
}

static int32_t big_top_bit(const uint32_t *big, int nbig)
{
    int i;
    for (i = nbig - 1; i >= 0; i--) {
        if (big[i] != 0u) {
            return (int32_t)i * 32 + (31 - clz32(big[i]));
        }
    }
    return -1;
}

static int big_any_below(const uint32_t *big, int nbig, int32_t shift)
{
    int32_t i;
    int off;
    if (shift <= 0) {
        return 0;
    }
    for (i = 0; i < shift / 32 && i < nbig; i++) {
        if (big[i] != 0u) {
            return 1;
        }
    }
    off = (int)(shift % 32);
    if (off != 0 && shift / 32 < nbig) {
        uint32_t mask = (1u << off) - 1u;
        if ((big[shift / 32] & mask) != 0u) {
            return 1;
        }
    }
    return 0;
}

/* Normalize exact value (big + f) * 2^base_exp, f = 0 when
 * sticky is 0 else 0 < f < 1, into an n-limb wf, truncating
 * (round_up == 0) or rounding away from zero when any bit is
 * dropped (round_up != 0). Values here are never negative. */
static void wf_normalize(wf_t *out, const uint32_t *big, int nbig,
                         int32_t base_exp, int sticky, int n, int round_up)
{
    int32_t w = (int32_t)n * 32;
    int32_t p = big_top_bit(big, nbig);
    int32_t shift;
    int i;
    if (p < 0) {
        if (sticky && round_up) {
            wf_set_zero(out);
            out->m[n - 1] = 0x80000000u;
            out->e = base_exp;
        } else {
            wf_set_zero(out);
        }
        return;
    }
    shift = p - (w - 1);
    for (i = 0; i < MSF_TRIG_MAXL; i++) {
        out->m[i] = 0u;
    }
    for (i = 0; i < n; i++) {
        out->m[i] = big_bits32(big, nbig, shift + (int32_t)i * 32);
    }
    out->e = base_exp + p;
    if (round_up && (sticky || big_any_below(big, nbig, shift))) {
        uint32_t carry = 1u;
        for (i = 0; i < n; i++) {
            uint32_t nv = out->m[i] + carry;
            carry = nv < out->m[i] ? 1u : 0u;
            out->m[i] = nv;
        }
        if (carry != 0u) {
            for (i = 0; i < n; i++) {
                out->m[i] = 0u;
            }
            out->m[n - 1] = 0x80000000u;
            out->e += 1;
        }
    }
}

static int wf_cmp(const wf_t *a, const wf_t *b, int n)
{
    int az = wf_is_zero(a, n), bz = wf_is_zero(b, n);
    int i;
    if (az || bz) {
        return az == bz ? 0 : (az ? -1 : 1);
    }
    if (a->e != b->e) {
        return a->e > b->e ? 1 : -1;
    }
    for (i = n - 1; i >= 0; i--) {
        if (a->m[i] != b->m[i]) {
            return a->m[i] > b->m[i] ? 1 : -1;
        }
    }
    return 0;
}

static void wf_mul(wf_t *out, const wf_t *a, const wf_t *b, int n,
                   int round_up)
{
    uint32_t big[2 * MSF_TRIG_MAXL];
    int i, j;
    if (wf_is_zero(a, n) || wf_is_zero(b, n)) {
        wf_set_zero(out);
        return;
    }
    for (i = 0; i < 2 * n; i++) {
        big[i] = 0u;
    }
    for (i = 0; i < n; i++) {
        uint64_t carry = 0u;
        for (j = 0; j < n; j++) {
            uint64_t t = (uint64_t)big[i + j]
                       + (uint64_t)a->m[i] * (uint64_t)b->m[j] + carry;
            big[i + j] = (uint32_t)t;
            carry = t >> 32;
        }
        big[i + n] = (uint32_t)carry;
    }
    /* Product of two normalized W-bit significands has its
     * top bit at 2W-1 or 2W-2; extract the top W bits. */
    {
        int32_t w = (int32_t)n * 32;
        int top2 = (big[2 * n - 1] >> 31) != 0u;
        int32_t shift = top2 ? w : w - 1;
        int dropped;
        int32_t eout = a->e + b->e + (top2 ? 1 : 0);
        for (i = 0; i < MSF_TRIG_MAXL; i++) {
            out->m[i] = 0u;
        }
        for (i = 0; i < n; i++) {
            out->m[i] = big_bits32(big, 2 * n, shift + (int32_t)i * 32);
        }
        out->e = eout;
        dropped = big_any_below(big, 2 * n, shift);
        if (round_up && dropped) {
            uint32_t carry = 1u;
            for (i = 0; i < n; i++) {
                uint32_t nv = out->m[i] + carry;
                carry = nv < out->m[i] ? 1u : 0u;
                out->m[i] = nv;
            }
            if (carry != 0u) {
                for (i = 0; i < n; i++) {
                    out->m[i] = 0u;
                }
                out->m[n - 1] = 0x80000000u;
                out->e += 1;
            }
        }
    }
}

/* Shift an n-limb significand right by d bits into a 2n-limb
 * accumulator position: acc (2n limbs, scale: acc holds
 * values in units of the acc LSB) receives src << (W - d)
 * for d <= W, else src >> (d - W); *frac reports whether any
 * bit fell below the acc LSB. W = 32n. */
static void big_align_b(uint32_t *acc, const uint32_t *src, int n,
                        int32_t d, int *frac)
{
    int32_t w = (int32_t)n * 32;
    int i;
    for (i = 0; i < 2 * n; i++) {
        acc[i] = 0u;
    }
    *frac = 0;
    if (d <= w) {
        int32_t s = w - d;
        int limb = (int)(s >> 5);
        int off = (int)(s & 31);
        for (i = 0; i < n; i++) {
            acc[limb + i] |= src[i] << off;
            if (off != 0 && limb + i + 1 < 2 * n) {
                acc[limb + i + 1] |= src[i] >> (32 - off);
            }
        }
    } else {
        int32_t s = d - w;
        int limb = (int)(s >> 5);
        int off = (int)(s & 31);
        for (i = 0; i < n; i++) {
            uint32_t v = 0u;
            if (i + limb < n) {
                v = src[i + limb] >> off;
                if (off != 0 && i + limb + 1 < n) {
                    v |= src[i + limb + 1] << (32 - off);
                }
            }
            acc[i] = v;
        }
        *frac = big_any_below(src, n, s);
    }
}

/* a + b (is_sub == 0) or a - b, at stage limbs n, rounded
 * toward zero (round_up == 0) or away. For subtraction with
 * a < b, delivers zero toward zero and a away: every kernel
 * quantity is >= 0, so both are sound interval endpoints. */
static void wf_addsub(wf_t *out, const wf_t *a, const wf_t *b, int n,
                      int is_sub, int round_up)
{
    int32_t w = (int32_t)n * 32;
    int32_t d;
    if (!is_sub && wf_cmp(a, b, n) < 0) {
        const wf_t *tmp = a;
        a = b;
        b = tmp;
    }
    if (wf_is_zero(b, n)) {
        *out = *a;
        return;
    }
    if (wf_is_zero(a, n)) {
        if (is_sub) {
            wf_set_zero(out);
        } else {
            *out = *b;
        }
        return;
    }
    if (is_sub && wf_cmp(a, b, n) < 0) {
        if (round_up) {
            *out = *a;
        } else {
            wf_set_zero(out);
        }
        return;
    }
    d = a->e - b->e;
    {
        /* Align at a's scale with W extra low bits: exact
         * value is (D + f) * 2^(ea-2W+1) with f = 0 when
         * frac == 0 else 0 < f < 1. Subtraction with a
         * fractional tail borrows one unit into D. */
        uint32_t abuf[2 * MSF_TRIG_MAXL + 1];
        uint32_t bbuf[2 * MSF_TRIG_MAXL];
        int frac = 0;
        int i;
        uint64_t carry;
        for (i = 0; i < n; i++) {
            abuf[i] = 0u;
            abuf[n + i] = a->m[i];
        }
        abuf[2 * n] = 0u;
        big_align_b(bbuf, b->m, n, d, &frac);
        if (is_sub) {
            carry = frac ? 0u : 1u; /* ~B + (1 - frac) */
            for (i = 0; i < 2 * n; i++) {
                uint64_t t = (uint64_t)abuf[i] + (uint64_t)(~bbuf[i]) + carry;
                abuf[i] = (uint32_t)t;
                carry = t >> 32;
            }
            abuf[2 * n] = 0u;
        } else {
            carry = 0u;
            for (i = 0; i < 2 * n; i++) {
                uint64_t t = (uint64_t)abuf[i] + (uint64_t)bbuf[i] + carry;
                abuf[i] = (uint32_t)t;
                carry = t >> 32;
            }
            abuf[2 * n] = (uint32_t)carry;
        }
        wf_normalize(out, abuf, 2 * n + 1, a->e - 2 * w + 1, frac, n,
                     round_up);
    }
}

/* A table constant at stage n: the stored 384-bit floor F
 * satisfies F <= true < F + ulp384; entries are normalized
 * at 384 bits and stage widths are limb multiples, so the
 * stage value is the top n limbs (truncation error under
 * 1 ulp at stage width, as the budget charges). */
static void wf_from_entry(wf_t *out, const msf_trig_entry_t *en,
                          int32_t e_adj, int n)
{
    int i;
    for (i = 0; i < MSF_TRIG_MAXL; i++) {
        out->m[i] = 0u;
    }
    for (i = 0; i < n; i++) {
        out->m[i] = en->m[MSF_TRIG_MAXL - n + i];
    }
    out->e = en->e + e_adj;
#ifdef MSF_TRIG_DROP_LIMB
    /* Permanent negative control only: truncated table
     * precision, realized at stage width (dropping low limbs
     * of every table-derived value). Never defined in a build
     * whose results are quoted. */
    out->m[0] = 0u;
    out->m[1] = 0u;
#endif
}

/* Evaluate one stage as a single truncating approximation A.
 * shape_sin != 0: A approximates sin(pi*t); else A
 * approximates delta = 1 - cos(pi*t). t is the exact dyadic
 * t_num * 2^t_exp in (0, 1/4]. The proven relative bound
 * |A - true| <= A * 2^-MSF_TRIG_EK_EXP[stage] is derived in
 * the design entry (generator-checked recurrence over table
 * quantum, pi truncation, u and u^2 rounding, Horner
 * accumulation, Taylor tails, delta-branch terms). */
static void trig_eval(wf_t *out, int shape_sin, uint64_t t_num,
                      int32_t t_exp, int stage)
{
    int n = MSF_TRIG_STAGE_LIMBS[stage];
    int nterms = shape_sin ? MSF_TRIG_NTERMS_SIN[stage]
                           : MSF_TRIG_NTERMS_DELTA[stage];
    wf_t t, pi, u, z, acc, prod, term;
    uint32_t tbig[2];
    int k;
    tbig[0] = (uint32_t)t_num;
    tbig[1] = (uint32_t)(t_num >> 32);
    wf_normalize(&t, tbig, 2, t_exp, 0, n, 0);
    wf_from_entry(&pi, &MSF_TRIG_PI, 0, n);
    wf_mul(&u, &pi, &t, n, 0);
    wf_mul(&z, &u, &u, n, 0);
    if (shape_sin) {
        wf_from_entry(&acc, &MSF_TRIG_SIN_C[nterms - 1], 0, n);
        for (k = nterms - 2; k >= 0; k--) {
            wf_mul(&prod, &z, &acc, n, 0);
            wf_from_entry(&term, &MSF_TRIG_SIN_C[k], 0, n);
            wf_addsub(&acc, &term, &prod, n, 1, 0);
        }
        wf_mul(out, &u, &acc, n, 0);
    } else {
        /* D coefficients: d_k = 2/(2k+2)! = 2 * COS_C[k+1]. */
        wf_from_entry(&acc, &MSF_TRIG_COS_C[nterms], 1, n);
        for (k = nterms - 2; k >= 0; k--) {
            wf_mul(&prod, &z, &acc, n, 0);
            wf_from_entry(&term, &MSF_TRIG_COS_C[k + 1], 1, n);
            wf_addsub(&acc, &term, &prod, n, 1, 0);
        }
        wf_mul(out, &z, &acc, n, 0);
        out->e -= 1;
    }
}

/* Pack exact value (big + f) * 2^base_exp (f as in
 * wf_normalize) by way of the pack's 128-bit grid: top 128
 * bits plus the OR of everything below. For every magnitude
 * this kernel produces, the destination round bit lies
 * inside those 128 bits, so the pack sees the exact
 * endpoint's rounding. */
static uint64_t trig_pack_big(const msf_fmt_params_t *fp, int sign,
                              const uint32_t *big, int nbig,
                              int32_t base_exp, int sticky_in, int rm,
                              msf_flags_t *flags)
{
    msf_u128_t sig;
    int32_t p = big_top_bit(big, nbig);
    int32_t shift;
    int sticky, i;
    if (p < 0) {
        sig = msf_u128_from_u64(0u);
        return msf_pack_generic(fp, sign, 0, sig, 0, rm, flags);
    }
    shift = p - 127;
    for (i = 0; i < 4; i++) {
        sig.w[i] = big_bits32(big, nbig, shift + (int32_t)i * 32);
    }
    sticky = sticky_in || big_any_below(big, nbig, shift);
    return msf_pack_generic(fp, sign, base_exp + p - 127, sig, sticky,
                            rm, flags);
}

static uint64_t trig_pack_wf(const msf_fmt_params_t *fp, int sign,
                             const wf_t *v, int n, int rm,
                             msf_flags_t *flags)
{
    /* Stage widths are limb multiples >= 128: the top four
     * limbs are the pack significand, the rest are sticky. */
    msf_u128_t sig;
    int sticky = 0;
    int i;
    if (wf_is_zero(v, n)) {
        sig = msf_u128_from_u64(0u);
        return msf_pack_generic(fp, sign, 0, sig, 0, rm, flags);
    }
    for (i = 0; i < 4; i++) {
        sig.w[i] = v->m[n - 4 + i];
    }
    for (i = 0; i < n - 4; i++) {
        sticky |= v->m[i] != 0u;
    }
    return msf_pack_generic(fp, sign, v->e - 127, sig, sticky, rm, flags);
}

/* Pack 1 - d for a cos-shaped endpoint d in [0, 1): exact
 * 288-bit fixed-point subtraction, sticky preserved. */
static uint64_t trig_pack_one_minus(const msf_fmt_params_t *fp, int sign,
                                    const wf_t *d, int n, int rm,
                                    msf_flags_t *flags)
{
    uint32_t abig[10];
    int32_t s;
    int g_sticky, i;
    uint32_t borrow;
    /* A = floor(d * 2^288) = M shifted by s, g = remainder. */
    s = d->e - ((int32_t)n * 32 - 1) + 288;
    for (i = 0; i < 10; i++) {
        abig[i] = big_bits32(d->m, n, (int32_t)i * 32 - s);
    }
    g_sticky = s < 0 ? big_any_below(d->m, n, -s) : 0;
    if (wf_is_zero(d, n)) {
        g_sticky = 0;
    }
    /* BIG = 2^288 - A - (g ? 1 : 0); value (BIG + f) 2^-288. */
    borrow = g_sticky ? 1u : 0u;
    for (i = 0; i < 10; i++) {
        uint32_t sub = abig[i] + borrow;
        borrow = sub < abig[i] ? 1u : 0u;
        abig[i] = (i == 9 ? 1u : 0u) - sub;
        if ((i == 9 ? 1u : 0u) < sub) {
            borrow = 1u;
        }
    }
    return trig_pack_big(fp, sign, abig, 10, -288, g_sticky, rm, flags);
}

/* Form the proven interval A +- A*2^-Ek around a stage
 * approximation and pack both endpoints; when is_delta the
 * endpoints are 1 - d_hi and 1 - d_lo. Returns 1 (and ORs
 * the agreed flags into the scratch accumulator *flags)
 * when both endpoints agree on bits and flags under the
 * caller's attribute: rounding is monotone, so the true
 * value between them rounds the same way. */
static int trig_decide(const msf_fmt_params_t *fp, int sign,
                       const wf_t *a, int is_delta, int n, int stage,
                       int rm, uint64_t *bits_out, msf_flags_t *flags)
{
    wf_t d, lo, hi;
    msf_flags_t flo = 0u, fhi = 0u;
    uint64_t blo, bhi;
    d = *a;
    d.e -= MSF_TRIG_EK_EXP[stage];
    wf_addsub(&lo, a, &d, n, 1, 0);
    wf_addsub(&hi, a, &d, n, 0, 1);
    if (is_delta) {
        blo = trig_pack_one_minus(fp, sign, &hi, n, rm, &flo);
        bhi = trig_pack_one_minus(fp, sign, &lo, n, rm, &fhi);
    } else {
        blo = trig_pack_wf(fp, sign, &lo, n, rm, &flo);
        bhi = trig_pack_wf(fp, sign, &hi, n, rm, &fhi);
    }
    if (blo == bhi && flo == fhi) {
        *bits_out = blo;
        *flags |= flo | MSF_FLAG_INEXACT;
        return 1;
    }
    *bits_out = blo;
    *flags |= flo | MSF_FLAG_INEXACT;
    return 0;
}

static uint64_t trig_core(int fmt, int is_cos, uint64_t bits, int rm,
                          msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    msf_decoded_t d = msf_decode(fmt, bits);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out;
    uint64_t sig, ipart, rem, half, tnum;
    int32_t exp2, k;
    int parity, r_neg = 0, swapped, shape_sin, result_sign;
    int stage;

    ops[0] = d;
    fmts[0] = fmt;
    if (msf_nan_delivery(fmt, ops, fmts, 1,
                         d.cls == MSF_VC_INFINITY, &out, flags)) {
        return out;
    }
    if (d.cls == MSF_VC_ZERO) {
        if (is_cos) {
            return msf_pack_generic(fp, 0, 0, msf_u128_from_u64(1u), 0,
                                    rm, flags);
        }
        return msf_pack_generic(fp, d.sign, 0, msf_u128_from_u64(0u), 0,
                                rm, flags);
    }
    sig = msf_u128_to_u64_trunc(d.sig);   /* < 2^53 */
    exp2 = d.exp;                          /* |x| = sig * 2^exp2 */
    if (exp2 >= 0) {
        parity = exp2 == 0 ? (int)(sig & 1u) : 0;
        if (is_cos) {
            return msf_pack_generic(fp, parity, 0, msf_u128_from_u64(1u),
                                    0, rm, flags);
        }
        return msf_pack_generic(fp, d.sign, 0, msf_u128_from_u64(0u), 0,
                                rm, flags);
    }
    k = -exp2;
    if (k < 64) {
        ipart = sig >> k;
        rem = sig & ((1ULL << k) - 1ULL);
        half = 1ULL << (k - 1);
    } else {
        /* fraction is below 1/2: sig < 2^53 <= 2^(k-1) */
        ipart = 0u;
        rem = sig;
        half = 0u;
    }
    if (rem == 0u) {
        parity = (int)(ipart & 1u);
        if (is_cos) {
            return msf_pack_generic(fp, parity, 0, msf_u128_from_u64(1u),
                                    0, rm, flags);
        }
        return msf_pack_generic(fp, d.sign, 0, msf_u128_from_u64(0u), 0,
                                rm, flags);
    }
    if (k < 64 && rem == half) {
        /* half-integer: sinPi = (-1)^ipart (sign of x applied),
         * cosPi = +0 in every mode (settled cell B). */
        if (is_cos) {
            return msf_pack_generic(fp, 0, 0, msf_u128_from_u64(0u), 0,
                                    rm, flags);
        }
        return msf_pack_generic(fp, d.sign ^ (int)(ipart & 1u), 0,
                                msf_u128_from_u64(1u), 0, rm, flags);
    }
    if (k >= 64 || rem < half) {
        parity = (int)(ipart & 1u);
        tnum = rem;
        r_neg = 0;
    } else {
        parity = (int)((ipart + 1ULL) & 1u);
        tnum = (1ULL << k) - rem;
        r_neg = 1;
    }
    /* t = tnum * 2^-k in (0, 1/2); k >= 2 on this path. */
    if (k < 64 && tnum > (1ULL << (k - 2))) {
        swapped = 1;
        tnum = (1ULL << (k - 1)) - tnum;
    } else {
        swapped = 0;
    }
    if (is_cos) {
        result_sign = parity;
        shape_sin = swapped;
    } else {
        result_sign = d.sign ^ parity ^ r_neg;
        shape_sin = !swapped;
    }
    out = 0u;
    for (stage = TRIG_START_STAGE; stage < 3; stage++) {
        wf_t approx;
        int n = MSF_TRIG_STAGE_LIMBS[stage];
        msf_flags_t tflags = 0u;
        TRIG_COUNT_STAGE(stage);
        trig_eval(&approx, shape_sin, tnum, -k, stage);
        if (trig_decide(fp, result_sign, &approx, !shape_sin, n, stage,
                        rm, &out, &tflags)) {
            *flags |= tflags;
            return out;
        }
        if (stage == 2) {
            /* Unreachable under the leg-(c) margin argument;
             * defined fallback packs the lo endpoint. */
            TRIG_COUNT_FINAL();
            *flags |= tflags;
            return out;
        }
    }
    return out;
}

#define DEF_TRIG(NAME, FMT, TYPE, ISCOS) \
    TYPE NAME(TYPE a, msf_rounding_t rm, msf_flags_t *fl) \
    { return (TYPE)trig_core(FMT, ISCOS, (uint64_t)a, (int)rm, fl); }

DEF_TRIG(msf16_sin_pi, MSF_FMT_F16, msf16_t, 0)
DEF_TRIG(msf32_sin_pi, MSF_FMT_F32, msf32_t, 0)
DEF_TRIG(msf64_sin_pi, MSF_FMT_F64, msf64_t, 0)
DEF_TRIG(msf16_cos_pi, MSF_FMT_F16, msf16_t, 1)
DEF_TRIG(msf32_cos_pi, MSF_FMT_F32, msf32_t, 1)
DEF_TRIG(msf64_cos_pi, MSF_FMT_F64, msf64_t, 1)

/* ---- exp2 / exp2m1 (SF-2 Step 3a) ----
 *
 * Design record: ledger/parcel-w5exp2.md (design entry,
 * written before this code). Exact n+f split (n the nearest
 * integer to x, |f| <= 1/2 an exact dyadic), 2^n delivered
 * as a pack exponent input, never a multiply. Kernel
 * argument u = f*ln2, |u| <= ln2/2: for u >= 0 the exp
 * Taylor series in u; for u < 0 the delta form
 * 1 - exp(u) = |u| * D(|u|) with the alternating
 * D(z) = sum (-z)^k/(k+1)!; exp2m1 for u > 0 uses
 * m = u * M(u), M(z) = sum z^k/(k+1)!, and composes at
 * pack scale, no new series. Three Ziv stages (160/256/384)
 * with generator-proven Ek (MSF_EXPLOG_EK_EXP). Outside the
 * enumerated integer branches 2^x is irrational for dyadic
 * x, so no exact result or rounding tie is attainable and
 * inexact always accompanies a kernel result; integer
 * inputs (including the 2^(emin-p) tie: -1075 at binary64)
 * are packed as exact integers/dyadics. Exact exponent cuts
 * run before the split, each delivered by packing a proxy
 * exact value proven to round identically in all modes. */

#ifdef MSF_EXPLOG_TEST_COUNTERS
uint64_t msf_explog_stage_hits[3];
uint64_t msf_explog_final_undecided;
#define EXPLOG_COUNT_STAGE(s) (msf_explog_stage_hits[s]++)
#define EXPLOG_COUNT_FINAL() (msf_explog_final_undecided++)
#else
#define EXPLOG_COUNT_STAGE(s) ((void)0)
#define EXPLOG_COUNT_FINAL() ((void)0)
#endif

#ifdef MSF_EXPLOG_FORCE_START
#define EXPLOG_START_STAGE MSF_EXPLOG_FORCE_START
#else
#define EXPLOG_START_STAGE 0
#endif

#ifndef MSF_EXPLOG_EK_NARROW
#define MSF_EXPLOG_EK_NARROW 0
#endif

#define EXPLOG_BIGL 64

static int u64_bitlen(uint64_t v)
{
    int n = 0;
    while (v != 0u) {
        n++;
        v >>= 1;
    }
    return n;
}

/* Exact comparison of a finite decoded x against a small
 * integer T (|T| <= 4096): -1, 0, +1. Cut tests only. */
static int explog_cmp_int(const msf_decoded_t *d, int32_t t)
{
    uint64_t sig = msf_u128_to_u64_trunc(d->sig);
    uint64_t a;
    int tsign, mag;
    if (d->cls == MSF_VC_ZERO || sig == 0u) {
        return (0 > t) - (0 < t);
    }
    tsign = t < 0;
    if (d->sign != tsign) {
        return d->sign ? -1 : 1;
    }
    if (t == 0) {
        return d->sign ? -1 : 1;
    }
    a = (uint64_t)(t < 0 ? -t : t);
    {
        int32_t top = d->exp + u64_bitlen(sig) - 1;
        int32_t ta = u64_bitlen(a) - 1;
        if (top != ta) {
            mag = top > ta ? 1 : -1;
        } else if (d->exp >= 0) {
            uint64_t v = sig << (unsigned)d->exp;
            mag = v > a ? 1 : (v < a ? -1 : 0);
        } else {
            int32_t k = -d->exp;
            if (k >= 53) {
                mag = -1;
            } else {
                uint64_t v = a << (unsigned)k;
                mag = sig > v ? 1 : (sig < v ? -1 : 0);
            }
        }
    }
    return d->sign ? -mag : mag;
}

static uint64_t explog_pack_pow2(const msf_fmt_params_t *fp, int sign,
                                 int32_t n, int rm, msf_flags_t *flags)
{
    uint32_t big[1];
    big[0] = 1u;
    return trig_pack_big(fp, sign, big, 1, n, 0, rm, flags);
}

/* Pack (1 - d) * 2^ns for d in (0, 1): the trig one-minus
 * construction with a pack exponent offset. */
static uint64_t explog_pack_one_minus(const msf_fmt_params_t *fp,
                                      const wf_t *d, int n, int32_t ns,
                                      int rm, msf_flags_t *flags)
{
    uint32_t abig[10];
    int32_t s = d->e - ((int32_t)n * 32 - 1) + 288;
    int g_sticky, i;
    uint32_t borrow;
    for (i = 0; i < 10; i++) {
        abig[i] = big_bits32(d->m, n, (int32_t)i * 32 - s);
    }
    g_sticky = s < 0 ? big_any_below(d->m, n, -s) : 0;
    if (wf_is_zero(d, n)) {
        g_sticky = 0;
    }
    borrow = g_sticky ? 1u : 0u;
    for (i = 0; i < 10; i++) {
        uint32_t sub = abig[i] + borrow;
        borrow = sub < abig[i] ? 1u : 0u;
        abig[i] = (i == 9 ? 1u : 0u) - sub;
        if ((i == 9 ? 1u : 0u) < sub) {
            borrow = 1u;
        }
    }
    return trig_pack_big(fp, 0, abig, 10, ns - 288, g_sticky, rm, flags);
}

/* Pack the exact endpoint value
 *   (2^ones_hi - 2^ones_lo) + s * Q * 2^ns     (s = -1 if
 *   q_neg else +1; Q == NULL omits the term)
 * with the given result sign. Q is a stage wf (positive);
 * its exact significand integer enters shifted, so the
 * composed endpoint is materialised exactly in an
 * EXPLOG_BIGL-limb big at base b = min(ones_lo, Q LSB
 * exponent). Span bounds: design entry Sec. 5 (worst case
 * under 1500 bits at binary64, inside 2048). */
static uint64_t explog_pack_bracket(const msf_fmt_params_t *fp, int sign,
                                    int32_t ones_lo, int32_t ones_hi,
                                    const wf_t *q, int n, int32_t ns,
                                    int q_neg, int rm, msf_flags_t *flags)
{
    uint32_t big[EXPLOG_BIGL];
    int32_t w = (int32_t)n * 32;
    int32_t t = 0, b = ones_lo;
    int have_q = q != NULL && !wf_is_zero(q, n);
    int i;
    if (have_q) {
        t = q->e - (w - 1) + ns;
        if (t < b) {
            b = t;
        }
    }
    for (i = 0; i < EXPLOG_BIGL; i++) {
        big[i] = 0u;
    }
    /* ones in bit positions [ones_lo-b, ones_hi-b) */
    {
        int32_t lo = ones_lo - b, hi = ones_hi - b;
        int32_t l0 = lo >> 5, l1 = (hi - 1) >> 5;
        int32_t li;
        for (li = l0; li <= l1; li++) {
            uint32_t mask = 0xffffffffu;
            if (li == l0) {
                mask &= 0xffffffffu << (lo & 31);
            }
            if (li == l1 && (hi & 31) != 0) {
                mask &= (1u << (hi & 31)) - 1u;
            }
            big[li] |= mask;
        }
    }
    if (have_q) {
        int32_t s = t - b;
        int limb = (int)(s >> 5);
        int off = (int)(s & 31);
        uint64_t carry = q_neg ? 1u : 0u;
        for (i = 0; i < EXPLOG_BIGL; i++) {
            uint32_t qv = 0u;
            int qi = i - limb;
            if (qi >= 0 && qi < n) {
                qv = q->m[qi] << off;
                if (off != 0 && qi > 0) {
                    qv |= q->m[qi - 1] >> (32 - off);
                }
            } else if (off != 0 && qi == n) {
                qv = q->m[n - 1] >> (32 - off);
            }
            if (q_neg) {
                uint64_t tt = (uint64_t)big[i] + (uint64_t)(~qv) + carry;
                big[i] = (uint32_t)tt;
                carry = tt >> 32;
            } else {
                uint64_t tt = (uint64_t)big[i] + (uint64_t)qv + carry;
                big[i] = (uint32_t)tt;
                carry = tt >> 32;
            }
        }
    }
    return trig_pack_big(fp, sign, big, EXPLOG_BIGL, b, 0, rm, flags);
}

static void wf_from_xentry(wf_t *out, const msf_explog_entry_t *en, int n)
{
    int i;
    for (i = 0; i < MSF_TRIG_MAXL; i++) {
        out->m[i] = 0u;
    }
    for (i = 0; i < n; i++) {
        out->m[i] = en->m[MSF_EXPLOG_MAXL - n + i];
    }
    out->e = en->e;
#ifdef MSF_EXPLOG_DROP_LIMB
    out->m[0] = 0u;
    out->m[1] = 0u;
#endif
}

/* One truncating stage approximation, z = |f| * ln2.
 * kind 1 (V): exp(z) Horner for f >= 0. Kind 0 (M):
 * z * M(z), M = sum z^k/(k+1)!, the expm1 magnitude for
 * f > 0. Kind 2 (D): z * D(z), D = sum (-z)^k/(k+1)! the
 * alternating delta form 1 - exp(-z) for f < 0 (Horner
 * partials stay positive, terms decreasing). Proven
 * relative bound 2^-MSF_EXPLOG_EK_EXP[stage] (generator). */
static void explog_eval(wf_t *out, int kind, uint64_t f_num,
                        int32_t f_exp, int stage)
{
    int n = MSF_EXPLOG_STAGE_LIMBS[stage];
    int kterms = MSF_EXPLOG_NTERMS[stage];
    wf_t f, ln2, u, acc, prod, term;
    uint32_t fbig[2];
    int k;
    fbig[0] = (uint32_t)f_num;
    fbig[1] = (uint32_t)(f_num >> 32);
    wf_normalize(&f, fbig, 2, f_exp, 0, n, 0);
    wf_from_xentry(&ln2, &MSF_EXPLOG_LN2, n);
    wf_mul(&u, &ln2, &f, n, 0);
    if (kind == 1) {
        wf_from_xentry(&acc, &MSF_EXPLOG_C[kterms - 1], n);
        for (k = kterms - 2; k >= 0; k--) {
            wf_mul(&prod, &u, &acc, n, 0);
            wf_from_xentry(&term, &MSF_EXPLOG_C[k], n);
            wf_addsub(&acc, &term, &prod, n, 0, 0);
        }
        *out = acc;
    } else {
        wf_from_xentry(&acc, &MSF_EXPLOG_C[kterms], n);
        for (k = kterms - 1; k >= 1; k--) {
            wf_mul(&prod, &u, &acc, n, 0);
            wf_from_xentry(&term, &MSF_EXPLOG_C[k], n);
            wf_addsub(&acc, &term, &prod, n, kind == 2, 0);
        }
        wf_mul(out, &u, &acc, n, 0);
    }
}

enum {
    EXPLOG_SH_PLAIN = 0,    /* Q * 2^ns, result sign sign */
    EXPLOG_SH_ONEMINUS = 1, /* (1 - Q) * 2^ns, positive */
    EXPLOG_SH_BRACKET = 2   /* ones + s*Q*2^ns, sign sign */
};

typedef struct explog_shape {
    int kind;
    int sign;
    int32_t ns;
    int32_t ones_lo, ones_hi;
    int q_neg;
} explog_shape_t;

static uint64_t explog_pack_shape(const msf_fmt_params_t *fp,
                                  const explog_shape_t *sh,
                                  const wf_t *q, int n, int rm,
                                  msf_flags_t *flags)
{
    if (sh->kind == EXPLOG_SH_ONEMINUS) {
        return explog_pack_one_minus(fp, q, n, sh->ns, rm, flags);
    }
    if (sh->kind == EXPLOG_SH_BRACKET) {
        return explog_pack_bracket(fp, sh->sign, sh->ones_lo, sh->ones_hi,
                                   q, n, sh->ns, sh->q_neg, rm, flags);
    }
    {
        wf_t v = *q;
        v.e += sh->ns;
        return trig_pack_wf(fp, sh->sign, &v, n, rm, flags);
    }
}

/* Interval decision through the composed pack, monotone in
 * either direction: pack both Q endpoints, agreement of
 * bits and flags decides. Inexact always (design Sec. 3). */
static int explog_decide(const msf_fmt_params_t *fp,
                         const explog_shape_t *sh, const wf_t *a, int n,
                         int stage, int rm, uint64_t *bits_out,
                         msf_flags_t *flags)
{
    wf_t d, lo, hi;
    msf_flags_t flo = 0u, fhi = 0u;
    uint64_t blo, bhi;
    d = *a;
    d.e -= MSF_EXPLOG_EK_EXP[stage] - MSF_EXPLOG_EK_NARROW;
    wf_addsub(&lo, a, &d, n, 1, 0);
    wf_addsub(&hi, a, &d, n, 0, 1);
    blo = explog_pack_shape(fp, sh, &lo, n, rm, &flo);
    bhi = explog_pack_shape(fp, sh, &hi, n, rm, &fhi);
    if (blo == bhi && flo == fhi) {
        *bits_out = blo;
        *flags |= flo | MSF_FLAG_INEXACT;
        return 1;
    }
    *bits_out = blo;
    *flags |= flo | MSF_FLAG_INEXACT;
    return 0;
}

static uint64_t explog_core(int fmt, int is_m1, uint64_t bits, int rm,
                            msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    msf_decoded_t d = msf_decode(fmt, bits);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out = 0u;
    uint64_t sig, ipart = 0u, rem = 0u, half = 0u, f_num = 0u;
    int32_t e, k = 0, n_int = 0, f_exp = 0;
    int is_int = 0, f_sign = 0, kind = 0, stage;
    explog_shape_t sh;

    ops[0] = d;
    fmts[0] = fmt;
    if (msf_nan_delivery(fmt, ops, fmts, 1, 0, &out, flags)) {
        return out;
    }
    if (d.cls == MSF_VC_INFINITY) {
        if (!d.sign) {
            return fp->infinity;
        }
        if (is_m1) {
            return msf_pack_generic(fp, 1, 0, msf_u128_from_u64(1u), 0,
                                    rm, flags);
        }
        return msf_pack_generic(fp, 0, 0, msf_u128_from_u64(0u), 0,
                                rm, flags);
    }
    if (d.cls == MSF_VC_ZERO) {
        if (!is_m1) {
            return msf_pack_generic(fp, 0, 0, msf_u128_from_u64(1u), 0,
                                    rm, flags);
        }
        return msf_pack_generic(fp, d.sign, 0, msf_u128_from_u64(0u), 0,
                                rm, flags);
    }
    /* exact exponent cuts, before the split (design Sec. 4) */
    if (!is_m1) {
        int32_t e_tie = fp->emin - fp->precision;
        if (explog_cmp_int(&d, fp->emax + 1) >= 0) {
            return explog_pack_pow2(fp, 0, fp->emax + 1, rm, flags);
        }
        if (explog_cmp_int(&d, e_tie) < 0) {
            return explog_pack_pow2(fp, 0, e_tie - 1, rm, flags);
        }
    } else {
        if (explog_cmp_int(&d, fp->emax + 2) >= 0) {
            return explog_pack_pow2(fp, 0, fp->emax + 2, rm, flags);
        }
        if (explog_cmp_int(&d, -(fp->precision + 1)) < 0) {
            /* saturation: pack the proxy magnitude 1 - 2^-128 */
            msf_u128_t ones;
            int i;
            for (i = 0; i < 4; i++) {
                ones.w[i] = 0xffffffffu;
            }
            return msf_pack_generic(fp, 1, -128, ones, 0, rm, flags);
        }
    }
    sig = msf_u128_to_u64_trunc(d.sig);
    e = d.exp;
    if (e >= 0) {
        is_int = 1;
        ipart = sig << (unsigned)e;
        rem = 0u;
    } else {
        k = -e;
        if (k < 64) {
            ipart = sig >> (unsigned)k;
            rem = sig & ((1ULL << (unsigned)k) - 1ULL);
            half = 1ULL << (unsigned)(k - 1);
        } else {
            ipart = 0u;
            rem = sig;
            half = 0u;
        }
        is_int = rem == 0u;
    }
    if (is_int) {
        n_int = d.sign ? -(int32_t)ipart : (int32_t)ipart;
        if (!is_m1) {
            return explog_pack_pow2(fp, 0, n_int, rm, flags);
        }
        if (n_int == 0) {
            return msf_pack_generic(fp, d.sign, 0,
                                    msf_u128_from_u64(0u), 0, rm, flags);
        }
        if (n_int > 0) {
            return explog_pack_bracket(fp, 0, 0, n_int, NULL, 1, 0, 0,
                                       rm, flags);
        }
        return explog_pack_bracket(fp, 1, n_int, 0, NULL, 1, 0, 0,
                                   rm, flags);
    }
    /* nearest-integer split x = n + f (design Sec. 4) */
    f_exp = -k;
    if (!d.sign) {
        if (k >= 64 || rem <= half) {
            n_int = (int32_t)ipart;
            f_sign = 0;
            f_num = rem;
        } else {
            n_int = (int32_t)ipart + 1;
            f_sign = 1;
            f_num = (1ULL << (unsigned)k) - rem;
        }
    } else {
        if (k >= 64 || rem <= half) {
            n_int = -(int32_t)ipart;
            f_sign = 1;
            f_num = rem;
        } else {
            n_int = -(int32_t)ipart - 1;
            f_sign = 0;
            f_num = (1ULL << (unsigned)k) - rem;
        }
    }
    sh.ns = n_int;
    sh.ones_lo = 0;
    sh.ones_hi = 0;
    sh.q_neg = 0;
    sh.sign = 0;
    kind = f_sign ? 2 : 0;
    if (!is_m1) {
        if (!f_sign && n_int == 0) {
            /* near-1 attractor: 1 + m composed at pack scale
             * (m can be ~2^-1075 relative, far below any
             * stage Ek on the direct v path) */
            sh.kind = EXPLOG_SH_BRACKET;
            sh.sign = 0;
            sh.ones_lo = 0;
            sh.ones_hi = 1;
            sh.q_neg = 0;
        } else if (!f_sign) {
            sh.kind = EXPLOG_SH_PLAIN;
            sh.sign = 0;
            kind = 1;
        } else {
            sh.kind = EXPLOG_SH_ONEMINUS;
        }
    } else if (n_int == 0) {
        sh.kind = EXPLOG_SH_PLAIN;
        sh.sign = f_sign;
    } else if (n_int >= 1) {
        sh.kind = EXPLOG_SH_BRACKET;
        sh.sign = 0;
        sh.ones_lo = 0;
        sh.ones_hi = n_int;
        sh.q_neg = f_sign;
    } else {
        sh.kind = EXPLOG_SH_BRACKET;
        sh.sign = 1;
        sh.ones_lo = n_int;
        sh.ones_hi = 0;
        sh.q_neg = !f_sign;
    }
    for (stage = EXPLOG_START_STAGE; stage < 3; stage++) {
        wf_t approx;
        int n = MSF_EXPLOG_STAGE_LIMBS[stage];
        msf_flags_t tflags = 0u;
        EXPLOG_COUNT_STAGE(stage);
        explog_eval(&approx, kind, f_num, f_exp, stage);
        if (explog_decide(fp, &sh, &approx, n, stage, rm, &out, &tflags)) {
            *flags |= tflags;
            return out;
        }
        if (stage == 2) {
            /* Unreachable under the leg-(c) margin argument;
             * counted: any hit in evidence is a STOP. */
            EXPLOG_COUNT_FINAL();
            *flags |= tflags;
            return out;
        }
    }
    return out;
}

#define DEF_EXPLOG(NAME, FMT, TYPE, ISM1) \
    TYPE NAME(TYPE a, msf_rounding_t rm, msf_flags_t *fl) \
    { return (TYPE)explog_core(FMT, ISM1, (uint64_t)a, (int)rm, fl); }

DEF_EXPLOG(msf16_exp2, MSF_FMT_F16, msf16_t, 0)
DEF_EXPLOG(msf32_exp2, MSF_FMT_F32, msf32_t, 0)
DEF_EXPLOG(msf64_exp2, MSF_FMT_F64, msf64_t, 0)
DEF_EXPLOG(msf16_exp2m1, MSF_FMT_F16, msf16_t, 1)
DEF_EXPLOG(msf32_exp2m1, MSF_FMT_F32, msf32_t, 1)
DEF_EXPLOG(msf64_exp2m1, MSF_FMT_F64, msf64_t, 1)
