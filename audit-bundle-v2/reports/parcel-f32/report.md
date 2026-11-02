# parcel-f32 report (Wave 1, binary32 format parcel)

COMPLETE - post-fix re-gate by regater-f32 under
ledger/briefs/w1-f32-regate.md, 2026-10-27. Verdict at the end:
READY. Pre-fix sections stand as measured; the "Post-fix re-gate"
section carries the closing evidence and final counts.

## Identity and bounds

- Brief: ledger/briefs/w1-f32.md. Start: test escalation filed
  2026-10-26T21:44:19-07:00; design entry ledger/parcel-f32.md
  2026-10-26 21:53:20 -0700 (time box runs from there).
- Worktree worktrees/w1-f32, branch w1-f32, base
  4cdb912dbd5ebda4fa2bc29168883dc4527d4091. Nothing was done in
  muse-softfloat/. Never pushed.
- Deliverable count re-measured by filtering docs/COVERAGE.tsv
  (wave=1, name starts msf32_): 173, matching the brief.
- Hand-written lines: src/msf32.c 831 + tests/gen_vectors_f32.py 954
  = 1,785 of the 3,000 ceiling at the checkpoint; the re-gate
  restatement takes gen_vectors_f32.py to 983, parcel total 1,814
  of 3,000. Committed new vector files: 930,433 bytes total
  (under the 1 MB ceiling; unchanged byte total after the re-gate
  regeneration - only flag digits moved).
- Machine under third-party load throughout; all wall times below
  are records, not rate claims.

## Commits

- 6c1bc01 Wave 1 parcel-f32: all 173 binary32 instantiations over
  shared kernels (pre-kernel-fix checkpoint; body names the open
  escalation).
- 9bb8723 Merge lead kernel fix b37fb12 into w1-f32 for re-gate
  (merges 53acb1a + b37fb12; implemented.tsv conflict resolved as
  below).
- 26c76aa Re-gated parcel-f32 after the lead tininess/ingest fix
  (READY) - full hash 26c76aafae1daad27fade6e19df2764d96980dc8;
  body carries these counts.

## What was implemented

src/msf32.c: decode via src/msf_decode.h, NaN delivery via
msf_nan_delivery, exact u128 kernels, one pack per operation.
Design tables and per-op algorithms are in the ledger design entry
(2026-10-26 21:53:20 -0700); the bit-126 alignment invariant (every
kernel input at most 106 bits, at least 21 trailing zeros after
normalization) is stated in the code at norm126 per lead note.
tables/implemented.tsv: 173 rows appended at the end, wave 1 -
note the file's existing blob uses CRLF line endings although
AGENTS.md says write LF; the appended rows match the file's
existing CRLF so the file stays uniform (lead to normalize if
desired). Generated outputs regenerated: include/muse_softfloat.h,
tests/msf_dispatch.h, docs/COVERAGE.tsv byte-clean by the drift
check inside run.sh (236 implemented = 63 + 173).

## Brief faults recorded (lead-ruled)

1. totalOrder keys "within binary64" - these instantiations are
   binary32. CONFIRMED by lead 2026-10-26 21:55:48 -0700.
2. "msf_pack_generic is for your dest only" - msf32_log_b has dest
   binary64 by the logBFormat ruling and packs as such. CONFIRMED.
3. Assumption A1 (scaleB infinite N saturates) CONFIRMED.
4. Assumption A2 (Exact to-int: invalid only out-of-range)
   CONFIRMED.
5. Remainder subnormal-by-infinity flags: Berkeley decides -
   measured 14 such cases in f32_rem level 1, all flags 0x00,
   matching the implementation (result x, no flag).
6. Berkeley ingest default testfloat_gen path assumes the
   muse-softfloat/ layout (parent.parent.parent lands in
   worktrees/ from a worktree); every ingest here set
   MSF_TESTFLOAT_GEN explicitly. Environment fact, not a defect
   in the primary layout.

## Escalation (shared kernel + ingest), status: lead-ruled, fix
## landed on main at b37fb12 (via 53acb1a) and merged here

Evidence and ruling are recorded in ledger/parcel-f32.md
(2026-10-26 evening, two entries) and ledger/lead.md
(2026-10-26 22:14:34 -0700). Summary: msf_pack_generic detects
tininess on the delivered value; Clause 7.5 after-rounding and
Berkeley judge the p-bit rounding computed as though the exponent
range were unbounded. Neither MSF_TININESS_AFTER_ROUNDING setting
matches Berkeley (probed both: after misses 16 te-mul cases one
way, before misses 24 the other way). And tests/berkeley_ingest.py
maps Berkeley's quiet f32_eq to compare_signaling_equal.

## Test evidence by provenance

### Berkeley SoftFloat/TestFloat 3e (compare as ingested:
### nan-class arith/conversions, berkeley-int int conversions,
### exact comparisons)

Driver scratch/parcel-f32/berkeley_driver.py; results log
scratch/parcel-f32/berkeley-results.log; per-FAIL runner logs in
scratch/parcel-f32/berkeley-logs/. Pre-fix run: 96 jobs,
27,258,784 cases, wall 123.7s under load. Coverage: level 1
complete for f32_add/sub/mul/div/sqrt/roundToInt, f64_to_f32,
f32_to_{i32,i64,ui32,ui64}, {i32,i64,ui32,ui64}_to_f32 in all five
modes te tz tp tn ta (ta travels through the runner's internal
mode value and evidences the pack's ties-to-away path; it is not a
public attribute claim); f32_rem level 1 (no mode); comparisons
eq/le/lt/le_quiet/lt_quiet level 1; level 2 --take 2000000 te+tz
for add/sub/mul/div (sqrt level 2 stream terminates at 8,800
cases, so complete); f32_mulAdd level 1 --take 2000000 all modes.

Pre-fix outcome: every job passes except the two escalated
classes. Result bits agree with Berkeley on all 27,258,784 cases
(including every failing line - classification script
scratch/parcel-f32/classify_fails.py). Failing jobs pre-fix:
mul (te16 tp13 tn12 ta16 of 46,464 L1; te28 of 2,000,000 L2),
div (te8 tp14 tn15 ta8 L1; te5 L2), mulAdd (te134 tp316 tn317
ta134 of 2,000,000), eq (1,967 of 46,464). All flags-only.

### Project-exact (tests/gen_vectors_f32.py, Fraction references)

Committed directed files into tests/vectors/, 11,129 cases
covering all 173 instantiations (min 24 cases each, checker
scratch/parcel-f32/check_coverage.py):
arith-f32.vec 3,520; fma-sqrt-f32.vec 864; conv-int-f32.vec 748;
toint-f32.vec 2,640; rint-misc-f32.vec 995; compare-f32.vec 2,362.
Replay: scratch/parcel-f32/directed2.log PASS 11,129/11,129.
Note: tools/run.sh (off-limits to this parcel) has a fixed smoke
vector list that does not name these new files; they were replayed
explicitly with build/smoke/msf_runner.exe verify, and the lead
wires the list at merge.

Seeded generated sweeps into build/w1 (not committed):
- arith sweep 210,000 cases seed 20261026 (28 templates x7500:
  add/sub/mul/div x4 combos, sqrt x2, fma x8, convertFormat x2) -
  PASS 210,000/210,000 (scratch/parcel-f32/sweep210k.log).
- misc sweep 145,000 cases seed 777 (145 templates x1000: rint 5+1,
  next x2, logB, remainder, scaleB, totalOrder/Mag, from-int x8,
  to-int x80, comparisons x44) - PASS 145,000/145,000
  (scratch/parcel-f32/misc-sweep.log), generated by
  scratch/parcel-f32/misc_sweep.py over the committed references.
- small 5,600-case smoke sweep seed 12345 - PASS.

First directed replay found two bugs in my Python reference (not
in the C): signed-zero loss through Fraction in ref_conv, and an
infinity comparison rank of 10^30 below binary32 maxfinite. Both
fixed in the generator; the C was correct on independent reading
and Berkeley f64_to_f32/to-int jobs corroborate.

### Regression budgets (tools/run.sh, Git Bash route)

- smoke PASS in 9s: drift byte-clean, host build, unit, 29,982
  committed vectors (pre-existing list), type scan clean, ARM
  symbol scan clean (undefined: own symbols, __aeabi_llsl/llsr/
  lmul, thumb case helpers, memcpy), 9/9 permanent controls
  refused. scratch/parcel-f32/smoke1.log.
- standard PASS in 27s: smoke + 917,504 exhaustive-f16 and
  200,000 seeded pack64 vectors.
  scratch/parcel-f32/standard1.log.

### Negative controls (brief item 4, scratch/parcel-f32/controls.py + controls.log)

1. Flipped result bit in a Berkeley mul-tz line: refused (rc=1, VERDICT FAIL).
2. Flipped flag bit in the same line: refused.
3. Wrong NaN-payload expectation (ffc18071 for ffc18073): PASSES
   under compare=nan-class (rc=0) and is REFUSED under
   compare=exact (rc=1) - masking is the stated kind only.
4. Wrong-tininess build (MSF_TININESS_AFTER_ROUNDING=0) on
   tests/vectors/arith-f32.vec: refused (rc=1); first failures are
   smallest-normal adds (result 800000, flags 0x18 vs 0x10);
   the normal build passes the same file. Re-demonstrated after
   the kernel fix in the post-fix section (item 4d), where the
   before-build fails exactly the complementary boundary subset.

## Skips by name

- Board budget: not run (lead-only under board lock).
- Berkeley levels beyond the brief's list (level 2 full streams
  for binary ops are ~40M cases/slice; brief caps with --take).
- f32_eq_signaling Berkeley function: not in the original brief's
  list; signaling equality is covered by project-exact directed
  cases and all Berkeley signaling le/lt jobs. ADDED as an extra
  job in the post-fix re-run (46,464 cases PASS, below).
- Host-FPU oracle cross-checks: not used; Fraction + Berkeley
  authorities cover the parcel per SF-0 gate order.

## Post-fix re-gate (regater-f32, 2026-10-27, brief
## ledger/briefs/w1-f32-regate.md items 1-6 in order)

Machine under third-party load throughout; every wall time below
is a record, not a rate claim. All regate logs are the regate-*
files in scratch/parcel-f32/ (pre-fix logs preserved untouched);
regate drivers are regate_berkeley_driver.py, regate_controls.py,
regate-budget.sh, regate_tally.py in the same directory.

1. Merge. git merge b37fb12 in worktrees/w1-f32: the ONLY conflict
   was tables/implemented.tsv, as the brief predicted (no
   generated-file conflicts, nothing else to escalate). Resolved
   as the union of rows with LF endings (scratch script
   resolve_impl.py over the three index stages: base 71 non-empty
   lines = 7 comments + header + 63 rows; theirs identical rows to
   base, LF-normalised; ours adds exactly the 173 parcel rows).
   Result: 244 LF lines, 0 CR bytes, 236 implemented rows
   (63 + 173), committed as merge 9bb8723. tools/gen_tables.py
   then re-run: 783 instantiations, 236 implemented, all four
   generated outputs byte-identical (no diff to commit); the
   drift check inside run.sh agrees in every budget below.

2. Reference restated. pack_mag in tests/gen_vectors_f32.py now
   judges tininess on the p-bit rounding at the value's own
   (unclamped) binade scale against 2^emin (Clause 7.5
   unbounded-rounded, per the lead ruling; flags-only - delivered
   bits unchanged). The committed file is byte-identical (36,683
   bytes, CR excluded) to the parcel's pre-validated
   scratch/parcel-f32/patched_gen.py, which probe_patched.py had
   measured bad=0 against all 464,640 Berkeley mul/div level-1
   cases before the fix landed. Directed regeneration
   (gen_vectors_f32.py directed tests/vectors,
   regate-gen-directed.log): same six files, same line counts
   (3,520/864/748/2,640/995/2,362), same 930,433-byte total; only
   arith-f32.vec changes - 4 expectations, all the same shape
   (delivered smallest normal 800000, flags 10 -> 18: tp adds of
   max-subnormal 7fffff with a tiny f64 in both source orders).
   Replay with the fixed-kernel runner (regate-directed.log, all
   six files in one verify): PASS 11,129/11,129, and
   check_coverage.py re-confirms all 173 instantiations covered,
   min 24 cases each, no extras. Seeded sweeps regenerated with
   the restated reference (gen wall 8.4s under load) and replayed:
   arith 210,000 seed 20261026 PASS 210,000/210,000
   (regate-sweep210k.log); misc 145,000 seed 777 PASS
   145,000/145,000 (regate-misc-sweep.log); small 5,600 seed
   12345 PASS 5,600/5,600 (regate-sweep-small.log).

3. Berkeley re-run (fixed ingest, MSF_TESTFLOAT_GEN set
   explicitly in regate_berkeley_driver.py to
   scratch/oracles/TestFloat-3e/build/Linux-x86_64-GCC/
   testfloat_gen.exe). The brief's blocked set was re-run inside
   the full pre-fix job set plus the offered extra, so nothing
   the kernel change touches is left unreplayed: 97 jobs,
   27,305,248 cases, fails=0, wall 125.7s under load
   (regate-berkeley-results.log, DONE line; console in
   regate-berkeley-console.log; zero per-failure logs because
   there were no failures to classify). Blocked classes, all now
   PASS complete: mul/div level 1 all five modes 464,640
   (pre-fix 57+45 flags-only fails); mul/div level 2 te slices
   4,000,000 (pre-fix 28+5), with the tz slices also re-run
   (8,000,000 both); mulAdd level 1 take-2M all five modes
   10,000,000 (pre-fix 901); f32_eq as ingested 46,464 (pre-fix
   1,967 under the wrong signaling map; b37fb12's ingest maps eq
   to compare_quiet_equal); plus the extra f32_eq_signaling
   46,464 PASS. Every other pre-fix job re-passed unchanged in
   scope: add/sub/sqrt/roundToInt/f64_to_f32/to-int/from-int
   level 1 all modes, rem level 1, le/lt/le_quiet/lt_quiet
   level 1, add/sub level 2 te+tz take-2M, sqrt level 2 te+tz
   complete at 8,800 each. Total = pre-fix 27,258,784 +
   eq_signaling 46,464 = 27,305,248 (tally re-derived by
   regate_tally.py from the results log).

4. Negative controls re-demonstrated (regate_controls.py,
   regate-controls.log), same four as pre-fix:
   (a) flipped result bit in a Berkeley mul-tz line: REFUSED
   rc=1. (b) flipped flag bit in the same line: REFUSED rc=1.
   (c) wrong NaN payload ffc18071 for ffc18073: PASSES under
   compare=nan-class rc=0 (expected), REFUSED under
   compare=exact rc=1 - masking is still exactly the stated kind.
   (d) wrong-tininess build (MSF_TININESS_AFTER_ROUNDING=0, the
   runner from build/smoke/controls) on the regenerated
   tests/vectors/arith-f32.vec: REFUSED rc=1, 12 failures of
   3,520, and classification over every FAIL line shows all 12
   are the complementary boundary subset only - got flags 18,
   want 10, delivered at the smallest-normal magnitude
   (800000/80800000), result bits always equal
   (complementary-subset-only: YES). The 4 expectations the
   restatement moved the other way (want 18) now AGREE with the
   before-build and so correctly do not appear; the normal
   fixed-kernel runner passes the same file rc=0.

5. Regression budgets in the worktree (Git Bash route,
   regate-budget.sh; control 9 in the merged tools/run.sh names
   msf16_add and is refused as required):
   - smoke PASS (regate-smoke.log 2026-10-27 05:10:27 -0700,
     wall 8s under load): drift byte-clean, host build, unit,
     29,982 committed vectors, type scan clean, ARM symbol scan
     clean (21 undefined: own symbols, __aeabi_llsl/llsr/lmul,
     thumb case helpers, memcpy), 9/9 permanent controls
     refused. An identical build-only smoke also passed before
     the vector replays (regate-smoke-build.log, 9s).
   - standard PASS (regate-standard.log 2026-10-27 05:10:40
     -0700, wall 28s under load): smoke + 917,504
     exhaustive-f16 and 200,000 seeded pack64 (37,821
     non-invariant dropped by construction, as pre-fix),
     total 1,117,504 generated cases PASS.

6. Commits and ledger. Merge 9bb8723 above; re-gate commit
   26c76aafae1daad27fade6e19df2764d96980dc8 changing only the
   two parcel-owned
   files tests/gen_vectors_f32.py (+33/-6 lines) and
   tests/vectors/arith-f32.vec (4 flag expectations). No
   off-limits file touched by the re-gate - every lead file in
   the worktree arrived through the merge itself (verified by
   git status/diff --name-only: only those two files modified
   after the merge). Ledger entry appended to
   ledger/parcel-f32.md via kit ledger.sh script file
   (ledger-regate.sh, body staged at regate-ledger-body.txt),
   stamped 2026-10-27 05:14:43 -0700. Never pushed.

### Final counts by provenance (post-fix)

- Berkeley SoftFloat/TestFloat 3e (as ingested after b37fb12):
  97 jobs, 27,305,248 cases, PASS complete, 0 fails.
- Project-exact (tests/gen_vectors_f32.py, restated Fraction
  references): committed directed 11,129 PASS; seeded sweeps
  into build/w1 and scratch 210,000 + 145,000 + 5,600 = 360,600
  PASS. Project-exact total replayed this re-gate: 371,729.
- Regression budgets (tools/run.sh, incl. lead exact-py pack/
  encodings/copysign and generated f16/pack sets): smoke 29,982
  committed vectors PASS; standard additionally 1,117,504
  generated PASS; 9/9 permanent controls refused in each.
- Parcel negative controls: 4/4 behaved as required above
  (result-bit and flag-bit flips refused; NaN-payload pass only
  under nan-class; wrong-tininess build refused on exactly the
  12-case complementary subset).
- Skips remaining, by name: board budget (lead-only under board
  lock); Berkeley beyond the brief's levels/slices (level-2 full
  ~40M-case streams for binary ops remain take-2M sampled per
  brief); host-FPU oracle cross-checks (not used - Fraction +
  Berkeley authorities cover the parcel per SF-0 gate order).
  No other skip from the pre-fix list survives: f32_eq_signaling
  was run.

## Verdict

READY. Every numbered item of ledger/briefs/w1-f32-regate.md is
green with the counts above: b37fb12 merged (union-LF
implemented.tsv, generated files byte-identical after
regeneration, 236 implemented = 63 + 173); the Fraction
reference restated to the Clause 7.5 unbounded-rounded tininess
and byte-identical to the pre-validated scratch version;
directed vectors regenerated (4 flag expectations moved) and
replayed 11,129/11,129 with all 173 instantiations covered;
seeded sweeps regenerated and replayed 360,600/360,600; the
blocked Berkeley counts re-run inside the full 97-job set,
27,305,248/27,305,248 PASS with f32_eq as ingested and
f32_eq_signaling both green; the four negative controls
re-demonstrated, wrong-tininess failing only the 12-case
complementary subset; tools/run.sh smoke and standard green
(control 9 naming msf16_add). Hand-written parcel total 1,814
of the 3,000-line ceiling; committed vectors 930,433 of the
1 MB ceiling; worktree clean but for the merge and re-gate
commits; never pushed. The two lead-owned defects that stopped
the parcel at 6c1bc01 (pack tininess definition, ingest eq row)
are closed by measurement, not by assumption: result bits
already agreed with Berkeley everywhere pre-fix, and flags now
agree on every one of the 27.3M Berkeley cases and every
project-exact case replayed.
