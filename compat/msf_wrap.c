/* msf_wrap.c - per-core wrapper state + first wrapped symbols.
 *
 * P0 proves the interposition mechanism end-to-end (SF-0 Section 6
 * item 7) with copysignf/copysign, the two wrapped libm names that
 * map exactly onto gated core operations. The AEABI arithmetic
 * surface lands with the operations it wraps (Wave 3).
 *
 * Link with --wrap=copysignf / --wrap=copysign (the SDK's own
 * pico_wrap_function mechanism, survey S3 section 1.1) so compiler
 * calls resolve to __wrap_* here; __real_* stays available.
 */
#include <string.h>
#include "pico.h"
#include "msf_wrap.h"

/* One state per RP2040 core. Wrapper static RAM is counted here,
 * never in the core's zero-static-RAM budget (SF-0 Section 8). */
static msf_wrap_state_t g_state[2];

msf_wrap_state_t *msf_wrap_state(void)
{
    return &g_state[get_core_num() & 1u];
}

msf32_t msf32_from_float(float x)
{
    msf32_t r;
    memcpy(&r, &x, sizeof(r));
    return r;
}

float msf32_to_float(msf32_t x)
{
    float r;
    memcpy(&r, &x, sizeof(r));
    return r;
}

msf64_t msf64_from_double(double x)
{
    msf64_t r;
    memcpy(&r, &x, sizeof(r));
    return r;
}

double msf64_to_double(msf64_t x)
{
    double r;
    memcpy(&r, &x, sizeof(r));
    return r;
}

float __wrap_copysignf(float x, float y)
{
    return msf32_to_float(msf32_copy_sign(msf32_from_float(x), msf32_from_float(y)));
}

double __wrap_copysign(double x, double y)
{
    return msf64_to_double(msf64_copy_sign(msf64_from_double(x), msf64_from_double(y)));
}

#ifdef MSF_WRAP_SELFTEST
void msf_wrap_selftest_raise(msf_flags_t group)
{
    msf_raise_flags(&msf_wrap_state()->flags, group);
}
#endif
