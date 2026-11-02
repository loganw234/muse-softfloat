# Ledger: parcel-w4interval (Wave 4 Step 1c host proof)

## 2026-10-27 design entry (before code)

Base `b704b4c9b805b584a2e221c3fa889017d480ac88`, worktree
`worktrees/w4-interval`, branch `wave4-interval`. Brief:
`ledger/briefs/w4-interval.md`. No board in this parcel; board
sample is a named not-done gating any on-silicon sentence.

Decisions frozen here, before implementation:

- **Catalogue is bit-level.** Every geometry input is a binary64
  bit pattern in the TSV (binary32-origin families store the exact
  binary64 widening of the binary32 value). The exact oracle in
  the generator is `Fraction` arithmetic on those exact values.
  Host naive arithmetic appears only in the generator's indicted
  naive column, never as oracle.
- **Sphere stages.** Stage 1: each point input becomes a binary32
  interval by outward directed conversion (RD/RU via
  `msf32_from_f64`), then binary32 interval discriminant. Stage 2:
  binary64 point intervals, binary64 interval discriminant (for
  binary32-origin rays this is exactly the survey's widening).
  Stage 3: exact sign of the discriminant over binary64 by
  error-free transformations (Knuth TwoSum, FMA TwoProduct),
  term distillation by iterated VecSum, sign by dominance against
  an RU-summed remainder bound. A fresh flags word guards stage
  3: overflow/underflow/invalid, term-capacity overflow, or an
  undecided distillation all yield UNCERTAIN, never a sign.
- **Decision mapping.** Exact discriminant >= 0 is HIT (tangent
  touches), < 0 is MISS. Interval stage decides HIT iff lo > 0
  (or the interval is exactly [0,0]), MISS iff hi < 0, else
  UNCERTAIN. Stage 3 decides HIT iff exact sign >= 0.
- **Endpoint convention (frozen before any board hash).** All
  interval endpoint selection (imul folds, isqr hi fold, box
  slab folds) goes through the library `msf*_minimum` /
  `msf*_maximum` (propagating 9.6 forms). Number forms are
  banned from the workload core; a source scan for `_number`
  is a gate. Signed-zero endpoint bits are therefore whatever
  9.6 delivers, identically on host and board.
- **Box.** Slab test in binary64 with both an outer (RD/RU) and
  an inner (RU/RD) t-interval intersection: outer empty proves
  MISS, inner nonempty proves HIT, otherwise UNCERTAIN. The
  axis-parallel case (D_i == 0) is explicit workload branch
  logic on exact comparisons. 9.6 does not fix the face case
  and nothing here will imply it does.
- **Torus.** R=2, r=1/2 frozen as bit patterns. First-hit
  bracketing with the 3D evaluation form (survey E2c: the
  t-Horner form could not prove IN at 1e-3), t in [0,11],
  dyadic bisection in t-order, tolerance 2^-10, per-ray scalar
  op cap (cap-hit -> UNCERTAIN). HIT requires a chain of
  proven-OUT segments from t=0, a first not-proven-OUT segment
  at tolerance width, then a point with interval-proven F<0;
  the proven bracket is [candidate lo, proven-negative t].
  All segments proven OUT proves MISS.
- **Hash (IW1).** SHA-256 (project `tests/sha256.c`) over, per
  catalogue row in file order: id, kind, every stage decision,
  endpoint bits at each stage, per-stage scalar op counts. The
  host evaluates every stage for every sphere ray (no
  short-circuit) so the frozen hash does not depend on staging
  policy; the board runner must replay the same sequence.
- **Workload core discipline.** `board/interval_workload.{c,h}`:
  public API only (`include/muse_softfloat.h`), no hardware
  floating-point type named, no allocation, caller-owned
  context struct holds scratch term arrays and the op counter.

Gates to run (script files under Git Bash, `MSF_PYTHON` pinned
to the workspace `.venv`): containment audit vs exact oracle
(zero violations, zero decided-wrong, guard cases UNCERTAIN),
naive-vs-exact disagreement counts reproduced, four mutants
watched failing in scratch, refinement monotonicity (stage
advance and torus tolerance halving), byte-identical catalogue
and host-hash regeneration, `-Wall -Wextra -Werror` with
contraction off, `smoke`/`standard` still PASS.

## 2026-10-27 close entry

Committed on `wave4-interval` as
`1d55a8a08366bfc8bfd3ee7bc7a305347c82c705` (never pushed/merged).
Report: `scratch/parcel-w4interval/report.md`, first line READY.
Host IW1 SHA-256
`ce81d66e9b0b0a4b654c4eb82664417780c6f09c3f866901002b286980ba9aec`
over 710 catalogue rows (616,754 counted scalar ops).

All brief gates passed via `scratch/parcel-w4interval/{build-run,
gates,mutants,budgets}.sh`: independent Fraction containment
audit zero violations and zero decided-wrong at every stage
(sphere UNCERTAIN 488 -> 139 -> 4 across stages; the 4 are the
stage-3 guard rays); survey counts reproduced (tangent400
0/285/115 staging, 386 naive disagreements; limb 63-step
UNCERTAIN band, 31 naive-wrong); four mutants watched failing
(Number-form mutant refused by the source scan; behaviourally
inert on this catalogue, recorded); tolerance-halving
monotonicity; op cap forces UNCERTAIN; byte-identical
regeneration; `smoke` and `standard` PASS untouched.
Hand-written lines 1419 of 3500.

Named not-dones: board sample (firmware/CMake/flashing is lead
work after merge; no on-silicon sentence licensed),
planted-copy verification before merge, per-op board bench.
