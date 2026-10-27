/* msf_performat.inc - classification and sign-bit operations,
 * instantiated once per format by msf16.c / msf32.c / msf64.c with
 * MSF_PF set to 16, 32, or 64. Constants come only from the
 * generated msf_formats.h (SF-0 Section 6 item 3). These operations
 * never signal (5.5.1, 5.7.2), so none takes a flags pointer.
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

#undef MSF_PF_C
#undef MSF_PF_T
#undef MSF_PF_FN
#undef MSF_PF_CAT
#undef MSF_PF_CAT2
#undef MSF_PF
