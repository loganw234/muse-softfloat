# verifier-w5log2

## 2026-10-29 — verdict NOT READY (5 findings)

Copy `worktrees/verify5-log2` @ 31a0adc (parent 54ac1bb), clean
before and after (git status empty; all builds/probes outside the
copy in scratch/verifier-w5log2). Own adaptive-precision MPFR
decider written for this verification (vlog2.c: RNDN-only bracket,
two-ulp ends, five-mode first-principles grid narrow, specials and
power-exacts by exact integer tests; escalation 256..4096); the
copy's own harness rebuilt outside the copy as second route. No
foreign oracle executed; nothing with cft in its name touched.

Findings:
- F1 (a) kernel: `src/msf_math.c:1424` recentre test `>=` should be
  `>` (its own comment states `bitlen(a^2) > bit2`). Takes the
  recentre branch for mm in [1,sqrt2) and all exact powers:
  `log2(1.0)` returns garbage+inexact (f64 `34d1f49d2ff62bf3/10`,
  f16 `0000/18`), powers inexact with directed splits
  (f64 `log2(2.0)` te `.../10` vs exact `/00`). Repro:
  `vlog2.exe one f64 log2 3ff0000000000000` FAIL all modes; copy's
  own harness agrees (BAD) on the same cells.
- F2 (b) regen: `src/msf_explog_tables.h:22` EK_LOG `{146,242,300}`
  vs committed-generator-proven `{146,242,370}` (twice
  byte-identical regen; full-file diff is that one integer).
  Parcel ledger claims 370 proven+committed; WIDTHS.md row 31 says
  2^-370. ln2 diff ~2^-702.3 and term counts reproduce as claimed.
- F3 (b/c) seam: `tables/implemented.tsv:848` wave 4 vs
  `tables/operations.tsv:143` wave 5 for msf64_log2p1;
  `tools/gen_tables.py:290` asserts and aborts
  (`implemented.tsv wave drift: msf64_log2p1`), so committed
  generated files cannot re-derive (parcel claimed twice
  byte-stable). Tier-2 inventory itself is 57/57/0 from COVERAGE.
- F4 (b) generator: `tests/gen_vectors_explog.py:58`
  UNDERFLOW = 0x04 (parent: 0x08); settled cross-check disagrees on
  the first underflow cell and generation exits 1 with no output.
  Scratch-only 0x08 restore completes: f16/f32 byte-identical,
  Step-3a prefixes intact (14848/15353/15418 lines), log settled
  tables agree with the C decider everywhere.
- F5 committed vector: `tests/vectors/explog-f64.vec:25369`
  `msf64_log2p1 te bff...0 -> fff...0 00` should be `02` like its
  tz/tp/tn/ta siblings (kernel delivers /02; runner FAILs the line).

Evidence: one-cell probes 379 cells (261 pass; 118 fail, all
powers/mm<sqrt2/tiny-residue per F1); f16 exhaustive 310 mismatches
/ 655360 checked by BOTH deciders (copy harness: 310/1310720 all4);
f32 shards 0,1,128,255 x log pair (counts in report; full
re-exhaustion NOT re-executed, stated); runner over committed
vectors total 90315 passed 87884 failed 2431 (2391 powers + 40
tiny) VERDICT: FAIL; ARM -Os AND -O3 -Werror clean, symbol scan
clean; NC-1ULP (log hardest) refused and NC-POLEFLAG mutant bites
(5 cells x 5 modes flag mismatch); final_undecided 0 and
decider-undecided 0 in every leg run here. Full record:
scratch/verifier-w5log2/report.md (first line NOT READY).
For: lead
