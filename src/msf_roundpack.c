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
 * the result tiny and inexact, where tiny is judged on the result
 * rounded to full precision AS THOUGH THE EXPONENT RANGE WERE
 * UNBOUNDED (Clause 7.5): that value below 2^emin is tiny even when
 * the delivered (subnormal-granularity) rounding reaches the
 * smallest normal exactly, and an exact value below 2^emin whose
 * unbounded rounding reaches 2^emin is not tiny. The unbounded
 * rounding below is flags-only; delivered bits never depend on it.
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

static int round_inc(int rm, int sign, uint64_t cand, int guard,
                     int round_bit, int stick)
{
    int inexact = guard || round_bit || stick;
    switch (rm) {
    case MSF_IROUND_TIES_TO_EVEN:
        return guard && (round_bit || stick || (cand & 1u));
    case MSF_IROUND_TIES_TO_AWAY:
        return guard;
    case MSF_IROUND_TOWARD_POSITIVE:
        return !sign && inexact;
    case MSF_IROUND_TOWARD_NEGATIVE:
        return sign && inexact;
    default: /* toward zero */
        return 0;
    }
}

/* Extract the (p+2)-bit window: result bits, guard, round; sticky
 * summarizes everything below the round bit plus the input sticky. */
static uint64_t extract_k2(msf_u128_t sig, int32_t sh, int sticky, int *stick_out)
{
    if (sh <= 0) {
        *stick_out = sticky != 0;
        return msf_u128_to_u64_trunc(msf_u128_shl(sig, (unsigned)-sh));
    }
    if (sh >= 128) {
        *stick_out = 1;
        return 0u;
    }
    *stick_out = (sticky != 0) || any_bits_below(sig, sh);
    return msf_u128_to_u64_trunc(msf_u128_shr(sig, (unsigned)sh));
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

    k2 = extract_k2(sig, sh, sticky, &stick);
    guard = (int)((k2 >> 1) & 1u);
    round_bit = (int)(k2 & 1u);
    cand = k2 >> 2;
    inexact = guard || round_bit || stick;

    inc = round_inc(rm, sign, cand, guard, round_bit, stick);
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
        int tiny_after, tiny_before = e_bits < fp->emin;
        if (!tiny_before) {
            tiny_after = 0;
        } else {
            /* flags-only: round at the unclamped binade scale and
             * ask whether that value reaches 2^emin (Clause 7.5) */
            int32_t sh_u = (e_bits - (p + 1)) - exp2;
            int stick_u;
            uint64_t k2_u = extract_k2(sig, sh_u, sticky, &stick_u);
            uint64_t cand_u = k2_u >> 2;
            int32_t e_r = e_bits;
            cand_u += (uint64_t)round_inc(rm, sign, cand_u,
                                           (int)((k2_u >> 1) & 1u),
                                           (int)(k2_u & 1u), stick_u);
            if ((cand_u >> p) != 0u) {
                e_r += 1;
            }
            tiny_after = e_r < fp->emin;
        }
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
