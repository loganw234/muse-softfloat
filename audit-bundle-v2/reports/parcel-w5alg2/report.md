READY

# parcel-w5alg2: SF-2 Step 2b correctly rounded hypot (3 rows)

Branch wave5-alg2 (worktrees/w5-alg2), base 0f08aa3. Two
commits, tree clean, nothing pushed or merged:
656660493b122e248569cbb84f571e8e2c20dca5 (kernel +
registration) and e858498242967f2ef4713e96521253dd6c7a088d
(evidence). Tier 2: 45 registered / 45 implemented
(inventory line below). Design entry (before any code,
with jam addendum): ledger/parcel-w5alg2.md. All runs:
script files scratch/parcel-w5alg2/01..12 under Git Bash,
MSF_PYTHON pinned to the workspace .venv, TMP in scratch,
ulimit -v ceilings; logs in scratch/parcel-w5alg2/out/.

## What shipped

hypot_core in src/msf_alg.c (study Sec. 3.2): magnitudes
ordered, window anchored at the top of the larger square
inside u128 (sum < 2^122), smaller square aligned by
truncation with separate tail sticky (never a jam),
sqrt_core scaling (119..122-bit radicand, 60/61-bit root),
one pack, sign always +. docs/WIDTHS.md hypot row:
"128-bit anchored sum + sticky". No new width, no new pack
entry points. Board wiring for msf_alg.c verified present
(board/CMakeLists.txt, board/run_board.sh; alg1 merge) -
no escalation needed there.

## Specials as shipped (evaluation order, [2R] dispositions)

(1) any sNaN -> first sNaN quieted + invalid; (2) any
+-inf -> +inf, no flag, including beside a quiet NaN in
both operand orders; (3) any qNaN -> first qNaN per the
SF-0 2.5 matrix; (4) both zeros -> +0; (5) finite kernel.
[2R] cell A hypot(+-inf, sNaN): second-read from the S1
extracts directly (p059 signaling sentence carries no
exception clause where the quiet sentence does; p063 names
only qNaN) plus Tier 1 composition - held at
qNaN + invalid, table-decided in kernel, decider and
generator, never MPFR-sourced (MPFR has no sNaN).
[2R]/[D] cell B inf+finite: Table 9.1 domain + affine
value, composition through gated mul/add/sqrt cells, MPFR
value corroboration - held at +inf, no flag. Neither cell
flipped; neither was guessed.

## Per-format counts

Committed hypot vectors: 2,500 lines per format (500 pairs
x 5 modes; specials 500, directed 1,140, ties 675, seeded
185 per format), appended after the rSqrt sections
(rSqrt lines byte-identical to the pre-parcel files -
checked). Files now 3,700/3,705/3,705 lines. Regeneration
byte-stable twice (vectors and all four table outputs);
post-commit regeneration leaves the tree clean.
Gate differentials (kernel vs the independent MPFR-recipe
decider, generated not committed): binary16 second-operand
sweep 20-encoding boundary/specials pool x 65,536 x 5 =
6,553,600 checks; binary16 sampled 300,000 pairs
(1,500,000 checks); binary32 and binary64 seeded finite
350,000 pairs each (1,750,000 checks each); all 0
mismatches. Generation itself is a three-way cross-check
(MPFR recipe vs exact-Python integer decider vs settled
table) on every committed pair and mode, the ta column
included; no disagreement occurred (stop rule never
engaged).

## Tie evidence

Exact midpoint ties are in the committed ties family at
all three formats, including the study's measured binary16
tie (inputs 062c 067b: te 087a / tz,tn 0879 / tp,ta 087a,
flags 10) and 16 te!=ta pairs per format (tie-to-even
chooses down, ties-to-away up, both cross-decided by MPFR
and exact-Python). This is why the floor (not jam) form is
mandatory and shipped.

## Negative controls (watched)

Refused: hypot(qNaN,inf)->NaN expectation mutant;
1-ulp-moved hardest (f64 tie); inexact stripped on the
study tie; tp<->tn swap on a subnormal-output pair;
MSF_ALG_TEST_NOSTICKY kernel mutant (1,280 lines fail,
incl. 80 ties-tagged). run.sh's own 11 controls all
refused, inventory counted as designed.

JAM finding (reported, not forced): the brief's
"jam-instead-of-floor mutant must fail the tie family"
does not occur for the tree-idiom shr_jam mutant
(MSF_ALG_TEST_JAM) in this anchored-window realization -
it is packed-equivalent to the shipped floor form (proof
by parity case analysis in the design-entry addendum; the
two jam sites compose to R|sticky at radicand scale and a
crossed square is always an odd root whose bit 0 recreates
the sticky in the pack). Watched PASSING the committed
11,095 lines and 1,500,000 decider-differential checks, 0
divergences - recorded as equivalence evidence, never as a
refused control. The floor form ships as mandated; the
biting mutant in the same defect is NOSTICKY above.

## Oracle corroboration (optional leg, run)

cr_hypot/cr_hypotf/cr_hypotf16 execution-only (units
compiled unopened from the Step 0b pin): 48,000 checks,
41,103 agreements with the exact decider. All 6,897
disagreements are td tp-only (FE_UPWARD) at binary32/64
(cr returns one ulp too high when the smaller operand is
far below), adjudicated foreign-host oracle-limit:
MPFR and exact-Python agree on all 6,897 (F1-class fence;
te/tz/tn and binary16 tp unaffected). Our kernel matches
MPFR+exact on every adjudicated case through the
differentials above.

## Gates

smoke PASS (182,518 cases, 21 s) and standard PASS
(+1,117,504, 53 s) on the committed tree, re-run
post-commit: "inventory: tier1 783 implemented of 783;
tier2 45 implemented, 0 planned, 45 registered; bad rows
0"; drift check clean; type/symbol scans clean. Target:
arm-none-eabi-gcc 14.2.1 cortex-m0plus -Os, msf_alg.o text
2,224 B total (hypot_core 1,032 B, data/bss 0), stack
hypot_core 520 B static, undefined symbols integer-only +
memcpy. No performance claims.

## Not done (named)

- Neither [2R] cell has an owner ruling beyond the study
  readings and my second reads; both held, so nothing is
  blocked, but the cells remain [2R]-class by pedigree.
- tests/VECTORS.md mpfr-alg tag rows still say "rSqrt ...";
  hypot rides the same four tag tokens (study Sec. 7.3 one
  tag family) and that file is outside my owned list -
  wording touch-up escalated to lead/owner at merge (no
  gate depends on it; provenance counts derive from the
  vector files).
- tests/msf_dispatch.h changed under regeneration
  (hypot trampolines now non-NULL) and is committed with
  the other generator outputs, as the drift check requires
  all four consistent.
- Board sampled replay and planted-copy verification are
  lead/verifier work; no board flashing done.
- cr_hypot directed-upward foreign defect origin not
  pursued (fenced by adjudication above).

Clean room: nothing with cft in its name was opened,
searched, or listed; foreign code was execution-only
(interface headers and listings per the study route).
