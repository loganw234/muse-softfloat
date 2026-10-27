/* ias15_selftest.h - on-silicon validation of the AEABI compat
 * surface, mirroring the host shim selftest of the IAS15 host proof
 * (scratch/ias15/work/shim_selftest.c). Run on the board BEFORE any
 * IAS15 hash from that board is trusted: every C-level double
 * operation/branch (which reaches compat/msf_aeabi.c through the
 * compiler's AEABI helpers) must equal the direct msf64_* call
 * bit-for-bit. */
#ifndef IAS15_SELFTEST_H
#define IAS15_SELFTEST_H

/* full=0: directed operands only (all pairs + singles + conversions).
 * full=1: plus IAS15_SELFTEST_LCG_PAIRS fixed-seed LCG pairs.
 * Prints up to 10 FAIL/NANDIFF lines (integer/hex only). Returns the
 * number of failed checks (0 = pass); counts via out params if given. */
int msf_aeabi_selftest(int full,
                       unsigned long long *checks_out,
                       unsigned long long *fails_out);

#endif /* IAS15_SELFTEST_H */
