# parcel-f64 report (Wave 1, binary64)

Status: RESTATED POST-MERGE by regater-f64, 2026-10-27. Every
PENDING-POSTMERGE section below now carries its measured outcome;
the pre-merge text is kept where it records history and is marked
as such. Final verdict at the end: READY.

## Deliverable and commits

- Worktree worktrees/w1-f64, branch w1-f64, base
  4cdb912dbd5ebda4fa2bc29168883dc4527d4091.
- Checkpoint commit 51533243a29e3a026493b8e3e04d2b2711ac4b4a:
  Implemented the Wave 1 binary64 parcel (173 instantiations).
- Coverage count measured before coding: docs/COVERAGE.tsv filtered
  wave=1 and name prefix msf64_ = 173 (wave-1 total 346), matching
  the brief. Script scratch/parcel-f64/inspect2.py.
- Owned files changed: src/msf64.c (880 lines);
  tests/gen_vectors_f64.py (900 lines; hand-written total 1,780 of
  the 3,000 ceiling); five new tests/vectors/*f64*.vec files
  (11,053 cases, 998,368 bytes total, under the 1 MB ceiling);
  173 rows appended only at the end of tables/implemented.tsv;
  regenerated include/muse_softfloat.h, tests/msf_dispatch.h,
  docs/COVERAGE.tsv (783 instantiations, 236 implemented, drift
  byte-clean). No off-limits file edited; kernel and ingest defects
  were escalated, not edited.
- Escalation test filed ledger/urgent/parcel-f64-test.md at
  21:45 -0700 (lead cleared). Design entry
  ledger/parcel-f64.md 2026-10-26 21:55:22 -0700, confirmed by lead
  21:56:25 with the 118-bit window invariant now stated in code at
  add_terms.
- Machine was under third-party load for every timed run below;
  all times are wall times under that load and are not rates or
  performance claims.
- Re-gate (regater-f64, 2026-10-27 from 05:04 -0700): merged lead
  fixes b37fb12 (via 53acb1a) into the worktree as merge commit
  80cbc97. Only conflict was tables/implemented.tsv, resolved as
  the union of rows with LF endings (244 lines: 71 base plus the
  173 parcel rows, 0 theirs-only rows beyond the LF
  normalisation; scratch/parcel-f64/regate-resolve.py). Re-ran
  tools/gen_tables.py: output byte-identical to the committed
  generated files (783 instantiations, 236 implemented), so no
  generated file changed in the merge. Re-gate commit cb10ee2
  adds four Clause 7.5 second-shape directed cases (test group 4
  restatement): hand-written total now 1,788 of 3,000
  (src/msf64.c 880, tests/gen_vectors_f64.py 908); committed
  parcel vector files now 11,057 cases, 998,736 bytes. Drivers
  scratch/parcel-f64/regate-step2.sh, regate-step3.sh,
  regate-step45.sh, regate-fix-directed.sh; outer logs alongside
  them. Worktree clean at cb10ee2; never pushed.

## Implementation summary

Every op: msf_decode -> msf_nan_delivery at dest f64 in operand
order -> special cases -> exact msf_u128 work -> one msf_pack_f64.
add/sub/mul/div x4, sqrt x2, fma x8, convertFormat x2, from-int x8,
to-int 10x8, compares 22x2, totalOrder/Mag, rint x6, nextUp/Down,
remainder, scaleB, logB. Details are the design entry; the code
states the window bound where the add/FMA kernel lives.

## Test group 1: run.sh smoke (regression)

- Run 2026-10-26 22:18 (8s wall under load), log
  worktrees/w1-f64/build/w1/logs/run-smoke-1.log: drift clean,
  host build clean, unit PASS, 29,982 committed vectors PASS
  (provenance printed), type scan clean, ARM symbol scan clean
  (19 undefined, all own/integer helpers), controls 1-8 refused.
  Final verdict FAIL only at control planned-only-verdict, which
  names msf64_add (now implemented here). Escalated in
  ledger/urgent/parcel-f64-control9.md; recorded as green-but-for
  that control by name, not as PASS.
- RESTATED POST-MERGE: final runs 2026-10-27 05:11:43 (smoke,
  8s wall under load) and 05:11:51 (standard, 28s), logs
  worktrees/w1-f64/build/w1/logs/regate-run-smoke.log and
  regate-run-standard.log (driver regate-step45.sh). Smoke PASS:
  drift clean (4 generated files byte-identical), unit PASS,
  29,982 committed vectors PASS, type and ARM symbol scans clean
  (19 undefined), all 9 controls refused including
  planned-only-verdict now naming msf16_add. Standard PASS:
  smoke contents plus 1,117,504 generated (917,504 f16-exhaustive
  + 200,000 pack64 sweep) PASS. An earlier identical pair at
  05:07 (before the four directed cases were added) also passed;
  the 05:11 pair is the final evidence against cb10ee2.

## Test group 2: Berkeley sweeps (build/w1, seed 1)

Driver scratch/parcel-f64/berkeley.sh; per-case logs in
worktrees/w1-f64/build/w1/logs/*.verify.log; summarizer
scratch/parcel-f64/summarize_logs.py. Ingest needs
MSF_TESTFLOAT_GEN set explicitly in a worktree (the ingest default
path assumes the muse-softfloat layout); recorded in every driver.

Level 1 complete, modes te tz tp tn ta where applicable:
- f64_add, f64_sub: 5 modes x 46,464 PASS each (464,640 total).
- f64_sqrt: 5 x 768 PASS. f64_rem (-): 46,464 PASS (confirms
  remainder(5,3) = -1 reading).
- f64_roundToInt: 5 named forms x 768 PASS.
- f32_to_f64: 5 x 600 PASS.
- f64_to_i32/i64/ui32/ui64: 5 named forms x 768 PASS each function.
- i32/i64/ui32/ui64_to_f64: 5 x 372/756/372/756 PASS.
- f64_mul, f64_div: tz PASS complete; te/tp/tn/ta FAIL only the
  ruled pack-tininess flag class (mul 16/12/12/16, div 8/14/14/8,
  all flags-only 0x10 vs 0x18, result bits equal). Kernel-blocked
  per lead ruling 2026-10-26 22:14:34.
- f64_to_f32: 5 x 768 SKIPPED-PLANNED (msf32_from_f64 is the f32
  parcel's row, not implemented in this worktree); runner verdict
  FAIL (no vectors passed) recorded by name, not counted.
- Comparisons: f64_eq_signaling, f64_le, f64_le_quiet, f64_lt,
  f64_lt_quiet 46,464 PASS each. f64_eq as ingested (mapped to
  signaling) FAIL 1,860 flags-only; with only the op name changed
  to msf64_compare_quiet_equal the identical file passes
  46,464/46,464 (ledger/urgent/parcel-f64-ingest-eq.md, confirmed
  and cleared by lead).

Level 2 --take 2000000, te and tz (22:15-22:16):
- add, sub, div: 2,000,000 PASS each mode (12,000,000 total).
- mul tz: 2,000,000 PASS. mul te: 1,999,992 pass, 8 fail, all the
  ruled tininess flag class.
- sqrt: generator exhausts at 26,112 cases per mode (requested
  take 2,000,000), both PASS.

f64_mulAdd level 1 --take 2000000, every mode (22:17):
- tz: 2,000,000 PASS. te 111, tp 342, tn 356, ta 111 failures,
  every one flags-only 0x10 vs 0x18 (classified by
  scratch/parcel-f64/classify_fails.py). Kernel-blocked.

Across all Berkeley logs at this writing (pre-merge history):
27,394,376 cases, 2,888 failures, every failure flags-only in
the two ruled classes (tininess, eq ingest), zero result-bit
failures, 3,840 skips all named f64_to_f32/msf32_from_f64.

RESTATED POST-MERGE (driver scratch/parcel-f64/regate-step3.sh,
2026-10-27 05:05:51-05:06:52 under load, MSF_TESTFLOAT_GEN set
explicitly in berkeley.sh; per-case logs
scratch/parcel-f64/regate-berk-*.log and
worktrees/w1-f64/build/w1/logs/*.verify.log): every blocked case
re-run complete against the fixed kernel and ingest, all PASS,
0 failures, 0 skips in this set:
- f64_mul and f64_div level 1, modes te tp tn ta: 8 x 46,464
  PASS (371,712; 1s wall each). Closes the pre-merge tininess
  counts (mul 16/12/12/16, div 8/14/14/8).
- f64_mul te level 2 --take 2000000: 2,000,000 PASS (9s). Closes
  the pre-merge 8 failures.
- f64_mulAdd level 1 --take 2000000, modes te tp tn ta:
  4 x 2,000,000 PASS (10-11s each). Closes the pre-merge
  111/342/356/111 failures.
- f64_eq as ingested level 1: 46,464 PASS (1s); ingest now maps
  it to msf64_compare_quiet_equal (compare=exact). Closes the
  pre-merge 1,860 flags-only failures.
Re-gate Berkeley total 10,418,176 cases, all passing (tally
scratch/parcel-f64/regate-tally.py / regate-tally.log). The
f64_to_f32 5 x 768 stay named skips (msf32_from_f64, sibling
parcel's row); they were not part of the blocked set and were
not re-run in the re-gate.

## Test group 3: project-exact sets

Generator tests/gen_vectors_f64.py, independent Fraction
references; pack tininess restated to unbounded-rounded per the
lead ruling (verified against the Berkeley boundary case and the
lead second shape in scratch/parcel-f64/check_tininess.py).
- Committed directed files tests/vectors/arith-f64.vec (3,980),
  conv-f64.vec (3,264), misc-f64.vec (1,222), compare-f64.vec
  (2,302), nan-f64.vec (285): 11,053 cases covering all 173
  instantiations (counted by scratch/parcel-f64/count_coverage.py,
  missing []). Against the unfixed kernel: 11,052 pass, 1 fail
  (arith-f64.vec:1824, the boundary flag case). Before the pack
  restatement the same sets passed 11,053/11,053.
- Seeded cross-format sweep into build only: 210,000 cases seed
  0xF64 PASS (pre-restatement kernel/reference pair);
  second seed 0xC0FFEE 150,000 PASS (post-restatement reference,
  pre-fix kernel).
- Additional scratch misc sweep (scratch/parcel-f64/
  gen_misc_sweep.py): 120,000 cases over remainder, int
  conversions, rint, next, logB, scaleB, compares, totalOrder,
  conversions PASS (pre-fix kernel).
- RESTATED POST-MERGE (driver scratch/parcel-f64/regate-step2.sh,
  2026-10-27 05:05 under load): the committed generator's pack
  reference verified to contain the unbounded-rounded restatement
  (tests/gen_vectors_f64.py:129-172, scale_u unbounded rounding
  compared against 2^emin; probe check_tininess.py re-run: mul
  boundary returns min-normal/0x18, the lead second shape returns
  min-normal/0x10). Regenerating the directed files from that
  generator reproduced all five committed files byte-identically,
  and the set then passed 11,053/11,053 against the fixed kernel,
  including arith-f64.vec:1824, the one pre-fix failure. Seeded
  sweeps re-run: 210,000 seed 0xF64 PASS (10s), 150,000 seed
  0xC0FFEE PASS (7s), misc sweep 120,000 PASS (4s), all
  provenance exact-f64. The re-gate then added four second-shape
  mul cases to directed_arith (test group 4); final committed
  directed set is 11,057 cases (arith 3,984), verified PASS
  11,057/11,057 at 05:13 (build/w1/logs/
  regate-final-committed-directed.log), coverage counted 173 of
  173 instantiations, missing [] (regate-coverage.log).

## Test group 4: negative controls

Driver scratch/parcel-f64/run-controls.sh, logs
worktrees/w1-f64/build/w1/logs/control-*.log. Preliminary run
22:21 (pre-merge history):
- Berkeley base file (f64_add te first 20,000) PASS; one flipped
  result bit refused (19,999 pass, 1 fail, verdict FAIL); one
  flipped flag bit refused the same way.
- Wrong-tininess build (-DMSF_TININESS_AFTER_ROUNDING=0) refused
  on the Berkeley f64_mul te level-1 file at the smallest-normal
  boundary (46,440 pass, 24 fail, first fails at result
  0010000000000000). It also fails my directed arith-f64.vec by
  exactly the one boundary case (line 1824). Note by construction:
  homogeneous binary64 addition cannot itself distinguish tininess
  definitions (a tiny exact sum of binary64 operands is on the
  subnormal grid and exact), so the boundary demonstration uses
  mul files, which is where the definitions separate at dest f64.
- NaN payload: nan-f64.vec with one quiet-NaN payload bit flipped
  in the expectation passes 285/285 only under
  # compare=nan-class and fails under # compare=exact (284 pass,
  1 fail), showing the masking is the stated kind.

RESTATED POST-MERGE: first final rerun 2026-10-27 05:07 returned
fails=1, classified before proceeding. Three of the four controls
behaved as required (base PASS 20,000; flipped result refused
19,999+1; flipped flag refused 19,999+1; wrong-tininess refused
on Berkeley f64_mul te 46,440+24; NaN payload 285 pass under
nan-class, 284+1 under exact). The one non-refusal was the
script's fifth expectation, wrong-tininess against the directed
arith file, which PASSED 3,980/3,980 under the before-rounding
build. Classification (proof scratch/parcel-f64/
regate-tinyproof2.py): the preliminary claim for that check
predates the generator restatement. The old arith boundary case
(line 1824, exact (2^53-1)*2^-1075) is tiny under BOTH the before
definition and the Clause 7.5 unbounded definition, so after the
restatement flipped its expectation from 0x10 to 0x18 no before
build can be refused by it; the parcel's own preliminary
run-controls2.log recorded that check as informational. The
distinguishing shape is an exact value below 2^emin whose
unbounded rounding reaches 2^emin (Berkeley f64_mul te:1190,
expectation 0x10, before build gives 0x18). The re-gate added
exactly that shape to directed_arith (largest subnormal times
1+2^-52 and its negative, te and ta, appended after all existing
cases so line 1824 is unchanged; each expectation corroborated
by the ingested Berkeley case and the exact Fraction proof) and
regenerated arith-f64.vec (+4). Correct build passes 11,057;
before build fails the directed arith by exactly those four.
Final rerun 05:11:39 (4s under load, regate-controls.log via
regate-step45.sh): fails=0 - base PASS, flip-result refused,
flip-flag refused, wrong-tininess refused on Berkeley mul
(46,440+24, first at 0010000000000000) and on directed arith
(3,980+4, the new cases), NaN payload passing only under
nan-class. All four mandated controls demonstrated post-merge;
commit cb10ee2.

## Gaps and skips by name (restated post-merge)

- msf32_from_f64 via f64_to_f32 Berkeley files: skipped-planned,
  other parcel's row (5 x 768). Unchanged; named skip, not a gap
  in this parcel.
- Board budget: lead-only, not run here.
- Nothing else. The three pre-merge blockers (pack tininess,
  ingest eq row, smoke control 9) are merged and re-run green
  above; standard budget has now run PASS.

## Counts by provenance (re-gate runs, 2026-10-27)

- berkeley (testfloat_gen seed 1 via ingest): 10,418,176 re-run
  blocked cases PASS, details in test group 2 (mul/div level 1
  371,712; mul te level 2 2,000,000; mulAdd 8,000,000; eq
  46,464), plus control files (add te 20,000 base; mul te 46,464
  for the wrong-tininess refusal).
- exact-f64 (project Fraction references): directed 11,057 PASS;
  cross sweeps 210,000 + 150,000 PASS; misc sweep 120,000 PASS.
- exact-py (run.sh budgets): smoke 29,982 committed PASS;
  standard adds 1,117,504 generated PASS.

Verdict: READY. All 173 instantiations implemented and covered,
every numbered re-gate item green with counts above, controls
demonstrated, no off-limits file touched (re-gate edits only
tests/gen_vectors_f64.py and tests/vectors/arith-f64.vec, both
owned), worktree clean at cb10ee2 on top of merge 80cbc97 over
checkpoint 5153324. The only named skip is the sibling parcel's
msf32_from_f64 row. Never pushed.
