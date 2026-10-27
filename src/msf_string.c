/* msf_string.c - decimal and hexadecimal character conversions.
 *
 * convertFrom/ToDecimalCharacter and convertFrom/ToHexCharacter for
 * binary16/32/64 (754-2019 5.4.2, 5.4.3, 5.12), correctly rounded
 * within H = MSF_DECIMAL_H = 20 significant decimal digits (SF-0 2.6)
 * and exactly for hex input of any length. Clean-room exact
 * big-integer arithmetic only; no hardware arithmetic types, no
 * allocation. Design of record: parcel-str design entry with lead
 * rulings R1-R6 (2026-10-27) in the round ledger.
 *
 * Grammar (R1): consumed is the longest valid prefix length from
 * s[0]; no leading whitespace is skipped; with no valid prefix the
 * result is positive zero, consumed 0, no flags (header rule).
 * Decimal finite: sign? (DIGITS [. DIGITS*] | . DIGITS) exponent?,
 * an incomplete exponent suffix is not consumed. Hex finite: the
 * 5.12.3 grammar with a mandatory p-exponent (R3). Specials in both
 * input ops: inf/infinity, nan (quiet, sign applied), snan
 * (signaling NaN, payload 1, no invalid - R2). No payload suffix is
 * emitted or accepted (R2). More than H significant decimal digits
 * take the 5.12.2 two-step route: round the digit string to H
 * digits under the attribute, then convert exactly; step 1 adds
 * inexact iff it dropped a nonzero digit, underflow comes only
 * from the step-2 pack (R4).
 *
 * Rounding routes through msf_pack_generic wherever the exact value
 * is in hand as sig * 2^exp2 (both input directions). The two
 * output roundings (decimal digit string, hex fraction digits)
 * cannot be expressed by the pack and round on exact digit/bit
 * tails with exact tie evidence.
 */
#include "msf_internal.h"
#include "msf_decode.h"

#include <stddef.h>

static const int MSF_PMIN[3] = { MSF_F16_PMIN, MSF_F32_PMIN, MSF_F64_PMIN };

/* ------------------------------------------------------------------ */
/* Fixed-width big unsigned integer (this TU only).                    */
/* 96 limbs = 3072 bits. Largest values built:                         */
/*  - D * 10^E or 10^|E| with |E| <= 400 after the magnitude           */
/*    early-outs: < 2^67 * 2^1330 < 2^1400.                            */
/*  - sig * 5^k for exact decimal expansion, sig < 2^53, k <= 1074:    */
/*    < 2^(53+2494) = 2^2547.                                          */
/* Every multiply that could overflow the array is in a path whose     */
/* bound above keeps the top limb at zero; mul_u32 returns the         */
/* carry out so the bound is checked, not assumed.                     */

#define BIG_LIMBS 96

typedef struct big {
    uint32_t w[BIG_LIMBS];
} big_t;

static void big_zero(big_t *a)
{
    int i;
    for (i = 0; i < BIG_LIMBS; i++) {
        a->w[i] = 0u;
    }
}

static void big_from_u64(big_t *a, uint64_t x)
{
    big_zero(a);
    a->w[0] = (uint32_t)x;
    a->w[1] = (uint32_t)(x >> 32);
}

static int big_is_zero(const big_t *a)
{
    uint32_t acc = 0u;
    int i;
    for (i = 0; i < BIG_LIMBS; i++) {
        acc |= a->w[i];
    }
    return acc == 0u;
}

static int big_bitlen(const big_t *a)
{
    int i;
    for (i = BIG_LIMBS - 1; i >= 0; i--) {
        if (a->w[i] != 0u) {
            uint32_t w = a->w[i];
            int n = i * 32;
            while (w != 0u) {
                n++;
                w >>= 1;
            }
            return n;
        }
    }
    return 0;
}

static int big_cmp(const big_t *a, const big_t *b)
{
    int i;
    for (i = BIG_LIMBS - 1; i >= 0; i--) {
        if (a->w[i] != b->w[i]) {
            return a->w[i] > b->w[i] ? 1 : -1;
        }
    }
    return 0;
}

/* a -= b; caller guarantees a >= b. */
static void big_sub(big_t *a, const big_t *b)
{
    uint64_t borrow = 0u;
    int i;
    for (i = 0; i < BIG_LIMBS; i++) {
        uint64_t d = (uint64_t)a->w[i] - (uint64_t)b->w[i] - borrow;
        a->w[i] = (uint32_t)d;
        borrow = (d >> 63) & 1u;
    }
}

/* a *= m; returns the carry out of the top limb (must be 0 in use). */
static uint32_t big_mul_u32(big_t *a, uint32_t m)
{
    uint64_t carry = 0u;
    int i;
    for (i = 0; i < BIG_LIMBS; i++) {
        uint64_t t = (uint64_t)a->w[i] * (uint64_t)m + carry;
        a->w[i] = (uint32_t)t;
        carry = t >> 32;
    }
    return (uint32_t)carry;
}

static void big_add_u32(big_t *a, uint32_t x)
{
    uint64_t carry = x;
    int i = 0;
    while (carry != 0u && i < BIG_LIMBS) {
        uint64_t t = (uint64_t)a->w[i] + carry;
        a->w[i] = (uint32_t)t;
        carry = t >> 32;
        i++;
    }
}

static void big_shl(big_t *r, const big_t *a, unsigned n)
{
    unsigned limbs = n / 32u, bits = n % 32u;
    int i;
    big_zero(r);
    if (limbs >= (unsigned)BIG_LIMBS) {
        return;
    }
    for (i = BIG_LIMBS - 1; i >= 0; i--) {
        int src = i - (int)limbs;
        uint32_t lo = 0u, hi = 0u;
        if (src >= 0) {
            lo = a->w[src] << bits;
            if (bits != 0u && src > 0) {
                hi = a->w[src - 1] >> (32u - bits);
            }
        }
        r->w[i] = lo | hi;
    }
}

static void big_shr1(big_t *a)
{
    int i;
    for (i = 0; i < BIG_LIMBS; i++) {
        uint32_t hi = (i + 1 < BIG_LIMBS) ? (a->w[i + 1] << 31) : 0u;
        a->w[i] = (a->w[i] >> 1) | hi;
    }
}

static void big_set_bit(big_t *a, unsigned n)
{
    if (n < (unsigned)(BIG_LIMBS * 32)) {
        a->w[n / 32u] |= 1u << (n % 32u);
    }
}

/* Binary long division: q = num / den, r = num % den. den != 0. */
static void big_divmod(big_t *q, big_t *r, const big_t *num, const big_t *den)
{
    big_t shifted, rem;
    int shift, k;
    big_zero(q);
    rem = *num;
    if (big_cmp(num, den) < 0) {
        *r = rem;
        return;
    }
    shift = big_bitlen(num) - big_bitlen(den);
    big_shl(&shifted, den, (unsigned)shift);
    for (k = shift; k >= 0; k--) {
        if (big_cmp(&rem, &shifted) >= 0) {
            big_sub(&rem, &shifted);
            big_set_bit(q, (unsigned)k);
        }
        big_shr1(&shifted);
    }
    *r = rem;
}

/* a *= 10^e (e >= 0) via 10^9 chunks. Returns nonzero on overflow. */
static int big_mul_pow10(big_t *a, int e)
{
    static const uint32_t p10[9] = { 1u, 10u, 100u, 1000u, 10000u,
        100000u, 1000000u, 10000000u, 100000000u };
    int bad = 0;
    while (e >= 9) {
        bad |= big_mul_u32(a, 1000000000u) != 0u;
        e -= 9;
    }
    if (e > 0) {
        bad |= big_mul_u32(a, p10[e]) != 0u;
    }
    return bad;
}

/* a *= 5^e (e >= 0) via 5^13 chunks. Returns nonzero on overflow. */
static int big_mul_pow5(big_t *a, int e)
{
    static const uint32_t p5[13] = { 1u, 5u, 25u, 125u, 625u, 3125u,
        15625u, 78125u, 390625u, 1953125u, 9765625u, 48828125u,
        244140625u };
    int bad = 0;
    while (e >= 13) {
        bad |= big_mul_u32(a, 1220703125u) != 0u;
        e -= 13;
    }
    if (e > 0) {
        bad |= big_mul_u32(a, p5[e]) != 0u;
    }
    return bad;
}

/* Reduce a nonzero big value to the pack input shape: value equals
 * (sig + f) * 2^(*off) with sig the top <=128 bits and f in [0,1)
 * nonzero iff *sticky. */
static msf_u128_t big_top128(const big_t *a, int32_t *off, int *sticky)
{
    int bl = big_bitlen(a);
    msf_u128_t sig;
    int i;
    if (bl <= 128) {
        for (i = 0; i < 4; i++) {
            sig.w[i] = a->w[i];
        }
        *off = 0;
        *sticky = 0;
        return sig;
    }
    {
        int shift = bl - 128;
        unsigned limb = (unsigned)shift / 32u, bits = (unsigned)shift % 32u;
        uint32_t acc = 0u;
        unsigned li;
        for (i = 0; i < 4; i++) {
            uint32_t lo = a->w[limb + (unsigned)i] >> bits;
            uint32_t hi = 0u;
            if (bits != 0u && limb + (unsigned)i + 1u < (unsigned)BIG_LIMBS) {
                hi = a->w[limb + (unsigned)i + 1u] << (32u - bits);
            }
            sig.w[i] = lo | hi;
        }
        for (li = 0; li < limb; li++) {
            acc |= a->w[li];
        }
        if (bits != 0u) {
            acc |= a->w[limb] & ((1u << bits) - 1u);
        }
        *off = shift;
        *sticky = acc != 0u;
        return sig;
    }
}

/* Divide by a small u32 in place; returns the remainder. */
static uint32_t big_divmod_u32(big_t *a, uint32_t d)
{
    uint64_t rem = 0u;
    int i;
    for (i = BIG_LIMBS - 1; i >= 0; i--) {
        uint64_t cur = (rem << 32) | (uint64_t)a->w[i];
        a->w[i] = (uint32_t)(cur / d);
        rem = cur % d;
    }
    return (uint32_t)rem;
}

/* ------------------------------------------------------------------ */
/* Character helpers and shared parse pieces (R1/R2 surface).         */

static int ascii_lower(int c)
{
    return (c >= 'A' && c <= 'Z') ? c + ('a' - 'A') : c;
}

static int is_digit(int c)
{
    return c >= '0' && c <= '9';
}

static int hex_val(int c)
{
    if (c >= '0' && c <= '9') {
        return c - '0';
    }
    c = ascii_lower(c);
    if (c >= 'a' && c <= 'f') {
        return c - 'a' + 10;
    }
    return -1;
}

/* Case-insensitive match of the NUL-terminated word at s. */
static int match_ci(const char *s, const char *word)
{
    while (*word != '\0') {
        if (ascii_lower((unsigned char)*s) != *word) {
            return 0;
        }
        s++;
        word++;
    }
    return 1;
}

enum { SPC_NONE = 0, SPC_INF = 1, SPC_NAN = 2, SPC_SNAN = 3 };

/* Parse sign? applied to a special word at s. On a match returns the
 * class and sets *sign and *consumed; else SPC_NONE. Longest valid
 * prefix: "infinity" wins over "inf" when fully present. */
static int parse_special(const char *s, int *sign, size_t *consumed)
{
    size_t i = 0u;
    *sign = 0;
    if (s[i] == '+' || s[i] == '-') {
        *sign = s[i] == '-';
        i++;
    }
    if (match_ci(s + i, "infinity")) {
        *consumed = i + 8u;
        return SPC_INF;
    }
    if (match_ci(s + i, "inf")) {
        *consumed = i + 3u;
        return SPC_INF;
    }
    if (match_ci(s + i, "snan")) {
        *consumed = i + 4u;
        return SPC_SNAN;
    }
    if (match_ci(s + i, "nan")) {
        *consumed = i + 3u;
        return SPC_NAN;
    }
    return SPC_NONE;
}

static uint64_t special_bits(int fmt, int cls, int sign)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    uint64_t sb = sign ? fp->sign_mask : 0u;
    if (cls == SPC_INF) {
        return sb | fp->infinity;
    }
    if (cls == SPC_SNAN) {
        return sb | fp->infinity | 1u;
    }
    return sb | fp->default_qnan;
}

/* Saturating signed decimal exponent parse over s[*pi..]: on entry
 * *pi sits just after the exponent indicator. Returns 1 and sets
 * *out / advances *pi past the digits when sign? DIGITS+ is
 * present; returns 0 and leaves *pi unchanged otherwise. The
 * magnitude clamps at EXP_CLAMP, far beyond every early-out band
 * threshold, while all digits are still consumed. */
#define EXP_CLAMP 100000

static int parse_exponent(const char *s, size_t *pi, int32_t *out)
{
    size_t i = *pi;
    int neg = 0;
    int64_t v = 0;
    if (s[i] == '+' || s[i] == '-') {
        neg = s[i] == '-';
        i++;
    }
    if (!is_digit((unsigned char)s[i])) {
        return 0;
    }
    while (is_digit((unsigned char)s[i])) {
        v = v * 10 + (s[i] - '0');
        if (v > EXP_CLAMP) {
            v = EXP_CLAMP + 1;
        }
        i++;
    }
    *out = (int32_t)(neg ? -v : v);
    *pi = i;
    return 1;
}

/* Decimal digit-string rounding decision (beyond-H step 1 and
 * to_decimal output): should the kept magnitude increment, given
 * the last kept digit, the first dropped digit, and whether any
 * later dropped digit is nonzero? Ties are exact. */
static int dec_round_inc(int rm, int sign, int last_kept,
                         int first_dropped, int rest_nonzero)
{
    int dropped_nonzero = first_dropped != 0 || rest_nonzero;
    int gt_half = first_dropped > 5 || (first_dropped == 5 && rest_nonzero);
    int eq_half = first_dropped == 5 && !rest_nonzero;
    switch (rm) {
    case MSF_IROUND_TIES_TO_EVEN:
        return gt_half || (eq_half && (last_kept & 1));
    case MSF_IROUND_TOWARD_POSITIVE:
        return !sign && dropped_nonzero;
    case MSF_IROUND_TOWARD_NEGATIVE:
        return sign && dropped_nonzero;
    default: /* toward zero (and any non-attribute value) */
        return 0;
    }
}

/* Increment a decimal digit char array in place. Returns 1 on
 * carry out (digits were all '9'; they become '100..0' shape left
 * to the caller through the returned flag: digits[0] set to '1',
 * the rest '0'). */
static int dec_increment(char *digits, int n)
{
    int i;
    for (i = n - 1; i >= 0; i--) {
        if (digits[i] != '9') {
            digits[i] = (char)(digits[i] + 1);
            return 0;
        }
        digits[i] = '0';
    }
    digits[0] = '1';
    return 1;
}

/* ------------------------------------------------------------------ */
/* Decimal input.                                                      */

/* Per-format certain-outcome magnitude bands on m, where the exact
 * value lies in [10^(m-1), 10^m): at or above OVF_M every mode
 * overflows (10^(m-1) exceeds the largest finite); at or below
 * UNF_M the value is below half the smallest subnormal ulp
 * 2^(emin-p), so the synthesised pack below reproduces every
 * mode's bits and underflow+inexact exactly. Both syntheses are
 * cross-checked against direct exact packing at the thresholds in
 * the generator-directed boundary sets, not assumed.               */
static const int32_t DEC_OVF_M[3] = { 6, 40, 310 };
static const int32_t DEC_UNF_M[3] = { -9, -46, -325 };

static uint64_t from_decimal_generic(int fmt, const char *s,
                                     size_t *consumed, int rm,
                                     msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    size_t i = 0u, mant_end;
    int sign = 0, spc;
    size_t spc_consumed = 0u;
    char sig[MSF_DECIMAL_H + 1];       /* first H+1 significant digits */
    int sig_stored = 0;                /* digits stored in sig[]       */
    int64_t sig_count = 0;             /* total significant digits     */
    int started = 0;                   /* first nonzero digit seen     */
    int rest_nonzero = 0;              /* nonzero beyond sig[] + 1     */
    int any_digit = 0;
    int64_t frac_digits = 0;
    int32_t exp10 = 0;
    int step1_inexact = 0;
    big_t d_big;
    int d_digits;                      /* decimal digits in d_big      */
    int64_t e10;                       /* value = d_big * 10^e10       */
    int64_t m;
    int k;

    if (consumed != NULL) {
        *consumed = 0u;
    }
    if (s == NULL) {
        return 0u;
    }
    spc = parse_special(s, &sign, &spc_consumed);
    if (spc != SPC_NONE) {
        if (consumed != NULL) {
            *consumed = spc_consumed;
        }
        return special_bits(fmt, spc, sign);
    }

    if (s[i] == '+' || s[i] == '-') {
        sign = s[i] == '-';
        i++;
    }
    /* Mantissa scan: DIGITS* ['.' DIGITS*], at least one digit. */
    {
        int seen_dot = 0;
        size_t j = i;
        for (;;) {
            unsigned char c = (unsigned char)s[j];
            if (is_digit(c)) {
                any_digit = 1;
                if (seen_dot) {
                    frac_digits++;
                }
                if (started || c != '0') {
                    started = 1;
                    if (sig_count < (int64_t)(MSF_DECIMAL_H + 1)) {
                        sig[sig_stored++] = (char)c;
                    } else if (c != '0') {
                        rest_nonzero = 1;
                    }
                    sig_count++;
                }
                j++;
            } else if (c == '.' && !seen_dot) {
                seen_dot = 1;
                j++;
            } else {
                break;
            }
        }
        mant_end = j;
        if (seen_dot && !any_digit) {
            return 0u; /* "." with no digits at all */
        }
        if (!any_digit) {
            return 0u;
        }
        i = j;
    }
    /* Optional exponent; an incomplete suffix is not consumed. */
    if (s[i] == 'e' || s[i] == 'E') {
        size_t ei = i + 1u;
        int32_t ev = 0;
        if (parse_exponent(s, &ei, &ev)) {
            exp10 = ev;
            i = ei;
        } else {
            i = mant_end;
        }
    }
    if (consumed != NULL) {
        *consumed = i;
    }
    if (!started) {
        return sign ? fp->sign_mask : 0u; /* exact signed zero */
    }

    /* Value so far: (significant digit string) * 10^(exp10 -
     * frac_digits). Build d_big from at most H digits, taking the
     * 5.12.2 beyond-H first step when there are more. */
    e10 = (int64_t)exp10 - frac_digits;
    if (sig_count > MSF_DECIMAL_H) {
        int first_dropped = sig[MSF_DECIMAL_H] - '0';
        step1_inexact = first_dropped != 0 || rest_nonzero;
        e10 += sig_count - MSF_DECIMAL_H;
        if (dec_round_inc(rm, sign, sig[MSF_DECIMAL_H - 1] - '0',
                          first_dropped, rest_nonzero)) {
            if (dec_increment(sig, MSF_DECIMAL_H)) {
                e10 += 1; /* 99..9 -> 100..0 keeps H digits */
            }
        }
        d_digits = MSF_DECIMAL_H;
    } else {
        d_digits = (int)sig_count;
    }
    big_zero(&d_big);
    for (k = 0; k < d_digits; k++) {
        (void)big_mul_u32(&d_big, 10u);
        big_add_u32(&d_big, (uint32_t)(sig[k] - '0'));
    }
    /* A beyond-H increment can in principle produce d_big == 10^19
     * with a trailing-zero digit count of H; d_digits stays the digit
     * count of the string, which is what the magnitude estimate
     * needs even when trailing digits are zero. */

    m = (int64_t)d_digits + e10;
    if (m >= DEC_OVF_M[fmt]) {
        msf_flags_t f = 0u;
        uint64_t r = msf_pack_generic(fp, sign, fp->emax + 2,
                                      msf_u128_from_u64(1u), 1, rm, &f);
        *flags |= f;
        return r;
    }
    if (m <= DEC_UNF_M[fmt]) {
        msf_flags_t f = 0u;
        uint64_t r = msf_pack_generic(fp, sign, fp->emin - fp->precision - 4,
                                      msf_u128_from_u64(1u), 1, rm, &f);
        *flags |= f;
        if (step1_inexact) {
            *flags |= MSF_FLAG_INEXACT;
        }
        return r;
    }

    /* In band: |e10| <= 400 here (m within the thresholds above and
     * d_digits <= 20), so the exact big integer fits the width
     * argument at the top of this file. */
    {
        msf_flags_t f = 0u;
        uint64_t r;
        if (e10 >= 0) {
            big_t n = d_big;
            int32_t off;
            int sticky;
            msf_u128_t sig128;
            (void)big_mul_pow10(&n, (int)e10);
            sig128 = big_top128(&n, &off, &sticky);
            r = msf_pack_generic(fp, sign, off, sig128, sticky, rm, &f);
        } else {
            big_t den, num, q, rem;
            int32_t s_shift, off;
            int sticky;
            msf_u128_t sig128;
            big_from_u64(&den, 1u);
            (void)big_mul_pow10(&den, (int)(-e10));
            s_shift = (int32_t)(big_bitlen(&den) + 200 - big_bitlen(&d_big));
            if (s_shift < 0) {
                s_shift = 0;
            }
            big_shl(&num, &d_big, (unsigned)s_shift);
            big_divmod(&q, &rem, &num, &den);
            sig128 = big_top128(&q, &off, &sticky);
            sticky = sticky || !big_is_zero(&rem);
            r = msf_pack_generic(fp, sign, off - s_shift, sig128,
                                 sticky, rm, &f);
        }
        *flags |= f;
        if (step1_inexact) {
            *flags |= MSF_FLAG_INEXACT;
        }
        return r;
    }
}

/* ------------------------------------------------------------------ */
/* Hexadecimal input (5.12.3 grammar, mandatory p-exponent, R3).     */

static uint64_t from_hex_generic(int fmt, const char *s,
                                 size_t *consumed, int rm,
                                 msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    size_t i = 0u;
    int sign = 0, spc;
    size_t spc_consumed = 0u;
    msf_u128_t sig;
    int fill = 0;          /* meaningful bits in sig (its bit length) */
    int started = 0;
    int sticky = 0;
    int64_t extra_exp = 0; /* bits dropped below sig's low end        */
    int64_t frac_digits = 0;
    int any_digit = 0, seen_dot = 0;
    int32_t pexp = 0;
    int64_t exp2;

    if (consumed != NULL) {
        *consumed = 0u;
    }
    if (s == NULL) {
        return 0u;
    }
    spc = parse_special(s, &sign, &spc_consumed);
    if (spc != SPC_NONE) {
        if (consumed != NULL) {
            *consumed = spc_consumed;
        }
        return special_bits(fmt, spc, sign);
    }
    if (s[i] == '+' || s[i] == '-') {
        sign = s[i] == '-';
        i++;
    }
    if (!(s[i] == '0' && (s[i + 1u] == 'x' || s[i + 1u] == 'X'))) {
        return 0u;
    }
    i += 2u;
    sig = msf_u128_from_u64(0u);
    for (;;) {
        int c = (unsigned char)s[i];
        int hv = hex_val(c);
        if (hv >= 0) {
            any_digit = 1;
            if (seen_dot) {
                frac_digits++;
            }
            if (started || hv != 0) {
                if (!started) {
                    started = 1;
                    sig = msf_u128_from_u64((uint64_t)hv);
                    fill = hv >= 8 ? 4 : hv >= 4 ? 3 : hv >= 2 ? 2 : 1;
                } else if (fill + 4 <= 128) {
                    sig = msf_u128_shl(sig, 4u);
                    sig.w[0] |= (uint32_t)hv;
                    fill += 4;
                } else {
                    int keep = 128 - fill; /* 0..3 high bits still fit */
                    if (keep > 0) {
                        sig = msf_u128_shl(sig, (unsigned)keep);
                        sig.w[0] |= (uint32_t)(hv >> (4 - keep));
                        if ((hv & ((1 << (4 - keep)) - 1)) != 0) {
                            sticky = 1;
                        }
                    } else if (hv != 0) {
                        sticky = 1;
                    }
                    extra_exp += 4 - keep;
                    fill = 128;
                }
            }
            i++;
        } else if (c == '.' && !seen_dot) {
            seen_dot = 1;
            i++;
        } else {
            break;
        }
    }
    if (!any_digit) {
        return 0u;
    }
    if (s[i] != 'p' && s[i] != 'P') {
        return 0u; /* mandatory exponent (R3): no valid prefix */
    }
    {
        size_t ei = i + 1u;
        if (!parse_exponent(s, &ei, &pexp)) {
            return 0u;
        }
        i = ei;
    }
    if (consumed != NULL) {
        *consumed = i;
    }
    if (!started) {
        return sign ? fp->sign_mask : 0u; /* exact signed zero */
    }
    exp2 = (int64_t)pexp - 4 * frac_digits + extra_exp;
    if (exp2 > (int64_t)1 << 30) {
        exp2 = (int64_t)1 << 30;
    }
    if (exp2 < -((int64_t)1 << 30)) {
        exp2 = -((int64_t)1 << 30);
    }
    {
        msf_flags_t f = 0u;
        uint64_t r = msf_pack_generic(fp, sign, (int32_t)exp2, sig,
                                      sticky, rm, &f);
        *flags |= f;
        return r;
    }
}

/* ------------------------------------------------------------------ */
/* Output emitter. One render function per output shape runs twice:  */
/* once with buf == NULL to measure the would-be length (zero runs   */
/* are O(1) there, so a huge precision never materializes), and, if  */
/* the caller's buffer can hold result plus NUL, once for real.      */
/* This is the header rule: write nothing when it does not fit.      */

typedef struct emit {
    char *buf;     /* NULL while measuring */
    uint64_t len;
} emit_t;

static void emit_char(emit_t *e, char c)
{
    if (e->buf != NULL) {
        e->buf[e->len] = c;
    }
    e->len++;
}

static void emit_str(emit_t *e, const char *s)
{
    while (*s != '\0') {
        emit_char(e, *s++);
    }
}

static void emit_zeros(emit_t *e, uint64_t n)
{
    uint64_t k;
    if (e->buf != NULL) {
        for (k = 0u; k < n; k++) {
            e->buf[e->len + k] = '0';
        }
    }
    e->len += n;
}

static void emit_chars(emit_t *e, const char *s, uint64_t n)
{
    uint64_t k;
    for (k = 0u; k < n; k++) {
        emit_char(e, s[k]);
    }
}

/* Signed decimal exponent: always a sign, at least minwidth digits. */
static void emit_exp(emit_t *e, int32_t v, int minwidth)
{
    char tmp[12];
    int n = 0, neg = v < 0;
    uint32_t u = neg ? (uint32_t)(-(v + 1)) + 1u : (uint32_t)v;
    do {
        tmp[n++] = (char)('0' + (int)(u % 10u));
        u /= 10u;
    } while (u != 0u);
    emit_char(e, neg ? '-' : '+');
    while (n < minwidth) {
        emit_char(e, '0');
        minwidth--;
    }
    while (n > 0) {
        emit_char(e, tmp[--n]);
    }
}

/* Run the measure-then-write pair. render is called with a fresh
 * emitter each pass; ctx carries everything it needs. */
typedef void (*render_fn)(emit_t *e, const void *ctx);

static size_t finish_render(render_fn render, const void *ctx,
                            char *buf, size_t buf_size)
{
    emit_t e;
    e.buf = NULL;
    e.len = 0u;
    render(&e, ctx);
    if (buf != NULL && e.len + 1u <= (uint64_t)buf_size) {
        emit_t w;
        w.buf = buf;
        w.len = 0u;
        render(&w, ctx);
        buf[w.len] = '\0';
    }
    return (size_t)e.len;
}

struct special_ctx {
    int sign;
    int cls; /* MSF_VC_* */
};

static void render_special(emit_t *e, const void *ctx)
{
    const struct special_ctx *c = (const struct special_ctx *)ctx;
    if (c->sign) {
        emit_char(e, '-');
    }
    if (c->cls == MSF_VC_INFINITY) {
        emit_str(e, "inf");
    } else if (c->cls == MSF_VC_SIGNALING_NAN) {
        emit_str(e, "snan");
    } else {
        emit_str(e, "nan");
    }
}

/* Decimal digit string of a nonzero big integer. out has room for
 * 1024 digits (largest exact expansion needs 767). Returns count. */
static int big_to_digits(big_t *a, char *out)
{
    uint32_t groups[96];
    int ng = 0, n = 0, gi;
    while (!big_is_zero(a)) {
        groups[ng++] = big_divmod_u32(a, 1000000000u);
    }
    for (gi = ng - 1; gi >= 0; gi--) {
        uint32_t g = groups[gi];
        char tmp[9];
        int tn = 0, k;
        do {
            tmp[tn++] = (char)('0' + (int)(g % 10u));
            g /= 10u;
        } while (g != 0u);
        if (gi != ng - 1) {
            while (tn < 9) {
                tmp[tn++] = '0';
            }
        }
        for (k = tn - 1; k >= 0; k--) {
            out[n++] = tmp[k];
        }
    }
    return n;
}

/* ------------------------------------------------------------------ */
/* Decimal output (spec freeze per R5).                                */

struct dec_out_ctx {
    int sign;
    int style;          /* MSF_DECIMAL_STYLE_* (non-1 = scientific) */
    const char *digits; /* K computed significant digits            */
    int k_digits;       /* K <= H                                   */
    int64_t n_emit;     /* total significant digits emitted (>= K)  */
    int32_t dexp;       /* value = 0.digits * 10^(dexp+1) place     */
};

/* Emit significant-digit positions [start, start+count) of the
 * emitted sequence: computed digits, then zero padding. */
static void dec_emit_range(emit_t *e, const struct dec_out_ctx *c,
                           int64_t start, int64_t count)
{
    int64_t real = 0;
    if (start < c->k_digits) {
        real = c->k_digits - start;
        if (real > count) {
            real = count;
        }
        emit_chars(e, c->digits + start, (uint64_t)real);
    }
    if (count > real) {
        emit_zeros(e, (uint64_t)(count - real));
    }
}

static void render_decimal(emit_t *e, const void *ctx)
{
    const struct dec_out_ctx *c = (const struct dec_out_ctx *)ctx;
    if (c->sign) {
        emit_char(e, '-');
    }
    if (c->style != MSF_DECIMAL_STYLE_FIXED) {
        dec_emit_range(e, c, 0, 1);
        if (c->n_emit > 1) {
            emit_char(e, '.');
            dec_emit_range(e, c, 1, c->n_emit - 1);
        }
        emit_char(e, 'e');
        emit_exp(e, c->dexp, 2);
        return;
    }
    {
        int64_t point = (int64_t)c->dexp + 1; /* digits before '.' */
        if (point <= 0) {
            emit_char(e, '0');
            emit_char(e, '.');
            emit_zeros(e, (uint64_t)(-point));
            dec_emit_range(e, c, 0, c->n_emit);
        } else if (point >= c->n_emit) {
            dec_emit_range(e, c, 0, c->n_emit);
            emit_zeros(e, (uint64_t)(point - c->n_emit));
        } else {
            dec_emit_range(e, c, 0, point);
            emit_char(e, '.');
            dec_emit_range(e, c, point, c->n_emit - point);
        }
    }
}

static size_t to_decimal_generic(int fmt, uint64_t bits,
                                 const msf_decimal_spec_t *spec,
                                 char *buf, size_t buf_size,
                                 int rm, msf_flags_t *flags)
{
    msf_decoded_t d = msf_decode(fmt, bits);
    int precision = spec != NULL ? spec->precision : 0;
    int style = spec != NULL ? spec->style : MSF_DECIMAL_STYLE_SCIENTIFIC;
    int min_digits = spec != NULL ? spec->min_digits : 0;
    int64_t n_emit;
    int k_digits;
    char digits[1024];
    int32_t dexp = 0;
    int inexact = 0;
    struct dec_out_ctx ctx;

    if (d.cls == MSF_VC_INFINITY || msf_is_nan_cls(d.cls)) {
        struct special_ctx sc;
        sc.sign = d.sign;
        sc.cls = d.cls;
        return finish_render(render_special, &sc, buf, buf_size);
    }
    n_emit = precision <= 0 ? MSF_PMIN[fmt] : precision;
    if ((int64_t)min_digits > n_emit) {
        n_emit = min_digits; /* R5: floor raises computed precision */
    }
    k_digits = n_emit > MSF_DECIMAL_H ? MSF_DECIMAL_H : (int)n_emit;

    if (d.cls == MSF_VC_ZERO) {
        int k;
        for (k = 0; k < k_digits; k++) {
            digits[k] = '0';
        }
        dexp = 0;
    } else {
        big_t n;
        int nd, k;
        big_from_u64(&n, msf_u128_to_u64_trunc(d.sig));
        if (d.exp >= 0) {
            big_t shifted;
            big_shl(&shifted, &n, (unsigned)d.exp);
            n = shifted;
            nd = big_to_digits(&n, digits);
            dexp = nd - 1;
        } else {
            (void)big_mul_pow5(&n, (int)(-d.exp));
            nd = big_to_digits(&n, digits);
            dexp = nd - 1 + d.exp;
        }
        if (nd > k_digits) {
            int fd = digits[k_digits] - '0';
            int rest = 0;
            for (k = k_digits + 1; k < nd; k++) {
                if (digits[k] != '0') {
                    rest = 1;
                    break;
                }
            }
            inexact = fd != 0 || rest;
            if (dec_round_inc(rm, d.sign, digits[k_digits - 1] - '0',
                              fd, rest)) {
                if (dec_increment(digits, k_digits)) {
                    dexp += 1;
                }
            }
        } else {
            for (k = nd; k < k_digits; k++) {
                digits[k] = '0';
            }
        }
    }
    if (inexact) {
        *flags |= MSF_FLAG_INEXACT; /* signaled even on no-fit (R5) */
    }
    ctx.sign = d.sign;
    ctx.style = style;
    ctx.digits = digits;
    ctx.k_digits = k_digits;
    ctx.n_emit = n_emit;
    ctx.dexp = dexp;
    return finish_render(render_decimal, &ctx, buf, buf_size);
}

/* ------------------------------------------------------------------ */
/* Hexadecimal output (C-style 0x shape; precision semantics R5).    */

struct hex_out_ctx {
    int sign;
    int lead;              /* leading hex digit value (0, 1, or 2) */
    uint8_t fdig[16];      /* real fraction hex digit values       */
    int n_real;            /* entries in fdig                      */
    int64_t n_emit;        /* fraction digits emitted (>= n_real   */
                           /* after zero padding, or the trimmed   */
                           /* exact count when smaller)            */
    int32_t exp2;
};

static char hex_char(int v)
{
    return (char)(v < 10 ? '0' + v : 'a' + (v - 10));
}

static void render_hex(emit_t *e, const void *ctx)
{
    const struct hex_out_ctx *c = (const struct hex_out_ctx *)ctx;
    int64_t k;
    if (c->sign) {
        emit_char(e, '-');
    }
    emit_str(e, "0x");
    emit_char(e, hex_char(c->lead));
    if (c->n_emit > 0) {
        emit_char(e, '.');
        for (k = 0; k < c->n_emit && k < c->n_real; k++) {
            emit_char(e, hex_char(c->fdig[k]));
        }
        if (c->n_emit > c->n_real) {
            emit_zeros(e, (uint64_t)(c->n_emit - c->n_real));
        }
    }
    emit_char(e, 'p');
    emit_exp(e, c->exp2, 1);
}

static size_t to_hex_generic(int fmt, uint64_t bits,
                             const msf_hex_spec_t *spec,
                             char *buf, size_t buf_size,
                             int rm, msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    msf_decoded_t d = msf_decode(fmt, bits);
    int precision = spec != NULL ? spec->precision : -1;
    struct hex_out_ctx ctx;
    int t = fp->frac_bits;
    uint64_t frac;
    int ndig_exact, j;
    int inexact = 0;

    if (d.cls == MSF_VC_INFINITY || msf_is_nan_cls(d.cls)) {
        struct special_ctx sc;
        sc.sign = d.sign;
        sc.cls = d.cls;
        return finish_render(render_special, &sc, buf, buf_size);
    }
    ctx.sign = d.sign;
    ctx.n_real = 0;
    frac = bits & fp->frac_mask;
    ndig_exact = (t + 3) / 4;
    for (j = 0; j < ndig_exact; j++) {
        int shift = t - 4 * (j + 1);
        ctx.fdig[j] = (uint8_t)(shift >= 0
            ? (frac >> shift) & 0xfu
            : (frac << (-shift)) & 0xfu);
    }

    if (d.cls == MSF_VC_ZERO) {
        ctx.lead = 0;
        ctx.exp2 = 0;
        ctx.n_real = 0;
        ctx.n_emit = precision < 0 ? 0 : precision;
        return finish_render(render_hex, &ctx, buf, buf_size);
    }
    ctx.exp2 = d.cls == MSF_VC_NORMAL ? d.exp + t : fp->emin;
    if (precision < 0) {
        int n = ndig_exact;
        while (n > 0 && ctx.fdig[n - 1] == 0u) {
            n--;
        }
        ctx.lead = d.cls == MSF_VC_NORMAL ? 1 : 0;
        ctx.n_real = n;
        ctx.n_emit = n;
        return finish_render(render_hex, &ctx, buf, buf_size);
    }
    {
        int64_t shift_bits = (int64_t)t - 4 * (int64_t)precision;
        if (shift_bits <= 0) {
            ctx.lead = d.cls == MSF_VC_NORMAL ? 1 : 0;
            ctx.n_real = ndig_exact;
            ctx.n_emit = precision;
            return finish_render(render_hex, &ctx, buf, buf_size);
        }
        {
            uint64_t s_val = msf_u128_to_u64_trunc(d.sig);
            unsigned sh = (unsigned)shift_bits;
            uint64_t dropped = s_val & ((1ULL << sh) - 1u);
            uint64_t kept = s_val >> sh;
            uint64_t half = 1ULL << (sh - 1u);
            int inc;
            inexact = dropped != 0u;
            switch (rm) {
            case MSF_IROUND_TIES_TO_EVEN:
                inc = dropped > half || (dropped == half && (kept & 1u));
                break;
            case MSF_IROUND_TOWARD_POSITIVE:
                inc = !d.sign && inexact;
                break;
            case MSF_IROUND_TOWARD_NEGATIVE:
                inc = d.sign && inexact;
                break;
            default:
                inc = 0;
                break;
            }
            kept += (uint64_t)inc;
            ctx.lead = (int)(kept >> (4 * precision));
            for (j = 0; j < precision; j++) {
                ctx.fdig[j] = (uint8_t)(
                    (kept >> (4 * (precision - 1 - j))) & 0xfu);
            }
            ctx.n_real = precision;
            ctx.n_emit = precision;
            if (inexact) {
                *flags |= MSF_FLAG_INEXACT;
            }
            return finish_render(render_hex, &ctx, buf, buf_size);
        }
    }
}

/* ------------------------------------------------------------------ */
/* Public entry points (header signatures).                            */

#define MSF_STR_FROM_DEC(NAME, TYPE, FMT)                                  \
    TYPE NAME(const char *s, size_t *consumed, msf_rounding_t rm,          \
              msf_flags_t *flags)                                          \
    {                                                                      \
        return (TYPE)from_decimal_generic(FMT, s, consumed, (int)rm,       \
                                          flags);                          \
    }
#define MSF_STR_FROM_HEX(NAME, TYPE, FMT)                                  \
    TYPE NAME(const char *s, size_t *consumed, msf_rounding_t rm,          \
              msf_flags_t *flags)                                          \
    {                                                                      \
        return (TYPE)from_hex_generic(FMT, s, consumed, (int)rm, flags);   \
    }
#define MSF_STR_TO_DEC(NAME, TYPE, FMT)                                    \
    size_t NAME(TYPE a, const msf_decimal_spec_t *spec, char *buf,         \
                size_t buf_size, msf_rounding_t rm, msf_flags_t *flags)    \
    {                                                                      \
        return to_decimal_generic(FMT, (uint64_t)a, spec, buf, buf_size,   \
                                  (int)rm, flags);                         \
    }
#define MSF_STR_TO_HEX(NAME, TYPE, FMT)                                    \
    size_t NAME(TYPE a, const msf_hex_spec_t *spec, char *buf,             \
                size_t buf_size, msf_rounding_t rm, msf_flags_t *flags)    \
    {                                                                      \
        return to_hex_generic(FMT, (uint64_t)a, spec, buf, buf_size,       \
                              (int)rm, flags);                             \
    }

MSF_STR_FROM_DEC(msf16_from_decimal, msf16_t, MSF_FMT_F16)
MSF_STR_FROM_DEC(msf32_from_decimal, msf32_t, MSF_FMT_F32)
MSF_STR_FROM_DEC(msf64_from_decimal, msf64_t, MSF_FMT_F64)
MSF_STR_TO_DEC(msf16_to_decimal, msf16_t, MSF_FMT_F16)
MSF_STR_TO_DEC(msf32_to_decimal, msf32_t, MSF_FMT_F32)
MSF_STR_TO_DEC(msf64_to_decimal, msf64_t, MSF_FMT_F64)
MSF_STR_FROM_HEX(msf16_from_hex, msf16_t, MSF_FMT_F16)
MSF_STR_FROM_HEX(msf32_from_hex, msf32_t, MSF_FMT_F32)
MSF_STR_FROM_HEX(msf64_from_hex, msf64_t, MSF_FMT_F64)
MSF_STR_TO_HEX(msf16_to_hex, msf16_t, MSF_FMT_F16)
MSF_STR_TO_HEX(msf32_to_hex, msf32_t, MSF_FMT_F32)
MSF_STR_TO_HEX(msf64_to_hex, msf64_t, MSF_FMT_F64)





