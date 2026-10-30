/* msf_alg.c - Clause 9.2 algebraic functions (SF-2 Step 2).
 * This TU carries rSqrt (Step 2a) and hypot (Step 2b) at
 * binary16/32/64.
 *
 * Design record: audit-bundle/ledger/parcel-w5alg1.md (design entry),
 * realising docs/studies/SF-2.md Sec. 3 and the SF-2
 * algebraic study Sec. 3.1. rSqrt(x) = 1/sqrt(x) is decided
 * by exact integer arithmetic: normalize the operand to
 * x = M' * 2^E' with E' even and 2^(p-1) <= M' < 2^(p+1),
 * take S = p + 9 + (p-1)/2, and find Q = floor(2^S/sqrt(M'))
 * by bit search, each candidate tested by the exact compare
 * cand^2 * M' vs 2^(2S). That compare is a 178-bit logical
 * product at binary64, evaluated as a split over the
 * existing 128-bit multiplies (WIDTHS row r_sqrt); no new
 * storage width is introduced. One call of the unmodified
 * msf_pack_generic on (0, -S - E'/2, Q, sticky) with
 * sticky = (Q^2 * M' != 2^(2S)) is then the correctly
 * rounded result in every attribute: Q has at least seven
 * bits below the destination significand in every attainable
 * binade, so the pack sees the exact guard/round/sticky of
 * the true value. The result range is strictly interior at
 * every format (binary64 [2^-512.01, 2^537]), so overflow
 * and underflow are unattainable; the pack still owns every
 * flag judgement on the finite path.
 *
 * Specials (study Sec. 5.1): NaNs ride the SF-0 2.5 matrix
 * via msf_nan_delivery; a negative nonzero operand or -inf
 * is outside the domain and delivers the default quiet NaN
 * with invalid; +inf delivers +0; both signed zeros are the
 * simple pole and deliver the correspondingly signed
 * infinity with divideByZero (the -0 pole sign is the
 * study's paired-sign cell, second-read in the design
 * entry; an executed MPFR disagrees there, so that cell is
 * table-decided in both kernel and vector generation,
 * never oracle-sourced).
 *
 * hypot (design record: audit-bundle/ledger/parcel-w5alg2.md, realising
 * study Sec. 3.2): order the finite magnitudes, anchor a
 * window at the top of the larger square inside the existing
 * u128 (window sum < 2^122), align the smaller square by
 * truncation with a separate tail sticky - never a jam into
 * the sqrt input, the floor-sum form being mandatory because
 * exact midpoint ties are attainable - finish with the
 * sqrt_core scaling (119..122-bit radicand, 60/61-bit root,
 * sticky = tail OR parity-dropped OR remainder) and one
 * unmodified pack, sign always +. Specials are evaluated in
 * the study Sec. 5.2 order: signaling NaN first (quieted
 * delivery + invalid), then any infinity delivers +inf
 * (including beside a quiet NaN, either order), then the
 * quiet-NaN matrix, then both-zeros +0, then finite.
 */
#include "msf_internal.h"
#include "msf_decode.h"

static int blen64(uint64_t x)
{
    int n = 0;
    while (x != 0u) {
        n++;
        x >>= 1;
    }
    return n;
}

/* Compare cand^2 * mp against 2^(2S): -1, 0, +1. cand < 2^63
 * and mp < 2^54 keep each split partial product inside one
 * 128-bit multiply; the six-limb assembly is compare-only. */
static int alg_cmp_sq(uint64_t cand, uint64_t mp, int s)
{
    msf_u128_t sq = msf_u128_mul_u64_u64(cand, cand);
    uint64_t b = msf_u128_to_u64_trunc(sq);
    uint64_t a = ((uint64_t)sq.w[3] << 32) | (uint64_t)sq.w[2];
    msf_u128_t mb = msf_u128_mul_u64_u64(mp, b);
    msf_u128_t ma = msf_u128_mul_u64_u64(mp, a);
    uint32_t prod[6];
    uint64_t carry = 0u;
    int i, tl, tb;
    for (i = 0; i < 4; i++) {
        prod[i] = mb.w[i];
    }
    prod[4] = 0u;
    prod[5] = 0u;
    for (i = 0; i < 4; i++) {
        uint64_t t = (uint64_t)prod[2 + i] + (uint64_t)ma.w[i] + carry;
        prod[2 + i] = (uint32_t)t;
        carry = t >> 32;
    }
    if (carry != 0u) {
        return 1; /* >= 2^192 > 2^(2S): unreachable by the bounds */
    }
    tl = (2 * s) / 32;
    tb = (2 * s) % 32;
    for (i = 5; i >= 0; i--) {
        uint32_t tv = i == tl ? (1u << tb) : 0u;
        if (prod[i] != tv) {
            return prod[i] > tv ? 1 : -1;
        }
    }
    return 0;
}

static uint64_t rsqrt_core(int fmt, uint64_t bits, int rm,
                           msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    msf_decoded_t d = msf_decode(fmt, bits);
    msf_decoded_t ops[1];
    int fmts[1];
    int inv = d.sign && d.cls != MSF_VC_ZERO;
    uint64_t out, m, q;
    int32_t e, ep;
    int p, bl, shift, s, top, k;

    ops[0] = d;
    fmts[0] = fmt;
    if (msf_nan_delivery(fmt, ops, fmts, 1, inv, &out, flags)) {
        return out;
    }
    if (d.cls == MSF_VC_ZERO) {
        *flags |= MSF_FLAG_DIVISION_BY_ZERO;
        return (d.sign ? fp->sign_mask : 0u) | fp->infinity;
    }
    if (d.cls == MSF_VC_INFINITY) {
        return 0u; /* +inf -> +0 (-inf took the NaN delivery) */
    }
    /* Finite x > 0: x = m * 2^e with m < 2^p. */
    p = fp->precision;
    m = msf_u128_to_u64_trunc(d.sig);
    e = d.exp;
    bl = blen64(m);
    shift = p - bl;
    m <<= shift;
    ep = e - shift;
    if ((ep % 2) != 0) {
        m <<= 1; /* now m < 2^(p+1), ep even */
        ep -= 1;
    }
    s = p + 9 + (p - 1) / 2;
#ifdef MSF_ALG_TEST_TRUNC
    /* Permanent negative control only: truncating the stage
     * scale destroys the pack-feed margin, so this build must
     * fail the committed vectors. Never defined in a build
     * whose results are quoted as the shipped library. */
    s -= 12;
#endif
    top = s - (p - 1) / 2; /* Q <= 2^top since m >= 2^(p-1) */
    q = 0u;
    for (k = top; k >= 0; k--) {
        uint64_t cand = q | (1ULL << k);
        if (alg_cmp_sq(cand, m, s) <= 0) {
            q = cand;
        }
    }
    return msf_pack_generic(fp, 0, -s - ep / 2, msf_u128_from_u64(q),
                            alg_cmp_sq(q, m, s) != 0, rm, flags);
}

static int blen128(msf_u128_t a)
{
    return 128 - msf_u128_clz(a);
}

static int any_bits_below128(msf_u128_t a, int32_t n)
{
    if (n <= 0) {
        return 0;
    }
    if (n >= 128) {
        return !msf_u128_is_zero(a);
    }
    return !msf_u128_is_zero(msf_u128_shl(a, (unsigned)(128 - n)));
}

static uint64_t hypot_core(int fmt, uint64_t abits, uint64_t bbits,
                           int rm, msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    msf_decoded_t da = msf_decode(fmt, abits);
    msf_decoded_t db = msf_decode(fmt, bbits);
    msf_decoded_t ops[2];
    int fmts[2];
    uint64_t out = 0, q;
    msf_u128_t sa, sb, tot, rad, rem;
    int la2, lsh, net, tail = 0, pdrop = 0, sticky, k;
    int32_t ea, eb, ew;

    ops[0] = da;
    ops[1] = db;
    fmts[0] = fmt;
    fmts[1] = fmt;
    /* Evaluation order (study Sec. 5.2): signaling NaN first,
     * then infinity over a quiet NaN, then the NaN matrix. */
    if (da.cls == MSF_VC_SIGNALING_NAN
            || db.cls == MSF_VC_SIGNALING_NAN) {
        (void)msf_nan_delivery(fmt, ops, fmts, 2, 0, &out, flags);
        return out;
    }
    if (da.cls == MSF_VC_INFINITY || db.cls == MSF_VC_INFINITY) {
        return fp->infinity; /* +inf, no flag, sign always + */
    }
    if (msf_nan_delivery(fmt, ops, fmts, 2, 0, &out, flags)) {
        return out;
    }
    if (da.cls == MSF_VC_ZERO && db.cls == MSF_VC_ZERO) {
        return 0u; /* hypot(+-0, +-0) = +0 */
    }
    /* Finite: order |a| >= |b| (even in both operands). With
     * that ordering ea >= eb (design entry lemma). */
    {
        msf_decoded_t ca = da, cb = db;
        ca.sign = 0;
        cb.sign = 0;
        if (msf_cmp_finite(&ca, &cb) < 0) {
            msf_decoded_t t = da;
            da = db;
            db = t;
        }
    }
    sa = msf_u128_mul_u64_u64(msf_u128_to_u64_trunc(da.sig),
                              msf_u128_to_u64_trunc(da.sig));
    sb = msf_u128_mul_u64_u64(msf_u128_to_u64_trunc(db.sig),
                              msf_u128_to_u64_trunc(db.sig));
    ea = da.exp;
    eb = db.exp;
    la2 = blen128(sa); /* sa != 0: the larger operand is nonzero */
    lsh = 121 - la2;
    tot = msf_u128_shl(sa, (unsigned)lsh);
    net = lsh - 2 * (int)(ea - eb);
    if (net >= 0) {
        sb = msf_u128_shl(sb, (unsigned)net);
    } else {
#ifdef MSF_ALG_TEST_JAM
        /* Permanent test-only mutant: jam the aligned square
         * into the window sum instead of truncating with a
         * separate sticky. Measured packed-equivalent to the
         * shipped floor form in this realization (design
         * addendum); never defined in a quoted build. */
        (void)any_bits_below128(sb, -net);
        sb = msf_u128_shr_jam(sb, (unsigned)-net, 0);
#else
        tail = any_bits_below128(sb, -net);
        sb = msf_u128_shr(sb, (unsigned)-net);
#endif
    }
    tot = msf_u128_add(tot, sb, 0); /* < 2^122: sb <= sa window */
    ew = 2 * ea - lsh;
    if ((ew % 2) != 0) {
#ifdef MSF_ALG_TEST_JAM
        rad = msf_u128_shr(tot, 1);
        rad.w[0] |= tot.w[0] & 1u;
#else
        pdrop = (int)(tot.w[0] & 1u);
        rad = msf_u128_shr(tot, 1);
#endif
        ew += 1;
    } else {
        rad = tot;
    }
    q = 0u;
    for (k = 60; k >= 0; k--) {
        uint64_t cand = q | (1ULL << k);
        if (msf_u128_cmp(msf_u128_mul_u64_u64(cand, cand), rad) <= 0) {
            q = cand;
        }
    }
    rem = msf_u128_sub(rad, msf_u128_mul_u64_u64(q, q), 0);
    sticky = tail || pdrop || !msf_u128_is_zero(rem);
#if defined(MSF_ALG_TEST_JAM) || defined(MSF_ALG_TEST_NOSTICKY)
    /* MSF_ALG_TEST_NOSTICKY: permanent test-only mutant that
     * drops the tail/parity sticky (keeps floor alignment);
     * it must fail the committed tie family. JAM shares the
     * remainder-only sticky by construction. */
    sticky = !msf_u128_is_zero(rem);
#endif
    return msf_pack_generic(fp, 0, ew / 2, msf_u128_from_u64(q),
                            sticky, rm, flags);
}

#define DEF_RSQRT(NAME, FMT, TYPE) \
    TYPE NAME(TYPE a, msf_rounding_t rm, msf_flags_t *fl) \
    { return (TYPE)rsqrt_core(FMT, (uint64_t)a, (int)rm, fl); }

DEF_RSQRT(msf16_r_sqrt, MSF_FMT_F16, msf16_t)
DEF_RSQRT(msf32_r_sqrt, MSF_FMT_F32, msf32_t)
DEF_RSQRT(msf64_r_sqrt, MSF_FMT_F64, msf64_t)

#define DEF_HYPOT(NAME, FMT, TYPE) \
    TYPE NAME(TYPE a, TYPE b, msf_rounding_t rm, msf_flags_t *fl) \
    { return (TYPE)hypot_core(FMT, (uint64_t)a, (uint64_t)b, \
                              (int)rm, fl); }

DEF_HYPOT(msf16_hypot, MSF_FMT_F16, msf16_t)
DEF_HYPOT(msf32_hypot, MSF_FMT_F32, msf32_t)
DEF_HYPOT(msf64_hypot, MSF_FMT_F64, msf64_t)
