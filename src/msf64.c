/* msf64.c - binary64 translation unit (SF-0 Section 3.1).
 *
 * Wave 1 binary64-destination instantiations (design entry:
 * audit-bundle/ledger/parcel-f64.md). Every operation: decode, NaN delivery, special
 * cases, exact integer work over msf_u128, one rounding pack.
 * Clause citations are to IEEE 754-2019 by number only.
 *
 * Wave 2 parcel-xf: the binary16-source instantiations are
 * additional wrappers over the same format-generic cores below.
 * Sources decode exactly in their own format (binary16/binary32
 * values are never materialized in an intermediate format) and the
 * exact result packs once. Landed Wave 1 wrappers are untouched.
 */
#include "msf_internal.h"
#include "msf_decode.h"

#define MSF_PF 64
#include "msf_performat.inc"

#define SGN64 MSF_F64_SIGN_MASK
#define INF64 MSF_F64_INFINITY

static msf_u128_t z128(void)
{
    return msf_u128_from_u64(0u);
}

static int blen128(msf_u128_t a)
{
    return 128 - msf_u128_clz(a);
}

static int bit128(msf_u128_t a, int32_t n)
{
    if (n < 0 || n >= 128) {
        return 0;
    }
    return (int)((a.w[n / 32] >> (n % 32)) & 1u);
}

static int any_below128(msf_u128_t a, int32_t n)
{
    if (n <= 0) {
        return 0;
    }
    if (n >= 128) {
        return !msf_u128_is_zero(a);
    }
    return !msf_u128_is_zero(msf_u128_shl(a, (unsigned)(128 - n)));
}

static msf64_t pk64(int sign, int32_t exp2, msf_u128_t sig, int sticky,
                    int rm, msf_flags_t *flags)
{
    return msf_pack_f64(sign, exp2, sig, sticky, rm, flags);
}

static msf64_t inf_bits(int sign)
{
    return (msf64_t)((sign ? SGN64 : 0u) | INF64);
}

static msf64_t zero_bits(int sign)
{
    return (msf64_t)(sign ? SGN64 : 0u);
}

/* Signed addition of two exact terms (sig times 2^exp), one pack.
 * Terms are aligned into a 118-bit window under the higher top bit:
 * exact shift when the term reaches the window, jam shift only for
 * a term whose top sits far below the dominant top, where the jam
 * bit can act only as sticky evidence below the rounding bits.
 * Bound: an exponent gap of at most 65 (118 minus 53) keeps a
 * 53-bit significand whole inside the window, so close operands
 * align exactly; a larger gap bounds cancellation so the result
 * top stays within a bit of the dominant top and the jam bit at
 * the window bottom stays at least 60 bits below the result top,
 * while the pack needs only p+2 = 55 bits under the top to decide
 * rounding. The 106-bit FMA product term is likewise exact in the
 * window whenever its top is the dominant one (top minus 106 is
 * inside top minus 118). */
static msf_u128_t align_term(msf_u128_t m, int32_t e, int32_t ce)
{
    if (e >= ce) {
        return msf_u128_shl(m, (unsigned)(e - ce));
    }
    return msf_u128_shr_jam(m, (unsigned)(ce - e), 0);
}

static msf64_t add_terms(int s1, msf_u128_t m1, int32_t e1,
                         int s2, msf_u128_t m2, int32_t e2,
                         int rm, msf_flags_t *flags)
{
    int32_t t1, t2, top, ce;
    msf_u128_t a, b, r;
    int c;

    if (msf_u128_is_zero(m1) && msf_u128_is_zero(m2)) {
        int s = (s1 == s2) ? s1 : (rm == MSF_IROUND_TOWARD_NEGATIVE);
        return (msf64_t)zero_bits(s);
    }
    if (msf_u128_is_zero(m1)) {
        return pk64(s2, e2, m2, 0, rm, flags);
    }
    if (msf_u128_is_zero(m2)) {
        return pk64(s1, e1, m1, 0, rm, flags);
    }
    t1 = e1 + blen128(m1);
    t2 = e2 + blen128(m2);
    top = t1 > t2 ? t1 : t2;
    ce = top - 118;
    a = align_term(m1, e1, ce);
    b = align_term(m2, e2, ce);
    if (s1 == s2) {
        r = msf_u128_add(a, b, 0);
        return pk64(s1, ce, r, 0, rm, flags);
    }
    c = msf_u128_cmp(a, b);
    if (c == 0) {
        return (msf64_t)zero_bits(rm == MSF_IROUND_TOWARD_NEGATIVE);
    }
    if (c > 0) {
        r = msf_u128_sub(a, b, 0);
        return pk64(s1, ce, r, 0, rm, flags);
    }
    r = msf_u128_sub(b, a, 0);
    return pk64(s2, ce, r, 0, rm, flags);
}

static msf64_t addsub_core(int fa, uint64_t ab, int fb, uint64_t bb,
                           int is_sub, int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(fa, ab);
    msf_decoded_t b = msf_decode(fb, bb);
    msf_decoded_t ops[2];
    int fmts[2];
    int esign = b.sign ^ is_sub;
    int inv = a.cls == MSF_VC_INFINITY && b.cls == MSF_VC_INFINITY
              && a.sign != esign;
    uint64_t out;

    ops[0] = a; ops[1] = b; fmts[0] = fa; fmts[1] = fb;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 2, inv, &out, flags)) {
        return (msf64_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        return inf_bits(a.sign);
    }
    if (b.cls == MSF_VC_INFINITY) {
        return inf_bits(esign);
    }
    return add_terms(a.sign, a.sig, a.exp, esign, b.sig, b.exp, rm, flags);
}

static msf64_t mul_core(int fa, uint64_t ab, int fb, uint64_t bb,
                        int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(fa, ab);
    msf_decoded_t b = msf_decode(fb, bb);
    msf_decoded_t ops[2];
    int fmts[2];
    int sign = a.sign ^ b.sign;
    int inv = (a.cls == MSF_VC_ZERO && b.cls == MSF_VC_INFINITY)
              || (a.cls == MSF_VC_INFINITY && b.cls == MSF_VC_ZERO);
    uint64_t out;
    msf_u128_t prod;

    ops[0] = a; ops[1] = b; fmts[0] = fa; fmts[1] = fb;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 2, inv, &out, flags)) {
        return (msf64_t)out;
    }
    if (a.cls == MSF_VC_INFINITY || b.cls == MSF_VC_INFINITY) {
        return inf_bits(sign);
    }
    if (a.cls == MSF_VC_ZERO || b.cls == MSF_VC_ZERO) {
        return zero_bits(sign);
    }
    prod = msf_u128_mul_u64_u64(msf_u128_to_u64_trunc(a.sig),
                                msf_u128_to_u64_trunc(b.sig));
    return pk64(sign, a.exp + b.exp, prod, 0, rm, flags);
}

static msf64_t div_core(int fa, uint64_t ab, int fb, uint64_t bb,
                        int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(fa, ab);
    msf_decoded_t b = msf_decode(fb, bb);
    msf_decoded_t ops[2];
    int fmts[2];
    int sign = a.sign ^ b.sign;
    int inv = (a.cls == MSF_VC_ZERO && b.cls == MSF_VC_ZERO)
              || (a.cls == MSF_VC_INFINITY && b.cls == MSF_VC_INFINITY);
    uint64_t out, av, bv;
    int la, lb, scale, i;
    msf_u128_t rem, quo, dvs;

    ops[0] = a; ops[1] = b; fmts[0] = fa; fmts[1] = fb;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 2, inv, &out, flags)) {
        return (msf64_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        return inf_bits(sign);
    }
    if (b.cls == MSF_VC_INFINITY || a.cls == MSF_VC_ZERO) {
        return zero_bits(sign);
    }
    if (b.cls == MSF_VC_ZERO) {
        *flags |= MSF_FLAG_DIVISION_BY_ZERO;
        return inf_bits(sign);
    }
    /* Finite nonzero: quotient with about 122 bits, remainder sticky. */
    av = msf_u128_to_u64_trunc(a.sig);
    bv = msf_u128_to_u64_trunc(b.sig);
    la = blen128(a.sig);
    lb = blen128(b.sig);
    scale = 122 - (la - lb);
    rem = z128();
    quo = z128();
    dvs = msf_u128_from_u64(bv);
    for (i = la + scale - 1; i >= 0; i--) {
        int bit = (i >= scale) ? (int)((av >> (i - scale)) & 1u) : 0;
        rem = msf_u128_shl(rem, 1u);
        rem.w[0] |= (uint32_t)bit;
        if (msf_u128_cmp(rem, dvs) >= 0) {
            rem = msf_u128_sub(rem, dvs, 0);
            if (i < 128) {
                quo.w[i / 32] |= 1u << (i % 32);
            }
        }
    }
    return pk64(sign, a.exp - b.exp - scale, quo,
                !msf_u128_is_zero(rem), rm, flags);
}

static msf64_t sqrt_core(int fa, uint64_t ab, int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(fa, ab);
    msf_decoded_t ops[1];
    int fmts[1];
    int inv = a.sign && a.cls != MSF_VC_ZERO;
    uint64_t out, q;
    int la, shift, k;
    msf_u128_t n, rem;

    ops[0] = a; fmts[0] = fa;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 1, inv, &out, flags)) {
        return (msf64_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        return inf_bits(0);
    }
    if (a.cls == MSF_VC_ZERO) {
        return zero_bits(a.sign);
    }
    la = blen128(a.sig);
    shift = 120 - la;
    if (((a.exp - shift) % 2) != 0) {
        shift -= 1;
    }
    n = msf_u128_shl(a.sig, (unsigned)shift);
    q = 0u;
    for (k = 60; k >= 0; k--) {
        uint64_t cand = q | (1ULL << k);
        if (msf_u128_cmp(msf_u128_mul_u64_u64(cand, cand), n) <= 0) {
            q = cand;
        }
    }
    rem = msf_u128_sub(n, msf_u128_mul_u64_u64(q, q), 0);
    return pk64(0, (a.exp - shift) / 2, msf_u128_from_u64(q),
                !msf_u128_is_zero(rem), rm, flags);
}

static msf64_t fma_core(int fa, uint64_t ab, int fb, uint64_t bb,
                        int fc, uint64_t cb, int rm, msf_flags_t *flags)
{
    msf_decoded_t x = msf_decode(fa, ab);
    msf_decoded_t y = msf_decode(fb, bb);
    msf_decoded_t c = msf_decode(fc, cb);
    msf_decoded_t ops[3];
    int fmts[3];
    int psign = x.sign ^ y.sign;
    int prod_inv = (x.cls == MSF_VC_ZERO && y.cls == MSF_VC_INFINITY)
                   || (x.cls == MSF_VC_INFINITY && y.cls == MSF_VC_ZERO);
    int prod_inf = (x.cls == MSF_VC_INFINITY || y.cls == MSF_VC_INFINITY)
                   && x.cls != MSF_VC_ZERO && y.cls != MSF_VC_ZERO
                   && !msf_is_nan_cls(x.cls) && !msf_is_nan_cls(y.cls);
    int inv = prod_inv
              || (prod_inf && c.cls == MSF_VC_INFINITY && c.sign != psign);
    uint64_t out;
    msf_u128_t prod;

    ops[0] = x; ops[1] = y; ops[2] = c;
    fmts[0] = fa; fmts[1] = fb; fmts[2] = fc;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 3, inv, &out, flags)) {
        if (prod_inv) {
            *flags |= MSF_FLAG_INVALID;
        }
        return (msf64_t)out;
    }
    if (prod_inf) {
        return inf_bits(psign);
    }
    if (c.cls == MSF_VC_INFINITY) {
        return inf_bits(c.sign);
    }
    if (x.cls == MSF_VC_ZERO || y.cls == MSF_VC_ZERO) {
        prod = z128();
    } else {
        prod = msf_u128_mul_u64_u64(msf_u128_to_u64_trunc(x.sig),
                                    msf_u128_to_u64_trunc(y.sig));
    }
    return add_terms(psign, prod, x.exp + y.exp,
                     c.sign, c.sig, c.exp, rm, flags);
}

static msf64_t conv_core(int fa, uint64_t ab, int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(fa, ab);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out;

    ops[0] = a; fmts[0] = fa;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 1, 0, &out, flags)) {
        return (msf64_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        return inf_bits(a.sign);
    }
    if (a.cls == MSF_VC_ZERO) {
        return zero_bits(a.sign);
    }
    return pk64(a.sign, a.exp, a.sig, 0, rm, flags);
}

/* Round a finite magnitude (sig times 2^exp, exp negative) to an
 * integer magnitude per internal mode irm. Sets *frac when a
 * nonzero fraction was present. */
static msf_u128_t round_mag_int(msf_u128_t sig, int32_t exp, int sign,
                                int irm, int *frac)
{
    int32_t s = -exp;
    msf_u128_t q = msf_u128_shr(sig, (unsigned)s);
    int half = bit128(sig, s - 1);
    int below = any_below128(sig, s - 1);
    int inc = 0;

    *frac = any_below128(sig, s);
    switch (irm) {
    case MSF_IROUND_TIES_TO_EVEN:
        inc = half && (below || (q.w[0] & 1u));
        break;
    case MSF_IROUND_TIES_TO_AWAY:
        inc = half;
        break;
    case MSF_IROUND_TOWARD_POSITIVE:
        inc = !sign && *frac;
        break;
    case MSF_IROUND_TOWARD_NEGATIVE:
        inc = sign && *frac;
        break;
    default:
        inc = 0;
        break;
    }
    if (inc) {
        q = msf_u128_add_u32(q, 1u, 0);
    }
    return q;
}

static msf64_t rint_core(msf64_t ab, int irm, int exact_form,
                         msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(MSF_FMT_F64, ab);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out;
    int frac = 0;
    msf_u128_t q;
    msf_flags_t tmp = 0u;
    msf64_t r;

    ops[0] = a; fmts[0] = MSF_FMT_F64;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 1, 0, &out, flags)) {
        return (msf64_t)out;
    }
    if (a.cls == MSF_VC_INFINITY || a.cls == MSF_VC_ZERO || a.exp >= 0) {
        return ab;
    }
    q = round_mag_int(a.sig, a.exp, a.sign, irm, &frac);
    r = pk64(a.sign, 0, q, 0, MSF_IROUND_TIES_TO_EVEN, &tmp);
    if (exact_form && frac) {
        *flags |= MSF_FLAG_INEXACT;
    }
    return r;
}

static msf64_t next_core(msf64_t ab, int is_up, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(MSF_FMT_F64, ab);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out;
    const uint64_t maxfin = 0x7fefffffffffffffull;

    ops[0] = a; fmts[0] = MSF_FMT_F64;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 1, 0, &out, flags)) {
        return (msf64_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        if (is_up) {
            return a.sign ? (msf64_t)(SGN64 | maxfin) : ab;
        }
        return a.sign ? ab : (msf64_t)maxfin;
    }
    if (a.cls == MSF_VC_ZERO) {
        return is_up ? (msf64_t)1u : (msf64_t)(SGN64 | 1u);
    }
    if (!a.sign) {
        return (msf64_t)(is_up ? ab + 1u : ab - 1u);
    }
    return (msf64_t)(is_up ? ab - 1u : ab + 1u);
}

static msf64_t scaleb_core(msf64_t ab, msf64_t nb, int rm,
                           msf_flags_t *flags)
{
    msf_decoded_t x = msf_decode(MSF_FMT_F64, ab);
    msf_decoded_t n = msf_decode(MSF_FMT_F64, nb);
    msf_decoded_t ops[2];
    int fmts[2];
    uint64_t out;
    int32_t nint;

    ops[0] = x; ops[1] = n; fmts[0] = MSF_FMT_F64; fmts[1] = MSF_FMT_F64;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 2, 0, &out, flags)) {
        return (msf64_t)out;
    }
    if (x.cls == MSF_VC_ZERO || x.cls == MSF_VC_INFINITY
        || n.cls == MSF_VC_ZERO) {
        return ab;
    }
    if (n.cls == MSF_VC_INFINITY) {
        nint = n.sign ? -5000 : 5000;
    } else {
        int32_t top = n.exp + blen128(n.sig);
        if (top > 13) {
            nint = n.sign ? -5000 : 5000;
        } else {
            msf_u128_t mag;
            if (n.exp >= 0) {
                mag = msf_u128_shl(n.sig, (unsigned)n.exp);
            } else {
                mag = msf_u128_shr(n.sig, (unsigned)-n.exp);
            }
            nint = (int32_t)msf_u128_to_u64_trunc(mag);
            if (n.sign) {
                nint = -nint;
            }
        }
    }
    return pk64(x.sign, x.exp + nint, x.sig, 0, rm, flags);
}

static msf64_t logb_core(msf64_t ab, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(MSF_FMT_F64, ab);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out;
    int32_t e;

    ops[0] = a; fmts[0] = MSF_FMT_F64;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 1, 0, &out, flags)) {
        return (msf64_t)out;
    }
    if (a.cls == MSF_VC_ZERO) {
        *flags |= MSF_FLAG_DIVISION_BY_ZERO;
        return inf_bits(1);
    }
    if (a.cls == MSF_VC_INFINITY) {
        return inf_bits(0);
    }
    e = a.exp + blen128(a.sig) - 1;
    return pk64(e < 0, 0,
                msf_u128_from_u64((uint64_t)(e < 0 ? -e : e)),
                0, MSF_IROUND_TIES_TO_EVEN, flags);
}

static int term_cmp(msf_u128_t s1, int32_t e1, msf_u128_t s2, int32_t e2)
{
    msf_decoded_t x, y;

    x.sign = 0; x.exp = e1; x.sig = s1; x.bits = 0u;
    x.cls = msf_u128_is_zero(s1) ? MSF_VC_ZERO : MSF_VC_NORMAL;
    y.sign = 0; y.exp = e2; y.sig = s2; y.bits = 0u;
    y.cls = msf_u128_is_zero(s2) ? MSF_VC_ZERO : MSF_VC_NORMAL;
    return msf_cmp_finite(&x, &y);
}

static msf64_t remainder_core(msf64_t ab, msf64_t bb, msf_flags_t *flags)
{
    msf_decoded_t x = msf_decode(MSF_FMT_F64, ab);
    msf_decoded_t y = msf_decode(MSF_FMT_F64, bb);
    msf_decoded_t ops[2];
    int fmts[2];
    int inv = x.cls == MSF_VC_INFINITY || y.cls == MSF_VC_ZERO;
    uint64_t out, av, bv;
    int32_t d;
    int la, i, q_parity = 0, cmp, up;
    msf_u128_t rem, remsig, dvs;
    int32_t remexp;

    ops[0] = x; ops[1] = y; fmts[0] = MSF_FMT_F64; fmts[1] = MSF_FMT_F64;
    if (msf_nan_delivery(MSF_FMT_F64, ops, fmts, 2, inv, &out, flags)) {
        return (msf64_t)out;
    }
    if (y.cls == MSF_VC_INFINITY || x.cls == MSF_VC_ZERO) {
        return ab;
    }
    av = msf_u128_to_u64_trunc(x.sig);
    bv = msf_u128_to_u64_trunc(y.sig);
    la = blen128(x.sig);
    d = x.exp - y.exp;
    rem = z128();
    if (d >= 0) {
        dvs = msf_u128_from_u64(bv);
        for (i = la + d - 1; i >= 0; i--) {
            int bit = (i >= d) ? (int)((av >> (i - d)) & 1u) : 0;
            rem = msf_u128_shl(rem, 1u);
            rem.w[0] |= (uint32_t)bit;
            q_parity = 0;
            if (msf_u128_cmp(rem, dvs) >= 0) {
                rem = msf_u128_sub(rem, dvs, 0);
                q_parity = 1;
            }
        }
        remsig = rem;
        remexp = y.exp;
    } else if (-d >= 53) {
        remsig = x.sig;
        remexp = x.exp;
    } else {
        dvs = msf_u128_shl(msf_u128_from_u64(bv), (unsigned)-d);
        for (i = la - 1; i >= 0; i--) {
            rem = msf_u128_shl(rem, 1u);
            rem.w[0] |= (uint32_t)((av >> i) & 1u);
            q_parity = 0;
            if (msf_u128_cmp(rem, dvs) >= 0) {
                rem = msf_u128_sub(rem, dvs, 0);
                q_parity = 1;
            }
        }
        remsig = rem;
        remexp = x.exp;
    }
    if (msf_u128_is_zero(remsig)) {
        return zero_bits(x.sign);
    }
    cmp = term_cmp(remsig, remexp + 1, y.sig, y.exp);
    up = (cmp > 0) || (cmp == 0 && q_parity);
    if (!up) {
        return pk64(x.sign, remexp, remsig, 0,
                    MSF_IROUND_TIES_TO_EVEN, flags);
    }
    {
        msf_u128_t mag;
        int32_t mexp;
        if (d >= 0) {
            mag = msf_u128_from_u64(bv - msf_u128_to_u64_trunc(remsig));
            mexp = y.exp;
        } else {
            msf_u128_t yat = msf_u128_shl(msf_u128_from_u64(bv),
                                          (unsigned)-d);
            mag = msf_u128_sub(yat, remsig, 0);
            mexp = x.exp;
        }
        return pk64(x.sign ^ 1, mexp, mag, 0,
                    MSF_IROUND_TIES_TO_EVEN, flags);
    }
}

static uint64_t sat_pos_bits(int width, int is_signed)
{
    if (is_signed) {
        return width == 64 ? 0x7fffffffffffffffull
                           : ((1ull << (width - 1)) - 1ull);
    }
    return width == 64 ? ~0ull : ((1ull << width) - 1ull);
}

static uint64_t sat_neg_bits(int width)
{
    return width == 64 ? 0x8000000000000000ull
                       : (0ull - (1ull << (width - 1)));
}

/* Converts to a width-bit integer; result returned as 64-bit
 * two-complement bit pattern for the wrappers to truncate. */
static uint64_t to_int_core(msf64_t ab, int irm, int exact_form,
                            int width, int is_signed, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(MSF_FMT_F64, ab);
    msf_u128_t q;
    uint64_t q64;
    int frac = 0, huge = 0;

    if (msf_is_nan_cls(a.cls)) {
        *flags |= MSF_FLAG_INVALID;
        return 0u;
    }
    if (a.cls == MSF_VC_INFINITY) {
        *flags |= MSF_FLAG_INVALID;
        return a.sign ? (is_signed ? sat_neg_bits(width) : 0u)
                      : sat_pos_bits(width, is_signed);
    }
    if (a.cls == MSF_VC_ZERO) {
        return 0u;
    }
    if (a.exp >= 0) {
        if (blen128(a.sig) + a.exp > 64) {
            huge = 1;
            q = z128();
        } else {
            q = msf_u128_shl(a.sig, (unsigned)a.exp);
        }
    } else {
        q = round_mag_int(a.sig, a.exp, a.sign, irm, &frac);
    }
    if (!huge && blen128(q) > 64) {
        huge = 1;
    }
    if (huge) {
        *flags |= MSF_FLAG_INVALID;
        return a.sign ? (is_signed ? sat_neg_bits(width) : 0u)
                      : sat_pos_bits(width, is_signed);
    }
    q64 = msf_u128_to_u64_trunc(q);
    if (!a.sign) {
        if (q64 > sat_pos_bits(width, is_signed)) {
            *flags |= MSF_FLAG_INVALID;
            return sat_pos_bits(width, is_signed);
        }
    } else if (q64 != 0u) {
        uint64_t lim = width == 64 ? (1ull << 63) : (1ull << (width - 1));
        if (!is_signed || q64 > lim) {
            *flags |= MSF_FLAG_INVALID;
            return is_signed ? sat_neg_bits(width) : 0u;
        }
    }
    if (exact_form && frac) {
        *flags |= MSF_FLAG_INEXACT;
    }
    return a.sign ? (0ull - q64) : q64;
}

enum {
    PRED_EQ = 0, PRED_NE, PRED_GT, PRED_GE, PRED_LT, PRED_LE,
    PRED_NOTGT, PRED_NOTLT, PRED_LTUN, PRED_GTUN, PRED_UNORD, PRED_ORD
};

static int pred_eval(int pred, int rel)
{
    /* rel: -1 less, 0 equal, 1 greater, 2 unordered (5.11 tables). */
    switch (pred) {
    case PRED_EQ: return rel == 0;
    case PRED_NE: return rel != 0;
    case PRED_GT: return rel == 1;
    case PRED_GE: return rel == 0 || rel == 1;
    case PRED_LT: return rel == -1;
    case PRED_LE: return rel == -1 || rel == 0;
    case PRED_NOTGT: return rel != 1;
    case PRED_NOTLT: return rel != -1;
    case PRED_LTUN: return rel == -1 || rel == 2;
    case PRED_GTUN: return rel == 1 || rel == 2;
    case PRED_UNORD: return rel == 2;
    default: return rel != 2;
    }
}

static int compare_core(int fa, uint64_t ab, int fb, uint64_t bb,
                        int pred, int signaling, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(fa, ab);
    msf_decoded_t b = msf_decode(fb, bb);
    int any_nan = msf_is_nan_cls(a.cls) || msf_is_nan_cls(b.cls);
    int any_snan = a.cls == MSF_VC_SIGNALING_NAN
                   || b.cls == MSF_VC_SIGNALING_NAN;
    int rel;

    if (signaling ? any_nan : any_snan) {
        *flags |= MSF_FLAG_INVALID;
    }
    if (any_nan) {
        rel = 2;
    } else if (a.cls == MSF_VC_INFINITY && b.cls == MSF_VC_INFINITY) {
        rel = (a.sign == b.sign) ? 0 : (a.sign ? -1 : 1);
    } else if (a.cls == MSF_VC_INFINITY) {
        rel = a.sign ? -1 : 1;
    } else if (b.cls == MSF_VC_INFINITY) {
        rel = b.sign ? 1 : -1;
    } else {
        rel = msf_cmp_finite(&a, &b);
    }
    return pred_eval(pred, rel);
}

static uint64_t total_key(uint64_t bits)
{
    return (bits & SGN64) ? ~bits : (bits | SGN64);
}

static msf64_t from_mag(int sign, uint64_t mag, int rm, msf_flags_t *flags)
{
    return pk64(sign, 0, msf_u128_from_u64(mag), 0, rm, flags);
}

/* Public wrappers: arithmetic (dest f64; Wave 1 sources in
 * {f32, f64}, Wave 2 parcel-xf adds the f16-source forms). */
#define DEF_ADD(NAME, FA, TA, FB, TB) \
    msf64_t NAME(TA a, TB b, msf_rounding_t rm, msf_flags_t *fl) \
    { return addsub_core(FA, (uint64_t)a, FB, (uint64_t)b, 0, (int)rm, fl); }
#define DEF_SUB(NAME, FA, TA, FB, TB) \
    msf64_t NAME(TA a, TB b, msf_rounding_t rm, msf_flags_t *fl) \
    { return addsub_core(FA, (uint64_t)a, FB, (uint64_t)b, 1, (int)rm, fl); }
#define DEF_MUL(NAME, FA, TA, FB, TB) \
    msf64_t NAME(TA a, TB b, msf_rounding_t rm, msf_flags_t *fl) \
    { return mul_core(FA, (uint64_t)a, FB, (uint64_t)b, (int)rm, fl); }
#define DEF_DIV(NAME, FA, TA, FB, TB) \
    msf64_t NAME(TA a, TB b, msf_rounding_t rm, msf_flags_t *fl) \
    { return div_core(FA, (uint64_t)a, FB, (uint64_t)b, (int)rm, fl); }

DEF_ADD(msf64_add_f32_f32, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t)
DEF_ADD(msf64_add_f32_f64, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t)
DEF_ADD(msf64_add_f64_f32, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t)
DEF_ADD(msf64_add, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t)
DEF_SUB(msf64_sub_f32_f32, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t)
DEF_SUB(msf64_sub_f32_f64, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t)
DEF_SUB(msf64_sub_f64_f32, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t)
DEF_SUB(msf64_sub, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t)
DEF_MUL(msf64_mul_f32_f32, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t)
DEF_MUL(msf64_mul_f32_f64, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t)
DEF_MUL(msf64_mul_f64_f32, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t)
DEF_MUL(msf64_mul, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t)
DEF_DIV(msf64_div_f32_f32, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t)
DEF_DIV(msf64_div_f32_f64, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t)
DEF_DIV(msf64_div_f64_f32, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t)
DEF_DIV(msf64_div, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t)
DEF_ADD(msf64_add_f16_f16, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t)
DEF_ADD(msf64_add_f16_f32, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t)
DEF_ADD(msf64_add_f16_f64, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t)
DEF_ADD(msf64_add_f32_f16, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t)
DEF_ADD(msf64_add_f64_f16, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t)
DEF_SUB(msf64_sub_f16_f16, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t)
DEF_SUB(msf64_sub_f16_f32, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t)
DEF_SUB(msf64_sub_f16_f64, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t)
DEF_SUB(msf64_sub_f32_f16, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t)
DEF_SUB(msf64_sub_f64_f16, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t)
DEF_MUL(msf64_mul_f16_f16, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t)
DEF_MUL(msf64_mul_f16_f32, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t)
DEF_MUL(msf64_mul_f16_f64, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t)
DEF_MUL(msf64_mul_f32_f16, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t)
DEF_MUL(msf64_mul_f64_f16, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t)
DEF_DIV(msf64_div_f16_f16, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t)
DEF_DIV(msf64_div_f16_f32, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t)
DEF_DIV(msf64_div_f16_f64, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t)
DEF_DIV(msf64_div_f32_f16, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t)
DEF_DIV(msf64_div_f64_f16, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t)

#define DEF_SQRT(NAME, FA, TA) \
    msf64_t NAME(TA a, msf_rounding_t rm, msf_flags_t *fl) \
    { return sqrt_core(FA, (uint64_t)a, (int)rm, fl); }
DEF_SQRT(msf64_sqrt_f32, MSF_FMT_F32, msf32_t)
DEF_SQRT(msf64_sqrt, MSF_FMT_F64, msf64_t)
DEF_SQRT(msf64_sqrt_f16, MSF_FMT_F16, msf16_t)

#define DEF_FMA(NAME, FA, TA, FB, TB, FC, TC) \
    msf64_t NAME(TA a, TB b, TC c, msf_rounding_t rm, msf_flags_t *fl) \
    { return fma_core(FA, (uint64_t)a, FB, (uint64_t)b, FC, (uint64_t)c, \
                      (int)rm, fl); }
DEF_FMA(msf64_fma_f32_f32_f32, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t)
DEF_FMA(msf64_fma_f32_f32_f64, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t)
DEF_FMA(msf64_fma_f32_f64_f32, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t)
DEF_FMA(msf64_fma_f32_f64_f64, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t)
DEF_FMA(msf64_fma_f64_f32_f32, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t)
DEF_FMA(msf64_fma_f64_f32_f64, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t)
DEF_FMA(msf64_fma_f64_f64_f32, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t)
DEF_FMA(msf64_fma, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t)
DEF_FMA(msf64_fma_f16_f16_f16, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t)
DEF_FMA(msf64_fma_f16_f16_f32, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t)
DEF_FMA(msf64_fma_f16_f16_f64, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t)
DEF_FMA(msf64_fma_f16_f32_f16, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t)
DEF_FMA(msf64_fma_f16_f32_f32, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t)
DEF_FMA(msf64_fma_f16_f32_f64, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t)
DEF_FMA(msf64_fma_f16_f64_f16, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t)
DEF_FMA(msf64_fma_f16_f64_f32, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t)
DEF_FMA(msf64_fma_f16_f64_f64, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t)
DEF_FMA(msf64_fma_f32_f16_f16, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t)
DEF_FMA(msf64_fma_f32_f16_f32, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t)
DEF_FMA(msf64_fma_f32_f16_f64, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t)
DEF_FMA(msf64_fma_f32_f32_f16, MSF_FMT_F32, msf32_t, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t)
DEF_FMA(msf64_fma_f32_f64_f16, MSF_FMT_F32, msf32_t, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t)
DEF_FMA(msf64_fma_f64_f16_f16, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t, MSF_FMT_F16, msf16_t)
DEF_FMA(msf64_fma_f64_f16_f32, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t, MSF_FMT_F32, msf32_t)
DEF_FMA(msf64_fma_f64_f16_f64, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t, MSF_FMT_F64, msf64_t)
DEF_FMA(msf64_fma_f64_f32_f16, MSF_FMT_F64, msf64_t, MSF_FMT_F32, msf32_t, MSF_FMT_F16, msf16_t)
DEF_FMA(msf64_fma_f64_f64_f16, MSF_FMT_F64, msf64_t, MSF_FMT_F64, msf64_t, MSF_FMT_F16, msf16_t)

msf64_t msf64_round_to_integral_ties_to_even(msf64_t a, msf_flags_t *fl)
{ return rint_core(a, MSF_IROUND_TIES_TO_EVEN, 0, fl); }
msf64_t msf64_round_to_integral_ties_to_away(msf64_t a, msf_flags_t *fl)
{ return rint_core(a, MSF_IROUND_TIES_TO_AWAY, 0, fl); }
msf64_t msf64_round_to_integral_toward_zero(msf64_t a, msf_flags_t *fl)
{ return rint_core(a, MSF_IROUND_TOWARD_ZERO, 0, fl); }
msf64_t msf64_round_to_integral_toward_positive(msf64_t a, msf_flags_t *fl)
{ return rint_core(a, MSF_IROUND_TOWARD_POSITIVE, 0, fl); }
msf64_t msf64_round_to_integral_toward_negative(msf64_t a, msf_flags_t *fl)
{ return rint_core(a, MSF_IROUND_TOWARD_NEGATIVE, 0, fl); }
msf64_t msf64_round_to_integral_exact(msf64_t a, msf_rounding_t rm,
                                      msf_flags_t *fl)
{ return rint_core(a, (int)rm, 1, fl); }

msf64_t msf64_next_up(msf64_t a, msf_flags_t *fl)
{ return next_core(a, 1, fl); }
msf64_t msf64_next_down(msf64_t a, msf_flags_t *fl)
{ return next_core(a, 0, fl); }

msf64_t msf64_remainder(msf64_t a, msf64_t b, msf_flags_t *fl)
{ return remainder_core(a, b, fl); }

msf64_t msf64_scale_b(msf64_t a, msf64_t n, msf_rounding_t rm,
                      msf_flags_t *fl)
{ return scaleb_core(a, n, (int)rm, fl); }

msf64_t msf64_log_b(msf64_t a, msf_flags_t *fl)
{ return logb_core(a, fl); }

msf64_t msf64_from_f32(msf32_t a, msf_rounding_t rm, msf_flags_t *fl)
{ return conv_core(MSF_FMT_F32, (uint64_t)a, (int)rm, fl); }
msf64_t msf64_from_f64(msf64_t a, msf_rounding_t rm, msf_flags_t *fl)
{ return conv_core(MSF_FMT_F64, (uint64_t)a, (int)rm, fl); }
msf64_t msf64_from_f16(msf16_t a, msf_rounding_t rm, msf_flags_t *fl)
{ return conv_core(MSF_FMT_F16, (uint64_t)a, (int)rm, fl); }

#define DEF_FROM_S(NAME, TY) \
    msf64_t NAME(TY a, msf_rounding_t rm, msf_flags_t *fl) \
    { int s = a < 0; \
      return from_mag(s, s ? (0ull - (uint64_t)a) : (uint64_t)a, \
                      (int)rm, fl); }
#define DEF_FROM_U(NAME, TY) \
    msf64_t NAME(TY a, msf_rounding_t rm, msf_flags_t *fl) \
    { return from_mag(0, (uint64_t)a, (int)rm, fl); }
DEF_FROM_S(msf64_from_i8, int8_t)
DEF_FROM_U(msf64_from_u8, uint8_t)
DEF_FROM_S(msf64_from_i16, int16_t)
DEF_FROM_U(msf64_from_u16, uint16_t)
DEF_FROM_S(msf64_from_i32, int32_t)
DEF_FROM_U(msf64_from_u32, uint32_t)
DEF_FROM_S(msf64_from_i64, int64_t)
DEF_FROM_U(msf64_from_u64, uint64_t)

#define CAT2(a, b) a##b
#define CAT(a, b) CAT2(a, b)
#define TOINT_FN(TOK, SUF) CAT(CAT(msf64_to_, TOK), CAT(_, SUF))
#define DEF_TOINT(TOK, TY, W, SG, SUF, IRM, EX) \
    TY TOINT_FN(TOK, SUF)(msf64_t a, msf_flags_t *fl) \
    { return (TY)to_int_core(a, IRM, EX, W, SG, fl); }
#define DEF_TOINT_ALL(TOK, TY, W, SG) \
    DEF_TOINT(TOK, TY, W, SG, ties_to_even, MSF_IROUND_TIES_TO_EVEN, 0) \
    DEF_TOINT(TOK, TY, W, SG, ties_to_away, MSF_IROUND_TIES_TO_AWAY, 0) \
    DEF_TOINT(TOK, TY, W, SG, toward_zero, MSF_IROUND_TOWARD_ZERO, 0) \
    DEF_TOINT(TOK, TY, W, SG, toward_positive, MSF_IROUND_TOWARD_POSITIVE, 0) \
    DEF_TOINT(TOK, TY, W, SG, toward_negative, MSF_IROUND_TOWARD_NEGATIVE, 0) \
    DEF_TOINT(TOK, TY, W, SG, exact_ties_to_even, MSF_IROUND_TIES_TO_EVEN, 1) \
    DEF_TOINT(TOK, TY, W, SG, exact_ties_to_away, MSF_IROUND_TIES_TO_AWAY, 1) \
    DEF_TOINT(TOK, TY, W, SG, exact_toward_zero, MSF_IROUND_TOWARD_ZERO, 1) \
    DEF_TOINT(TOK, TY, W, SG, exact_toward_positive, MSF_IROUND_TOWARD_POSITIVE, 1) \
    DEF_TOINT(TOK, TY, W, SG, exact_toward_negative, MSF_IROUND_TOWARD_NEGATIVE, 1)
DEF_TOINT_ALL(i8, int8_t, 8, 1)
DEF_TOINT_ALL(u8, uint8_t, 8, 0)
DEF_TOINT_ALL(i16, int16_t, 16, 1)
DEF_TOINT_ALL(u16, uint16_t, 16, 0)
DEF_TOINT_ALL(i32, int32_t, 32, 1)
DEF_TOINT_ALL(u32, uint32_t, 32, 0)
DEF_TOINT_ALL(i64, int64_t, 64, 1)
DEF_TOINT_ALL(u64, uint64_t, 64, 0)

#define CMP_FN(SUF) CAT(msf64_compare_, SUF)
#define DEF_CMP(SUF, PRED, SIG) \
    int CMP_FN(SUF)(msf64_t a, msf64_t b, msf_flags_t *fl) \
    { return compare_core(MSF_FMT_F64, a, MSF_FMT_F64, b, PRED, SIG, fl); } \
    int CAT(CMP_FN(SUF), _f32)(msf64_t a, msf32_t b, msf_flags_t *fl) \
    { return compare_core(MSF_FMT_F64, a, MSF_FMT_F32, (uint64_t)b, \
                          PRED, SIG, fl); }
DEF_CMP(quiet_equal, PRED_EQ, 0)
DEF_CMP(quiet_not_equal, PRED_NE, 0)
DEF_CMP(signaling_equal, PRED_EQ, 1)
DEF_CMP(signaling_not_equal, PRED_NE, 1)
DEF_CMP(quiet_greater, PRED_GT, 0)
DEF_CMP(quiet_greater_equal, PRED_GE, 0)
DEF_CMP(quiet_less, PRED_LT, 0)
DEF_CMP(quiet_less_equal, PRED_LE, 0)
DEF_CMP(quiet_not_greater, PRED_NOTGT, 0)
DEF_CMP(quiet_not_less, PRED_NOTLT, 0)
DEF_CMP(quiet_less_unordered, PRED_LTUN, 0)
DEF_CMP(quiet_greater_unordered, PRED_GTUN, 0)
DEF_CMP(quiet_unordered, PRED_UNORD, 0)
DEF_CMP(quiet_ordered, PRED_ORD, 0)
DEF_CMP(signaling_greater, PRED_GT, 1)
DEF_CMP(signaling_greater_equal, PRED_GE, 1)
DEF_CMP(signaling_less, PRED_LT, 1)
DEF_CMP(signaling_less_equal, PRED_LE, 1)
DEF_CMP(signaling_not_greater, PRED_NOTGT, 1)
DEF_CMP(signaling_not_less, PRED_NOTLT, 1)
DEF_CMP(signaling_less_unordered, PRED_LTUN, 1)
DEF_CMP(signaling_greater_unordered, PRED_GTUN, 1)

#define DEF_CMP_F16(SUF, PRED, SIG) \
    int CAT(CMP_FN(SUF), _f16)(msf64_t a, msf16_t b, msf_flags_t *fl) \
    { return compare_core(MSF_FMT_F64, a, MSF_FMT_F16, (uint64_t)b, \
                          PRED, SIG, fl); }
DEF_CMP_F16(quiet_equal, PRED_EQ, 0)
DEF_CMP_F16(quiet_not_equal, PRED_NE, 0)
DEF_CMP_F16(signaling_equal, PRED_EQ, 1)
DEF_CMP_F16(signaling_not_equal, PRED_NE, 1)
DEF_CMP_F16(quiet_greater, PRED_GT, 0)
DEF_CMP_F16(quiet_greater_equal, PRED_GE, 0)
DEF_CMP_F16(quiet_less, PRED_LT, 0)
DEF_CMP_F16(quiet_less_equal, PRED_LE, 0)
DEF_CMP_F16(quiet_not_greater, PRED_NOTGT, 0)
DEF_CMP_F16(quiet_not_less, PRED_NOTLT, 0)
DEF_CMP_F16(quiet_less_unordered, PRED_LTUN, 0)
DEF_CMP_F16(quiet_greater_unordered, PRED_GTUN, 0)
DEF_CMP_F16(quiet_unordered, PRED_UNORD, 0)
DEF_CMP_F16(quiet_ordered, PRED_ORD, 0)
DEF_CMP_F16(signaling_greater, PRED_GT, 1)
DEF_CMP_F16(signaling_greater_equal, PRED_GE, 1)
DEF_CMP_F16(signaling_less, PRED_LT, 1)
DEF_CMP_F16(signaling_less_equal, PRED_LE, 1)
DEF_CMP_F16(signaling_not_greater, PRED_NOTGT, 1)
DEF_CMP_F16(signaling_not_less, PRED_NOTLT, 1)
DEF_CMP_F16(signaling_less_unordered, PRED_LTUN, 1)
DEF_CMP_F16(signaling_greater_unordered, PRED_GTUN, 1)

int msf64_total_order(msf64_t a, msf64_t b)
{
    return total_key((uint64_t)a) <= total_key((uint64_t)b);
}

int msf64_total_order_mag(msf64_t a, msf64_t b)
{
    return total_key((uint64_t)a & ~SGN64)
           <= total_key((uint64_t)b & ~SGN64);
}

