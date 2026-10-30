/* interval_workload.h - Step 1c guaranteed interval geometry.
 *
 * Board-portable original C over the public muse_softfloat API
 * only. No hardware floating arithmetic type is named, there is
 * no allocation, and every scalar operation is a library call
 * whose rounding direction is explicit. Claims are containment
 * claims: every ray returns HIT, MISS, or UNCERTAIN, never a
 * silently wrong sign.
 *
 * Endpoint convention (frozen before any board hash exists):
 * every interval endpoint selection goes through the library
 * minimum/maximum rows (754-2019 9.6 propagating forms), so NaN
 * and signed-zero endpoint bits are library-owned and identical
 * on host and board. The suppressing forms of 9.6 are banned
 * from this core; a source scan is a gate.
 *
 * The axis-parallel slab case in the box test is explicit
 * workload branch logic. Clause 9.6 does not fix it.
 *
 * IW_RM_LO / IW_RM_HI / IW_STAGE3_GUARD exist only as
 * negative-control hooks (project precedent: the tininess mutant
 * in tools/run.sh); their defaults are the correct behaviour and
 * mutant builds are watched failing in scratch, never shipped.
 */
#ifndef MSF_INTERVAL_WORKLOAD_H
#define MSF_INTERVAL_WORKLOAD_H

#include <stdint.h>
#include "../include/muse_softfloat.h"

typedef enum iw_class {
    IW_UNCERTAIN = 0,
    IW_HIT = 1,
    IW_MISS = 2
} iw_class_t;

/* Stage 3 expansion capacities. The discriminant term list is
 * bounded by construction (pairs of distilled dot expansions);
 * exceeding a capacity yields UNCERTAIN, never a truncated sign. */
#define IW_MAX_SMALL_TERMS 64
#define IW_MAX_TERMS 1024

/* Caller-owned context: scratch term arrays plus the scalar op
 * counter (every library call in the core increments it). One
 * context per concurrent ray stream; no other state exists. */
typedef struct iw_ctx {
    uint64_t ops;
    msf64_t terms[IW_MAX_TERMS];
    msf64_t terms_a[IW_MAX_SMALL_TERMS];
    msf64_t terms_b[IW_MAX_SMALL_TERMS];
    msf64_t terms_c[IW_MAX_SMALL_TERMS];
} iw_ctx_t;

void iw_ctx_init(iw_ctx_t *ctx);

/* Ray-sphere discriminant classification. Inputs are binary64
 * bit patterns (binary32-origin rays store the exact widening).
 * Exact discriminant >= 0 is HIT (a tangent ray touches). Each
 * stage is a full independent evaluation so the frozen host hash
 * does not depend on short-circuit policy; the board runner
 * replays the same sequence. ops_out counts library calls. */
iw_class_t iw_sphere_stage1_f32(iw_ctx_t *ctx,
                                const msf64_t O[3], const msf64_t D[3],
                                const msf64_t C[3], msf64_t r,
                                msf32_t *lo_out, msf32_t *hi_out,
                                uint64_t *ops_out);
iw_class_t iw_sphere_stage2_f64(iw_ctx_t *ctx,
                                const msf64_t O[3], const msf64_t D[3],
                                const msf64_t C[3], msf64_t r,
                                msf64_t *lo_out, msf64_t *hi_out,
                                uint64_t *ops_out);
/* Exact sign by error-free expansion over binary64 built from
 * the Clause 9.5 augmented pairs, guarded by a fresh flags word:
 * any inexact pair (overflowed head, unrepresentable mul
 * residual), invalid, or non-finite pair yields UNCERTAIN, never
 * a sign. An exact tiny residual is an exact expansion term. */
iw_class_t iw_sphere_stage3_exact(iw_ctx_t *ctx,
                                  const msf64_t O[3], const msf64_t D[3],
                                  const msf64_t C[3], msf64_t r,
                                  uint64_t *ops_out);

/* Ray-box slab test, binary64. An outer t-interval (directed
 * outward) proves MISS when empty; an inward-rounded t-interval
 * proves HIT when nonempty; otherwise UNCERTAIN. tmin/tmax_out
 * receive the outer interval endpoints. D_i == 0 axes are
 * explicit branch logic on exact comparisons. */
iw_class_t iw_box(iw_ctx_t *ctx,
                  const msf64_t O[3], const msf64_t D[3],
                  const msf64_t loB[3], const msf64_t hiB[3],
                  msf64_t *tmin_out, msf64_t *tmax_out,
                  uint64_t *ops_out);

/* Torus (R = 2, r = 1/2, frozen bit patterns) first-hit
 * bracketing over t in [0, 11]: interval evaluation of the
 * implicit quartic over segments, dyadic bisection in t order
 * to the tolerance, per-ray op cap (cap hit -> UNCERTAIN). HIT
 * requires proven-OUT segments chained from t = 0, then a point
 * whose point interval is entirely negative; the bracket is
 * [first not-proven-OUT segment lo, that point]. */
#define IW_TORUS_TOL_BITS ((msf64_t)0x3F50000000000000ULL) /* 2^-10 */
typedef struct iw_torus_result {
    iw_class_t cls;
    msf64_t br_lo;
    msf64_t br_hi;
    uint64_t ops;
    uint64_t evals;
    uint32_t max_depth;
    int cap_hit;
} iw_torus_result_t;

void iw_torus_first_hit(iw_ctx_t *ctx,
                        const msf64_t O[3], const msf64_t D[3],
                        msf64_t tol_bits, uint64_t op_cap,
                        iw_torus_result_t *res);

#endif /* MSF_INTERVAL_WORKLOAD_H */
