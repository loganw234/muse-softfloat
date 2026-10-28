/* ias15_host_shim.c - host soft-float interposition for the demo.
 * SPDX-License-Identifier: MIT
 *
 * The demo's soft IAS15 build compiles the workload with
 * -msoft-float -mno-sse2, which turns every binary64 operation
 * into a runtime libcall (__adddf3 and family).  This file
 * provides those libcalls over the muse-softfloat core, so the
 * soft binary's floating point IS the library, operation for
 * operation - the host analogue of the board's AEABI wraps.
 * It contains no floating-point arithmetic itself (memcpy bit
 * casts only) and is compiled with the same soft flags.
 *
 * Comparison-libcall contract: each routine returns int64_t
 * -1/0/+1 for ordered operands; unordered returns are +1
 * (eq/ne/lt/le) and -1 (gt/ge), the unique classes that make the
 * compiler's emitted sign/zero tests yield the IEEE predicates
 * (derived from emitted code and validated by branch battery in
 * the original IAS15 host proof; the end-to-end hash equality of
 * the demo run re-validates it here).
 *
 * Rounding is fixed ties-to-even: IAS15 assumes the default FP
 * environment and never touches fenv.  Flags accumulate into
 * static state the workload never reads.  Libm names outside the
 * earned surface are loud traps (message + exit), never silent
 * approximations.  demo_ias15_shim_ops() counts interposed
 * arithmetic calls so the demo can refuse a vacuous soft build.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "muse_softfloat.h"

static msf_flags_t g_flags;
static unsigned long long g_ops;
static unsigned long long g_traps;

unsigned long long demo_ias15_shim_ops(void) { return g_ops; }
unsigned long long demo_ias15_shim_traps(void) { return g_traps; }

static uint64_t d2u(double v) { uint64_t u; memcpy(&u, &v, 8); return u; }
static double u2d(uint64_t u) { double v; memcpy(&v, &u, 8); return v; }
static uint32_t f2u(float v) { uint32_t u; memcpy(&u, &v, 4); return u; }
static float u2f(uint32_t u) { float v; memcpy(&v, &u, 4); return v; }
#define RM MSF_ROUND_TIES_TO_EVEN

double __adddf3(double a, double b) { g_ops++; return u2d(msf64_add(d2u(a), d2u(b), RM, &g_flags)); }
double __subdf3(double a, double b) { g_ops++; return u2d(msf64_sub(d2u(a), d2u(b), RM, &g_flags)); }
double __muldf3(double a, double b) { g_ops++; return u2d(msf64_mul(d2u(a), d2u(b), RM, &g_flags)); }
double __divdf3(double a, double b) { g_ops++; return u2d(msf64_div(d2u(a), d2u(b), RM, &g_flags)); }

double sqrt(double a) { g_ops++; return u2d(msf64_sqrt(d2u(a), RM, &g_flags)); }
double fma(double a, double b, double c) { g_ops++; return u2d(msf64_fma(d2u(a), d2u(b), d2u(c), RM, &g_flags)); }
double fabs(double a) { g_ops++; return u2d(msf64_abs(d2u(a))); }
double copysign(double a, double b) { g_ops++; return u2d(msf64_copy_sign(d2u(a), d2u(b))); }

/* -1: a<b, 0: a==b, +1: a>b, 2: unordered */
static int cmp3(uint64_t a, uint64_t b)
{
    if (msf64_is_nan(a) || msf64_is_nan(b)) return 2;
    if (msf64_compare_quiet_less(a, b, &g_flags)) return -1;
    if (msf64_compare_quiet_greater(a, b, &g_flags)) return 1;
    return 0;
}
int64_t __eqdf2(double a, double b) { g_ops++; int c = cmp3(d2u(a), d2u(b)); return c == 2 ? 1 : c; }
int64_t __nedf2(double a, double b) { g_ops++; int c = cmp3(d2u(a), d2u(b)); return c == 2 ? 1 : c; }
int64_t __ltdf2(double a, double b) { g_ops++; int c = cmp3(d2u(a), d2u(b)); return c == 2 ? 1 : c; }
int64_t __ledf2(double a, double b) { g_ops++; int c = cmp3(d2u(a), d2u(b)); return c == 2 ? 1 : c; }
int64_t __gtdf2(double a, double b) { g_ops++; int c = cmp3(d2u(a), d2u(b)); return c == 2 ? -1 : c; }
int64_t __gedf2(double a, double b) { g_ops++; int c = cmp3(d2u(a), d2u(b)); return c == 2 ? -1 : c; }
int64_t __unorddf2(double a, double b) { g_ops++; return (msf64_is_nan(d2u(a)) || msf64_is_nan(d2u(b))) ? 1 : 0; }

double __floatsidf(int32_t a) { g_ops++; return u2d(msf64_from_i32(a, RM, &g_flags)); }
double __floatdidf(int64_t a) { g_ops++; return u2d(msf64_from_i64(a, RM, &g_flags)); }
double __floatunsidf(uint32_t a) { g_ops++; return u2d(msf64_from_u32(a, RM, &g_flags)); }
double __floatundidf(uint64_t a) { g_ops++; return u2d(msf64_from_u64(a, RM, &g_flags)); }
int32_t __fixdfsi(double a) { g_ops++; return msf64_to_i32_toward_zero(d2u(a), &g_flags); }
int64_t __fixdfdi(double a) { g_ops++; return msf64_to_i64_toward_zero(d2u(a), &g_flags); }
uint32_t __fixunsdfsi(double a) { g_ops++; return msf64_to_u32_toward_zero(d2u(a), &g_flags); }
uint64_t __fixunsdfdi(double a) { g_ops++; return msf64_to_u64_toward_zero(d2u(a), &g_flags); }

double __extendsfdf2(float a) { g_ops++; return u2d(msf64_from_f32(f2u(a), RM, &g_flags)); }
float __truncdfsf2(double a) { g_ops++; return u2f(msf32_from_f64(d2u(a), RM, &g_flags)); }

/* Libm traps: names the workload links but must never execute.
 * Any call is a loud failure, never an approximate answer. */
static double trap1(const char *name, double a)
{
    (void)a;
    g_traps++;
    fprintf(stderr, "ias15_host_shim TRAP: %s called (not interposed)\n", name);
    exit(3);
}
#define TRAP1(n) double n(double a) { return trap1(#n, a); }
TRAP1(acos) TRAP1(acosh) TRAP1(asin) TRAP1(atan) TRAP1(cbrt) TRAP1(cos)
TRAP1(cosh) TRAP1(exp) TRAP1(floor) TRAP1(log) TRAP1(log10) TRAP1(sin)
TRAP1(sinh) TRAP1(tan) TRAP1(tanh)
double atan2(double a, double b) { (void)b; return trap1("atan2", a); }
double pow(double a, double b) { (void)b; return trap1("pow", a); }
double fmod(double a, double b) { (void)b; return trap1("fmod", a); }
void sincos(double a, double *s, double *c) { (void)s; (void)c; (void)trap1("sincos", a); }
