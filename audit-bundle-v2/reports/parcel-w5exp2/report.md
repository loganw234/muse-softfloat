READY

# parcel-w5exp2 report: exp2/exp2m1 (SF-2 Step 3a)

Branch wave5-exp2, worktree worktrees/w5-exp2, base a0acf2a.
Design entry (written before kernel code, exact/tie
branches + inexact obligations enumerated):
ledger/parcel-w5exp2.md.

## Inventory as printed by the runner tooling

tools/gen_tables.py prints: tier1 783 implemented of 783;
tier2 51 implemented of 57; instantiations 840 (834
implemented). Registered 57 = 45 + 12 Step 3a rows;
implemented 51 = 45 + 6 exp2-pair rows; the log2 pair
(msf{16,32,64}_{log2,log2p1}) is registered PLANNED. The
brief's phrasing "51 registered / 51 implemented ...
51-with-6-planned" is inconsistent with the seam
arithmetic; the runner-printed state above governs and
is repeated here exactly (run.sh inventory line quoted in
the smoke log).

## Registration

operations.tsv: exp2/exp2m1/log2/log2p1 (9.2, math_un, attr,
flags yes, wave 5, mpfr-exact, exact, tier 2, C-754).
implemented.tsv: +msf{16,32,64}_exp2, +msf{16,32,64}_exp2m1
at wave 5 only. run.sh: TIER2_TOTAL_EXPECTED 45 -> 57 with
rewritten freeze comment; VECS += explog-{f16,f32,f64}.vec.
Regen: gen_tables.py twice byte-identical (plus drift
check inside smoke); gen_explog_tables.py twice
byte-identical (fc /b FC: no differences).

## Kernel (src/msf_math.c explog section)

Per spike Sec. 6.1: exact nearest-integer n+f split, 2^n
as pack exponent input (never a multiply), u = f*ln2
Taylor: exp Horner for u >= 0, alternating delta form
D(z) = sum (-z)^k/(k+1)! for u < 0, expm1 ratio M for
exp2m1 u > 0; exp2m1 by composition only (ones-bracket
(2^n - 1) +- Q*2^n and (1 - 2^n) +- Q*2^n exact endpoints
materialised in a 64-limb big; (1-delta)*2^n by scaled
one-minus; 1+m ones-bracket for the exp2 n=0 near-1
attractor). Ziv stages 160/256/384. Constants only from
tools/gen_explog_tables.py: bracket-floored ln2
(|dps260-dps210| ~ 2^-702.3, bracket +-2^-590 stable) +
exact 1/k! floors, 67 entries, no decimal literals in C.
Ek integers as proven in the generator output:
MSF_EXPLOG_EK_EXP = {147, 243, 371}; stage terms
{35, 49, 66}; tails <= 2^-(W+24) exact-rational.

Specials as shipped (Clause 9.2, S1 extracts lines
2738-2811): NaN matrix wholesale with infinity NOT
invalid; exp2: (+-0)->+1, +inf->+inf, -inf->+0;
exp2m1: +-0->+-0, +inf->+inf, -inf->-1; sNaN invalid;
no other exceptions except pack-judged
overflow/underflow/inexact. Exact/tie branches = the
integers only (2^x irrational for non-integer dyadic x),
including exp2(emin-p) (f64 -1075) packed exactly and
exp2m1 at p+1 / -(p+1); saturation cut x < -(p+1) packs
the exact proxy magnitude 1 - 2^-128.

## Evidence (per-leg counts)

Decider: tests/explog_decider.c (MPFR bracket, adaptive
precision 192 -> 3072, five-mode first-principles grid
narrow - no raw RNDNA, specials/integers table-decided,
far-cut proxies >= 64 exponent bits beyond kernel cuts,
near-1 1+exp2m1 composition bracket, stride audits vs
mpfr_get_flt/get_d). No foreign oracle executed anywhere;
the exp2m1 RN subnormal-corner fence is MPFR-decided.

- binary16 exhaustive: 655,360 mode checks (65,536
  encodings x 2 fn x 5 modes), mismatches 0, undecided 0,
  final_undecided 0, stage hits 389410/0/0. PASS.
- binary64 worst-case (published sets, fetch record in
  ledger: worst.html sha256 5941af17..., pin
  3b2163bb...; exp2.wc sha256 51f847cf..., exp2m1.wc
  sha256 70516fe2..., scratch only):
  exp2: lines 77213, tokens 77182, finite inputs checked
  77176 occurrences = 77121 unique encodings (spike
  census 77120 unique values + the -0 encoding, set-diff
  verified), nonfinite skipped 4, unparsed 2, inexact
  tokens 0; checks 385,880, mismatches 0, PASS.
  exp2m1: lines 240883, tokens 240834, finite 240828
  occurrences = 240825 unique (spike 240824 + -0);
  checks 1,204,140, mismatches 0, PASS. 100% of the
  published finite unique inputs for both functions,
  five modes. final_undecided 0; stage 1 decided every
  wc input.
- binary64 seeded: seed 20261028: 1,999,055 checks PASS;
  seed 777001: 1,999,130 checks PASS (draws 200,000/fn
  each, nonfinite skipped by construction). Escalations
  27 after the decider composition fix.
- binary32 EXHAUSTIVE differential: PASS. 256 shards x
  2^24 encodings over [0, 2^32), both functions, five
  modes, bits+flags; every shard rc=0. Aggregate
  (re-summed exactly from shard logs): checked
  42,949,672,960 mode-checks = 4,294,967,296 patterns
  per function (finite 4,278,190,080; the 16,777,216
  nonfinite patterns per function decided by the
  specials table inside the same sweep), mismatches 0,
  decider-undecided 0, kernel final_undecided 0 in all
  shards, stage hits 22,386,767,760 / 0 / 0 (stage 1
  decides every binary32 kernel input), decider
  escalations 6,377,992, specials 33,560,832, far-cut
  shortcuts 3,951,034,368, stride audits 25,986 with
  audit_fail 0. Driver: scratch/parcel-w5exp2/
  run_f32_exhaustive.sh, 11 workers, ulimit -v 4194304
  KB recorded in f32-driver.log; wall 09:36:35 ->
  17:25:20 -0700 (7 h 49 m; host shared with sibling
  parcels and the sweep tree was lowered to BelowNormal
  priority mid-run by the lead at the owner's request,
  ledger LEAD NOTE 12:25:32 - no shard lost, throughput
  only). The shipped kernel under test is exactly
  branch HEAD (kernel last touched in 048aa29).
- committed vectors: explog-f16.vec 14,845 lines,
  explog-f32.vec 15,350, explog-f64.vec 15,415 (total
  45,610; families specials/integers/cuts/lattice/tiny/
  strips/hardest/seeded; ta independently decided;
  specials+integers cross-checked against the generator's
  exact Fraction rounder; regeneration byte-identical).
  Runner verify: 45,610 passed / 0 failed.
- smoke: PASS (157 s contended; inventory line exactly:
  "tier1 783 implemented of 783; tier2 51 implemented,
  6 planned, 57 registered; bad rows 0"; planned rows
  named msf{16,32,64}_{log2,log2p1}; all 10 built-in
  controls refused). standard: PASS (240 s; +917,504
  f16-exhaustive and 200,000 pack-sweep vectors).
- Target compile: arm-none-eabi-gcc cortex-m0plus
  -Werror clean at BOTH -Os and -O3 (the -O3 check the
  brief names), host -O2/-O3 clean; msf_math.o text:
  ARM -Os 13,908 B, ARM -O3 60,724 B; symbol scan clean
  at both (undefined limited to integer helpers + pack).
- Negative controls (run_negatives.sh, scratch/parcel-
  w5exp2/negatives.log): ALL REFUSED. NC1a Ek tamper
  replay: wc stage hits 374095/242117/0 vs baseline
  */0/0; NC1b hand-narrowed EK_EXP refused by generator
  re-derivation (byte compare); NC2 ln2 limb digit flip:
  7,349 runner FAILs; NC2b top-limb-only table: 7,322;
  NC3 cut thresholds off-by-one: refused on exactly the
  3 tie-cell ta lines; NC4 tie-path flag strip: 4,565;
  NC5 1-ulp hardest: refused. Note measured during
  control design: subtle 2-/3-limb table drops do NOT
  bite this vector set (their error sits below the
  hardest committed input's boundary distance) - the
  watched forms above are the deterministic ones, and a
  merely-narrowed Ek (exponent raised) is caught by
  re-derivation (NC1b), as the brief allows.
- Forced-stage corroboration (test-only builds): wc +
  f16 + seeded legs rerun with FORCE_START=1 and =2:
  identical PASS counts, stage hits entirely at the
  forced stage, final_undecided 0 (forced.log).
- binary32 seeded (seed 987654, 100k draws/fn):
  995,965 checks PASS.

## Bugs found by the evidence (fixed, by leg)

1. Delta series shape (binary16 exhaustive, first run:
   123,778 mismatches): first cut evaluated 1-exp(u) as
   |u|*M(|u|) with the positive expm1 ratio - that is
   expm1(|u|), not delta. Fixed to the alternating
   D series with its own generator Ek recurrence.
2. exp2 near-1 attractor (wc exp2 first run: 9
   mismatches, final_undecided=9 - a brief STOP, reported
   here rather than widened): direct v path cannot
   resolve m ~ 2^-1075 against stage Ek for n=0 inputs.
   Fixed by design, not by width: 1+m ones-bracket
   composition for exp2 n=0, f>0 (spike Sec. 4 item 2b).
   Re-run: final_undecided 0.
3. Decider-side: value-threshold far cuts (undecided at
   exp2m1 x ~ -3830 under the log2-threshold form) and
   the decider's own near-1 collapse on tiny exp2 inputs
   (168k escalations, fixed by the 1+exp2m1 composition
   bracket). Decider defects only; kernel unaffected.
4. Tooling-side (recorded, host hygiene): the first
   gen_vectors_explog.py run ballooned to ~18 GB by
   forming Fraction(2)^n for integer-valued seeded
   patterns with |n| up to ~10^308 in its cross-check
   table. The process was identified by exact command
   line as this parcel's own (the .venv python) and
   stopped; the generator now proxies |n| beyond format
   thresholds. No other agent's process was touched.

## Proposed metrics rows (not landed here; lead lands)

briefs.jsonl: {"wave": "wave5", "work": "SF-2 Step 3a
exp2/exp2m1 correctly rounded (6 rows implemented;
log2/log2p1 6 rows registered planned; Tier 2 57
registered / 51 implemented)", "author": "parcel-w5exp2",
"base": "a0acf2a", "time_box_min": 900, "ceiling_lines": 0,
"ceiling_text": "no line ceiling stated in brief
w5-exp2.md; owned-files list is the bound, generated
files/vectors excluded"}.
fetches.jsonl: no new fetch - the .wc inputs are the
Step 0b CORE-MATH pin already recorded (worst.html fetch
recorded by study-sf2-explog); if the lead wants a parcel
row, the data are: exp2.wc sha256
51f847cf7102c56fb6d474a304cc56f55ae84b405c8366d77fba3d22523d0f2b,
exp2m1.wc sha256
70516fe27283474d55d38ed120569027c81e9bdd3b6f914f6cc855744afbc057,
mechanical first-token parse only, values re-decided by
MPFR, scratch only, never vendored.

## Not done

- log2/log2p1: registered planned (Step 3b parcel; wide
  division + integer composition (a) per spike Sec. 6.2).
- Board sampled replay: not run (no board flashing per
  brief; board lists already carry msf_math.c, verified).
- Nothing else outstanding in the brief's work list.

## Commits (branch wave5-exp2, not pushed/merged)

87d00d2 kernel + registration + generator + decider;
048aa29 delta-series and near-1 attractor fixes, decider
hardening; 2618b34 committed vectors + WIDTHS/VECTORS
rows. All end Co-Authored-By: Muse Code
(muse-wonder-full-1.0).
