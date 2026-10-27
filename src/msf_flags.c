/* msf_flags.c - the six 5.7.4 flag operations over caller-owned
 * state, plus the global 5.7.1 version predicates (SF-0 2.4).
 * Groups are masked to the five Clause 7 bits: bits outside the
 * subset are not flags and are ignored everywhere here.
 */
#include "msf_internal.h"

void msf_lower_flags(msf_flags_t *state, msf_flags_t group)
{
    *state = (msf_flags_t)(*state & ~(group & MSF_FLAGS_ALL));
}

void msf_raise_flags(msf_flags_t *state, msf_flags_t group)
{
    *state = (msf_flags_t)(*state | (group & MSF_FLAGS_ALL));
}

int msf_test_flags(const msf_flags_t *state, msf_flags_t group)
{
    return (*state & group & MSF_FLAGS_ALL) != 0u;
}

int msf_test_saved_flags(msf_saved_flags_t saved, msf_flags_t group)
{
    return ((msf_flags_t)saved & group & MSF_FLAGS_ALL) != 0u;
}

void msf_restore_flags(msf_flags_t *state, msf_saved_flags_t saved,
                       msf_flags_t group)
{
    msf_flags_t g = group & MSF_FLAGS_ALL;
    *state = (msf_flags_t)((*state & ~g) | ((msf_flags_t)saved & g));
}

msf_saved_flags_t msf_save_all_flags(const msf_flags_t *state)
{
    return (msf_saved_flags_t)(*state & MSF_FLAGS_ALL);
}

int msf_is754version1985(void)
{
    return 0;
}

int msf_is754version2008(void)
{
    return 0;
}

int msf_is754version2019(void)
{
    return 1;
}
