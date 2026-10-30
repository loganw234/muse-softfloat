/* msf16.c - binary16 translation unit (SF-0 Section 3.1).
 *
 * Wave 2 parcel-f16: every binary16-destination instantiation of
 * the homogeneous core, with sources spanning the full
 * {binary16, binary32, binary64} grid (design entry:
 * audit-bundle/ledger/parcel-f16.md). Shape per the brief: msf_decode to exact sig*2^exp,
 * NaN delivery via msf_nan_delivery, exact integer work over
 * msf_u128, then ONE rounding through msf_pack_f16 (the logB result
 * is the single exception, packed as binary64 because logBFormat
 * is binary64, SF-0 Section 2.2). No operation rounds twice. The
 * kernels mirror src/msf32.c at binary16 destination widths; the
 * one width-forced deviation is the remainder early-return
 * threshold (s >= 12 = p+1 at p = 11, in place of 25).
 */
#include "msf_internal.h"
#include "msf_decode.h"

#define MSF_PF 16
#include "msf_performat.inc"

#define FMT16 MSF_FMT_F16
#define FMT32 MSF_FMT_F32
#define FMT64 MSF_FMT_F64
#define INF16(sign) ((msf16_t)(((sign) ? MSF_F16_SIGN_MASK : 0u) | MSF_F16_INFINITY))
#define ZERO16(sign) ((msf16_t)((sign) ? MSF_F16_SIGN_MASK : 0u))

static int bitlen128(msf_u128_t a)
{
    return 128 - msf_u128_clz(a);
}

static int bit128(msf_u128_t a, unsigned n)
{
    return (int)((a.w[n >> 5] >> (n & 31u)) & 1u);
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

static msf_u128_t zero128(void)
{
    return msf_u128_from_u64(0u);
}

/* Normalize a nonzero sig so its top bit is bit 126 (exact).
 * Invariant (lead note at the Wave 1 design review): every sig
 * reaching this alignment has bit length at most 106 (decoded
 * source at most 53, exact product at most 106), so after
 * normalization it carries at least 21 trailing zeros; that is
 * what keeps the jam bit far below the binary16 rounding
 * position in add_mag. */
static void norm126(msf_u128_t sig, int32_t exp, msf_u128_t *osig, int32_t *oexp)
{
    int shift = 127 - bitlen128(sig);
    *osig = msf_u128_shl(sig, (unsigned)shift);
    *oexp = exp - shift;
}

/* Signed-magnitude addition of two exact finite magnitudes, packed
 * once into binary16. A zero sig means that operand is an exact
 * zero of the given sign. Clause 6.3 zero rules live here. */
static msf16_t add_mag(int sa, msf_u128_t siga, int32_t expa,
                       int sb, msf_u128_t sigb, int32_t expb,
                       int rm, msf_flags_t *flags)
{
    int az = msf_u128_is_zero(siga), bz = msf_u128_is_zero(sigb);
    msf_u128_t na, nb, dom, other, res;
    int32_t ea, eb, edom;
    int sdom, sother;

    if (az && bz) {
        int s = (sa == sb) ? sa : (rm == MSF_IROUND_TOWARD_NEGATIVE);
        return ZERO16(s);
    }
    if (az) {
        return msf_pack_f16(sb, expb, sigb, 0, rm, flags);
    }
    if (bz) {
        return msf_pack_f16(sa, expa, siga, 0, rm, flags);
    }
    norm126(siga, expa, &na, &ea);
    norm126(sigb, expb, &nb, &eb);
    if (ea >= eb) {
        dom = na; edom = ea; sdom = sa; sother = sb;
        other = msf_u128_shr_jam(nb, (unsigned)(ea - eb), 0);
    } else {
        dom = nb; edom = eb; sdom = sb; sother = sa;
        other = msf_u128_shr_jam(na, (unsigned)(eb - ea), 0);
    }
    if (sdom == sother) {
        res = msf_u128_add(dom, other, 0);
        return msf_pack_f16(sdom, edom, res, 0, rm, flags);
    }
    if (msf_u128_cmp(dom, other) == 0) {
        return ZERO16(rm == MSF_IROUND_TOWARD_NEGATIVE);
    }
    if (msf_u128_cmp(dom, other) > 0) {
        res = msf_u128_sub(dom, other, 0);
        return msf_pack_f16(sdom, edom, res, 0, rm, flags);
    }
    res = msf_u128_sub(other, dom, 0);
    return msf_pack_f16(sother, edom, res, 0, rm, flags);
}

static msf16_t add_impl(int afmt, uint64_t abits, int bfmt, uint64_t bbits,
                        int issub, int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(afmt, abits);
    msf_decoded_t b = msf_decode(bfmt, bbits);
    msf_decoded_t ops[2];
    int fmts[2];
    int effb = b.sign ^ (issub != 0);
    int inv = a.cls == MSF_VC_INFINITY && b.cls == MSF_VC_INFINITY
              && a.sign != effb;
    uint64_t out;
    ops[0] = a; ops[1] = b; fmts[0] = afmt; fmts[1] = bfmt;
    if (msf_nan_delivery(FMT16, ops, fmts, 2, inv, &out, flags)) {
        return (msf16_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        return INF16(a.sign);
    }
    if (b.cls == MSF_VC_INFINITY) {
        return INF16(effb);
    }
    return add_mag(a.sign, a.sig, a.exp, effb, b.sig, b.exp, rm, flags);
}

static msf16_t mul_impl(int afmt, uint64_t abits, int bfmt, uint64_t bbits,
                        int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(afmt, abits);
    msf_decoded_t b = msf_decode(bfmt, bbits);
    msf_decoded_t ops[2];
    int fmts[2];
    int sign = a.sign ^ b.sign;
    int inv = (a.cls == MSF_VC_ZERO && b.cls == MSF_VC_INFINITY)
              || (a.cls == MSF_VC_INFINITY && b.cls == MSF_VC_ZERO);
    uint64_t out;
    msf_u128_t prod;
    ops[0] = a; ops[1] = b; fmts[0] = afmt; fmts[1] = bfmt;
    if (msf_nan_delivery(FMT16, ops, fmts, 2, inv, &out, flags)) {
        return (msf16_t)out;
    }
    if (a.cls == MSF_VC_INFINITY || b.cls == MSF_VC_INFINITY) {
        return INF16(sign);
    }
    if (a.cls == MSF_VC_ZERO || b.cls == MSF_VC_ZERO) {
        return ZERO16(sign);
    }
    prod = msf_u128_mul_u64_u64(msf_u128_to_u64_trunc(a.sig),
                                msf_u128_to_u64_trunc(b.sig));
    return msf_pack_f16(sign, a.exp + b.exp, prod, 0, rm, flags);
}

static msf16_t div_impl(int afmt, uint64_t abits, int bfmt, uint64_t bbits,
                        int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(afmt, abits);
    msf_decoded_t b = msf_decode(bfmt, bbits);
    msf_decoded_t ops[2];
    int fmts[2];
    int sign = a.sign ^ b.sign;
    int inv = (a.cls == MSF_VC_ZERO && b.cls == MSF_VC_ZERO)
              || (a.cls == MSF_VC_INFINITY && b.cls == MSF_VC_INFINITY);
    uint64_t out;
    int la, lb, i;
    uint64_t topa, topb;
    msf_u128_t num, den, rem, quo;
    ops[0] = a; ops[1] = b; fmts[0] = afmt; fmts[1] = bfmt;
    if (msf_nan_delivery(FMT16, ops, fmts, 2, inv, &out, flags)) {
        return (msf16_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        return INF16(sign);
    }
    if (b.cls == MSF_VC_INFINITY) {
        return ZERO16(sign);
    }
    if (b.cls == MSF_VC_ZERO) {
        *flags |= MSF_FLAG_DIVISION_BY_ZERO;
        return INF16(sign);
    }
    if (a.cls == MSF_VC_ZERO) {
        return ZERO16(sign);
    }
    la = bitlen128(a.sig);
    lb = bitlen128(b.sig);
    topa = msf_u128_to_u64_trunc(a.sig) << (64 - la);
    topb = msf_u128_to_u64_trunc(b.sig) << (64 - lb);
    num = msf_u128_shl(msf_u128_from_u64(topa), 63u);
    den = msf_u128_from_u64(topb);
    rem = zero128();
    quo = zero128();
    for (i = 127; i >= 0; i--) {
        rem = msf_u128_shl(rem, 1u);
        rem.w[0] |= (uint32_t)bit128(num, (unsigned)i);
        if (msf_u128_cmp(rem, den) >= 0) {
            rem = msf_u128_sub(rem, den, 0);
            quo.w[((unsigned)i) >> 5] |= 1u << (((unsigned)i) & 31u);
        }
    }
    return msf_pack_f16(sign, a.exp - b.exp + (la - lb) - 63, quo,
                        !msf_u128_is_zero(rem), rm, flags);
}

static msf16_t sqrt_impl(int afmt, uint64_t abits, int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(afmt, abits);
    msf_decoded_t ops[1];
    int fmts[1];
    int inv = a.sign && (a.cls == MSF_VC_INFINITY || a.cls == MSF_VC_NORMAL
                         || a.cls == MSF_VC_SUBNORMAL);
    uint64_t out;
    msf_u128_t sig, scaled;
    int32_t exp;
    int len, shift, bit;
    uint64_t q = 0u;
    ops[0] = a; fmts[0] = afmt;
    if (msf_nan_delivery(FMT16, ops, fmts, 1, inv, &out, flags)) {
        return (msf16_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        return INF16(0);
    }
    if (a.cls == MSF_VC_ZERO) {
        return ZERO16(a.sign);
    }
    sig = a.sig;
    exp = a.exp;
    if ((exp % 2) != 0) {
        sig = msf_u128_shl(sig, 1u);
        exp -= 1;
    }
    len = bitlen128(sig);
    shift = 126 - len;
    if ((shift % 2) != 0) {
        shift -= 1;
    }
    scaled = msf_u128_shl(sig, (unsigned)shift);
    for (bit = 63; bit >= 0; bit--) {
        uint64_t cand = q | (1ULL << bit);
        if (msf_u128_cmp(msf_u128_mul_u64_u64(cand, cand), scaled) <= 0) {
            q = cand;
        }
    }
    return msf_pack_f16(0, exp / 2 - shift / 2, msf_u128_from_u64(q),
                        msf_u128_cmp(msf_u128_mul_u64_u64(q, q), scaled) != 0,
                        rm, flags);
}

static msf16_t fma_impl(int afmt, uint64_t abits, int bfmt, uint64_t bbits,
                        int cfmt, uint64_t cbits, int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(afmt, abits);
    msf_decoded_t b = msf_decode(bfmt, bbits);
    msf_decoded_t c = msf_decode(cfmt, cbits);
    msf_decoded_t ops[3];
    int fmts[3];
    int psign = a.sign ^ b.sign;
    int prod_zero_inf = (a.cls == MSF_VC_ZERO && b.cls == MSF_VC_INFINITY)
                        || (a.cls == MSF_VC_INFINITY && b.cls == MSF_VC_ZERO);
    int prod_inf = ((a.cls == MSF_VC_INFINITY && !msf_is_nan_cls(b.cls)
                     && b.cls != MSF_VC_ZERO)
                    || (b.cls == MSF_VC_INFINITY && !msf_is_nan_cls(a.cls)
                        && a.cls != MSF_VC_ZERO));
    int inv = prod_zero_inf
              || (prod_inf && c.cls == MSF_VC_INFINITY && psign != c.sign);
    uint64_t out;
    msf_u128_t psig;
    int32_t pexp = 0;
    ops[0] = a; ops[1] = b; ops[2] = c;
    fmts[0] = afmt; fmts[1] = bfmt; fmts[2] = cfmt;
    if (prod_zero_inf && c.cls == MSF_VC_QUIET_NAN) {
        *flags |= MSF_FLAG_INVALID;
    }
    if (msf_nan_delivery(FMT16, ops, fmts, 3, inv, &out, flags)) {
        return (msf16_t)out;
    }
    if (prod_inf) {
        return INF16(psign);
    }
    if (c.cls == MSF_VC_INFINITY) {
        return INF16(c.sign);
    }
    if (a.cls == MSF_VC_ZERO || b.cls == MSF_VC_ZERO) {
        psig = zero128();
    } else {
        psig = msf_u128_mul_u64_u64(msf_u128_to_u64_trunc(a.sig),
                                    msf_u128_to_u64_trunc(b.sig));
        pexp = a.exp + b.exp;
    }
    return add_mag(psign, psig, pexp, c.sign, c.sig, c.exp, rm, flags);
}

/* Round an exact magnitude sig*2^exp to an integer magnitude.
 * Mode is the internal rounding enum; sign decides directed modes.
 * Reports whether a nonzero fraction was discarded. Callers keep
 * shifts inside u128 (binary16 sources, or squared/clamped cases). */
static msf_u128_t round_mag_to_int(msf_u128_t sig, int32_t exp, int sign,
                                   int mode, int *frac_nonzero)
{
    msf_u128_t q;
    int32_t shift;
    int frac, half_bit, below, inc = 0;
    *frac_nonzero = 0;
    if (msf_u128_is_zero(sig)) {
        return sig;
    }
    if (exp >= 0) {
        return msf_u128_shl(sig, (unsigned)exp);
    }
    shift = -exp;
    q = shift >= 128 ? zero128() : msf_u128_shr(sig, (unsigned)shift);
    frac = any_below128(sig, shift);
    *frac_nonzero = frac;
    if (!frac) {
        return q;
    }
    half_bit = (shift - 1 >= 128) ? 0 : bit128(sig, (unsigned)(shift - 1));
    below = any_below128(sig, shift - 1);
    switch (mode) {
    case MSF_IROUND_TIES_TO_EVEN:
        inc = half_bit && (below || (q.w[0] & 1u));
        break;
    case MSF_IROUND_TIES_TO_AWAY:
        inc = half_bit;
        break;
    case MSF_IROUND_TOWARD_POSITIVE:
        inc = !sign;
        break;
    case MSF_IROUND_TOWARD_NEGATIVE:
        inc = sign != 0;
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

static msf16_t rint_impl(msf16_t abits, int mode, int exact_form,
                         msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(FMT16, abits);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out;
    int frac = 0;
    msf_u128_t q;
    msf_flags_t scratch = 0u;
    msf16_t res;
    ops[0] = a; fmts[0] = FMT16;
    if (msf_nan_delivery(FMT16, ops, fmts, 1, 0, &out, flags)) {
        return (msf16_t)out;
    }
    if (a.cls == MSF_VC_INFINITY || a.cls == MSF_VC_ZERO || a.exp >= 0) {
        return abits;
    }
    q = round_mag_to_int(a.sig, a.exp, a.sign, mode, &frac);
    res = msf_pack_f16(a.sign, 0, q, 0, MSF_IROUND_TIES_TO_EVEN, &scratch);
    if (exact_form && frac) {
        *flags |= MSF_FLAG_INEXACT;
    }
    return res;
}

static msf16_t next_impl(msf16_t abits, int up, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(FMT16, abits);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out;
    ops[0] = a; fmts[0] = FMT16;
    if (msf_nan_delivery(FMT16, ops, fmts, 1, 0, &out, flags)) {
        return (msf16_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        if (up) {
            return a.sign
                       ? (msf16_t)(MSF_F16_SIGN_MASK | (MSF_F16_INFINITY - 1u))
                       : abits;
        }
        return a.sign ? abits : (msf16_t)(MSF_F16_INFINITY - 1u);
    }
    if (a.cls == MSF_VC_ZERO) {
        return up ? (msf16_t)1u : (msf16_t)(MSF_F16_SIGN_MASK | 1u);
    }
    if (up) {
        return a.sign ? (msf16_t)(abits - 1u) : (msf16_t)(abits + 1u);
    }
    return a.sign ? (msf16_t)(abits + 1u) : (msf16_t)(abits - 1u);
}

msf16_t msf16_remainder(msf16_t abits, msf16_t bbits, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(FMT16, abits);
    msf_decoded_t b = msf_decode(FMT16, bbits);
    msf_decoded_t ops[2];
    int fmts[2];
    int inv = a.cls == MSF_VC_INFINITY || b.cls == MSF_VC_ZERO;
    uint64_t out;
    uint64_t A, B;
    int32_t d, er;
    msf_u128_t rint, yint, rmag;
    int qparity = 0, rsign, i;
    ops[0] = a; ops[1] = b; fmts[0] = FMT16; fmts[1] = FMT16;
    if (msf_nan_delivery(FMT16, ops, fmts, 2, inv, &out, flags)) {
        return (msf16_t)out;
    }
    if (b.cls == MSF_VC_INFINITY || a.cls == MSF_VC_ZERO) {
        return abits;
    }
    A = msf_u128_to_u64_trunc(a.sig);
    B = msf_u128_to_u64_trunc(b.sig);
    d = a.exp - b.exp;
    if (d >= 0) {
        uint64_t rem = 0u;
        er = b.exp;
        yint = msf_u128_from_u64(B);
        for (i = 63; i >= 0; i--) {
            rem = (rem << 1) | ((A >> i) & 1u);
            if (rem >= B) { rem -= B; qparity = 1; } else { qparity = 0; }
        }
        for (i = 0; i < d; i++) {
            rem <<= 1;
            if (rem >= B) { rem -= B; qparity = 1; } else { qparity = 0; }
        }
        rint = msf_u128_from_u64(rem);
    } else {
        int32_t s = -d;
        msf_u128_t rem, den;
        /* s >= 12 = p+1: B*2^s >= 4096 > 2*2047 >= 2A, so 2|X| is
         * certainly below |Y| and the quotient integer is 0. */
        if (s >= 12) {
            return abits;
        }
        er = a.exp;
        den = msf_u128_shl(msf_u128_from_u64(B), (unsigned)s);
        yint = den;
        rem = zero128();
        for (i = 63; i >= 0; i--) {
            rem = msf_u128_shl(rem, 1u);
            rem.w[0] |= (uint32_t)((A >> i) & 1u);
            if (msf_u128_cmp(rem, den) >= 0) {
                rem = msf_u128_sub(rem, den, 0);
                qparity = 1;
            } else {
                qparity = 0;
            }
        }
        rint = rem;
    }
    {
        int cmp = msf_u128_cmp(msf_u128_shl(rint, 1u), yint);
        if (cmp < 0 || (cmp == 0 && qparity == 0)) {
            rmag = rint;
            rsign = a.sign;
        } else {
            rmag = msf_u128_sub(yint, rint, 0);
            rsign = a.sign ^ 1;
        }
    }
    if (msf_u128_is_zero(rmag)) {
        return ZERO16(a.sign);
    }
    return msf_pack_f16(rsign, er, rmag, 0, MSF_IROUND_TIES_TO_EVEN, flags);
}

msf16_t msf16_scale_b(msf16_t abits, msf64_t nbits, msf_rounding_t rm,
                      msf_flags_t *flags)
{
    msf_decoded_t x = msf_decode(FMT16, abits);
    msf_decoded_t n = msf_decode(FMT64, nbits);
    msf_decoded_t ops[2];
    int fmts[2];
    uint64_t out;
    int32_t nint;
    ops[0] = x; ops[1] = n; fmts[0] = FMT16; fmts[1] = FMT64;
    if (msf_nan_delivery(FMT16, ops, fmts, 2, 0, &out, flags)) {
        return (msf16_t)out;
    }
    if (x.cls == MSF_VC_INFINITY || x.cls == MSF_VC_ZERO) {
        return abits;
    }
    if (n.cls == MSF_VC_ZERO) {
        return abits;
    }
    if (n.cls == MSF_VC_INFINITY) {
        nint = n.sign ? -10000 : 10000;
    } else {
        int32_t top = (bitlen128(n.sig) - 1) + n.exp;
        int frac = 0;
        uint64_t mag;
        if (top >= 14) {
            nint = n.sign ? -10000 : 10000;
            return msf_pack_f16(x.sign, x.exp + nint, x.sig, 0, (int)rm, flags);
        }
        if (top < 0) {
            return abits;
        }
        mag = msf_u128_to_u64_trunc(
            round_mag_to_int(n.sig, n.exp, n.sign,
                             MSF_IROUND_TOWARD_ZERO, &frac));
        nint = n.sign ? -(int32_t)mag : (int32_t)mag;
    }
    return msf_pack_f16(x.sign, x.exp + nint, x.sig, 0, (int)rm, flags);
}

msf64_t msf16_log_b(msf16_t abits, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(FMT16, abits);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out;
    int32_t e;
    ops[0] = a; fmts[0] = FMT16;
    if (msf_nan_delivery(FMT64, ops, fmts, 1, 0, &out, flags)) {
        return (msf64_t)out;
    }
    if (a.cls == MSF_VC_ZERO) {
        *flags |= MSF_FLAG_DIVISION_BY_ZERO;
        return (msf64_t)(MSF_F64_SIGN_MASK | MSF_F64_INFINITY);
    }
    if (a.cls == MSF_VC_INFINITY) {
        return (msf64_t)MSF_F64_INFINITY;
    }
    e = (bitlen128(a.sig) - 1) + a.exp;
    return msf_pack_f64(e < 0, 0,
                        msf_u128_from_u64((uint64_t)(e < 0 ? -e : e)), 0,
                        MSF_IROUND_TIES_TO_EVEN, flags);
}

static msf16_t conv_impl(int sfmt, uint64_t abits, int rm, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(sfmt, abits);
    msf_decoded_t ops[1];
    int fmts[1];
    uint64_t out;
    ops[0] = a; fmts[0] = sfmt;
    if (msf_nan_delivery(FMT16, ops, fmts, 1, 0, &out, flags)) {
        return (msf16_t)out;
    }
    if (a.cls == MSF_VC_INFINITY) {
        return INF16(a.sign);
    }
    if (a.cls == MSF_VC_ZERO) {
        return ZERO16(a.sign);
    }
    return msf_pack_f16(a.sign, a.exp, a.sig, 0, rm, flags);
}

static msf16_t from_int_impl(int sign, uint64_t mag, int rm,
                             msf_flags_t *flags)
{
    return msf_pack_f16(sign, 0, msf_u128_from_u64(mag), 0, rm, flags);
}

/* Convert to an integer destination. Returns the raw low bits of
 * the delivered value; wrappers cast to the C integer type.
 * Project invalid rule (public header): saturate, NaN to zero.
 * Inexact appears only in Exact variants, only in range. */
static uint64_t to_int_impl(msf16_t abits, int is_signed, int width,
                            int mode, int exact_form, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(FMT16, abits);
    uint64_t max_pat, min_pat;
    msf_u128_t q, limit;
    int frac = 0;

    if (width == 64) {
        max_pat = is_signed ? 0x7fffffffffffffffULL : 0xffffffffffffffffULL;
        min_pat = is_signed ? 0x8000000000000000ULL : 0u;
    } else if (is_signed) {
        max_pat = (1ULL << (width - 1)) - 1u;
        min_pat = 1ULL << (width - 1);
    } else {
        max_pat = (1ULL << width) - 1u;
        min_pat = 0u;
    }
    if (msf_is_nan_cls(a.cls)) {
        *flags |= MSF_FLAG_INVALID;
        return 0u;
    }
    if (a.cls == MSF_VC_INFINITY) {
        *flags |= MSF_FLAG_INVALID;
        return a.sign ? min_pat : max_pat;
    }
    q = round_mag_to_int(a.sig, a.exp, a.sign, mode, &frac);
    if (msf_u128_is_zero(q)) {
        if (exact_form && frac) {
            *flags |= MSF_FLAG_INEXACT;
        }
        return 0u;
    }
    if (a.sign) {
        limit = is_signed ? msf_u128_from_u64(min_pat) : zero128();
        if (!is_signed || msf_u128_cmp(q, limit) > 0) {
            *flags |= MSF_FLAG_INVALID;
            return min_pat;
        }
        if (exact_form && frac) {
            *flags |= MSF_FLAG_INEXACT;
        }
        return 0ULL - msf_u128_to_u64_trunc(q);
    }
    limit = msf_u128_from_u64(max_pat);
    if (msf_u128_cmp(q, limit) > 0) {
        *flags |= MSF_FLAG_INVALID;
        return max_pat;
    }
    if (exact_form && frac) {
        *flags |= MSF_FLAG_INEXACT;
    }
    return msf_u128_to_u64_trunc(q);
}

enum { REL_LT = 1, REL_EQ = 2, REL_GT = 4, REL_UN = 8 };

static int cmp_impl(int afmt, uint64_t abits, int bfmt, uint64_t bbits,
                    unsigned mask, int signaling, msf_flags_t *flags)
{
    msf_decoded_t a = msf_decode(afmt, abits);
    msf_decoded_t b = msf_decode(bfmt, bbits);
    unsigned rel;
    if (msf_is_nan_cls(a.cls) || msf_is_nan_cls(b.cls)) {
        rel = REL_UN;
        if (a.cls == MSF_VC_SIGNALING_NAN || b.cls == MSF_VC_SIGNALING_NAN
            || signaling) {
            *flags |= MSF_FLAG_INVALID;
        }
    } else if (a.cls == MSF_VC_INFINITY || b.cls == MSF_VC_INFINITY) {
        if (a.cls == MSF_VC_INFINITY && b.cls == MSF_VC_INFINITY) {
            rel = a.sign == b.sign ? REL_EQ : (a.sign ? REL_LT : REL_GT);
        } else if (a.cls == MSF_VC_INFINITY) {
            rel = a.sign ? REL_LT : REL_GT;
        } else {
            rel = b.sign ? REL_GT : REL_LT;
        }
    } else {
        int c = msf_cmp_finite(&a, &b);
        rel = c < 0 ? REL_LT : (c > 0 ? REL_GT : REL_EQ);
    }
    return (mask & rel) != 0u;
}

static uint16_t total_order_key(msf16_t a)
{
    return (uint16_t)(((uint64_t)a & MSF_F16_SIGN_MASK) != 0u
                          ? ~a
                          : (a | (msf16_t)MSF_F16_SIGN_MASK));
}

int msf16_total_order(msf16_t a, msf16_t b)
{
    return total_order_key(a) <= total_order_key(b);
}

int msf16_total_order_mag(msf16_t a, msf16_t b)
{
    return total_order_key((msf16_t)(a & ~(msf16_t)MSF_F16_SIGN_MASK))
           <= total_order_key((msf16_t)(b & ~(msf16_t)MSF_F16_SIGN_MASK));
}

/* ---- public wrappers (one per instantiation) ---- */

#define DEF_ADD(NAME, AT, AF, BT, BF) \
    msf16_t NAME(AT a, BT b, msf_rounding_t rm, msf_flags_t *flags) \
    { return add_impl(AF, (uint64_t)a, BF, (uint64_t)b, 0, (int)rm, flags); }
#define DEF_SUB(NAME, AT, AF, BT, BF) \
    msf16_t NAME(AT a, BT b, msf_rounding_t rm, msf_flags_t *flags) \
    { return add_impl(AF, (uint64_t)a, BF, (uint64_t)b, 1, (int)rm, flags); }
#define DEF_MUL(NAME, AT, AF, BT, BF) \
    msf16_t NAME(AT a, BT b, msf_rounding_t rm, msf_flags_t *flags) \
    { return mul_impl(AF, (uint64_t)a, BF, (uint64_t)b, (int)rm, flags); }
#define DEF_DIV(NAME, AT, AF, BT, BF) \
    msf16_t NAME(AT a, BT b, msf_rounding_t rm, msf_flags_t *flags) \
    { return div_impl(AF, (uint64_t)a, BF, (uint64_t)b, (int)rm, flags); }
#define DEF_BIN_ALL(OP, FN) \
    FN(msf16_##OP, msf16_t, FMT16, msf16_t, FMT16) \
    FN(msf16_##OP##_f16_f32, msf16_t, FMT16, msf32_t, FMT32) \
    FN(msf16_##OP##_f16_f64, msf16_t, FMT16, msf64_t, FMT64) \
    FN(msf16_##OP##_f32_f16, msf32_t, FMT32, msf16_t, FMT16) \
    FN(msf16_##OP##_f32_f32, msf32_t, FMT32, msf32_t, FMT32) \
    FN(msf16_##OP##_f32_f64, msf32_t, FMT32, msf64_t, FMT64) \
    FN(msf16_##OP##_f64_f16, msf64_t, FMT64, msf16_t, FMT16) \
    FN(msf16_##OP##_f64_f32, msf64_t, FMT64, msf32_t, FMT32) \
    FN(msf16_##OP##_f64_f64, msf64_t, FMT64, msf64_t, FMT64)
DEF_BIN_ALL(add, DEF_ADD)
DEF_BIN_ALL(sub, DEF_SUB)
DEF_BIN_ALL(mul, DEF_MUL)
DEF_BIN_ALL(div, DEF_DIV)
#undef DEF_BIN_ALL
#undef DEF_ADD
#undef DEF_SUB
#undef DEF_MUL
#undef DEF_DIV

msf16_t msf16_sqrt(msf16_t a, msf_rounding_t rm, msf_flags_t *flags)
{
    return sqrt_impl(FMT16, a, (int)rm, flags);
}
msf16_t msf16_sqrt_f32(msf32_t a, msf_rounding_t rm, msf_flags_t *flags)
{
    return sqrt_impl(FMT32, a, (int)rm, flags);
}
msf16_t msf16_sqrt_f64(msf64_t a, msf_rounding_t rm, msf_flags_t *flags)
{
    return sqrt_impl(FMT64, a, (int)rm, flags);
}

#define DEF_FMA(NAME, AT, AF, BT, BF, CT, CF) \
    msf16_t NAME(AT a, BT b, CT c, msf_rounding_t rm, msf_flags_t *flags) \
    { return fma_impl(AF, (uint64_t)a, BF, (uint64_t)b, CF, (uint64_t)c, \
                      (int)rm, flags); }
DEF_FMA(msf16_fma, msf16_t, FMT16, msf16_t, FMT16, msf16_t, FMT16)
DEF_FMA(msf16_fma_f16_f16_f32, msf16_t, FMT16, msf16_t, FMT16, msf32_t, FMT32)
DEF_FMA(msf16_fma_f16_f16_f64, msf16_t, FMT16, msf16_t, FMT16, msf64_t, FMT64)
DEF_FMA(msf16_fma_f16_f32_f16, msf16_t, FMT16, msf32_t, FMT32, msf16_t, FMT16)
DEF_FMA(msf16_fma_f16_f32_f32, msf16_t, FMT16, msf32_t, FMT32, msf32_t, FMT32)
DEF_FMA(msf16_fma_f16_f32_f64, msf16_t, FMT16, msf32_t, FMT32, msf64_t, FMT64)
DEF_FMA(msf16_fma_f16_f64_f16, msf16_t, FMT16, msf64_t, FMT64, msf16_t, FMT16)
DEF_FMA(msf16_fma_f16_f64_f32, msf16_t, FMT16, msf64_t, FMT64, msf32_t, FMT32)
DEF_FMA(msf16_fma_f16_f64_f64, msf16_t, FMT16, msf64_t, FMT64, msf64_t, FMT64)
DEF_FMA(msf16_fma_f32_f16_f16, msf32_t, FMT32, msf16_t, FMT16, msf16_t, FMT16)
DEF_FMA(msf16_fma_f32_f16_f32, msf32_t, FMT32, msf16_t, FMT16, msf32_t, FMT32)
DEF_FMA(msf16_fma_f32_f16_f64, msf32_t, FMT32, msf16_t, FMT16, msf64_t, FMT64)
DEF_FMA(msf16_fma_f32_f32_f16, msf32_t, FMT32, msf32_t, FMT32, msf16_t, FMT16)
DEF_FMA(msf16_fma_f32_f32_f32, msf32_t, FMT32, msf32_t, FMT32, msf32_t, FMT32)
DEF_FMA(msf16_fma_f32_f32_f64, msf32_t, FMT32, msf32_t, FMT32, msf64_t, FMT64)
DEF_FMA(msf16_fma_f32_f64_f16, msf32_t, FMT32, msf64_t, FMT64, msf16_t, FMT16)
DEF_FMA(msf16_fma_f32_f64_f32, msf32_t, FMT32, msf64_t, FMT64, msf32_t, FMT32)
DEF_FMA(msf16_fma_f32_f64_f64, msf32_t, FMT32, msf64_t, FMT64, msf64_t, FMT64)
DEF_FMA(msf16_fma_f64_f16_f16, msf64_t, FMT64, msf16_t, FMT16, msf16_t, FMT16)
DEF_FMA(msf16_fma_f64_f16_f32, msf64_t, FMT64, msf16_t, FMT16, msf32_t, FMT32)
DEF_FMA(msf16_fma_f64_f16_f64, msf64_t, FMT64, msf16_t, FMT16, msf64_t, FMT64)
DEF_FMA(msf16_fma_f64_f32_f16, msf64_t, FMT64, msf32_t, FMT32, msf16_t, FMT16)
DEF_FMA(msf16_fma_f64_f32_f32, msf64_t, FMT64, msf32_t, FMT32, msf32_t, FMT32)
DEF_FMA(msf16_fma_f64_f32_f64, msf64_t, FMT64, msf32_t, FMT32, msf64_t, FMT64)
DEF_FMA(msf16_fma_f64_f64_f16, msf64_t, FMT64, msf64_t, FMT64, msf16_t, FMT16)
DEF_FMA(msf16_fma_f64_f64_f32, msf64_t, FMT64, msf64_t, FMT64, msf32_t, FMT32)
DEF_FMA(msf16_fma_f64_f64_f64, msf64_t, FMT64, msf64_t, FMT64, msf64_t, FMT64)
#undef DEF_FMA

msf16_t msf16_from_f16(msf16_t a, msf_rounding_t rm, msf_flags_t *flags)
{
    return conv_impl(FMT16, a, (int)rm, flags);
}
msf16_t msf16_from_f32(msf32_t a, msf_rounding_t rm, msf_flags_t *flags)
{
    return conv_impl(FMT32, a, (int)rm, flags);
}
msf16_t msf16_from_f64(msf64_t a, msf_rounding_t rm, msf_flags_t *flags)
{
    return conv_impl(FMT64, a, (int)rm, flags);
}

#define DEF_RINT(NAME, MODE) \
    msf16_t NAME(msf16_t a, msf_flags_t *flags) \
    { return rint_impl(a, MODE, 0, flags); }
DEF_RINT(msf16_round_to_integral_ties_to_even, MSF_IROUND_TIES_TO_EVEN)
DEF_RINT(msf16_round_to_integral_ties_to_away, MSF_IROUND_TIES_TO_AWAY)
DEF_RINT(msf16_round_to_integral_toward_zero, MSF_IROUND_TOWARD_ZERO)
DEF_RINT(msf16_round_to_integral_toward_positive, MSF_IROUND_TOWARD_POSITIVE)
DEF_RINT(msf16_round_to_integral_toward_negative, MSF_IROUND_TOWARD_NEGATIVE)
#undef DEF_RINT

msf16_t msf16_round_to_integral_exact(msf16_t a, msf_rounding_t rm,
                                      msf_flags_t *flags)
{
    return rint_impl(a, (int)rm, 1, flags);
}

msf16_t msf16_next_up(msf16_t a, msf_flags_t *flags)
{
    return next_impl(a, 1, flags);
}
msf16_t msf16_next_down(msf16_t a, msf_flags_t *flags)
{
    return next_impl(a, 0, flags);
}

#define DEF_FROM_SINT(NAME, TYPE) \
    msf16_t NAME(TYPE a, msf_rounding_t rm, msf_flags_t *flags) \
    { return from_int_impl(a < 0, a < 0 ? 0ULL - (uint64_t)(int64_t)a \
                                        : (uint64_t)a, (int)rm, flags); }
#define DEF_FROM_UINT(NAME, TYPE) \
    msf16_t NAME(TYPE a, msf_rounding_t rm, msf_flags_t *flags) \
    { return from_int_impl(0, (uint64_t)a, (int)rm, flags); }
DEF_FROM_SINT(msf16_from_i8, int8_t)
DEF_FROM_UINT(msf16_from_u8, uint8_t)
DEF_FROM_SINT(msf16_from_i16, int16_t)
DEF_FROM_UINT(msf16_from_u16, uint16_t)
DEF_FROM_SINT(msf16_from_i32, int32_t)
DEF_FROM_UINT(msf16_from_u32, uint32_t)
DEF_FROM_SINT(msf16_from_i64, int64_t)
DEF_FROM_UINT(msf16_from_u64, uint64_t)
#undef DEF_FROM_SINT
#undef DEF_FROM_UINT

#define DEF_TO_INT_ONE(INTTOK, TYPE, ISS, W, SUFFIX, MODE, EXACT) \
    TYPE msf16_to_##INTTOK##_##SUFFIX(msf16_t a, msf_flags_t *flags) \
    { return (TYPE)to_int_impl(a, ISS, W, MODE, EXACT, flags); }
#define DEF_TO_INT_ALL(SUFFIX, MODE, EXACT) \
    DEF_TO_INT_ONE(i8, int8_t, 1, 8, SUFFIX, MODE, EXACT) \
    DEF_TO_INT_ONE(u8, uint8_t, 0, 8, SUFFIX, MODE, EXACT) \
    DEF_TO_INT_ONE(i16, int16_t, 1, 16, SUFFIX, MODE, EXACT) \
    DEF_TO_INT_ONE(u16, uint16_t, 0, 16, SUFFIX, MODE, EXACT) \
    DEF_TO_INT_ONE(i32, int32_t, 1, 32, SUFFIX, MODE, EXACT) \
    DEF_TO_INT_ONE(u32, uint32_t, 0, 32, SUFFIX, MODE, EXACT) \
    DEF_TO_INT_ONE(i64, int64_t, 1, 64, SUFFIX, MODE, EXACT) \
    DEF_TO_INT_ONE(u64, uint64_t, 0, 64, SUFFIX, MODE, EXACT)
DEF_TO_INT_ALL(ties_to_even, MSF_IROUND_TIES_TO_EVEN, 0)
DEF_TO_INT_ALL(ties_to_away, MSF_IROUND_TIES_TO_AWAY, 0)
DEF_TO_INT_ALL(toward_zero, MSF_IROUND_TOWARD_ZERO, 0)
DEF_TO_INT_ALL(toward_positive, MSF_IROUND_TOWARD_POSITIVE, 0)
DEF_TO_INT_ALL(toward_negative, MSF_IROUND_TOWARD_NEGATIVE, 0)
DEF_TO_INT_ALL(exact_ties_to_even, MSF_IROUND_TIES_TO_EVEN, 1)
DEF_TO_INT_ALL(exact_ties_to_away, MSF_IROUND_TIES_TO_AWAY, 1)
DEF_TO_INT_ALL(exact_toward_zero, MSF_IROUND_TOWARD_ZERO, 1)
DEF_TO_INT_ALL(exact_toward_positive, MSF_IROUND_TOWARD_POSITIVE, 1)
DEF_TO_INT_ALL(exact_toward_negative, MSF_IROUND_TOWARD_NEGATIVE, 1)
#undef DEF_TO_INT_ALL
#undef DEF_TO_INT_ONE

#define DEF_CMP_TRIPLE(PRED, MASK, SIG) \
    int msf16_compare_##PRED(msf16_t a, msf16_t b, msf_flags_t *flags) \
    { return cmp_impl(FMT16, a, FMT16, b, MASK, SIG, flags); } \
    int msf16_compare_##PRED##_f32(msf16_t a, msf32_t b, msf_flags_t *flags) \
    { return cmp_impl(FMT16, a, FMT32, b, MASK, SIG, flags); } \
    int msf16_compare_##PRED##_f64(msf16_t a, msf64_t b, msf_flags_t *flags) \
    { return cmp_impl(FMT16, a, FMT64, b, MASK, SIG, flags); }
DEF_CMP_TRIPLE(quiet_equal, REL_EQ, 0)
DEF_CMP_TRIPLE(quiet_not_equal, REL_LT | REL_GT | REL_UN, 0)
DEF_CMP_TRIPLE(signaling_equal, REL_EQ, 1)
DEF_CMP_TRIPLE(signaling_not_equal, REL_LT | REL_GT | REL_UN, 1)
DEF_CMP_TRIPLE(quiet_greater, REL_GT, 0)
DEF_CMP_TRIPLE(quiet_greater_equal, REL_GT | REL_EQ, 0)
DEF_CMP_TRIPLE(quiet_less, REL_LT, 0)
DEF_CMP_TRIPLE(quiet_less_equal, REL_LT | REL_EQ, 0)
DEF_CMP_TRIPLE(quiet_not_greater, REL_LT | REL_EQ | REL_UN, 0)
DEF_CMP_TRIPLE(quiet_not_less, REL_GT | REL_EQ | REL_UN, 0)
DEF_CMP_TRIPLE(quiet_less_unordered, REL_LT | REL_UN, 0)
DEF_CMP_TRIPLE(quiet_greater_unordered, REL_GT | REL_UN, 0)
DEF_CMP_TRIPLE(quiet_unordered, REL_UN, 0)
DEF_CMP_TRIPLE(quiet_ordered, REL_LT | REL_EQ | REL_GT, 0)
DEF_CMP_TRIPLE(signaling_greater, REL_GT, 1)
DEF_CMP_TRIPLE(signaling_greater_equal, REL_GT | REL_EQ, 1)
DEF_CMP_TRIPLE(signaling_less, REL_LT, 1)
DEF_CMP_TRIPLE(signaling_less_equal, REL_LT | REL_EQ, 1)
DEF_CMP_TRIPLE(signaling_not_greater, REL_LT | REL_EQ | REL_UN, 1)
DEF_CMP_TRIPLE(signaling_not_less, REL_GT | REL_EQ | REL_UN, 1)
DEF_CMP_TRIPLE(signaling_less_unordered, REL_LT | REL_UN, 1)
DEF_CMP_TRIPLE(signaling_greater_unordered, REL_GT | REL_UN, 1)
#undef DEF_CMP_TRIPLE
