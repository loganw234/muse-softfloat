/* msf_aug.c - Clause 9.5 augmented arithmetic (SF-2 Step 4).
 *
 * augmentedAddition/Subtraction/Multiplication at binary16,
 * binary32 and binary64: two same-format operands in, an
 * ordered (head, tail) pair out. head is the exact result
 * rounded by roundTiesTowardZero, the direction the clause
 * fixes (no caller attribute exists on these names); tail
 * is the exact residual exact - head, delivered exactly
 * whenever representable (add/sub: always; mul: except the
 * characterised below-step cell, where tail is the residual
 * itself rounded by roundTiesTowardZero). Definitions and
 * the representability proof: docs/WIDTHS.md augmented rows;
 * design record ledger/parcel-w5aug.md.
 *
 * Flags (ratified table, default handling only): invalid
 * from the SF-0 2.5 matrix; overflow + inexact exactly when
 * the finite-input head overflows; mul's unrepresentable
 * residual raises underflow + inexact; nothing else raises.
 * In particular pin P1 = R2: an exact tiny residual (nonzero,
 * strictly between +-b^emin, delivered exactly as a
 * subnormal tail) signals underflow under 9.5 but raises NO
 * flag, because 7.5 default handling withholds the flag for
 * an exact delivered result. Inexact tracks exactness of the
 * pair, never rounding of the head alone. Head tininess
 * alone raises nothing.
 *
 * Mechanism: flags are computed from exact-residual tests
 * in this file only. The shared pack is used with the
 * internal MSF_IROUND_RTTZ mode (value 5, pin P5) as a
 * bits-only oracle for the head and for an exactly
 * representable tail; its scratch flags are discarded
 * unread in shipped builds. Add/sub form the exact sum in a
 * plain-shift 128-bit window when the operand bit span is
 * at most 127; wider spans take the verbatim far-operand
 * branch (head is the larger operand, tail the smaller,
 * effective signs applied) under the gap lemma in WIDTHS.
 * Mul splits the exact 2p product at the head grid.
 * Specials ride msf_nan_delivery; the decided NaN bits are
 * delivered to both outputs, as is an exact infinity.
 *
 * Test-only mutants below (MSF_AUG_TEST_*), never defined
 * in a build whose results are quoted: each was watched
 * refusing the committed vectors (parcel report).
 */
#include "msf_internal.h"
#include "msf_decode.h"

enum { AUG_ADD = 0, AUG_SUB = 1, AUG_MUL = 2 };

typedef struct aug_exact {
    int sign;
    msf_u128_t mag; /* value = (-1)^sign * mag * 2^exp */
    int32_t exp;
} aug_exact_t;

static int aug_blen(msf_u128_t a)
{
    return 128 - msf_u128_clz(a);
}

static int aug_tz(msf_u128_t a) /* a != 0 */
{
    int i, n = 0;
    for (i = 0; i < 4; i++) {
        uint32_t w = a.w[i];
        if (w != 0u) {
            while ((w & 1u) == 0u) {
                w >>= 1;
                n++;
            }
            return n;
        }
        n += 32;
    }
    return 128;
}

/* Bits-only packs. The scratch flag word is the whole point
 * of the separation: the pack's own Clause 7 judgements
 * (after-rounding tininess on the head, head inexactness)
 * are not this family's flags and are discarded. */
static uint64_t aug_pack_head(const msf_fmt_params_t *fp, int sign,
                              int32_t exp, msf_u128_t mag,
                              msf_flags_t *scratch_out)
{
    int rm = MSF_IROUND_RTTZ;
    msf_flags_t scratch = 0u;
    uint64_t r;
#ifdef MSF_AUG_TEST_TE_HEAD
    rm = MSF_IROUND_TIES_TO_EVEN; /* mutant: wrong tie rule */
#endif
    r = msf_pack_generic(fp, sign, exp, mag, 0, rm, &scratch);
    if (scratch_out != 0) {
        *scratch_out = scratch;
    }
    return r;
}

static uint64_t aug_pack_tail(const msf_fmt_params_t *fp, int sign,
                              int32_t exp, msf_u128_t mag)
{
    msf_flags_t scratch = 0u;
    return msf_pack_generic(fp, sign, exp, mag, 0,
                            MSF_IROUND_RTTZ, &scratch);
}

static void aug_leak(msf_flags_t head_scratch, msf_flags_t *flags)
{
#ifdef MSF_AUG_TEST_PACK_LEAK
    /* mutant: inherit the head pack's underflow/inexact */
    *flags |= head_scratch & (MSF_FLAG_UNDERFLOW | MSF_FLAG_INEXACT);
#else
    (void)head_scratch;
    (void)flags;
#endif
}

static uint64_t aug_zero_tail(const msf_fmt_params_t *fp, uint64_t head)
{
    uint64_t z = head & fp->sign_mask; /* zero with head sign */
#ifdef MSF_AUG_TEST_ZERO_TAIL_SIGN
    z ^= fp->sign_mask; /* mutant: wrong exact-zero tail sign */
#endif
    return z;
}

/* r = exact - head_value, computed at the coarser input
 * scale min(exact.exp, head.exp). Shift bounds are WIDTHS
 * facts: the head is a nearest grid neighbour of exact, so
 * the two top-bit positions differ by at most one and each
 * left shift is bounded by the other value's bit length
 * (at most 127 here). A zero head leaves r = exact. */
static aug_exact_t aug_residual(aug_exact_t exact,
                                const msf_decoded_t *head)
{
    aug_exact_t r;
    int32_t er;
    msf_u128_t ev, hv;
    if (msf_u128_is_zero(head->sig)) {
        return exact;
    }
    er = exact.exp < head->exp ? exact.exp : head->exp;
    ev = msf_u128_shl(exact.mag, (unsigned)(exact.exp - er));
    hv = msf_u128_shl(head->sig, (unsigned)(head->exp - er));
    r.exp = er;
    if (msf_u128_cmp(ev, hv) >= 0) {
        r.mag = msf_u128_sub(ev, hv, 0);
        r.sign = exact.sign;
    } else {
        r.mag = msf_u128_sub(hv, ev, 0);
        r.sign = exact.sign ^ 1;
    }
    return r;
}

static int aug_is_inf_bits(const msf_fmt_params_t *fp, uint64_t bits)
{
    return (bits & ~fp->sign_mask) == fp->infinity;
}

#ifdef MSF_AUG_TEST_P1_OPPOSITE
static int aug_tiny(const msf_fmt_params_t *fp, aug_exact_t r)
{
    /* nonzero r with |r| < 2^emin, judged on exact r */
    return !msf_u128_is_zero(r.mag)
        && (r.exp + aug_blen(r.mag) - 1) < fp->emin;
}
#endif

static void aug_p1_opposite(const msf_fmt_params_t *fp, aug_exact_t r,
                            msf_flags_t *flags)
{
#ifdef MSF_AUG_TEST_P1_OPPOSITE
    /* mutant: R1 reading (raise on an exact tiny residual) */
    if (aug_tiny(fp, r)) {
        *flags |= MSF_FLAG_UNDERFLOW;
    }
#else
    (void)fp;
    (void)r;
    (void)flags;
#endif
}

/* Exact representability of a nonzero dyadic value in fp:
 * at most p significant bits, no set bit below the
 * subnormal step, top bit inside the exponent range. */
static int aug_representable(const msf_fmt_params_t *fp, aug_exact_t r)
{
    int bl = aug_blen(r.mag);
    int tz = aug_tz(r.mag);
    return bl - tz <= fp->precision
        && r.exp + tz >= fp->emin - fp->frac_bits
        && r.exp + bl - 1 <= fp->emax;
}

static uint64_t aug_with_sign(const msf_fmt_params_t *fp, uint64_t bits,
                              int sign)
{
    return (bits & ~fp->sign_mask) | (sign ? fp->sign_mask : 0u);
}

/* Finite add/sub. eff_b is b's sign in the effective sum. */
static void aug_addsub_finite(int fmt, const msf_decoded_t *da,
                              const msf_decoded_t *db, int eff_b,
                              uint64_t *head, uint64_t *tail,
                              msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    int a_nz = !msf_u128_is_zero(da->sig);
    int b_nz = !msf_u128_is_zero(db->sig);
    aug_exact_t exact;
    msf_flags_t head_scratch = 0u;
    msf_decoded_t hd;
    aug_exact_t r;

    if (a_nz && b_nz) {
        int32_t ta = da->exp + aug_blen(da->sig) - 1;
        int32_t tb = db->exp + aug_blen(db->sig) - 1;
        int32_t lo_b = da->exp < db->exp ? da->exp : db->exp;
        int32_t hi_t = ta > tb ? ta : tb;
        if (hi_t - lo_b + 1 > 127) {
            /* Verbatim far-operand branch (WIDTHS gap
             * lemma): the smaller magnitude is strictly
             * below half the smaller grid step beside the
             * larger operand, so the head is the larger
             * operand and the residual is the smaller one. */
            const msf_decoded_t *hi = ta > tb ? da : db;
            const msf_decoded_t *lo = ta > tb ? db : da;
            int hi_s = ta > tb ? da->sign : eff_b;
            int lo_s = ta > tb ? eff_b : da->sign;
            aug_exact_t lr;
            *head = aug_with_sign(fp, hi->bits, hi_s);
            *tail = aug_with_sign(fp, lo->bits, lo_s);
#ifdef MSF_AUG_TEST_JAM_WINDOW
            /* mutant: far operand jammed away as sticky,
             * so the exact tail is lost entirely */
            *tail = *head & fp->sign_mask;
#endif
            lr.sign = lo_s;
            lr.mag = lo->sig;
            lr.exp = lo->exp;
            aug_p1_opposite(fp, lr, flags);
            return;
        }
    }

    {
        int32_t e = a_nz && b_nz
            ? (da->exp < db->exp ? da->exp : db->exp)
            : (a_nz ? da->exp : db->exp);
        msf_u128_t av = a_nz
            ? msf_u128_shl(da->sig, (unsigned)(da->exp - e))
            : msf_u128_from_u64(0u);
        msf_u128_t bv = b_nz
            ? msf_u128_shl(db->sig, (unsigned)(db->exp - e))
            : msf_u128_from_u64(0u);
        exact.exp = e;
        if (da->sign == eff_b) {
            uint32_t carry = 0u;
            exact.mag = msf_u128_add(av, bv, &carry);
            exact.sign = da->sign;
            (void)carry; /* sum < 2^128: span <= 127 (WIDTHS) */
        } else if (msf_u128_cmp(av, bv) >= 0) {
            exact.mag = msf_u128_sub(av, bv, 0);
            exact.sign = da->sign;
        } else {
            exact.mag = msf_u128_sub(bv, av, 0);
            exact.sign = eff_b;
        }
    }

    if (msf_u128_is_zero(exact.mag)) {
        /* 6.3 read with RTTZ: an exact zero sum takes the
         * common sign only when both effective operands
         * are negative; cancellation delivers +0. */
        int zs = da->sign && eff_b;
        *head = zs ? fp->sign_mask : 0u;
        *tail = aug_zero_tail(fp, *head);
        return;
    }

    *head = aug_pack_head(fp, exact.sign, exact.exp, exact.mag,
                          &head_scratch);
    if (aug_is_inf_bits(fp, *head)) {
        *flags |= MSF_FLAG_OVERFLOW | MSF_FLAG_INEXACT;
        *tail = *head;
        return;
    }
    aug_leak(head_scratch, flags);
    hd = msf_decode(fmt, *head);
    r = aug_residual(exact, &hd);
    if (msf_u128_is_zero(r.mag)) {
        *tail = aug_zero_tail(fp, *head);
        return;
    }
    /* Representable always (WIDTHS proof); pack is exact. */
    *tail = aug_pack_tail(fp, r.sign, r.exp, r.mag);
    aug_p1_opposite(fp, r, flags); /* P1 = R2: no flag here */
}

/* Finite mul: exact 2p product, split at the head grid. */
static void aug_mul_finite(int fmt, const msf_decoded_t *da,
                           const msf_decoded_t *db,
                           uint64_t *head, uint64_t *tail,
                           msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    int sign = da->sign ^ db->sign;
    aug_exact_t exact;
    msf_flags_t head_scratch = 0u;
    msf_decoded_t hd;
    aug_exact_t r;

    if (msf_u128_is_zero(da->sig) || msf_u128_is_zero(db->sig)) {
        *head = sign ? fp->sign_mask : 0u; /* 6.3 product sign */
        *tail = aug_zero_tail(fp, *head);
        return;
    }
    exact.sign = sign;
    exact.mag = msf_u128_mul_u64_u64(msf_u128_to_u64_trunc(da->sig),
                                     msf_u128_to_u64_trunc(db->sig));
    exact.exp = da->exp + db->exp;

    *head = aug_pack_head(fp, sign, exact.exp, exact.mag,
                          &head_scratch);
    if (aug_is_inf_bits(fp, *head)) {
        *flags |= MSF_FLAG_OVERFLOW | MSF_FLAG_INEXACT;
        *tail = *head;
        return;
    }
    aug_leak(head_scratch, flags);
    hd = msf_decode(fmt, *head);
    r = aug_residual(exact, &hd);
    if (msf_u128_is_zero(r.mag)) {
        *tail = aug_zero_tail(fp, *head);
        return;
    }
    if (aug_representable(fp, r)) {
        *tail = aug_pack_tail(fp, r.sign, r.exp, r.mag);
        aug_p1_opposite(fp, r, flags); /* P1 = R2: no flag */
        return;
    }
    /* The one inexact finite cell: nonzero residual digits
     * below the subnormal step. The tail is the residual
     * rounded by RTTZ (a zero so rounded keeps the
     * residual's own sign, per the exact-zero sentence's
     * absence here and 6.3's nonzero-to-zero rule), and
     * default handling raises underflow + inexact (9.5).
     * The pack's scratch word is still discarded: these
     * flags come from this exact-residual test. */
    *tail = aug_pack_tail(fp, r.sign, r.exp, r.mag);
    *flags |= MSF_FLAG_UNDERFLOW | MSF_FLAG_INEXACT;
}

static void aug_core(int fmt, int op, uint64_t abits, uint64_t bbits,
                     uint64_t *head, uint64_t *tail, msf_flags_t *flags)
{
    const msf_fmt_params_t *fp = &MSF_FMT_PARAMS[fmt];
    msf_decoded_t da = msf_decode(fmt, abits);
    msf_decoded_t db = msf_decode(fmt, bbits);
    msf_decoded_t ops[2];
    int fmts[2];
    int eff_b = db.sign ^ (op == AUG_SUB ? 1 : 0);
    int inv = 0;
    uint64_t out = 0u;

    ops[0] = da;
    ops[1] = db;
    fmts[0] = fmt;
    fmts[1] = fmt;
    if (op == AUG_MUL) {
        inv = (da.cls == MSF_VC_ZERO && db.cls == MSF_VC_INFINITY)
           || (da.cls == MSF_VC_INFINITY && db.cls == MSF_VC_ZERO);
    } else {
        inv = da.cls == MSF_VC_INFINITY
           && db.cls == MSF_VC_INFINITY && da.sign != eff_b;
    }
    if (msf_nan_delivery(fmt, ops, fmts, 2, inv, &out, flags)) {
        *head = out; /* same NaN bits twice (9.5) */
        *tail = out;
        return;
    }
    if (da.cls == MSF_VC_INFINITY || db.cls == MSF_VC_INFINITY) {
        int s = op == AUG_MUL ? (da.sign ^ db.sign)
              : (da.cls == MSF_VC_INFINITY ? da.sign : eff_b);
        *head = (s ? fp->sign_mask : 0u) | fp->infinity;
        *tail = *head; /* exact infinity twice, no flag */
        return;
    }
    if (op == AUG_MUL) {
        aug_mul_finite(fmt, &da, &db, head, tail, flags);
    } else {
        aug_addsub_finite(fmt, &da, &db, eff_b, head, tail, flags);
    }
#ifdef MSF_AUG_TEST_SWAP_PAIR
    {
        uint64_t t = *head; /* mutant: swapped pair order */
        *head = *tail;
        *tail = t;
    }
#endif
}

#define DEF_AUG(NAME, PAIR, TYPE, FMT, OP) \
    PAIR NAME(TYPE a, TYPE b, msf_flags_t *fl) \
    { \
        PAIR r; \
        uint64_t h = 0u, t = 0u; \
        aug_core(FMT, OP, (uint64_t)a, (uint64_t)b, &h, &t, fl); \
        r.head = (TYPE)h; \
        r.tail = (TYPE)t; \
        return r; \
    }

DEF_AUG(msf16_augmented_add, msf16_pair_t, msf16_t, MSF_FMT_F16, AUG_ADD)
DEF_AUG(msf32_augmented_add, msf32_pair_t, msf32_t, MSF_FMT_F32, AUG_ADD)
DEF_AUG(msf64_augmented_add, msf64_pair_t, msf64_t, MSF_FMT_F64, AUG_ADD)
DEF_AUG(msf16_augmented_sub, msf16_pair_t, msf16_t, MSF_FMT_F16, AUG_SUB)
DEF_AUG(msf32_augmented_sub, msf32_pair_t, msf32_t, MSF_FMT_F32, AUG_SUB)
DEF_AUG(msf64_augmented_sub, msf64_pair_t, msf64_t, MSF_FMT_F64, AUG_SUB)
DEF_AUG(msf16_augmented_mul, msf16_pair_t, msf16_t, MSF_FMT_F16, AUG_MUL)
DEF_AUG(msf32_augmented_mul, msf32_pair_t, msf32_t, MSF_FMT_F32, AUG_MUL)
DEF_AUG(msf64_augmented_mul, msf64_pair_t, msf64_t, MSF_FMT_F64, AUG_MUL)

