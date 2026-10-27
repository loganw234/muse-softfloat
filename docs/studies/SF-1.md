# SF-1: Tier 2 after Tier 1 - workloads first, claims second

Status: **approved by Logan on 2026-10-27 (decisions recorded in
Section 14). Steps 0-1c, optional Step 2a, and the Step 2b
pricing spike may begin; Step 2c still requires a closed 2b.**

Date: 2026-10-27. Author: the lead (Muse Code,
muse-wonder-full-1.0). Base: `32dac7d` (repository facts read at
`54e4bff`; the two differ only by `docs/metrics/briefs.jsonl`).
Evidence: SF-0; four read-only Tier 2 surveys kept in scratch
(`scratch/tier2-kissfft/report.md`, `scratch/tier2-interval/
report.md`, `scratch/tier2-clause9/report.md`, and
`scratch/tier2-architecture/report.md`); the lead ledger outside
this repository. IEEE 754-2019 is cited by clause only; the
licensed PDF is never copied here.

## Contents

0. The short answers
1. Why Tier 2 needs a new study
2. The earning rule and the two workloads
3. The authorised-prefix shape
4. The lead seam (Step 0)
5. Step 1: Clause 9.6/9.7 and the interval proof
6. Step 2: KissFFT and the trig fork
7. Everything deferred, by name
8. Authorities, gates, and claim discipline
9. Board evidence and public wording
10. Questions for Logan, with recommendations
11. Risks and stop rules
12. Sources
13. Send-backs
14. Approval and decisions

## 0. The short answers

1. **Do not start with the 180-row Clause 9 menu.** The studies
   count a homogeneous Tier 2 surface of 180 core instantiations
   plus 5 wrapper operations (Clause 9 survey, MEASURED through
   the repository generator). SF-0 Section 2.7 already says Tier 2
   is conditional; the owner added two sharper rules on
   2026-10-27: another scientific workload should *earn* the
   additions, and **anything added for one supported format is
   added for binary16, binary32, and binary64 alike** (the
   format-parity rule, Section 2.1). This study therefore
   proposes a stoppable prefix of all-format family bundles, not
   a plan to do all 180 and not single-format additions.

2. **Adopt interval geometry first, framed as mostly a Tier 1
   workload.** A guaranteed interval-geometry workload (spheres,
   boxes, torus-class implicit surfaces, staged refinement) is
   scientifically strong because it returns HIT / MISS /
   UNCERTAIN instead of a silently wrong sign. But its load-bearing
   operations (directed rounding, directed FMA/div/sqrt, widening)
   already ship in Tier 1. The only new surface it earns is
   Clause 9.6 minimum/maximum in the **semantics-owning** sense:
   one library-owned NaN / signed-zero / signaling policy for
   endpoint selection, instead of per-helper compare-and-select.
   If the earning bar is strict new capability, interval geometry
   earns zero; the workload is still worth doing.

3. **Adopt KissFFT second, only under a runtime-generation
   contract.** Measured statically and dynamically, KissFFT's
   execution path is only `+`, `-`, `*` (already Tier 1). Its
   absent functions are at plan allocation: binary64 `sin`/`cos`
   for twiddles, plus one `floor` already covered semantically by
   Tier 1 `roundToIntegralTowardNegative`. If twiddles may be
   pinned offline per N (the IAS15 coefficient pattern), KissFFT
   runs on today's Tier 1 and earns **nothing**. It earns the
   binary64 trig pair only if SF-1 requires on-device runtime
   twiddle generation for caller-chosen N. Under the parity rule
   the library bundle is then the pair at **all three formats
   (6 rows)**; the binary16/32 rows are parity-mandated matching
   rows, never described as called or earned by KissFFT.

4. **Fork B is adopted.** Either fork would ship its pair for
   binary16/32/64 as one bundle; only the binary64 rows sit in
   KissFFT's call path.
   - **Fork A (unmodified KissFFT):** keep the upstream phase
     formula; implement correctly rounded `sin`/`cos` over the
     full Clause 9.2 domain. Claim: twiddles are correctly rounded
     **of the computed phase** arguments, not of the exact angles.
   - **Fork B (exact-angle twiddles, adopted):** make one named
     change to the phase formula so binary64 twiddles use
     correctly rounded `sinPi`/`cosPi` of exact cycle fractions.
     Claim, at the gated `N=2^k` sizes: twiddles are correctly
     rounded **of the mathematical twiddle angles**. The word
     "unmodified" is forfeited for that one site.
   Logan adopted the lead's Fork B recommendation at approval
   (Section 14); Fork A remains the priced fallback if 2b cannot
   close Fork B as a bundle.

5. **Before any semantics, land the seam.** Today's full-surface
   inventory assertion (the control-9 successor) refuses planned
   rows by design (Tier 1 is 783/783). Tier 2
   first needs tier/claim accounting, new signature shapes, and
   watched-failing controls proving Tier 1 cannot silently
   regress while Tier 2 rows are still planned. No min/max,
   payload, augmented, reduction, or math parcel starts before
   that seam closes.

6. **Smallest first honest Tier 2 claim:** Clause 9.6 min/max
   (24 rows) + Clause 9.7 NaN payloads (9 rows) = **33 rows**,
   every name at all three formats per the parity rule, claim
   class C-754 (Section 8), gated by project-exact bit-level
   evidence. Only the minimum/maximum names are workload-earned
   (by interval geometry, semantics-owning sense; the workload
   itself runs f32/f64, so their binary16 rows are parity
   matching); the Number forms and payloads are cheap compliance
   breadth along SF-0's order, and SF-1 must say so wherever
   counts are published.

## 1. Why Tier 2 needs a new study

SF-0 Section 2.7 reserved Clause 9 recommended operations, NaN
payload access, dynamic rounding wrappers, augmented arithmetic,
reductions, and mathematical functions as Tier 2 "if time
allows", and forbade approximate functions under conforming
names. Tier 1 closed at 783/783 instantiations with
`tools/run.sh standard` passing (85,148 committed vectors plus
1,117,504 generated standard vectors; READ from RECORD/AGENTS).

Four things changed since SF-0:

- The owner directed (2026-10-27) that Tier 2 continue only with
  another scientific workload that earns the additions, naming
  KissFFT and interval arithmetic applied to geometry.
- The owner directed (same day, while this draft was under
  verification; that verification was stopped and restarted on
  the revised text) a standing **format-parity rule**: in
  general, anything added for one supported format is added for
  each of binary16, binary32, and binary64. SF-1's first draft
  violated it with a binary64-only trig step; this revision
  removes every single-format addition.
- Four independent read-only surveys measured what those
  workloads actually call, what Clause 9 would cost, and what
  the current code shape cannot yet express.
- The owner's hardware situation also changed the order of the
  day without changing Tier 2: a six-board IAS15 cross-chip run
  tested the genuine board and two enumerated clones at 200
  steps (all PASS, 201/201 hash records, ~1.5003 steps/s each at
  125 MHz). The other three clones did not enumerate; the owner
  reports power-only cables and defers the full range test until
  data cables arrive. No Tier 2 claim below depends on that
  deferred run.

## 2. The earning rule and the two workloads

### 2.1 The rule

An addition is **workload-earned** only if removing it breaks the
workload's stated contract (not merely makes it slower, longer,
or uglier). Two weaker categories stay visible:

- **Semantics-owning:** the workload can compose the values from
  Tier 1, but the special-value policy (NaN, signed zero,
  signaling) must live in one gated library place for endpoint
  hashes and containment claims to rest on a single owner.
- **Compliance breadth:** cheap, in SF-0's order, and openly not
  earned by either workload. It may ride a parcel; it may not be
  marketed as earned.

Orthogonal to earning is the owner's **format-parity rule**
(2026-10-27): a family added for one supported format is added
for binary16, binary32, and binary64 alike, as one bundle.
Consequences SF-1 obeys throughout: (1) no single-format parcel
and no family claimed complete until all three formats' rows
have closed their gates - development inside a parcel may
sequence f16 -> f32 -> f64, but merge and public claim happen
at bundle closure; (2) parity is not earning evidence - rows a
workload never calls (binary16/32 trig for KissFFT, binary16
min/max for the f32/f64 interval workload) are labelled
**parity-mandated**, held to the same claim and evidence
standard, and never described as workload-called; (3) refusing
a family at one format refuses the bundle (Section 8).

Anything else is **deferred** until a workload or a later study
earns it. The submission is already complete without Tier 2;
"neither workload earns enough; stop" remains an available
answer at approval time.

### 2.2 Interval geometry (ADOPT WITH FRAMING)

Candidate: guaranteed interval classification for polynomial
geometry only - ray/sphere and ray/box staged into implicit-
surface root isolation (torus class), with f32 intervals,
f64-widened refinement, and an exact FMA-expansion sign stage.
Every ray ends HIT, MISS, or UNCERTAIN-at-budget (interval
survey Section 2).

Why it is good science here:

- Containment is checked against exact rationals in the study
  prototype (~5,071 containment assertions, zero failed).
- Naive failure concentrates where judges can see it: tangent
  and grazing cases. In one measured family, naive f32 was
  sign-wrong on 11 of 400 tangent-by-construction cases and
  collapsed 375 to zero; staged intervals decided 285 of the
  400 at f64 with zero wrong decisions (E1b/E1c).
- A grazing torus chord of exact width 0.063 was missed by a
  naive march at step 0.10 and bracket-proven by interval
  isolation (E2). Costs were measured by ray type, not hidden
  (E8: clean miss 2,840 endpoint ops; grazing 30,280).

What it earns, precisely:

| Addition | Earning class | Remove-it result |
|---|---|---|
| Clause 9.6 `minimum`/`maximum` | semantics-owning | Containment survives; NaN/signed-zero/signaling endpoint policy becomes workload folklore, and board endpoint hashes rest on helper convention |
| Other six 9.6 names | compliance breadth | Nothing in the workload breaks; Number forms are banned from the containment path regardless (E4) |
| Augmented ops, reductions, payloads, dynamic modes, ties-to-away, roundToOdd, all 9.2 math | not earned | Augmented only shortens the exact stage (8 vs 21-36 calls, E5); 9.4 reductions have no accuracy contract and cannot carry containment; trig-defined geometry is out of scope |

Scope condition: no trig-defined geometry in SF-1. Kinematics
or trig implicits would be the direction that earns directed-
mode trig enclosures; that is a separate study (interval survey
Sections 4.3 and 8).

### 2.3 KissFFT (ADOPT WITH FRAMING)

Pinned in the survey: KissFFT 131.2.0, BSD-3-Clause, archive
SHA-256 recorded in `scratch/tier2-kissfft/report.md` Section 1.
The C core (not the C++ header) is the candidate; fixed-point
configurations earn nothing and bypass the library at execution.

Measured call shape (survey Sections 3 and 6):

- Execution (`kiss_fft`, `kiss_fftr`): scalar `+`/`-`/`*` only.
  No division, sqrt, FMA, float comparison, or libm call. ARM
  objects confirm the closed undefined-symbol world
  (`__aeabi_fadd/fsub/fmul` or the binary64 trio).
- Allocation only: N binary64 `sin` + N `cos` per plan (plus N/4
  each for real-input super-twiddles), phase arithmetic, and one
  `floor(sqrt(n))` per alloc. The trig is binary64 even in the
  float configuration, so binary32/binary16 trig is never earned
  by this workload.

Twiddle sensitivity was measured, not assumed (survey Section
8.1, N=1,024, host MinGW64 libm vs ~200-bit mpmath): host
`cos`/`sin` bit-match correctly-rounded-of-computed-phase at
1,022/1,024 points each - nearly CR on these arguments, but not
CR, and refused as an oracle regardless. KissFFT's twiddles
differ from correctly-rounded-of-true-angle at 620/1,024 `cos`
and 590/1,024 `sin` points (the computed phase itself is ~1 ulp
off the true angle), while a 1-ulp flip of one twiddle changed
3 (double) / 4 (float) of 2,048 output scalars. That is why
"the twiddles" are a claim question before they are a kernel
question.

What KissFFT earns, precisely:

| Addition | Earning class | Condition |
|---|---|---|
| Trig pair at binary64 (`sin`/`cos` *or* `sinPi`/`cosPi`) | workload-earned | Only if the demo contract requires on-device runtime twiddle generation for caller-chosen N. Fork decides which pair (Section 6) |
| Same pair at binary16/32 (4 rows) | parity-mandated, **not earned** | Required by the format-parity rule if the pair ships at all; KissFFT's trig is binary64 in every configuration, so these rows are never workload-called. Same C-754 evidence standard (Section 6.2) |
| Compat `__wrap_floor`, `__wrap_sin/cos` or `sinPi/cosPi` path, float-config AEABI trio | integration load-bearing, zero compliance value | Without them nothing links; they retire named traps over gated core rows only. Wrappers exist only where a workload calls them (binary64 trig); parity binds core rows, not compat spellings |
| min/max, payloads, dynamic modes, augmented, reductions, other Clause 9 functions | not earned | KissFFT calls none of them (remove-it test, survey Section 5) |

If runtime generation is *not* required, SF-1's KissFFT story
collapses honestly to a pinned-twiddle consumer demo on Tier 1:
still a fine second bit-identity exhibit, but it funds no trig.

## 3. The authorised-prefix shape

SF-1 authorises a prefix. Every step is a complete stopping
point with its own brief, design entry, planted-copy
verification, serial merge, and RECORD text - the standing
strict-leaning risk-tier policy. Nothing after a refused or
unclosed step is authorised by optimism.

| Step | Contents | Rows | Earned by |
|---|---|---|---|
| 0 | Lead seam: tier/claim accounting, sig/vector shapes, oracle bring-up (Section 4) | 0 new semantics | prerequisite for everything |
| 1a | Clause 9.6 `minimum`/`maximum` (homogeneous) | 6 (2 names x 3 formats) | interval (semantics-owning at f32/f64; f16 parity) |
| 1b | Remaining six 9.6 names + Clause 9.7 payloads | 27 (9 names x 3 formats) | compliance breadth (openly unearned) |
| 1c | Interval-geometry workload proof (host + sampled board hash) | 0 library rows | the workload itself |
| 2a | KissFFT pinned-twiddle consumer demo (Tier 1 only) | 0 core rows | second bit-identity exhibit; de-risks integration |
| 2b | Trig design spike: Fork A vs Fork B priced at **all three formats** against worst-case evidence | 0 | decision gate for 2c |
| 2c | Trig pair (all formats) + runtime-twiddle KissFFT | 6 core rows (2 names x 3 formats; + binary64 wrappers) | binary64 pair: KissFFT under runtime-generation contract; binary16/32: parity-mandated |

Steps 1a-1c are the recommended first authorisation. Step 2a
may run in parallel as workload code (scratch/board only; no
library semantics). Step 2c needs the owner's fork choice
(Section 10) *and* a closed Step 2b pricing note; if the
worst-case argument cannot close inside the hackathon window,
Step 2c returns refused with Steps 0-2a standing - SF-0
forbids the quiet relabel to an approximate claim. Prefix
arithmetic: authorised core rows 33 + 6 = **39**; deferred
(Section 7) 9 + 21 + 111 = **141**; 39 + 141 = 180.

Wave numbering: Tier 2 is wave 4 (the study-round metrics rows
already say so; architecture survey Section 3.1).

## 4. The lead seam (Step 0)

Lead-owned, no new semantics. The architecture and Clause 9
surveys independently found the same blockers; this step is
where they are paid once.

1. **Table columns.** `tables/operations.tsv` gains `tier`
   (1|2) and `claim` (closed token set, Section 8). The
   generator propagates both into `docs/COVERAGE.tsv` and
   aborts on unknown tokens, as it does for sig classes today.
   All 81 Tier 1 families take `tier=1` with one claim token
   meaning the SF-0 required-set claim. No tier or claim is
   encoded in free-text `authority`/`comparison` fields.
2. **Inventory split.** The full-surface inventory assertion
   (control-9 successor) becomes two printed invariants:
   Tier 1 implemented == Tier 1 total (783, refusing any
   regression or silent renumbering), and Tier 2
   implemented/planned counted separately with planned rows
   named. Exit gate includes watched-failing controls both
   ways: a Tier 1 row flipped to planned must refuse; a Tier 2
   row silently deleted instead of implemented must refuse.
3. **Signature and vector shapes.** Add, only as needed by the
   authorised prefix first (homogeneous unary/binary reuse for
   9.6/9.7 and math), then the pair-result shape
   (`<op> <rm> a b -> hi lo flags prov`) and vector shape only
   if a later authorised step needs them. Malformed-shape
   refusals and a corrupted-second-result control are watched
   failing before the shapes are trusted. Stateful wrappers
   never enter the line-replay runner; they are unit-gated
   (flag-op precedent).
4. **Authority vocabulary.** Existing tokens stand. Add at most
   one foreign-oracle corroboration suffix (Section 8) and the
   claim tokens. Host libm never decides a Tier 2 row.
5. **Oracle bring-up.** MPFR binary32/binary16 emulation
   constants are believed, not probed (Clause 9 survey Section
   5). The seam known-answer-probes them (smallest subnormal,
   overflow threshold, directed subnormal rounding) before any
   Tier 2 vector is trusted. If the owner approves the
   CORE-MATH fetch (Section 10), its pin + smoke-vs-MPFR also
   lands here, execution-only, never design input.
6. **Provenance budget.** 43 of 128 tags are used (Clause 9
   survey, MEASURED). Rule: one tag family per generator, not
   per function file; raising the cap is seam work that
   re-watches the overflow refusal.
7. **Budgets.** Smoke stays within ~2x today's committed count
   and wall time; exhaustive/streamed sets belong to
   `standard`. Exhaustive binary16 is required for every Tier 2
   unary family whose authority can decide all encodings.

Exit gate: `smoke` green with zero Tier 2 rows implemented and
at least one planned Tier 2 family present, proving the new
accounting passes the new way and refuses the old way.

## 5. Step 1: Clause 9.6/9.7 and the interval proof

### 5.1 Rows and semantics (homogeneous, all formats)

Tier 2 counts in SF-1 are homogeneous (same-format operands and
result) and, per the format-parity rule, every name below is a
three-format bundle (binary16 + binary32 + binary64) that
merges and is claimed only at bundle closure. Cross-format
`formatOf` expansion would multiply rows up to ~4x and is
refused for SF-1; callers compose with gated Tier 1 conversions
(Clause 9 survey Q1).

- **Step 1a (6 rows):** Clause 9.6 `minimum` and `maximum` for
  binary16/32/64. These are the names the interval workload may
  use for hull/intersect/endpoint selection (at f32/f64; the
  binary16 rows are parity matching).
- **Step 1b (27 rows):** the other six 9.6 names
  (`minimumNumber`, `maximumNumber`, `minimumMagnitude`,
  `maximumMagnitude`, `minimumMagnitudeNumber`,
  `maximumMagnitudeNumber`; 18 rows) plus Clause 9.7 payload
  access (9 rows), each name at all three formats. Labelled
  compliance breadth, not earned.

Entry gate for 1a/1b: the ruling pins are written before code -
SF-0 NaN-matrix reuse, first-operand tie pins, signed-zero
ordering, signaling-NaN invalid behaviour, and (for 9.7) the
admissible payload sets, set-NaN sign, and payload operand
encoding. Payload rulings approved in Section 14 follow the
Clause 9 survey (maximal admissible sets: quiet `0..max`,
signaling `1..max`; set-NaN sign positive; `-0`
admissible-as-0 for the quiet form). The operand encoding
(same-format floating pattern vs integer payload) is frozen in
the table and the Step 1b design entry before any 1b code -
verifier suggestion S6, carried as an entry gate rather than
decided here. Character payload suffixes stay out; the Wave 3
string grammar is not reopened.

Exit gate: exhaustive binary16 per the Clause 9 survey, directed
binary32/64 families, controls watched failing (Number-form
substitution in the containment path; payload admissibility
mutants), `standard` green, and COVERAGE rows carrying
`claim=C-754` - none `unconfirmed` at wave close.

The interval workload **bans Number forms from the containment
path** regardless of 1b (interval survey E4: a suppressing form
silently discards a NaN axis). The axis-parallel slab branch
remains workload logic; 9.6 does not fix the face case and SF-1
must not pretend it does.

### 5.2 Interval workload gates (Step 1c)

Workload code only (scratch then `board/`-class placement as
briefed); it adds no library semantics. Proposed gates, in the
interval survey's G1-G7 shape:

- Containment audit vs an exact-rational oracle: zero violations
  over the frozen adversarial catalogue plus seeded randoms,
  counts printed by family; forced-underflow stage-3 cases must
  yield UNCERTAIN, never a wrong sign.
- Naive-vs-exact disagreement catalogue with construction
  provenance; a contracting host build is a named control that
  must be seen to disagree more.
- Mutants refused, watched failing first: RD/RU swapped on one
  endpoint; RN substituted for directed; min/max policy flipped;
  exact-stage flag guard removed.
- Refinement monotonicity: UNCERTAIN count non-increasing under
  tolerance halving and stage advance; decided rays never flip.
- Per-ray op cap enforced (cap-hit returns UNCERTAIN), with
  ops/depth histograms printed.
- Board sample: hashed ray sample identical host vs RP2040
  (artifact hash, commit, board ID, placement, clock named),
  plus the first measured per-op bench table for the used ops.
  Decide the endpoint-select bit convention (1a vs
  compare-select differ on `-0`/`+0` endpoint bits) **before**
  any hash is frozen.

Board ambition adopted: sampled-ray hash proof plus hosted
frames. A full frame computed on the Pico is a minutes-long
time-lapse beat, optional and separately briefed (interval
survey Section 8).

## 6. Step 2: KissFFT and the trig fork

### 6.1 Step 2a - pinned consumer demo (optional, Tier 1 only)

If run, this is honestly labelled: twiddles pinned offline
against MPFR (IAS15 coefficient pattern), injected by
workload-local glue, execution through Tier 1. It proves a
second host-vs-board bit-identity exhibit and de-risks KissFFT
integration (state sizing, RAM, CDC shape, negative controls).
It earns no core row and must never be cited as the reason a
trig pair exists. If clean injection is not possible without
core changes, skip 2a; do not bend the library for it.

Double configuration first (reuses the silicon-proven binary64
AEABI surface); float configuration is a stretch needing three
trivial `__aeabi_fadd/fsub/fmul` wrappers and its own selftest
surface (KissFFT survey Sections 9-10).

### 6.2 Step 2b - the pricing spike (mandatory before 2c)

A scratch-only design note, lead-reviewed, that prices **both**
forks **at all three formats** against evidence before any
kernel brief is cut (parity makes a binary64-only price
meaningless):

- quoted worst-case gap and source per candidate function per
  format - binary64 first, since it dominates (Clause 9 survey
  deliberately did not transcribe per-function bit counts; the
  spike must);
- intermediate precision + error-bound argument shape, or a Ziv
  escalation strategy with a termination bound, per format;
- oracle legs per format: binary16 exhaustive against MPFR
  (complete evidence, and the kernel de-risking step);
  binary32 exhaustive only against a fast foreign decider if
  fetched, else directed + worst-case + seeded MPFR volume;
  binary64 directed + worst-case + seeded MPFR volume; specials
  from Clause 9.2.1 second-read, and the truncated-precision
  negative control (a kernel built with reduced wide precision
  must fail) in every format;
- constant derivation: pi-class constants as integer limb
  tables generated by the MPFR/exact side and regenerated
  byte-identically - never copied tables, never decimal
  literals re-converted per build;
- RP2040 flash/stack budget per function per format.

If the spike cannot price a closing argument for either fork
**as a three-format bundle** inside the remaining schedule, 2c
is deferred and the record says so - shipping binary16 alone
because it closed first is exactly what the parity rule
forbids. A domain-restricted twiddle helper under a
non-conforming workload-local name remains possible, but it is
not a Tier 2 claim and not named `msf64_sin`.

### 6.3 Fork A - unmodified KissFFT, `sin`/`cos`

Keep KissFFT source unmodified. Implement correctly rounded
`sin` and `cos` as a three-format bundle (6 core rows), full
Clause 9.2 domain, all claimed rounding attributes; only the
binary64 rows are workload-earned, the binary16/32 rows are
parity-mandated. The hard part at binary64 is huge-argument
reduction (Payne-Hanek class), not the polynomial; the workload
only ever passes `|phase| < 2pi`, but a conforming name claims
the whole domain at every format (Clause 9 survey 9.1
cross-check). Binary16/32 reduction is bounded by their smaller
exponent ranges, which is why the bundle can be developed
f16 -> f32 -> f64 - but it still merges whole or not at all.

Public claim under Fork A: host-vs-board FFT bit identity with
twiddles correctly rounded **of the computed binary64 phases**.
Never "correctly rounded twiddles" without naming the argument,
and never a tolerance comparison vs numpy/FFTW called
byte-identical (KissFFT survey Section 8.2).

### 6.4 Fork B - exact-angle twiddles, `sinPi`/`cosPi` (adopted)

Make one named change to KissFFT's twiddle generation: cycle
fractions `-2i/N` (exact for `N=2^k`, correctly rounded
division otherwise) into correctly rounded binary64
`sinPi`/`cosPi`, instead of radian phases into `sin`/`cos`.
The library bundle is the pair at all three formats (6 core
rows; binary16/32 parity-mandated). Period reduction for the Pi
forms is exact at any magnitude in every format, which removes
Fork A's dominant reduction risk; the remaining burden is the
bounded-range kernel plus its worst-case argument per format -
still K3-class, still gated by 2b.

Public claim under Fork B, at the gated `N=2^k` sizes: board
twiddles are the correctly rounded values of the **exact
mathematical twiddles**, generated at runtime; FFT outputs
bit-identical host vs board under the same patched source. For
non-power-of-two N the cycle-fraction argument is itself a
correctly rounded binary64 division, so any public sentence
covering those sizes must restate the claim before use
(verifier suggestion S2). The patch is named wherever the
claim is made; "unmodified KissFFT" is not claimed.

Fork B was adopted at approval (Section 14): it is the stronger
scientific statement (true-angle twiddles) at equal-or-lower
risk, and the one-site patch is small, visible, and itself a
demo beat. Fork A remains the fallback 2b prices only if Fork B
cannot close as a three-format bundle.

### 6.5 KissFFT gates (either fork)

- Pin gate: KissFFT 131.2.0 archive/tag/SHA-256/licence hashes
  in `docs/metrics/fetches.jsonl` shape; workload tree only in
  scratch/`board/`, never `src/` or `include/`.
- Trig gate (per function, per format): claim level declared in
  the brief; specials per Clause 9.2.1; Section 6.2's oracle
  legs in every claimed mode (binary16 exhaustive; binary32 per
  the fetched-or-not fast decider; binary64 hardest + seeded
  MPFR volume). The pair merges only when all six rows close;
  trap symbols (`sin`, `cos`, `floor` in the AEABI census) are
  retired only at that bundle closure, and only for the
  binary64 spellings KissFFT actually links.
- Wrapper gate: AEABI selftest extended to the adopted symbols
  with bit+flag comparison against the core; per-core/IRQ state
  contract inherited from SF-0 Section 3.4. Parity rows
  (binary16/32 trig) need core gates and sampled board replay
  like any core row, but no compat wrapper is invented for them
  without a caller.
- Workload gate: fenced host reference (twiddle provenance
  printed) vs board, field-hashed outputs at
  `N in {256, 1024, 4096}` x {complex, real} x adopted configs;
  negative controls permanent in the runner: 1-ulp twiddle
  flip, host-libm twiddle substitution at adversarial scaling,
  bootrom/libgcc substitution on subnormal-crossing inputs,
  `-ffp-contract=fast` host build, analytic anchors (delta,
  bin-centred tone, exact N=4/8 DFT), aliased in-place path.
- Claim gate: every public sentence names which claim it is
  (bit identity / CR-of-phase / CR-of-true-angle / tolerance
  sanity check). No tolerance result is called byte-identical.

## 7. Everything deferred, by name

Mapped by the Clause 9 survey, **not authorised** by SF-1.
Naming them here is the defence against the 180-row menu
reading as a plan. Every core row count below is already the
three-format bundle count under the parity rule; the wrapper
and attribute items are global/state surface by nature, not
per-format rows, and parity does not multiply them.

| Family | Rows (homogeneous, all formats) | SF-1 disposition |
|---|---|---|
| Dynamic rounding wrappers (9.3-shaped get/set/save/restore/default) | 5 wrapper ops, C-API | Deferred. Neither workload earns them; the core's explicit rounding argument dominates for intervals, and KissFFT never reads a mode. If later authorised: compat-only over per-core state, unit-gated, invalid enum = ignore-write (survey recommendation, **provisional** until that family is authorised and the owner confirms - verifier suggestion S5) |
| Ties-to-away as fifth public attribute | 0 new rows; mode sweep over 249 Tier 1 attr rows + Tier 2 attr rows | Deferred. Largest pure-evidence bill in Tier 2; placed after the first math function in the survey sequence, which SF-1 does not reach unless 2c closes |
| `roundToOdd` | internal pack mode only | Deferred as scaffolding; may land inside a math parcel that needs it, never as public 754 surface |
| Augmented add/sub/mul (9.5) | 9 | Deferred. Performance-only for intervals; uncalled by KissFFT. Needs the pair shape + Clause 9.5 flag table second-read when earned |
| Reductions (9.4), sum family | 12 | Deferred; placement disputed between surveys (core exact-round-once vs nowhere-in-library). SF-1 does not need to pick: neither workload may rest a proof on 9.4 as standardised. Scaled family (+9) only on workload evidence, ever |
| Other Clause 9.2 math functions (37 names) | 111 (of 117) | Deferred. Survey ranking stands for a future study: `rSqrt` first (algebraic, exactly decidable), then `hypot`, `pown`/`compound`, `rootn`, `exp2`/`log2` families, Pi trig, hyperbolics; `pow`/`powr` refused in any first sequence. `rSqrt` is the named fallback if the owner wants a math function with no workload - it is not in SF-1's prefix. Step 2c takes the remaining 6 rows as one three-format pair bundle; any family from this deferred set, if ever authorised, likewise ships at all three formats or not at all |
| SDK flavour completion | 0 | Out of Tier 2 scope (architecture D10) unless a chosen workload needs SDK-internal FP behaviour changed; neither does |

Standing refusals carried verbatim from SF-0 Sections 2.7/11:
binary128 and decimal formats, Clause 8 alternate exception
handling, traps/resumption, non-IEEE fast-math/flush-to-zero,
dynamic allocation or hardware FP in the core, bootrom FP entry
points, copied third-party softfloat/math source, claims ahead
of closed gates, any "mostly compliant" label. Foreign math
libraries are executed oracles in scratch at most; their
source, constants, and polynomials are never design input.

## 8. Authorities, gates, and claim discipline

SF-0 Section 4's order survives unchanged: the standard for
meaning (by clause, via S1 extracts), Berkeley for what it
covers (Tier 1 + pack rounding-mode behaviour; it is silent on
Clause 9 operations), MPFR/exact for values Berkeley cannot
decide, fenced host checks never deciding Tier 2. Disagreement
routes to the standard, then MPFR/exact - never averaged, never
outvoted by vector count. The Wave 1 tininess episode (lead
kernel and lead reference agreeing wrongly, caught by parcel
escalation against Berkeley) is restated in every Tier 2 brief.

Claim tokens (closed set, frozen by the seam):

| Token | Meaning | SF-1 use |
|---|---|---|
| `C-754` | 754-conforming recommended-operation semantics; exact bit+flag comparison; named authority | Steps 1a/1b; Step 2c trig only with the full evidence ladder |
| `C-754-EXC` | Exact-round-once semantics exceeding the clause's loose results, stated in the claim text | Reserved (reductions, if ever) |
| `C-ULP` | Bounded-ULP approximation, machine-checked bound | **Not admitted in SF-1's window** (architecture D9: needs its own gated runner mode) |
| `C-API` | Project API contract, not a 754 claim | Reserved (dynamic wrappers, if ever). "API-compatible only" names get no COVERAGE rows |

Headline counting: Tier 1 (783) and Tier 2 counts are never
summed into one conformance number. README/RECORD language
counts per tier and per claim token.

Foreign-oracle option (owner Q, Section 10): CORE-MATH-class
executables + worst-case (`.wc`) data, pinned into
`scratch/oracles/` with a fetches row, execution/metadata only,
smoked against MPFR before any differential is trusted, never
deciding specials/flags/NaNs. Without it, binary32-exhaustive
differentials are forgone and binary64 leg (a) worst-case
evidence must come from quoted literature gaps + MPFR volume -
the 2b spike prices both routes.

Per-function, per-format evidence ladder for any `C-754` math
row (Clause 9 survey 4.6.4): (a) published hardest-to-round
cases pass; (b) directed + seeded-random MPFR differentials at
volume, all claimed modes, specials exact-compared (binary16:
exhaustive, which is complete evidence for that format);
(c) the argument - intermediate precision + proven error bound
exceeds the known worst-case gap, or a Ziv loop certifies
undecided cases with a termination bound. Under the parity
rule the ladder is climbed for all three formats inside one
parcel: if (c) cannot close at any format, the **bundle**
returns refused and no format's rows merge - partial evidence
is recorded in the ledger, never landed as a single-format
claim. Directed modes are gated, not inherited from a
nearest-mode story.

Math TU placement: new per-family translation unit(s) for 9.2
kernels (Tier 1 files stay byte-stable), each TU carrying its
family's three formats together so a parity bundle is one
reviewable diff; 9.6/9.7 follow the per-format pattern over
existing decode/compare kernels (architecture D6). Constants
are generated integer tables with regeneration drift refusal,
like vectors.

## 9. Board evidence and public wording

- On-silicon bit identity is this project's differentiator:
  no Tier 2 row is host-only by default (architecture D8).
  Exceptions must be named in the parcel brief and in RECORD,
  in the Wave 3 string-rows style. Pair/vector shapes extend
  the CDC harness only when an authorised step needs them;
  whole-surface board language ("783 of 783") must not silently
  extend to shapes the harness cannot run.
- Board claims name commit, artifact hash, board unique ID,
  placement, and clock, as Tier 1 does. Per-function flash
  accounting from the linker map extends SF-0 Section 8.
- The deferred six-board IAS15 range (power-only cables) is
  independent hardware backlog: when the remaining three
  clones enumerate, run them with the existing multi-board
  script and optionally a full 2,000-step parallel sweep on
  all six; record per-board hashes/rates. It gates nothing in
  SF-1 and SF-1 gates nothing in it.
- Video/README may claim only closed steps. In particular:
  interval results are containment claims (HIT/MISS/UNCERTAIN),
  not accuracy claims; KissFFT claims follow Section 6.5's
  claim gate word for word.

## 10. Questions for Logan, with recommendations

These questions are kept as put. Logan answered them on
2026-10-27 with "go ahead with recommendations"; the settled
decisions are recorded in Section 14.

- **Q1. Prefix authorisation:** Steps 0-1c now, 2a optional in
  parallel, 2b as the gate to any trig (recommended) - or a
  different cut (1a only / no Tier 2 / trig-first)?
- **Q2. Earning bar for 9.6:** accept `minimum`/`maximum` as
  earned in the semantics-owning sense, and land the full 33
  (9.6+9.7) with the unearned 27 openly labelled compliance
  breadth (recommended) - or hold the strict-capability line
  and land only the 6 the workload names?
- **Q3. Payload rulings:** maximal admissible sets (quiet
  `0..max`, signaling `1..max`), set-NaN sign positive, `-0`
  admissible-as-0 for the quiet form; character suffixes out;
  homogeneous-only throughout Tier 2 (all recommended)?
  Format parity is not part of this question - it is your
  standing direction of 2026-10-27, already applied: every
  family below ships at binary16/32/64 or not at all.
- **Q4. Interval shape:** f32 intervals with f64 staged
  refinement (recommended over f64-throughout; makes UNCERTAIN
  bands visible and board costs sane); sampled-ray board hash +
  hosted frames (recommended over a full on-Pico frame);
  trig-defined geometry out (recommended)?
- **Q5. KissFFT contract:** is on-device runtime twiddle
  generation for caller-chosen N part of the demo contract?
  Yes earns the trig pair; no makes KissFFT a pinned consumer
  demo only (Step 2a). This is the whole ballgame for 2c.
- **Q6. Trig fork (if Q5 is yes):** Fork B `sinPi`/`cosPi`
  exact-angle twiddles with the named one-site patch
  (recommended), or Fork A unmodified KissFFT with `sin`/`cos`
  of computed phases? (Sections 6.3-6.4.)
- **Q7. KissFFT config order:** double-first (recommended; zero
  new execution wrappers) with float as stretch, or
  float-first?
- **Q8. Foreign oracle:** pin CORE-MATH (MIT) into scratch
  oracles for execution + worst-case data under Section 8's
  fences (recommended; priced by 2b either way), or MPFR-only?
- **Q9. Claim discipline:** tier/claim columns + inventory
  split + exact-only claims in this window (no C-ULP) + per-tier
  headline counting (all recommended)? Including the verifier's
  S1 parity-scope reading: parity binds core rows, while compat
  spellings are added only where a workload links them.
- **Q10. Deferrals:** Section 7 as written - dynamic wrappers,
  fifth attribute, roundToOdd-public, augmented, reductions
  (placement deliberately undecided), other math, SDK flavour -
  all mapped-but-not-authorised until earned (recommended)?

## 11. Risks and stop rules

1. **Trig leg (c) is the schedule risk, now at three formats.**
   Steps 0-1c are small (33 K0/K1 rows - 4 semantics-owning +
   2 parity + 27 compliance breadth - vs Tier 1 parcels of
   ~173 rows). Step 2c is K3 and, under parity, a six-row
   bundle: binary16 closes by exhaustion and de-risks the
   kernel, but binary32 and especially binary64 still need
   their worst-case arguments; until 2b quotes the chosen
   pair's gaps per format, its cost is a ranking, not an
   estimate. Stop rule: if 2b cannot state a closing argument
   for the bundle, 2c defers past 2026-11-04 and the
   video/RECORD claim only closed steps - the easy formats do
   not ship alone. The submission does not need 2c.
2. **Single-reader semantics.** Clause 9.5/9.4 and 9.2.1
   specials in the surveys rest on S1 paraphrase. Every parcel
   entry gate re-reads its clause tables with a second reader;
   the tininess episode is the priced example of skipping this.
3. **Foreign-oracle bring-up.** CORE-MATH availability is
   documentation-parsed, not execution-verified, and its
   Windows-host build is unverified (Clause 9 survey Section 9).
   It is corroboration only; MPFR-only remains the floor and 2b
   prices the build before any reliance.
4. **Claim dilution.** The failure mode Tier 2 adds is a weaker
   row hiding beside exact rows. Defences are mechanical, not
   editorial: closed claim tokens, the tier-split inventory
   assertion, per-tier headlines, no COVERAGE rows for
   API-compatible-only
   names.
5. **Homogeneous scope.** If Q3's homogeneous reading is wrong
   for the owner's intent, every count in Sections 3-7 scales
   by the formatOf multipliers. Settle it at approval, not
   mid-parcel.
6. **Verifier cost.** Planted-copy verification caught 24/25
   across Waves 1-3 but costs a full Spark pass per parcel.
   Keep parcels at Section 3's sizes; never parallelise more
   than the lead can plant and grade serially.

## 12. Sources

Repository at `32dac7d`: `docs/studies/SF-0.md` (Sections 2.7,
3-5, 7-9, 11 load-bearing), `docs/RECORD.md`, `docs/KICKOFF.md`,
`docs/COVERAGE.tsv`, `docs/BOARD.md`, `AGENTS.md`,
`tables/{formats,operations,implemented}.tsv`,
`tools/gen_tables.py`, `tools/run.sh`.

Scratch surveys (read in full by the lead for this synthesis):
`scratch/tier2-kissfft/report.md` (479 lines; KissFFT 131.2.0
pin, call census, twiddle study, gates),
`scratch/tier2-interval/report.md` (379 lines; experiments
E1-E8, remove-it inventory, gates G1-G7),
`scratch/tier2-clause9/report.md` (1,874 lines; 180+5 surface
count through the real generator, per-function ranking,
evidence ladder, Q1-Q13),
`scratch/tier2-architecture/report.md` (702 lines; seam
blockers, claim accounting, D1-D10). Briefs:
`ledger/briefs/tier2-{kissfft,interval-geometry,clause9,
architecture}.md`; ledgers `ledger/study-tier2-*.md`,
`ledger/lead.md` (Tier 2 dispatches; multi-board deferral
2026-10-27 14:31).

External facts enter only through the surveys' own citations
(KissFFT pin/licence; CORE-MATH documentation metadata; MPFR
4.2.2 header inventory). IEEE 754-2019 is cited by clause
through S1/SF-0; the PDF was not opened for SF-1.

## 13. Send-backs

Round 0 (aborted): verification of the first 691-line draft was
stopped before any verdict when the owner's format-parity rule
landed (Section 1); no findings were consumed and that draft's
binary64-only Step 2c was withdrawn.

Round 1 (2026-10-27): the revised 771-line draft was verified
under `ledger/briefs/sf1-verify.md` by two independent
muse-spark-1.3 lenses (fidelity/arithmetic; adversarial
consistency against the four surveys, SF-0, and the code) plus
a synthesis pass. Verdict: **PASS** - no (a) regression and no
(b) wrong answer survived either lens; report at
`scratch/sf1-verify/report.md`, verifier ledger at
`ledger/verifier-sf1.md`. This was a document verification, not
a planted-copy code verification, so no plant score attaches.

Six non-blocking suggestions were recorded for the approval
edit / owner, none a send-back: S1 confirm the parity-scope
reading (core rows bound; compat spellings only where a
workload links them); S2 qualify Fork B's public sentence to
the gated `N=2^k` sizes; S3 rename the control-9 successor in
the seam; S4 carry the earned/parity/breadth split in Section
11's count; S5 mark the deferred invalid-enum ruling
provisional; S6 pin the payload operand encoding before Step
1b code. At approval: S1 confirmed as recommended (Section
10 Q9), S2-S5 applied in this text, S6 carried as the Step 1b
entry gate in Section 5.1.

## 14. Approval and decisions

Approved by Logan on 2026-10-27 ("go ahead with
recommendations"), settling Section 10 as recommended:

- **Q1:** Steps 0-1c authorised now; Step 2a optional in
  parallel as workload code; Step 2b is the mandatory gate to
  any trig implementation.
- **Q2:** `minimum`/`maximum` accepted as earned in the
  semantics-owning sense; the full 33 rows land, with the
  unearned 27 openly labelled compliance breadth (and the
  binary16 minimum/maximum rows labelled parity).
- **Q3:** Payload rulings as written; character suffixes out;
  homogeneous-only; format parity at binary16/32/64 throughout.
- **Q4:** Interval workload is f32 intervals with f64 staged
  refinement; sampled-ray board hash plus hosted frames;
  trig-defined geometry out.
- **Q5:** Runtime twiddle generation for caller-chosen N **is**
  the KissFFT demo contract, so the trig pair is earned at
  binary64 (binary16/32 by parity).
- **Q6:** **Fork B** (`sinPi`/`cosPi`, named one-site patch,
  public claim qualified to gated `N=2^k` sizes per S2).
- **Q7:** KissFFT double configuration first; float is stretch.
- **Q8:** CORE-MATH may be pinned into scratch oracles under
  Section 8's fences (execution/metadata only), priced by 2b.
- **Q9:** Tier/claim columns, inventory split, exact-only
  claims (no C-ULP), per-tier headlines; S1 parity-scope
  reading confirmed (core rows bound; compat spellings only
  where a workload links them).
- **Q10:** Section 7 deferrals stand as written.

Authorisation boundary: Step 2c implementation is **not**
authorised until Step 2b closes with a priced three-format
bundle argument for Fork B (or returns Fork A as fallback for
fresh owner decision). No deferred family in Section 7 is
authorised by this approval.
