/* examples/pico/main.c - muse-softfloat on-ramp (RP2040).
 *
 * The same calls as examples/host/main.c, over the public
 * API only, printing the same result lines over USB CDC.
 * Keep the demonstration section in step with the host file:
 * examples/pico/run_example.sh checks every line of
 * examples/host/expected.txt against the board output, so
 * drift fails loudly at the merge gate. Only the platform
 * prologue below differs (stdio bring-up, board banner, and
 * the final EXAMPLE-RESULT line the host reader waits for).
 *
 * Built by examples/pico/CMakeLists.txt; run lead-only under
 * the board lock by examples/pico/run_example.sh.
 */
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "muse_softfloat.h"

static int g_failures = 0;

static void expect(int ok)
{
    if (!ok) {
        g_failures++;
    }
}

/* Decimal rendering uses its own flags cell: conversion can
 * itself signal inexact, and that must not pollute the flags
 * printed for the arithmetic operation. Precision is a count
 * of significant digits (17 for binary64, 9 for binary32 -
 * enough to identify the value), fixed style. */
static const msf_decimal_spec_t SPEC64 = { 17, MSF_DECIMAL_STYLE_FIXED, 0 };
static const msf_decimal_spec_t SPEC32 = { 9, MSF_DECIMAL_STYLE_FIXED, 0 };

static void dec64(msf64_t bits, msf_rounding_t rm, char *buf, size_t size)
{
    msf_flags_t scratch_flags = 0;
    size_t need = msf64_to_decimal(bits, &SPEC64, buf, size, rm,
                                   &scratch_flags);
    if (need >= size) {
        (void)snprintf(buf, size, "<buffer-too-small>");
        expect(0);
    }
}

static void dec32(msf32_t bits, msf_rounding_t rm, char *buf, size_t size)
{
    msf_flags_t scratch_flags = 0;
    size_t need = msf32_to_decimal(bits, &SPEC32, buf, size, rm,
                                   &scratch_flags);
    if (need >= size) {
        (void)snprintf(buf, size, "<buffer-too-small>");
        expect(0);
    }
}

static void show64(const char *label, msf64_t bits, msf_flags_t flags,
                   msf_rounding_t rm, msf64_t want_bits,
                   msf_flags_t want_flags, const char *want_dec)
{
    char dec[64];
    dec64(bits, rm, dec, sizeof dec);
    expect(bits == want_bits);
    expect(flags == want_flags);
    expect(strcmp(dec, want_dec) == 0);
    printf("f64 %s bits=%016llx flags=%02x dec=%s\n", label,
           (unsigned long long)bits, (unsigned)flags, dec);
}

static void show32(const char *label, msf32_t bits, msf_flags_t flags,
                   msf_rounding_t rm, msf32_t want_bits,
                   msf_flags_t want_flags, const char *want_dec)
{
    char dec[64];
    dec32(bits, rm, dec, sizeof dec);
    expect(bits == want_bits);
    expect(flags == want_flags);
    expect(strcmp(dec, want_dec) == 0);
    printf("f32 %s bits=%08x flags=%02x dec=%s\n", label,
           (unsigned)bits, (unsigned)flags, dec);
}

/* Split a positive normal binary32 pattern into significand
 * and exponent with value = m * 2^e. Returns 0 for any other
 * shape (the proof below only claims this shape). */
static int split32(msf32_t bits, uint64_t *m, int *e)
{
    uint32_t exp = (bits >> 23) & 0xffu;
    if ((bits >> 31) != 0u || exp == 0u || exp == 0xffu) {
        return 0;
    }
    *m = (uint64_t)(bits & 0x7fffffu) | 0x800000u;
    *e = (int)exp - 127 - 23;
    return 1;
}

/* Re-express m * 2^e at the common exponent target, exactly.
 * Returns 0 when that cannot be done in 64 bits. */
static int rescale(uint64_t m, int e, int target, uint64_t *out)
{
    if (e >= target) {
        int shift = e - target;
        if (shift > 0 && (m >> (64 - shift)) != 0u) {
            return 0;
        }
        *out = m << shift;
        return 1;
    }
    {
        int shift = target - e;
        if (shift >= 64 || (m & (((uint64_t)1u << shift) - 1u)) != 0u) {
            return 0; /* would drop nonzero bits: not exact */
        }
        *out = m >> shift;
        return 1;
    }
}

static void run_example(void)
{
    /* Input operands as interchange bit patterns. */
    const msf64_t one64 = UINT64_C(0x3ff0000000000000);  /* 1 */
    const msf64_t ten64 = UINT64_C(0x4024000000000000);  /* 10 */
    const msf64_t two64 = UINT64_C(0x4000000000000000);  /* 2 */
    const msf64_t three_halves64 = UINT64_C(0x3ff8000000000000);
    const msf32_t one32 = UINT32_C(0x3f800000);          /* 1 */
    const msf32_t ten32 = UINT32_C(0x41200000);          /* 10 */
    const msf32_t two32 = UINT32_C(0x40000000);          /* 2 */
    msf_flags_t flags;
    msf64_t r64;
    msf32_t r32;

    printf("muse-softfloat example (public API, bit patterns in/out)\n");

    /* 1/10 has no finite binary expansion: the attribute
     * decides which neighbour is delivered. */
    flags = 0;
    r64 = msf64_div(one64, ten64, MSF_ROUND_TIES_TO_EVEN, &flags);
    show64("div 1/10 TE", r64, flags, MSF_ROUND_TIES_TO_EVEN,
           UINT64_C(0x3fb999999999999a), MSF_FLAG_INEXACT,
           "0.10000000000000001");
    flags = 0;
    r64 = msf64_div(one64, ten64, MSF_ROUND_TOWARD_ZERO, &flags);
    show64("div 1/10 TZ", r64, flags, MSF_ROUND_TOWARD_ZERO,
           UINT64_C(0x3fb9999999999999), MSF_FLAG_INEXACT,
           "0.099999999999999991");
    flags = 0;
    r32 = msf32_div(one32, ten32, MSF_ROUND_TIES_TO_EVEN, &flags);
    show32("div 1/10 TE", r32, flags, MSF_ROUND_TIES_TO_EVEN,
           UINT32_C(0x3dcccccd), MSF_FLAG_INEXACT, "0.100000001");
    flags = 0;
    r32 = msf32_div(one32, ten32, MSF_ROUND_TOWARD_ZERO, &flags);
    show32("div 1/10 TZ", r32, flags, MSF_ROUND_TOWARD_ZERO,
           UINT32_C(0x3dcccccc), MSF_FLAG_INEXACT, "0.0999999940");

    /* An exact result raises no flag at all. */
    flags = 0;
    r64 = msf64_mul(three_halves64, two64, MSF_ROUND_TIES_TO_EVEN,
                    &flags);
    show64("mul 1.5*2 TE", r64, flags, MSF_ROUND_TIES_TO_EVEN,
           UINT64_C(0x4008000000000000), (msf_flags_t)0,
           "3.0000000000000000");

    flags = 0;
    r64 = msf64_sqrt(two64, MSF_ROUND_TIES_TO_EVEN, &flags);
    show64("sqrt 2 TE", r64, flags, MSF_ROUND_TIES_TO_EVEN,
           UINT64_C(0x3ff6a09e667f3bcd), MSF_FLAG_INEXACT,
           "1.4142135623730951");
    flags = 0;
    r32 = msf32_sqrt(two32, MSF_ROUND_TIES_TO_EVEN, &flags);
    show32("sqrt 2 TE", r32, flags, MSF_ROUND_TIES_TO_EVEN,
           UINT32_C(0x3fb504f3), MSF_FLAG_INEXACT, "1.41421354");

    /* Augmented multiplication: a = 1 + 2^-23 (the next
     * binary32 value above 1). Its exact square is
     * 1 + 2^-22 + 2^-46, one bit wider than any single
     * binary32 value near 1 can hold. The pair must carry
     * all of it: head = 1 + 2^-22, tail = 2^-46. */
    {
        const msf32_t a32 = UINT32_C(0x3f800001);
        msf32_pair_t pair;
        uint64_t ma = 0, mh = 0, mt = 0, head_at = 0, tail_at = 0;
        int ea = 0, eh = 0, et = 0, proof;
        uint64_t prod, sum;

        flags = 0;
        pair = msf32_augmented_mul(a32, a32, &flags);
        expect(pair.head == UINT32_C(0x3f800002));
        expect(pair.tail == UINT32_C(0x28800000));
        expect(flags == (msf_flags_t)0); /* pair is exact */
        printf("f32 augmul (1+2^-23)^2 head=%08x tail=%08x flags=%02x\n",
               (unsigned)pair.head, (unsigned)pair.tail,
               (unsigned)flags);

        proof = split32(a32, &ma, &ea) && split32(pair.head, &mh, &eh)
                && split32(pair.tail, &mt, &et);
        prod = ma * ma; /* exact product is prod * 2^(2*ea) */
        if (proof) {
            proof = rescale(mh, eh, 2 * ea, &head_at)
                    && rescale(mt, et, 2 * ea, &tail_at);
        }
        sum = head_at + tail_at;
        proof = proof && (sum == prod);
        expect(proof);
        printf("augcheck exact-product prod=%012llx head+tail=%012llx %s\n",
               (unsigned long long)prod, (unsigned long long)sum,
               proof ? "PASS" : "FAIL");
    }

    /* Deliberate invalid operation: 0/0 delivers a quiet NaN
     * and raises invalid in caller-owned flags. */
    flags = 0;
    r64 = msf64_div((msf64_t)0, (msf64_t)0, MSF_ROUND_TIES_TO_EVEN,
                    &flags);
    {
        int is_nan = (((r64 >> 52) & 0x7ffu) == 0x7ffu)
                     && ((r64 & UINT64_C(0xfffffffffffff)) != 0u);
        int invalid = msf_test_flags(&flags, MSF_FLAG_INVALID);
        int inexact = msf_test_flags(&flags, MSF_FLAG_INEXACT);
        expect(is_nan);
        expect(invalid == 1);
        expect(inexact == 0);
        expect(flags == MSF_FLAG_INVALID);
        expect(r64 == UINT64_C(0x7ff8000000000000));
        printf("f64 div 0/0 TE bits=%016llx flags=%02x invalid=%d inexact=%d\n",
               (unsigned long long)r64, (unsigned)flags, invalid,
               inexact);
    }

    if (g_failures == 0) {
        printf("EXAMPLE PASS\n");
    } else {
        printf("EXAMPLE FAIL failures=%d\n", g_failures);
    }
}

int main(void)
{
    pico_unique_board_id_t id;
    int i;

    stdio_init_all();
    while (!stdio_usb_connected()) {
        sleep_ms(50);
    }
    sleep_ms(200);
    pico_get_unique_board_id(&id);
    printf("MSF-EXAMPLE 1 ID ");
    for (i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
        printf("%02x", id.id[i]);
    }
    printf("\n");

    run_example();

    printf("EXAMPLE-RESULT %s failures=%d\n",
           g_failures == 0 ? "PASS" : "FAIL", g_failures);
    for (;;) {
        sleep_ms(1000);
    }
}
