/* msf_decode.h - shared decode, NaN delivery, finite comparison.
 *
 * Lead-owned helpers both format parcels build on, so operand
 * classification and the SF-0 Section 2.5 NaN matrix exist exactly
 * once. Static inline; no state.
 *
 * Decoded finite values are (sign, sig, exp) with the exact value
 * (-1)^sign * sig * 2^exp. Normals carry the hidden bit in sig;
 * subnormals carry the raw trailing field (not normalized).
 *
 * NaN delivery reading of the SF-0 2.5 matrix (project ruling where
 * the standard leaves the choice open): the matrix applies as an
 * if/else chain - (b) any signaling NaN input signals invalid and
 * the FIRST signaling operand, quieted, is delivered; else (c) the
 * first quiet NaN operand is delivered; else (a) an invalid with no
 * NaN input delivers the default quiet NaN. Payloads convert by
 * shifting the trailing field (left widening, right narrowing with
 * truncation, quiet bit set); narrowing that would truncate the
 * payload to the infinity pattern delivers the default quiet NaN
 * instead, with no invalid for the truncation itself. For FMA the
 * operand order is multiplicand, multiplier, addend, and the
 * 0 x infinity with quiet-NaN addend ruling (signal invalid, deliver
 * the addend) falls out: the caller raises invalid for the product
 * and this helper delivers the addend under (c).
 */
#ifndef MSF_DECODE_H
#define MSF_DECODE_H

#include "msf_internal.h"

enum {
    MSF_VC_ZERO = 0,
    MSF_VC_SUBNORMAL = 1,
    MSF_VC_NORMAL = 2,
    MSF_VC_INFINITY = 3,
    MSF_VC_QUIET_NAN = 4,
    MSF_VC_SIGNALING_NAN = 5
};

typedef struct msf_decoded {
    int sign;          /* 0 or 1 */
    int cls;           /* MSF_VC_* */
    int32_t exp;       /* finite: value = sig * 2^exp */
    msf_u128_t sig;    /* finite: significand; NaN: trailing field */
    uint64_t bits;     /* original encoding */
} msf_decoded_t;

static inline msf_decoded_t msf_decode(int fmt, uint64_t bits)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    msf_decoded_t d;
    uint32_t e = (uint32_t)((bits >> fp->frac_bits) & fp->exp_max);
    uint64_t frac = bits & fp->frac_mask;
    d.sign = (bits & fp->sign_mask) != 0u;
    d.bits = bits;
    if (e == fp->exp_max) {
        d.sig = msf_u128_from_u64(frac);
        d.exp = 0;
        d.cls = frac == 0u ? MSF_VC_INFINITY
                : ((frac & fp->quiet_bit) != 0u ? MSF_VC_QUIET_NAN
                                                : MSF_VC_SIGNALING_NAN);
    } else if (e == 0u) {
        d.sig = msf_u128_from_u64(frac);
        d.exp = fp->emin - fp->frac_bits;
        d.cls = frac == 0u ? MSF_VC_ZERO : MSF_VC_SUBNORMAL;
    } else {
        d.sig = msf_u128_from_u64(frac | (1ULL << fp->frac_bits));
        d.exp = (int32_t)e - fp->bias - fp->frac_bits;
        d.cls = MSF_VC_NORMAL;
    }
    return d;
}

static inline int msf_is_nan_cls(int cls)
{
    return cls == MSF_VC_QUIET_NAN || cls == MSF_VC_SIGNALING_NAN;
}

/* Convert one NaN operand to a quiet NaN encoding of dest format. */
static inline uint64_t msf_nan_to_dest(int dfmt, int sfmt, const msf_decoded_t *src)
{
    const msf_fmt_params_t *df = &MSF_FMT_PARAMS[dfmt];
    const msf_fmt_params_t *sf = &MSF_FMT_PARAMS[sfmt];
    uint64_t payload = msf_u128_to_u64_trunc(src->sig);
    uint64_t dpayload;
    if (df->frac_bits >= sf->frac_bits) {
        dpayload = payload << (df->frac_bits - sf->frac_bits);
    } else {
        dpayload = payload >> (sf->frac_bits - df->frac_bits);
    }
    dpayload |= df->quiet_bit;
    if ((dpayload & df->frac_mask) == 0u) {
        return df->default_qnan;
    }
    return (src->sign ? df->sign_mask : 0u) | df->infinity | dpayload;
}

/* Decide a NaN delivery. Returns 1 and writes *out when the result
 * is a NaN under the matrix; invalid is ORed into *flags by this
 * helper for cases (a) and (b). */
static inline int msf_nan_delivery(int dfmt, const msf_decoded_t ops[],
                                   const int op_fmts[], int n,
                                   int invalid_without_nan,
                                   uint64_t *out, msf_flags_t *flags)
{
    int i;
    for (i = 0; i < n; i++) {
        if (ops[i].cls == MSF_VC_SIGNALING_NAN) {
            *flags |= MSF_FLAG_INVALID;
            *out = msf_nan_to_dest(dfmt, op_fmts[i], &ops[i]);
            return 1;
        }
    }
    for (i = 0; i < n; i++) {
        if (ops[i].cls == MSF_VC_QUIET_NAN) {
            *out = msf_nan_to_dest(dfmt, op_fmts[i], &ops[i]);
            return 1;
        }
    }
    if (invalid_without_nan) {
        *flags |= MSF_FLAG_INVALID;
        *out = MSF_FMT_PARAMS[dfmt].default_qnan;
        return 1;
    }
    return 0;
}

/* Exact comparison of two finite decoded values: -1, 0, +1.
 * Signed zeros compare equal. Domain: cls ZERO/SUBNORMAL/NORMAL. */
static inline int msf_cmp_finite(const msf_decoded_t *a, const msf_decoded_t *b)
{
    int az = a->cls == MSF_VC_ZERO, bz = b->cls == MSF_VC_ZERO;
    int mag;
    if (az && bz) {
        return 0;
    }
    if (a->sign != b->sign) {
        return a->sign ? -1 : 1;
    }
    if (az) {
        mag = -1;
    } else if (bz) {
        mag = 1;
    } else {
        int32_t la = 128 - msf_u128_clz(a->sig);
        int32_t lb = 128 - msf_u128_clz(b->sig);
        int32_t ta = a->exp + la, tb = b->exp + lb;
        if (ta != tb) {
            mag = ta > tb ? 1 : -1;
        } else if (a->exp >= b->exp) {
            mag = msf_u128_cmp(msf_u128_shl(a->sig, (unsigned)(a->exp - b->exp)),
                               b->sig);
        } else {
            mag = msf_u128_cmp(a->sig,
                               msf_u128_shl(b->sig, (unsigned)(b->exp - a->exp)));
        }
    }
    return a->sign ? -mag : mag;
}

#endif /* MSF_DECODE_H */
