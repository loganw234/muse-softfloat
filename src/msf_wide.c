/* msf_wide.c - 128-bit exact integer helpers over 32-bit limbs.
 * SF-0 Section 3.2: implemented in-tree; compiler wide types are not
 * used so the target build's symbol surface stays integer-only and
 * auditable. Width rationale: docs/WIDTHS.md.
 */
#include "msf_internal.h"

msf_u128_t msf_u128_from_u64(uint64_t x)
{
    msf_u128_t r;
    r.w[0] = (uint32_t)x;
    r.w[1] = (uint32_t)(x >> 32);
    r.w[2] = 0u;
    r.w[3] = 0u;
    return r;
}

uint64_t msf_u128_to_u64_trunc(msf_u128_t a)
{
    return ((uint64_t)a.w[1] << 32) | (uint64_t)a.w[0];
}

int msf_u128_is_zero(msf_u128_t a)
{
    return (a.w[0] | a.w[1] | a.w[2] | a.w[3]) == 0u;
}

int msf_u128_cmp(msf_u128_t a, msf_u128_t b)
{
    int i;
    for (i = 3; i >= 0; i--) {
        if (a.w[i] != b.w[i]) {
            return a.w[i] > b.w[i] ? 1 : -1;
        }
    }
    return 0;
}

msf_u128_t msf_u128_add(msf_u128_t a, msf_u128_t b, uint32_t *carry_out)
{
    msf_u128_t r;
    uint64_t carry = 0u;
    int i;
    for (i = 0; i < 4; i++) {
        uint64_t s = (uint64_t)a.w[i] + (uint64_t)b.w[i] + carry;
        r.w[i] = (uint32_t)s;
        carry = s >> 32;
    }
    if (carry_out != 0) {
        *carry_out = (uint32_t)carry;
    }
    return r;
}

msf_u128_t msf_u128_add_u32(msf_u128_t a, uint32_t b, uint32_t *carry_out)
{
    msf_u128_t bb;
    bb.w[0] = b;
    bb.w[1] = 0u;
    bb.w[2] = 0u;
    bb.w[3] = 0u;
    return msf_u128_add(a, bb, carry_out);
}

msf_u128_t msf_u128_sub(msf_u128_t a, msf_u128_t b, uint32_t *borrow_out)
{
    msf_u128_t r;
    uint64_t borrow = 0u;
    int i;
    for (i = 0; i < 4; i++) {
        uint64_t d = (uint64_t)a.w[i] - (uint64_t)b.w[i] - borrow;
        r.w[i] = (uint32_t)d;
        borrow = (d >> 63) & 1u;
    }
    if (borrow_out != 0) {
        *borrow_out = (uint32_t)borrow;
    }
    return r;
}

msf_u128_t msf_u128_mul_u64_u64(uint64_t a, uint64_t b)
{
    /* 32x32->64 limb products accumulated into 128 bits. */
    uint32_t a32[2], b32[2];
    msf_u128_t r;
    int i, j;
    a32[0] = (uint32_t)a;
    a32[1] = (uint32_t)(a >> 32);
    b32[0] = (uint32_t)b;
    b32[1] = (uint32_t)(b >> 32);
    r.w[0] = r.w[1] = r.w[2] = r.w[3] = 0u;
    for (i = 0; i < 2; i++) {
        uint64_t carry = 0u;
        for (j = 0; j < 2; j++) {
            uint64_t t = (uint64_t)a32[i] * (uint64_t)b32[j]
                       + (uint64_t)r.w[i + j] + carry;
            r.w[i + j] = (uint32_t)t;
            carry = t >> 32;
        }
        r.w[i + 2] = (uint32_t)(r.w[i + 2] + (uint32_t)carry);
    }
    return r;
}

msf_u128_t msf_u128_shl(msf_u128_t a, unsigned n)
{
    msf_u128_t r;
    unsigned limbs, bits;
    int i;
    r.w[0] = r.w[1] = r.w[2] = r.w[3] = 0u;
    if (n >= 128u) {
        return r;
    }
    limbs = n / 32u;
    bits = n % 32u;
    for (i = 3; i >= 0; i--) {
        uint32_t lo = 0u, hi = 0u;
        int src = i - (int)limbs;
        if (src >= 0) {
            lo = a.w[src] << bits;
            if (bits != 0u && src > 0) {
                hi = a.w[src - 1] >> (32u - bits);
            }
        }
        r.w[i] = lo | hi;
    }
    return r;
}

msf_u128_t msf_u128_shr(msf_u128_t a, unsigned n)
{
    msf_u128_t r;
    unsigned limbs, bits;
    int i;
    r.w[0] = r.w[1] = r.w[2] = r.w[3] = 0u;
    if (n >= 128u) {
        return r;
    }
    limbs = n / 32u;
    bits = n % 32u;
    for (i = 0; i < 4; i++) {
        uint32_t lo = 0u, hi = 0u;
        int src = i + (int)limbs;
        if (src < 4) {
            lo = a.w[src] >> bits;
            if (bits != 0u && src < 3) {
                hi = a.w[src + 1] << (32u - bits);
            }
        }
        r.w[i] = lo | hi;
    }
    return r;
}

msf_u128_t msf_u128_shr_jam(msf_u128_t a, unsigned n, int sticky_in)
{
    int jam = sticky_in != 0;
    msf_u128_t masked;
    int i;
    if (n == 0u) {
        if (jam) {
            a.w[0] |= 1u;
        }
        return a;
    }
    if (n >= 128u) {
        jam = jam || !msf_u128_is_zero(a);
        masked = msf_u128_from_u64(jam ? 1u : 0u);
        return masked;
    }
    masked = a;
    if (!jam) {
        unsigned full = n / 32u, rem = n % 32u;
        for (i = 0; i < (int)full; i++) {
            jam = jam || (masked.w[i] != 0u);
        }
        if (rem != 0u) {
            jam = jam || ((masked.w[full] & ((1u << rem) - 1u)) != 0u);
        }
    }
    masked = msf_u128_shr(a, n);
    if (jam) {
        masked.w[0] |= 1u;
    }
    return masked;
}

int msf_u128_clz(msf_u128_t a)
{
    int i, n = 0;
    for (i = 3; i >= 0; i--) {
        uint32_t w = a.w[i];
        if (w != 0u) {
            while ((w & 0x80000000u) == 0u) {
                w <<= 1;
                n++;
            }
            return n;
        }
        n += 32;
    }
    return 128;
}
