/* msf_aeabi.c - AEABI binary64 helpers over the gated msf64 core.
 *
 * House style follows msf_wrap.c: this translation unit contains no
 * C floating-point arithmetic (a helper that used `a + b` on doubles
 * would call itself); every value crosses between C types and core
 * bit containers by memcpy, through the bit casts in msf_wrap.h.
 * Compile it with -ffp-contract=off like the rest of the compat
 * layer. It deliberately does not include pico.h: per-core state
 * comes through msf_wrap_state(), so this file also builds for host
 * logic tests and standalone cross-compile checks.
 *
 * Comparison helpers return the AEABI boolean (0/1 in r0) of the
 * quiet IEEE predicates: unordered operands make every ordered
 * predicate false and dcmpun true, which is what the compiler's
 * emitted branch code expects (measured, census in the ias15-pico
 * design entry). Flags raised by the core comparisons (invalid on
 * signaling NaNs) accumulate in the per-core state.
 */
#include "msf_aeabi.h"
#include "msf_wrap.h"

static msf_wrap_state_t *st(void)
{
    return msf_wrap_state();
}

double __wrap___aeabi_dadd(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_add(msf64_from_double(a), msf64_from_double(b),
                                     s->rounding, &s->flags));
}

double __wrap___aeabi_dsub(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_sub(msf64_from_double(a), msf64_from_double(b),
                                     s->rounding, &s->flags));
}

double __wrap___aeabi_drsub(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_sub(msf64_from_double(b), msf64_from_double(a),
                                     s->rounding, &s->flags));
}

double __wrap___aeabi_dmul(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_mul(msf64_from_double(a), msf64_from_double(b),
                                     s->rounding, &s->flags));
}

double __wrap___aeabi_ddiv(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_div(msf64_from_double(a), msf64_from_double(b),
                                     s->rounding, &s->flags));
}

double __wrap___aeabi_dneg(double a)
{
    return msf64_to_double(msf64_negate(msf64_from_double(a)));
}

int __wrap___aeabi_dcmpeq(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_compare_quiet_equal(msf64_from_double(a), msf64_from_double(b),
                                     &s->flags);
}

int __wrap___aeabi_dcmplt(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_compare_quiet_less(msf64_from_double(a), msf64_from_double(b),
                                    &s->flags);
}

int __wrap___aeabi_dcmple(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_compare_quiet_less_equal(msf64_from_double(a),
                                          msf64_from_double(b), &s->flags);
}

int __wrap___aeabi_dcmpgt(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_compare_quiet_greater(msf64_from_double(a), msf64_from_double(b),
                                       &s->flags);
}

int __wrap___aeabi_dcmpge(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_compare_quiet_greater_equal(msf64_from_double(a),
                                             msf64_from_double(b), &s->flags);
}

int __wrap___aeabi_dcmpun(double a, double b)
{
    msf_wrap_state_t *s = st();
    return msf64_compare_quiet_unordered(msf64_from_double(a),
                                         msf64_from_double(b), &s->flags);
}

double __wrap___aeabi_i2d(int a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_from_i32(a, s->rounding, &s->flags));
}

double __wrap___aeabi_ui2d(unsigned int a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_from_u32(a, s->rounding, &s->flags));
}

double __wrap___aeabi_l2d(long long a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_from_i64(a, s->rounding, &s->flags));
}

double __wrap___aeabi_ul2d(unsigned long long a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_from_u64(a, s->rounding, &s->flags));
}

int __wrap___aeabi_d2iz(double a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_i32_toward_zero(msf64_from_double(a), &s->flags);
}

unsigned int __wrap___aeabi_d2uiz(double a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_u32_toward_zero(msf64_from_double(a), &s->flags);
}

long long __wrap___aeabi_d2lz(double a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_i64_toward_zero(msf64_from_double(a), &s->flags);
}

unsigned long long __wrap___aeabi_d2ulz(double a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_u64_toward_zero(msf64_from_double(a), &s->flags);
}

double __wrap___aeabi_f2d(float a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_from_f32(msf32_from_float(a),
                                          s->rounding, &s->flags));
}

float __wrap___aeabi_d2f(double a)
{
    msf_wrap_state_t *s = st();
    return msf32_to_float(msf32_from_f64(msf64_from_double(a),
                                         s->rounding, &s->flags));
}

double __wrap_sqrt(double a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_sqrt(msf64_from_double(a),
                                      s->rounding, &s->flags));
}

double __wrap_fabs(double a)
{
    return msf64_to_double(msf64_abs(msf64_from_double(a)));
}

double __wrap_fma(double a, double b, double c)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_fma(msf64_from_double(a), msf64_from_double(b),
                                     msf64_from_double(c),
                                     s->rounding, &s->flags));
}

double __wrap_sinpi(double a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_sin_pi(msf64_from_double(a),
                                        s->rounding, &s->flags));
}

double __wrap_cospi(double a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_cos_pi(msf64_from_double(a),
                                        s->rounding, &s->flags));
}

double __wrap_floor(double a)
{
    msf_wrap_state_t *s = st();
    return msf64_to_double(msf64_round_to_integral_toward_negative(
        msf64_from_double(a), &s->flags));
}

/* ---- Named traps -------------------------------------------------
 * None of these is implemented by the core; a wrapped binary that
 * reaches one has left the proven surface and must stop loudly
 * (SF-0 Sec.11: no approximate math). The canonical quiet NaN bits
 * are returned only if a non-conforming trap handler returns. */
static double trap_bits(const char *name)
{
    msf_aeabi_trap(name);
    return msf64_to_double((msf64_t)0x7FF8000000000000ULL);
}

#define MSF_TRAP1(nm) double __wrap_##nm(double a) { (void)a; return trap_bits(#nm); }
#define MSF_TRAP2(nm) double __wrap_##nm(double a, double b) \
    { (void)a; (void)b; return trap_bits(#nm); }

MSF_TRAP1(acos)
MSF_TRAP1(acosh)
MSF_TRAP1(asin)
MSF_TRAP1(asinh)
MSF_TRAP1(atan)
MSF_TRAP1(atanh)
MSF_TRAP1(cbrt)
MSF_TRAP1(ceil)
MSF_TRAP1(cos)
MSF_TRAP1(cosh)
MSF_TRAP1(exp)
MSF_TRAP1(exp2)
MSF_TRAP1(expm1)
/* floor is NOT trapped: __wrap_floor above is earned (Step 2c). */
MSF_TRAP1(log)
MSF_TRAP1(log2)
MSF_TRAP1(log10)
MSF_TRAP1(log1p)
MSF_TRAP1(sin)
MSF_TRAP1(sinh)
MSF_TRAP1(tan)
MSF_TRAP1(tanh)
MSF_TRAP1(erf)
MSF_TRAP1(erfc)
MSF_TRAP1(tgamma)
MSF_TRAP1(lgamma)
MSF_TRAP1(trunc)
MSF_TRAP1(round)
MSF_TRAP1(nearbyint)
MSF_TRAP1(rint)
MSF_TRAP2(atan2)
MSF_TRAP2(pow)
MSF_TRAP2(fmod)
MSF_TRAP2(remainder)
MSF_TRAP2(hypot)
MSF_TRAP2(fmax)
MSF_TRAP2(fmin)
MSF_TRAP2(fdim)
/* copysign is NOT trapped here: msf_wrap.c owns __wrap_copysign. */
#undef MSF_TRAP1
#undef MSF_TRAP2
