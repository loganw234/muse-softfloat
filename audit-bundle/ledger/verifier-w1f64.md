
## 2026-10-27 05:44:40 -0700 - wave-1 binary64 parcel verdict: NOT READY (3 regressions, 3 wrong data)

Measured: verify-f64@d1e9442, Git Bash, pinned x86_64-w64-mingw32 gcc 16.1.0
FLT_EVAL_METHOD=0, machine under third-party load. smoke PASS 7s (29982
vectors, 9/9 controls refused); standard PASS 38s (+1117504). Committed
f64 directed 11057 total / 45 fail. Berkeley independent reruns
(MSF_TESTFLOAT_GEN pinned oracle, tininess-after): 3,795,688 cases /
2307 fails / 3840 named f64_to_f32 skips. Own Fraction reference
(scratch/verifier-w1f64/v-exact.py, never imports the copy generator):
29028 cases / 520 fails, residue exactly the three code mutations by
class audit. gen_tables regen: 4/4 byte-identical. Branch generator
regenerates branch vectors byte-identically (all 5 files). implemented
rows: 173 new msf64 wave-1, 0 removed. Full evidence with vector lines:
scratch/verifier-w1f64/report.md.
Believed: NOT READY. (a) div_core drops divisionByZero (src/msf64.c:201;
branch :202 has it). (a) add_terms zero-zero sign inverted to
roundTowardPositive (:93; branch has Negative). (a) FMA inf/inf invalid
condition inverted to == (:281; branch has !=). (b) generator F_UNF=0x04
should be 0x08 (gen_vectors_f64.py:27; branch has 0x08). (b) committed
arith-f64.vec:5 expects 00, correct 01 (0/0 invalid; branch line is 01).
(b) d1e9442 message claims 11,057 pass and 10,418,176 Berkeley cases at
0 failures; measured 11012/45 and per-mode div/mulAdd failures (the
parcel's own div-te log claims 46464/0 for the identical case replayed
here as 46135/329). Off-limits diffs vs base are all lead-owned and
byte-identical to parcel branch w1-f64@cb10ee2. Six notes N1-N6 in the
report (negative-NaN payload order observed descending, round_inc TA
unreachable, f64_to_f32 sibling skips, symbol-scan SKIP, from_f64
Berkeley-generator absence, min-normal-with-UNF adjudicated correct per
the documented Clause 7.5 reading). No fourth wrong table entry found.
Fixed nothing in the copy; no commits; board/lead/cft untouched.
For: lead
