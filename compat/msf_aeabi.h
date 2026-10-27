/* msf_aeabi.h - AEABI double-precision compat surface over msf64.
 *
 * SF-0 Sec.3.4 layer 1, first workload consumer IAS15 (SF-0 Sec.9).
 * These are the compiler-emitted runtime helpers for binary64 on
 * Cortex-M0+ soft-float ABI, routed to the gated core by the SDK's
 * own --wrap mechanism (see board/CMakeLists.txt): link with
 * --wrap=__aeabi_dadd etc. and references resolve to the
 * __wrap___aeabi_* bodies in msf_aeabi.c. copysignf/copysign stay in
 * msf_wrap.c, unchanged from P0.
 *
 * State contract is the msf_wrap.h contract: rounding and flags are
 * the per-core msf_wrap_state() (shared by thread and IRQ execution
 * on one core, never across cores, never implicitly saved/restored).
 * Zero-initialised state means ties-to-even rounding.
 *
 * The measured emitted surface this covers (arm-none-eabi-gcc
 * 14.2.1, -mcpu=cortex-m0plus -mfloat-abi=soft, -O2/-O3; census in
 * the ias15-pico ledger design entry): dadd/dsub/dmul/ddiv,
 * dcmpeq/lt/le/gt/ge/un (boolean 0/1 in r0 - this compiler emits no
 * condition-code cdcmple-family helpers), i2d/ui2d/l2d/ul2d,
 * d2iz/d2uiz/d2lz/d2ulz, f2d/d2f, and the libm name sqrt. dneg,
 * drsub, fabs and fma are provided as the same-family neighbours so
 * no libgcc/libm double body enters a wrapped binary through them.
 * Everything else libm-shaped is a named trap (msf_aeabi_trap),
 * never an approximation.
 *
 * Deliberate bare-metal omissions, documented: sqrt/fma here do not
 * set errno; invalid operations accumulate MSF_FLAG_INVALID in the
 * per-core state exactly as the core reports them.
 */
#ifndef MSF_AEABI_H
#define MSF_AEABI_H

#include "../include/muse_softfloat.h"

/* Trap sink, implemented by the firmware target linking this layer
 * (print the name, then stop loudly). Must not return; msf_aeabi.c
 * still returns a canonical NaN pattern if it ever does. */
void msf_aeabi_trap(const char *name);

double __wrap___aeabi_dadd(double a, double b);
double __wrap___aeabi_dsub(double a, double b);
double __wrap___aeabi_drsub(double a, double b); /* returns b - a (RTABI) */
double __wrap___aeabi_dmul(double a, double b);
double __wrap___aeabi_ddiv(double a, double b);
double __wrap___aeabi_dneg(double a);

int __wrap___aeabi_dcmpeq(double a, double b);
int __wrap___aeabi_dcmplt(double a, double b);
int __wrap___aeabi_dcmple(double a, double b);
int __wrap___aeabi_dcmpgt(double a, double b);
int __wrap___aeabi_dcmpge(double a, double b);
int __wrap___aeabi_dcmpun(double a, double b);

double __wrap___aeabi_i2d(int a);
double __wrap___aeabi_ui2d(unsigned int a);
double __wrap___aeabi_l2d(long long a);
double __wrap___aeabi_ul2d(unsigned long long a);
int __wrap___aeabi_d2iz(double a);
unsigned int __wrap___aeabi_d2uiz(double a);
long long __wrap___aeabi_d2lz(double a);
unsigned long long __wrap___aeabi_d2ulz(double a);
double __wrap___aeabi_f2d(float a);
float __wrap___aeabi_d2f(double a);

double __wrap_sqrt(double a);
double __wrap_fabs(double a);
double __wrap_fma(double a, double b, double c);

#endif /* MSF_AEABI_H */
