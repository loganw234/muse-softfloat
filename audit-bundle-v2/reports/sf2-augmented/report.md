GO/NO-GO - 9.5 augmented (9 rows): CONDITIONAL GO (design + price closed below; authorise only bundled with a named exact-stage workload). 9.4 reductions (21 rows): NO-GO (nowhere in the library). 9.3 dynamic rounding wrappers (5 ops): NO-GO for the SF-2 prefix (SF-1 provisional design CONFIRMED; keep deferred).

# SF-2 input study: Clause 9.5 augmented arithmetic, 9.4 reductions, 9.3 dynamic wrappers

Study `study-sf2-augmented`, scratch only, no repo changes. Pair
semantics are derived from the clause text alone (S1 extracts
cited by clause number; no third-party implementation source used
as design input). Measurements were executed this study (script
files in `scratch/sf2-augmented/`, Git Bash, `MSF_PYTHON` pinned
to the workspace `.venv`, `TMP` inside this scratch). Governing
inputs read in full: brief `ledger/briefs/sf2-augmented.md`;
S1 extracts for Clauses 4.2/4.3, 5.4.1, 6.1-6.3, 7.1-7.6, 8.2,
9.1, 9.3, 9.4, 9.5; SF-1 (Sec.0, 2.2, 7, 8, 10/14); Clause 9
survey Sec.4.3-4.5 + 6/7; architecture survey placement table +
D5; interval survey E5; `src/msf_roundpack.c`, `src/msf_internal.h`,
`src/msf_decode.h`, `src/msf64.c` add/mul kernels,
`src/msf_performat.inc`, `docs/WIDTHS.md`, header prelude +
`tools/gen_tables.py` sig machinery, `compat/msf_wrap.{c,h}`,
`compat/msf_aeabi.{c,h}`, `board/interval_workload.{c,h}`,
`board/interval_host.c`, `scratch/parcel-w4interval/report.md`.

## 0. Recommendation order, price, stop conditions

Prices are in the project's own unit (brief time boxes,
`docs/metrics/briefs.jsonl`: 173-instantiation core parcel =
300 min, 33-row min/max parcel = 300 min, interval host proof
1,419 hand lines = 360 min, lead seam = 180 min / 900 lines).
Hours below are box-hours of implementation work, verifier time
excluded unless stated.

| Order | Family | Verdict | Box | Entry condition |
|---|---|---|---|---|
| 1 (when earned) | 9.5 augmented add/sub/mul, 9 rows, `C-754` | CONDITIONAL GO | 7-10 h (one 480 min parcel + 2 h second-read/verifier) | A named SF-2 workload whose hot path is exact-expansion / compensated arithmetic, or a stated board-replay cost case (Sec.2). Flag pin P1 settled first. |
| 2 (when earned) | 9.3-shaped dynamic wrappers, 5 compat ops, `C-API` | NO-GO now; design confirmed | 3 h (+1 h verifier) | A firmware consumer that must switch rounding at runtime through a stable API (Sec.4.3). |
| 3 | 9.4 reductions, 21 rows | NO-GO (nowhere) | not priced for SF-2; conditional sum-family price in Sec.3.4 | Fresh study only if a workload's own source calls a vector API and rests a proof on exact round-once (Sec.3.3). Scaled family: refused without a named consumer, ever. |

Stop conditions:

- Augmented: if pin P1 (the exact-tiny-residual underflow flag
  reading, Sec.1.3) cannot be second-read to one reading, the
  parcel does not start - it returns to the owner as a decision,
  not a guess in code. If the pair seam (sig + runner + board
  reply) exceeds 3 h on its own, stop and re-price before kernel
  work. All three formats or none (parity rule).
- Wrappers: if the host test seam would require changing the
  shipped Pico contract in `compat/msf_wrap.c`, stop; the design
  in Sec.4.2 avoids it by construction.
- Reductions: no entry condition is met by any current or SF-1
  workload; do not spend the seam (vector sig, `C-754-EXC`
  admission) speculatively.

What changed versus the prior surveys: (a) the augmented kernel
does **not** need the ~2,100-bit accumulator the Clause 9 survey
priced - a 128-bit exact window plus a verbatim far-operand
branch is exact (Sec.1.5); (b) the survey's "tiny exact residual
signals underflow (flag)" paraphrase does not survive a second
read against Clauses 7.1/7.5 - the flag question is genuinely
open and is pinned as P1 with a recommendation (Sec.1.3);
(c) reductions: the architecture survey's "nowhere" wins over
the Clause 9 survey's core exact-round-once, for fresh reasons
(Sec.3), including that augmented itself removes the best
argument for a core exact dot.

## 1. Clause 9.5 augmented arithmetic (9 rows)

### 1.1 Result-pair definition

Three homogeneous binary-only operations
(`augmentedAddition/Subtraction/Multiplication`, Clause 9.5):
two same-format operands in, an ordered pair `(head, tail)` of
same-format results out, for binary16/32/64 = **9 rows**. No
formatOf reading (the clause spells `(sourceFormat,
sourceFormat)`; a mixed-format pair would need conversion
semantics the clause never states).

The clause fixes its own rounding direction,
`roundTiesTowardZero` (here RTTZ): the nearest float to the
infinitely precise result, the smaller-magnitude neighbour on
an exact tie. Overflow behaviour is part of the definition:
magnitude **greater than** `b^emax*(b - (1/2)*b^(1-p))` rounds
to signed infinity; magnitude **equal to** that threshold
rounds down to the largest finite `b^emax*(b - b^(1-p))`. RTTZ
differs from ties-to-even exactly on ties, including the
overflow-threshold tie, where ties-to-even delivers infinity
and RTTZ delivers max-finite with a half-ulp tail (directed
case measured in Sec.5: `maxfin + 2^970 -> (maxfin, 2^970)`,
no flags).

Pair definition, finite operands, exact value `s = x op y`:

- `head = RTTZ(s)` where `op` is `+`, `-`, `x`.
- If `head` is infinite: `tail = head` (the pair deliberately
  does **not** sum to `s`; Sec.1.3 flag row).
- If `head` is finite: `tail` is the residual `s - head`,
  delivered **exactly** whenever it is representable - for
  add/sub always (Sec.1.4), for mul except one characterised
  cell, where `tail = RTTZ(s - head)` instead.
- A zero tail takes the head's sign. A nonzero tail's sign is
  the sign of `s - head` (with the head, against it when the
  head rounded up in magnitude).
- Specials: any NaN input delivers the propagated NaN as
  **both** results (same bits twice); an invalid operation
  delivers the same quiet NaN twice; an exact infinite result
  (infinite operand) delivers that infinity twice.

### 1.2 Which attributes apply

None that the caller controls. Clause 9.5 specifies "a single
rounding direction to be used in the operations in this
subclause" - the applicable rounding-direction attribute
(Clause 4.3, all five values) is **forbidden** from influencing
either result. Consequences for the API: no `msf_rounding_t`
parameter (Sec.1.6). Other attributes: preferred exponents and
cohorts are decimal notions and do not arise (binary only);
Clause 8 alternate handling, including the flush-underflow
wording for augmented pairs in 8.2, is under this project's
standing Clause 8 refusal (SF-1 Sec.7) and is **not** part of
the design - the flag table below is default handling only.

### 1.3 Flag table (second read)

Exceptional behaviour is "the same as addition/subtraction/
multiplication (5.4.1) using roundTiesTowardZero", plus the
9.5-specific sentences. The table distinguishes **signaled**
(from the clause text) from **flag raised** (what this library
observes in `*flags` under default handling). The distinction
is the whole P1 dispute (below).

Common rows (all three ops):

| Case | head | tail | Flags raised |
|---|---|---|---|
| signaling NaN input | propagated qNaN bits `Q` | `Q` | invalid |
| quiet NaN input only | propagated qNaN `Q` | `Q` | none |
| invalid, no NaN input: add `(+inf)+(-inf)`; sub `inf-inf` like signs; mul `0 x inf` | default qNaN | same | invalid |
| exact infinity from infinite operand(s) | `+-inf` (6.1/6.3 signs) | same inf | none |
| finite operands, `RTTZ(s)` overflows | signed inf | same inf | overflow + inexact |
| divisionByZero | - | - | never signaled (add/sub/mul) |

NaN bit choice `Q` is not free in this library: the shipped
SF-0 2.5 matrix via `msf_nan_delivery` (first signaling operand
quieted, else first quiet NaN, else default qNaN) decides it,
and 9.5's "propagates a NaN as both results (6.2.3)" is
satisfied by delivering those bits twice.

Finite rows, augmentedAddition/Subtraction (`r = s - head`):

| Case | head | tail | Signaled | Flags raised |
|---|---|---|---|---|
| `r = 0` (incl. exact subnormal/zero head) | `s` exact | zero, head's sign | underflow if head tiny nonzero (7.5) | none |
| `r != 0`, `|r| >= b^emin` | `RTTZ(s)` | `r` exact | none | none |
| `r != 0`, `0 < |r| < b^emin` | `RTTZ(s)` | `r` exact (subnormal) | underflow (9.5) | **P1: none (R2, recommended) or underflow (R1)** |
| inexact | - | - | only on overflow (9.5 explicit) | as overflow row |

Finite rows, augmentedMultiplication:

| Case | head | tail | Signaled | Flags raised |
|---|---|---|---|---|
| `r = 0` | `s` exact | zero, head's sign | underflow if head tiny nonzero | none |
| `r != 0`, representable, `|r| >= b^emin` | `RTTZ(s)` | `r` exact | none | none |
| `r != 0`, representable, `0 < |r| < b^emin` | `RTTZ(s)` | `r` exact | underflow (9.5) | **P1 as above** |
| `r != 0`, **not** representable (nonzero digits below `b^(emin-p+1)`) | `RTTZ(s)` | `RTTZ(r)` (may be signed zero / subnormal / min normal) | underflow + inexact | **underflow + inexact** (9.5 explicit: "raises the underflow flag and signals the inexact exception in this case") |
| inexact otherwise | - | - | only on overflow (9.5 explicit) | as overflow row |

Three subtleties the second read must ratify with the table:

1. **Head tininess never raises anything by itself.** For
   add/sub a subnormal or zero head is always exact (`r = 0`,
   proof Sec.1.4) - 9.5 says so ("the operation's subnormal
   and zero results are exact"). For mul, a tiny head with
   `r != 0` forces `r` onto a finer-than-subnormal grid, i.e.
   into the not-representable row. So there is no separate
   "head underflow + inexact" cell, and the shipped pack's
   after-rounding tininess judgment (SF-0 2.5) must not leak
   into augmented flags: flags are computed from the table
   (exact-residual tests), never inherited from a head pack.
   Note the 9.5 underflow test is on the **exact residual**
   before any rounding of it (`r` "lies strictly between
   `+-b^emin`") - e.g. `r = b^emin - b^(emin-p-1)` in the mul
   inexact-tail row raises underflow even though `RTTZ(r)`
   reaches `b^emin`. Do not reuse pack tininess for it.
2. **Inexact belongs to neither head nor tail rounding.** The
   pair is the result: it is exact in every finite row except
   mul's not-representable cell, so inexact tracks pair
   exactness, not the head's rounding error. A consumer that
   reads "inexact == rounding happened" from Tier 1 habits
   will misread these rows; the header comment must say so.
3. **P1 - does an exact tiny residual raise the underflow
   flag?** 9.5: residual nonzero strictly between `+-b^emin`
   => "the underflow exception shall be signaled". 7.5 default
   handling: if the rounded result is exact, "no flag is
   raised and no inexact exception is signaled... the only
   case in this standard of an exception signal receiving
   default handling that does not raise the corresponding
   flag"; 7.1 repeats that flags are withheld only for exact
   underflow. **R1** (Clause 9 survey paraphrase): 9.5 creates
   a flag-raising inversion of the exact-tiny silence.
   **R2** (recommended here): "signaled" in 9.5 invokes the
   ordinary 7.5 rule, whose exactness attaches to the tiny
   delivered result (the tail, exact in this row), so no flag
   is raised and nothing is observable under default handling;
   the signal is observable only under Clause 8 handling the
   project refuses. Textual support for R2: the mul paragraph
   bothers to state that default handling **raises the
   underflow flag** precisely and only in the inexact-tail
   case - a pointless clarification if the exact case also
   raised it. Risk if R2 is wrong: a flags-based consumer
   (interval stage 3's guard, Sec.2) cannot see tiny exact
   residuals - but it does not need to, because the pair is
   still exact. Risk if R1 is wrong: workloads refuse
   (UNCERTAIN) on benign exact cases. Either way the bits of
   head/tail are unaffected. **Pin P1 = R2 recommended; owner
   + second reader must ratify before the parcel starts**, and
   the chosen reading gets a mutant control in the gate.
   Measured this study: the shipped interval catalogue never
   discriminates R1 from R2 (zero exact tiny residuals in
   stage 3, Sec.2), so workload evidence cannot settle it.

Zero-sign cells (head): exact-zero sum/difference follows 6.3
read with RTTZ in place of the attribute - `+0` for
opposite-sign cancellation (RTTZ is not roundTowardNegative),
the common sign for like-signed zeros (`x + x`, `x - (-x)`);
product zero sign is the XOR (6.3). A nonzero exact result
rounding to a zero head (mul only; add/sub results are
multiples of the subnormal step and cannot round to zero
unless zero) takes the exact result's sign. These cells are
in the directed probe (Sec.5) and belong on the pin list.

### 1.4 Exactness: is the residual always representable?

Claim (add/sub): when `RTTZ(s)` is finite, `r = s - RTTZ(s)`
is always exactly representable in the same format. Proof
sketch: every finite float is a multiple of the subnormal
step `u0 = b^(emin-p+1)`, so `s` and `r` are. If the head is
zero or subnormal its grid step is `u0` and a nearest multiple
of `u0` to `s` is `s` itself, so `r = 0`. Else let
`u = ulp(head)`; nearest rounding gives `|r| <= u/2`. Write
`s = A*u + r'` with `A` integral and `|r'| < u` (truncate at
the head grid): head is `A*u` or the adjacent grid point, so
`r` is `r'` or `r'` shifted by one `u`. The sub-grid part
`r'` is contributed only by operand bits below `u`; the
operand on the head's binade grid contributes nothing below
`u`, and the other operand contributes a value that is a
multiple of its own ulp with at most `p` significant bits.
Hence `r` has at most `p` significant bits; being also a
multiple of `u0`, it is representable whether normal or
subnormal (the huge-gap extremal case is `head = x`,
`r = y` verbatim). This is the representability fact the
error-free-transformation literature rests on, here for the
ties-toward-zero nearest rule; the parcel must restate it
rigorously in WIDTHS form (the sketch's one loose step is
the binade-crossing head, where the grid below the head is
`u/2` - the bound survives, but it must be written out).
Probe evidence (Sec.5): exhaustive at p=4, all-operands-x-pool
at p=6, sampled at p=11/24/53 - zero counterexamples.

Claim (mul): the exact product has at most `2p` significant
bits. Splitting it at the head's grid leaves a residual with
at most `p` significant bits, representable **unless** it has
nonzero bits below `u0`, which happens exactly when the
product's bit span reaches below the subnormal step (tiny
products). The clause's parenthetical names the same
characterisation, and mandates `RTTZ(r)` + underflow +
inexact there. So mul's answer to "is the residual always
representable?" is **no, near underflow only** - and that
single cell is the only finite inexact cell in the family.

### 1.5 Kernel design over the shipped machinery

Existing facts: `msf_pack_generic` (`src/msf_roundpack.c`)
consumes a 128-bit significand + sticky and implements
rounding in `round_inc` over internal modes 0-4 (4 =
ties-to-away); its interface discards the residual by design.
The shipped add kernel aligns into a 118-bit window with jam
shifts (`src/msf64.c:82-128` and siblings), so far-tail bits
survive only as sticky - sufficient for one rounded result,
insufficient for an exact residual. The mul kernel already
forms the exact `2p`-bit product in `msf_u128` (WIDTHS.md:
106 bits at binary64).

Design (generic over `MSF_FMT_PARAMS`, one new TU
`src/msf_augmented.c` reusing `msf_decode` /
`msf_nan_delivery`; Tier 1 per-format TUs untouched - a
deliberate dissent from architecture D6's per-format
placement, justified because augmented is homogeneous-only
and decode/pack/NaN-delivery are already format-generic):

- New internal pack mode for RTTZ. In `round_inc` it is
  `guard && (round_bit || stick)` (increment only strictly
  above half); in the overflow branch it joins the
  to-infinity modes. The threshold tie then falls out of the
  existing arithmetic (all-ones candidate, guard set, round
  and sticky clear => no increment => max finite). Coordinate
  the enum value with the internal round-to-odd value the
  surveys proposed; whichever lands second takes the next
  value (pin P5).
- Add/sub exact path - **no wide accumulator needed.** Decode
  both operands as `(sig, exp)` integers. Let `span` be the
  distance from the higher operand top bit to the lower
  operand's lowest possible bit (`span <= top_gap + p`). If
  `span <= 128`, align both significands **exactly** (plain
  shifts, no jam) into `msf_u128` at the lower exponent and
  form the exact signed sum. If `span > 128`, the smaller
  operand's top sits more than `128 - p >= p + 2` bits below
  the larger top (75/104/117 vs the needed 55/26/13 at the
  three formats), so its magnitude is below half an ulp of
  the larger operand: head is the larger operand verbatim,
  tail is the smaller operand verbatim (effective sign).
  Zero operands are the trivial sub-case. Head and tail are
  then split from the exact window integer: head by packing
  with the RTTZ mode and scratch flags, tail as the exact
  integer residual (`exact - head`) re-encoded exactly -
  or, equivalently and more second-reader-friendly, by the
  direct integer split at the head grid step (the probe
  reference's algorithm). Flags come only from Sec.1.3's
  table (overflow detected via the scratch pack; residual
  tininess tested on the exact residual).
- Mul exact path: exact product in `msf_u128` as today,
  head by the same pack, tail by extracting the product's
  low bits under the head grid (adjusting by one grid step
  when the head rounded up in magnitude). Representability
  of the tail is tested exactly; the not-representable cell
  packs the residual itself under RTTZ and raises
  underflow + inexact. The pack's own underflow logic is
  bypassed (scratch flags discarded) for the Sec.1.3 reason.
- Specials front-end mirrors `addsub_core`/`mul_core`:
  `msf_nan_delivery` decides NaN bits and the
  invalid-without-NaN cases; the decided bits are delivered
  to both outputs.

Width restatement the parcel owes WIDTHS.md: one row
("augmented add/sub: exact 128-bit window when span <= 128,
verbatim pair otherwise; augmented mul: 128-bit exact
product, tail split at head grid") with the span lemma.
Nothing needs the string TU's multi-kilobit accumulator, and
stack cost stays at a few `msf_u128` values - the Clause 9
survey's K2 stands, but for the new pack mode + exact split
+ flag table, not for a new wide type.

### 1.6 Header, table, runner, board shape

This library's core is explicit-argument, table-generated
(operations.tsv -> header + dispatch + COVERAGE, drift
refused). Two-output results fit **no** existing operation
kind: every current sig returns one scalar through the
runner's `uint64_t` trampoline (`tools/gen_tables.py:
wrapper_for`, REPLAYABLE set). A new sig class is required -
the first result-shape extension since the char families,
which are the precedent for special-cased shapes.

Proposed contract, to be frozen in the seam slice of the
parcel:

- Table: three families `augmented_add`, `augmented_sub`,
  `augmented_mul` (std names `augmentedAddition` etc.;
  short tokens follow the house `add/sub/mul` abbreviations),
  clause `9.5`, sig `aug_pair`, tier 2, claim `C-754`
  (admitted today: `CLAIM_BY_TIER` tier 2 = {`C-754`}),
  authority `project-exact`, flags `yes`, rounding: recommend
  a new documented token `fixed` (direction fixed by the
  clause) rather than overloading `named` (direction in the
  operation name) or `none` (not subject to rounding - false
  here). Mechanically the generator only tests `== "attr"`,
  so either works; `fixed` keeps COVERAGE truthful. (Pin P4.)
- Header: per-format pair structs in the generated prelude,
  struct return (cannot be half-consumed; flags pointer keeps
  its trailing position; no new aliasing questions):

```c
typedef struct msf64_pair { msf64_t head; msf64_t tail; } msf64_pair_t;
msf64_pair_t msf64_augmented_add(msf64_t a, msf64_t b, msf_flags_t *flags);
```

  (and 16/32 analogues). Board ABI note: `msf16_pair_t`
  (4 B) and `msf32_pair_t` (8 B) return in registers under
  the ARM soft-float ABI; `msf64_pair_t` (16 B) returns via
  a caller-allocated hidden pointer - still allocation-free
  (caller stack), but the parcel brief should state it so
  nobody prices it as two register returns. The out-pointer
  alternative (`head` returned, `tail` via `msf64_t *`
  beside `flags`) is rejected: it invites half-use and a
  second non-null contract to no benefit.
- Runner/vectors: a special-cased line family beside
  `internal.pack*`, not the generic trampoline:
  `msf64_augmented_add - <a> <b> -> <head> <tail> <flags> <prov>`
  (`-` is the existing no-attribute mode token). Generator
  emits a two-result trampoline shape for `aug_pair`;
  runner parses by sig; both results exact-compared (no new
  masking mode). One new provenance tag family for the
  generator (VECTORS.md budget rule), e.g.
  `exact-py-t2:augmented-directed`, `...:augmented-seeded`.
- Board: extend the CDC harness reply for pair ops
  (`R <head> <tail> <flags>` plus a two-result canonical
  hash line; `board/harness_main.c`, `board/host_replay.py`).
  Host-gating in the string-rows style is available but
  rejected here: augmented's only earning story is a board
  workload, and SF-1 Sec.9 makes host-only the named
  exception, not the default. Price includes the extension;
  if it balloons, the Sec.0 stop condition fires.
- Compat/AEABI: no spellings. No C or AEABI name maps to a
  pair result (parity binds core rows, not compat spellings,
  SF-1 Q9/S1). Workloads call the core API directly, as the
  interval workload does.

Evidence plan (entry gate: pins P1/P4/P5 + flag table
second-read + WIDTHS row drafted): project-exact integer
reference implementing Sec.1.3 literally (Sec.5's
`ref_aug.py` is a working prototype, to be rewritten in
house generator style and reviewed against the clause table
independently - the Wave 3 decimal pattern: exact reference
decides, no Berkeley exists for 9.5, MPFR has no augmented
primitive and is unnecessary since add/mul are exact in
integers). Directed families: RTTZ tie discriminators at
several binades incl. binade boundaries, overflow-threshold
tie and one step above, huge-gap verbatim pairs, exact-zero
sign cells, subnormal heads, tiny-exact-residual cells under
both P1 readings, mul below-step cells, infinity/NaN matrix
duplicated to both outputs. Binary16: all-first-operand x
pool standing; one-time exhaustive-pairs C evidence run
(2^32 per name) recorded like a board run, not budgeted.
Negative controls: ties-to-even head mutant (fails tie
family), tail-sign flip on exact zeros, swapped head/tail,
jam-window mutant (fails huge-gap family), P1-opposite flag
mutant, pack-tininess-leak mutant (fails tiny-head cells).

## 2. Interval remove-it test (executed)

Question: does the shipped catalogue's hot path honestly
benefit if augmented replaces the current multi-call
expansions? Method: the workload already counts every
library call (`iw_ctx_t.ops`). Baseline = shipped
`board/interval_workload.c` unmodified. Variant = scratch
copy with exactly two changes - Knuth `two_sum` (6 counted
calls, statically recounted from source) becomes one counted
augmentedAddition, FMA `two_product` (3 counted calls:
mul + negate + fma) becomes one counted
augmentedMultiplication, and the `O - C` site uses
augmentedSubtraction directly (saving its `negate` too).
The augmented pair is emulated exactly over the shipped
ties-to-even EFTs plus an RTTZ tie adjustment (emulation
calls uncounted; emulation fidelity cross-checked against
the independent exact reference in Sec.5). Three guard/flag
policies were run: R2 flags (P1 recommended), R1 flags with
the shipped guard, R1 flags with an adapted guard (refuse on
overflow/invalid/(underflow+inexact)). Counts only - no wall
or cycle claims anywhere in this section.

Baseline reproduction (independent re-run, current tree):
710 rows, host SHA-256
`ce81d66e...9aec` and 616,754 counted ops - byte-identical
to `scratch/parcel-w4interval/report.md`'s frozen values.
Stage shares (all stages evaluated for every sphere ray, as
the IW1 hash design requires): stage 1 (f32) 132,836;
stage 2 (f64) 118,464; **stage 3 exact 283,314 (45.9%)**;
box 466; torus 81,674.

Measured deltas (all three flag policies: identical op
counts, identical decisions - reasons below):

| Model | Baseline | With augmented | Delta |
|---|---|---|---|
| Catalogue total (replay-all) | 616,754 | 394,666 | -222,088 (-36.0%) |
| Stage 3 total | 283,314 | 61,226 | -222,088 (-78.4%, 4.6x fewer) |
| Stage 3 mean per sphere ray | 408.8 | 88.3 | -320.5 |
| Short-circuit deployment total* | 360,799 | 311,665 | -49,134 (-13.6%) |
| Stage 3 part of deployment* | 62,395 (139 rays) | 13,261 | -49,134 (-78.7%) |

\* Deployment model computed from the same runs: stage 2
runs only where stage 1 is UNCERTAIN, stage 3 only where
stage 2 is UNCERTAIN (139 of 693 sphere rays reach it).

Composition: 54,266 augmented calls replace 276,354 counted
EFT-internal calls - 97.5% of stage 3's op count is
TwoSum/TwoProduct plumbing. The 61,226 remaining stage-3
ops are those 54,266 pair calls plus 6,960 others
(`tpush_prod` component negations - kept counted, so as not
to inflate the benefit - and the `sign_of_terms` bound
arithmetic). The variant's IW1-shaped hash differs from
baseline only through `s3ops` fields; every stage-3 and
final **decision is identical** (0 diffs, 0 decided-wrong
against the catalogue's exact column, 4 guard rays still
UNCERTAIN, stages 1/2/box/torus rows bit-identical).

E5 recount (SF-1 Sec.2.2's "8 vs 21-36 calls", from the
interval survey): exact dot3 = 3 TwoProducts + VecSum over
6 terms (5 TwoSums). Survey counting (TwoProduct = mul+fma):
Knuth 6 + 30 = 36; Fast2Sum 6 + 15 = 21; augmented
3 + 5 = 8 - the quoted numbers reproduce exactly. In the
shipped workload's stricter counting (in-EFT `negate` is a
call) the Knuth route is 39, so the catalogue-measured 4.6x
sits consistently at the top of the survey's static range.

Why the three guard policies coincide on this catalogue -
measured event tallies over all 54,266 augmented calls:
**exact tiny residuals: 0** (the P1 cell never occurs -
catalogue geometry is ordinary-scale, residuals are normal);
mul inexact tails: 8; augmented overflows: 8; RTTZ-vs-
ties-to-even tie adjustments actually exercised: 47 (so the
variant is not vacuous - heads really do move, expansions
still sum exactly, decisions hold). Under R1 the shipped
guard would therefore not degrade stage 3 on *this*
catalogue; that is catalogue luck, not a theorem. A scene
family at subnormal scale would put exact tiny residuals on
the hot path: under R2 nothing changes; under R1 the guard
must use the adapted form (underflow alone from an augmented
op is exactness-preserving; underflow+inexact is the only
augmented refusal signal). Design the workload change to
the adapted guard regardless - it is correct under both
readings - and settle P1 for the flags' sake, not the
workload's.

Honest-benefit verdict. Augmented is a real, measured
**op-count** win with three hard boundaries:

1. **It touches only stage 3.** Stages 1/2, box, and torus
   spend 333,440 ops (54%) on directed endpoint arithmetic;
   augmented heads are nearest-toward-zero, not outward
   directed, so pairs cannot serve as interval endpoints
   (interval survey App. note) and nothing there changes.
2. **Stage 3 exists to be rare.** In short-circuit
   deployment it sees 139/693 already-adversarial catalogue
   rays (115/400 tangent-by-construction in survey terms,
   0/300 ordinary rays). The -36% catalogue figure is a
   replay-all-stages number (it prices host/board evidence
   runs, where every ray pays stage 3); the deployment
   figure is -13.6% of this catalogue and near zero on
   ordinary scenes.
3. **Ops are not cycles.** One augmented call internally
   costs roughly a decode + exact window/product + two
   packs; the six TwoSum calls it replaces each pay their
   own decode/pack round trips. Structurally the cycle win
   should be substantial (no per-micro-op pack/dispatch
   overhead) but smaller than 4.6x, and nothing on silicon
   was measured in this study - any speed sentence beyond
   op counts needs the board bench parcel-w4interval left
   unpriced (survey G6 second half).

Remove-it conclusion: removing augmented breaks nothing -
no expressible result is lost (E5), today's exact stage is
already correct. Adding it buys counted-call headroom on
exactly one cold-ish stage of one workload. That is
**performance-only, workload-conditional** value: it earns
its 9 rows when a workload puts exact expansions (robust
predicates, compensated dot/expansions) on its hot path, or
when full-catalogue board replay time is a stated cost. On
the current SF-1 workload set it does not earn them yet -
hence CONDITIONAL GO, not GO.

## 3. Clause 9.4 reductions (21 rows): NO-GO

### 3.1 The claim problem (what would C-754 even assert?)

Clause 9.4 defines 7 names over operand vectors - `sum`,
`dot`, `sumSquare`, `sumAbs` (vector -> same format) and
`scaledProd`, `scaledProdSum`, `scaledProdDiff` (vector(s)
-> `{pr, sf}` pair) - x3 formats = 21 rows with integral
choices fixed once. But the clause standardises almost no
numerics: each result is "an implementation-defined
approximation"; association order and intermediate width are
free; inexact is **unspecified** except that it accompanies
signaled overflow/inexact-underflow under default handling;
preferred exponents unspecified; behaviour for
non-integral/negative length language-defined.

So under a plain `C-754` token ("754-conforming
recommended-operation semantics; exact bit+flag comparison",
SF-1 Sec.8) there are **no bits and almost no flags to
assert**. The entire clause-conformance content that a gate
could bite on is exception/special discipline:

- any signaling-NaN element signals invalid; at most **one**
  exception per invocation (not per element); processing
  may stop after an invalid condition (sNaN, mixed-sign
  infinities in sums, `0 x inf` in products);
- sum/dot: any NaN element -> quiet NaN; same-sign
  infinities -> that infinity silently; mixed infinities or
  a `0 x inf` product -> invalid; final-result overflow /
  underflow signaled, with "no avoidable intermediate
  exception conditions";
- sumSquare/sumAbs: an infinite element yields `+inf` **in
  preference to** a NaN element elsewhere (clause order),
  else NaN -> quiet NaN;
- scaled family: NaN -> quiet NaN; `0 x inf` products and
  per-element inf-sum/difference invalids; zeros/infinities
  in the product deliver signed zero/infinity without
  invalid; regular-case `pr` itself must not over/underflow
  and divideByZero should not be signaled even via logB;
  unrepresentable `sf` -> invalid + quiet NaN(s);
- length zero: sums `+0`, scaled products `{1, +0}`, silent.

That is a *discipline-only* claim (architecture survey's
level (d)): gateable, but it certifies no numeric result a
consumer could rely on, and it would sit in COVERAGE beside
783+ exact rows under any shared headline discipline -
exactly the claim-dilution failure the architecture survey
warned about. The stronger token SF-1 reserves, `C-754-EXC`,
asserts **project** semantics exceeding the clause
(correctly rounded exact reduction, one final rounding
under the caller's attribute, flags from that rounding plus
the special table). That is honest and bit-gateable (MPFR
declares correctly rounded `mpfr_sum`/`mpfr_dot`; exact
rational references decide small-`n` and flag cells) - but
note what it concedes: the standard is no longer deciding
the values, the project is, under a token the generator
does not yet admit (`CLAIM_BY_TIER` tier 2 = {`C-754`} today,
so even the seam is unspent). Either way, "we implemented
Clause 9.4" can never mean what "we implemented Clause 9.5"
means. Any future authorisation must price the claim-token
seam and separate headline counting as part of the family -
and must never use bit-exact-conforming language for it
(SF-0 2.7 already prohibits that here).

### 3.2 The survey dispute, restated

Clause 9 survey (Sec.4.5): put the sum family (12 rows) in
the **core** under pinned exact-round-once semantics
(`C-754-EXC`): fixed wide superaccumulator spanning the
format's exponent range (~2,100 bits at binary64 for sums,
~4,300 for dot/sumSquare products) + log-in-`n` carry
headroom stated as an exactness formula in `n`, one final
pack under the caller's attribute; directed modes then give
true interval enclosures. Scaled family later only, under
stated wide-jammed semantics. Architecture survey (D5):
reductions **nowhere** in the library - no bit-exact claim
exists to gate, the array+length signature breaks dispatch,
vectors, and the board line at once; workload-local helpers
under workload claims if ever needed. SF-1 Sec.7 explicitly
did not pick.

### 3.3 Fresh verdict: nowhere (core exact-round-once loses)

The Clause 9 survey's design is technically sound. It still
loses, on grounds that are decidable now:

1. **No call path exists.** Compiler-emitted code on this
   target calls scalar AEABI helpers; no compilation route
   emits vector-reduction library calls (KissFFT's execution
   is scalar `+ - *`; IAS15 likewise). A consumer must be
   *source code written against this API* - and no SF-2
   candidate names one. Exact-round-once directed dot is
   genuinely the tightest interval primitive, but the
   interval workload already ships staged directed
   intervals + an exact stage and is not blocked on it.
2. **Augmented removes the fallback argument.** The best
   technical case for a core reduction was "exact dot is
   expensive to express". With augmented pairs, an exact
   dot at any length is expansion code over scalar
   pair calls (8 counted calls per dot3 vs 21-39 today,
   Sec.2) - workload-local, exact, and already the proven
   pattern in `interval_workload.c` stage 3. What remains
   unique to a core reduction is one-call convenience and
   superaccumulator constant factors, neither of which
   carries a conformance claim.
3. **The shape tax is the largest of any family, paid
   three times** (generator sig with pointer+length and a
   scale-factor pair for the scaled three; variable-length
   runner lines with a 4096-byte ceiling pushing large-`n`
   evidence into runtime suites; board bulk transfer or a
   host-only exception), **plus** a claim-token seam - all
   for rows whose standard-conformance content is Sec.3.1's
   discipline list.
4. **The `n`-bound is an honest-claim liability.** A fixed
   superaccumulator makes "correctly rounded" true only
   below a carry-headroom formula in `n` per format. That
   caveat must be stated in the claim text forever; it is
   precisely the kind of asterisk this project's exact rows
   do not carry.

Home: **nowhere in the library for SF-2**; exact reductions
are workload-local helpers over Tier 1 (today) or augmented
(if authorised), under the workload's own claim, as stage 3
already demonstrates. Re-entry condition (all parts): a
workload whose own source calls a vector reduction API;
whose correctness argument rests on exact round-once
directed enclosures or correctly rounded dot (not merely
speed); and at vector lengths where expansion code is
measurably the wrong shape. Then a fresh study may propose
the sum family (12 rows) under `C-754-EXC` with the
Sec.3.1 discipline table + project value semantics
second-read. The scaled family stays refused under any
condition short of a consumer naming scaled products: its
`{pr, sf}` split has no foreign oracle, its value semantics
would be wholly project-invented, and it pays vector **and**
pair shape taxes simultaneously.

### 3.4 Conditional price (only because the brief asks; not a recommendation)

Sum family only, `C-754-EXC`, if the Sec.3.3 re-entry
condition were met: claim-token seam 1-2 h; vector sig +
runner syntax 3-4 h; superaccumulator + kernels + special
table 4-5 h; exact references + MPFR sum/dot triangulation
+ discriminating families (cancel-back-into-range,
one-exception, infinity precedence) 3 h; board sampled
selftest digest (not vector replay) 1-2 h. Total **10-14 h**
(+ verifier). Scaled family: not priced - refused.

## 4. Dynamic rounding wrappers (9.3-shaped, 5 ops): NO-GO, design CONFIRMED

### 4.1 SF-1's provisional ruling, evaluated fresh

SF-1 Sec.7 (survey recommendation, marked **provisional**
pending owner confirmation): compat-only over per-core
state, unit-gated, invalid enum = ignore-write. **Confirmed
on all three points**, with sharper grounds than the survey
stated:

- *Compat-only.* Clause 9.3's five operations
  (get/setBinaryRoundingDirection, saveModes, restoreModes,
  defaultModes - the decimal pair permanently out) are
  conditional requirements on **language standards** that
  define dynamic-mode specification (Clause 4.2, itself a
  "should", debugging-motivated). A C library cannot provide
  a language's dynamic scoping, precedence of static vs
  dynamic specification, or asynchronous-event semantics -
  all explicitly language-defined in 4.2. The core's
  explicit-rounding-argument design is stronger where it
  matters (interval endpoints switch direction per call with
  no state hazard; header prelude: "Rounding is an explicit
  argument, never process state"). Anything here is
  therefore `C-API` at best, worded "Clause 9.3-shaped
  access to wrapper state", with **no COVERAGE rows** (SF-1
  Sec.8 reserves `C-API` for exactly this and bars such
  names from the coverage ledger).
- *Over the shipped per-core state.* The state already
  exists and is already load-bearing: `msf_wrap_state_t
  {rounding, flags}`, two RP2040 statics in
  `compat/msf_wrap.c`, zero-init = ties-to-even (enum 0) =
  Clause 4.3's default, read by every AEABI wrapper in
  `compat/msf_aeabi.c` on every call. Zero core change is
  not a slogan - it is literally accessors over
  `msf_wrap_state()`, inheriting SF-0 3.4's contract
  verbatim (thread and IRQ share a core's state; never
  across cores; never implicitly saved/restored).
- *Ignore-write is a safety property, not a preference.*
  Storing a raw caller value is actively dangerous in this
  codebase: wrapper bodies pass `s->rounding` as the core
  `rm`, and `msf_pack_generic`'s `round_inc` interprets
  internal value 4 as ties-to-away (an unclaimed fifth
  attribute leaking through compat) and any value >= 5 via
  its default arm as toward-zero (measured in
  `src/msf_roundpack.c:51-67`). Ignore-write (set/restore
  with an out-of-enum value leave the state unchanged,
  get returns the live valid value) preserves the last
  valid mode, is deterministic, and is unit-gateable;
  clamp-to-ties-to-even silently substitutes a mode the
  caller never validly asked for. Confirm ignore-write,
  and gate it: a wrapper state that can be observed holding
  4 before the fifth-attribute parcel lands is a failed
  negative control.

One refinement to the survey shape: the modes snapshot
type should be an opaque integer typedef
(`typedef uint32_t msf_wrap_modes_t;`) holding the rounding
value - the house precedent is `msf_saved_flags_t` (a flags
word in disguise). A struct buys extensibility for dynamic
modes this project has permanently refused (Clause 8
attributes, decimal directions); it is not buying anything
here. Modes and flags stay **disjoint** (9.3.2's modeGroup
vs 5.7.4's flag save/restore are different shapes in the
standard): mode ops must not touch flags and flag ops must
not touch modes, both directions gated.

### 4.2 Priced design (if authorised)

- New TU `compat/msf_modes.c` (not `msf_wrap.c`, which is
  Pico-only via `pico.h`): implements the 5 ops over
  `msf_wrap_state()` only, so it host-links exactly as
  `msf_aeabi.c` already does by design ("also builds for
  host logic tests" - file header). Declarations in
  `compat/msf_wrap.h` beside the state contract; spellings
  `msf_wrap_get_rounding` / `msf_wrap_set_rounding` /
  `msf_wrap_save_modes` / `msf_wrap_restore_modes` /
  `msf_wrap_default_modes`. Never `fesetround`/`fegetround`:
  `<fenv.h>` emulation is refused (SF-0 3.3) and the names
  may already exist in the SDK/newlib link.
- Validation in set **and** restore (ignore-write for any
  value outside 0..3); default = ties-to-even; save/restore
  round-trips the validated value.
- Unit gate (host, no numeric oracle exists for state
  machines; authority = clause text + SF-0 3.4): a test-only
  shim TU under `tests/` providing `msf_wrap_state()` over
  two static states with a settable fake core id (the
  shipped Pico TU is not linked). Cases: set/get per mode,
  save/restore across interleaved sets, default after dirty
  state, invalid set/restore ignored (values 4, 5, -1 as
  cast), flags untouched by mode ops, modes untouched by
  flag ops, end-to-end behaviour (set toward-positive via
  the API -> a wrapped `__aeabi_dadd` bit result changes on
  a directed case -> restore -> result returns).
- Board evidence: extend the existing AEABI/selftest hello
  shape with set/get/save/restore isolation across both
  cores and an IRQ (negative controls: cross-core leak must
  fail; same-core IRQ sharing must be *observed* - it is
  the documented contract, so the control proves the test
  can see sharing; invalid value silently accepted must
  fail; claim-label grep control - compat docs must not say
  "dynamic modes" unqualified by "9.3-shaped / wrapper
  state").
- Price: implementation ~120 lines + shim ~60 + units
  ~250 + board extension ~60 + doc wording. **Box 180 min
  (3 h) + 1 h verifier.** The cheapest family in this
  study by a factor of three - which is an argument only
  once something earns it.

### 4.3 What would earn them (nothing does yet)

Fresh check of the candidates: KissFFT never reads a mode;
the interval workload's per-call explicit attributes strictly
dominate a mode switch (and are reentrant in ways shared
per-core state is not). IAS15, the one firmware consumer
running over AEABI state, integrates at fixed ties-to-even;
tellingly, its selftest already performs save/set/restore
of `s->rounding` by direct struct field access through the
shipped `msf_wrap_state()` (`board/ias15_selftest.c:262-306`)
- the capability exists today for firmware that holds the
compat header, so the wrappers would add a validated,
documented spelling, not a new ability. Even the strongest
hypothetical - an IAS15 rounding-sensitivity experiment
(re-run the integrator under directed modes from a runtime
knob, no recompile) - is achievable this afternoon by
assigning `msf_wrap_state()->rounding` once in board code,
which is where 4.2's "particularly to support debugging"
centres its value.

Earning triggers, named so SF-2 can recognise them: (a) an
incoming workload whose source performs runtime mode
changes (fenv-style or its own mode variable) and must run
unmodified through the wrapped path; (b) productising a
rounding-sensitivity experiment as supported firmware
behaviour rather than a struct poke in test code; (c) any
consumer that needs save/restore across its own IRQ/RTOS
boundary through a stable API instead of field access.
Absent one: **keep deferred** (NO-GO), with the design
above banked and the SF-1 provisional ruling now read as
confirmed rather than provisional. If the owner wants one
small completeness win in SF-2 regardless of earning, this
is the honest one to take - labelled `C-API` and unearned,
in the same spirit as SF-1's openly-labelled compliance
breadth - but this study does not recommend spending the
prefix on it.

## 5. Measurement appendix (this study, executed)

Scripts (files, run under Git Bash, `MSF_PYTHON` =
workspace `.venv` Python 3.12.15, gcc 16.1.0 MinGW64,
`TMPDIR/TMP/TEMP` in `scratch/sf2-augmented/tmp`):

- `run_all.sh` - reference probe, baseline build+run, three
  variant builds+runs, comparison. Result `RUN_ALL_OK`.
- `ref_aug.py` - exact integer reference for Clause 9.5
  (generic over format parameters; signaled vs raised
  tracked separately per Sec.1.3). Assertions per case:
  head+tail == exact value (except the mul inexact-tail
  cell, where tail == RTTZ(residual) and inexactness is
  asserted); add/sub residual always representable; raised
  inexact only on overflow / mul-inexact-tail; zero tail
  carries head sign; NaN/infinity duplicated to both
  outputs. Coverage: p=4 exhaustive (196,608 cases: all
  256x256 pairs x 3 ops), p=6 all-first-operand x 87-value
  pool (534,528), binary16/32/64 pool x pool + seeded random
  (112,707 / 82,707 / 82,707). Cell mix confirms every flag
  row is exercised at every format (e.g. binary64: pair-exact
  63,612; tiny-exact-residual 2,379; mul-inexact-tail 4,418;
  overflow 3,372). `REF PROBE PASS`.
- Directed binary64 exhibits (from `ref-out.txt`): tie
  discriminator `(1+ulp) + 2^-53 -> head 1+ulp, tail 2^-53`
  (ties-to-even would round the head up); overflow-threshold
  tie `maxfin + 2^970 -> (maxfin, 2^970)` no flags vs
  `maxfin + 2^971 -> (inf, inf)` overflow+inexact; huge gap
  `1 + minsub -> (1, minsub)` underflow *signaled*, no flag
  under R2; `minsub x 0.75 -> (minsub, -0)`
  underflow+inexact; `-0 + -0 -> (-0, -0)`,
  `-0 + +0 -> (+0, +0)`; NaN/invalid duplication cells.
- `make_variant.py` + `variant/` - generates the Sec.2
  host variant from pristine copies (asserted single-site
  replacements). `compare.py` - op totals, decision diffs,
  decided-wrong vs catalogue exact column, short-circuit
  deployment model, static TwoSum=6 / TwoProduct=3 recount.
- `crosscheck.py` + `variant/test_aug.c` - C emulation vs
  Python reference on 42,707 binary64 cases: 42,010 exact
  bit+flag matches; 697 in four named scratch-emulation-only
  exemption classes (sub-via-negate NaN sign 254; mul
  inexact-tail RN-vs-RTTZ residual value 339 and subnormal-
  grid head tie 96; overflow-threshold tie 8 - every one a
  cell where the real integer kernel of Sec.1.5 is exact by
  construction and/or the workload guard refuses); 0
  unclassified mismatches. `CROSSCHECK PASS`.
- Outputs: `build/ref-out.txt`, `build/base-out.txt`
  (SHA-256 `ce81d66e...9aec`, 616,754 ops - frozen parcel
  values reproduced), `build/var-{r2,r1,r1adapt}-out.txt`
  (394,666 ops; variant hash `96d925e2...e42`),
  `build/compare-out.txt`, `build/crosscheck-out.txt`.

Known measurement limits: the augmented pair in the variant
is emulated over ties-to-even EFTs, so (a) it inherits any
subnormal-intermediate limits of Knuth TwoSum that the real
window kernel would not have - stage-3 decision equivalence
is therefore conservative; (b) op counts model an augmented
call as 1 - true to the workload's counting discipline, not
a cycle claim (Sec.2 boundary 3). Nothing was run on
silicon; no board claim is made or implied.

## 6. Pins and unread items

Pins for owner + second reader (before any parcel):
**P1** exact-tiny-residual underflow flag reading (Sec.1.3,
R2 recommended); **P2** exact-zero head-sign cells read with
RTTZ (Sec.1.3); **P3** augmented token spellings
(`augmented_add/sub/mul` proposed vs full
`augmented_addition/...`); **P4** rounding-column token
(`fixed` proposed); **P5** internal pack mode value for
RTTZ, coordinated with any internal round-to-odd value;
**P6** pair struct return (vs out-pointer) and the 16-byte
`msf64_pair_t` sret note; **P7** wrappers' snapshot typedef
shape and ignore-write on restore (Sec.4.1) - only if that
family is ever authorised.

Unread / unexecuted, named honestly: the IEEE PDF itself
was not opened (all clause readings rest on the S1 extract
tree, single-reader - hence the second-read entry gates);
Annex C was not re-read for these names; no MPFR or other
foreign oracle was executed for 9.5 (none decides it;
integer-exact references are complete for add/mul);
Berkeley oracle not re-probed for 9.5 (Clause 9 survey
measured no Clause 9 surface there - relied on, not
re-verified here); `src/msf_string.c`'s
multi-kilobit accumulator was not audited (Sec.1.5 needs
nothing from it); per-format `msf16.c`/`msf32.c` add kernels
were read via the binary64 exemplar + shared decode/pack
only; board bench cycles, board runs of any variant, and
`tools/run.sh` budgets were not executed (read-only study;
repo tree untouched - verified `git status` clean in
`muse-softfloat/`); harness pair-reply and runner pair-line
costs are design estimates from the char-family precedent,
not prototypes. The augmented kernel of Sec.1.5 is a
design with a measured counting model, not an
implementation - no core claim of any kind is made here.


