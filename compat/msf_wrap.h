/* msf_wrap.h - AEABI/toolchain compatibility layer state (SF-0 3.4).
 *
 * This layer, never the core, owns per-core rounding/flags state so
 * compiler-emitted helper calls have somewhere to accumulate flags.
 * Contract that follows from per-core state (SF-0 3.4): the state is
 * shared between thread and IRQ execution ON THE SAME CORE and never
 * between cores; the wrapper does not implicitly save or restore it
 * across interrupts or RTOS switches - an IRQ/task layer using these
 * helpers must save/restore via the core flag operations, or call
 * the stateless core API with its own state.
 *
 * Bit-cast helpers between C arithmetic types and core bit
 * containers live here too, and nowhere else (SF-0 3.3).
 */
#ifndef MSF_WRAP_H
#define MSF_WRAP_H

#include "../include/muse_softfloat.h"

typedef struct msf_wrap_state {
    msf_rounding_t rounding;
    msf_flags_t flags;
} msf_wrap_state_t;

/* State for the core the caller is running on. */
msf_wrap_state_t *msf_wrap_state(void);

/* Bit casts (no arithmetic, no flags). */
msf32_t msf32_from_float(float x);
float msf32_to_float(msf32_t x);
msf64_t msf64_from_double(double x);
double msf64_to_double(msf64_t x);

#ifdef MSF_WRAP_SELFTEST
/* Test-only: raise flag bits in the current core's wrapper state so
 * interposition self-tests can watch state isolation directly. */
void msf_wrap_selftest_raise(msf_flags_t group);
#endif

#endif /* MSF_WRAP_H */
