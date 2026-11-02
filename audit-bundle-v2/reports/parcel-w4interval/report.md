READY

# Step 1c interval workload, host proof (parcel-w4interval)

Verdict READY for lead merge review and the board step. This is
a host proof only: the board sample is a named not-done below
and gates any on-silicon sentence.

Base `b704b4c9b805b584a2e221c3fa889017d480ac88`, worktree
`worktrees/w4-interval`, branch `wave4-interval`. Design entry
precedes code in `ledger/parcel-w4interval.md`.

## Deliverables (owned files only)

- `board/interval_workload.{c,h}` - board-portable original C
  over the public API. No hardware floating type named, no
  allocation, caller-owned context (scratch terms + op counter).
- `board/interval_host.c` - host runner: classifies every
  catalogue ray at every stage, prints per-ray decisions,
  endpoint bits and op counts, plus the frozen IW1 SHA-256.
- `tests/gen_interval_catalogue.py` - fresh generator; exact
  `Fraction` oracle on stored bit patterns. Host naive
  arithmetic appears only in the indicted naive column.
- `tests/interval_catalogue.tsv` - frozen catalogue, 710 rows:
  tangent400=400, adv2k=21, limb=260, guard=4, ordinary=8,
  box=12, torus=5. Every row carries construction provenance.
- `docs/metrics/briefs.jsonl` - this brief's row only.

Hand-written lines: 1419 of the 3500 ceiling (workload 645+114,
host 206, generator 454); catalogue rows excluded per brief.

## Frozen conventions

- Sphere stages: stage 1 binary32 intervals from outward
  directed conversion of each binary64-stored input; stage 2
  binary64 intervals (exact widening for binary32-origin rays);
  stage 3 exact discriminant sign by FMA error-free expansion
  (Knuth TwoSum / FMA TwoProduct, VecSum distillation, sign by
  dominance over an upward-rounded remainder bound), guarded by
  a fresh flags word: overflow/underflow/invalid, capacity
  overflow, or an undecided distillation yield UNCERTAIN.
- Exact discriminant >= 0 is HIT (tangent touches). Interval
  decision: lo > 0 (or exactly [0,0]) HIT, hi < 0 MISS, else
  UNCERTAIN. Sphere class is the discriminant-sign class.
- All endpoint selection goes through library
  `minimum`/`maximum`; Number forms are banned from the core
  and a source scan gates it. Endpoint bits in the hash are
  therefore the 9.6 bits, frozen before any board hash exists.
- Box: outer (RD/RU) slab intersection proves MISS when empty,
  inward-rounded proves HIT when nonempty, else UNCERTAIN.
  Axis-parallel axes are explicit workload branch logic; 9.6
  does not fix the face case and nothing here implies it does.
- Torus: 3D evaluation form, t-order dyadic bisection to
  tolerance 2^-10 over t in [0,11], per-ray op cap (cap hit
  returns UNCERTAIN). HIT = proven-OUT chain from t=0, a first
  not-proven-OUT segment, then a point with proven F<0.
- IW1 hash: SHA-256 over (id, kind, every stage decision,
  endpoint bits, per-stage op counts), all stages fully
  evaluated for every sphere ray, so the hash is independent of
  short-circuit policy. The board runner must replay this
  sequence.

## Measured results (host, Git Bash, MSF_PYTHON = workspace .venv)

Host SHA-256:
`ce81d66e9b0b0a4b654c4eb82664417780c6f09c3f866901002b286980ba9aec`
710 rows, 616,754 counted scalar ops total. Sphere UNCERTAIN by
stage: s1=488, s2=139, s3=4 (the 4 guard rows).

Survey reproduction (independent cross-check, not fitted):
tangent400 decides 0 at f32, 285 at widened f64, 115 left and
all decided exactly at stage 3 - the survey E1c numbers. Limb
f32 UNCERTAIN band is 63 steps (E6c: 63). Naive-vs-exact
disagreements: tangent400=386 (E1b: 11 sign-wrong + 375
zero-collapse), limb=31 (E6c: 31), adv2k=21 (every row), box=3
(the E4 face/edge/face cases), torus=1 (phase-shifted grazing
chord march-miss), guard=3.

Torus per-ray: clean miss 13 evals/1,150 ops; central hit 99/
8,826; ordinary 99/8,816; grazing 357/31,755; grazing shifted
350/31,127; max depth 14. All five decided, brackets verified
against exact rational roots (F(br_hi) < 0 and root inside).

Box: 7 HIT, 5 MISS, 0 UNCERTAIN, all exact-correct, including
the E4 in-face ray (HIT via the axis-parallel branch).

## Gates (script files in scratch/parcel-w4interval/)

- `audit.py` containment audit (independent Fraction
  recomputation from stored bits; TSV exact column
  cross-checked, not trusted): containment violations 0,
  decided-wrong 0 at every stage, decided flips 0, guard rows
  UNCERTAIN at stage 3, counts by family/stage printed. PASS.
- Naive-vs-exact disagreement catalogue reproduced with counts
  (above). PASS.
- Mutants watched failing (`mutants.sh`): M1 RD/RU swapped on
  lo endpoints - 1,330 containment violations, refused. M2 RN
  for directed - 1,329 violations, refused. M4 flags guard
  removed - underflow guard rows decide HIT, one decidably
  wrong (row 685, exact MISS), refused; overflow guard rows
  stay UNCERTAIN even unguarded (NaN terms never decide). M3
  Number forms in the containment path - refused by the
  source-scan gate; behaviourally the audit still passes on
  this catalogue (no decided endpoint depends on NaN
  suppression), so the scan is the refusing gate, as the brief
  designs it.
- Refinement monotonicity: sphere UNCERTAIN 488 -> 139 -> 4
  across stages; torus tolerance halving (2^-11 run): no flips,
  UNCERTAIN 0 -> 0, sphere/box decisions unchanged. PASS.
- Op cap: `--cap 500` forces all 5 torus rays to UNCERTAIN with
  caphit=1; capped run still audits clean. PASS.
- Catalogue and host-output regeneration byte-identical. PASS.
- Host build clean under `-Wall -Wextra -Werror`,
  `-ffp-contract=off`. Source scans clean (Number forms,
  hardware float types, allocation). PASS.
- `tools/run.sh smoke` PASS (24s) and `standard` PASS (55s) in
  the worktree, untouched. The runner and vector set do not
  know this workload exists; no existing file was modified
  except the briefs.jsonl append.

## Audit-script incident (recorded, not a workload defect)

The first audit run crashed converting infinite endpoint bits
(the guard rows legitimately produce [-inf,+inf] stage-2
intervals - valid containment). The audit script was fixed to
honour infinities; the workload was not changed. Re-run PASS.

## Not done

- **Board sample**: no firmware target, no `board/CMakeLists.txt`
  change, no flashing, no RP2040 hash. The IW1 host hash above
  is the value a later board run must match; no on-silicon
  sentence is licensed by this parcel.
- **Planted-copy verification**: named in the brief as a
  before-merge step; not performed by this parcel.
- Per-op board bench numbers (survey G6 second half): not
  attempted; the host op counts are model counts of library
  calls, unpriced on silicon.
- Torus full all-roots isolation and tolerance below 2^-11:
  out of the frozen first-hit shape.
- Subnormal-scale and overflow-adjacent *scene* families beyond
  the 4 stage-3 guard rays: the guard family proves the refuse
  path; a broader scene sweep was not in the frozen shape.
- Trig-defined geometry: out of scope per brief.
