/* bench_main.c - measured bench record set (SF-0 Section 6 item 9,
 * post-seal parcel-psbench; stock-SDK baseline rows added by
 * parcel-psbench2).
 *
 * Placement/clock-labelled cycle and size records for a representative
 * operation matrix plus the SDK-harness baselines (bootrom via the
 * default pico flavour, libgcc via the compiler flavour, chosen at
 * build time by MSF_BENCH_FLAVOUR). These are measurement records
 * only: no performance claim is made from these numbers (SF-0
 * Sections 5.1, 8). Cortex-M0+ has no cycle counter; cycles are
 * derived from the microsecond timer and the measured system clock.
 *
 * Method (labelled in the log, restated in docs/BENCH.md):
 * - Operands come from an in-code LCG (multiplier 1664525, increment
 *   1013904223) seeded per row from BENCH_LCG_SEED; the seed is reset
 *   every repetition, so every repetition of a row sees the same
 *   operand sequence and must print the same row sink. Mantissas are
 *   fully varying; exponents are confined to a mid normal range per
 *   format so divisors are never zero and the transcendental rows
 *   stay on their ordinary finite paths.
 * - Each row runs BENCH_REPS repetitions; every repetition prints a
 *   BENCH-REP line (raw total_us, iters, sink) and each row ends with
 *   a BENCH summary line carrying the median and min/max spread of
 *   cycles/op over the repetitions. The empty-loop row measures the
 *   loop+LCG+sink overhead the same way; it is reported, never
 *   subtracted. A short discarded warm-up per row fills the XIP
 *   cache before repetition 0.
 * - Iteration counts are fixed per row (identical in both SDK
 *   flavours, which is what makes the msf sinks comparable across
 *   flavours) and scaled so each repetition takes at least 0.2 s.
 * - The four P0 exemplar rows and the two SDK baseline rows are
 *   retained under their original names; the exemplars now also draw
 *   operands from the common LCG, and the SDK rows keep their
 *   original volatile accumulator bodies (reset per repetition).
 * - The sdk32_/sdk64_ baseline rows (parcel-psbench2) run the stock
 *   SDK float/double routines (native operators, fmaf/fma,
 *   sqrtf/sqrt, casts - whatever the build flavour routes them to)
 *   in the same loop-body shape as the library rows: operands are
 *   regenerated from the same LCG on every iteration (same per-row
 *   seeding and exponent ranges as the matching library rows) and
 *   result bit patterns accumulate into the printed 64-bit row
 *   sink. They are labelled baseline rows recorded under the same
 *   labels; no ranking is made from them.
 */
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "hardware/clocks.h"
#include "../include/muse_softfloat.h"
#include "../src/msf_internal.h"
#include "msf_led.h"

#ifndef MSF_FLAVOUR_NAME
#define MSF_FLAVOUR_NAME "pico(default: ROM-routed)"
#endif

#define BENCH_REPS 5
#define BENCH_LCG_SEED 0x2545F491u
#define BENCH_WARMUP_ITERS 32u

static uint32_t g_hz = 0;
static uint64_t g_msf_sink = 0;
static uint64_t g_sdk_sink = 0;
static volatile uint64_t g_warm_sink = 0;
static int g_row_index = 0;

static uint32_t lcg_next(uint32_t *s)
{
    *s = *s * 1664525u + 1013904223u;
    return *s;
}

/* Mid-range normal operands: exponents binary16 8..22, binary32
 * 110..145, binary64 1000..1047 (never zero, infinite or NaN). */
static msf16_t gen16(uint32_t *s, int positive)
{
    uint32_t r = lcg_next(s);
    uint32_t sign = positive ? 0u : (r >> 31);
    uint32_t exp = 8u + ((r >> 16) % 15u);
    uint32_t mant = (r >> 4) & 0x3FFu;
    return (msf16_t)((sign << 15) | (exp << 10) | mant);
}

static msf32_t gen32(uint32_t *s, int positive)
{
    uint32_t r = lcg_next(s);
    uint32_t m = lcg_next(s);
    uint32_t sign = positive ? 0u : (r >> 31);
    uint32_t exp = 110u + ((r >> 16) % 36u);
    return (sign << 31) | (exp << 23) | (m >> 9);
}

static msf64_t gen64(uint32_t *s, int positive)
{
    uint32_t r = lcg_next(s);
    uint32_t m1 = lcg_next(s);
    uint32_t m2 = lcg_next(s);
    uint64_t sign = positive ? 0u : (uint64_t)(r >> 31);
    uint64_t exp = 1000u + ((r >> 16) % 48u);
    uint64_t mant = (((uint64_t)m1 << 20) | (m2 >> 12)) & 0xFFFFFFFFFFFFFULL;
    return (sign << 63) | (exp << 52) | mant;
}

/* Near-unity operands for exp2/log2/sinPi: signed sweep about
 * 2^-2..2^2, or positive-only 2^-1..2^3 for log2. */
static msf32_t gen32_small(uint32_t *s)
{
    uint32_t r = lcg_next(s);
    uint32_t m = lcg_next(s);
    return ((r >> 31) << 31) | ((125u + ((r >> 16) % 5u)) << 23) | (m >> 9);
}

static msf32_t gen32_pos(uint32_t *s)
{
    uint32_t r = lcg_next(s);
    uint32_t m = lcg_next(s);
    return ((126u + ((r >> 16) % 4u)) << 23) | (m >> 9);
}

static msf64_t gen64_small(uint32_t *s)
{
    uint32_t r = lcg_next(s);
    uint32_t m1 = lcg_next(s);
    uint32_t m2 = lcg_next(s);
    uint64_t mant = (((uint64_t)m1 << 20) | (m2 >> 12)) & 0xFFFFFFFFFFFFFULL;
    return ((uint64_t)(r >> 31) << 63)
         | ((uint64_t)(1021u + ((r >> 16) % 5u)) << 52) | mant;
}

static msf64_t gen64_pos(uint32_t *s)
{
    uint32_t r = lcg_next(s);
    uint32_t m1 = lcg_next(s);
    uint32_t m2 = lcg_next(s);
    uint64_t mant = (((uint64_t)m1 << 20) | (m2 >> 12)) & 0xFFFFFFFFFFFFFULL;
    return ((uint64_t)(1022u + ((r >> 16) % 4u)) << 52) | mant;
}

/* Bitcasts between the library's raw patterns and native float/
 * double, for the stock-SDK baseline rows: the same generated bit
 * patterns feed the native operations. */
static float f32_of(msf32_t bits)
{
    float f;
    memcpy(&f, &bits, sizeof f);
    return f;
}

static double f64_of(msf64_t bits)
{
    double d;
    memcpy(&d, &bits, sizeof d);
    return d;
}

static uint32_t bits32_of(float f)
{
    uint32_t b;
    memcpy(&b, &f, sizeof b);
    return b;
}

static uint64_t bits64_of(double d)
{
    uint64_t b;
    memcpy(&b, &d, sizeof b);
    return b;
}

static uint64_t cycles_x100(uint64_t us, uint32_t iters)
{
    return (us * (uint64_t)g_hz) / ((uint64_t)iters * 10000u);
}

static void emit_rep(const char *name, int rep, uint32_t iters, uint64_t us,
                     uint64_t sink)
{
    msf_led_busy(); /* after the timed loop, with the printing */
    printf("BENCH-REP name=%s rep=%d iters=%lu total_us=%llu "
           "ns_per_op=%llu cycles_per_op_x100=%llu sink=%016llx\n",
           name, rep, (unsigned long)iters, (unsigned long long)us,
           (unsigned long long)((us * 1000u) / iters),
           (unsigned long long)cycles_x100(us, iters),
           (unsigned long long)sink);
}

static void emit_summary(const char *name, uint32_t iters,
                         const uint64_t *cyc, const uint64_t *us,
                         uint64_t sink)
{
    uint64_t cs[BENCH_REPS], uu[BENCH_REPS];
    for (int i = 0; i < BENCH_REPS; i++) { cs[i] = cyc[i]; uu[i] = us[i]; }
    for (int i = 0; i < BENCH_REPS; i++) {
        for (int j = i + 1; j < BENCH_REPS; j++) {
            if (cs[j] < cs[i]) { uint64_t t = cs[i]; cs[i] = cs[j]; cs[j] = t; }
            if (uu[j] < uu[i]) { uint64_t t = uu[i]; uu[i] = uu[j]; uu[j] = t; }
        }
    }
    printf("BENCH name=%s reps=%d iters=%lu median_total_us=%llu "
           "median_cycles_per_op_x100=%llu min_cycles_per_op_x100=%llu "
           "max_cycles_per_op_x100=%llu sink=%016llx\n",
           name, BENCH_REPS, (unsigned long)iters,
           (unsigned long long)uu[BENCH_REPS / 2],
           (unsigned long long)cs[BENCH_REPS / 2],
           (unsigned long long)cs[0],
           (unsigned long long)cs[BENCH_REPS - 1],
           (unsigned long long)sink);
}

/* One bench row. setup/body/finish see s_ (LCG state), fl_ (flags),
 * rsink_ (row sink) and, in body, i_ (iteration index). finish runs
 * after the timer stops (used by the SDK rows to fold the final
 * accumulator bits into the row sink). */
#define BENCH_ROW(name, iters, is_sdk, setup, body, finish) do { \
    uint64_t cyc_[BENCH_REPS]; \
    uint64_t us_[BENCH_REPS]; \
    uint64_t sink_ = 0; \
    { \
        uint32_t s_ = BENCH_LCG_SEED + (uint32_t)g_row_index * 0x9E3779B9u; \
        msf_flags_t fl_ = 0; \
        uint64_t rsink_ = 0; \
        setup; \
        for (uint32_t i_ = 0; i_ < BENCH_WARMUP_ITERS; i_++) { body; } \
        finish; \
        g_warm_sink += rsink_ + (uint64_t)fl_; \
    } \
    for (int rep_ = 0; rep_ < BENCH_REPS; rep_++) { \
        uint32_t s_ = BENCH_LCG_SEED + (uint32_t)g_row_index * 0x9E3779B9u; \
        msf_flags_t fl_ = 0; \
        uint64_t rsink_ = 0; \
        setup; \
        uint64_t t0_ = time_us_64(); \
        for (uint32_t i_ = 0; i_ < (uint32_t)(iters); i_++) { body; } \
        uint64_t us1_ = time_us_64() - t0_; \
        finish; \
        rsink_ += (uint64_t)fl_; \
        sink_ = rsink_; \
        us_[rep_] = us1_; \
        cyc_[rep_] = cycles_x100(us1_, (uint32_t)(iters)); \
        emit_rep(name, rep_, (uint32_t)(iters), us1_, rsink_); \
    } \
    emit_summary(name, (uint32_t)(iters), cyc_, us_, sink_); \
    if (is_sdk) { g_sdk_sink += sink_; } else { g_msf_sink += sink_; } \
    g_row_index++; \
} while (0)

#define NOP_SETUP ((void)0)
#define NOP_FINISH ((void)0)
#define RNE MSF_ROUND_TIES_TO_EVEN

int main(void)
{
    pico_unique_board_id_t id;
    msf_u128_t sig = msf_u128_from_u64(0x123456789abcdef0ULL);
    volatile float fa = 1.5f, fb = 2.25f;
    volatile double da = 1.5, db = 2.25;

    stdio_init_all();
    msf_led_init();
    while (!stdio_usb_connected()) {
        sleep_ms(50);
    }
    sleep_ms(200);
    g_hz = clock_get_hz(clk_sys);
    pico_get_unique_board_id(&id);
    printf("MSF-BENCH 1 ID ");
    for (int i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
        printf("%02x", id.id[i]);
    }
    printf(" flavour=%s clk_sys_hz=%lu placement=flash(xip,cached) clock=default\n",
           MSF_FLAVOUR_NAME, (unsigned long)g_hz);
    printf("BENCH-META reps=%d lcg_seed=0x%08lx lcg=1664525/1013904223 "
           "rounding=ties_to_even timer=time_us_64 warmup_iters=%lu "
           "compiler=%s\n",
           BENCH_REPS, (unsigned long)BENCH_LCG_SEED,
           (unsigned long)BENCH_WARMUP_ITERS, __VERSION__);
    printf("note: measured records only - no performance claim (SF-0 6 item 9)\n");

    /* Overhead reference row: loop + LCG + sink only. */
    BENCH_ROW("empty_loop", 2400000u, 0, NOP_SETUP,
              rsink_ += lcg_next(&s_), NOP_FINISH);

    /* binary16 arithmetic */
    BENCH_ROW("msf16_add", 10000u, 0, NOP_SETUP,
              rsink_ += msf16_add(gen16(&s_, 0), gen16(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf16_mul", 16000u, 0, NOP_SETUP,
              rsink_ += msf16_mul(gen16(&s_, 0), gen16(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf16_fma", 9000u, 0, NOP_SETUP,
              rsink_ += msf16_fma(gen16(&s_, 0), gen16(&s_, 0), gen16(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf16_div", 650u, 0, NOP_SETUP,
              rsink_ += msf16_div(gen16(&s_, 0), gen16(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf16_sqrt", 1400u, 0, NOP_SETUP,
              rsink_ += msf16_sqrt(gen16(&s_, 1), RNE, &fl_), NOP_FINISH);

    /* binary32 arithmetic */
    BENCH_ROW("msf32_add", 9000u, 0, NOP_SETUP,
              rsink_ += msf32_add(gen32(&s_, 0), gen32(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf32_mul", 16000u, 0, NOP_SETUP,
              rsink_ += msf32_mul(gen32(&s_, 0), gen32(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf32_fma", 3200u, 0, NOP_SETUP,
              rsink_ += msf32_fma(gen32(&s_, 0), gen32(&s_, 0), gen32(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf32_div", 650u, 0, NOP_SETUP,
              rsink_ += msf32_div(gen32(&s_, 0), gen32(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf32_sqrt", 1400u, 0, NOP_SETUP,
              rsink_ += msf32_sqrt(gen32(&s_, 1), RNE, &fl_), NOP_FINISH);

    /* binary64 arithmetic */
    BENCH_ROW("msf64_add", 12000u, 0, NOP_SETUP,
              rsink_ += msf64_add(gen64(&s_, 0), gen64(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf64_mul", 15000u, 0, NOP_SETUP,
              rsink_ += msf64_mul(gen64(&s_, 0), gen64(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf64_fma", 9000u, 0, NOP_SETUP,
              rsink_ += msf64_fma(gen64(&s_, 0), gen64(&s_, 0), gen64(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf64_div", 550u, 0, NOP_SETUP,
              rsink_ += msf64_div(gen64(&s_, 0), gen64(&s_, 0), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf64_sqrt", 1400u, 0, NOP_SETUP,
              rsink_ += msf64_sqrt(gen64(&s_, 1), RNE, &fl_), NOP_FINISH);

    /* Recommended-math rows (Clause 9.2), binary32 + binary64 */
    BENCH_ROW("msf32_exp2", 220u, 0, NOP_SETUP,
              rsink_ += msf32_exp2(gen32_small(&s_), RNE, &fl_), NOP_FINISH);
    BENCH_ROW("msf32_log2", 150u, 0, NOP_SETUP,
              rsink_ += msf32_log2(gen32_pos(&s_), RNE, &fl_), NOP_FINISH);
    BENCH_ROW("msf32_sin_pi", 340u, 0, NOP_SETUP,
              rsink_ += msf32_sin_pi(gen32_small(&s_), RNE, &fl_), NOP_FINISH);
    BENCH_ROW("msf64_exp2", 210u, 0, NOP_SETUP,
              rsink_ += msf64_exp2(gen64_small(&s_), RNE, &fl_), NOP_FINISH);
    BENCH_ROW("msf64_log2", 150u, 0, NOP_SETUP,
              rsink_ += msf64_log2(gen64_pos(&s_), RNE, &fl_), NOP_FINISH);
    BENCH_ROW("msf64_sin_pi", 330u, 0, NOP_SETUP,
              rsink_ += msf64_sin_pi(gen64_small(&s_), RNE, &fl_), NOP_FINISH);

    /* Conversion rows: from int, to int, format to format */
    BENCH_ROW("msf32_from_i32", 37000u, 0, NOP_SETUP,
              rsink_ += msf32_from_i32((int32_t)lcg_next(&s_), RNE, &fl_),
              NOP_FINISH);
    BENCH_ROW("msf64_to_i32_ties_to_even", 28000u, 0, NOP_SETUP,
              rsink_ += (uint64_t)(uint32_t)msf64_to_i32_ties_to_even(gen64(&s_, 0), &fl_),
              NOP_FINISH);
    BENCH_ROW("msf32_from_f64", 28000u, 0, NOP_SETUP,
              rsink_ += msf32_from_f64(gen64(&s_, 0), RNE, &fl_), NOP_FINISH);

    /* Retained P0 exemplar rows (original names; LCG operands) */
    BENCH_ROW("msf16_class", 750000u, 0, NOP_SETUP,
              rsink_ += (uint64_t)msf16_class((msf16_t)lcg_next(&s_)),
              NOP_FINISH);
    BENCH_ROW("msf32_is_signaling", 1000000u, 0, NOP_SETUP,
              rsink_ += (uint64_t)msf32_is_signaling(lcg_next(&s_)),
              NOP_FINISH);
    BENCH_ROW("msf64_copy_sign", 250000u, 0, NOP_SETUP,
              rsink_ += msf64_copy_sign(gen64(&s_, 0), gen64(&s_, 0)),
              NOP_FINISH);
    BENCH_ROW("msf_pack_f64(exemplar)", 47000u, 0, NOP_SETUP, {
        msf_flags_t pfl_ = 0;
        rsink_ += msf_pack_f64(0, -60 + (int32_t)(lcg_next(&s_) & 127u), sig, 1,
                               MSF_IROUND_TIES_TO_EVEN, &pfl_);
        rsink_ += pfl_;
    }, NOP_FINISH);

    /* Stock-SDK baseline rows (parcel-psbench2): native float/double
     * operations in the same loop-body shape as the library rows -
     * operands regenerated from the same LCG every iteration (same
     * exponent ranges as the matching library rows; divisors never
     * zero, sqrt operands positive normals, conversion inputs
     * in-range), result bit patterns folded into the row sink.
     * Labelled baseline rows, not a comparison or ranking. */
    BENCH_ROW("sdk32_add", 200000u, 1, NOP_SETUP,
              rsink_ += bits32_of(f32_of(gen32(&s_, 0)) + f32_of(gen32(&s_, 0))),
              NOP_FINISH);
    BENCH_ROW("sdk32_mul", 215000u, 1, NOP_SETUP,
              rsink_ += bits32_of(f32_of(gen32(&s_, 0)) * f32_of(gen32(&s_, 0))),
              NOP_FINISH);
    BENCH_ROW("sdk32_fma", 65000u, 1, NOP_SETUP,
              rsink_ += bits32_of(fmaf(f32_of(gen32(&s_, 0)), f32_of(gen32(&s_, 0)),
                                        f32_of(gen32(&s_, 0)))),
              NOP_FINISH);
    BENCH_ROW("sdk32_div", 195000u, 1, NOP_SETUP,
              rsink_ += bits32_of(f32_of(gen32(&s_, 0)) / f32_of(gen32(&s_, 0))),
              NOP_FINISH);
    BENCH_ROW("sdk32_sqrt", 300000u, 1, NOP_SETUP,
              rsink_ += bits32_of(sqrtf(f32_of(gen32(&s_, 1)))),
              NOP_FINISH);
    BENCH_ROW("sdk64_add", 155000u, 1, NOP_SETUP,
              rsink_ += bits64_of(f64_of(gen64(&s_, 0)) + f64_of(gen64(&s_, 0))),
              NOP_FINISH);
    BENCH_ROW("sdk64_mul", 125000u, 1, NOP_SETUP,
              rsink_ += bits64_of(f64_of(gen64(&s_, 0)) * f64_of(gen64(&s_, 0))),
              NOP_FINISH);
    BENCH_ROW("sdk64_fma", 75000u, 1, NOP_SETUP,
              rsink_ += bits64_of(fma(f64_of(gen64(&s_, 0)), f64_of(gen64(&s_, 0)),
                                       f64_of(gen64(&s_, 0)))),
              NOP_FINISH);
    BENCH_ROW("sdk64_div", 110000u, 1, NOP_SETUP,
              rsink_ += bits64_of(f64_of(gen64(&s_, 0)) / f64_of(gen64(&s_, 0))),
              NOP_FINISH);
    BENCH_ROW("sdk64_sqrt", 150000u, 1, NOP_SETUP,
              rsink_ += bits64_of(sqrt(f64_of(gen64(&s_, 1)))),
              NOP_FINISH);
    BENCH_ROW("sdk32_from_i32", 560000u, 1, NOP_SETUP,
              rsink_ += bits32_of((float)(int32_t)lcg_next(&s_)),
              NOP_FINISH);
    BENCH_ROW("sdk64_to_i32", 340000u, 1, NOP_SETUP,
              rsink_ += (uint64_t)(uint32_t)(int32_t)f64_of(gen64(&s_, 0)),
              NOP_FINISH);
    BENCH_ROW("sdk32_from_f64", 305000u, 1, NOP_SETUP,
              rsink_ += bits32_of((float)f64_of(gen64(&s_, 0))),
              NOP_FINISH);

    /* Retained SDK-flavour baselines: original volatile bodies; the
     * accumulator is reset per repetition and its final bits form
     * the row sink. Labelled baseline rows, not a comparison. */
    BENCH_ROW("sdk-flavour float add (baseline)", 400000u, 1,
              fa = 1.5f,
              fa = fa + fb, {
        float tf_ = fa;
        uint32_t bits_ = 0;
        memcpy(&bits_, &tf_, sizeof bits_);
        rsink_ += bits_;
    });
    BENCH_ROW("sdk-flavour double add (baseline)", 300000u, 1,
              da = 1.5,
              da = da + db, {
        double td_ = da;
        uint64_t bits_ = 0;
        memcpy(&bits_, &td_, sizeof bits_);
        rsink_ += bits_;
    });

    printf("BENCH-DONE msf_sink=%016llx sdk_sink=%016llx rows=%d\n",
           (unsigned long long)g_msf_sink, (unsigned long long)g_sdk_sink,
           g_row_index);
    msf_led_idle();
    for (;;) {
        sleep_ms(1000);
    }
}
