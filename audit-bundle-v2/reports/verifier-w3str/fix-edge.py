#!/usr/bin/env python3
"""Fix the OR-only flag convention + LEN miscount in vw_edge.c."""
import re
p = r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\vw_edge.c"
s = open(p).read()
# NULL-s block: init fl=0 (callee ORs only; runner zeroes before each call)
s = s.replace("""    /* NULL s: +0, consumed 0, no flags (all input ops, all widths) */
    fl = 0xFF; c = 99;
    msf16_from_decimal(NULL, &c, MSF_ROUND_TIES_TO_EVEN, &fl);
    CHECK(fl == 0, "null-s-dec16-flags-clear");
    fl = 0xFF; c = 99;""",
"""    /* NULL s: +0, consumed 0, no flags (all input ops, all widths).
     * Flags are OR-only by codebase convention (kernel uses |=);
     * the runner zeroes before each call, so init 0 here. */
    fl = 0; c = 99;
    msf16_from_decimal(NULL, &c, MSF_ROUND_TIES_TO_EVEN, &fl);
    CHECK(fl == 0, "null-s-dec16-flags-clear");
    fl = 0; c = 99;""")
s = s.replace("fl = 0xFF; c = 99;", "fl = 0; c = 99;")
s = s.replace('CHECK(n == 7 && (unsigned char)big[0] == 0xAA, "zero-buf-hex16");',
              'CHECK(n == 6 && (unsigned char)big[0] == 0xAA, "zero-buf-hex16");')
open(p, "w", newline="\n").write(s)
print("patched")
