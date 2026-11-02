READY

# Wave 4 Step 2c kernel parcel: correctly rounded sinPi/cosPi (parcel-w4trig)

## Verdict

READY. All six registered rows
(msf{16,32,64}_sin_pi / _cos_pi, C-754, all four rounding
attributes) are implemented as one bundle in a single new
translation unit and gated as below. Branch `wave4-trig`
in `worktrees/w4-trig`, base a4f6fb9, tip
81b76357b357b802ebca9ba39a1e1d9005d5f485. Ledger:
`ledger/parcel-w4trig.md` (design entry before code,
checkpoints at the f16 gate, the worst-case gate, and f32
exhaustive completion).

## What shipped

- `src/msf_math.c` (702 lines): exact integer
  period/quadrant reduction (nearest-integer remainder,
  fold to [0, 1/4]); exact integer/half-integer branches;
  shared wide kernel over 32-bit limbs with three Ziv
  stages (W = 160/256/384 bits, 21/29/39 Taylor terms per
  series). Each stage evaluates one truncating
  approximation A; the proven relative error bound Ek
  (generator-derived recurrence, 9-bit margin: endpoints
  A +- A*2^-146 / 2^-242 / 2^-370) is packed through the
  existing `msf_pack_generic` (interval-pack directed
  rounding; agreement of bits and flags decides).
  Cos-shaped results evaluate delta = 1 - cos(u) as a wide
  value with its own exponent and form 1 - delta exactly at
  pack scale (288-bit fixed-point subtraction), so directed
  decisions near +-1 rest on delta's relative accuracy, per
  design. NaNs go through the existing `msf_nan_delivery`
  matrix. Pure C, no allocation, no recursion; worst-call
  stack by -fstack-usage frames: trig_core 608 B + deepest
  wf helper 304 B + pack frame, about 1 KB.
- `tools/gen_trig_tables.py` -> `src/msf_trig_tables.h`:
  pi (bracket-proved 384-bit floor) and exact rational
  factorial-reciprocal coefficients floored to 384-bit
  limbs; per-entry exact containment asserted at generation;
  Ek exponents emitted from the same recurrence;
  regeneration byte-identical (verified by cmp).
- `tests/trig_exhaustive.c` (827 lines): MPFR-decided
  differential harness (bracketed narrowing by the proven
  recipe, fast conversion path for f32/f64 with recipe
  fallback at subnormal scale, finals at 2560 bits for the
  saturation family; decider cross-checked against the
  spike's recipe-narrowed file on 6,000 hard rows and
  against mpmath on 440 seeded inputs, 0 disagreements).
- `tests/gen_vectors_trig.py` -> `tests/vectors/trig-*.vec`:
  43,492 committed lines (11,164 + 14,240 + 18,088),
  provenance `mpfr640-trig:*`, regeneration byte-identical
  (verified). Generator independently computes every
  special from the settled table and refuses on decider
  disagreement (none occurred).
- Wiring: `tables/implemented.tsv` +6 rows at wave 4,
  generated outputs regenerated (drift-clean, inventory
  Tier 2 39/39), `tools/run.sh` SRC + VECS lines,
  `board/CMakeLists.txt` core line, `tests/VECTORS.md` tag
  rows, `docs/metrics/briefs.jsonl` row.
- Hand-written total 2,115 lines (ceiling 4,500);
  generated tables/vectors excluded per brief.

## Design decisions and one amendment

Specials second-read and the two flagged zero-sign cells
are settled in the ledger design entry with three agreeing
routes (odd/even table structure; MPFR 4.2.2 measurement;
execution of the pinned binary64 objects): sinPi at a
negative integer delivers -0 (sign of x) in every mode;
cosPi at any half-integer delivers +0 in every mode.

Error budget re-derived by script (Fraction-exact
recurrence over table quantum, pi truncation, u and u^2
rounding, Horner accumulation with per-term ratios, Taylor
tails by first-neglected-term/(1-ratio), delta terms):
Ek <= 2^-155.9 / 2^-251.9 / 2^-379.9 relative at the three
widths. Stage-final (384-bit) undecided packs the lo
endpoint under a test-only counter; it is unreachable under
the leg-(c) margin (needs a boundary distance under
2^-370 relative against the published-completeness
measurement of 58.58 extra bits at binary64). All gate sets
record zero final-undecided hits.

Amendment (ledger checkpoint, measured): the first kernel
used per-operation interval arithmetic and measured
182k host calls/s, pricing the f32 exhaustive leg at ~74
core-hours. Stage evaluation became the brief's scalar
A +- Ek form (same tables, reduction, delta branch,
interval-pack decision); Ek re-derived for that evaluation
order. 383,700 host calls/s after; f16/wc gates re-passed
bit-identically.

## Gate results (all script files, Git Bash, MSF_PYTHON pinned; logs in scratch/parcel-w4trig/out)

- binary16 exhaustive differential (all finite, both
  functions, all modes): checked 507,904, mismatches 0,
  stage hits 376,832/0/0, final_undecided 0. PASS (2 s).
- binary64 worst cases, 100% of the published inputs
  (mechanical parse of the pinned tree; parsed sets
  byte-equal as sets to the spike's independent extraction,
  74,258 sinPi + 44,334 cosPi unique; MPFR re-decided):
  sinPi checked 297,084, cosPi 206,232, mismatches 0,
  final_undecided 0. PASS (~1 s per file).
- binary64 seeded sweep, 2,097,152 (= 2^21) inputs per
  function: checked 16,777,216, mismatches 0,
  final_undecided 0. PASS (81 s, under shard load).
- binary32 exhaustive finite differential, 32 magnitude
  shards x 2^26, both signs, per-shard logs summed by
  sum_f32.py against the exact finite total: checked
  34,225,520,640 = 4,278,190,080 finite encodings x 2
  functions x 4 modes; mismatches 0; decider undecided 0;
  audits 2,478, audit failures 0; stage hits
  19,864,223,744 / 0 / 0; final_undecided 0. PASS
  (12,613 s wall, 8 concurrent shards,
  2026-10-27 20:18:45 -> 23:48:58 -0700).
- Forced-stage gates (test-only -DMSF_TRIG_FORCE_START):
  f16 exhaustive and full worst-case sets pass starting at
  stage 2 (256-bit) and at stage 3 (384-bit), plus a 65,536
  per-function f64 seeded pass at stage 3; stage-hit
  counters confirm the forced stage took every decision;
  final_undecided 0 everywhere.
- Escalation instrumentation (test-only build): natural
  stage-1 hits take every decision in every gate above
  (stage 2/3 hits 0 outside forced runs), consistent with
  the Ek slack of ~44 bits over the measured binary64
  hardest margin at stage 1.
- Committed vectors replay inside smoke/standard (below)
  and are byte-identical on regeneration.
- Negative controls, each watched failing:
  - truncated table precision (low limbs dropped at stage
    width, -DMSF_TRIG_DROP_LIMB): worst-case gate FAILS,
    sinPi 50,244 mismatches, cosPi 7,326 (one literal
    384-bit-table limb is provably invisible at these
    margins - see ledger; byte-identical regeneration is
    the catch at that scale, verified);
  - quadrant sign flip expectations: 1,360 failures;
  - delta-branch sign error expectations: 1,368 failures;
  - directed neighbour on the wrong side: 3,104 failures;
  - non-integer reduction input against exact-zero
    expectations: 464 failures;
  - unmutated 400-line subset passes (control sanity).
- Budgets in the worktree: `smoke` PASS 44 s (inventory
  tier2 39 implemented, 0 planned, 39 registered; symbol
  and type scans clean); `standard` PASS 94 s. Both runs
  shared the host with the f32 shards.
- Firmware compile (no flashing, no board lock taken):
  CMake/Ninja Pico build of all 5 targets in 74 s,
  447/447 steps. msf_math object: 7,812 B text at the
  symbol-scan -Os flags (about 3.9 KB code + 3.9 KB
  tables); 26,644 B at the board Release flags. UF2
  hashes in the build log (scratch report only; board
  replay remains lead work under the lock).

## Known limitations / lead remainders

- Planted-copy verification before merge is not run by
  this parcel (verifier step, as with prior parcels).
- Board sampled replay and linker-map flash accounting
  under the board lock are lead/board work; this parcel
  only proves firmware targets compile, per the brief.
- KissFFT compat wrappers are the next parcel, untouched.
- f64 leg (c) rests on the settled authority named in the
  brief (published full-range worst-case completeness;
  measured 58.58 extra bits). Nothing in this parcel
  re-derives a binary64 gap from scratch.
- The spike's prec-320 redecided file is blind in the
  saturation family (claims exactly 1.0 towardZero where
  the true value is strictly below 1); our decider's
  2560-bit final escalation resolves it, adjudicated by
  mpmath via 1-cosPi = 2 sinPi(x/2)^2. Lead may want that
  noted against the spike artefact.
- Two decider-side defects were found and fixed en route
  (32-bit mpfr_get_ui truncation on this host; audit
  path must skip special inputs). Both are recorded in the
  ledger checkpoint; the shipped kernel was never at fault
  in either (0 kernel mismatches in every gate).

Claim as registered: C-754 correctly rounded, all four
attributes, all six rows, one bundle. Commit on
`wave4-trig` only; never pushed or merged.
