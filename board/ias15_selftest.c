/* ias15_selftest.c - board AEABI contract checks (see header).
 *
 * Operand set, check shapes and the commutative-NaN-payload rule are
 * the host proof's (scratch/ias15/work/shim_selftest.c, 346,901
 * checks on x86-64): 24 directed bit patterns covering zeros,
 * subnormals, min/max normals, infinities, qNaN/sNaN payloads and
 * halfway cases; all pairs for arithmetic and every branch
 * predicate; the IAS15-shaped compounds (isnormal guard, Kahan
 * add_cs replay, Horner chain); conversions both ways. No decimal
 * literal defines an operand (the 7.0 in the chain replay is matched
 * on the core side by its own bit pattern, as on the host).
 *
 * This TU is a CONSUMER of the helpers under test: it uses ordinary
 * C double arithmetic, which the target wraps route to
 * compat/msf_aeabi.c. Do not compile it into the compat layer.
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "../compat/msf_wrap.h"
#include "../include/muse_softfloat.h"
#include "ias15_selftest.h"

/* C23 names, wrapped to compat/msf_aeabi.c (Step 2c); declared here
 * because neither newlib nor host MinGW math.h declares them under
 * the build's -std flags. An identical redeclaration is legal. */
double sinpi(double x);
double cospi(double x);

#ifndef IAS15_SELFTEST_LCG_PAIRS
#define IAS15_SELFTEST_LCG_PAIRS 2000
#endif

static uint64_t d2u(double v) { uint64_t u; memcpy(&u, &v, 8); return u; }
static double u2d(uint64_t u) { double v; memcpy(&v, &u, 8); return v; }
static int isnan_bits(uint64_t u)
{
    return ((u >> 52) & 0x7FFu) == 0x7FFu && (u & 0xFFFFFFFFFFFFFULL) != 0;
}

static const uint64_t OPS[] = {
    0x0000000000000000ULL, 0x8000000000000000ULL,
    0x0000000000000001ULL, 0x8000000000000001ULL,
    0x000FFFFFFFFFFFFFULL, 0x0010000000000000ULL,
    0x3FF0000000000000ULL, 0xBFF0000000000000ULL,
    0x4000000000000000ULL, 0x3FE0000000000000ULL,
    0x3FF0000000000001ULL, 0x3FEFFFFFFFFFFFFFULL,
    0x7FEFFFFFFFFFFFFFULL, 0xFFEFFFFFFFFFFFFFULL,
    0x7FF0000000000000ULL, 0xFFF0000000000000ULL,
    0x7FF8000000000000ULL, 0xFFF8000000001234ULL,
    0x7FF0000000000001ULL, 0x3F847AE147AE147BULL,
    0x3E45798EE2308C3AULL, 0x4330000000000000ULL,
    0x4340000000000000ULL, 0x0008000000000000ULL,
};
#define NOPS (sizeof OPS / sizeof OPS[0])

static unsigned long long g_checks, g_fails, g_nan;

static void check_bits(const char *what, uint64_t got, uint64_t want)
{
    g_checks++;
    if (got == want) {
        return;
    }
    if (isnan_bits(got) && isnan_bits(want)) {
        if (g_nan < 10) {
            printf("NANDIFF %s got=%016llx want=%016llx\n", what,
                   (unsigned long long)got, (unsigned long long)want);
        }
        g_nan++;
        return;
    }
    if (g_fails < 10) {
        printf("FAIL %s got=%016llx want=%016llx\n", what,
               (unsigned long long)got, (unsigned long long)want);
    }
    g_fails++;
}

static void check_int(const char *what, long long got, long long want)
{
    g_checks++;
    if (got != want) {
        if (g_fails < 10) {
            printf("FAIL %s got=%lld want=%lld\n", what, got, want);
        }
        g_fails++;
    }
}

#define RM MSF_ROUND_TIES_TO_EVEN

static void pair_checks(uint64_t ua, uint64_t ub)
{
    msf_flags_t fl = 0;
    volatile double va = u2d(ua), vb = u2d(ub);
    double a = va, b = vb, r;
    r = a + b;
    {
        uint64_t fwd = msf64_add(ua, ub, RM, &fl);
        uint64_t rev = msf64_add(ub, ua, RM, &fl);
        check_bits("add", d2u(r), (d2u(r) == rev && rev != fwd) ? rev : fwd);
    }
    r = a - b;
    check_bits("sub", d2u(r), msf64_sub(ua, ub, RM, &fl));
    r = a * b;
    {
        uint64_t fwd = msf64_mul(ua, ub, RM, &fl);
        uint64_t rev = msf64_mul(ub, ua, RM, &fl);
        check_bits("mul", d2u(r), (d2u(r) == rev && rev != fwd) ? rev : fwd);
    }
    r = a / b;
    check_bits("div", d2u(r), msf64_div(ua, ub, RM, &fl));
    check_int("lt", (a < b) ? 1 : 0, msf64_compare_quiet_less(ua, ub, &fl));
    check_int("gt", (a > b) ? 1 : 0, msf64_compare_quiet_greater(ua, ub, &fl));
    check_int("eq", (a == b) ? 1 : 0, msf64_compare_quiet_equal(ua, ub, &fl));
    {
        int le = msf64_compare_quiet_less_equal(ua, ub, &fl);
        int ge = msf64_compare_quiet_greater_equal(ua, ub, &fl);
        int ne = !msf64_compare_quiet_equal(ua, ub, &fl);
        check_int("le", (a <= b) ? 1 : 0, le);
        check_int("ge", (a >= b) ? 1 : 0, ge);
        check_int("ne", (a != b) ? 1 : 0, ne);
        check_int("nlt", (!(a < b)) ? 1 : 0,
                  !msf64_compare_quiet_less(ua, ub, &fl));
        check_int("nge", (!(a >= b)) ? 1 : 0, !ge);
    }
    check_int("guard-max", (isnormal(a) && a > b) ? 1 : 0,
              (msf64_is_normal(ua)
               && msf64_compare_quiet_greater(ua, ub, &fl)) ? 1 : 0);
    check_int("uno", __builtin_isunordered(a, b) ? 1 : 0,
              (msf64_is_nan(ua) || msf64_is_nan(ub)) ? 1 : 0);
    check_bits("copysign", d2u(copysign(a, b)),
               msf64_copy_sign(ua, ub));
    {
        double p = a;
        double y = b - u2d(0x3E45798EE2308C3AULL);
        double t = p + y;
        double cs2v = (t - p) - y;
        uint64_t uy = msf64_sub(ub, 0x3E45798EE2308C3AULL, RM, &fl);
        uint64_t ut = msf64_add(ua, uy, RM, &fl);
        uint64_t ucs = msf64_sub(msf64_sub(ut, ua, RM, &fl), uy, RM, &fl);
        check_bits("kahan-t", d2u(t), ut);
        check_bits("kahan-cs", d2u(cs2v), ucs);
    }
}

static void single_checks(uint64_t ua)
{
    msf_flags_t fl = 0;
    volatile double va = u2d(ua);
    double a = va;
    check_bits("sqrt", d2u(sqrt(a)), msf64_sqrt(ua, RM, &fl));
    check_bits("sinpi", d2u(sinpi(a)), msf64_sin_pi(ua, RM, &fl));
    check_bits("cospi", d2u(cospi(a)), msf64_cos_pi(ua, RM, &fl));
    check_bits("floor", d2u(floor(a)),
               msf64_round_to_integral_toward_negative(ua, &fl));
    check_bits("fabs", d2u(fabs(a)), msf64_abs(ua));
    check_bits("neg", d2u(-a), msf64_negate(ua));
    check_int("isnormal", isnormal(a) ? 1 : 0, msf64_is_normal(ua) ? 1 : 0);
    {
        double x = a * a * a - a / 7.0;
        uint64_t u = msf64_mul(ua, ua, RM, &fl);
        u = msf64_mul(u, ua, RM, &fl);
        u = msf64_sub(u, msf64_div(ua, d2u(7.0), RM, &fl), RM, &fl);
        check_bits("chain", d2u(x), u);
    }
    check_int("to-i32", (int)a, msf64_to_i32_toward_zero(ua, &fl));
    check_int("to-u32", (long long)(unsigned int)a,
              (long long)msf64_to_u32_toward_zero(ua, &fl));
    check_int("to-i64", (long long)a, msf64_to_i64_toward_zero(ua, &fl));
    check_bits("to-u64", (unsigned long long)a,
               msf64_to_u64_toward_zero(ua, &fl));
    {
        double d = (double)(float)a;
        check_bits("d2f2d", d2u(d),
                   msf64_from_f32(msf32_from_f64(ua, RM, &fl), RM, &fl));
        float f = (float)a;
        uint32_t fu;
        memcpy(&fu, &f, 4);
        check_bits("d2f", fu, msf32_from_f64(ua, RM, &fl));
        check_bits("f2d", d2u((double)f), msf64_from_f32(fu, RM, &fl));
    }
}

/* Bit+flag checks for the three Step 2c wrappers. The wrapper state
 * flags are zeroed before each wrapped call and must equal the
 * flags the core call raises from zero. Cycle points are exact bit
 * patterns: 0, +-1/4, +-1/2, +-1, +-2, +-2^52, min subnormal, and a
 * few non-dyadic patterns, plus the directed OPS set. */
static void trig_floor_flag_checks(void)
{
    static const uint64_t pts[] = {
        0x0000000000000000ULL, 0x8000000000000000ULL,
        0x3FD0000000000000ULL, 0xBFD0000000000000ULL, /* +-1/4 */
        0x3FE0000000000000ULL, 0xBFE0000000000000ULL, /* +-1/2 */
        0x3FF0000000000000ULL, 0xBFF0000000000000ULL, /* +-1 */
        0x4000000000000000ULL, 0xC000000000000000ULL, /* +-2 */
        0x4330000000000000ULL, 0xC330000000000000ULL, /* +-2^52 */
        0x0000000000000001ULL, 0x8000000000000001ULL,
        0x3F847AE147AE147BULL, 0xBF847AE147AE147BULL, /* +-0.01-ish */
        0x400921FB54442D18ULL, 0xC00921FB54442D18ULL, /* +-pi bits */
    };
    msf_wrap_state_t *s = msf_wrap_state();
    size_t i, n = sizeof pts / sizeof pts[0] + NOPS;
    for (i = 0; i < n; i++) {
        uint64_t ua = i < sizeof pts / sizeof pts[0]
                          ? pts[i]
                          : OPS[i - sizeof pts / sizeof pts[0]];
        volatile double va = u2d(ua);
        double a = va, r;
        msf_flags_t cf = 0;
        uint64_t want;

        want = msf64_sin_pi(ua, RM, &cf);
        s->flags = 0;
        r = sinpi(a);
        check_bits("sinpi-fl", d2u(r), want);
        check_int("sinpi-flags", (long long)s->flags, (long long)cf);

        cf = 0;
        want = msf64_cos_pi(ua, RM, &cf);
        s->flags = 0;
        r = cospi(a);
        check_bits("cospi-fl", d2u(r), want);
        check_int("cospi-flags", (long long)s->flags, (long long)cf);

        cf = 0;
        want = msf64_round_to_integral_toward_negative(ua, &cf);
        s->flags = 0;
        r = floor(a);
        check_bits("floor-fl", d2u(r), want);
        check_int("floor-flags", (long long)s->flags, (long long)cf);
    }
}

int msf_aeabi_selftest(int full,
                       unsigned long long *checks_out,
                       unsigned long long *fails_out)
{
    msf_flags_t fl = 0;
    size_t i, j;
    static const int32_t iv[] = {0, 1, -1, 7, -7, 1000000, -1000000,
                                 2147483647, -2147483647 - 1,
                                 16777217, 16777215};
    static const int64_t lv[] = {0, 1, -1, 9007199254740993LL,
                                 -9007199254740993LL,
                                 9223372036854775807LL};
    static const uint64_t uv[] = {0, 1, 20, 9007199254740993ULL,
                                  18014398509481984ULL,
                                  18446744073709551615ULL};
    static const uint32_t u32v[] = {0, 1, 16777217u, 4294967295u};

    g_checks = 0;
    g_fails = 0;
    g_nan = 0;
    /* The checks compare against ties-to-even core results; make the
     * per-core wrapper state match for the duration, then restore. */
    {
        msf_wrap_state_t *s = msf_wrap_state();
        msf_rounding_t saved_rm = s->rounding;
        msf_flags_t saved_fl = s->flags;
        s->rounding = MSF_ROUND_TIES_TO_EVEN;

        trig_floor_flag_checks();
        for (i = 0; i < NOPS; i++) {
            single_checks(OPS[i]);
            for (j = 0; j < NOPS; j++) {
                pair_checks(OPS[i], OPS[j]);
            }
        }
        for (i = 0; i < sizeof iv / sizeof iv[0]; i++) {
            volatile int32_t v = iv[i];
            check_bits("from-i32", d2u((double)v),
                       msf64_from_i32(iv[i], RM, &fl));
        }
        for (i = 0; i < sizeof lv / sizeof lv[0]; i++) {
            volatile int64_t v = lv[i];
            check_bits("from-i64", d2u((double)v),
                       msf64_from_i64(lv[i], RM, &fl));
        }
        for (i = 0; i < sizeof uv / sizeof uv[0]; i++) {
            volatile uint64_t v = uv[i];
            check_bits("from-u64", d2u((double)v),
                       msf64_from_u64(uv[i], RM, &fl));
        }
        for (i = 0; i < sizeof u32v / sizeof u32v[0]; i++) {
            volatile uint32_t v = u32v[i];
            check_bits("from-u32", d2u((double)v),
                       msf64_from_u32(u32v[i], RM, &fl));
        }
        if (full) {
            uint64_t seed = 0x9E3779B97F4A7C15ULL;
            int k;
            for (k = 0; k < IAS15_SELFTEST_LCG_PAIRS; k++) {
                seed = seed * 6364136223846793005ULL + 1442695040888963407ULL;
                uint64_t ua = seed;
                seed = seed * 6364136223846793005ULL + 1442695040888963407ULL;
                pair_checks(ua, seed);
                if ((k & 7) == 0) {
                    single_checks(ua);
                }
            }
        }
        s->rounding = saved_rm;
        s->flags = saved_fl;
    }
    if (checks_out != NULL) {
        *checks_out = g_checks;
    }
    if (fails_out != NULL) {
        *fails_out = g_fails;
    }
    printf("SELFTEST checks=%llu fails=%llu nan_payload_only=%llu\n",
           g_checks, g_fails, g_nan);
    return (int)g_fails;
}
