/* msf_alg.c - Clause 9.2 algebraic functions (SF-2 Step 2).
 * This TU carries rSqrt at binary16/32/64 (Step 2a); hypot
 * joins it in its own parcel.
 *
 * Design record: ledger/parcel-w5alg1.md (design entry),
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

#define DEF_RSQRT(NAME, FMT, TYPE) \
    TYPE NAME(TYPE a, msf_rounding_t rm, msf_flags_t *fl) \
    { return (TYPE)rsqrt_core(FMT, (uint64_t)a, (int)rm, fl); }

DEF_RSQRT(msf16_r_sqrt, MSF_FMT_F16, msf16_t)
DEF_RSQRT(msf32_r_sqrt, MSF_FMT_F32, msf32_t)
DEF_RSQRT(msf64_r_sqrt, MSF_FMT_F64, msf64_t)
