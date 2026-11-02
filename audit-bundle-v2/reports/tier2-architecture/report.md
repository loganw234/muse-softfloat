# Tier 2 architecture and integration survey

Role: study-tier2-architecture (read-only). Brief:
`ledger/briefs/tier2-architecture.md`. Base `54e4bff` (HEAD `32dac7d`
adds only the four wave4 rows in `docs/metrics/briefs.jsonl`, MEASURED
by `git diff --stat`; working tree clean). Ledger:
`ledger/study-tier2-architecture.md`; channel test
`ledger/urgent/study-tier2-architecture-test.md` at 2026-10-27
13:56:19 -0700 started the 180-minute box. Nothing with `cft` in its
name was opened, searched, or listed. No repository code was modified
and the board was not touched. Marks: READ a file, MEASURED a run or
count, COMPUTED arithmetic on measured inputs, BELIEVED unverified.

## 0. Top findings and recommendation

Tier 2 can be integrated without weakening the Tier 1 claim, but only
through a lead-owned seam step first, and only for additions a
workload earns under the rubric in Section 5. Three measured facts
bound every proposal:

1. **The runner currently forbids planned operations.**
   `tools/run.sh` control 9 ("full-surface inventory", lines 170-179)
   passes only when implemented rows equal total coverage rows
   (783 of 783). The first planned Tier 2 table row breaks `smoke`.
   Tier accounting must be split (Tier 1 rows invariant at 783/783;
   Tier 2 planned rows counted and named, never silently dropped)
   before any Tier 2 family is tabled. This is a lead seam change in
   the P0 sense, not a parcel edit.
2. **The evidence shape is one result from at most three operands.**
   The generated dispatch (`tools/gen_tables.py` `wrapper_for`,
   `msf_op_desc_t.argkinds[3]`) binds a trampoline
   `(args[<=3], rm, flags*) -> uint64`. The host runner's token
   formula (2 + nargs + 1 + 3), the whole-run hash line, and the
   board harness (`R <result> <flags>`, 512-byte lines) all assume
   exactly that. Augmented two-result operations, array reductions,
   and stateful dynamic wrappers are **not expressible** today. The
   two precedents outside the shape are the six flag operations,
   gated as an exhaustive state machine in runner `unit` mode, and
   the 12 character conversions, special-cased in `tests/runner.c`
   and host-only on the board (the harness answers `E noshape`;
   Wave 3's record accepts this for strings).
3. **The formatOf multiplier is the dominant cost decision.**
   A binary family costs 3 instantiations homogeneous-only, 9 in the
   compare-shaped cross-format form, or 27 in the `arith_bin`
   formatOf form (COMPUTED from `gen_tables.py` expansion rules).
   Tier 1 paid the full matrix because Clause 5 owes it. Tier 2
   items are recommended operations; paying 27 per op by default
   would let a handful of families rival a whole wave of vectors,
   board sample, and verification. Default: homogeneous-first (3),
   formatOf only where a workload call path or the standard's own
   definition (as study-tier2-clause9 enumerates it) demands it.

Recommendation in one paragraph: SF-1 should be structured like SF-0
(Section 6 below), beginning with a lead seam parcel that adds
tier/claim accounting, the control-9 split, new signature classes and
vector/board shapes, and their negative controls — with zero new
semantics and the Tier 1 gates byte-identical. Workload-independent
Tier 2 items (9.6 min/max, 9.7 payload get/set, dynamic-rounding
wrapper accessors in `compat/`) may follow as small parcels if SF-1
keeps SF-0 §2.7's order. Everything else — augmented operations,
reductions, each mathematical function — enters only through the
chosen workload, one gated item at a time, each preceded by its
oracle bring-up. The workload choice itself is the lead's, made by
applying Section 5's rubric to the KissFFT and interval-geometry
surveys; this report deliberately does not pre-judge it.

## 1. The current integration map (measured)

All counts below are from `scratch/tier2-architecture/counts.py` and
`tier2_counts.py` (script files, read-only), run 2026-10-27 against
the tree at `32dac7d`.

| surface | today (MEASURED unless tagged) |
|---|---|
| tables | `tables/formats.tsv` (3 formats), `tables/operations.tsv` (81 families), `tables/implemented.tsv` (783 rows) |
| generation | `tools/gen_tables.py` (543 lines) -> `include/muse_softfloat.h` (118,150 B), `src/msf_formats.h`, `tests/msf_dispatch.h` (301,252 B), `docs/COVERAGE.tsv` (783 rows); drift check in every budget |
| authorities in COVERAGE | berkeley 117, mpfr-exact 390, project-exact 165, project-exact+berkeley-check 111; 0 unconfirmed |
| comparison rules | `exact` 543, `exact-invalid-project-rule` 240 (integer conversions); runner implements exact / nan-class / berkeley-int via `# compare=` directives, printed per file |
| waves | 0: 63, 1: 346, 2: 362, 3: 12 instantiations; status all implemented |
| dispatch | 765 of 783 vector-replayable; non-replayable = 12 char + 6 flag_op; planned ops would carry NULL and be reported not-implemented BY NAME |
| vectors | 33 committed files, 85,148 lines; provenance tag is the last field; runner provenance table cap 128 (overflow refuses; raised from 32 at the Wave 3 merge after silent drops were caught) |
| budgets | smoke ~15 s, standard ~60 s (smoke + 1,117,504 generated vectors), board ~20 s + builds, bench skeleton ~75 s (AGENTS.md, measured 2026-10-26 under load; not re-run by this study) |
| core | `src/msf16.c` 866, `msf32.c` 914, `msf64.c` 956, `msf_string.c` 1,228 lines + shared `msf_wide.c`, `msf_roundpack.c`, `msf_flags.c`; type scan refuses the words float/double in `src/`+`include/`; symbol scan refuses FP helper symbols in target objects |
| source lists (3 copies) | `tools/run.sh` `SRC=` (line 37), `board/run_board.sh` host build (lines 19-21), `board/CMakeLists.txt` `MSF_SRC` — a new core TU must be added in all three or gates disagree about what the library is |
| compat | `compat/msf_wrap.{c,h}`: per-core state `g_state[2]` via `get_core_num()`, bit casts, copysign wraps. `compat/msf_aeabi.{c,h}`: binary64 AEABI surface over msf64 + named libm traps |
| board | harness protocol v1 (`I`/`Z`/`H`, vector lines, `R` replies, whole-run SHA-256); hello proves --wrap + per-core/IRQ state contract (12/12); AEABI selftest 47,107 checks; board-smoke set is generated fresh per run (stride sample of directed encodings + pack cases), not a subsample of committed vectors |
| board samples so far | 968 (P0), 2,767 (Wave 1), 2,489 (Wave 2/3) vectors, host hash == board hash each time |
| IAS15 anchors | ~13,100 binary64 ops/step at N=3 (host census 13,062 counted libcalls/step); 1.58 accepted steps/s on silicon at 125 MHz; firmware .text 139,560 B, .bss 35,720 B (arena 20,464 B required at NMAX 16); stack 4 KiB (8 KiB refused by SCRATCH_Y); host soft build 53x the native build's wall time (host only) |

Two structural notes the table cannot show. First, coverage is per
instantiation and status/wave consistency is asserted inside
`gen_tables.py` itself (`implemented.tsv` wave must equal the computed
wave; unknown or duplicate rows abort generation). Any new accounting
column inherits that enforcement only if `gen_tables.py` is taught to
check it. Second, the public header's fixed prelude (types, the
four-value `msf_rounding_t`, flag bits, spec structs) lives inside
`gen_tables.py` as `HEADER_PRELUDE`, so even "just add an enum value"
is a generator change that regenerates four files.

## 2. API and state design: what belongs where

Placement vocabulary follows the existing tree: **core** =
`include/muse_softfloat.h` + `src/` (pure, bit containers, explicit
rounding/flags, no allocation, no globals); **compat** = `compat/`
(per-core state, C arithmetic types, AEABI/libm interposition);
**workload** = the separate program outside the library tree (the
REBOUND/IAS15 precedent: scratch-side, its own licence, consumes the
library through compat or the core API); **nowhere** = refused.

| Tier 2 item (SF-0 §2.7 order) | placement | proposed shape | notes |
|---|---|---|---|
| 9.6 minimum/maximum family | core | new homogeneous binary sig, e.g. `msf64_minimum(msf64_t a, msf64_t b, msf_flags_t *flags)` per named op; 3 instantiations each | mechanically the `remainder`/`sign_bin` shape, but give it its own sig name so COVERAGE reads honestly. Whether each named op takes flags (signaling-NaN behaviour) is clause9's semantic call; the table's flags column already expresses either answer per family. Fits today's dispatch unchanged. formatOf (27/op) refused until earned |
| 9.7 NaN payload get/set | core | homogeneous unary/binary sigs over bit containers; 3 instantiations each | open type question for SF-1 (payload carried as same-format pattern vs integer) — the table needs the answer before sig design; see decision D4. Must be specified against the SF-0 §2.5 NaN matrix (default qNaN, quiet-bit polarity, truncation-to-infinity rule) so get/set cannot mint a non-canonical result the rest of the core would not deliver |
| dynamic rounding get/set wrappers | compat only | accessors over the existing `msf_wrap_state()` (which already holds `rounding`; zero-init = ties-to-even because the enum is 0) | zero core change. The SF-0 §3.4 contract already covers per-core sharing, IRQ interleaving, and save/restore duty. Evidence is hello-style selftest lines, not vectors. A `<fenv.h>`-lookalike API in the core header is refused (SF-0 §3.3 is explicit) |
| `roundTiesToAway` as a dynamic attribute | compat first; core enum only by SF-1 ruling | if core: `MSF_ROUND_TIES_TO_AWAY = 4` (the internal enum already uses 4 and `msf_pack_generic` implements it) | the cheap-looking change is the expensive one: every `attr` operation's semantics and vector matrix grow from 4 modes to 5 (249 attr instantiations today), Berkeley's dynamic modes do not include ties-to-away and neither does the fenced host FPU, so the whole fifth column is MPFR/project-exact work. Do not let a wrapper need quietly reprice all of Tier 1; decision D3 |
| public `roundToOdd`-style helper | nowhere public; internal only if a math parcel needs it | `src/msf_internal.h` internal rounding value, like ties-to-away today | an internal helper needs kernel-level vectors (the `internal.pack*` precedent) but no COVERAGE row and no claim. A public helper is a new operation family and must earn its own gate like any other |
| augmented addition/subtraction/multiplication | core, new two-result sig | recommend a per-format pair struct in the generated prelude, e.g. `msf64_pair_t { msf64_t head, tail; }` returned by value: `msf64_pair_t msf64_aug_add(msf64_t a, msf64_t b, msf_flags_t *flags)` (rounding-attribute presence is clause9's call; both shapes are costed in Section 3) | struct return keeps the no-allocation, no-aliasing-surprise core style and cannot be half-consumed. Costs a new sig class, a two-result dispatch trampoline, vector shape, and board reply (Section 3). 3 ops x 3 formats = 9 instantiations homogeneous; 81 if formatOf-shaped — refuse the latter |
| reduction operations (sum, dot product, scaled variants) | nowhere as library conformance operations; workload-local helpers if needed | if a workload needs one, it writes it over core ops in its own tree, under its own claim | SF-0 §2.7 already limits reductions to exception discipline with implementation-defined numerics — there is no bit-exact claim to gate, and the array+length signature breaks dispatch, vectors, and the board line all at once. Putting an unclaimable family in COVERAGE next to 783 exact rows is exactly the claim-dilution risk. If SF-1 wants flag-discipline-only rows, they need their own claim level and a sequence-shaped gate (Section 3), and should be counted separately from any headline number; decision D5 |
| Clause 9 mathematical functions | core, one function at a time | homogeneous unary/binary sigs reusing existing shapes (3 instantiations per unary function); new TU per function family vs additions to per-format TUs — decision D6 | fits today's dispatch and vector shape; the difficulty is entirely oracle and hardest-case evidence (clause9's survey), plus RP2040 table/stack costs (Section 4). Each function that graduates also retires exactly one named trap in `compat/msf_aeabi.c` |
| stateful duplicates of the whole core API (implicit rounding/flags) | nowhere | — | a second semantics surface. Compat already provides the stateful C-operator path through AEABI/libm names; anything more doubles the evidence burden for zero conformance gain |

Preserving the pure core is mostly a matter of refusing three
temptations: no default-rounding overloads in the public header (the
header comment "Rounding is an explicit argument, never process
state" is a load-bearing sentence), no allocation-taking signatures
(array reductions, string-returning helpers) in `src/`, and no new
global or per-core state in `src/` — the type scan and symbol scan
will not catch a global, so SF-1 briefs must name it as a refusal and
verifiers must grep for it (today's core static RAM is zero by SF-0
§8 budget; the wrapper's `g_state[2]` is counted in compat).

## 3. Table generation, claim levels, and vector shapes

### 3.1 Growing operations.tsv

- **New columns, not overloaded strings.** Add `tier` (1|2) and
  `claim` to `tables/operations.tsv`, propagated by `gen_tables.py`
  into `docs/COVERAGE.tsv` and asserted there (generation aborts on
  an unknown claim token, the same way unknown sig classes abort
  today). All 81 Tier 1 families take `tier=1`; their claim value is
  a single new token meaning the SF-0 required-set claim, so the
  regeneration diff for Tier 1 rows is purely additive columns.
  Encoding tier or claim inside the existing `authority` or
  `comparison` free-text is refused: the runner never reads COVERAGE,
  and free text is how a weaker claim hides beside exact rows.
- **Claim levels** (names are SF-1's to freeze; the set must stay
  closed): (a) the Tier 1 required claim; (b) Tier 2 conforming —
  recommended-operation semantics, exact comparison, named authority,
  same gate discipline as Tier 1; (c) Tier 2 bounded — ULP-budgeted
  approximation, claimable **only** when the runner can machine-check
  the bound (below); (d) Tier 2 discipline-only — exception behaviour
  gated, numerics implementation-defined (the reductions case), never
  summed into a conformance headline. SF-0 §2.7's third label,
  "API-compatible only", should not get COVERAGE rows at all: a name
  that merely compiles belongs in compat documentation, not in the
  coverage ledger.
- **Authorities stay a closed token set.** Today's tokens (`berkeley`,
  `mpfr-exact`, `project-exact`, `project-exact+berkeley-check`, and
  the `auto-arith`/`auto-int` expanders documented in
  `gen_tables.py`) cover min/max and payloads plausibly (project-exact
  over bit decoding, Berkeley cross-check only where its headers
  actually declare the family — clause9 checks this). Mathematical
  functions need at most one new token for a CORE-MATH-class foreign
  oracle (executed, never read for design), added to the generator's
  docstring with its fetch pin. An instantiation whose deciding
  authority is the host libm of the day is refused by name: this
  project has already measured a host library `sqrt` that is 1 ulp
  wrong (AGENTS.md, ias15-port).
- **Wave numbering.** Use wave 4 (the metrics rows for this study
  round already say `wave4`). `wave_of()`'s binary16 deferral
  applies only to wave-1 rows, so a wave-4 family stays wave 4 for
  all formats; if SF-1 wants binary16 instantiations of a Tier 2
  family deferred, that is a deliberate generator rule change, not
  an accident of copying the wave-1 pattern.
- **Control 9 split.** Replace the single equality with two printed
  invariants: Tier 1 implemented == Tier 1 total (783, refusing any
  regression or silent renumbering), and Tier 2 implemented/planned
  counts printed with planned rows named. The runner already prints
  "skips are not passes" and fails a zero-pass run; the seam parcel
  must watch the new control fail both ways (a planted un-implement
  of a Tier 1 row; a Tier 2 row silently deleted instead of
  implemented) before it is trusted, per SF-0 §5.2's rule.
- **Generated-surface cost per family** (COMPUTED): one header decl +
  one dispatch row (+ trampoline when replayable) + one COVERAGE row
  per instantiation. At 783 instantiations the dispatch is 301 KB /
  1,629 lines; each homogeneous Tier 2 family adds ~3 of each, each
  formatOf binary family ~27. The drift check makes this safe but
  not free: every seam regeneration is a tree-wide diff that
  verifiers must re-derive, which is why table changes stay
  lead-owned and batched at wave boundaries, as in Waves 1-3.

### 3.2 New vector shapes

The current public shape is `<op> <rm> <args...> -> <result> <flags>
<provenance>` with two existing escapes: `internal.pack*` kernel
lines and the Wave 3 character shapes (`IN=`/`A=`/`SPEC=`/`OUT=`/
`LEN=`/`C=`, canary-buffer checks). Three Tier 2 shapes need rulings:

1. **Multi-result (augmented).** Extend, do not overload:
   `<op> <rm> a b -> hi lo <flags> <prov>`. Consequences, all
   mechanical but all required: a second retkind in `msf_op_desc_t`
   (or a PAIR kind), a two-`uint64` trampoline ABI beside
   `msf_call_fn`, a per-sig token-count rule in `runner.c` (today's
   formula is global), a canonical hash line carrying both results,
   and a board `R hi lo flags` reply under a bumped harness version.
   Comparison stays exact on both results and flags — an augmented
   op whose tail is "approximately the error term" is a different,
   weaker operation and must not share the name. Provenance remains
   the last field, so `run.sh`'s expect-counts (`$NF`) keeps working.
2. **Stateful wrappers (dynamic rounding).** Not vector-replayable,
   by design. The flag-op precedent is the model: an exhaustive
   state-machine test in runner `unit` mode (setter/getter over all
   attribute values including out-of-range values, save/restore
   interplay), plus hello-style on-silicon checks for per-core
   isolation and same-core IRQ sharing. Refuse any design that
   makes the vector runner carry hidden state between lines — the
   whole-run hash and board replay both assume line independence.
3. **Mathematical functions.** The existing shape fits (unary/binary
   homogeneous). The new work is comparison machinery, not syntax:
   a bounded claim needs a runner mode that computes ULP distance in
   the result format (handling NaN/inf/zero classes explicitly) and
   prints the bound it enforced, the same way `nan-class` and
   `berkeley-int` masking is printed today. Until that mode exists
   and has been watched refusing an out-of-bound result, only exact
   (correctly rounded) claims can close a gate. Hardest-case vector
   volume must stream generate-and-replay with seeds recorded, per
   SF-0 §4.3/§6 — the P0 slip that wrote 3.4 GB of vector files is
   the standing warning, and Berkeley level-2 pricing (40,284,288
   cases for one binary-op slice) is the scale to budget against.

### 3.3 Provenance caps and budget growth

Measured today: 85,148 committed vectors, 33 files, smoke ~15 s;
standard adds 1,117,504 generated vectors (917,504 exhaustive-f16 +
200,000 seeded pack sweep) for ~60 s total; board samples of
1-3k vectors. Hard caps already in the tree: provenance tags ≤ 128
(runner refuses beyond), tag ≤ 63 chars, tokens ≤ 16 per line, host
line buffer 4,096 B, board line buffer 512 B, hash line 256 B.

Growth rules SF-1 should state as numbers, not intentions:

- smoke keeps only directed/committed sets and stays within ~2x
  today's vector count and wall time; exhaustive or streamed sets
  belong to standard. A Tier 2 family whose only honest gate is
  exhaustive-f32-scale (4 billion cases) cannot be a smoke citizen.
- each parcel introduces at most a handful of new provenance tags,
  each naming generator + oracle + seed policy in `tests/VECTORS.md`
  at merge; the 128 cap is raised only by a seam change that also
  re-watches the overflow refusal.
- board budget grows by sample design, not by replaying smoke: the
  board-smoke generator gains a Tier 2 section with the same stride
  sampling, keeping the replay in the low thousands of lines, and
  the sample's generation is priced before the parcel briefs are
  written.
- binary16 exhaustiveness is the cheap superpower (65,536 unary
  encodings already run in standard); SF-1 should require exhaustive
  binary16 for every Tier 2 unary family where the authority can
  decide all encodings, and treat binary32/binary64 evidence as
  directed + seeded + hardest-case, never implied by the f16 sweep.

## 4. RP2040 evidence: ABI surface, costs, and what bit-compares

Everything quantitative here reuses IAS15's measured numbers
(RECORD Waves 2-3; `ledger/ias15-port.md`, `ledger/ias15-pico.md`);
no board rate is invented. Extrapolations are marked BELIEVED.

- **Interposition surface today is binary64-only, by measurement.**
  The AEABI census (arm-none-eabi-gcc 14.2.1, cortex-m0plus,
  soft-float ABI) found the compiler emits boolean `__aeabi_dcmp*`
  helpers only — no condition-code family — and `compat/` wraps
  dadd/dsub/dmul/ddiv/drsub/dneg, six compares, i32/u32/i64/u64
  conversions both ways, f2d/d2f, plus libm `sqrt`/`fabs`/`fma` and
  copysign from P0. Everything else libm-shaped (38 named functions)
  is a loud trap in `msf_aeabi.c`. That trap list is the Tier 2
  graduation path: each earned mathematical function retires exactly
  one trap into a `--wrap` over a gated core op, with a final-ELF
  undefined-symbol census (the ias15-pico Gate F precedent) proving
  no unwrapped body remains. A workload using binary32 arithmetic
  through C operators needs its own `__aeabi_f*` census first — none
  exists today (ias15-pico correction 3 scoped traps to double/libm
  names) — and a workload calling the core API directly needs no
  AEABI work at all. Which of those postures a candidate takes is
  therefore a first-order architecture cost, and each workload
  survey must state it.
- **The SDK flavour work is still owed.** `board/CMakeLists.txt`
  selects the empty `compiler` float/double flavour per target and
  applies `--wrap` from this project; the full pico-sdk drop-in
  flavour library SF-0 §3.4 item 2 describes was not built (the
  CMake comment still says "Wave 3 registers a full flavour").
  Tier 2 does not need it unless a workload requires SDK-internal
  floating point to change behaviour; SF-1 should say so explicitly
  rather than letting it reappear as scope.
- **errno and friends.** The compat header already documents that
  wrapped `sqrt`/`fma` do not set `errno` and flags accumulate in
  per-core state instead. Graduating more libm names keeps that
  contract or changes it in writing; a workload that reads `errno`
  or `fetestexcept` after a call is asking for a different compat
  claim and must say so in its survey.
- **Per-core dynamic state already exists and is already gated.**
  `msf_wrap_state()` returns `g_state[get_core_num() & 1]`; the
  hello firmware proves cross-core isolation, same-core IRQ sharing
  (flags `0x12` observed after IRQ), and save/restore round-trips on
  silicon. Dynamic rounding get/set adds accessors to a field that
  is already there; the new silicon evidence needed is the same
  three checks with a directed-rounding-sensitive operation, e.g.
  proving core 1's ties-to-even sum differs from core 0's
  toward-positive sum on a directed case while neither leaks into
  the other. What must not happen: the core library acquiring a
  "current rounding mode" — the board harness and runner pass `rm`
  per line precisely so no state can leak between vectors.
- **Cost anchors (MEASURED).** Mixed binary64 throughput implied by
  IAS15 on silicon: ~13,100 ops/step x 1.58 steps/s at 125 MHz is
  about 20,700 wrapped core ops/s (COMPUTED; mix is add/sub/mul/div
  with ~0.4% sqrt, from the host census 7.23M/7.10M/8.85M/2.84M/
  0.105M over 2,000 steps). At that rate 1e6 binary64 ops take
  roughly 48 s and 1e7 roughly 8 minutes on the board (BELIEVED
  extrapolation; a transcendental-heavy mix will be slower per op,
  a binary32 mix faster — each survey must decompose its own op mix
  and re-derive, not quote these two numbers flat). Board step
  stack: 816 B + 288 B measured for IAS15, 4 KiB stack set, 8 KiB
  refused by SCRATCH_Y — any Tier 2 kernel with large constant
  tables must put them in flash (const) and any deep recursion or
  large stack arrays are a design smell to catch at brief time.
  Flash: the full IAS15 firmware text is 139,560 B and the harness
  UF2 is 167,424 B against a 2 MB part, so code size is not the
  binding constraint until a mathematical function brings big
  tables; SF-0 §8 already requires per-format flash accounting from
  the linker map, and SF-1 should extend it per function. SRAM is
  264 KB total; IAS15's arena formula (1,176 B/particle + particle
  storage; N=100 fits, N=200 does not) is the worked example of a
  budget done before coding.
- **What can be bit-compared host-vs-board.** Today: every
  dispatch-replayable instantiation (765) and the `internal.pack*`
  kernel lines, via per-line result+flags and the whole-run SHA-256
  over the canonical line both sides build identically. After the
  seam: two-result lines join that set under harness version 2
  (banner string bump; `host_replay.py` width logic today infers
  width from the op-name prefix and compares only the first result
  token — both must be taught the new shape, and the old harness
  must refuse new lines rather than misparse them). Stateful
  wrappers bit-compare only as selftest verdict lines (counts of
  checks), never as vectors. Mathematical functions bit-compare
  exactly like arithmetic — that is their architectural advantage —
  provided their input sample is chosen so the board run finishes:
  CDC replay is line-at-a-time request/response, so sample size,
  not per-op cost, has bounded every board budget so far, but a
  sample of hardest-to-round binary64 cases is also the slowest
  per line and must be priced on the host first.
- **Host-only evidence is a claim decision, not a shortcut.** Wave 3
  accepted host-gated string rows because the CDC protocol is
  numeric-only, and the record says so in plain words. If any Tier 2
  shape is proposed as host-only, SF-1 must name which shapes, why,
  and what the board claim then excludes — before parcels are
  briefed, not in a closing report.

## 5. The workload-earning rubric

Owner direction (lead ledger 2026-10-27 13:54 -0700): Tier 2
continues only with another scientific workload that *earns* the
additions. Each criterion below is stated so that a survey can fail
it with evidence. **R1-R6 are gates: any one failure rejects the
workload (or that addition within it). R7-R8 rank the survivors.**
The rubric is candidate-neutral; nothing in it mentions either
named candidate's domain.

| # | criterion | evidence that passes it | it fails if |
|---|---|---|---|
| R1 | addition is load-bearing | for each claimed addition: a named executed call path in the unmodified (or extraction-pinned) workload, an op census showing it runs (static + dynamic where practical), and a remove-it experiment — trap or stub the addition and the workload's compared output changes or stops | the addition is never executed, executes only in dead branches/configurations the demo does not use, or removing it leaves every compared output bit-identical |
| R2 | cannot be pinned away | a written pinning attempt: constants/tables/twiddles carried as verified hex bit patterns (the IAS15 coefficient precedent), precomputation on the host, or restriction to existing Tier 1 ops — showing the honest demo definition still needs runtime evaluation of the addition on the target | pinning removes the need and the demo's claim survives pinning intact; or the "need" exists only because pinning was declared out of bounds without a reason tied to the demo's scientific claim |
| R3 | oracle is independent | a deciding authority from SF-0 §4's order (standard by clause, pinned Berkeley where it covers the family, MPFR/exact generation, or a pinned foreign correctly-rounded oracle executed in scratch), with fetch provenance (URL, version, archive SHA-256, licence hash) in the `fetches.jsonl` shape, built and self-checked before the parcel that needs it | the only oracle is the implementation itself, the workload's own output, an unpinned host libm (this host's library sqrt is measured 1-ulp wrong), or an oracle whose coverage of the family is asserted but never checked at header/interface level |
| R4 | claim is exact or honestly bounded | the claim level per instantiation declared **before** the parcel (Section 3.1 tokens), matching what the evidence can machine-check: exact bits+flags, a ULP bound the runner computes and prints, an enclosure/containment statement with its theorem named, or host-vs-board bit identity over a named field set — never a tolerance result described as byte identity | the strongest honest statement is "outputs look close", the bound is quoted from a paper instead of enforced by the gate, or directed-rounding/containment claims rest on ties-to-even correct rounding alone |
| R5 | board budget fits | arithmetic from measured anchors: op-mix census x the IAS15-implied rate (~20,700 wrapped binary64 ops/s at 125 MHz, re-derived per mix), RAM by explicit arena-style formula against 264 KB, flash from a trial link or per-function table accounting against 2 MB, stack within the measured 4 KiB posture, and a board sample size the line-at-a-time CDC replay can finish | the budget is an unlabelled guess, needs performance the bench skeleton has never produced, overflows SRAM/stack at the demo's own representative size, or the honest runtime at demo scale defeats the demo (e.g. the visual needs real-time and the measured rate gives a time-lapse — which must then be the stated framing, as IAS15's video does) |
| R6 | licence boundary clean | workload licence identified and compatible with its placement (separate program in scratch/outside the library tree, own notices, like GPL REBOUND beside MIT muse-softfloat); oracle licences recorded; a statement of what third-party source was read and for what (interface facts) vs never used as design input; nothing enters `src/` or `include/` | the workload or an oracle would have to be vendored into the library tree, its licence reaches the MIT library, its implementation is the de-facto design source for a core function, or provenance cannot be pinned to an archive hash |
| R7 | visual/demo value | a smallest demo a viewer can check: a visible difference between the guaranteed/exact result and a naive or bootrom-class baseline, or a hash-lock reveal in the IAS15 style, plus at least one negative control the video or a verifier can actually run (perturbed constant diverges, trap fires, naive path misclassifies) | correctness is invisible in principle (any output looks plausible), the only evidence is a number the demo itself computed, or the visual requires claiming real-time/accuracy properties R4/R5 did not earn |
| R8 | implementation parcel is bounded | instantiation count by the Section 3 arithmetic (homogeneous-first), one TU or one compat file owned per parcel, hand-written line ceiling in the Wave 1-3 range (briefs used 3,000-3,500), a time box, named negative controls, and plantable surfaces (code semantics, flags, committed vectors, generator constants — the four shapes Waves 1-3 planted) | the addition only makes sense as an unbounded family (all of libm, the full formatOf matrix "for completeness"), needs shared-kernel rewrites mid-parcel, or its gate cannot be planted and independently verified within one parcel-verifier cycle |

### 5.1 What each running survey must return for the lead to score it

From study-tier2-kissfft and study-tier2-interval-geometry, per
claimed addition (one row each): executed call path and census
count (R1); pinning attempt and why it fails or succeeds (R2);
deciding oracle and its pin (R3); strongest honest claim sentence,
worded exactly as it would appear in the record, with the comparison
machinery it needs (R4); op-mix/RAM/flash/stack budget at the demo's
representative sizes, measured vs believed labelled (R5); licence
and fetch record, plus the binary32-vs-binary64 AEABI posture from
Section 4 (R6 + Section 4); smallest demo and its negative control
(R7); instantiation count and parcel shape (R8). A survey that
returns a domain-level verdict ("FFT needs trig") without the
per-addition rows has not returned scorable evidence.

From study-tier2-clause9, per SF-0 §2.7 item: the first honest claim
level in Section 3.1's vocabulary, the deciding authority and whether
Berkeley coverage is header-verified, the hardest-case burden for any
correct-rounding claim by format, and the instantiation count under
both homogeneous and formatOf readings where the standard leaves the
choice open. The lead cannot price R3/R4/R8 for any workload until
these rows exist.

### 5.2 Worked falsification examples (generic)

- A workload whose transcendental calls all happen at initialization
  over fixed sizes fails R2 for those functions (pinned tables are
  the honest implementation), however central they look in a static
  symbol list. It may still earn other additions under R1.
- A workload whose correctness property is containment fails R4 if
  its evidence is ties-to-even correct rounding of the scalar
  function; it passes only with directed enclosures and a named
  containment argument checked independently (exact rational or
  MPFR-interval reference).
- A workload comparing board output against the desktop's own libm
  by tolerance fails R3/R4 as a conformance vehicle; reframed as
  "host-vs-board bit identity of the same extracted source over the
  gated core" (the IAS15 definition) it can pass, and the desktop
  libm then decides nothing.
- A workload needing an unmodified upstream binary's behaviour,
  where expression evaluation order or FMA contraction in the
  upstream build is part of the numerics, fails R1/R4 until the
  reference build is pinned exactly as SF-0 §9 pinned IAS15's
  (same source both sides, strict flags, hex-carried constants);
  the measured FMA-contracting control diverging at step 1 is the
  template negative control.

## 6. SF-1 structure and the first gated parcels

### 6.1 SF-1 should mirror SF-0's skeleton

So that nothing SF-0 settled is silently restated: (0) short answers
with the workload decision and its rubric scores; (1) the owner's
words that authorize Tier 2; (2) the Tier 2 contract — items in
SF-0 §2.7 order, each with formats claimed, homogeneous-vs-formatOf
ruling, claim level token, and the exact claim sentence allowed in
the record and video; (3) API/state deltas only (Section 2 placements
as decided); (4) authorities per item with fetch pins and the
disagreement protocol restated by reference; (5) gates — the seam
changes of Section 3, new negative controls by name, budget caps;
(6) the seam parcel, exactly, in the SF-0 §6 style; (7) parcels and
parallelism (below); (8) board — protocol v2, sample design,
per-function flash accounting; (9) the expansion workload definition
with the same pinning discipline as SF-0 §9; (10) metrics rows
(below); (11) what Tier 2 still does not do (binary128, decimal
formats, Clause 8, traps-as-handling, fast-math — plus any workload
addition refused by name); (12) owner questions with
recommendations; (13) sources; (14) send-backs. SF-1 approval
should be recorded the way SF-0's was: whole-study approval plus
any individually corrected items.

### 6.2 Parcel sequence

Order matters more than parallelism; parallel pairs are marked.
Line ceilings and boxes by Wave 1-3 analogy (parcels actually used
34-56 minutes of 300-360-minute boxes, but Tier 2 parcels carry
oracle novelty Tier 1 parcels did not; keep the boxes, expect the
escalations).

0. **Lead seam parcel (no new semantics).** `tier`/`claim` columns +
   generator assertions; control-9 split with both failure
   directions watched; new sig classes *only for the items SF-1 has
   already approved*, with dispatch trampolines, runner token rules
   and hash lines, `tests/VECTORS.md` shapes; ULP comparison mode
   if (and only if) an approved item claims a bound, watched
   refusing an out-of-bound vector; board harness v2 + board-smoke
   Tier 2 section (empty until parcels land); full Tier 1 gates
   re-run with byte-identical results as the acceptance test. This
   parcel is the Tier 1 insurance policy: after it, planned rows
   can exist without breaking smoke, and every later parcel is
   semantics-only.
1. **Oracle bring-up parcel(s)** for whatever SF-1 approves first,
   in the P0-item-5 pattern: pinned fetch into scratch, build
   through the pinned compiler path, header/interface-level
   coverage verification, real vector counts and runtimes priced on
   sampled functions, Berkeley cross-check where both cover a
   family. No parcel may name vectors from an oracle this step has
   not priced. (Parallel with 2.)
2. **Cheap independent Tier 2 (only if SF-1 keeps SF-0 §2.7 order
   ahead of workload-earned items — decision D2).** One parcel:
   9.6 min/max + 9.7 payload get/set, homogeneous, project-exact
   authorities with Berkeley cross-checks where header-verified,
   exhaustive binary16 binary-op samples by the copysign-sample
   precedent (full f16 pairs are 4 billion — seeded pairs plus
   directed encodings, as `copysign.vec` already does). One small
   compat parcel (or the same parcel if SF-1 allows the file
   spread): dynamic rounding get/set over `msf_wrap_state()`, unit
   state-machine extension, hello-style board checks. These two are
   the only Tier 2 items that fit today's dispatch with no new
   shapes beyond a homogeneous sig.
3. **The earned set, one family at a time, in workload-call-path
   order.** Augmented ops as one parcel (all three ops share the
   two-result machinery and exact-error-term oracle design —
   MPFR/exact-integer decides head and tail independently). Each
   mathematical function as its own parcel with its own
   hardest-case evidence; a function parcel that cannot meet its
   declared claim is refused, per SF-0 §2.7, not merged at a weaker
   claim under the same name. Reductions, if SF-1 admits them at
   all, come last and only at discipline-only claim level with the
   sequence gate designed in SF-1 §5.
4. **Workload track (parallel with 3, after its first needed ops
   land), following the ias15-port -> ias15-pico ladder:** host
   feasibility proof with interposition shim and op census;
   extraction with a host equivalence gate against the unmodified
   reference; AEABI/compat additions the final link census demands
   (including a binary32 census if applicable); board firmware
   with selftest-before-hashes; lead-run board budget under
   `board.lock`. The workload consumes conformance evidence, never
   sources it.
5. **Close:** integration `standard` + `board` on the final tree,
   final adherence audit (now standing practice per RECORD),
   RECORD wave entry, video update only over hash evidence that
   exists.

### 6.3 Verification and plant strategy

Unchanged machinery, restated so SF-1 briefs can cite it: Spark
(muse-spark-1.3) verifiers by planted copy, five plants per parcel
spanning code semantics, a flags-only change, a committed-vector
expectation, a generator constant, and one shape specific to the
parcel (for augmented: swap head/tail; for a math function: one
table entry 1 ulp off; for dynamic state: get/set touching the wrong
core's slot). Keys hashed into the ledger before dispatch, grades
into `docs/metrics/plants.jsonl`; Waves 1-3 caught 24 of 25, and the
one miss (generator drift filed benign) is why every Tier 2 brief
must state the byte-identity norm for committed generated sets in
words. Only regressions and wrong answers send work back. Fresh
regater agents for send-backs, since finished agents return
tool-less on follow-up (measured, Wave 1).

New permanent negative controls the seam parcel adds (each watched
failing first): Tier 1 row un-implemented; Tier 2 planned row
silently deleted; two-result vector with results swapped; ULP mode
fed an out-of-bound result (if the mode exists); harness v2 line fed
to v1 logic and vice versa; dynamic-state leak across cores (the
§5.2 wrapper-leak control, extended from flags to rounding);
a trap-graduation control — a workload ELF still referencing an
unwrapped libm/AEABI body must fail its census.

### 6.4 Metrics rows

No new files are needed; the shapes already exist and this study
round is already rowed as `wave4`. SF-1 should require, per parcel:
a `briefs.jsonl` row at dispatch (work, author, base SHA, time box,
line ceiling with `ceiling_text` saying what counts — generated
vectors excluded, as the Wave 1 caveat established);
`corrections.jsonl` and `escalations.jsonl` rows as they happen;
`fetches.jsonl` rows for every new oracle or workload archive
(URL, version, archive SHA-256, licence hash); `plants.jsonl` rows
at grading (never earlier, keys by hash); `passes.jsonl` /
`usage.jsonl` at the record close with the extractor cutoff named.
One addition worth making in `briefs.jsonl` rows for Tier 2: the
claim level the parcel is gated at, inside `ceiling_text` or a new
key — the metrics extractor tolerates extra keys (rows already vary),
and claim level is the number future audits will ask for first.

### 6.5 Stop rules

- A candidate addition failing R1 or R2 at survey or host-proof
  stage stops there; it is recorded as not claimed with the
  remove-it/pinning evidence, and does not ride along "since the
  seam supports it".
- An oracle that cannot be built, pinned, or header-verified stops
  its family (R3); the family does not fall back to host libm or to
  the implementation as its own reference.
- A mathematical function whose hardest-case evidence cannot close
  at its declared claim is refused or explicitly re-briefed at a
  lower claim by SF-1 amendment — never merged silently weaker
  (SF-0 §2.7).
- If the seam parcel cannot keep Tier 1 gates byte-identical, Tier 2
  stops at the seam; the submission is the 783/783 tree, which is
  already complete.
- If the workload's host proof shows the extraction or reference
  pinning cannot be made honest (R4), the workload stops and the
  already-gated library additions stand or fall on their own
  COVERAGE rows — the demo defect does not reach back into the
  library claim.
- Schedule stop: at any checkpoint where remaining work cannot fit
  before 2026-11-04 with verification intact, cut from the end of
  the sequence (workload first, then latest functions), never by
  thinning gates on what remains.

## 7. Risks to Tier 1, mitigations, and refusals

| risk | mechanism (measured where stated) | mitigation / refusal |
|---|---|---|
| generated-surface churn | every table change regenerates 4 files (header 118 KB, dispatch 301 KB, COVERAGE 115 KB); a bad expansion rule silently renames or drops Tier 1 rows | seam parcel acceptance = Tier 1 gates byte-identical; control-9 split pins the 783 count by tier; table edits stay lead-owned and batched; refusals: no parcel edits `gen_tables.py` |
| claim dilution | "783 of 783" is the headline; Tier 2 rows at weaker claims in the same ledger invite a bigger, mushier number ("850 of 860") that reads as conformance | claim tokens per row (§3.1); headline always stated per tier and per claim ("Tier 1: 783/783 required; Tier 2: N conforming, M bounded, K discipline-only"); API-compatible-only names get no COVERAGE rows; RECORD and video scripts name the tier of every number they show |
| runner protocol breakage | runner token formula is global; char shapes already special-cased by name-matching in `runner.c`; a careless third shape can misparse Tier 1 lines or, worse, pass them | per-sig shape table in the seam parcel; Tier 1 vector files unchanged byte-for-byte; manifest + expect-counts already refuse count drift in smoke |
| board protocol breakage | harness v1 infers width from op-name prefix on the host side and compares one result token; new shapes fed to old firmware could compare the wrong thing and pass | version the banner (`MSF-HARNESS 2`), refuse unknown shapes by name on both ends, re-run the Wave 2 sample under v2 and require the historical hash to reproduce for the Tier 1 subset before trusting v2 for Tier 2 lines |
| performance / table blow-up | formatOf defaults (27/op) and fifth-rounding-mode creep (249 attr rows x 5/4 modes) multiply vectors, board sample, and verifier load; Berkeley L2 slices are 40M cases each | homogeneous-first default; dynamic ties-to-away stays compat-side until the repricing is an explicit SF-1 decision (D3); §3.3 numeric growth caps; streamed, seeded generation only |
| licence leakage | a workload or oracle with a strong licence vendored for convenience; a correctly-rounded-function implementation read "for reference" becoming the design | the REBOUND pattern is the ceiling: scratch-side, hash-pinned, own notices, hex-carried tables where data must cross; oracle source executed, not read for design (clause9's brief already states this); fetches rows before parcels; refusal: no third-party source in `src/`/`include/` regardless of licence (SF-0 §4.5 already refuses even BSD-3 Berkeley on policy) |
| schedule before 2026-11-04 | 8 days from this study (2026-10-27) remain in the window KICKOFF names. Waves 1-3 each landed inside a day of wall time, but each rested on a seam and oracles that already existed; Tier 2 needs a new seam, at least one new oracle, a workload extraction, and a board run in series | the §6.2 order front-loads the seam and oracle so the failure mode is "Tier 2 not started", never "Tier 1 reopened"; §6.5 schedule stop cuts from the workload end; the already-complete 783/783 + IAS15 submission is the floor at every point |
| authority disagreement | Tier 2 families are exactly where Berkeley is silent and host libm is wrong; pressure to average or to let vector count outvote the oracle rises with deadline | SF-0 §4.4 restated in SF-1 by reference; the Wave 1 tininess episode (lead kernel and lead reference agreeing wrongly, caught by Berkeley via parcel escalation) is the standing example in every Tier 2 brief |
| verifier overload | planted-copy verification caught 24/25 but costs a full Spark pass per parcel (~46-82 measured minutes per wave) | keep parcels small (R8); batch the two cheap independent items into one parcel (§6.2 item 2); never parallelize more parcels than the lead can plant and grade serially |

Standing refusals SF-1 should carry verbatim from SF-0 §2.7/§11,
unchanged by Tier 2: binary128 and decimal formats, Clause 8
alternate exception handling, traps and resumption, non-IEEE
fast-math and flush-to-zero modes, dynamic allocation and hardware
floating arithmetic in the core, bootrom FP entry points, copied
third-party softfloat source, claims ahead of closed gates, and any
"mostly compliant" label.

## 8. Owner / lead decision list

Recommendations are the survey's; the decisions are not.

- **D1 — which workload (if either).** The lead scores both
  workload surveys against Section 5 once clause9's per-item rows
  exist, and puts one recommendation to the owner. "Neither earns
  its additions; Tier 2 = cheap independent items only, or no
  Tier 2" must remain an available answer; the submission is
  already complete without Tier 2.
- **D2 — SF-0 §2.7 order vs workload-first order.** §2.7's order
  (min/max, payloads, dynamic modes, augmented, reductions, math)
  was written before the workload-earning rule. Recommend: the
  seam first; then the workload's earned set in call-path order;
  min/max + payloads + dynamic wrappers only as slack allows,
  unless the chosen workload earns them under R1, in which case
  they move into the earned set at their call-path position.
- **D3 — dynamic ties-to-away placement.** Recommend compat-side
  (wrapper state value only) at first; a core `MSF_ROUND_...=4`
  enum addition only with an explicit SF-1 ruling that prices the
  fifth mode across all 249 attribute-taking instantiations and
  names its authority (MPFR/project-exact; neither Berkeley dynamic
  modes nor host SSE2 decide it).
- **D4 — payload get/set operand type** (same-format floating
  pattern vs integer payload), and its interaction with the SF-0
  §2.5 NaN matrix. Needs clause9's reading; the table cannot be
  written before it.
- **D5 — reductions admitted at all?** Recommend nowhere in the
  library; workload-local if needed. If admitted: discipline-only
  claim token, separate headline counting, and a sequence-shaped
  gate designed in SF-1 §5 before any parcel.
- **D6 — mathematical-function TU placement.** Per-format files
  (`msf16/32/64.c` growth) keep the house structure but make every
  function a three-file diff across files Tier 1 verifiers already
  closed; new per-family TUs keep Tier 1 files byte-stable but add
  entries to the three source lists (§1). Recommend new TU(s) for
  math functions (Tier 1 diff = 0 is worth more than symmetry);
  min/max, payloads, and augmented ops follow the per-format
  pattern since they are thin over existing decode/compare kernels.
- **D7 — first mathematical function and formats claimed.** Clause9
  ranks candidates; the architectural constraint to add: claim
  binary16 first where exhaustiveness makes the gate cheapest and
  strongest, and do not let a workload's binary64 need silently
  commit to binary64 correct rounding before its hardest-case
  burden is priced (R3/R4/R8).
- **D8 — host-only board evidence.** Which Tier 2 shapes, if any,
  may be host-gated like the Wave 3 string rows, and the exact
  record sentence that says so. Recommend: none by default —
  stateful wrappers excepted (selftest-verdict evidence), since
  on-silicon bit identity is this project's differentiator.
- **D9 — claim-token vocabulary and headline format** (§3.1, §7),
  including whether bounded (ULP) claims are admitted at all
  before 2026-11-04 given the runner mode they require.
  Recommend exact-only for anything merged in the hackathon
  window; bounded claims after only, with the ULP runner mode as
  its own gated seam work.
- **D10 — SDK flavour completion.** Confirm out of Tier 2 scope
  (§4) unless the chosen workload needs SDK-internal FP
  behaviour changed.

## 9. Evidence, gaps, and what was not done

READ in full: the brief; `ledger/README.md`; repo `AGENTS.md`;
`docs/studies/SF-0.md` (whole file; §2.7, 3, 4, 5, 7-9 load-bearing);
`docs/RECORD.md`; `docs/BOARD.md`; `tables/formats.tsv`,
`tables/operations.tsv`; `tools/gen_tables.py`; `tools/run.sh`;
`tests/runner.c`; `tests/VECTORS.md`; `compat/` (4 files);
`src/msf_internal.h`, `src/msf_flags.c`; `board/harness_main.c`,
`board/host_replay.py`, `board/CMakeLists.txt`, `board/run_board.sh`;
sibling briefs (`tier2-clause9`, `tier2-kissfft`,
`tier2-interval-geometry`); `ledger/ias15-port.md`,
`ledger/ias15-pico.md`; the lead's Tier 2 dispatch entries and the
three sibling survey-plan entries. READ in part: `tests/gen_vectors.py`
(board-smoke mode), `board/hello_main.c` and `board/bench_main.c`
(structure and checks), `docs/metrics/*.jsonl` (shapes and tail rows).

MEASURED by script (`scratch/tier2-architecture/counts.py`,
`tier2_counts.py`, outputs reproduced in §§1, 3, 4): family/
instantiation/authority/wave/comparison counts from the tables
through the real `gen_tables.instantiate()`; replayable count 765;
committed vector files and lines; generated-file sizes; metrics
JSONL row counts and keys; base-diff (`54e4bff..32dac7d` = 4 lines in
`docs/metrics/briefs.jsonl`); clean tree. COMPUTED: per-family
instantiation costs under each sig shape; the IAS15-implied board
ops/s and its extrapolations (labelled BELIEVED where used).

Not done, deliberately or by scope: `tools/run.sh` was **not**
re-run (it writes into `muse-softfloat/build/`; this study is
read-only on the repo, and RECORD/AGENTS timings are cited as their
runs' facts, not re-measured). The board was not touched and no COM
port opened. The generated header and dispatch were studied through
their generator, not read line-by-line (118 KB / 301 KB of generated
text; the generator is the source of truth and the drift check binds
them). S1/S2 scratch survey reports were not re-read — clause
semantics and oracle internals are study-tier2-clause9's remit, and
this report cites SF-0's distillation of them. Bench numbers were
not produced (`bench` is a skeleton and never a correctness or
performance claim). Per-format core sources were sampled for
rounding-mode handling, not audited line-by-line; a D3 ruling in
favour of a core fifth mode would need that audit as parcel work.
IEEE 754-2019 is cited by clause through SF-0/S1 only; the PDF was
not opened.
