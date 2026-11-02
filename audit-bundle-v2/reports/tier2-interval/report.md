# Interval arithmetic for geometry as a Tier 2 workload

**Recommendation: ADOPT WITH FRAMING.**

Adopt a guaranteed interval-geometry workload (sphere/box classification
staged into implicit-surface root isolation, torus-class). Frame it
honestly:

- **It is a Tier 1 workload.** Everything load-bearing already ships:
  directed rounding as an explicit per-call argument (toward
  +/-infinity), directed FMA/div/sqrt, exact f32->f64 widening, and
  correctly rounded cross-format ops. Measured below: staged
  f32-interval -> f64-interval refinement decided 285 of 400 brutal
  tangent cases that f32 could not decide at all, with zero wrong
  decisions, using only Tier 1 calls.
- **The only Tier 2 addition it earns is the Clause 9.6
  minimum/maximum family**, and only in the semantics-owning sense:
  interval hull/intersect/endpoint selection needs one library-owned
  NaN/signed-zero/signaling policy instead of per-helper compare-and-
  select re-derivations. Containment survives without it. If the
  earning bar is strict new capability, the same evidence reads
  REJECT-as-Tier-2-vehicle, adopt-as-Tier-1-workload; the workload
  itself is worth doing either way.
- **Not earned** (remove-it evidence in Section 3): augmented
  add/sub/mul, Clause 9.4 reductions/dot, NaN payload get/set,
  dynamic rounding get/set, ties-to-away attribute, roundToOdd, and
  every Clause 9 mathematical function including trig and hypot.
  Reductions as standardized are actively unusable here: their
  numeric results are implementation-defined, so no containment
  proof may rest on them.
- **Scope condition:** polynomial/quadric geometry only (spheres,
  boxes, torus-class implicits, orientation predicates). Trig-defined
  geometry (kinematics, trig implicits) is the one direction that
  could earn Clause 9 functions; it is excluded and would need its
  own study with directed-mode worst-case gates (Section 4.3).

Base: `54e4bff` (HEAD `32dac7d` at study time; diff between them is
empty for the header, COVERAGE.tsv, and SF-0 — MEASURED). Tier 1 at
base: 783 of 783 instantiations implemented (docs/COVERAGE.tsv,
counted); the header contains no minimum/maximum, augmented,
reduction, payload, or Clause 9 function (searched). Tags: MEASURED
= ran/read this study; COMPUTED = arithmetic on measured inputs;
BELIEVED = extrapolation. Prototype evidence is my own scratch code
in `scratch/tier2-interval/` (`prototype*.py`, results in
`prototype*-results.txt`, `analysis-numbers.txt`); no third-party
interval/softfloat implementation was consulted as code.

## 1. What the prototype measured (evidence index)

Model: exact rational (`Fraction`) endpoints; every scalar op
emulates a library call by computing the exact result and rounding
it toward -inf/+inf to f32/f64 with a from-first-principles rounder.
Every interval result was asserted to contain the exact rational
result (~5,071 containment assertions across E1-E8, COMPUTED from
experiment sizes; an assertion failure would have halted the run;
zero failed). Naive models are host RN f32/f64 — the thing indicted,
never the oracle.

| # | experiment | headline numbers (MEASURED) |
|---|---|---|
| E1 | ray-sphere discriminant, adversarial f64 family (tangent at distance 2^k) | exact disc +2.2e-16 (HIT); naive f64 returns exactly 0 (tangent) at every k=10..40; interval f64 UNCERTAIN, width 2.3e-10 -> 4.0e8 as k grows — never wrong |
| E1b | tangent-by-construction random f32, n=400 | naive f32: 11 sign-wrong, 375 collapsed to 0 vs nonzero exact; interval f32 decided 0, wrong 0 |
| E1c | same 400, staged refinement | f64-widened intervals decided 285, left 115 for an exact-expansion stage, decided-wrong 0 — all Tier 1 ops |
| E2/E2c | torus (R=2, r=1/2) grazing ray, chord width 0.063 in t (exact rational proof) | naive march h=0.10 MISSED the chord (phase-shifted), h=0.05 found it; interval first-hit bracket proven with 757 evals / 30,280 endpoint ops at tol 1e-3; full all-roots isolation at 1e-5: 7,735 evals / 464,100 ops (dependency blow-up is real) |
| E8 | torus cost by ray type | clean miss 71 evals / 2,840 ops; central hit 194 / 7,760; ordinary hit 220 / 8,800; grazing 757 / 30,280 |
| E3 | interval dot3 tightness at >=100x cancellation, n=200 | f32 directed chain width median ~64 f32-ulps; f64 chain outward to f32: median ~0.25 ulp, identical to exact-dot-rounded-once in this sample |
| E4 | ray-box slab at D=0 with origin exactly on face plane | exact answer HIT; propagating minimum/maximum -> NaN -> MISS; minimumNumber-style suppressing -> tmin=+inf -> MISS; only an explicit axis-parallel branch answers HIT |
| E5 | exact dot3 by expansions, op count (COMPUTED) | FMA error-free-transformation route 36 calls (Knuth TwoSum) or 21 (Fast2Sum); augmented route 8 calls; augmented adds no expressible result |
| E6 | 48x48 sphere grid, far-offset scene, f32 | 106 endpoint ops/ray general-case (57/ray FMA-chain-optimized, analysis-numbers); coarse random pixels: 0 naive errors — errors concentrate in the limb band, next row |
| E6c | limb scanline, direction stepped by single f32 ulps, 260 steps | exact first-MISS at step 31; naive f32 sign wrong at 31 steps, first negative at step 62 (limb displaced ~31 ulp-steps, tangent-zero plateau between); interval UNCERTAIN at 63 steps, proven MISS at 78 |
| E7 | orient2d, det exactly -1 at coordinate scale 2^k | k<=26 naive+filter correct; k=27 (products pass 2^53): naive f64 collapses to +0.0 (says collinear), interval UNDECIDED with honestly growing width; random ordinary cases: filter decides 300/300 |

Negative result worth stating: on coarse random pixels (E6) naive
f32 made no classification error at all. Naive failure is not
uniform noise; it concentrates exactly at silhouettes, tangencies,
thin chords, and far-from-origin cancellation — which is why the
demo must be a limb/grazing exhibit, not a beauty render (Section 6).

## 2. Candidate comparison

| candidate | Tier 2 it could earn | verdict |
|---|---|---|
| A. Guaranteed ray/box + ray/sphere classification (HIT/MISS/UNCERTAIN) | 9.6 min/max (semantics only; E4 shows it does not fix the slab face case) | Adopt as outer stage of B; too shallow alone |
| B. Interval implicit-surface root isolation (polynomial implicits, torus) | 9.6 min/max (hull/intersect); nothing else | **Adopt as headline.** Strongest science (containment + IVT bracket proofs), visible naive failures (E2 missed chord), honest costs (E8) |
| C. Robust predicates via floating expansions (orient2d/3d) | augmented add/mul — performance only (E5: 2.6-4.5x fewer calls on the exact stage, same results) | Reject as headline; absorb its technique as B's exact refinement stage. It is exact arithmetic, not interval geometry, and Tier 1 FMA already makes TwoProduct a 2-call idiom |
| D. Interval CSG (t-interval booleans over primitives from A/B) | more min/max call sites; no new numerics | Defer; optional stretch inside B. Scene/code complexity buys no new library evidence |
| E. Interval kinematics (joint-angle intervals) | Clause 9 sin/cos with directed correct rounding — genuinely intrinsic trig | Reject here. Only candidate that truly needs new functions, but weakest fit: no robotics assets/story in this project, and the enclosure gate (4.3) is the most expensive in Tier 2. Revisit only by owner direction |

Proposed SF-1 workload shape (B with A/C stages): a guaranteed
classification renderer. Stage 1: f32 interval discriminant/slab
tests (cheap cull). Stage 2: f64-widened intervals for survivors
(E1c: decides most). Stage 3: exact sign by FMA expansions and/or
segment root isolation to tolerance for the implicit surface. Every
ray ends HIT, MISS, or UNCERTAIN-at-budget — never silently wrong.

## 3. Operation inventory: remove it and what breaks

Tier 1 = in the header at base and implemented per COVERAGE.tsv.
"Load-bearing" = removing it breaks a proof or makes the result
unattainable, not merely slower or uglier.

| operation | tier | remove it and what breaks |
|---|---|---|
| add/sub/mul/div with explicit toward +/-inf argument | 1 | **Everything.** Outward rounding is the containment mechanism. The explicit-argument core is better for intervals than a dynamic mode: both endpoint directions in one expression, no state, no save/restore between the RN exact stage and RD/RU stages, IRQ-safe (SF-0 3.4 caveat avoided) |
| FMA, directed | 1 | Dot products/ifma chains widen faster; TwoProduct falls back to Dekker splitting (more ops, more proof surface, needs its own no-overflow argument). Breaks the cheap exact stage (C) |
| sqrt, directed | 1 | Hit-distance enclosures and interval hypot-style bounds lose their monotone enclosure; classification by discriminant survives (no sqrt needed) |
| convertFormat + formatOf cross-format ops, directed | 1 | Stage-2 widening (E1c: 285/400) and E3's 100x dot tightening disappear. Exact f32->f64 conversion and exact f32 products in f64 are a Tier 1 inheritance this workload exploits constantly |
| comparisons (quiet/signaling), totalOrder, class/isFinite family | 1 | Endpoint selection, empty/degenerate detection, and stage decisions need ad-hoc bit surgery. Load-bearing as the decision layer |
| nextUp/nextDown | 1 | Minor: convenience for widening point values (e.g. parsed scene constants) into intervals; directed ops already cover computed values |
| scaleB | 1 | Minor: exact dyadic segment halving/scaling convenience; mul by powers of two substitutes |
| remainder | 1 | Unused by polynomial scope. Would matter only inside a future trig enclosure's argument checks |
| **9.6 minimum/maximum family (8 names)** | **2** | **Earned, framing-only.** Without it, every hull/intersect/imul endpoint selection (dozens per ray) is workload compare-and-select. Values are identical for non-NaN endpoints, so containment survives; what breaks is semantic ownership: NaN policy, signaling-NaN flagging, and -0/+0 endpoint choice (ordered by 9.6, arbitrary under `a<b?a:b`) become workload-defined, and endpoint-bit hashes (SF-1 board gate) then rest on helper conventions. E4 proves the policy choice is a silent-wrong-answer hazard, and proves 9.6 alone is not the fix (both 9.6 flavors miss the face case; the axis-parallel branch is workload logic either way). Cheap gate: project-exact bit-level oracle, no Table-Maker problem. Number forms must be banned from the containment path (they silently discard a NaN axis — E4) |
| augmented add/sub/mul (9.5) | 2 | Not earned. Exact stage costs 21-36 calls instead of 8 per dot3 (E5), on a stage E1c leaves at 115/400 of already-adversarial rays and E7 at 0/300 ordinary ones. Also a poor fit where it first looks useful: the augmented head is rounded ties-toward-zero (S1 Section 5), not toward +/-inf, so pairs do not serve directly as interval endpoints |
| reductions sum/dot/sumSquare... (9.4) | 2 | Not earned, and not usable: 9.4 results are implementation-defined approximations (any association, any wider format — S1 Section 5; SF-0 2.7 already limits the claim to exception discipline). A containment proof may not rest on a dot with no accuracy contract. The tight dot this workload wants is a workload helper (directed FMA chain / widened chain / expansion), or would be a new project-named exact-dot — not a 754 claim |
| dynamic rounding get/set (9.3), ties-to-away attribute, roundToOdd | 2 | Not earned. The core's explicit rounding argument strictly dominates for interval code. roundToOdd is an implementation technique for future correctly rounded functions, not a workload input |
| NaN payload get/set (9.7) | 2 | Not earned. Empty intervals encode as [+inf,-inf] with a pre-check before ops that would form 0*inf, or as a status enum — both type-safer than payloads. Tagging indeterminacy sources via payloads is diagnostics, replaceable by an enum, and payloads do not reliably survive arithmetic as a data channel |
| hypot, rSqrt (9.2) | 2 | Not earned. Interval norm encloses today by monotone composition isqr/iadd/sqrt with directed rounding; scaleB handles overflow scaling. Correctly rounded hypot would tighten endpoints by ~ulps, nothing structural |
| sin/cos/tan + Pi forms, atan2, exp/log, pow/rootn/pown, compound (9.2) | 2 | Not earned under polynomial scope: no surface in A-D needs them. Camera/scene setup can pin directions as exact bit patterns (IAS15 precedent, SF-0 Section 9) instead of computing trig at runtime. The gate they would need is in 4.3 |

Workload-level helpers that must NOT become library claims: the
interval type and its ops; sign-aware product/FMA-chain dot
endpoints; exact-expansion discriminant/dot sign; segment isolation
with point-proofs; empty-interval policy; axis-parallel slab branch;
scene, renderer, and hash harness.

## 4. Proof claims and oracles

### 4.1 Claims, each reducible to a Tier 1 gate already closed

- **C1 containment by construction.** Each interval op encloses the
  exact range of the scalar op over its input intervals, given
  correct directed rounding (Tier 1's claim, gated per
  instantiation in COVERAGE.tsv) and exact endpoint min/max
  selection. Induction over the expression DAG gives: exact
  discriminant / exact implicit value range is inside the computed
  interval. This is the workload's core inheritance: SF-1 does not
  re-prove rounding; it names C1's dependence on specific COVERAGE
  rows (add/sub/mul/div/sqrt/FMA/convert in the used formats and
  modes).
- **C2 classification soundness.** Interval entirely >0 (or <0)
  implies the exact classification. UNCERTAIN claims nothing. There
  is no fourth outcome, and no epsilon anywhere in the design.
- **C3 staged refinement soundness.** Widening f32 endpoints to f64
  is exact (convertFormat); the f64 interval is contained in the f32
  one after outward rounding back, so stage advance never flips a
  decision. Expansion stage: error-free transformations are exact
  only under their preconditions (ties-to-even; error terms not
  lost to underflow; no overflow). Caller-owned flags make the
  guard cheap: run the stage with a fresh flags word; if
  overflow/underflow raised, fall back to UNCERTAIN. That
  flag-as-proof-guard idiom is only available because Tier 1 flags
  are data, not process state.
- **C4 root bracket.** Segments proven OUT (interval F > 0 over the
  segment, by C1) chained from t=0, followed by a point whose point-
  interval F is entirely < 0, bracket a root by continuity of the
  polynomial. E2c demonstrates the shape, including the honest cost:
  first not-proven-OUT bracket at t=2.923, proven-negative point at
  3.006, exact root 3.0054 inside. A straddling segment alone proves
  nothing — E2c's first form made exactly that error and the exact
  oracle caught it; SF-1 must encode OUT/IN/point-proof discipline
  in the gate, not in comments.

### 4.2 Oracles

- **Exact rational reference (deciding, for polynomial geometry):**
  discriminant signs, predicate signs, and implicit point values are
  rational functions of exactly representable inputs. An
  arbitrary-precision rational implementation, independently
  reviewed like any project oracle (SF-0 4.3 pattern), decides every
  SF-1 vector. This study's prototype is a seed and an existence
  proof, not the oracle itself.
- **MPFR:** cross-check only here (rationals are stronger for this
  scope); becomes deciding only if trig ever enters.
- **Host f32/f64 naive builds:** negative exhibits with pinned flags
  (strict, no contraction — SF-0 Section 9 discipline), never
  references. The catalogue of naive-vs-exact disagreements (E1,
  E1b, E6c, E7 families, with construction parameters) freezes as
  SF-1 vectors with provenance.
- **Host-vs-board bit identity:** IAS15FH1-shaped hash over
  (classification, endpoint bits, bracket bits) per ray in fixed
  order, sampled rays replayed over the existing CDC harness with
  UF2 hash, commit, and board ID named — the `board` budget pattern,
  not a full-frame board render.
- **Randomized adversarial generation:** tangent-by-construction
  (perturb exact tangency by ulps), far-offset scenes, ulp-stepped
  limb scans, phase-shifted grazing chords, slab face cases,
  subnormal-scale and overflow-adjacent transforms (last two named
  here, not prototyped — SF-1 owes them).

### 4.3 Scalar correct rounding is not an enclosure (trig gate)

If trig is ever adopted, ties-to-even correct rounding alone proves
no containment. The enclosure theorem interval code actually needs:
for function f and segment [a,b], the result must contain
{f(x) : a<=x<=b}. Endpoint evaluations suffice only where f is
monotone on [a,b], and then only if the scalar op is correctly
rounded **toward -inf and +inf** (the applicable-attribute reading
of 9.1 that S1 Section 5 records), giving
[RD(f(a)), RU(f(b))] bracketed endpoints. Interior extrema (sin/cos
turning points at pi/2 + k*pi) must be detected and clamped to
+/-1, which needs a proven enclosure of pi and exact determination
of k — an argument-reduction enclosure problem that stays
workload-side and grows with |x| even if the library ships sin.
Directed-mode worst cases are different inputs from the
ties-to-even worst cases CORE-MATH publishes (S2 Section 4 item 6),
so SF-0 2.7's Table-Maker-grade bar would need a per-mode
worst-case argument. That is the price tag kinematics carries and
polynomial scope avoids.

## 5. RP2040 feasibility (estimates: BELIEVED, anchors stated)

Op counts are MEASURED in the model (Sections 1, E8). Rates are
not: no per-op board bench exists yet (`bench` is skeleton-only,
SF-0 Section 6 item 9). Two anchors bound the truth:

- **Pessimistic, measured-effective:** IAS15 on silicon: 1.58
  accepted steps/s at ~13,100 f64 ops/step (docs/RECORD.md Wave 3;
  op mix in scratch/ias15/report.md) = ~2.07e4 f64 ops/s effective
  (~6.0e3 cycles/op at 125 MHz, COMPUTED), including div-heavy mix,
  AEABI wrapper, and non-FP overhead. Pure-op rate is higher; this
  is a floor.
- **Optimistic, unmeasured goal:** SF-0 Section 8 working budget of
  basic ops within 2x ROM averages RAM-resident (ROM: f32 add/mul
  71/58, f64 mul 155 cycles, S3 Section 4.1) gives ~9e5 f32 ops/s,
  ~4e5 f64 ops/s blended. Nobody has measured the library within
  this goal; SF-1 must produce the first per-op bench numbers
  before quoting any rate publicly.

| job | endpoint ops | @2.07e4/s (floor) | @goal |
|---|---|---|---|
| sphere classification 48x48, f32 (E6 general-case) | 244,224 | ~12 s | ~0.3-0.6 s |
| sphere 128x128, f32 FMA-chain (57 ops/ray) | ~934k | ~45 s | ~1-2 s |
| torus frame 64x64, f64, avg 5k ops/ray (E8: miss 2.8k, hit ~8k, grazing 30k) | ~20M | ~17 min | ~50 s |
| torus frame 48x48, same avg | ~12M | ~9 min | ~28 s |
| one pathological grazing ray, tol 1e-5 all roots (E2) | 464k | ~22 s/ray | ~1 s/ray |

Reading: sphere/box classification frames are board-cheap under
every anchor. A torus frame is minutes-class at the floor —
IAS15-precedented (its full period is ~10 min and the video treats
it as time-lapse with hash beats, never real-time). The honest
board claim is sampled-ray hash identity plus a time-lapse strip,
not interactive rendering. Silhouette-heavy views push the average
toward the grazing tail; a per-ray op cap that returns
UNCERTAIN-at-budget bounds worst-case frame time by construction
(and is a correctness feature: no hang, no silent guess).

Memory (COMPUTED, static): interval 8 B (f32) / 16 B (f64);
subdivision stack depth ~25 at tol 1e-5 over unit-ish domains,
<1 KB; expansion stage <=~16 f64 terms ~128 B/ray; scene trivial;
128x128 1-byte classification map 16 KB. All trivially inside
264 KB SRAM (S3 Section 4.2); zero core allocation compatible.
Second core could halve frame time (stateless core calls; no
wrapper-state sharing) — BELIEVED, not needed for the claim.

Subdivision blow-up, stated plainly: naive interval evaluation of
the torus implicit pays the dependency effect twice (E2: 7,735
evals for full isolation of one grazing ray, vs 757 first-hit at
coarser tolerance). Mitigations are workload-level and known:
first-hit-only marching, t-polynomial or derivative (interval
Newton/monotonicity) pruning, f32 outer + f64 refinement staging.
Formulation matters as much as tolerance — in E2c the t-Horner form
could not prove any segment IN at 1e-3 (coefficient cancellation)
where the 3D form could at 1e-5; SF-1 should treat evaluation form
as a measured design choice, not a given.

## 6. Demo and video value

Smallest visual experiment (all host-reproducible, board-sampled):

1. **Three-panel 48x48 torus classification** at a grazing view:
   naive f32 point-march (fixed step) / exact-rational reference /
   guaranteed HIT-MISS-UNCERTAIN. E2's construction guarantees the
   naive panel is missing a chord sliver the other two agree on.
2. **Limb strip:** one scanline stepped by f32 ulps across a far
   sphere's silhouette (E6c data): naive edge sits ~31 ulp-steps
   late with a tangent-zero plateau; guaranteed panel shows a
   63-step UNCERTAIN band exactly where the naive panel is silently
   wrong. This is the single most legible frame: "the honest pixels
   are the ones naive rendering gets wrong."
3. **Refinement toggle:** re-run UNCERTAIN pixels through stage 2/3
   live in the video; band must shrink (E1c pattern 400 -> 115 ->
   exact). 

Negative controls: band-doesn't-shrink = bug, shown by construction;
f64-naive panel on the E1 family still misclassifies (not an f32
strawman); exact-rational audit of sampled pixels must never
contradict a decided pixel; translating the scene far from origin
must grow the UNCERTAIN band, not move decided pixels. Viewer-
visible distinction: cracks and displaced silhouettes vs an
explicit, shrinkable honesty band. No real-time claim.

## 7. Proposed SF-1 gates

In `tools/run.sh` shape (a new workload budget; names are proposals):

- **G1 containment audit:** zero violations vs the rational oracle
  over the frozen adversarial catalogue + seeded randoms; counts
  printed by family. Includes stage-3 flag-guard cases (forced
  underflow must yield UNCERTAIN, never a wrong sign).
- **G2 disagreement catalogue:** every naive-vs-exact disagreement
  vector carries construction provenance; the naive builds are
  pinned (flags recorded) and a contracting build is a named
  control that must be seen to disagree more.
- **G3 mutants refused, watched failing first:** RD/RU swapped on
  one endpoint; RN substituted for directed; min/max policy flipped
  (Number form in containment path); exact-stage flag guard removed.
- **G4 refinement monotonicity:** on the frozen ray set, UNCERTAIN
  count is non-increasing under tolerance halving and stage advance;
  decided rays never flip.
- **G5 termination/budget:** per-ray op cap enforced; ops/ray and
  depth histograms printed; cap-hit returns UNCERTAIN.
- **G6 board sample:** hashed ray sample identical host vs RP2040
  (artifact hash, commit, board ID, placement, clock named);
  first measured per-op bench table for the used ops, replacing
  Section 5's anchors with measurements.
- **G7 (only if 9.6 adopted):** minimum/maximum rows land in
  COVERAGE.tsv with project-exact authority and their own gates
  **before** any workload claim uses them; decide the
  endpoint-select bit convention before G6 freezes hashes
  (compare-select vs 9.6 differ on -0/+0 endpoint bits).

## 8. Open questions for owner/lead

1. Framing call: accept 9.6 as "earned" in the semantics-owning
   sense, or hold the strict-capability line (then this is a Tier 1
   workload that earns nothing, still worth adopting)?
2. If 9.6 lands: all 8 names, or stage minimum/maximum first and
   the rest only if a caller appears? (Workload bans Number forms
   in the containment path regardless — E4.)
3. Board ambition: sampled-ray hash proof + hosted frames
   (recommended), or a full frame computed on the Pico as a
   minutes-long time-lapse beat?
4. Confirm trig-defined geometry out of scope for SF-1 (Section
   4.3 is the price of re-opening)?
5. Format posture: f32 intervals with f64 staged refinement
   (recommended; makes UNCERTAIN bands visible and board costs
   sane) vs f64 throughout?
6. Does SF-1 get written as a successor study in SF-0's shape, and
   who independently reviews the rational oracle before G1 counts?

## 9. Anything the brief got wrong

- The brief's test list ("augmented add/mul, min/max family, NaN
  payloads, dynamic rounding, reductions/dot products, Clause 9
  functions") is the right checklist, but two items are weaker than
  their billing suggests: augmented heads are not outward-rounded
  (Section 3), and 9.4 reductions carry no accuracy contract at
  all, so a "reduction" can never be the load-bearing piece of a
  *guaranteed* workload as standardized. Measured, the exact stage
  these items compete for is already served by Tier 1 FMA chains
  and cross-format widening (E1c, E3, E5).
- Minor: 754-2019 9.5 has three augmented ops (addition,
  subtraction, multiplication; S1 Section 5), not two.
- The lead's dispatch note believed interval geometry "more
  naturally stresses augmented operations/reductions"
  (`ledger/lead.md` 2026-10-27 13:54). Measurement disagrees: what
  it stresses is directed rounding, FMA, and widening — all Tier 1.
  That is a finding about the shape of the workload, recorded as
  the brief instructed ("do not force a fit").

## 10. Method and limits

Read: the brief, ledger README, AGENTS.md, SF-0 in full (2.7 and 4
weighted), S1 Section 5 + S2 Section 4 in context, COVERAGE.tsv
(783 implemented rows counted, header operation families
inventoried), RECORD.md (IAS15 rates), S3 cycle/memory tables.
Prototype: four scratch script files + one analysis script, run
under the project venv; every containment claim above was asserted
against exact rationals at runtime. Limits: the prototype models
library semantics — it is not the library, and its directed sqrt
is <=1 ulp conservative (unused in classification paths); op counts
are model counts of endpoint scalar ops (call overhead, wrapper,
and placement effects unmeasured); per-op RP2040 rates are
extrapolations between two named anchors 20-40x apart until G6
measures them; torus costs are for one evaluation form and a
bisection-only isolator, i.e. an upper-bound shape, not an
optimized design; subnormal-scale and overflow-adjacent scenes
were not prototyped. Nothing in the repository or on the board was
modified.
