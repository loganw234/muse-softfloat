/* msf_internal.h - shared exact-integer kernel interface.
 * Internal to src/. The public contract is include/muse_softfloat.h.
 * No hardware arithmetic types are named in this tree (SF-0 3.2, 5.3).
 */
#ifndef MSF_INTERNAL_H
#define MSF_INTERNAL_H

#include <stdint.h>
#include "../include/muse_softfloat.h"
#include "msf_formats.h"

/* Internal rounding modes: the four public attributes (same values)
 * plus the operation-named ties-to-away (SF-0 2.3). */
enum {
    MSF_IROUND_TIES_TO_EVEN = 0,
    MSF_IROUND_TOWARD_ZERO = 1,
    MSF_IROUND_TOWARD_POSITIVE = 2,
    MSF_IROUND_TOWARD_NEGATIVE = 3,
    MSF_IROUND_TIES_TO_AWAY = 4
};

/* Tininess is detected AFTER rounding (SF-0 2.5). The 0 setting exists
 * only so the permanent wrong-polarity negative control (SF-0 5.2) can
 * be built and watched failing; it must never be set in a build whose
 * results are quoted. */
#ifndef MSF_TININESS_AFTER_ROUNDING
#define MSF_TININESS_AFTER_ROUNDING 1
#endif

/* 128-bit exact integer over 32-bit limbs, w[0] least significant. */
typedef struct msf_u128 {
    uint32_t w[4];
} msf_u128_t;

msf_u128_t msf_u128_from_u64(uint64_t x);
uint64_t msf_u128_to_u64_trunc(msf_u128_t a);
int msf_u128_is_zero(msf_u128_t a);
int msf_u128_cmp(msf_u128_t a, msf_u128_t b);
msf_u128_t msf_u128_add(msf_u128_t a, msf_u128_t b, uint32_t *carry_out);
msf_u128_t msf_u128_add_u32(msf_u128_t a, uint32_t b, uint32_t *carry_out);
msf_u128_t msf_u128_sub(msf_u128_t a, msf_u128_t b, uint32_t *borrow_out);
msf_u128_t msf_u128_mul_u64_u64(uint64_t a, uint64_t b);
msf_u128_t msf_u128_shl(msf_u128_t a, unsigned n);
msf_u128_t msf_u128_shr(msf_u128_t a, unsigned n);
/* Right shift that ORs discarded bits into bit 0 (sticky capture). */
msf_u128_t msf_u128_shr_jam(msf_u128_t a, unsigned n, int sticky_in);
int msf_u128_clz(msf_u128_t a);

/* The binary64 round-and-pack exemplar (SF-0 6 item 4).
 * Exact magnitude = (sig + f) * 2^exp2, where f = 0 when sticky is 0
 * and 0 < f < 1 when sticky is nonzero. Rounds once per rm (internal
 * enum), packs binary64, and ORs Clause 7 flags into *flags with
 * tininess after rounding. Domain: finite numeric intermediates;
 * sig == 0 delivers a signed zero and signals nothing. */
msf64_t msf_pack_f64(int sign, int32_t exp2, msf_u128_t sig, int sticky,
                     int rm, msf_flags_t *flags);

#endif /* MSF_INTERNAL_H */
