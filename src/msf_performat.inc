/* msf_performat.inc - classification, sign-bit, Clause 9.6
 * minimum/maximum and Clause 9.7 payload operations, instantiated
 * once per format by msf16.c / msf32.c / msf64.c with MSF_PF set
 * to 16, 32, or 64. Constants come only from the generated
 * msf_formats.h (SF-0 Section 6 item 3). The classification,
 * sign-bit and payload operations never signal, so none takes a
 * flags pointer; the 9.6 family takes one and signals only
 * invalid, only from a signaling NaN operand. Nothing here
 * rounds: 9.6 selects an operand, 9.7 payloads are exact
 * integers below 2^p in the same format.
 */
#define MSF_PF_CAT2(a, b) a##b
#define MSF_PF_CAT(a, b) MSF_PF_CAT2(a, b)
#define MSF_PF_FN(op) MSF_PF_CAT(MSF_PF_CAT(msf, MSF_PF), MSF_PF_CAT(_, op))
#define MSF_PF_T MSF_PF_CAT(MSF_PF_CAT(msf, MSF_PF), _t)
#define MSF_PF_C(x) MSF_PF_CAT(MSF_PF_CAT(MSF_F, MSF_PF), MSF_PF_CAT(_, x))

static uint32_t MSF_PF_FN(exp_field)(MSF_PF_T a)
{
    return (uint32_t)(((uint64_t)a >> MSF_PF_C(FRAC_BITS)) & MSF_PF_C(EXP_MAX));
}

static uint64_t MSF_PF_FN(frac_field)(MSF_PF_T a)
{
    return (uint64_t)a & MSF_PF_C(FRAC_MASK);
}

MSF_PF_T MSF_PF_FN(copy)(MSF_PF_T a)
{
    return a;
}

MSF_PF_T MSF_PF_FN(negate)(MSF_PF_T a)
{
    return (MSF_PF_T)((uint64_t)a ^ MSF_PF_C(SIGN_MASK));
}

MSF_PF_T MSF_PF_FN(abs)(MSF_PF_T a)
{
    return (MSF_PF_T)((uint64_t)a & ~MSF_PF_C(SIGN_MASK));
}

MSF_PF_T MSF_PF_FN(copy_sign)(MSF_PF_T a, MSF_PF_T b)
{
    return (MSF_PF_T)(((uint64_t)a & ~MSF_PF_C(SIGN_MASK))
                      | ((uint64_t)b & MSF_PF_C(SIGN_MASK)));
}

msf_class_t MSF_PF_FN(class)(MSF_PF_T a)
{
    int negative = ((uint64_t)a & MSF_PF_C(SIGN_MASK)) != 0u;
    if (MSF_PF_FN(exp_field)(a) == MSF_PF_C(EXP_MAX)) {
        if (MSF_PF_FN(frac_field)(a) == 0u) {
            return negative ? MSF_CLASS_NEGATIVE_INFINITY
                            : MSF_CLASS_POSITIVE_INFINITY;
        }
        return (((uint64_t)a & MSF_PF_C(QUIET_BIT)) != 0u)
                   ? MSF_CLASS_QUIET_NAN : MSF_CLASS_SIGNALING_NAN;
    }
    if (MSF_PF_FN(exp_field)(a) == 0u) {
        if (MSF_PF_FN(frac_field)(a) == 0u) {
            return negative ? MSF_CLASS_NEGATIVE_ZERO : MSF_CLASS_POSITIVE_ZERO;
        }
        return negative ? MSF_CLASS_NEGATIVE_SUBNORMAL
                        : MSF_CLASS_POSITIVE_SUBNORMAL;
    }
    return negative ? MSF_CLASS_NEGATIVE_NORMAL : MSF_CLASS_POSITIVE_NORMAL;
}

int MSF_PF_FN(is_sign_minus)(MSF_PF_T a)
{
    return ((uint64_t)a & MSF_PF_C(SIGN_MASK)) != 0u;
}

int MSF_PF_FN(is_normal)(MSF_PF_T a)
{
    uint32_t e = MSF_PF_FN(exp_field)(a);
    return e != 0u && e != MSF_PF_C(EXP_MAX);
}

int MSF_PF_FN(is_finite)(MSF_PF_T a)
{
    return MSF_PF_FN(exp_field)(a) != MSF_PF_C(EXP_MAX);
}

int MSF_PF_FN(is_zero)(MSF_PF_T a)
{
    return MSF_PF_FN(exp_field)(a) == 0u && MSF_PF_FN(frac_field)(a) == 0u;
}

int MSF_PF_FN(is_subnormal)(MSF_PF_T a)
{
    return MSF_PF_FN(exp_field)(a) == 0u && MSF_PF_FN(frac_field)(a) != 0u;
}

int MSF_PF_FN(is_infinite)(MSF_PF_T a)
{
    return MSF_PF_FN(exp_field)(a) == MSF_PF_C(EXP_MAX)
        && MSF_PF_FN(frac_field)(a) == 0u;
}

int MSF_PF_FN(is_nan)(MSF_PF_T a)
{
    return MSF_PF_FN(exp_field)(a) == MSF_PF_C(EXP_MAX)
        && MSF_PF_FN(frac_field)(a) != 0u;
}

int MSF_PF_FN(is_signaling)(MSF_PF_T a)
{
    return MSF_PF_FN(is_nan)(a) && (((uint64_t)a & MSF_PF_C(QUIET_BIT)) == 0u);
}

int MSF_PF_FN(is_canonical)(MSF_PF_T a)
{
    (void)a;
    return 1; /* every encoding of this binary format is canonical (SF-0 2.5) */
}

int MSF_PF_FN(radix)(MSF_PF_T a)
{
    (void)a;
    return 2;
}

int MSF_PF_FN(is754version1985)(void)
{
    return 0;
}

int MSF_PF_FN(is754version2008)(void)
{
    return 0;
}

int MSF_PF_FN(is754version2019)(void)
{
    return 1;
}

/* ---- Clause 9.6 minimum/maximum (SF-1 Step 1) ----
 * Value order for non-NaN operands, with signed zeros ordered
 * (-0 the minimum, +0 the maximum): a deliberate tweak over
 * msf_cmp_finite, which compares zeros equal. Equal values
 * otherwise deliver the first operand. Magnitude order is the
 * sign-cleared encoding order; a magnitude tie breaks by the
 * corresponding value form. Plain forms deliver any NaN per the
 * SF-0 2.5 matrix; Number forms deliver the number when exactly
 * one operand is NaN (a signaling NaN there still signals
 * invalid) and the matrix result when both are NaN. */

static int MSF_PF_FN(fmt_idx)(void)
{
    return MSF_PF == 16 ? MSF_FMT_F16 : (MSF_PF == 32 ? MSF_FMT_F32 : MSF_FMT_F64);
}

static int MSF_PF_FN(value_cmp_nonan)(const msf_decoded_t *a,
                                      const msf_decoded_t *b)
{
    int ainf = a->cls == MSF_VC_INFINITY, binf = b->cls == MSF_VC_INFINITY;
    if (ainf || binf) {
        if (ainf && binf) {
            return a->sign == b->sign ? 0 : (a->sign ? -1 : 1);
        }
        if (ainf) {
            return a->sign ? -1 : 1;
        }
        return b->sign ? 1 : -1;
    }
    if (a->cls == MSF_VC_ZERO && b->cls == MSF_VC_ZERO) {
        if (a->sign == b->sign) {
            return 0;
        }
        return a->sign ? -1 : 1; /* -0 below +0 (9.6) */
    }
    return msf_cmp_finite(a, b);
}

static int MSF_PF_FN(mag_cmp_nonan)(MSF_PF_T a, MSF_PF_T b)
{
    uint64_t ma = (uint64_t)a & ~MSF_PF_C(SIGN_MASK);
    uint64_t mb = (uint64_t)b & ~MSF_PF_C(SIGN_MASK);
    return ma < mb ? -1 : (ma > mb ? 1 : 0);
}

static MSF_PF_T MSF_PF_FN(minmax_core)(MSF_PF_T a, MSF_PF_T b, int want_min,
                                       int by_mag, int is_number,
                                       msf_flags_t *flags)
{
    int fmt = MSF_PF_FN(fmt_idx)();
    msf_decoded_t da = msf_decode(fmt, (uint64_t)a);
    msf_decoded_t db = msf_decode(fmt, (uint64_t)b);
    int an = msf_is_nan_cls(da.cls), bn = msf_is_nan_cls(db.cls);
    int vc;
    if (is_number && an != bn) {
        if ((an ? da.cls : db.cls) == MSF_VC_SIGNALING_NAN) {
            *flags |= MSF_FLAG_INVALID;
        }
        return an ? b : a; /* the number, verbatim */
    }
    if (an || bn) {
        msf_decoded_t ops[2];
        int fmts[2];
        uint64_t out = 0u;
        ops[0] = da;
        ops[1] = db;
        fmts[0] = fmt;
        fmts[1] = fmt;
        (void)msf_nan_delivery(fmt, ops, fmts, 2, 0, &out, flags);
        return (MSF_PF_T)out;
    }
    vc = MSF_PF_FN(value_cmp_nonan)(&da, &db);
    if (by_mag) {
        int mc = MSF_PF_FN(mag_cmp_nonan)(a, b);
        if (mc != 0) {
            return want_min ? (mc < 0 ? a : b) : (mc > 0 ? a : b);
        }
    }
    /* value selection; first operand wins on equality, which is
     * also the magnitude tie-break */
    return want_min ? (vc <= 0 ? a : b) : (vc >= 0 ? a : b);
}

MSF_PF_T MSF_PF_FN(minimum)(MSF_PF_T a, MSF_PF_T b, msf_flags_t *flags)
{
    return MSF_PF_FN(minmax_core)(a, b, 1, 0, 0, flags);
}

MSF_PF_T MSF_PF_FN(maximum)(MSF_PF_T a, MSF_PF_T b, msf_flags_t *flags)
{
    return MSF_PF_FN(minmax_core)(a, b, 0, 0, 0, flags);
}

MSF_PF_T MSF_PF_FN(minimum_number)(MSF_PF_T a, MSF_PF_T b, msf_flags_t *flags)
{
    return MSF_PF_FN(minmax_core)(a, b, 1, 0, 1, flags);
}

MSF_PF_T MSF_PF_FN(maximum_number)(MSF_PF_T a, MSF_PF_T b, msf_flags_t *flags)
{
    return MSF_PF_FN(minmax_core)(a, b, 0, 0, 1, flags);
}

MSF_PF_T MSF_PF_FN(minimum_magnitude)(MSF_PF_T a, MSF_PF_T b,
                                      msf_flags_t *flags)
{
    return MSF_PF_FN(minmax_core)(a, b, 1, 1, 0, flags);
}

MSF_PF_T MSF_PF_FN(maximum_magnitude)(MSF_PF_T a, MSF_PF_T b,
                                      msf_flags_t *flags)
{
    return MSF_PF_FN(minmax_core)(a, b, 0, 1, 0, flags);
}

MSF_PF_T MSF_PF_FN(minimum_magnitude_number)(MSF_PF_T a, MSF_PF_T b,
                                             msf_flags_t *flags)
{
    return MSF_PF_FN(minmax_core)(a, b, 1, 1, 1, flags);
}

MSF_PF_T MSF_PF_FN(maximum_magnitude_number)(MSF_PF_T a, MSF_PF_T b,
                                             msf_flags_t *flags)
{
    return MSF_PF_FN(minmax_core)(a, b, 0, 1, 1, flags);
}

/* ---- Clause 9.7 NaN payloads (SF-1 Step 1) ----
 * Payload = trailing bits below the quiet bit (p-2 bits). The
 * family never signals and takes no flags. Setters build a
 * positive NaN from an admissible integral operand (quiet
 * 0..max, signaling 1..max; -0 admissible-as-0 for the quiet
 * form only) and deliver +0 for anything else, signaling NaN
 * inputs included. */

/* Exact encoding of a non-negative integer k < 2^p. */
static MSF_PF_T MSF_PF_FN(encode_u64_int)(uint64_t k)
{
    int bl = 0;
    uint64_t t = k;
    uint64_t bits;
    if (k == 0u) {
        return (MSF_PF_T)0u;
    }
    while (t != 0u) {
        bl++;
        t >>= 1;
    }
    bits = ((uint64_t)(MSF_PF_C(BIAS) + bl - 1) << MSF_PF_C(FRAC_BITS))
           | ((k << (MSF_PF_C(FRAC_BITS) - (bl - 1))) & MSF_PF_C(FRAC_MASK));
    return (MSF_PF_T)bits;
}

MSF_PF_T MSF_PF_FN(get_payload)(MSF_PF_T a)
{
    if (!MSF_PF_FN(is_nan)(a)) {
        /* -1: sign set, unit exponent, zero trailing field */
        return (MSF_PF_T)(MSF_PF_C(SIGN_MASK)
                          | ((uint64_t)MSF_PF_C(BIAS) << MSF_PF_C(FRAC_BITS)));
    }
    return MSF_PF_FN(encode_u64_int)((uint64_t)a & (MSF_PF_C(QUIET_BIT) - 1u));
}

static MSF_PF_T MSF_PF_FN(set_payload_core)(MSF_PF_T a, int signaling)
{
    int pbits = (int)MSF_PF_C(FRAC_BITS) - 1;
    msf_decoded_t d;
    uint64_t k;
    if (MSF_PF_FN(is_nan)(a) || MSF_PF_FN(is_infinite)(a)) {
        return (MSF_PF_T)0u;
    }
    if (MSF_PF_FN(is_zero)(a)) {
        /* +-0: admissible-as-0 for the quiet form only */
        return signaling ? (MSF_PF_T)0u : (MSF_PF_T)MSF_PF_C(DEFAULT_QNAN);
    }
    if (((uint64_t)a & MSF_PF_C(SIGN_MASK)) != 0u) {
        return (MSF_PF_T)0u;
    }
    d = msf_decode(MSF_PF_FN(fmt_idx)(), (uint64_t)a);
    /* finite nonzero positive: exact value sig * 2^exp */
    if (d.exp >= 0) {
        int bl = 128 - msf_u128_clz(d.sig);
        if (bl + d.exp > pbits) {
            return (MSF_PF_T)0u; /* integral but above max */
        }
        k = msf_u128_to_u64_trunc(msf_u128_shl(d.sig, (unsigned)d.exp));
    } else {
        int32_t s = -d.exp;
        if (s >= 128) {
            return (MSF_PF_T)0u; /* nonzero magnitude below 1 */
        }
        if (!msf_u128_is_zero(msf_u128_shl(d.sig, (unsigned)(128 - s)))) {
            return (MSF_PF_T)0u; /* low s bits set: not integral */
        }
        k = msf_u128_to_u64_trunc(msf_u128_shr(d.sig, (unsigned)s));
    }
    if ((k >> pbits) != 0u) {
        return (MSF_PF_T)0u; /* above max = 2^pbits - 1 */
    }
    if (signaling && k == 0u) {
        return (MSF_PF_T)0u;
    }
    return (MSF_PF_T)(MSF_PF_C(INFINITY)
                      | (signaling ? 0u : MSF_PF_C(QUIET_BIT)) | k);
}

MSF_PF_T MSF_PF_FN(set_payload)(MSF_PF_T a)
{
    return MSF_PF_FN(set_payload_core)(a, 0);
}

MSF_PF_T MSF_PF_FN(set_payload_signaling)(MSF_PF_T a)
{
    return MSF_PF_FN(set_payload_core)(a, 1);
}

#undef MSF_PF_C
#undef MSF_PF_T
#undef MSF_PF_FN
#undef MSF_PF_CAT
#undef MSF_PF_CAT2
#undef MSF_PF
