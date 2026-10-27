/* msf_string.c - decimal/hex character conversions (Wave 3).
 *
 * LEAD-PREP STUB: seeded so the runner's char-vector support links
 * while these instantiations are still planned (dispatch NULL,
 * runner SKIPs them; these bodies are unreachable through the
 * vector path). parcel-str replaces every body with the real
 * implementation; see ledger/briefs/w3-str.md. The stub behavior
 * (no valid prefix / empty result) is deliberately the
 * header-documented degenerate case, never a silent wrong answer
 * for a claimed row: no row in tables/implemented.tsv names these
 * functions until the parcel lands them. */
#include "msf_internal.h"

#define MSF_STR_STUB_FROM(NAME, T)                                     \
    T NAME(const char *s, size_t *consumed, msf_rounding_t rm,         \
           msf_flags_t *flags)                                         \
    {                                                                  \
        (void)s; (void)rm; (void)flags;                                \
        if (consumed != NULL) { *consumed = 0u; }                      \
        return (T)0;                                                   \
    }
#define MSF_STR_STUB_TO_DEC(NAME, T)                                   \
    size_t NAME(T a, const msf_decimal_spec_t *spec, char *buf,        \
                size_t buf_size, msf_rounding_t rm, msf_flags_t *flags) \
    {                                                                  \
        (void)a; (void)spec; (void)buf; (void)buf_size;                \
        (void)rm; (void)flags;                                         \
        return 0u;                                                     \
    }
#define MSF_STR_STUB_TO_HEX(NAME, T)                                   \
    size_t NAME(T a, const msf_hex_spec_t *spec, char *buf,            \
                size_t buf_size, msf_rounding_t rm, msf_flags_t *flags) \
    {                                                                  \
        (void)a; (void)spec; (void)buf; (void)buf_size;                \
        (void)rm; (void)flags;                                         \
        return 0u;                                                     \
    }

MSF_STR_STUB_FROM(msf16_from_decimal, msf16_t)
MSF_STR_STUB_FROM(msf32_from_decimal, msf32_t)
MSF_STR_STUB_FROM(msf64_from_decimal, msf64_t)
MSF_STR_STUB_FROM(msf16_from_hex, msf16_t)
MSF_STR_STUB_FROM(msf32_from_hex, msf32_t)
MSF_STR_STUB_FROM(msf64_from_hex, msf64_t)
MSF_STR_STUB_TO_DEC(msf16_to_decimal, msf16_t)
MSF_STR_STUB_TO_DEC(msf32_to_decimal, msf32_t)
MSF_STR_STUB_TO_DEC(msf64_to_decimal, msf64_t)
MSF_STR_STUB_TO_HEX(msf16_to_hex, msf16_t)
MSF_STR_STUB_TO_HEX(msf32_to_hex, msf32_t)
MSF_STR_STUB_TO_HEX(msf64_to_hex, msf64_t)
