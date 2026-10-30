parcel-str: runner.c:236 reads C= token as flags for char-from lines
For: lead
tests/runner.c line 236 (process_char_line, bc15b2c): expect_flags reads tok[ntok-2], which for char-from lines (ntok 8) is the C= token, not the flags token tok[5]; strtoul base 16 turns "C=..." into 0x0c, so every from_* vector will flag-fail. Fix: read flags from tok[5] in the char-from branch. Full measured entry in ledger/parcel-str.md. to_* shapes unaffected. I keep coding; ping me when the fix lands on main and I will merge it.

Written: 2026-10-27 08:34:47 -0700
