/* msf_roundpack.c - binary64 round-and-pack exemplar (SF-0 6 item 4).
 *
 * The single rounding event every binary64 operation funnels into:
 * exact magnitude (sig + f) * 2^exp2, f in [0,1) recorded only as
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

#define P MSF_F64_PRECISION
#define EMIN MSF_F64_EMIN
#define EMAX MSF_F64_EMAX
#define BIAS MSF_F64_BIAS

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

msf64_t msf_pack_f64(int sign, int32_t exp2, msf_u128_t sig, int sticky,
                     int rm, msf_flags_t *flags)
{
    uint64_t sign_bit = sign ? MSF_F64_SIGN_MASK : 0u;
    int32_t l, e_bits, e, sh;
    uint64_t k2, cand;
    int guard, round_bit, stick, inexact, inc;

    if (msf_u128_is_zero(sig)) {
        return (msf64_t)sign_bit;
    }
    l = 128 - msf_u128_clz(sig);          /* significand bit length */
    e_bits = exp2 + l - 1;                /* exponent of the top bit */
    e = e_bits < EMIN ? EMIN : e_bits;    /* subnormal clamp */
    sh = (e - (P + 1)) - exp2;            /* bits dropped below round */

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
    if ((cand >> P) != 0u) {
        cand >>= 1;
        e += 1;
    }

    if (e > EMAX) {
        int to_inf = (rm == MSF_IROUND_TIES_TO_EVEN)
                  || (rm == MSF_IROUND_TIES_TO_AWAY)
                  || (rm == MSF_IROUND_TOWARD_POSITIVE && !sign)
                  || (rm == MSF_IROUND_TOWARD_NEGATIVE && sign);
        *flags |= MSF_FLAG_OVERFLOW | MSF_FLAG_INEXACT;
        if (to_inf) {
            return (msf64_t)(sign_bit | MSF_F64_INFINITY);
        }
        return (msf64_t)(sign_bit
                         | ((uint64_t)(MSF_F64_EXP_MAX - 1u) << MSF_F64_FRAC_BITS)
                         | MSF_F64_FRAC_MASK);
    }

    if (inexact) {
        int tiny_after = cand < (1ULL << (P - 1));
        int tiny_before = e_bits < EMIN;
        *flags |= MSF_FLAG_INEXACT;
        if (MSF_TININESS_AFTER_ROUNDING ? tiny_after : tiny_before) {
            *flags |= MSF_FLAG_UNDERFLOW;
        }
    }

    if (cand >= (1ULL << (P - 1))) {
        return (msf64_t)(sign_bit
                         | ((uint64_t)(e + BIAS) << MSF_F64_FRAC_BITS)
                         | (cand - (1ULL << (P - 1))));
    }
    return (msf64_t)(sign_bit | cand);
}
