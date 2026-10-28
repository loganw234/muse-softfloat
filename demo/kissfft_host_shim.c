/* kissfft_host_shim.c - host stand-in for the Pico-bound wrapper parts.
 * SPDX-License-Identifier: MIT
 *
 * compat/msf_aeabi.c (which provides __wrap_sinpi/__wrap_cospi/
 * __wrap_floor for the KissFFT host proof) is deliberately
 * pico-free, but it needs msf_wrap_state() and the bit casts from
 * compat/msf_wrap.c - and that file includes pico.h for its
 * per-core state.  This shim provides the same contract for a
 * single-threaded host process: one zero-initialised state
 * (ties-to-even), memcpy bit casts, the copysign wraps, and the
 * trap sink as a loud abort.  Firmware links the real
 * compat/msf_wrap.c instead; nothing here is in a board binary.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "msf_wrap.h"

static msf_wrap_state_t g_state;

msf_wrap_state_t *msf_wrap_state(void) { return &g_state; }

msf32_t msf32_from_float(float x) { msf32_t r; memcpy(&r, &x, 4); return r; }
float msf32_to_float(msf32_t x) { float r; memcpy(&r, &x, 4); return r; }
msf64_t msf64_from_double(double x) { msf64_t r; memcpy(&r, &x, 8); return r; }
double msf64_to_double(msf64_t x) { double r; memcpy(&r, &x, 8); return r; }

float __wrap_copysignf(float x, float y)
{
    return msf32_to_float(msf32_copy_sign(msf32_from_float(x), msf32_from_float(y)));
}

double __wrap_copysign(double x, double y)
{
    return msf64_to_double(msf64_copy_sign(msf64_from_double(x), msf64_from_double(y)));
}

void msf_aeabi_trap(const char *name)
{
    fprintf(stderr, "MSF-TRAP %s\n", name);
    abort();
}
