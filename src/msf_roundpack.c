/* msf_roundpack.c - the shared round-and-pack kernel.
 *
 * P0 built this as the binary64 exemplar (SF-0 6 item 4); the Wave 1
 * lead prep generalized it over generated format parameters so both
 * format parcels share ONE rounding event implementation and cannot
 * drift on Clause 7 boundary behaviour. The binary64 behaviour is
 * unchanged (the P0 vector gates are the evidence, re-run).
 *
 * Exact magnitude (sig + f) * 2^exp2, f in [0,1) recorded only as
 * "nonzero" by sticky, is rounded once and packed. Flags follow
 * Clause 7 with tininess after rounding (SF-0 2.5): underflow needs
 * the ROUNDED result tiny (zero or subnormal) and inexact; the exact
 * value crossing to the smallest normal is therefore not underflow.
 * Overflow delivery (infinity vs largest finite) follows the mode
 * and sign; overflow always carries inexact.
 *
 * Domain contract: finite numeric intermediates only. sig == 0 with
 * sticky set is outside the domain - callers jam tail bits into sig
 * (msf_u128_shr_jam) so a nonzero value always has a bit in sig.
 */
#include "msf_internal.h"

#define FMT_ROW(P) \
    { MSF_##P##_PRECISION, MSF_##P##_FRAC_BITS, MSF_##P##_EMIN, \
      MSF_##P##_EMAX, MSF_##P##_BIAS, (uint32_t)MSF_##P##_EXP_MAX, \
      MSF_##P##_SIGN_MASK, MSF_##P##_INFINITY, MSF_##P##_FRAC_MASK, \
      MSF_##P##_QUIET_BIT, MSF_##P##_DEFAULT_QNAN }

const msf_fmt_params_t MSF_FMT_PARAMS[3] = {
    FMT_ROW(F16),
    FMT_ROW(F32),
    FMT_ROW(F64)
};

static int any_bits_below(msf_u128_t a, int32_t n)
{
    if (n <= 0) {
        return 0;
    }
    if (n >= 128) {
        return !msf_u128_is_zero(a);
    }
    return !msf_u128_is_zero(msf_u128_shl(a, (unsigned)(128 - n)));
}

uint64_t msf_pack_generic(const msf_fmt_params_t *fp, int sign, int32_t exp2,
                          msf_u128_t sig, int sticky, int rm,
                          msf_flags_t *flags)
{
    const int p = fp->precision;
    uint64_t sign_bit = sign ? fp->sign_mask : 0u;
    int32_t l, e_bits, e, sh;
    uint64_t k2, cand;
    int guard, round_bit, stick, inexact, inc;

    if (msf_u128_is_zero(sig)) {
        return sign_bit;
    }
    l = 128 - msf_u128_clz(sig);          /* significand bit length */
    e_bits = exp2 + l - 1;                /* exponent of the top bit */
    e = e_bits < fp->emin ? fp->emin : e_bits;    /* subnormal clamp */
    sh = (e - (p + 1)) - exp2;            /* bits dropped below round */

    if (sh <= 0) {
        k2 = msf_u128_to_u64_trunc(msf_u128_shl(sig, (unsigned)-sh));
        stick = sticky != 0;
    } else if (sh >= 128) {
        k2 = 0u;
        stick = 1;
    } else {
        k2 = msf_u128_to_u64_trunc(msf_u128_shr(sig, (unsigned)sh));
        stick = (sticky != 0) || any_bits_below(sig, sh);
    }
    guard = (int)((k2 >> 1) & 1u);
    round_bit = (int)(k2 & 1u);
    cand = k2 >> 2;
    inexact = guard || round_bit || stick;

    inc = 0;
    switch (rm) {
    case MSF_IROUND_TIES_TO_EVEN:
        inc = guard && (round_bit || stick || (cand & 1u));
        break;
    case MSF_IROUND_TIES_TO_AWAY:
        inc = guard;
        break;
    case MSF_IROUND_TOWARD_POSITIVE:
        inc = !sign && inexact;
        break;
    case MSF_IROUND_TOWARD_NEGATIVE:
        inc = sign && inexact;
        break;
    default: /* toward zero */
        inc = 0;
        break;
    }
    cand += (uint64_t)inc;
    if ((cand >> p) != 0u) {
        cand >>= 1;
        e += 1;
    }

    if (e > fp->emax) {
        int to_inf = (rm == MSF_IROUND_TIES_TO_EVEN)
                  || (rm == MSF_IROUND_TIES_TO_AWAY)
                  || (rm == MSF_IROUND_TOWARD_POSITIVE && !sign)
                  || (rm == MSF_IROUND_TOWARD_NEGATIVE && sign);
        *flags |= MSF_FLAG_OVERFLOW | MSF_FLAG_INEXACT;
        if (to_inf) {
            return sign_bit | fp->infinity;
        }
        return sign_bit
               | ((uint64_t)(fp->exp_max - 1u) << fp->frac_bits)
               | fp->frac_mask;
    }

    if (inexact) {
        int tiny_after = cand < (1ULL << (p - 1));
        int tiny_before = e_bits < fp->emin;
        *flags |= MSF_FLAG_INEXACT;
        if (MSF_TININESS_AFTER_ROUNDING ? tiny_after : tiny_before) {
            *flags |= MSF_FLAG_UNDERFLOW;
        }
    }

    if (cand >= (1ULL << (p - 1))) {
        return sign_bit
               | ((uint64_t)(e + fp->bias) << fp->frac_bits)
               | (cand - (1ULL << (p - 1)));
    }
    return sign_bit | cand;
}

msf16_t msf_pack_f16(int sign, int32_t exp2, msf_u128_t sig, int sticky,
                     int rm, msf_flags_t *flags)
{
    return (msf16_t)msf_pack_generic(&MSF_FMT_PARAMS[MSF_FMT_F16], sign, exp2,
                                     sig, sticky, rm, flags);
}

msf32_t msf_pack_f32(int sign, int32_t exp2, msf_u128_t sig, int sticky,
                     int rm, msf_flags_t *flags)
{
    return (msf32_t)msf_pack_generic(&MSF_FMT_PARAMS[MSF_FMT_F32], sign, exp2,
                                     sig, sticky, rm, flags);
}

msf64_t msf_pack_f64(int sign, int32_t exp2, msf_u128_t sig, int sticky,
                     int rm, msf_flags_t *flags)
{
    return (msf64_t)msf_pack_generic(&MSF_FMT_PARAMS[MSF_FMT_F64], sign, exp2,
                                     sig, sticky, rm, flags);
}
