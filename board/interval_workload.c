/* interval_workload.c - see interval_workload.h. Original code;
 * interval operations are built here from directed scalar calls,
 * the exact stage from Clause 9.5 augmented pairs consumed as
 * error-free transformations, with a flags guard re-derived for
 * augmented semantics (ledger/parcel-w6augint.md). */
#include "interval_workload.h"

#ifndef IW_RM_LO
#define IW_RM_LO MSF_ROUND_TOWARD_NEGATIVE
#endif
#ifndef IW_RM_HI
#define IW_RM_HI MSF_ROUND_TOWARD_POSITIVE
#endif
#ifndef IW_STAGE3_GUARD
#define IW_STAGE3_GUARD 1
#endif

#define IW_RN MSF_ROUND_TIES_TO_EVEN
#define Z64 ((msf64_t)0)
#define INF64 ((msf64_t)0x7FF0000000000000ULL)
#define HALF64 ((msf64_t)0x3FE0000000000000ULL)
#define Z32 ((msf32_t)0)

void iw_ctx_init(iw_ctx_t *ctx)
{
    ctx->ops = 0;
}

/* ---- counted scalar wrappers (one per library form used) ---- */
static msf64_t a64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_rounding_t rm, msf_flags_t *fl)
{ c->ops++; return msf64_add(x, y, rm, fl); }
static msf64_t s64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_rounding_t rm, msf_flags_t *fl)
{ c->ops++; return msf64_sub(x, y, rm, fl); }
static msf64_t m64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_rounding_t rm, msf_flags_t *fl)
{ c->ops++; return msf64_mul(x, y, rm, fl); }
static msf64_t d64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_rounding_t rm, msf_flags_t *fl)
{ c->ops++; return msf64_div(x, y, rm, fl); }
static msf64_pair_t augadd64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_flags_t *fl)
{ c->ops++; return msf64_augmented_add(x, y, fl); }
static msf64_pair_t augmul64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_flags_t *fl)
{ c->ops++; return msf64_augmented_mul(x, y, fl); }
static msf64_t neg64(iw_ctx_t *c, msf64_t x)
{ c->ops++; return msf64_negate(x); }
static msf64_t abs64(iw_ctx_t *c, msf64_t x)
{ c->ops++; return msf64_abs(x); }
static msf64_t min64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_flags_t *fl)
{ c->ops++; return msf64_minimum(x, y, fl); }
static msf64_t max64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_flags_t *fl)
{ c->ops++; return msf64_maximum(x, y, fl); }
static int gt64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_flags_t *fl)
{ c->ops++; return msf64_compare_quiet_greater(x, y, fl); }
static int lt64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_flags_t *fl)
{ c->ops++; return msf64_compare_quiet_less(x, y, fl); }
static int le64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_flags_t *fl)
{ c->ops++; return msf64_compare_quiet_less_equal(x, y, fl); }
static int ge64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_flags_t *fl)
{ c->ops++; return msf64_compare_quiet_greater_equal(x, y, fl); }
static int eq64(iw_ctx_t *c, msf64_t x, msf64_t y, msf_flags_t *fl)
{ c->ops++; return msf64_compare_quiet_equal(x, y, fl); }

static msf32_t a32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_rounding_t rm, msf_flags_t *fl)
{ c->ops++; return msf32_add(x, y, rm, fl); }
static msf32_t s32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_rounding_t rm, msf_flags_t *fl)
{ c->ops++; return msf32_sub(x, y, rm, fl); }
static msf32_t m32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_rounding_t rm, msf_flags_t *fl)
{ c->ops++; return msf32_mul(x, y, rm, fl); }
static msf32_t min32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_flags_t *fl)
{ c->ops++; return msf32_minimum(x, y, fl); }
static msf32_t max32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_flags_t *fl)
{ c->ops++; return msf32_maximum(x, y, fl); }
static int gt32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_flags_t *fl)
{ c->ops++; return msf32_compare_quiet_greater(x, y, fl); }
static int lt32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_flags_t *fl)
{ c->ops++; return msf32_compare_quiet_less(x, y, fl); }
static int ge32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_flags_t *fl)
{ c->ops++; return msf32_compare_quiet_greater_equal(x, y, fl); }
static int le32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_flags_t *fl)
{ c->ops++; return msf32_compare_quiet_less_equal(x, y, fl); }
static int eq32(iw_ctx_t *c, msf32_t x, msf32_t y, msf_flags_t *fl)
{ c->ops++; return msf32_compare_quiet_equal(x, y, fl); }
static msf32_t cvt32(iw_ctx_t *c, msf64_t x, msf_rounding_t rm, msf_flags_t *fl)
{ c->ops++; return msf32_from_f64(x, rm, fl); }

/* ---- binary64 intervals ---- */
typedef struct { msf64_t lo, hi; } iv64_t;
typedef struct { msf32_t lo, hi; } iv32_t;

static iv64_t pt64(msf64_t v) { iv64_t r; r.lo = v; r.hi = v; return r; }

static iv64_t iadd64(iw_ctx_t *c, iv64_t a, iv64_t b, msf_flags_t *fl)
{
    iv64_t r;
    r.lo = a64(c, a.lo, b.lo, IW_RM_LO, fl);
    r.hi = a64(c, a.hi, b.hi, IW_RM_HI, fl);
    return r;
}

static iv64_t isub64(iw_ctx_t *c, iv64_t a, iv64_t b, msf_flags_t *fl)
{
    iv64_t r;
    r.lo = s64(c, a.lo, b.hi, IW_RM_LO, fl);
    r.hi = s64(c, a.hi, b.lo, IW_RM_HI, fl);
    return r;
}

static iv64_t imul64(iw_ctx_t *c, iv64_t a, iv64_t b, msf_flags_t *fl)
{
    msf64_t ae[2], be[2], lo, hi, p;
    int i, j;
    ae[0] = a.lo; ae[1] = a.hi; be[0] = b.lo; be[1] = b.hi;
    lo = m64(c, ae[0], be[0], IW_RM_LO, fl);
    hi = m64(c, ae[0], be[0], IW_RM_HI, fl);
    for (i = 0; i < 2; i++) {
        for (j = 0; j < 2; j++) {
            if (i == 0 && j == 0) continue;
            p = m64(c, ae[i], be[j], IW_RM_LO, fl);
            lo = min64(c, lo, p, fl);
            p = m64(c, ae[i], be[j], IW_RM_HI, fl);
            hi = max64(c, hi, p, fl);
        }
    }
    { iv64_t r; r.lo = lo; r.hi = hi; return r; }
}

static iv64_t isqr64(iw_ctx_t *c, iv64_t a, msf_flags_t *fl)
{
    iv64_t r;
    if (ge64(c, a.lo, Z64, fl)) {
        r.lo = m64(c, a.lo, a.lo, IW_RM_LO, fl);
        r.hi = m64(c, a.hi, a.hi, IW_RM_HI, fl);
    } else if (le64(c, a.hi, Z64, fl)) {
        r.lo = m64(c, a.hi, a.hi, IW_RM_LO, fl);
        r.hi = m64(c, a.lo, a.lo, IW_RM_HI, fl);
    } else {
        msf64_t p = m64(c, a.lo, a.lo, IW_RM_HI, fl);
        msf64_t q = m64(c, a.hi, a.hi, IW_RM_HI, fl);
        r.lo = Z64;
        r.hi = max64(c, p, q, fl);
    }
    return r;
}

static iv64_t idot64(iw_ctx_t *c, const iv64_t x[3], const iv64_t y[3],
                     msf_flags_t *fl)
{
    iv64_t acc = imul64(c, x[0], y[0], fl);
    acc = iadd64(c, acc, imul64(c, x[1], y[1], fl), fl);
    acc = iadd64(c, acc, imul64(c, x[2], y[2], fl), fl);
    return acc;
}

static iw_class_t decide64(iw_ctx_t *c, iv64_t v, msf_flags_t *fl)
{
    if (gt64(c, v.lo, Z64, fl)) return IW_HIT;
    if (lt64(c, v.hi, Z64, fl)) return IW_MISS;
    if (eq64(c, v.lo, Z64, fl) && eq64(c, v.hi, Z64, fl)) return IW_HIT;
    return IW_UNCERTAIN;
}

/* ---- binary32 intervals ---- */
static iv32_t iadd32(iw_ctx_t *c, iv32_t a, iv32_t b, msf_flags_t *fl)
{
    iv32_t r;
    r.lo = a32(c, a.lo, b.lo, IW_RM_LO, fl);
    r.hi = a32(c, a.hi, b.hi, IW_RM_HI, fl);
    return r;
}

static iv32_t isub32(iw_ctx_t *c, iv32_t a, iv32_t b, msf_flags_t *fl)
{
    iv32_t r;
    r.lo = s32(c, a.lo, b.hi, IW_RM_LO, fl);
    r.hi = s32(c, a.hi, b.lo, IW_RM_HI, fl);
    return r;
}

static iv32_t imul32(iw_ctx_t *c, iv32_t a, iv32_t b, msf_flags_t *fl)
{
    msf32_t ae[2], be[2], lo, hi, p;
    int i, j;
    ae[0] = a.lo; ae[1] = a.hi; be[0] = b.lo; be[1] = b.hi;
    lo = m32(c, ae[0], be[0], IW_RM_LO, fl);
    hi = m32(c, ae[0], be[0], IW_RM_HI, fl);
    for (i = 0; i < 2; i++) {
        for (j = 0; j < 2; j++) {
            if (i == 0 && j == 0) continue;
            p = m32(c, ae[i], be[j], IW_RM_LO, fl);
            lo = min32(c, lo, p, fl);
            p = m32(c, ae[i], be[j], IW_RM_HI, fl);
            hi = max32(c, hi, p, fl);
        }
    }
    { iv32_t r; r.lo = lo; r.hi = hi; return r; }
}

static iv32_t isqr32(iw_ctx_t *c, iv32_t a, msf_flags_t *fl)
{
    iv32_t r;
    if (ge32(c, a.lo, Z32, fl)) {
        r.lo = m32(c, a.lo, a.lo, IW_RM_LO, fl);
        r.hi = m32(c, a.hi, a.hi, IW_RM_HI, fl);
    } else if (le32(c, a.hi, Z32, fl)) {
        r.lo = m32(c, a.hi, a.hi, IW_RM_LO, fl);
        r.hi = m32(c, a.lo, a.lo, IW_RM_HI, fl);
    } else {
        msf32_t p = m32(c, a.lo, a.lo, IW_RM_HI, fl);
        msf32_t q = m32(c, a.hi, a.hi, IW_RM_HI, fl);
        r.lo = Z32;
        r.hi = max32(c, p, q, fl);
    }
    return r;
}

static iv32_t idot32(iw_ctx_t *c, const iv32_t x[3], const iv32_t y[3],
                     msf_flags_t *fl)
{
    iv32_t acc = imul32(c, x[0], y[0], fl);
    acc = iadd32(c, acc, imul32(c, x[1], y[1], fl), fl);
    acc = iadd32(c, acc, imul32(c, x[2], y[2], fl), fl);
    return acc;
}

static iw_class_t decide32(iw_ctx_t *c, iv32_t v, msf_flags_t *fl)
{
    if (gt32(c, v.lo, Z32, fl)) return IW_HIT;
    if (lt32(c, v.hi, Z32, fl)) return IW_MISS;
    if (eq32(c, v.lo, Z32, fl) && eq32(c, v.hi, Z32, fl)) return IW_HIT;
    return IW_UNCERTAIN;
}

/* ---- staged ray-sphere discriminant ---- */
iw_class_t iw_sphere_stage1_f32(iw_ctx_t *ctx,
                                const msf64_t O[3], const msf64_t D[3],
                                const msf64_t C[3], msf64_t r,
                                msf32_t *lo_out, msf32_t *hi_out,
                                uint64_t *ops_out)
{
    msf_flags_t fl = 0;
    uint64_t start = ctx->ops;
    iv32_t Ov[3], Dv[3], Cv[3], L[3], rv, a, b, cc, disc;
    int i;
    for (i = 0; i < 3; i++) {
        Ov[i].lo = cvt32(ctx, O[i], IW_RM_LO, &fl);
        Ov[i].hi = cvt32(ctx, O[i], IW_RM_HI, &fl);
        Dv[i].lo = cvt32(ctx, D[i], IW_RM_LO, &fl);
        Dv[i].hi = cvt32(ctx, D[i], IW_RM_HI, &fl);
        Cv[i].lo = cvt32(ctx, C[i], IW_RM_LO, &fl);
        Cv[i].hi = cvt32(ctx, C[i], IW_RM_HI, &fl);
        L[i] = isub32(ctx, Ov[i], Cv[i], &fl);
    }
    rv.lo = cvt32(ctx, r, IW_RM_LO, &fl);
    rv.hi = cvt32(ctx, r, IW_RM_HI, &fl);
    a = idot32(ctx, Dv, Dv, &fl);
    b = idot32(ctx, L, Dv, &fl);
    cc = isub32(ctx, idot32(ctx, L, L, &fl), isqr32(ctx, rv, &fl), &fl);
    disc = isub32(ctx, isqr32(ctx, b, &fl), imul32(ctx, a, cc, &fl), &fl);
    *lo_out = disc.lo;
    *hi_out = disc.hi;
    { iw_class_t cls = decide32(ctx, disc, &fl);
      *ops_out = ctx->ops - start;
      return cls; }
}

iw_class_t iw_sphere_stage2_f64(iw_ctx_t *ctx,
                                const msf64_t O[3], const msf64_t D[3],
                                const msf64_t C[3], msf64_t r,
                                msf64_t *lo_out, msf64_t *hi_out,
                                uint64_t *ops_out)
{
    msf_flags_t fl = 0;
    uint64_t start = ctx->ops;
    iv64_t Dv[3], L[3], a, b, cc, disc;
    int i;
    for (i = 0; i < 3; i++) {
        Dv[i] = pt64(D[i]);
        L[i] = isub64(ctx, pt64(O[i]), pt64(C[i]), &fl);
    }
    a = idot64(ctx, Dv, Dv, &fl);
    b = idot64(ctx, L, Dv, &fl);
    cc = isub64(ctx, idot64(ctx, L, L, &fl), isqr64(ctx, pt64(r), &fl), &fl);
    disc = isub64(ctx, isqr64(ctx, b, &fl), imul64(ctx, a, cc, &fl), &fl);
    *lo_out = disc.lo;
    *hi_out = disc.hi;
    { iw_class_t cls = decide64(ctx, disc, &fl);
      *ops_out = ctx->ops - start;
      return cls; }
}

/* ---- stage 3: exact sign by error-free expansion ---- */
/* The two primitives are the Clause 9.5 augmented operations
 * consumed as error-free transformations: head + tail equals the
 * exact sum/product, with the head rounded by the clause-fixed
 * roundTiesTowardZero. Nothing below needs the head's rounding
 * to be to-nearest, only that the pair be exact; the flags guard
 * (guard_tripped) checks exactly that. An exact infinity or a
 * quiet NaN from an augmented call raises no flag in the
 * library, so a non-finite pair member poisons the guard word
 * here (bit test only, no library call). */
static int nonfinite64(msf64_t x)
{
    return ((x >> 52) & 0x7FFu) == 0x7FFu;
}

static void aug_sum(iw_ctx_t *c, msf64_t a, msf64_t b,
                    msf64_t *s_out, msf64_t *e_out, msf_flags_t *fl)
{
    msf64_pair_t pr = augadd64(c, a, b, fl);
    if (nonfinite64(pr.head) || nonfinite64(pr.tail)) {
        *fl |= MSF_FLAG_INVALID;
    }
    *s_out = pr.head;
    *e_out = pr.tail;
}

static void aug_prod(iw_ctx_t *c, msf64_t a, msf64_t b,
                     msf64_t *p_out, msf64_t *e_out, msf_flags_t *fl)
{
    msf64_pair_t pr = augmul64(c, a, b, fl);
    if (nonfinite64(pr.head) || nonfinite64(pr.tail)) {
        *fl |= MSF_FLAG_INVALID;
    }
    *p_out = pr.head;
    *e_out = pr.tail;
}

typedef struct { msf64_t *v; int n; int cap; int bad; } tlist_t;

static void tpush(tlist_t *t, msf64_t x)
{
    if (t->n >= t->cap) { t->bad = 1; return; }
    t->v[t->n++] = x;
}

static void tpush_prod(iw_ctx_t *c, tlist_t *t, msf64_t a, msf64_t b,
                       int negate, msf_flags_t *fl)
{
    msf64_t p, e;
    aug_prod(c, a, b, &p, &e, fl);
    if (negate) { p = neg64(c, p); e = neg64(c, e); }
    tpush(t, p);
    tpush(t, e);
}

/* VecSum: exact in-place transformation, same total sum. */
static void vecsum(iw_ctx_t *c, msf64_t *v, int n, msf_flags_t *fl)
{
    msf64_t s, ns, e;
    int i;
    if (n < 2) return;
    s = v[0];
    for (i = 1; i < n; i++) {
        aug_sum(c, s, v[i], &ns, &e, fl);
        v[i - 1] = e;
        s = ns;
    }
    v[n - 1] = s;
}

static int drop_zeros(msf64_t *v, int n)
{
    int i, w = 0;
    for (i = 0; i < n; i++) {
        if ((v[i] << 1) != 0) v[w++] = v[i];
    }
    return w;
}

static int distill(iw_ctx_t *c, msf64_t *v, int n, msf_flags_t *fl)
{
    int pass;
    for (pass = 0; pass < 8 && n > 1; pass++) {
        vecsum(c, v, n, fl);
        n = drop_zeros(v, n);
    }
    return n;
}

/* Exact sign of an exactly-summing term list: iterated VecSum
 * until the largest-magnitude term dominates an upward-rounded
 * bound on the rest (or all terms vanish). Undecided at the pass
 * cap reports *ok = 0. The bound uses its own flags word so its
 * rounding cannot pollute the proof guard. */
static int sign_of_terms(iw_ctx_t *c, msf64_t *v, int n,
                         msf_flags_t *fl, int *ok)
{
    int iter, i;
    *ok = 1;
    for (iter = 0; iter < 100; iter++) {
        msf_flags_t dfl = 0;
        msf64_t bound = Z64, am, ai;
        int mi = 0;
        vecsum(c, v, n, fl);
        n = drop_zeros(v, n);
        if (n == 0) return 0;
        am = abs64(c, v[0]);
        for (i = 1; i < n; i++) {
            ai = abs64(c, v[i]);
            if (gt64(c, ai, am, &dfl)) { am = ai; mi = i; }
        }
        for (i = 0; i < n; i++) {
            if (i == mi) continue;
            bound = a64(c, bound, abs64(c, v[i]), IW_RM_HI, &dfl);
        }
        if (gt64(c, am, bound, &dfl)) {
            return lt64(c, v[mi], Z64, &dfl) ? -1 : 1;
        }
    }
    *ok = 0;
    return 0;
}

/* Guard for augmented semantics: every write to the stage-3
 * flags word now comes from an augmented call (or the
 * non-finite poison above), and there inexact is raised exactly
 * when a pair itself is inexact - an overflowed head, or a mul
 * residual below the subnormal step (underflow+inexact). An
 * exact tiny residual raises nothing (P1 = R2) and must not
 * trip: it is an exact expansion term. So the guard is quiet
 * iff every pair consumed was exact and finite. */
static int guard_tripped(msf_flags_t fl)
{
#if IW_STAGE3_GUARD
    return (fl & (MSF_FLAG_OVERFLOW | MSF_FLAG_UNDERFLOW |
                  MSF_FLAG_INVALID | MSF_FLAG_INEXACT)) != 0;
#else
    (void)fl;
    return 0;
#endif
}

iw_class_t iw_sphere_stage3_exact(iw_ctx_t *ctx,
                                  const msf64_t O[3], const msf64_t D[3],
                                  const msf64_t C[3], msf64_t r,
                                  uint64_t *ops_out)
{
    msf_flags_t fl = 0;
    uint64_t start = ctx->ops;
    msf64_t lhi[3], llo[3], s, e;
    tlist_t la, lb, lc, ld;
    int i, j, ok, sign;
    iw_class_t cls;

    la.v = ctx->terms_a; la.n = 0; la.cap = IW_MAX_SMALL_TERMS; la.bad = 0;
    lb.v = ctx->terms_b; lb.n = 0; lb.cap = IW_MAX_SMALL_TERMS; lb.bad = 0;
    lc.v = ctx->terms_c; lc.n = 0; lc.cap = IW_MAX_SMALL_TERMS; lc.bad = 0;
    ld.v = ctx->terms;   ld.n = 0; ld.cap = IW_MAX_TERMS;       ld.bad = 0;

    for (i = 0; i < 3; i++) {
        aug_sum(ctx, O[i], neg64(ctx, C[i]), &s, &e, &fl);
        lhi[i] = s;
        llo[i] = e;
        tpush_prod(ctx, &la, D[i], D[i], 0, &fl);
        tpush_prod(ctx, &lb, lhi[i], D[i], 0, &fl);
        tpush_prod(ctx, &lb, llo[i], D[i], 0, &fl);
        tpush_prod(ctx, &lc, lhi[i], lhi[i], 0, &fl);
        tpush_prod(ctx, &lc, lhi[i], llo[i], 0, &fl);
        tpush_prod(ctx, &lc, lhi[i], llo[i], 0, &fl);
        tpush_prod(ctx, &lc, llo[i], llo[i], 0, &fl);
    }
    tpush_prod(ctx, &lc, r, r, 1, &fl);

    la.n = distill(ctx, la.v, la.n, &fl);
    lb.n = distill(ctx, lb.v, lb.n, &fl);
    lc.n = distill(ctx, lc.v, lc.n, &fl);

    /* disc = b*b - a*c over the distilled expansions. */
    for (i = 0; i < lb.n; i++) {
        tpush_prod(ctx, &ld, lb.v[i], lb.v[i], 0, &fl);
        for (j = i + 1; j < lb.n; j++) {
            tpush_prod(ctx, &ld, lb.v[i], lb.v[j], 0, &fl);
            tpush_prod(ctx, &ld, lb.v[i], lb.v[j], 0, &fl);
        }
    }
    for (i = 0; i < la.n; i++) {
        for (j = 0; j < lc.n; j++) {
            tpush_prod(ctx, &ld, la.v[i], lc.v[j], 1, &fl);
        }
    }

    if (la.bad || lb.bad || lc.bad || ld.bad || guard_tripped(fl)) {
        *ops_out = ctx->ops - start;
        return IW_UNCERTAIN;
    }
    sign = sign_of_terms(ctx, ld.v, ld.n, &fl, &ok);
    if (!ok || guard_tripped(fl)) {
        *ops_out = ctx->ops - start;
        return IW_UNCERTAIN;
    }
    cls = (sign < 0) ? IW_MISS : IW_HIT;
    *ops_out = ctx->ops - start;
    return cls;
}

/* ---- ray-box slab test ---- */
static iv64_t idiv_pt(iw_ctx_t *c, iv64_t a, msf64_t d,
                      msf_rounding_t lo_mode, msf_rounding_t hi_mode,
                      msf_flags_t *fl)
{
    iv64_t r;
    if (gt64(c, d, Z64, fl)) {
        r.lo = d64(c, a.lo, d, lo_mode, fl);
        r.hi = d64(c, a.hi, d, hi_mode, fl);
    } else {
        r.lo = d64(c, a.hi, d, lo_mode, fl);
        r.hi = d64(c, a.lo, d, hi_mode, fl);
    }
    return r;
}

/* One slab intersection. outward selects (RD lo, RU hi); the
 * inward call swaps them, giving an inner t-interval. Returns 0,
 * or 1 when an axis-parallel ray lies outside its slab (exact). */
static int slab_intersect(iw_ctx_t *c, const msf64_t O[3],
                          const msf64_t D[3], const msf64_t loB[3],
                          const msf64_t hiB[3], int outward,
                          msf64_t *t0_out, msf64_t *t1_out,
                          msf_flags_t *fl)
{
    msf_rounding_t lo_mode = outward ? IW_RM_LO : IW_RM_HI;
    msf_rounding_t hi_mode = outward ? IW_RM_HI : IW_RM_LO;
    msf64_t t0 = Z64, t1 = INF64;
    int i;
    for (i = 0; i < 3; i++) {
        iv64_t n1, n2, q1, q2;
        msf64_t axis_lo, axis_hi;
        if (eq64(c, D[i], Z64, fl)) {
            /* Explicit axis-parallel branch (workload logic). */
            if (lt64(c, O[i], loB[i], fl) || gt64(c, O[i], hiB[i], fl)) {
                return 1;
            }
            continue;
        }
        n1.lo = s64(c, loB[i], O[i], lo_mode, fl);
        n1.hi = s64(c, loB[i], O[i], hi_mode, fl);
        n2.lo = s64(c, hiB[i], O[i], lo_mode, fl);
        n2.hi = s64(c, hiB[i], O[i], hi_mode, fl);
        q1 = idiv_pt(c, n1, D[i], lo_mode, hi_mode, fl);
        q2 = idiv_pt(c, n2, D[i], lo_mode, hi_mode, fl);
        axis_lo = min64(c, q1.lo, q2.lo, fl);
        axis_hi = max64(c, q1.hi, q2.hi, fl);
        t0 = max64(c, t0, axis_lo, fl);
        t1 = min64(c, t1, axis_hi, fl);
    }
    *t0_out = t0;
    *t1_out = t1;
    return 0;
}

iw_class_t iw_box(iw_ctx_t *ctx,
                  const msf64_t O[3], const msf64_t D[3],
                  const msf64_t loB[3], const msf64_t hiB[3],
                  msf64_t *tmin_out, msf64_t *tmax_out,
                  uint64_t *ops_out)
{
    msf_flags_t fl = 0;
    uint64_t start = ctx->ops;
    msf64_t o0, o1, i0, i1;
    iw_class_t cls;
    if (slab_intersect(ctx, O, D, loB, hiB, 1, &o0, &o1, &fl)) {
        *tmin_out = Z64;
        *tmax_out = neg64(ctx, Z64);
        *ops_out = ctx->ops - start;
        return IW_MISS;
    }
    *tmin_out = o0;
    *tmax_out = o1;
    if (gt64(ctx, o0, o1, &fl)) {
        *ops_out = ctx->ops - start;
        return IW_MISS;
    }
    if (slab_intersect(ctx, O, D, loB, hiB, 0, &i0, &i1, &fl)) {
        *ops_out = ctx->ops - start;
        return IW_MISS; /* same exact branch, defensive */
    }
    cls = le64(ctx, i0, i1, &fl) ? IW_HIT : IW_UNCERTAIN;
    *ops_out = ctx->ops - start;
    return cls;
}

/* ---- torus first-hit bracketing ---- */
#define TORUS_S_CONST ((msf64_t)0x400E000000000000ULL) /* R^2-r^2 = 3.75 */
#define TORUS_K ((msf64_t)0x4030000000000000ULL)       /* 4R^2 = 16 */
#define TORUS_TMAX ((msf64_t)0x4026000000000000ULL)    /* 11 */
#define TORUS_STACK 128

static iv64_t torus_F(iw_ctx_t *c, const msf64_t O[3], const msf64_t D[3],
                      iv64_t T, msf_flags_t *fl)
{
    iv64_t P[3], sx, sy, sz, s, xy;
    int i;
    for (i = 0; i < 3; i++) {
        P[i] = iadd64(c, pt64(O[i]), imul64(c, T, pt64(D[i]), fl), fl);
    }
    sx = isqr64(c, P[0], fl);
    sy = isqr64(c, P[1], fl);
    sz = isqr64(c, P[2], fl);
    s = iadd64(c, iadd64(c, iadd64(c, sx, sy, fl), sz, fl),
               pt64(TORUS_S_CONST), fl);
    xy = iadd64(c, sx, sy, fl);
    return isub64(c, isqr64(c, s, fl), imul64(c, pt64(TORUS_K), xy, fl), fl);
}

void iw_torus_first_hit(iw_ctx_t *ctx,
                        const msf64_t O[3], const msf64_t D[3],
                        msf64_t tol_bits, uint64_t op_cap,
                        iw_torus_result_t *res)
{
    msf_flags_t fl = 0;
    uint64_t start = ctx->ops;
    msf64_t sa[TORUS_STACK], sb[TORUS_STACK];
    uint32_t sd[TORUS_STACK];
    int sp = 0, cand_found = 0;
    msf64_t cand_lo = Z64;

    res->cls = IW_UNCERTAIN;
    res->br_lo = Z64;
    res->br_hi = Z64;
    res->evals = 0;
    res->max_depth = 0;
    res->cap_hit = 0;

    sa[sp] = Z64; sb[sp] = TORUS_TMAX; sd[sp] = 0; sp++;
    while (sp > 0) {
        msf64_t a, b, width;
        uint32_t depth;
        iv64_t T, F;
        sp--;
        a = sa[sp]; b = sb[sp]; depth = sd[sp];
        if (depth > res->max_depth) res->max_depth = depth;
        if (ctx->ops - start >= op_cap) { res->cap_hit = 1; break; }
        T.lo = a; T.hi = b;
        F = torus_F(ctx, O, D, T, &fl);
        res->evals++;
        if (gt64(ctx, F.lo, Z64, &fl)) continue; /* proven OUT */
        width = s64(ctx, b, a, IW_RM_HI, &fl);
        if (!le64(ctx, width, tol_bits, &fl)) {
            msf64_t mid = m64(ctx, a64(ctx, a, b, IW_RN, &fl), HALF64,
                              IW_RN, &fl);
            if (!eq64(ctx, mid, a, &fl) && !eq64(ctx, mid, b, &fl)) {
                if (sp > TORUS_STACK - 2) { res->cap_hit = 1; break; }
                sa[sp] = mid; sb[sp] = b; sd[sp] = depth + 1; sp++;
                sa[sp] = a; sb[sp] = mid; sd[sp] = depth + 1; sp++;
                continue;
            }
            /* adjacent endpoints: cannot split further */
        }
        if (!cand_found) { cand_found = 1; cand_lo = a; }
        {
            iv64_t Fp = torus_F(ctx, O, D, pt64(b), &fl);
            res->evals++;
            if (lt64(ctx, Fp.hi, Z64, &fl)) {
                res->cls = IW_HIT;
                res->br_lo = cand_lo;
                res->br_hi = b;
                res->ops = ctx->ops - start;
                return;
            }
        }
    }
    res->ops = ctx->ops - start;
    if (res->cap_hit) {
        res->cls = IW_UNCERTAIN;
    } else if (cand_found) {
        res->cls = IW_UNCERTAIN;
        res->br_lo = cand_lo;
        res->br_hi = TORUS_TMAX;
    } else {
        res->cls = IW_MISS;
    }
}
