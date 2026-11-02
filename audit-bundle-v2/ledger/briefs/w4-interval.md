# Brief: Wave 4 Step 1c - interval geometry workload (host proof)

Role: parcel-w4interval. Base:
`b704b4c9b805b584a2e221c3fa889017d480ac88` (Step 1 landed).
Worktree: `worktrees/w4-interval` (lead-cut; work only there).
Time box: 360 minutes. Ceiling: 3,500 hand-written lines
(workload C + host main + catalogue generator), generated
catalogue rows excluded. Report:
`scratch/parcel-w4interval/report.md`; ledger:
`ledger/parcel-w4interval.md`, design entry before code.

## Authority and scope

SF-1 Sections 5.2, 9, 14; interval survey
(`scratch/tier2-interval/report.md`, Sections 1/2/6 and the
G1-G7 gates; its `prototype*.py` are project scratch evidence
you may read and re-derive from, not code to copy). This parcel
is the **host proof** of Step 1c: a board-portable original C
workload core over the public API, an exact-rational oracle, a
frozen ray catalogue, and a deterministic host hash. Board
firmware/CMake/flashing is lead work after merge - no board in
this parcel. Trig-defined geometry is out of scope.

Every ray ends **HIT, MISS, or UNCERTAIN-at-budget** - never a
silently wrong sign. Claims are containment claims, never
accuracy claims.

## Workload (frozen shape)

1. **Staged ray-sphere discriminant classification.**
   Stage 1 f32 intervals (directed Tier 1 ops); stage 2 the
   same rays widened to f64 intervals; stage 3 exact sign by
   FMA error-free-expansion (TwoProduct/TwoSum over Tier 1
   binary64 ops) for the discriminant, with a flags guard: an
   exact stage that overflows/underflows its proof yields
   UNCERTAIN, never a sign.
2. **Ray-box slab test** with endpoint selection through the
   library's `minimum`/`maximum` (Step 1 rows). Number forms
   are **banned from the containment path** (survey E4) - a
   source-scan gate proves no `*_number` call exists in the
   workload core. The axis-parallel/face case is explicit
   workload branch logic; 9.6 does not fix it and the report
   must not imply it does.
3. **Torus implicit first-hit bracketing** for named rays
   (at minimum: clean miss, central hit, and the survey's
   grazing chord R=2 r=1/2): interval evaluation of the quartic
   along segments + bisection to a stated tolerance, per-ray
   op cap enforced (cap-hit -> UNCERTAIN), op/depth counts
   printed per ray.
4. **Frozen catalogue + exact oracle.** A fresh Python
   catalogue generator (exact `Fraction` decisions for
   sphere/box; exact endpoint signs for torus brackets)
   emits a committed TSV: regenerated deterministic versions
   of the survey's tangent-by-construction family (n=400,
   seeded), the adversarial distance-2^k family, a limb
   scanline family, box face/axis cases, and the named torus
   rays. Each row carries construction provenance. The C host
   runner classifies every catalogue ray at every stage and
   prints a SHA-256 over (ray id, stage decisions, endpoint
   bits, op counts) - the hash the board run will later match.
   Endpoint bits use the library minimum/maximum convention
   frozen here, before any board hash exists.

## Owned files

`board/interval_workload.{c,h}` (new, public-API only, no
hardware floating-point types named), `board/interval_host.c`
(new host main), `tests/gen_interval_catalogue.py` (new),
`tests/interval_catalogue.tsv` (generated, committed),
`docs/metrics/briefs.jsonl` (this brief's row only).

Forbidden: `src/`, `compat/`, `include/`, tables, generator,
runner, `tools/run.sh`, existing `board/` files and
`board/CMakeLists.txt` (firmware target is lead work), README/
RECORD. No dynamic allocation in the workload core; no
third-party interval/geometry code; naive host arithmetic may
appear only as the indicted comparison in the catalogue
generator, never as an oracle.

## Gates (worktree, script files, Git Bash, MSF_PYTHON pinned)

- Containment audit vs the exact oracle: zero violations over
  the whole catalogue, counts by family/stage printed; zero
  decided-wrong at every stage; stage-3 forced-overflow cases
  yield UNCERTAIN.
- Naive-vs-exact disagreement catalogue reproduced with counts
  (tangent family, limb scanline, grazing chord march-miss).
- Mutants watched failing (scratch): RD/RU swapped on one
  endpoint; RN substituted for directed; Number form in the
  containment path; exact-stage flags guard removed.
- Refinement monotonicity: UNCERTAIN non-increasing under stage
  advance and tolerance halving; decided rays never flip.
- Catalogue + host hash regeneration byte-identical; host
  runner rebuilds clean under `-Wall -Wextra -Werror`
  (contraction off); `smoke`/`standard` still PASS untouched.

Planted-copy verification before merge; board sample is a
named not-done here and gates any on-silicon sentence later.
