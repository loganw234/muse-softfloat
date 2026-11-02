# Tier 2 Clause 9 study: an SF-1-ready map of the SF-0 Section 2.7 ordered surface

Role: study-tier2-clause9 (read-only survey). Brief:
`ledger/briefs/tier2-clause9.md`. Base commit
`54e4bffea44aff6a9c2ab4b64e26707ad1e9779a`; the tree surveyed is
muse-softfloat at HEAD `32dac7d`, which differs from base only in
`docs/metrics/briefs.jsonl` (+4 lines, [M] by `git diff --stat`).
Ledger: `ledger/study-tier2-clause9.md` (plan entry starts the
180-minute box at 2026-10-27 13:56 -0700; channel test
`ledger/urgent/study-tier2-clause9-test.md` immediately before it).

Evidence tags, per the round habit: **[M]** measured by execution in
this survey (script output in `scratch/tier2-clause9/out/` or the
count script, reproducible), **[R]** read in a named source,
**[A]** argued here (a recommendation or inference, not evidence).
IEEE 754-2019 is cited by clause only; the PDF was not opened.
Clause semantics come from S1's report and the clause extracts under
`scratch/S1/extract/` (survey-authorised), paraphrased. No
third-party math-function implementation source was inspected for
design; oracle material used is public documentation, licence and
accuracy claims, header/interface declarations, and execution of the
already-pinned test oracles. Nothing with `cft` in its name was
opened, searched, or listed by this agent. One disclosure, for the
record: an early orientation listing of the workspace's *parent*
directory printed sibling directory names (this host keeps other
projects there); nothing inside any such directory was opened,
searched, or listed, and no use was made of it.

## Contents

1. The short answer (what SF-1 should propose, in order)
2. Rules inherited from SF-0, and the measured current state
3. Counting rules and the master surface table (180 + 5)
4. Item maps in SF-0 2.7 order
   - 4.1 Clause 9.6 minimum/maximum (24)
   - 4.2 Clause 9.7 NaN payload get/set (9)
   - 4.3 Dynamic rounding get/set, dynamic ties-to-away, roundToOdd (5 + mode coverage)
   - 4.4 Clause 9.5 augmented add/sub/mul (9)
   - 4.5 Clause 9.4 reductions (21)
   - 4.6 Clause 9.2 mathematical functions (117) and first-candidate ranking
5. Oracle and evidence architecture (Berkeley, MPFR, CORE-MATH, exact references)
6. Table / API / runner / board implications (study level)
7. Smallest useful gated first parcel sequence, with entry gates
8. SF-1 decision questions for the owner, with recommendations
9. Risks, falsifiers, and what was not read or not verified
Appendix A. Reproduction (scripts and probe outputs)
Appendix B. Sources

Difficulty classes used throughout (implementation + proof burden,
not schedule promises):

- **K0** — pure encoding/class combinational logic over the existing
  decode (`msf_decode`); no rounding event.
- **K1** — reuses an existing exact kernel and the one shared pack;
  work is an edge/flag table and its gate.
- **K2** — needs a new exact-integer kernel or a new pack rounding
  mode with a WIDTHS-style width proof; still exactly decidable for
  every input by construction.
- **K3** — transcendental: needs an approximation with a proven error
  bound measured against published hardest-to-round knowledge, or a
  per-input certified (Ziv-style) decision loop.
- **K4** — transcendental where hardest-case knowledge is incomplete
  or the domain needs unbounded-precision argument reduction;
  refuse in any first sequence.

Claim levels (SF-0 2.7 entry criteria, restated as labels):

- **C-754** — 754-conforming for the named clause, formats, and
  rounding modes: results, specials, and Clause 7 flags as the
  clause specifies, with correct rounding where the clause demands
  it.
- **C-ULP** — ULP-budgeted approximation under a stated error bound.
  Never under a conforming name (SF-0 2.7); if ever shipped it needs
  a distinct API name.
- **C-API** — API-compatible only: signature and documented
  behaviour exist, no conformance claim.
- **C-754-EXC** (reductions only) — Clause 9.4 exception discipline
  conforming, numeric value project-defined and stated exactly;
  SF-0 2.7 already rules that no bit-exact conformance claim
  attaches to reduction values.

A claim is always per instantiation and per rounding-mode set: a
function may honestly be C-754 for binary16 (exhaustively gated)
while still unclaimed for binary64. SF-1 should write claims that
way, never per family name (SF-0 4.3 already requires per-
instantiation coverage).

## 1. The short answer

1. **The SF-0 2.7 order is the right build order, with one seam
   step first.** [M/A] Two measured facts block any Tier 2 table
   row today (Section 2): negative control 9 in `tools/run.sh`
   refuses unless implemented rows equal coverage rows (783 of 783),
   and the generated dispatch/runner/board shape is a single
   `uint64` result from at most 3 `uint64` arguments. SF-1's first
   parcel is therefore a lead-owned seam (tier/claim accounting,
   control-9 split, new signature classes, pair- and vector-shaped
   vector syntax, watched-failing controls), exactly as P0 preceded
   Wave 1. The architecture sibling study measured the same two
   blockers independently (`ledger/study-tier2-architecture.md`,
   2026-10-27 14:02:47 entry) [R] — two routes agree.
2. **Homogeneous-only Clause 9.** [A] Counted under the current
   table's own expansion precedents [M, Section 3]: the whole
   ordered surface is **180 new core instantiations + 5 wrapper
   dynamic-mode operations** (9.6: 24, 9.7: 9, 9.5: 9, 9.4: 21,
   9.2: 117), against 783 Tier 1 rows. A `formatOf` expansion of
   the same names would cost roughly 3-9x more rows (min/max alone
   216 vs 24) for semantics Clause 9 does not ask for. Recommend
   homogeneous; put the multiplier in front of the owner as Q1.
3. **First honest claims are cheap at the front of the order.**
   9.6 min/max and 9.7 payloads are K0/K1: exact bit/class logic,
   exhaustively gateable at binary16 in the unary direction and
   class-exhaustively for pairs, decidable by
   a small project-exact bit reference — Berkeley 3e has none of
   Clause 9 [M, header inventory `scratch/oracles/sf-functions.txt`].
   They can carry C-754 first, in one small parcel (33 rows).
4. **Dynamic rounding is wrapper-layer work with a C-API label,
   and ties-to-away as a fifth attribute is a 249-row evidence
   obligation, not a 5-row feature.** [M] 249 of today's
   instantiations take the rounding attribute. The internal pack
   and the exact generators already implement ties-to-away
   (`MSF_IROUND_TIES_TO_AWAY`; `tests/gen_vectors.py` RMS includes
   `ta`) and Berkeley generates `-rnear_maxMag` [M probe], so the
   mode can be earned — but the gate, not the code, is the cost.
   Dynamic get/set itself (Clause 9.3 names) belongs in
   `compat/` over the existing per-core state and should be claimed
   C-API ("9.3-shaped access to wrapper state"), because a C
   library cannot provide a *language's* dynamic-mode scoping
   (Clauses 4.2, 9.3) [R via S1].
5. **roundToOdd: internal helper only.** [A] It is not a 754-2019
   attribute or operation; it is valuable scaffolding (round-to-odd
   at intermediate precision makes a later rounding safe, the
   Boldo-Melquiond double-rounding result [R]; Berkeley's jamming
   mode gives a pinned oracle for the pack behaviour [M probe]).
   Public exposure would be a project extension with a C-API label
   at best. Recommend internal pack mode, no header surface, no
   coverage rows — revisit only if a workload asks by name.
6. **Augmented operations are K2 and are the first item that
   cannot reuse the shipped kernels as-is.** [A] Clause 9.5 pairs
   a clause-local rounding (nearest, ties toward zero, overflow
   always to infinity) with the *exact* residual. The current
   add kernel's jam-window discards exactly the far-tail bits that
   are the residual when exponents differ widely, and the shared
   pack has no ties-toward-zero mode. Still fully C-754-able with
   an exact-residual kernel + one new internal pack mode + a width
   proof (9 rows).
7. **Reductions should be pinned to exact-round-once project
   semantics or not shipped.** [A] Clause 9.4 leaves values
   implementation-defined with conforming exception discipline.
   A superaccumulator (exact sum, one final pack) makes
   sum/dot/sumSquare/sumAbs deterministic, bit-gateable against
   MPFR's `mpfr_sum`/`mpfr_dot` + exact rationals [R, MPFR header],
   and honestly labelled C-754-EXC. The scaledProd family cannot
   be exact at fixed width for arbitrary length; propose it only
   with a stated wide-jammed-product semantics and a bounded claim,
   or defer to the workload studies.
8. **Mathematical functions: rank by decidability, not by
   familiarity.** [A, Section 4.6] First: algebraic functions whose
   rounding is exactly decidable with integer remainder evidence —
   `rSqrt`, then `hypot`, `pown`/`compound`, `rootn` (K2). First
   transcendental: `exp2` (exact exponent split, no pi), then the
   `*Pi` trig family (period reduction is exact integer arithmetic,
   unlike radian trig). Refuse in any first sequence: `pow`,
   `powr` (two-variable hardest cases are not fully known [R,
   CORE-MATH worst-cases page]) and radian `sin`/`cos`/`tan` at
   binary64 until a Payne-Hanek-grade reduction is itself gated.
   Per-format staging is the honest shape: binary16 unary is
   exhaustively provable (65,536 inputs x modes [M counts]);
   binary32 unary is exhaustively checkable against a fast foreign
   oracle; binary64 needs a Table-Maker-grade argument per
   function (SF-0 2.7 already demands this) — test volume alone
   never upgrades a claim.
9. **Oracles exist for every item, with two fences.** Berkeley
   decides nothing in Clause 9 except the rounding *modes*
   (ties-to-away and round-odd generation measured working). MPFR
   4.2.2 is installed and declares counterparts for all 39
   Table 9.1 functions plus sum/dot [M, header inventory + probe
   execution], under its documented subnormal-emulation recipe.
   CORE-MATH (MIT, execution/metadata only) is the fast foreign
   cross-check and the source of worst-case vector files, fenced
   by its own documentation: correct rounding claimed for regular
   numbers, specials/flags *not* guaranteed [R, project page] — so
   MPFR/exact references decide, CORE-MATH corroborates at volume.
10. **Nothing here is authorised by this map.** The owner directed
    that Tier 2 continue only with a scientific workload that earns
    the additions (lead ledger 2026-10-27 13:54:13 [R]). This
    report is the capability/evidence menu and the smallest gated
    sequence (Section 7); which prefix of it SF-1 should take is
    the owner's call against the two workload studies (Q13).

## 2. Rules inherited from SF-0, and the measured current state

### 2.1 What SF-0 already settled (no SF-1 re-litigation needed)

Read in full for this survey: SF-0 Sections 0, 2 (all), 3, 4, 5,
11, 12 (`muse-softfloat/docs/studies/SF-0.md` at base).

- **Order and entry criteria** (SF-0 2.7): Tier 2 in order —
  Clause 9.6 + 9.7; dynamic rounding wrappers + ties-to-away
  attribute + any public roundToOdd-style helper; augmented
  add/sub/mul; reductions (exception discipline only); then
  Clause 9 mathematical functions one at a time, each only with a
  Table-Maker-grade worst-case argument and MPFR/CORE-MATH-class
  oracle evidence. Per item: oracle built, claim level declared in
  its brief (754-conforming / ULP-budgeted / API-compatible only),
  negative controls exist. A function that cannot meet its bar is
  **refused, not shipped approximately under a conforming name**.
- **Never in this project** (SF-0 2.7, 5.3, 11): binary128,
  decimal formats, Clause 8 alternate exception handling, traps,
  fast-math / flush-to-zero / denormals-are-zero modes, "mostly
  compliant" labels. Consequences for this map: the decimal
  dynamic-mode pair of Clause 9.3 is out; decimal-only pieces of
  Clauses 9.2-9.7 (preferred exponents/cohorts, `powd` noted in
  S1's 9.2.1 extract) are out; Clause 10 expression rules and
  Clause 11 reproducibility are not Tier 2 surface here.
- **Authority order** (SF-0 4.1): standard (clause) > pinned
  Berkeley SoftFloat 3e (executable, for what it covers) > MPFR /
  exact-integer generation (what Berkeley does not cover) >
  fenced host FPU (narrow envelope, SF-0 4.2: no transcendentals,
  no ties-to-away, no binary16). Disagreements stop and are
  classified, never averaged (SF-0 4.4). Coverage is per
  instantiation; no `authority=unconfirmed` row at a wave gate
  (SF-0 4.3). No third-party source in `src/`/`include/`; oracles
  are executed, fetched by pinned hash into scratch (SF-0 4.5).
- **Contract facts Tier 2 must keep**: tininess after rounding,
  judged on the unbounded-exponent rounded value (SF-0 2.5 as
  restated by the Wave 1 tininess ruling — the shipped pack
  comment and `msf_roundpack.c` carry the corrected definition
  [R]); the SF-0 2.5 NaN matrix (default quiet NaN, first-NaN
  payload propagation, quieted-signaling delivery); flags in
  caller-owned state, non-null pointer wherever taken (SF-0 2.4);
  rounding an explicit argument, never core process state
  (SF-0 2.3/3.3); no dynamic allocation and no hardware
  arithmetic types in the core (SF-0 3.2/5.3); per-core state only
  in the compat layer with the IRQ caveat (SF-0 3.4).
- **Standard's own frame** (via S1 [R]): Clause 9 operations are
  *recommended*; anything presented as a conforming version of one
  must meet Clauses 9.1-9.2 (canonical results; correct rounding
  for the applicable attribute across the domain for Table 9.1;
  Clause 7 exceptions with Clause 9 adjustments — signaling NaN
  signals invalid, out-of-domain delivers quiet NaN + invalid,
  simple poles deliver divideByZero, inexact is a `should`).
  Special values are tabulated per function in Clause 9.2.1.

### 2.2 Measured current state (all [M] this survey unless noted)

- 783 instantiations, 783 implemented, 0 authority=unconfirmed,
  81 operation families (`scratch/tier2-clause9/count_surface.py`
  driving `tools/gen_tables.py:instantiate()` read-only). By
  rounding: attr 249, named 255, none 279. Attr rows by deciding
  authority: mpfr-exact 210, berkeley 39. (Attribute expansion in
  Section 4.3 costs evidence against both, mostly exact
  references — Berkeley cannot be the workhorse for a fifth mode.)
- Negative control 9 (`tools/run.sh` lines 170-179) computes
  implemented rows from `tables/implemented.tsv` and total rows
  from `docs/COVERAGE.tsv` and refuses unless equal: **adding one
  planned Tier 2 family reddens smoke** until SF-1 splits the
  control by tier/wave. The runner separately fails a vector line
  that names an implemented-but-not-replayable op
  (`tests/runner.c`, "implemented but not vector-replayable here").
- Dispatch shape: `msf_call_fn` returns one `uint64_t` from
  `const uint64_t *args` with `argkinds[3]` (max 3 args), generated
  by `tools/gen_tables.py:wrapper_for`; runner generic lines are
  `op rm args... -> result flags prov` with `tok[16]` and a 4096-byte
  line buffer; `hash_result` folds one result per line into the
  whole-run hash (256-byte canonical line). Precedents outside the
  generic shape: `internal.pack*` lines and char-conversion lines
  (`IN=`/`OUT=`/`SPEC=` token style) are special-cased in
  `tests/runner.c`; flag ops and versions are gated in runner
  `unit` mode, not by vectors (coverage vectors column
  `unit-flags-state`, `project-unit`).
- Board: `board/harness_main.c` reuses the same dispatch and
  replies one result + flags per vector; string rows are already
  host-gated because the CDC protocol is numeric-only
  (`docs/RECORD.md` Wave 3 [R]). Any pair- or vector-result family
  is host-only until the harness grows a shape for it.
- Core purity gates that bound Tier 2 implementation style:
  `type_scan` in `tools/run.sh` refuses the *words* float/double
  anywhere in `src/` or `include/` (comments included), and
  `symbol_scan` refuses helper symbols in target objects. All
  Tier 2 math in the core is therefore integer fixed-point over
  the limb types — no soft-float-in-soft-float shortcuts.
- Kernels available to build on [R, `src/`]: `msf_decode` +
  `msf_nan_delivery` + `msf_cmp_finite` (`msf_decode.h`, lead-owned,
  format-generic); format-parameterised exact add/sub/mul/div/
  sqrt/fma/remainder/scaleB/logB/conversions/comparisons in
  `msf16.c`/`msf32.c`/`msf64.c` over one shared pack
  (`msf_pack_generic`, 128-bit significand + sticky, internal modes
  0-4 incl. ties-to-away); `msf_u128` limb helpers with jam shift
  (`msf_wide.c`); a private 96-limb (3072-bit) big-unsigned in
  `msf_string.c` (multiply by 32-bit limb only, TU-static).
  Widths are frozen with proof notes in `docs/WIDTHS.md`; any
  kernel needing more must restate that file in its own commit.
- Provenance budget: 43 distinct provenance tags in the committed
  vectors [M, runner-style last-token count — agrees with the
  lead ledger's "43 tags total now" [R]], runner cap `MAX_PROV`
  128 with refuse-on-overflow. Headroom is finite; 39 math
  functions minting several tags each would exhaust it (Section 6).
- Compat state: `msf_wrap_state_t {rounding, flags}` per RP2040
  core in `compat/msf_wrap.c` (Pico-only: includes `pico.h`,
  `get_core_num()`; zero-init = ties-to-even because the enum puts
  it at 0) [R]. There is no host-compilable state shim and no
  public rounding setter today; the AEABI layer openly traps
  unimplemented libm names rather than approximating them
  (`compat/msf_aeabi.h` [R]).
- Oracle state: Berkeley SoftFloat + TestFloat 3e pinned by
  archive SHA-256 in `docs/metrics/fetches.jsonl`, built in
  `scratch/oracles/` with 8086-SSE specialization, tininess after
  rounding, and `-DSOFTFLOAT_ROUND_ODD` [M, `sf-build.log`];
  header inventory has 119 functions and no Clause 9 operation
  (no min/max, payload, augmented, reduction, or mathematical
  function) [M, `sf-functions.txt`]; its rounding modes are the
  five attributes plus round-odd [M, header lines 60-83]. MPFR
  4.2.2 + GMP present (S2 measured; re-measured by probe execution
  here, `mpfr version=4.2.2`). Host libm is *not* an oracle:
  mingw64 libmingwex sqrt is 1-ulp wrong on rare operands
  (repo `AGENTS.md` [R]); S2 fences SSE2 to basic ops and is
  explicit that transcendentals have no host oracle [R].

## 3. Counting rules and the master surface table

Counts below come from `count_surface.py` run against the repo's
own generator for the current surface, and from applying the
generator's existing expansion precedents to the Clause 9 names
for proposed rows (the script prints every arithmetic step;
Appendix A). Existing precedents [R, `tools/gen_tables.py:expand`]:

- homogeneous unary (roundToIntegral, next, sign-bit, classify):
  **3** per name (one per format);
- homogeneous pair (remainder, copySign, totalOrder): **3** per name;
- `formatOf` arithmetic binary (add..div): dest x src x src = **27**;
- `formatOf` arithmetic unary (sqrt): dest x src = **9**;
- comparisons (ordered source pairs, result bool): **9**;
- integer-width expansion: 8 widths (i8..u64);
- global state/version rows (flag ops): **1** per name.

Clause 9.5/9.6/9.7 spell their signatures as homogeneous
`sourceFormat` operations in S1's extracts [R]; Clause 9.2's
Table 9.1 is format-silent but SF-0 2.7 frames it like the rest of
Clause 9, and Clause 9.4 vectors are "in one format" returning
that format [R via S1]. The recommended reading is homogeneous
everywhere, with cross-format needs met by the caller's existing
gated `convertFormat` (exactly how Tier 1 treats `remainder`).
The `formatOf` alternative is costed so the owner sees the price
of reversing that reading (Q1).

| Order (SF-0 2.7) | Clause | Names | Homogeneous rows [M] | formatOf alternative [M] | New result/arg shape |
|---|---|---|---|---|---|
| min/max family | 9.6 | 8 | 24 | 216 (27/name) or 72 (compare-style 9/name) | none (existing pair shape) |
| payload get/set | 9.7 | 3 | 9 | n/a (encoding-local by definition) | none (existing unary shape) |
| dynamic get/set + save/restore/default | 9.3 (via 4.2) | 5 | 5 wrapper rows, 0 core rows | n/a | state ops (unit-gated) |
| ties-to-away attribute | 4.3 (attribute), dynamic use 9.3 | 0 new names | 0 rows; mode coverage x5/4 on 249 attr rows | n/a | enum value + vector mode token `ta` (exists for pack) |
| roundToOdd helper | not in 754-2019 | 0-1 | 0 rows recommended (internal) | n/a | internal pack mode only |
| augmented add/sub/mul | 9.5 | 3 | 9 | 81 (27/name) | **pair result (new)** |
| reductions | 9.4 | 7 | 21 (integralFormat fixed once) | 84 if scaled family widens sf over 8 int widths | **vector args (new)**; scaled family also pair result |
| mathematical functions | 9.2 Table 9.1 | 39 (31 unary, 5 binary-float, 3 float-int) | 117 (93 + 15 + 9 with one integral width) | 441; 180 if only float-int widens over 8 widths | float-int arg pair (new-ish; scaleB is the precedent) |
| **Total** | | | **180 core + 5 wrapper** | | |

Never-in-scope items stay out of every count above: decimal
dynamic modes, decimal forms of any Clause 9 item, binary128,
Clause 8, traps, non-Table-9.1 libm names that other projects ship
under similar umbrellas (e.g. error/gamma functions, cube root as
a named op — it is `rootn(x,3)` if earned, not a separate row),
and combined sin+cos operations (not Table 9.1 names).

## 4. Item maps in SF-0 2.7 order

API spelling below follows the frozen table conventions [R,
`tables/operations.tsv` header, generated header prelude]: `op` is
the snake_case token of the standard name (with the shipped
abbreviations add/sub/mul/div as precedent), the function is
`msf<dest>_<op>`, homogeneous forms carry no source suffix, the
rounding argument appears only for attribute-taking rows, and a
flags pointer appears only for flag-bearing rows. Final spellings
are SF-1's to freeze once; these are the derivations the table
rules produce.

### 4.1 Clause 9.6 minimum/maximum — 24 rows, K0/K1, C-754 first

**Names** (Clause 9.6 [R via S1 S5 + extracts]): `minimum`,
`maximum`, `minimumNumber`, `maximumNumber`, `minimumMagnitude`,
`maximumMagnitude`, `minimumMagnitudeNumber`,
`maximumMagnitudeNumber`. Proposed tokens: the snake_case forms,
e.g. `msf64_minimum_number(msf64_t a, msf64_t b, msf_flags_t
*flags)`. Homogeneous general-computational, two same-format
operands, same-format result: fits the existing homogeneous-pair
signature class (like `remainder`); rounding `none`, flags `yes`.
8 names x 3 formats = **24 rows** [M].

**Semantics** (paraphrase, Clause 9.6): the result is one of the
two operands, selected by value (plain and Number forms) or by
magnitude with the corresponding value form as tie-break
(Magnitude forms). Signed zeros are ordered for this family,
unlike ordinary comparison: negative zero is the minimum /
positive zero the maximum. Equal same-sign operands may deliver
either operand (SF-1 should pin *first operand wins* as the
project choice so vectors are deterministic [A]). Plain forms:
any NaN operand makes a quiet-NaN result under the usual NaN
rules. Number forms: with exactly one NaN operand the *number*
is delivered; with both operands NaN a quiet NaN; a signaling
NaN still signals invalid even when it is the ignored operand.
Flags: invalid is the only possible signal (signaling NaN
operand, any form). No rounding ever (selection, not
arithmetic), so exactness is unconditional and mode-independent.

**Project-choice points SF-1 must pin** [A]: (i) delivered NaN
payload/sign in the NaN cases — recommend the SF-0 2.5 matrix via
the existing `msf_nan_delivery` (first signaling quieted, else
first quiet, preserving sign+payload) so this family cannot drift
from the rest of the library; (ii) the ignored-signaling-NaN case
of the Number forms is *not* the matrix default (matrix would
deliver the quieted NaN) — the kernel must signal invalid yet
deliver the number, so `msf_nan_delivery` cannot be reused
wholesale for the Number forms; (iii) infinities and zeros fall
out of value comparison, but `msf_cmp_finite` deliberately
compares signed zeros equal (Clause 5.11) — min/max needs its own
zero-order tweak on top of it.
Also name-collision hygiene: 2008 `minNum`/`maxNum` do not exist
in 2019 (SF-0 2.1 refuses 2008 spellings unless the 2019 operation
is named); SF-1 should refuse `*_min_num`-style aliases in the
core header. A compat-layer alias, if a workload needs C
`fmin`/`fmax` spellings, maps to the **Number** forms (C's fmin
returns the number with one NaN) — that mapping belongs in the
wrapper brief, not the core.

**Difficulty: K0/K1.** Implementation is decode + class table +
finite comparison + zero-sign rule; no pack, no new width. The
only subtlety is the flag/result decoupling in (ii).

**Oracle/evidence.** Berkeley: none (header inventory [M]).
Deciding authority: project-exact bit/class reference over
decoded encodings — same provenance family as the shipped
classification/totalOrder gates (`exact-py:*` generators), which
SF-0 4.3 already accepts for Berkeley-uncovered rows, with the
reference independently reviewed like an oracle. Cross-check
(non-deciding): MPFR's `mpfr_min`/`mpfr_max` agree with the
Number forms' *value* semantics including -0 minimum / +0
maximum [M probe, Appendix A] — but MPFR has no signaling NaN,
no payloads, and a different flag model, so it can only
corroborate finite/zero/infinity cases. Exhaustive evidence:
binary16 all ordered pairs = 2^32 per name is the heroic form;
the proportionate gate [A] is exhaustive class-pair coverage by
construction (every (class, class, sign, magnitude-order) cell
with directed payloads) + exhaustive binary16 *unary-style*
sweeps of the second operand against boundary first operands +
seeded pair sweeps for binary32/64 — the shipped `copySign`
gate (`exhaustive-f16-pairs` sample tag) is the working
precedent for pair-shaped combinational ops.

**Negative controls** (each watched failing before trusted, per
SF-0 5.2 habit) [A]: sNaN-ignored-but-invalid case with the
invalid bit stripped from expectation (must fail); plain vs
Number expectations swapped on single-qNaN inputs (must fail);
-0/+0 selections swapped (must fail); a magnitude tie-break case
corrupted (must fail); NaN payload altered in expectation (must
fail under exact compare — proves the gate sees payload, unlike
Berkeley-file `nan-class` masking).

**Entry gate**: seam step landed (Section 7 step 0); semantic
pins (i)-(iii) recorded in the brief; reference generator
reviewed. **First honest claim: C-754** (Clause 9.6, all three
formats, no rounding axis). **Parcel**: one per-format-file
parcel following the Wave 1/2 pattern, or one new small TU —
recommend appending to the per-format TUs through a shared
format-generic core in the style of `msf_decode.h`, since the
logic is format-parameterised; vectors committed like
`compare-*.vec`.

### 4.2 Clause 9.7 NaN payload get/set — 9 rows, K0, C-754 first

**Names**: `getPayload`, `setPayload`, `setPayloadSignaling` —
homogeneous quiet-computational unary, **no exceptions ever**
(Clause 9.7 [R]). Proposed: `msf32_get_payload(msf32_t a)` etc.;
rounding `none`, flags `no` (like sign-bit ops — the runner flags
token is `--`). 3 names x 3 formats = **9 rows** [M].

**Semantics** (paraphrase, Clauses 9.7, 6.2.1, 2.1): the payload
is the diagnostic information in a NaN's trailing field other
than the quiet/signaling distinguishing bit — for binary formats
the trailing bits below that first bit. `getPayload` of a NaN
delivers the payload valued as a non-negative integral number in
the same format; of a non-NaN, -1. `setPayload` /
`setPayloadSignaling` of an admissible non-negative integral
operand build a quiet/signaling NaN carrying that payload; of
anything else they deliver +0. The admissible set is
implementation-defined, and a payload readable by `getPayload`
is not guaranteed settable (Clause 9.7's own note) — SF-1 gets to
choose, and should choose the maximal honest set [A]:

- payload bits available: p-2 per format → binary16 9 bits
  (0..511), binary32 22 bits (0..4,194,303), binary64 51 bits
  (0..2,251,799,813,685,247) [M]. Every such integer is exactly
  representable in its format (max < 2^p [M]), so `getPayload`
  never rounds, never overflows, and -1 is exact.
- Proposed admissible sets: quiet form 0..max (0 gives the
  existing default quiet NaN encoding — a free consistency
  check against `MSF_*_DEFAULT_QNAN`); signaling form 1..max
  (0 would encode infinity, not a signaling NaN, since a
  signaling encoding needs some trailing bit set (Clause 6.2.1)).

**Project-choice points** [A]: sign of a set NaN (recommend
positive; the input is a non-negative magnitude and the clause
is silent — document it); `getPayload` ignores the NaN's sign
(result is non-negative by definition); treatment of -0 input to
the setters (its value is 0; recommend admissible-as-0 for the
quiet form and inadmissible→+0 for signaling consistency, but
either ruling is defensible — it must be one stated ruling, with
vectors); non-integral / too-large / infinite / NaN inputs all
fall to +0 by the clause's remainder rule, *including signaling
NaN inputs signaling nothing* (the whole family is
exception-free — a deliberate contrast with general-computational
ops that the gate must prove, since reusing `msf_nan_delivery`
here would be a bug, not a shortcut).

**Interaction with shipped surface**: the character conversions
deliberately emit and accept no payload suffix (Wave 3 ruling R2,
`msf_string.c` header [R]). Clause 6.2.3 *recommends* character-
sequence payload access; Clause 9.7 does not require it. Adding
9.7 therefore makes payloads programmatically accessible while
the string grammar stays closed — SF-1 should say so explicitly
(Q3) so the claim is never read as 5.12 payload support.

**Difficulty: K0.** Mask/shift over the generated format
constants; integral checks can ride the decode (subnormal inputs
are the only non-integral finite trap below 1; large exponents
are automatically integral — the shipped roundToIntegral kernels
prove the classification pattern).

**Oracle/evidence.** Berkeley: none. MPFR: no payload model.
Deciding: project-exact encoding reference. Exhaustive binary16
in both directions is trivial (65,536 encodings): every NaN
encoding's payload readback, every admissible integer's round
trip `getPayload(setPayload(k)) == k`, `is_signaling` agreement
against the Tier 1 gated classifier. binary32/64: boundary and
directed sets (0, 1, max, max+1 as values, largest integral
below max, subnormals, ±0, infinities, both NaN kinds with
directed payloads) + algebraic round-trip sweeps.

**Negative controls** [A]: expectation with quiet bit flipped on
a `setPayloadSignaling` result (must fail); `setPayload(0)`
expected as +0 instead of default qNaN (must fail); inadmissible
input (e.g. -1, 1/2, signaling NaN) expected as NaN instead of
+0 (must fail); a flags token of `00` where `--` is required
(runner malformed — proves the no-flags shape is enforced).

**Entry gate**: admissible sets and sign/-0 rulings frozen in
the brief. **First honest claim: C-754** (Clause 9.7 with the
stated admissible sets — the sets are part of the claim text,
as the clause intends). **Parcel**: bundle with 4.1 in the first
semantics parcel (shared class-table shape; 33 rows total).

### 4.3 Dynamic rounding get/set, dynamic ties-to-away, roundToOdd

Three different objects that SF-0 2.7 bundles because they all
live "in the wrapper layer". Keep them separate in SF-1: they
have different claims, gates, and failure modes.

#### 4.3.1 Dynamic-mode get/set (Clauses 4.2, 9.3.1, 9.3.2) — 5 wrapper ops, K1, C-API first

**Names** [R via S1]: `getBinaryRoundingDirection`,
`setBinaryRoundingDirection`, and the collective `saveModes`,
`restoreModes`, `defaultModes`. The decimal pair is out (never
rule). These are *conditional* in the standard: they are
required of a language that defines dynamic mode specification,
and dynamic modes themselves are recommended, with constant
(block-scoped) specification being the required mechanism
(Clauses 4.1-4.3 via S1 S2). This library's core already chose
the stronger, testable design: rounding is an explicit argument
on every call (SF-0 2.3/3.3). Dynamic get/set is therefore
purely a compat-layer convenience over `msf_wrap_state_t`.

Proposed surface [A] (in `compat/msf_wrap.h`, never the core
header, so the core's "rounding is never process state" claim
survives untouched):

- `msf_rounding_t msf_wrap_get_rounding(void);`
  `void msf_wrap_set_rounding(msf_rounding_t rm);` — read/write
  the calling core's wrapper rounding field. Invalid enum values
  must have a stated behaviour (recommend: ignore the write, or
  clamp to ties-to-even — pick one, gate it; never store raw).
- An opaque modes snapshot type holding the dynamic modes only
  (rounding today; SF-1 decides whether it is exactly
  `msf_rounding_t` in disguise, like `msf_saved_flags_t` is a
  flags word in disguise, or a small struct for future modes):
  `msf_wrap_modes_t msf_wrap_save_modes(void);`
  `void msf_wrap_restore_modes(msf_wrap_modes_t);`
  `void msf_wrap_default_modes(void);` — default = ties-to-even
  (the Clause 4.3.3 default, and already the zero-init reading).
  Note modes != flags: flag save/restore already shipped as
  Tier 1 (Clause 5.7.4); a snapshot that silently captured flags
  too would violate both clauses' shapes. Keep them disjoint.
- Count: **5 operations, 0 core instantiations** [M counting]:
  no format axis, no flags axis, no vector replay shape today.

**Semantics/state**: per-core as shipped (RP2040: 2 static
states, IRQ shares its core's state, never implicitly
saved/restored — SF-0 3.4 contract carries over verbatim). Host
builds have no wrapper state today (`compat/msf_wrap.c` is
Pico-only [R]); SF-1 must decide the host-side test seam
(recommend: a test-only core-id shim so the state machine is
unit-testable on host, plus the P0-style board hello extended to
set/get/save/restore isolation across cores and in an IRQ).

**Oracle/evidence**: no numeric oracle exists for state
machines; the authority is the clause text + SF-0 3.4 as
restated in the brief, gated like the Tier 1 flag operations:
state-machine unit tests (set/get round trip per mode value,
save/restore across interleaved sets, default after dirty,
invalid-value ruling, flags untouched by mode ops and modes
untouched by flag ops), an end-to-end behaviour test (set
toward-positive -> wrapped add changes answer on a directed
case -> restore -> answer returns), and board isolation
evidence. **Negative controls** [A]: cross-core leak probe
(mode set on core 0 observed on core 1 must fail the selftest);
same-core IRQ clobber without save/restore (must be *observed*
— it is the documented contract, so the control proves the test
can see sharing rather than isolation); invalid enum accepted
silently (must fail per the SF-1 ruling); claim-label control:
coverage/header text must not call this language-level dynamic
modes (grep-level refusal in the brief's checks).

**First honest claim: C-API**, worded e.g. "Clause 9.3-shaped
dynamic rounding access over per-core wrapper state for the
AEABI/pico-sdk layers; the core API remains stateless and no
language binding is claimed." Anything stronger is not a
library's to claim (Clause 9.3 binds language standards [R]).

#### 4.3.2 Ties-to-away as a dynamic/fifth attribute (Clause 4.3) — 0 rows, 249-row mode obligation, K1 code / K2 evidence

Ties-to-away is already in the library where the standard
*names* it (roundToIntegral + integer-conversion named forms,
Tier 1 [R]) and in the internal pack (`MSF_IROUND_TIES_TO_AWAY`
[R]); it is required as an *attribute* only for decimal
implementations (Clause 4.3.3 via S1). SF-0 2.3/2.7 make the
attribute form Tier 2 "in the wrapper layer". Two readings,
very different costs — SF-1 must pick (Q5):

- **Reading W (wrapper-only)**: the wrapper state may hold a
  fifth value and wrapper bodies pass it into the core (the
  internal numeric value 4 already exists). But the public core
  enum has 4 values; wrapper callers casting 4 are outside the
  published contract, and every core op's behaviour under it is
  unclaimed until gated. This reading is only honest as C-API
  *even inside the wrapper* until the same evidence below lands —
  it saves no gating, it only narrows who may ask.
- **Reading P (public fifth attribute)**: add
  `MSF_ROUND_TIES_TO_AWAY = 4` to `msf_rounding_t` (value already
  reserved by the internal enum — deliberate or lucky, the seam
  exists [R]), restate the generated header prelude sentence
  that currently says ties-to-away exists only in named forms,
  and gate **every attribute-taking instantiation under `ta`**:
  249 rows [M] (arith `formatOf` 108+9+81, conversions,
  scaleB, roundToIntegralExact, fromInt, and the 12
  character-conversion rows — partitioning exactly from the
  sig counts of Section 2.2). Tier 2 then adds its own attr
  rows (reductions 21 + math 117 if all landed = 387 attr rows
  in total) which are born five-mode under this reading. Vector plumbing already supports
  the mode token `ta` for pack lines (`tests/VECTORS.md` [R])
  and the runner parses it; what is missing is per-row `ta`
  vector sets and header/table wording, not mechanism.

Semantics are already fixed (nearest, ties away from zero;
overflow to infinity like the other nearest mode; inexactness
and tininess unchanged — the shipped pack implements exactly
this [R], including its unbounded-rounded tininess judgment,
and the exact Python pack reference mirrors it). The open work
is *evidence + one trap*: string conversions under `ta`. The
decimal output rounding in `msf_string.c` rounds digit strings
outside the pack; SF-1 must verify its tie handling under a
fifth mode rather than assume the pack's gate covers it (the
Wave 3 verifier's ties plant sat in exactly that code [R via
lead ledger plant grading]).

**Oracle/evidence**: Berkeley generates ties-to-away for every
operation it covers (`-rnear_maxMag`, measured this survey:
46,464 f64_add level-1 lines, rc 0 [M]) and the shipped ingest
already maps `ta` [R]. That decides the 39 Berkeley-authority
attr rows [M]; the other 210 attr rows are decided by the exact
rational generators, which already emit `ta` for pack vectors
and need the same treatment per family (the Wave briefs'
generator pattern). MPFR note: `MPFR_RNDA` is round *away from
zero always*, not ties-to-away; the ties-away enum `MPFR_RNDNA`
is documented for a specific rounding inquiry, not as a general
operation mode [R, header] — SF-1 generators must not map `ta`
to `MPFR_RNDA`; exact references or Berkeley decide `ta`.
Exhaustive binary16 sweeps extend from 4 to 5 modes at linear
cost (262,144 -> 327,680 unary cases [M counts]).

**Negative controls** [A]: a `ta` vector replayed as `te` on an
exact-tie operand (must fail — ties are the only place the
modes differ for nearest, so the set must be tie-rich by
construction, including subnormal-boundary ties); decimal
output tie digit string under `ta` vs `te` (must differ where
the exact value is a tie); header drift control (enum added by
hand instead of through the generator must fail the drift
check — already permanent); wrapper state holding `ta` then a
zeroed state must read back ties-to-even, not `ta`.

**First honest claim**: under Reading P, C-754 per attr row
correctly extended to five attributes — but only row-by-row as
each family's `ta` gate closes; until then each row's claim
stays four-attribute. Under Reading W, C-API only. **Parcel**:
lead-owned seam + generation step (enum, prelude, ingest mode
sweep, generator mode sweep) with per-family vector landings;
the *code* change is likely near-zero [A] — budget it as an
evidence parcel. Sequence note: landing this *before* Clause
9.2 math (the SF-0 order) raises every math function's mode
obligation from 4 to 5 (Clause 9.2 demands correct rounding for
the applicable direction); landing it after lets early math
claim four modes and owe the fifth as a follow-on gate. SF-1
should choose deliberately (Section 7 recommends dynamic
get/set early, fifth attribute as its own later gate).

#### 4.3.3 roundToOdd helper — 0 public rows recommended, K1 internally

Round-to-odd (jamming: exact results unchanged; inexact results
delivered with an odd least-significant bit) is **not** a
754-2019 attribute or named operation [R via S1: Clause 4.3
defines five attributes, round-to-odd nowhere]. SF-0 2.7 admits
"any public roundToOdd-style helper" to Tier 2 without
committing to one. Its real value is internal: rounding an
intermediate result to odd at precision p+2 makes a second
rounding to any smaller precision correctly rounded for nearest
modes (the Boldo-Melquiond double-rounding result, formally
proved [R]); in pack terms it is the perfect sticky carrier.
That is exactly the machinery a Ziv-style math kernel wants
between its wide intermediate and its final pack (Section 4.6).

Measured state: the shipped pack does **not** implement it —
`round_inc`'s default arm truncates, so an unrecognised internal
mode value silently means toward-zero today [R]; Berkeley's
round-odd is compiled into the pinned oracle and generates
vectors (`-rodd`, 46,464 f64_add + 768 f64_sqrt lines, rc 0
[M]), so an internal mode is gateable on day one via
`internal.pack*` vectors with a new `to`-style token. Overflow/
underflow/inexact behaviour under jamming must be pinned from
Berkeley's measured behaviour + project ruling in the seam
brief (no clause decides it): inexact iff the exact value is
not representable; overflow behaviour follows the nearest-mode
delivery Berkeley exhibits — measure, don't assume.

**Recommendation** [A]: implement as internal pack mode 5
(`MSF_IROUND_TIES...` sibling, name e.g. `MSF_IROUND_TO_ODD`)
with pack-level vectors + a wrong-mode negative control, used
by whatever math kernel needs it; no public enum value, no
header function, no COVERAGE row (coverage counts must not
imply 754 surface). If a workload later demands the public
helper, its claim ceiling is C-API under a project-extension
name (Clause 9.1 lets implementations define extra operations;
that does not make them standard surface) — SF-1 question Q6.

### 4.4 Clause 9.5 augmented addition/subtraction/multiplication — 9 rows, K2, C-754 available

**Names**: `augmentedAddition`, `augmentedSubtraction`,
`augmentedMultiplication` (Clause 9.5, binary formats only [R]).
Proposed tokens following the shipped abbreviations:
`augmented_add`, `augmented_sub`, `augmented_mul` (SF-1 may
prefer the full snake_case standard names; the table's `std_name`
column carries either). Each takes two same-format operands and
delivers an ordered **pair** of same-format results plus flags;
it takes **no rounding attribute** (the clause fixes its own
rounding, below), so table shape is rounding `named`-like with
flags `yes`. 3 names x 3 formats = **9 rows** [M]; a formatOf
reading would be 81 and is not recommended (the clause spells
homogeneous pairs; mixed-format pairs would need conversion
semantics the clause never states [A]).

**API shape decision** [A]: C has no tuple; the table precedents
offer (i) a returned pair struct (`msf16_pair_t` etc. — new
public types, generator-emitted) or (ii) head returned by value
+ tail through an out-pointer beside the flags pointer.
Recommend the struct return: it cannot be half-used, mirrors the
clause's `(sourceFormat, sourceFormat)` shape, and keeps the
flags pointer in its usual trailing position. The dispatch
trampoline cannot express it today (Section 2.2) — new sig
class + runner pair-line (Section 6).

**Semantics** (paraphrase, Clause 9.5 [R]): let the clause-local
rounding be *nearest, ties toward zero* — the nearer of the two
neighbours, the smaller-magnitude one on an exact tie, with
overflow always delivering signed infinity (the overflow
threshold sits half an ulp above the largest finite magnitude,
and exact equality with that threshold rounds *down* to the
largest finite — the one place this mode differs from
ties-to-even at the top of the range). The pair is (head,
residual) where head is the exact result so rounded and, when
head is finite, residual is the *exact* difference between the
exact result and head. A zero residual takes head's sign.
Special and flag behaviour, operation by operation:

- Exception behaviour otherwise mirrors the corresponding
  Tier 1 arithmetic operation under the clause-local rounding.
- Any NaN input: that NaN (per the propagation rules) is
  delivered as **both** results; an invalid operation likewise
  delivers the same quiet NaN twice.
- Infinite head (overflow or infinite operand): both results
  are the head value, flagging like the underlying operation.
- A nonzero residual strictly inside the subnormal magnitude
  range signals underflow **even when the residual is exact**
  (a deliberate inversion of the usual exact-tiny silence).
- For add/sub, inexact is signaled **only** on overflow; the
  pair (head, residual) is otherwise exact by construction —
  including when head is subnormal.
- For mul, the residual of a near-underflow product may fall
  between representable subnormal steps and be *inexactly*
  representable: in that case the residual is itself rounded
  with the clause-local rounding and the operation signals
  underflow **and** inexact. Otherwise mul flags like add.

**Why this is K2, not kernel reuse** [A]: (1) the shared pack
has no nearest-ties-toward-zero mode — a new internal mode is
needed in `round_inc` + overflow-threshold handling (its
overflow-to-infinity rule differs from ties-to-even exactly at
the threshold tie, and from toward-zero everywhere else);
(2) the pack's interface discards the residual by design (it
returns one rounded value from significand+sticky), while
augmented ops must produce the residual *exactly*; (3) the
shipped add kernel jams the smaller operand into a fixed
128-bit window, collapsing far-tail bits into sticky — but when
operands differ hugely in exponent those bits *are* the residual
(e.g. head = larger operand, residual = smaller operand
verbatim), so a jammed kernel cannot emit them. Mul is the easy
third: the exact product fits today (106 bits in 128 [R,
WIDTHS]), so residual = exact product minus head is computable
from existing machinery once the head pack gains the new mode.
For add/sub the honest design is an exact-residual path: form
the exact sum at a common scale in a wide accumulator whose
span covers the format's exponent range plus precisions
(binary64: emin-p to emax is ~2,100 bits of span), or compute
head first and then the residual as an exact three-term
difference with the same span argument. Either way a WIDTHS.md
restatement and probably a shared multi-limb exact type beyond
`msf_u128` (the string TU's 3072-bit accumulator proves the
project can build and gate one, but it is TU-private and
multiply-by-limb only [R]).

Tininess interplay to pin in the brief [A]: the clause-local
rounding is *not* one of the four attributes, so SF-0 2.5's
after-rounding judgment must be restated for the head pack (the
residual-underflow rule above replaces it for the pair as a
whole in most cases — the brief must walk the boundary cases,
e.g. head itself tiny-and-inexact with an exactly-zero or
normal residual). This is exactly the class of definition the
Wave 1 tininess ruling burned time on; SF-1 should front-load a
second-reader check on the flag table before code.

**Oracle/evidence.** Berkeley: none. MPFR: no augmented
primitive, but decides everything needed indirectly — head via
MPFR at destination precision (nearest mode + exact-tie
detection by higher-precision recomputation), residual via exact
MPFR/rational subtraction of head from the exact result.
Deciding authority recommendation: project-exact reference over
integers/rationals implementing the clause table literally,
triangulated against MPFR on directed sets (the Wave 3 decimal
pattern: exact reference decides, MPFR cross-checks, any split
stops the gate under SF-0 4.4). Exhaustive: binary16 pairs are
2^32 per name — feasible as a one-time evidence run in C
against the exact reference's compiled twin, sampled in the
standing budget [A]; add/sub additionally admit an algebraic
whole-domain argument (residual representability) that the
verifier can check as a proof note. Directed families that
must exist: exact ties at several binades (ties-toward-zero
discriminators), overflow threshold tie, cancellation to exact
zero (sign rule), huge-exponent-gap pairs (residual = far
operand), subnormal heads, tiny-residual underflow-without-
inexact cases, mul residual-below-subnormal-step cases
(underflow+inexact), infinity/NaN matrix duplicated to both
outputs.

**Negative controls** [A]: head computed ties-to-even (must
fail on directed ties); residual sign flipped on exact-zero
cases; underflow expectation removed on a tiny exact residual
(must fail); inexact added on a non-overflow add (must fail);
pair results swapped (must fail — proves order is checked);
jam-window mutant (residual sticky-collapsed) must fail the
huge-gap family.

**Entry gate**: flag table second-read; width proof drafted;
pair runner shape landed in the seam. **First honest claim:
C-754** (Clause 9.5 as written — its semantics are fully
specified, unlike reductions). **Parcel**: one new TU over a
new shared exact-wide helper, all three formats in one parcel
(the kernels are format-parameterised; splitting by format
would triple-review the flag table).

### 4.5 Clause 9.4 reductions — 21 rows, K2, C-754-EXC with project-defined values

**Names** (Clause 9.4 [R]): `sum`, `dot`, `sumSquare`, `sumAbs`
(vector -> same format) and `scaledProd`, `scaledProdSum`,
`scaledProdDiff` (vector(s) -> {scaled product, integral scale
factor} pair). Proposed tokens: `sum`, `dot`, `sum_square`,
`sum_abs`, `scaled_prod`, `scaled_prod_sum`, `scaled_prod_diff`.
7 names x 3 formats = **21 rows** when the integral choices are
fixed once [M].

**API shape decisions** [A] (SF-1 freezes; recommendations in
parentheses):

- Vector operand: pointer + length, `const msf64_t *p, size_t n`
  (the clause's length lives in a language-defined integral
  format — `size_t` is the C-honest choice and makes the
  clause's negative/non-integral-length latitude unreachable;
  null-with-zero-length behaviour must still be stated:
  recommend n=0 never dereferences).
- Rounding: the clause leaves results implementation-defined
  approximations (any association, any wider intermediate). A
  deterministic library should nonetheless take the explicit
  attribute + flags pointer like every other core op and apply
  the attribute at its **one** final rounding (recommend yes —
  interval consumers need directed bounds from the same call).
- Scale factor `sf` type: (recommend `msf64_t` holding an
  integral value, i.e. this API's existing logBFormat choice —
  it composes directly with the shipped `msf*_scale_b` whose
  second operand is binary64, and the clause itself phrases the
  result as a `scaleB` input). The integer-type alternative
  (`int64_t`) is cheaper to test for range but breaks that
  composition; widening over 8 int widths (84 rows) is refused.
  With binary64 `sf`, an exactly-integral `sf` overflows only at
  exponent sums beyond 2^1024 scale — unreachable for vectors
  that fit in any memory this project targets, but the clause's
  invalid-on-unrepresentable-sf rule must still be specified
  and reached by a *constructed* test at the representation
  boundary if SF-1 keeps the case (or explicitly documented as
  unreachable-by-construction — a claim a verifier should
  challenge).
- Pair return for the scaled family: struct {scaled, sf} like
  4.4, with `sf`'s delivered value on NaN/invalid outcomes
  pinned (the clause fixes `pr` = quiet NaN and, for the
  sf-overflow case, `sf` = quiet NaN when `sf` is floating; for
  operand-NaN outcomes it says only that a quiet NaN is
  returned — recommend pr = SF-0-matrix NaN, sf = +0, stated).

**Standard's semantics** (paraphrase, Clause 9.4 [R]): results
are implementation-defined approximations to the exact sums/
products; intermediate association and precision are free; at
most **one exception per invocation** (not per element); any
signaling NaN element signals invalid; after an invalid
condition (sNaN, infinities of opposite signs summing, zero
times infinity in products) processing may stop early (relevant
to timing on the RP2040, and to observable behaviour if vector
reads could fault — state it); under default handling inexact
accompanies signalled overflow/underflow, and is otherwise
unspecified; empty sums deliver +0 and empty scaled products
deliver {1, +0}, silently. Per family specials: sum/dot — any
NaN element yields a quiet NaN; same-sign infinities yield that
infinity silently; mixed infinities (or a zero-times-infinity
product inside dot) signal invalid; otherwise no avoidable
intermediate exceptions, with overflow/underflow judged on the
final result. sumSquare/sumAbs — an infinite element yields
+infinity **in preference to** a NaN element elsewhere (order in
the clause: infinity check first), else NaN yields quiet NaN.
Scaled family — any NaN yields quiet NaN; invalid for
zero-times-infinity products and for per-element
opposite-sign infinity sums / like-sign infinity differences
feeding the product; otherwise zeros/infinities in the product
deliver a signed zero/infinity without invalid; in the regular
case the scaled mantissa result must not itself overflow or
underflow (that is the point of the scale factor) and
divideByZero should not be signalled even if logB is used
internally.

**Project semantics recommended** [A]: exact accumulation, one
rounding. For sum/dot/sumSquare/sumAbs keep a fixed wide
superaccumulator spanning the destination's full exponent range
(binary64 terms span ~2,100 bits; dot/sumSquare products span
~4,300 bits) plus carry headroom that grows logarithmically in
n — a fixed 5-6 kbit accumulator makes the exact claim true for
any n whose carry headroom fits, so SF-1 states the exactness
bound as a formula in n per format rather than pretending
fixed-width means unbounded. The final value is then rounded
once by the shared pack under the attribute; flags derive from
that final rounding plus the clause's special table. This is a
*stronger* semantics than 9.4 requires (correctly rounded exact
reduction), it is deterministic and bit-gateable, and directed
modes give true interval enclosures — the property interval
consumers actually need, provable here rather than hoped.
For the scaled family, exact significand products grow ~p bits
per element, so no fixed width is exact for arbitrary n:
propose a precisely stated wide-jammed semantics [A] (exponent
sum tracked exactly in a wide integer; significands multiplied
into a fixed wide window with jam capture and a stated
reduction schedule (left-to-right), one final rounding of the
scaled mantissa) and label the numeric claim accordingly
(project-defined approximation, exception-conforming) — or
defer the scaled family entirely until a workload names it.
Shipping sequential same-format multiplication as "the"
implementation is also clause-legal but strictly worse and
harder to bound; do not.

**Difficulty: K2** for the sum family (superaccumulator + final
pack + special-table flags), **K2/K3 boundary** for the scaled
family (semantics design and its evidence, not code volume).

**Oracle/evidence.** Berkeley: none. MPFR declares exactly the
two decidable primitives wanted for the recommended semantics —
`mpfr_sum` and `mpfr_dot`, correctly rounded exact reductions
[R, header lines 811-813] — under the same subnormal-emulation
recipe as Section 5; sumSquare/sumAbs reduce to them by exact
pre-transformation in the generator (squares/abs are exact).
Exact rational references in Python (`Fraction`, the shipped
generators' pattern) decide small-n cases and every flag cell.
No foreign oracle exists for the scaled family's split result;
its reference is the project definition itself with MPFR
checking `scaleB(pr, sf)` reconstruction against the exact
product on directed sets. No exhaustiveness is possible over
vectors; evidence = property-directed families: n in {0, 1, 2,
boundary around accumulator headroom claims}, cancellation
chains (exact zero from huge terms — sign-of-zero under
roundTowardNegative must be pinned: exact zero sums take the
Clause 6.3 sign for the attribute [A]), overflow that cancels
back into range (kills sequential implementations — the
discriminating family for the exact claim), subnormal-boundary
final results, one-exception discipline (two sNaNs + an invalid
product in one vector still deliver exactly one invalid bit and
nothing else), infinity-vs-NaN precedence per family, and
length/aliasing hygiene (p==q for dot, n=0 null).

**Negative controls** [A]: sequential-rounding mutant must fail
the cancel-back-into-range family; per-element flagging mutant
(inexact on every intermediate) must fail one-exception cases;
infinity-precedence swap in sumSquare must fail; `sf` off by
one must fail reconstruction; early-exit that skips reading a
later sNaN *before* an invalid condition exists must fail
(pin: early exit is permitted only after the invalid condition
is already certain).

**Runner/board impact** is the largest of any item (Section 6):
variable-length operands do not fit current token shapes, and
board replay would need bulk transfer. Recommend host-gated
first, like the string rows, with board evidence as a sampled
selftest digest rather than vector replay.

**Entry gate**: numeric semantics + sf type + n-bound formula +
special/flag table frozen and second-read; vector syntax
frozen. **First honest claim: C-754-EXC** — "Clause 9.4
exception discipline conforming; values are the correctly
rounded exact reduction (sum family) / stated wide-jammed
product (scaled family) under the caller's attribute" — never
"bit-exact conforming", which SF-0 2.7 already prohibits here.
**Parcels**: sum family (12 rows) first; scaled family (9 rows)
as a separate later parcel only on workload evidence.

### 4.6 Clause 9.2 mathematical functions — 117 rows, K2-K4, claim per function per format

#### 4.6.1 Common contract

**Names and shapes** (Clause 9.2 Table 9.1, 39 operations [R,
S1 count agrees: 6+6+7+14+6]). Homogeneous reading [A]:
31 unary x 3 formats = 93; 5 binary-float x 3 = 15; 3 float-int
x 3 = 9 (one integral width) — **117 rows** [M]. Proposed tokens
(snake_case of standard names): `exp, expm1, exp2, exp2m1,
exp10, exp10m1, log, log2, log10, logp1, log2p1, log10p1,
r_sqrt` (rSqrt, following the `log_b`/`scale_b` hump precedent),
`sin, cos, tan, sin_pi, cos_pi, tan_pi, asin, acos, atan,
asin_pi, acos_pi, atan_pi, sinh, cosh, tanh, asinh, acosh,
atanh, hypot, pow, powr, atan2, atan2_pi, compound, rootn,
pown`. All take the rounding attribute + flags (rounding `attr`,
flags `yes`), like unary/binary arithmetic. Float-int rows need
a new sig class (float result, float operand, integer operand);
the integer operand's width is Q-level (recommend single
`int64_t` — it covers every exponent a binary64 can name
integrally, matches the widest shipped integer format, and
avoids 72 rows of width theatre [A]; the standard leaves
behaviour for non-integral/infinite floating `n` language-
defined precisely because integers are the natural domain [R]).

**Result/flag semantics common to all** (paraphrase, Clauses
9.1-9.2, 9.2.1 [R]): a conforming form must be **correctly
rounded for the applicable attribute over its whole domain**,
deliver canonical results, and signal Clause 7 exceptions with
Clause 9 adjustments: signaling NaN operand signals invalid
(and a quiet NaN is delivered); quiet NaN operand delivers a
quiet NaN except where the function states otherwise (three
families do: `hypot` with an infinite other operand delivers
+infinity **even with a quiet NaN operand**; `pow(+1, y)` is 1
even for quiet NaN y, and `pow(x, ±0)` / `pown(x, 0)` /
`compound(x, 0)` are 1 even for quiet NaN bases — each such
exception defeats wholesale reuse of `msf_nan_delivery` and
needs its own directed cases [R via 9.2.1 extracts, summarised
per function below]); finite out-of-domain input delivers quiet
NaN + invalid; a simple pole at a finite operand delivers
signed infinity + divideByZero; overflow/underflow per Table
9.1 per function; inexact should accompany inexact results and
should not accompany exact ones — this project already treats
every `should` it can gate as a promise (SF-0 2.5 payload
precedent), so SF-1 should claim inexact always-correct too
[A] (it is free: any correct-rounding kernel knows whether its
decision discarded a nonzero tail). Special values are fully
tabulated per function in Clause 9.2.1 (zeros with signs,
integer/half-integer trig-Pi anchors, atan2 quadrants including
signed-zero arguments, the pow family decision trees) — a
per-function specials table second-read against 9.2.1 is part
of every math parcel's entry gate, exactly like Tier 1's
Clause 6 tables. Tininess for results that land subnormal
follows the project's single after-rounding choice (SF-0 2.5) —
Table 9.1 lists underflow for most functions, so the shared
pack's judgment must be the one making it [A].

**What "applicable attribute" includes** is SF-1's staging
choice (4.3.2): four modes if math lands before the fifth
attribute, five after. Correct rounding in directed modes is
not a by-product of a nearest-mode implementation — kernels
must carry rigorous error bounds that decide directed cases at
the same precision (the pack decides directed modes from
guard/round/sticky, so a kernel that produces a sufficiently
wide correctly-jammed intermediate (4.3.3) plus one pack gets
all modes from one decision — the architecture this report
recommends per function [A]).

#### 4.6.2 The implementation reality in this codebase

Three measured facts shape every estimate below. (1) Core code
may name no hardware arithmetic types and acquires no helper
symbols [M gates, Section 2.2]: kernels are limb-integer
fixed-point. Polynomial evaluation therefore needs a wide
fixed-point multiply-accumulate over limbs — `msf_u128` has
"multiply two 64-bit words to 128" but no 128x128 product [R],
so K3 work starts with a new internal wide type (recommend one
shared 256/512-bit fixed-point helper in its own tested TU,
WIDTHS-rested) — build it once, in the seam or first math
parcel, not per function. (2) The final rounding event already
exists and is mode-complete (the shared pack): a kernel's job
is to deliver sign + wide significand + faithful sticky such
that the pack's one rounding is the correctly rounded answer
in every claimed mode. For transcendental kernels that means
the intermediate error must be *proved* smaller than the
distance from the true value to the nearest rounding boundary
for every input — the Table Maker obligation — or the kernel
must certify the decision per input with an error bound and
escalate precision when the bound cannot decide (Ziv's
strategy). (3) Constants (pi, ln2, log2e, ...) become hex limb
tables *derived and gated like vectors* (generated by the
exact/MPFR side, regenerated byte-identically, never copied
from another library's tables — provenance discipline is the
SF-0 4.3 vector rule applied to code constants; the IAS15
coefficient-table verification in scratch measured that
toolchain conversions of such tables can silently differ, so
SF-1 pins constants as integers, never as decimal literals
re-converted per build [R, lead ledger ias15 entries]).

Argument reduction splits the 39 cleanly [A]:

- **Exact reductions**: `exp2` family (split exponent into
  integer + fraction exactly); `log2` family (extract binary
  exponent exactly); `*Pi` trig (argument is already scaled by
  pi: reduction modulo the period is exact integer arithmetic
  on the significand/exponent for *every* finite input, however
  large — after which a bounded-range kernel in t = fraction
  needs pi to working precision); `hypot`/`rSqrt`/powers/roots
  (algebraic, below).
- **Constant-factor reductions**: `exp`/`exp10`/`log`/`log10`
  (+ m1/p1 variants) reduce through a multiplication by an
  irrational constant carried to intermediate precision — the
  constant's precision is part of the error budget.
- **Hard reductions**: radian `sin`/`cos`/`tan` for large
  arguments need the argument reduced modulo pi/2 with pi
  carried to a width growing with the input exponent (over a
  thousand bits at binary64 extremes) before any polynomial is
  reached; correctness of the reduced argument near multiples
  of the period is the dominant risk, not the polynomial.

#### 4.6.3 Per-function map and ranking (workload-agnostic, per brief)

Classes: **ALG** algebraic — correct rounding decidable exactly
with integer arithmetic + remainder evidence (no Table Maker
search needed; the decision is exact by construction);
**TR-B** transcendental, bounded/exactly-reducible domain —
needs approximation + published hardest-case margin or Ziv
certification; **TR-R** transcendental dominated by argument
reduction or two-variable hardness. Rank is feasibility order
for *first C-754 parcels*, considering specials burden,
directed-mode cost, and oracle coverage (MPFR column: header
declaration present in 4.2.2 [M]; CORE-MATH column: project
documentation table lists all three formats [R, parsed
2026-10-27, Appendix A] — execution on this host unverified,
see Section 5).

| Rank | Function(s) | Class | Why here / main hazards | MPFR | CORE-MATH doc |
|---|---|---|---|---|---|
| 1 | rSqrt | ALG | 1/sqrt decided by exact integer comparisons of x*y^2 against 1 (width ~3p — new WIDTHS row); tiny specials table (negative invalid, signed zeros are poles, +inf -> +0); reuses sqrt/div kernel craft | `mpfr_rec_sqrt` | f16/f32/f64 |
| 2 | hypot | ALG | Exact sum of two squares into the sqrt pack; span doubles (exponent range x2) so needs the wide accumulator of 4.5 kin; NaN-vs-infinity precedence exception; overflow only from the final value | `mpfr_hypot` (probe agrees on inf/NaN) | f16/f32/f64 (worst cases restricted — irrelevant if decision is exact) |
| 3 | pown, compound | ALG | Exact integer powering with capped multiplication + exact tie detection (ties are *attainable*: exact powers can sit on midpoints); enormous |n| decided by exponent bounds, not iteration; specials trees are the cost (zero/infinity bases x sign/parity of n; compound's -1 boundary) | `mpfr_pow_si/_z`, `mpfr_compound_si` | compound f16/f32 only per doc parse; pown none |
| 4 | rootn | ALG | Exact integer n-th root + power comparisons for small |n|; large |n| collapses toward 1 and needs its own boundary analysis (results 1 vs next neighbours); n=0 invalid; signed-zero parity differs from sqrt (clause note) | `mpfr_rootn_si` | none listed |
| 5 | exp2, exp2m1 | TR-B | Easiest transcendentals: integer part exact via scaleB machinery, fraction in a unit interval; exp2m1 keeps accuracy near 0 by direct series; overflow/underflow thresholds are exact exponent cuts | yes | f16/f32/f64 |
| 6 | log2, log2p1 | TR-B | Binary exponent extraction exact; reduced range near 1 via atanh-style series; log2p1's pole at -1 and accuracy near 0 are the care points; exact anchor log2(2^k)=k must be exact by construction | yes | f16/f32/f64 |
| 7 | exp, expm1, exp10, exp10m1 | TR-B | As rank 5 plus one irrational constant factor in reduction; exp10m1/expm1 near-zero branches; well-studied worst cases exist (Section 4.6.4) | yes | f16/f32/f64 |
| 8 | log, log10, logp1, log10p1 | TR-B | As rank 6 plus division by ln(2)/ln(10)-class constants to working precision; poles at 0 (-1 for p1 forms) | yes | f16/f32/f64 |
| 9 | sinPi, cosPi, tanPi | TR-B | Period reduction exact at any magnitude (see 4.6.2); then pi*t needs pi to wide precision; exact anchors at integers/half-integers incl. tanPi poles (+divideByZero) and signed zeros — specials *are* the gate | yes (`*_sinpi` spellings) | f16/f32/f64 |
| 10 | asinPi, acosPi, atanPi, atan2Pi | TR-B | Bounded domains/outputs; division by pi once at the end (constant in the error budget); atan2Pi specials are exact constants (cleaner than radian atan2); underflow near 0 | yes | f16/f32/f64 |
| 11 | asin, acos, atan | TR-B | Bounded in/out, no reduction; acos near 1 and asin near ±1 lose relative accuracy structurally (series in sqrt(1-x)-style variables); atan(±inf) is a rounded constant that should signal inexact | yes | f16/f32/f64 |
| 12 | sinh, tanh, asinh, atanh | TR-B | Ride on exp/log kernels once those exist; tanh saturates to ±1 exactly beyond a cut; atanh poles at ±1; cosh/acosh overflow cuts | yes | f16/f32/f64 |
| 13 | cosh, acosh | TR-B | As 12; cosh evenness + overflow threshold must be exact-cut, acosh domain edge at 1 | yes | f16/f32/f64 |
| 14 | atan2 | TR-R | Quadrant logic + pi-precision range results (results *are* pi multiples near axes); worst cases only partially computed in the literature tooling [R]; specials table is large but enumerable | yes | f16/f32/f64 (restricted worst cases) |
| 15 | sin, cos, tan (radian), binary64 | TR-R | Payne-Hanek-grade multi-precision reduction is a parcel in itself; near-period-multiple inputs decide the claim. **Refuse at binary64 until the reduction is gated alone**; binary16/32 are far cheaper (bounded input exponent => bounded pi width) and may be claimed earlier per format | yes | f16/f32/f64 |
| 16 | pow, powr | TR-R | Two-variable hardest cases not fully known (worst-case files cover mainly exact/midpoint-prone exponents [R]); huge specials trees; only a Ziv-certified kernel with unbounded-precision fallback carries the claim, which this codebase cannot honestly field inside the window. **Refuse in SF-1's first sequence**; revisit only with a dedicated study | yes (`mpfr_pow`, `mpfr_powr`) | pow f16/f32/f64; powr none listed |

Unranked leftovers check: the 39 are all placed — unary 31
(ranks 1, 5-13, 15), hypot/atan2/pow/powr/atan2Pi (2, 10, 14,
16), compound/rootn/pown (3, 4) [M count against Section 3].

#### 4.6.4 Evidence ladder by format (what each claim level costs)

Correct-rounding evidence is *format-asymmetric* — the same
function is three different claims:

- **binary16 unary** (65,536 encodings x 4-5 modes = 262,144 /
  327,680 cases [M]): exhaustive against MPFR is *complete*
  evidence — the gate itself proves the claim for the shipped
  binary, kernel proof or not. binary16 binary-float pairs are
  2^32 per mode: feasible as a one-time recorded exhaustive run
  against a fast decider (exact MPFR twin in C), sampled in the
  standing budgets; float-int rows add an n axis that cannot be
  exhausted — n-classes (0, ±1, small, boundary, huge) + the ALG
  exactness argument carry it. A kernel that computes in wide
  fixed point and is then **proved by exhaustion at binary16**
  is a legitimate first parcel shape; do not demand the binary64
  argument before claiming binary16.
- **binary32 unary** (2^32 x modes): exhaustive is possible
  only against a *fast* foreign decider. MPFR-per-case at that
  volume is a days-scale run [A]; CORE-MATH-class execution is
  precisely the intended role (their own binary32 univariate
  checks are exhaustive [R]), with MPFR triangulating samples,
  specials, and every disagreement. Binary binary32 is 2^64 —
  impossible; worst-case + directed + random MPFR volume,
  under an error-bound argument.
- **binary64** (and binary forms everywhere): no exhaustiveness.
  A C-754 claim needs all three legs, per SF-0 2.7's
  "Table-Maker-grade worst-case argument **and** MPFR/CORE-MATH-
  class oracle evidence": (a) the function's published
  hardest-to-round cases pass (worst-case vector files exist
  per function in the CORE-MATH ecosystem, computed mostly with
  the BaCSeL tool, headers stating the identical-bit counts [R,
  worst-cases page]; importing them is a fetch-record act with
  licence noted, Section 5); (b) directed + seeded-random MPFR
  differentials at volume, all modes, specials exact-compared;
  (c) the *argument*: intermediate precision + proven error
  bound exceeds the known worst-case gap for that function and
  format (numbers live in (a)'s sources and the Handbook
  literature S2 cites — SF-1's per-function brief must quote
  the gap and its source, this survey deliberately does not
  transcribe per-function bit counts it did not re-derive), or
  a Ziv loop whose per-stage error bounds certify each
  undecided case at higher precision with a proven termination
  bound. For ALG functions leg (c) collapses to the exactness
  of integer remainder comparisons — which is why they rank
  first. For pow, leg (a) is known-incomplete [R], so only Ziv
  certification can carry binary64 — the concrete reason for
  refusal rank 16.
- **C-ULP / C-API fallbacks**: if a function's leg (c) cannot
  close in its parcel budget, SF-0's rule is refusal, not a
  quiet downgrade. A workload that genuinely needs speed over
  proof may ask SF-1 for an explicitly approximate variant
  under a **different name** with a stated, *measured* ULP
  budget (max-ULP evidence vs MPFR over the same suites; never
  a claim of correct rounding) — no such variant is in the
  recommended first sequence.

Directed modes deserve one explicit warning: most published
worst-case searches and many library claims are nearest-mode
stories. A kernel+pack design where one jammed wide
intermediate feeds the mode-aware pack (4.6.1) makes directed
correctness follow from the same error bound, but the *gate*
must still run every directed mode over the worst-case and
random suites; CORE-MATH claims all modes for most entries with
some marked nearest-only [R] — per-function mode coverage of
the oracle must be read at fetch time, not assumed (Section 5).

**Negative controls per math parcel** [A]: a worst-case input
with its expected value moved 1 ulp (must fail); specials
mutants (hypot(qNaN, inf) expected NaN; pow-family anchors if
ever attempted; tanPi pole expected finite); inexact stripped
from a known-inexact anchor (atan(inf)); directed-mode swap
(tp expectation under tn) on a subnormal-output case (also
exercises the tininess judgment); constant table regenerated
with one limb altered (drift/regen refusal + vector failures —
two independent catches required); and the project-permanent
style control: a kernel built with its wide precision truncated
must fail the worst-case family (proves the suite can see the
margin it claims).

**Parcel shape** [A]: one function at a time (SF-0's words),
all three formats in the parcel (kernels are
format-parameterised like the shipped ones; claims may still
*close* per format in sequence f16 -> f32 -> f64 within the
parcel's gates), new `src/msf_math.c`-style TU growing function
by function over the shared wide helper. Each parcel carries:
specials table (second-read), error-bound/worst-case note
(WIDTHS sibling), constants generator, vector sets per mode,
oracle triangulation log. First parcel recommendation: rSqrt
(Section 7) — it exercises the whole pipeline (wide widths,
specials, flags, modes, MPFR+CORE-MATH triangulation, f16
exhaustion, f32 fast-oracle exhaustion if fetched) with an
exactly decidable core, de-risking every later K3 parcel.

## 5. Oracle and evidence architecture

The Tier 1 authority order (SF-0 4.1) survives; what changes is
which authority can decide what. Summary first, fences after.

| Authority | Decides (Tier 2) | Corroborates | Never decides |
|---|---|---|---|
| IEEE 754-2019 by clause (S1 extracts) | semantics, specials, flag rules, admissible-set latitude | — | numeric values |
| Berkeley SoftFloat/TestFloat 3e (pinned, built) | rounding-*mode* behaviour of the pack: ties-to-away, round-odd [M probes]; Tier 1 regression unchanged | — | any Clause 9 operation (absent [M]) |
| MPFR 4.2.2 (installed [M]) | all 39 Table 9.1 result values; sum/dot exact reductions; augmented head/residual ingredients; min/max values in finite cases | worst-case adjudication, constant derivation | flags under 754 rules (its flag model differs), NaN payloads/signs, signaling NaNs, min/max NaN cases, pair splits, reductions' sf |
| CORE-MATH-class executables (not yet fetched) | nothing alone | fast binary32/binary16 exhaustive differentials; binary64 worst-case suites (.wc data) | specials/flags/NaN behaviour (its own docs fence these [R]); any design input (execution/metadata only) |
| Project-exact references (Python Fraction + compiled C twins) | 9.6/9.7 entire; augmented literal clause table; reductions' specials/flags + scaled split; pack modes; string-mode extensions | everything MPFR decides, on sampled classes | itself (must be independently reviewed, SF-0 4.3) |
| Host SSE2/libm | nothing new (Tier 1 fenced envelope unchanged) | — | transcendentals, ties-to-away, binary16 (SF-0 4.2); host libm sqrt is a measured counterexample, not an oracle |

**Berkeley fences** [M/R]: coverage is exactly the Tier 1 set
(header inventory 119 functions, `scratch/oracles/
sf-functions.txt`); its five modes + round-odd are compiled in
(`-DSOFTFLOAT_ROUND_ODD` in the pinned build log) and
`testfloat_gen -rnear_maxMag` / `-rodd` both generate cleanly
(46,464-line f64_add level-1 sets, rc 0, this survey). Flag
translation at ingest and `nan-class` masking for Berkeley
files already exist and carry over to `ta`/`rodd` pack checks.

**MPFR fences and recipe**: MPFR's correct-rounding claim is
per operation at set precision with exact inputs [R, S2 S2.1];
binary-format emulation needs the documented recipe — precision
p, exponent bounds set so the format's subnormal floor is the
MPFR floor, and `mpfr_subnormalize` after each operation (S2
gives binary64 emin -1073 / emax 1024 [R]; binary32 emin -148 /
emax 128 by the same convention [R, marked believed there];
binary16 emin -23 / emax 16 by the same derivation — this
survey's arithmetic from the binary64 anchor: smallest
subnormal is 2^-24 = 0.5 x 2^-23 in MPFR's exponent
convention). The f32/f16 pairs were **not** probe-verified here;
SF-1's oracle bring-up must known-answer-probe them (smallest
subnormal, overflow threshold, directed subnormal rounding)
before any vector is trusted — that probe is in Section 7's
seam checklist. Header inventory [M]: all 39 Table 9.1
functions have declarations (spellings `mpfr_log1p` for logp1,
`mpfr_rec_sqrt` for rSqrt, `mpfr_rootn_si`, `mpfr_pow_si/_z`,
`mpfr_compound_si`, `mpfr_powr`, `mpfr_{sin,cos,tan,...}pi`),
plus `mpfr_sum`, `mpfr_dot`, `mpfr_min`, `mpfr_max`,
`mpfr_fmma/fmms` (irrelevant here). MPFR flags (nan/underflow/
overflow/inexact/erange queries) exist [M probe shows the API]
but their semantics are MPFR's, not Clause 7's — SF-1 derives
754 flags from the exact references and the implementation's
pack, never transcribes MPFR flags. MPFR is LGPLv3+ [R, S2]:
test-only linking in scratch, as today. Throughput honesty:
MPFR decides millions of cases per gate, not billions — the
volume legs of Section 4.6.4 are sized accordingly.

**CORE-MATH fences (documentation survey only)**: INRIA
project, MIT licence [R]; mission is correctly rounded
functions for integration into libms; per its project page,
correct rounding is claimed for all rounding modes (some
entries marked nearest-only), univariate binary32 is checked
by exhaustive search, bivariate/larger formats only against
known hard-to-round cases; **implementations care about
correct rounding for regular numbers and do not necessarily
handle NaN/infinity/zero or set underflow/overflow/inexact
flags** [R, page notes]. Worst cases ship as `xxx.wc` files
beside each function, mostly computed with BaCSeL, headers
stating identical-bit counts and symmetries; binary64 worst
cases cover the full range except pow (mainly exact/midpoint-
prone exponents), atan2, hypot, atan2pi (restricted sets) [R,
worst-cases page]. Parsed availability (documentation table,
2026-10-27): 35 of the 39 Table 9.1 names list binary16 +
binary32 + binary64 code; compound lists binary16/binary32
only; powr, rootn, pown have no rows — 36 listed in some form
(Appendix A — parser over
the fetched documentation text; **not** execution-verified, and
per-cell parse error is possible: SF-1 re-verifies against the
pinned tree's directory *listing* at fetch, which is metadata,
before relying on any cell). Adopted role if the owner approves
(Q10): fetch by archive/commit hash into `scratch/oracles/`
beside Berkeley with a `fetches.jsonl` row; build only the
test/check executables needed; smoke the build against MPFR on
directed sets before any differential is trusted (a foreign
oracle gets the same bring-up suspicion Berkeley got in P0);
use for (i) fast exhaustive binary16/binary32-unary
differentials and (ii) provenance-tagged worst-case vector
import (`coremath-wc:<fn>` style, with the file's own
identical-bits header quoted in the parcel's worst-case note).
Never copied source, never a design input, never the decider
on specials/flags — disagreements route to MPFR/exact under
SF-0 4.4. Also named in its docs, for completeness of the
foreign-oracle menu [R]: CRlibm (unmaintained mirror),
RLIBM (binary32 subset, all modes), LLVM-libc correctly rounded
subset — one foreign oracle is enough; SF-1 should pin one.

**Project-exact references**: the shipped precedent is per-wave
Python generators over `Fraction`/integers whose outputs are
committed vectors, plus MPFR triangulation on sampled classes
(Waves 1-3 [R]). Tier 2 needs new references for: min/max class
tables, payload encodings, augmented clause table, reduction
specials/flags, scaled-product reconstruction, per-function
specials. Each is test code reviewed like an oracle (SF-0 4.3)
— the Tier 1 lesson that a shared wrong formula in C *and*
reference passes both (tininess ruling [R]) is why MPFR
triangulation is mandatory wherever MPFR can speak.

**Provenance/authority labelling** [A]: today's authority
vocabulary (berkeley / mpfr-exact / project-exact /
project-exact+berkeley-check / auto-*) needs two honest
extensions, both as seam work: a `+coremath-check` suffix family
(corroboration never deciding, mirroring `+berkeley-check`),
and a **claim column** (C-754 / C-754-EXC / C-ULP / C-API with
mode-set qualifier) in `operations.tsv` propagated to
COVERAGE.tsv — claim levels are currently brief-text only,
which is invisible to counting. Provenance tags: budget them
(43/128 used [M]) — one tag family per *generator*, not per
function file, or raise `MAX_PROV` deliberately in the seam.

## 6. Table / API / runner / board implications (study level)

Everything here is a *consequence to design in SF-1*, costed so
parcels are not surprised; none of it was changed by this
read-only survey.

**Tables & generator** (`tables/operations.tsv`,
`tools/gen_tables.py`):

- New sig classes: homogeneous min/max pair (can reuse the
  remainder/pair expansion shape under a truthful new sig name),
  payload unary (reuse sign-unary shape, flags `no`),
  pair-result binary (augmented), vector reductions (two shapes:
  plain + pair-with-sf), math unary / math binary (reuse
  homogeneous shapes), math float-int (new). Dynamic mode ops:
  recommend **not** core table rows at all (compat header only);
  if SF-1 wants them counted, flag_op-style global rows are the
  precedent (1 per name, unit-gated).
- New public types emitted in the header prelude: per-format
  pair structs; (if counted) an opaque saved-modes type lives in
  the compat header, not the generated core header.
- A `claim` column (Section 5) plus per-row mode-set
  qualification for math functions claimed per format — the
  generator currently emits one status per row from
  `implemented.tsv`; per-format claim closure for one function
  is already per-row (93 unary rows are per-format), so no new
  mechanism is needed there, only discipline in `implemented` +
  `claim`.
- A `tier` notion: the `wave` column can carry Tier 2 wave
  numbers (4, 5, ...) [A], but control 9's implements==total
  accounting must split by tier (Tier 1 forever 783/783; Tier 2
  implemented-of-total reported separately) — seam-owned, with
  its own watched-failing control (a Tier 1 row flipped to
  planned must still refuse).
- Header prelude restatements queued by design decisions:
  five-attribute sentence (4.3.2), pair/vector shapes, claim
  wording per family. All go through the generator (drift gate
  already refuses hand edits).

**Runner & vectors** (`tests/runner.c`, `tests/VECTORS.md`):

- Pair results: extend the special-cased line family (pack/char
  precedent) rather than the generic trampoline: proposed
  syntax `op - a b -> hi lo flags prov` parsed by sig, both
  results folded into `hash_result`-equivalent canonical lines
  so board/hash comparisons see both halves. [A]
- Vector reductions: comma-joined single-token operand lists in
  the char-line token style: `op rm N=<n> V=<hex,...> [W=<...>]
  -> r [sf] flags prov`. Consequences the seam must answer:
  4096-byte line buffer caps committed-line n (fine — large-n
  evidence belongs in generated runtime suites, with seeds);
  `tok[16]` is untouched by comma-joining; the expect-counts
  awk in `run.sh` takes last field = provenance, still true;
  malformed-shape refusals per family join the existing
  char-line style checks.
- State ops (dynamic modes): unit-mode gating like flag ops
  (no vectors), plus a host shim decision (4.3.1).
- Mode tokens: `ta` accepted for generic lines once 4.3.2
  lands (parser already knows it; public-op lines must gain
  per-family `ta` sets); an internal `rodd` pack token (4.3.3)
  if the internal mode lands (`to` suggested, seam picks).
- Comparison rules: exact stays default; **no new masking
  modes** for Tier 2 — MPFR/CORE-MATH expected NaNs in foreign
  files cannot be payload-compared, so foreign-generated files
  either carry the existing `nan-class` compare with its printed
  masking, or (recommended for math) generator-side translation
  to SF-0-matrix expectations with provenance naming the
  translation, so specials compare exactly. [A]
- Budgets: smoke gains committed directed Tier 2 sets per
  landed family; `standard` gains the exhaustive binary16
  extensions (cheap) and per-function random MPFR streams
  (generated at run time into build dir, the berkeley_ingest
  pattern). Exhaustive binary32 differentials (if CORE-MATH is
  fetched) are a *new named evidence run*, not a standing
  budget — recorded once per function with oracle hashes, like
  board runs. `tools/run.sh` SRC list grows per new TU
  (lead wiring step, as in Wave 3).

**Board** (`board/harness_main.c`, CDC protocol): pair/vector
shapes do not fit the one-result reply. Options in cost order:
host-gate Tier 2 non-scalar families (string precedent),
extend the reply to two results for pair ops (small, worth it
for augmented), bulk vector transfer for reductions (defer).
Whatever SF-1 chooses, board claims name shapes covered —
"783 of 783" style whole-surface board language must not
silently extend to Tier 2 rows the harness cannot run. Math
kernels on RP2040 also need flash/RAM honesty per function
(constant tables + accumulator stack) measured in the parcel,
descriptive per SF-0 Section 8 — 264KB SRAM total [R, IAS15
entries] makes a 5-6 kbit accumulator (~0.75 KB) and kilobyte
constant tables non-issues, but float-int/vector APIs take
caller buffers whose sizes are the caller's.

**Compat/AEABI**: adding core math does **not** unwrap the
`msf_aeabi_trap` libm names automatically [A]. Each `__wrap_*`
libm spelling (sin, exp, ...) is its own workload-earned step
mapping C semantics (errno-free documented, ties-to-even wrapper
state, binary32+64 spellings) onto gated rows — and only rows
whose C-754 claim has closed at that format. `<fenv.h>` remains
unemulated; dynamic wrapper get/set (4.3.1) is the project's
own spelling, deliberately not `fesetround`.

## 7. Smallest useful gated first parcel sequence

Sequencing principle [A]: follow SF-0 2.7's order (it is
already cheapest-evidence-first), insert one seam step, defer
only the fifth attribute *inside* its bundle (it is an evidence
multiplier on everything after it), and stop the sequence
wherever the workload evidence stops — every prefix is a
complete, claimable stopping point. Sizes are instantiation
counts [M]; effort classes from Sections 4-5. Every step keeps
Tier 1's gates green on `standard` and follows the round's
standing shape (brief file, design entry, planted-copy
verification where it fits, serial merge — strict-leaning
risk-tier policy [R, KICKOFF closing decisions]).

**Step 0 — SF-1 seam (lead-owned, no new semantics).** Contents:
claim + tier columns and control-9 split with its watched-
failing control; new sig classes and pair/vector runner syntax
with malformed-shape refusals and negative controls
(corrupted-bit-on-pair-second-result watched failing);
authority vocabulary extension; MPFR emulation known-answer
probes for binary32/16 (Section 5) recorded as oracle bring-up;
(optional, Q10) CORE-MATH fetch pin + smoke-vs-MPFR; host shim
for wrapper state; provenance-tag budget rule. *Entry gate*:
SF-1 approved. *Exit gate*: smoke green with zero Tier 2 rows
implemented and at least one planned Tier 2 family present in
the table proving the accounting split refuses the old way and
passes the new way.

**Step 1 — min/max + payloads (33 rows, K0/K1, C-754).**
Sections 4.1-4.2 in one parcel. *Entry*: ruling pins recorded
(NaN matrix reuse, first-operand tie pins, admissible sets,
sign/-0 rulings). *Exit*: exhaustive binary16 coverage per
4.1/4.2 + directed f32/f64, controls watched failing, standard
green. This step also proves the new table/claim plumbing on
the cheapest possible semantics.

**Step 2 — dynamic wrapper modes (5 ops, K1, C-API) + internal
round-to-odd pack mode (0 rows, K1).** Sections 4.3.1, 4.3.3.
*Entry*: claim wording approved (C-API text); invalid-enum and
save/restore semantics pinned; round-to-odd pack behaviour
measured from Berkeley and restated as project rules. *Exit*:
host state-machine units + board isolation evidence;
`internal.pack*` round-to-odd vectors vs Berkeley-generated
expectations + truncated-mode negative control. (Round-to-odd
may slip to step 5 if no kernel needs it yet — it is
scaffolding, sequenced by need [A].)

**Step 3 — augmented add/sub/mul (9 rows, K2, C-754).**
Section 4.4. *Entry*: flag/underflow table second-read against
Clause 9.5, width proof drafted, pair runner live (step 0).
*Exit*: directed families of 4.4 incl. huge-gap and
tiny-residual cells, MPFR triangulation, controls watched
failing, WIDTHS restated in the same commit series.

**Step 4 — reductions, sum family only (12 rows, K2,
C-754-EXC).** Section 4.5. *Entry*: exact-round-once semantics,
n-bound formula, sf-type decision (needed now only to avoid
re-opening the family later), specials table second-read.
*Exit*: discriminating families (cancel-back-into-range,
one-exception, infinity precedence) + MPFR sum/dot
triangulation. Scaled family (+9 rows) is **step 4b, only on
workload evidence naming it**, with its wide-jammed semantics
statement as its entry gate.

**Step 5 — first mathematical function: rSqrt (3 rows, K2-ALG,
C-754 staged f16 -> f32 -> f64).** Section 4.6. Includes the
shared wide fixed-point helper if the design wants it now
(rSqrt itself needs wide integer comparisons more than
polynomial machinery — SF-1 may land the general helper here
or defer to step 7; decide in the design entry). *Entry*:
specials table second-read, width proof (x*y^2 bound), oracle
legs per format declared. *Exit*: f16 exhaustive; f32
exhaustive-or-sampled per Q10 outcome with MPFR triangulation;
f64 directed + random MPFR at volume + worst-case files if
fetched; controls watched failing.

**Step 6 — fifth attribute (ties-to-away, Reading P) — placed
here deliberately [A].** 0 new rows; mode sweep over the 249
Tier 1 attr rows plus the Tier 2 attr rows landed by then
(reductions + rSqrt: 15-24 more). *Why
here*: before this point every Tier 2 claim is mode-light
(min/max, payload, augmented, reductions-with-stated-modes,
one math function); landing the fifth mode now applies it to a
finished Tier 1 + small Tier 2 surface in one evidence parcel,
and every later math function is then born five-mode. Landing
it at SF-0's literal position (step 2) is also defensible but
front-loads the largest pure-evidence bill before any new
semantics exist. Q5 puts both placements to the owner.
*Exit*: per-family `ta` sets closed row-by-row; claim column
updated only where closed; char-conversion tie families
explicitly included.

**Step 7+ — one function at a time in rank order** (hypot,
pown/compound, rootn, exp2/exp2m1, log2/log2p1, ... per
4.6.3), each a parcel with per-format staged claims, stopping
whenever the earning workload is satisfied. Radian binary64
trig and pow/powr are **outside** this sequence (separate
studies if ever earned).

Per-step line/effort honesty: steps 1-2 are small (Tier 1
parcels shipped ~173 rows inside 3,000-line ceilings [R, lead
ledger]; 33 K0 rows are far below that). Steps 3-5 are
medium: one new kernel + one new reference + tables each.
Step 6 is generation-heavy and code-light. Step 7 items vary
from medium (ALG) to the largest parcels in the project (K3
binary64 with worst-case notes) — SF-1 should box them by
function with explicit stop rules (if leg (c) of 4.6.4 cannot
close, the parcel returns *refused* with the binary16/32
claims it did earn, not a silent C-ULP relabel).

## 8. SF-1 decision questions for the owner

Recommendations are the survey's [A]; each is phrased so a
one-line owner answer settles it.

- **Q1. Clause 9 shape: homogeneous-only (180 core rows) or
  formatOf-expanded (up to ~4x rows)?** Recommend homogeneous
  (Sections 3-4); cross-format callers compose with the gated
  conversions, as Tier 1's remainder already does.
- **Q2. Payload rulings**: maximal admissible sets (quiet
  0..max, signaling 1..max), set-NaN sign positive, -0
  admissible-as-0 for the quiet form? Recommend yes as stated
  in 4.2 — the admissible sets become part of the claim text.
- **Q3. Character payload suffixes stay out** (9.7 numeric
  access only; string grammar not reopened)? Recommend yes.
- **Q4. Dynamic modes**: compat-only 9.3-shaped get/set +
  save/restore/default over per-core state, claimed C-API with
  the wording in 4.3.1, modes disjoint from flag save/restore?
  Recommend yes. Sub-choice: invalid enum value on set —
  ignore-write (recommended) vs clamp-to-even.
- **Q5. Ties-to-away attribute**: public fifth enum value gated
  across all 249 attr rows (Reading P), placed after the first
  math function (recommended, step 6) or at SF-0's literal
  position (step 2)? Or wrapper-only C-API (Reading W)?
  Recommend P at step 6. Either way the *applicable-attribute*
  set for Clause 9.2 claims must be stated per function.
- **Q6. roundToOdd**: internal pack mode only, no public
  surface (recommended), or a public helper now? If public,
  accept it can only ever be labelled a project extension
  (C-API), never 754 surface.
- **Q7. Augmented API**: pair-struct return (recommended) vs
  out-pointer tail; full names (`augmented_addition`) vs
  shipped-style abbreviations (`augmented_add`)? Recommend
  struct + abbreviations, frozen in the table.
- **Q8. Reductions semantics**: exact-round-once values under
  the caller's attribute (recommended, C-754-EXC label) with
  `sf` as binary64 integral value (recommended) vs `int64_t`;
  and scaled family deferred unless a workload names it
  (recommended)? The n-bound exactness formula is part of
  whichever claim text is chosen.
- **Q9. First math function and staging**: rSqrt first, claims
  staged per format inside each function parcel (recommended).
  Confirm refusal list for SF-1's first sequence: pow, powr,
  radian sin/cos/tan at binary64 (per-format binary16/32 trig
  remains admissible when earned).
- **Q10. Foreign oracle fetch**: pin CORE-MATH (MIT) into
  scratch oracles for execution + worst-case data under the
  fences of Section 5 (recommended), or proceed MPFR-only and
  forgo binary32-exhaustive differentials? Either answer keeps
  the no-copied-source / no-design-input rule untouched.
- **Q11. Accounting**: claim column + tier-split control 9 +
  provenance budget in the seam (recommended yes), so README/
  RECORD counts can never blend C-754 with lesser claims.
- **Q12. Board evidence bar for Tier 2**: host-gate new shapes
  first with sampled board digests per landed wave
  (recommended), or extend the CDC harness before any Tier 2
  merge? Budget implication only; correctness gates are host
  either way.
- **Q13. How much of the sequence does the chosen workload
  earn?** This map is workload-agnostic by brief; the owner's
  standing direction is that Tier 2 continues only with a
  workload that earns the additions (lead ledger
  2026-10-27 13:54:13 [R]). Recommend SF-1 authorise a *prefix*
  of Section 7 against the KissFFT and interval-geometry
  studies' remove-it-and-what-breaks findings, and record the
  remainder as mapped-but-not-authorised rather than letting
  the full 180-row menu read as a plan.

## 9. Risks, falsifiers, and what was not read or not verified

**Load-bearing risks in using this map** [A]:

1. If the homogeneous reading (Q1) is wrong for the owner's
   intent, every count and parcel size in Sections 3-7 scales
   by the formatOf multipliers shown — settle Q1 before SF-1
   drafting, not during.
2. The Clause 9.5/9.4 flag tables restated here are
   paraphrases of S1's extracts; the Wave 1 tininess episode
   is the measured cost of a shared misreading between code
   and reference. The entry gates require a second reader on
   the 9.5 tininess interplay and the 9.4 one-exception/
   precedence tables precisely because this survey is a single
   reader.
3. CORE-MATH availability per function/format is
   documentation-parsed, not execution-verified; if cells are
   wrong (notably compound at binary64), Section 4.6.4's
   binary32-binary64 evidence legs change cost, not shape —
   MPFR-only remains the floor. Its build on this Windows host
   (documented testing is x86_64-linux [R]) is unverified and
   could itself cost a parcel of oracle bring-up.
4. MPFR binary32/binary16 emulation constants are believed,
   not probed (Section 5); a wrong emin silently poisons
   subnormal expectations — hence the seam probe.
5. Per-function worst-case gaps (bit counts) are deliberately
   not transcribed here; until an SF-1 brief quotes each chosen
   function's gap from its source, K3 effort classes are
   rankings, not estimates. A function whose true gap exceeds
   the chosen intermediate precision falsifies that parcel's
   design — that is the intended failure shape (refuse, restate
   precision), and the negative control (truncated-precision
   build must fail) is how the project notices.
6. The fifth-attribute step assumes near-zero core code change
   because the pack already implements ties-to-away; ops whose
   kernels round outside the pack (string output; scaleB/rint
   internals) could each hide a mode assumption. The step is
   budgeted as evidence work, but a verifier should treat
   "kernel handles mode 4" as a per-TU claim to test, not an
   inheritance.

**Not read / not verified in this survey** (named so SF-1 does
not mistake silence for coverage):

- The IEEE PDF itself (forbidden by brief); Clause 9 semantics
  rest on S1's paraphrase + S1's page extracts, other clauses
  on S1/SF-0. Annex C's operation list (S1 extract pages
  82-83) was used only as a name cross-check via search hits,
  not read line by line.
- S1/S2 reports outside the sections used (S1 Clause 5 detail
  and binary16-interchange analysis; S2 host-FPU traps beyond
  what's quoted; S3/S4 not authorised for this brief beyond
  SF-0's citations of them).
- Any CORE-MATH (or other libm) implementation source,
  constants, or proof PDFs — by brief restriction (public
  documentation, licences, accuracy claims, interfaces only).
  Worst-case `.wc` *contents* were not fetched or read; only
  their documented existence/format/provenance.
- Berkeley implementation source beyond the public header
  interface lines and build logs already in scratch; TestFloat
  generation was executed, its source not read for design.
- The full text of `msf16.c`/`msf32.c`/`msf64.c`/
  `msf_string.c` line by line (kernel inventories and headers
  were read; per-kernel mode-4 behaviour was argued from the
  pack + generator evidence, not re-proved per kernel — see
  risk 6). `board/` firmware beyond the harness protocol,
  `video/`, and IAS15 scratch were not surveyed.
- Bench/performance data for Tier 2 shapes (no Tier 2 code
  exists to measure; any cycles figures in sibling workload
  studies rest on Tier 1 op costs, not on anything here).
- No `tools/run.sh` budget was executed in this survey (read-
  only brief; the tree's green state is the RECORD/ledger's at
  base [R], re-verified by the lead at merge time, not here).
  Probe programs built and ran only against the test oracles
  in scratch (Appendix A).

### 9.1 Sibling-study cross-check (ledger re-read at close)

Read before closing (third read moment): the three sibling
surveys' closing ledger entries (their scratch reports were
not re-read in full here; claims below are as ledgered).

- **Architecture** (closed 14:07:39): independently measured
  the same seam blockers and the same authority partition
  (berkeley 117 / mpfr-exact 390 / project-exact 165 /
  +berkeley-check 111 — agrees with Section 2.2's count), and
  proposes the same seam-first shape. One placement differs
  from this map: it puts reductions *nowhere* in the library,
  where Section 4.5/Step 4 here propose a core exact-round-once
  sum family. SF-1 must pick; this report's costing stands
  either way (the "nowhere" answer simply deletes Step 4/4b).
- **Interval geometry** (closed 14:12:54, ADOPT WITH FRAMING):
  the workload earns **only Clause 9.6** (semantics-owning
  endpoint selection), corroborating Step 1's priority;
  augmented ops measured as performance-only there (8 augmented
  calls vs 21-36 FMA expansion calls for exact dot3), and
  Clause 9.4 reductions judged unusable for containment under
  the clause's own loose results (true as written; Section
  4.5's strengthened exact semantics would change the fact but
  not the earn, since Tier 1 FMA already suffices there).
  Payloads, dynamic modes, and all Clause 9 functions unearned
  by that workload.
- **KissFFT** (closed 14:05:33, ADOPT WITH FRAMING): earns
  **binary64 sin/cos only, and only under runtime twiddle
  generation** (exactly N sin + N cos at init, none in
  execution); rejects the rest of Tier 2 as earner. That is a
  direct tension with Section 4.6.3 rank 15 (radian binary64
  trig refused in the first sequence) that the lead must
  resolve in synthesis; two mitigating facts for that
  conversation, both from the sibling's measurements: the
  workload's arguments are the *computed* phases (bounded by
  construction, |phase| < 2pi), which is far inside the domain
  a full C-754 sin/cos claim must cover — bounded-argument
  correct rounding is not the Payne-Hanek problem; and their
  twiddle reference itself distinguishes correctly-rounded-of-
  computed-phase from correctly-rounded-of-true-angle (620 of
  1,024 cos points differ), so which quantity the workload
  wants correctly rounded is an SF-1 question before it is a
  kernel question. A library claim, however, cannot quietly be
  partial-domain: shipping `msf64_sin` claims the whole Clause
  9.2 domain, so the earn either funds rank 15 in full, uses
  precomputed/generated-off-board twiddles (no core addition),
  or takes an explicitly non-conforming name — SF-1 decides
  with both maps open.

## Appendix A. Reproduction

All scripts live in `scratch/tier2-clause9/` (run from the
workspace root; outputs under `scratch/tier2-clause9/out/`):

- `count_surface.py` — current surface (via the repo
  generator) and every proposed count in Sections 3-4.
  Headline output: 783 instantiations, 783 implemented, attr
  249; Tier 2 homogeneous total 180 core + 5 wrapper.
- `mpfr_probe.c` + `oracle_probes.sh` — MPFR 4.2.2 execution
  probes. Observed: `mpfr_min/max` ignore a single NaN operand
  (Number-like), `min(-0,+0)=-0`, `max(-0,+0)=+0`,
  `hypot(+inf,NaN)=+inf`.
- `gen_probes2.sh` — pinned `testfloat_gen` executions:
  `-rnear_maxMag` and `-rodd` f64_add (46,464 lines each,
  rc 0), `-rodd` f64_sqrt (768 lines, rc 0). A first attempt
  with `-n 200` was refused by the generator's per-function
  minimum — recorded, not used.
- `parse_coremath_page.py` — parser over the fetched CORE-MATH
  documentation page text producing the availability matrix
  used in 4.6.3/5 (35/39 all-format, compound f16/f32, powr/
  rootn/pown unlisted). Documentation metadata only.
- `verify_report.py` — independent re-checks run post-draft:
  MPFR header declares counterparts for 39/39 Table 9.1
  names; the ranking places all 39 exactly once; the attr-row
  partition sums to 249; Q1-Q13 and Steps 0-7 all present; no
  copied-standard-text telltales. Exit 0.
- `ledger_start.sh`, body files — the channel test + plan
  entry that open this survey's ledger record.

## Appendix B. Sources

Local (at base `54e4bff` unless noted): `ledger/briefs/
tier2-clause9.md`; `ledger/README.md`; `ledger/lead.md`;
muse-softfloat `AGENTS.md`, `docs/studies/SF-0.md` (S0, S2-S5,
S11, S12), `docs/RECORD.md` (Wave 3 close + closing decisions),
`docs/KICKOFF.md` (risk-tier brief policy), `docs/WIDTHS.md`,
`docs/BOARD.md`, `tables/{formats,operations}.tsv`,
`tools/gen_tables.py`, `tools/run.sh`, `tests/VECTORS.md`,
`tests/runner.c`, `tests/berkeley_ingest.py` (head),
`tests/gen_vectors.py` (mode inventory), `src/msf_internal.h`,
`src/msf_decode.h`, `src/msf_roundpack.c`, `src/msf_string.c`
(header), `compat/msf_wrap.{h,c}`, `compat/msf_aeabi.h`,
`board/harness_main.c` (protocol shape),
`docs/metrics/fetches.jsonl`. Scratch: S1 report (S1.1-S5
focus) + extracts (outline; Clause 9 pages; 6.2.1/6.2.3); S2
report (S1 Berkeley, S2 MPFR, S4 hard cases); oracle header
inventory and build logs under `scratch/oracles/`; sibling
ledger entries `ledger/study-tier2-{architecture,kissfft,
interval}.md` (plans + architecture blockers entry).

Public web (documentation/claims only, fetched 2026-10-27):
CORE-MATH project page, worst-cases page, and FAQ
(core-math.gitlabpages.inria.fr — mission, MIT licence,
availability table, accuracy-claim notes and fences,
BaCSeL/worst-case file description, C-binding naming note);
Boldo & Melquiond, "When double rounding is odd" (abstract —
round-to-odd double-rounding property); S2's recorded web
sources for Berkeley/MPFR (jhauser.us, mpfr.org) as cited
there. IEEE 754-2019 is cited by clause throughout, never
quoted at length and never opened as PDF.

