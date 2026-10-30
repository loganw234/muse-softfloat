# SF-0 evidence audit — what S1–S4 actually support

Auditor: sf0-evidence-auditor (read-only). Date of audit: 2026-10-26.
Brief: audit `scratch/S1/report.md`, `scratch/S2/report.md`,
`scratch/S3/report.md`, `scratch/S4/report.md` against
`softfloat-bootstrap-kit/WORKFLOW.md` Phase 2 ("the study, the plan of
record") and `softfloat-bootstrap-kit/PROJECT.md`'s nine questions, after
reading `ledger/README.md` and `ledger/lead.md`.

Inputs actually read for this audit: the two ledger files named in the
brief; `softfloat-bootstrap-kit/WORKFLOW.md`; `softfloat-bootstrap-kit/PROJECT.md`;
the four survey reports in full; `ledger/S1.md`–`ledger/S4.md` as ledger
context (per `ledger/README.md` "Read every file in the directory");
`softfloat-bootstrap-kit/OWNER.md`, `METRICS.md`, `BOARD.md`, and
`tools/ledger.sh` for the Phase 2 dimensions they define. No other scratch
was opened. Nothing with `cft` in its name was opened, searched inside, or
listed. No repository file was edited by this audit; this report and one
ledger entry are its only writes.

Citation form: `S1 §1.2, lines 119–131` means section 1.2 of
`scratch/S1/report.md` at those line numbers as read this run. Survey tags
are preserved: **READ** (read in a primary source), **MEASURED** (executed
on this host this run), **BELIEVED** (surveyor inference). Where this audit
infers, it says **AUDIT INFERENCE**.

WORKFLOW Phase 2 requires SF-0 to cover, verbatim in substance
(`WORKFLOW.md` lines 50–60): PROJECT's questions each with the lead's
proposal as a question to Logan; the authority and the oracles; refusals;
the gates and their negative controls; P0's contents; the parcels and the
waves (owned files, time box, scope ceiling each); and how metrics are
captured. Section 1 below maps evidence decision by decision. Sections
2–5 give the qualifications, oracle gaps, P0/board constraints, and Tier 2
risks the brief asked for.

**Terminology warning (AUDIT INFERENCE).** The brief's phrase "expanded
IEEE 754 Tier 2 scope" is not defined in `WORKFLOW.md`, `PROJECT.md`, or
any of S1–S4. Section 5 defines it explicitly from survey evidence so SF-0
does not inherit an undefined scope noun. If the lead means something
else by Tier 2, SF-0 must say so before any parcel is sized against it.

## 1. Decision-by-decision evidence matrix

Each row states: the decision SF-0 must put to Logan, what the surveys
support (with exact citations), what remains undecided or unmeasured, and
the audit's judgement on whether the surveys are sufficient to propose.
"Sufficient to propose" means the lead can write a proposal + alternative
for Logan without new survey work; it never means the decision is already
made.

### Q1 — Edition: IEEE 754-2019 or 2008 (PROJECT Q1)

- Supported for 2019: S1 is a direct READ survey of the owner's
  `754-2019.pdf` (S1 header, lines 1–9; normative vocabulary READ Clause
  1.6, lines 19–21; scope caveat READ Clauses 1.5/3.1, lines 22–27). The
  edition-decisive fact is READ twice: 2008 `minNum`/`maxNum` no longer
  exist in Clause 5 and were replaced by recommended Clause 9.6
  operations (S1 §1.1, lines 112–115; S1 §5, lines 419–425), restated as
  brief correction 1 (S1 lines 501–506). The 2019 version predicates
  `is754version1985/2008/2019` are themselves required operations (S1
  §1.6, lines 217–218).
- Oracle consequence: S2's Berkeley authority is frozen at Release 3e
  (2018-01-20) for both SoftFloat and TestFloat (S2 §1.1, lines 51–58)
  and covers the 1985 core + FMA; absence of most post-1985 operations
  (2019 min/max family, augmented arithmetic named) is only **BELIEVED**
  from a mirror README snippet, with an explicit "verify against
  754-2019 clause list at SF-0" (S2 §1.3, lines 128–132). S2 brief
  correction 6 repeats the warning: "passes TestFloat level 2" must
  never be phrased as "IEEE 754-2019 conformant" (S2 lines 645–649).
- Unsurveyed: no parcel read 754-2008. There is no evidence base for a
  2008 conformance surface (2008 Clause 5 min/max semantics, 2008
  decimal/hex wording) beyond S1's backward references. S3 and S4 are
  edition-agnostic (S3 surveys ROM/SDK deviation, S4 surveys a binary64
  workload assuming RN defaults).
- Judgement: **sufficient to propose 2019; insufficient to propose 2008**
  without new survey. SF-0 must state the edition in every conformance
  sentence. An unqualified "IEEE-754 compliant" claim would smuggle the
  edition decision past Logan.

### Q2 — Formats: arithmetic vs interchange per binary16/32/64; Clause 9 in or out (PROJECT Q2)

- Format status (READ): five basic formats are binary32/64/128 + two
  decimal; **binary16 is not a basic format**, defined only as a 16-bit
  binary interchange format (S1 §0, lines 34–37, MEASURED string search).
  Any format *can* be supported as arithmetic; arithmetic and interchange
  statuses are independent choices (S1 §0, lines 38–40). Binary-radix
  conformance requires at least one of binary32/64/128 as **both**
  arithmetic and interchange; binary16 can never be the only basis (S1
  §0, lines 41–44). Parameters `k/p/emax/emin/w/t/bias` for all three
  formats are READ from Table 3.5 (S1 §0, lines 45–51). Conformance
  hooks: any supported format needs initialize + conversions to all other
  supported formats; a supported arithmetic format needs **all** Clause 5
  operations; a supported interchange format needs Clause 3 encoding
  read/write (S1 §0, lines 58–62).
- Clause 5 surface if all three are arithmetic (READ 5.1, S1 §1, lines
  70–77): S1 tallies **81 distinct operation names** for a binary
  arithmetic format by enumerating the `shall provide` lists in 5.3–5.7,
  with only the comparison count (22) and Table 9.1 count (39)
  script-verified (S1 §1, lines 79–81; Evidence index, lines 492–493).
  Critically, S1 warns the *instantiation* surface is larger:
  `formatOf` operations for every destination × same-radix source (5.4.1),
  `convertFormat` for every ordered pair (5.4.2), integer conversions
  for every supported integer format (5.4.1, 5.8); "the per-name
  instantiations, not the 81-name count, are the true conformance
  surface" is **BELIEVED** by S1 (S1 §1, lines 82–87).
- Required families SF-0 must not undersize (all READ in S1 §1):
  homogeneous `roundToIntegral*` (6 incl. ties-to-away *operation*),
  `nextUp`/`nextDown`, `remainder`, `scaleB`/`logB` (lines 94–110);
  `formatOf` `addition/subtraction/multiplication/division/squareRoot/
  fusedMultiplyAdd/convertFromInt` — **FMA required, single-rounding,
  explicitly not multiply-then-add** (lines 119–126, 514–516); ten
  `convertToInteger*`/`convertToIntegerExact*` variants (lines 133–139);
  `convertFormat` + decimal-character conversions (lines 143–150);
  hex-character conversions with a recorded shall/should tension (lines
  152–158); digit/round-trip obligations `Pmin` 5/9/17 and `H >= M+3`
  (lines 160–186; BELIEVED consequence `M=17`, `H>=20` for a
  binary16+32+64 set, lines 171–172); quiet sign ops `copy/negate/abs/
  copySign` (lines 189–194); 22 comparison predicates + `totalOrder/
  totalOrderMag` (lines 198–213); version predicates, 11 classification
  ops, 6 flag ops (lines 217–230). S1 brief correction 4 lists the
  easily-missed subset explicitly (S1 lines 517–521).
- Decimal/hex character conversions are **inside** Clause 5 for an
  arithmetic format, not an optional extra (S1 §1.3, lines 141–186).
  PROJECT Q2 already flags them as "a large piece of work"; S1 quantifies
  why (correct rounding for digit counts 1..H both directions with flags,
  lines 165–170). Any SF-0 that proposes binary32/64 as arithmetic
  formats while deferring decimal conversion without a refusal is
  proposing a partial conformance claim and must label it so.
- Clause 9 recommended set (READ headnote: Clause 5 completely specifies
  the required operations; Clause 9 is recommended, but a conforming
  version of any Clause 9 operation **shall** meet 9.1–9.2 accuracy/
  exception rules incl. correct rounding) (S1 §5, lines 388–394).
  Itemised: 39 Table 9.1 mathematical operations (lines 398–405);
  9.3 dynamic-mode get/set (lines 406–410); 9.4 seven reduction ops with
  implementation-defined approximated results (lines 411–414); 9.5 three
  augmented ops under a clause-local rounding (lines 415–418); 9.6 eight
  min/max ops, the 2008 replacement family (lines 419–425); 9.7 three
  payload ops (lines 426–428). S1 **BELIEVED**: "nothing in a minimal
  conformance claim needs any of Section 5" and Table 9.1 correct
  rounding is "far harder than the Clause 5 core" (lines 430–431).
- binary16 interchange-only residue (S1 §6, lines 433–483): still
  required are encoding read/write (lines 442–447), initialization
  (lines 448–449), and conversions to/from every other supported format
  — the last item is **BELIEVED** as a joint reading of 3.1.2 + 5.4.2 +
  5.12, including correctly rounded decimal with `Pmin=5` and global `H`,
  and exact hex (lines 450–465). Classification for interchange-only is
  only `should` (lines 466–468). Boundary warnings are **BELIEVED**:
  exposing any *supported* binary16 arithmetic makes binary16 an
  arithmetic format and pulls in all of Clause 5 — "partial arithmetic
  support has no conforming middle position in the text read" (lines
  473–476). S1 summary: interchange-only "escapes binary16 *computation*
  only" (lines 480–483). S1 brief correction 2 makes the asymmetry
  explicit (lines 507–513).
- Target-side corroboration: pico-sdk wraps **no** half-precision helpers
  (`__aeabi_f2h`, `__aeabi_h2f`, `__gnu_*2h*` unwrapped, MEASURED against
  CMake lists) (S3 §1.6, lines 257–265). A binary16 decision therefore
  has no incumbent drop-in surface to inherit; it is new API + new
  conversions either way. TestFloat does cover `f16` as a format (S2
  §1.3, lines 116–119), so oracle cover exists for the arithmetic option
  (see §3 for its limits).
- Undecided by surveys: whether binary128/decimal formats are supported
  at all (S1 assumes binary-only throughout, e.g. decimal-only exclusions
  S1 lines 112–113, 193–194, 226); the set of supported integer formats
  for conversions (standard does not define integer formats, S1 §1.2,
  lines 138–139); `logBFormat` choice (S1 §1.1, lines 105–110);
  decimal conversion specification (language-defined, S1 §1.3, lines
  149–150).
- Judgement: **sufficient to propose**, provided SF-0 proposes per-format
  status separately (never "binary16/32/64" as one lump), prices decimal/
  hex conversion as Clause 5 work, and treats Clause 9 as default-out
  with per-family opt-ins (see §5). The interchange-only arithmetic-
  pull-in boundary is BELIEVED and must be presented to Logan as S1's
  reading, not as a quoted `shall`.

### Q3 — Rounding: required attributes; roundTiesToAway in or out (PROJECT Q3)

- Required set (READ 4.3.1–4.3.3): five attributes defined; **required
  for every implementation: `roundTiesToEven` + three directed;
  `roundTiesToAway` required only for decimal, expressly not required
  for binary**; binary default shall be ties-to-even (S1 §2, lines
  236–242). Attribute governs all possibly-inexact ops except ops that
  name their own rounding, zero-sum signs, overflow/underflow thresholds
  (lines 243–247). Mechanism: constant (block-scoped) specification
  shall be supported; dynamic modes only `should` for languages (lines
  248–254). S1 **BELIEVED** library mapping: one binary attribute with
  four selectable values + ties-even default (lines 255–257).
- Attribute vs operation trap (READ): the ties-to-away *operations*
  remain required for binary — `roundToIntegralTiesToAway` (S1 §1.1,
  lines 94–98) and ties-to-away `convertToInteger*` variants (S1 §1.2,
  lines 134–137) — even though the ties-to-away *attribute* is not.
  S1 brief correction 5 warns the confusion "cuts both ways" (lines
  522–525). SF-0 must never write "ties-to-away: out" without naming
  which of the two it means.
- Oracle cover by mode: TestFloat ordinarily tests **all five** 754
  modes plus optional round-to-odd if compiled in (S2 §1.3, lines
  134–142) — oracle coverage is wider than the binary requirement, and
  round-to-odd is not a 754-2019 binary attribute at all (AUDIT
  INFERENCE from S1 §2 + S2 §1.3 together). MPFR offers the five IEEE
  modes `RNDN/RNDZ/RNDU/RNDD/RNDA` (READ, S2 §2.1, lines 261–263). Host
  SSE2 covers RNE + three directed only — no ties-to-away, no
  round-to-odd (S2 §3.3, lines 403–408; summary lines 481–486).
- Incumbent/workload: ROM supports **only** RN-even, no traps (READ
  datasheet, S3 §2.2, lines 354–355). IAS15 assumes default RN with all
  exceptions masked and never touches `fenv` (MEASURED no
  `fesetround/fetestexcept` hits) (S4 §2.6 item 10, lines 341–345); its
  Kahan primitive is RN-dependent (S4 §2.6 item 7, lines 329–334).
- Undecided: whether SF-0 offers ties-to-away *attribute* as a
  non-conformance-required extra (cost: every rounding site + decimal
  conversion paths); how the attribute is stored/selected (with Q4 state
  decision — no survey measures a per-call vs per-core mode API).
- Judgement: **sufficient to propose** the required four + named-rounding
  operations. Any proposal to add the fifth attribute is Tier 2 (§5) and
  needs Berkeley/MPFR-only gating (no host oracle).

### Q4 — Exceptions: default handling + five flags; flag/mode state home; Clause 8 (PROJECT Q4)

- Five exceptions + flags (READ 7.1): invalid, divideByZero, overflow,
  underflow, inexact, each with a status flag; default handling is
  non-stop (deliver Clause 7 default, continue, raise flag) except exact
  underflow raises nothing; flags lowered only at user request; at most
  one exception per invocation, at most two flags raised (S1 §3.1, lines
  263–274). Default results per exception are READ in full (S1 §3.2,
  lines 280–307), incl. invalid → quiet NaN, divideByZero → signed Inf,
  overflow by-attribute table. Flag operations `lowerFlags/raiseFlags/
  testFlags/testSavedFlags/restoreFlags/saveAllFlags` are required
  `shall`s (S1 §1.6, lines 228–230).
- Clause 8 alternate handling: **not required by 754** (READ Clause 8 +
  4.1 + 7.1: every operative sentence is a `should` addressed to language
  standards; "Nothing in Clause 8 is a `shall` on a floating-point
  implementation as such") (S1 §4, lines 365–374). Flush-to-zero exists
  only as 8.2 abrupt-underflow alternate attribute, "not a conforming
  *default*" (**BELIEVED** consequence, lines 383–384). Two conditional
  `shall`s bind only implementations of those attributes (lines 380–382).
- Incumbent has **no FP state at all**: no status/flags register or flag
  word, traps unsupported (S3 §2.2, lines 368–375, MEASURED grep: no
  `fenv`/flags symbol wrapped or defined). Any IEEE flags "must be
  entirely new state" (S3 §2.2, lines 374–375). ROM renders error cases
  as infinities, not NaNs (S3 §2.2, lines 376–383) — the incumbent
  cannot be any part of an exceptions oracle.
- Dual-core homes (S3 §6, lines 685–754, facts READ, suitability
  **BELIEVED** where marked): `get_core_num()` one-load inline (lines
  691–693); per-core SIO divider/interpolators at identical addresses
  (lines 694–696) but using an ACCUM as flags would collide (lines
  697–701); TLS default `per_thread` = per-core `.tls0`/`.tls1` via
  `__tls_adjusted_by_core[2]`, so `__thread uint32_t fp_flags` would be
  per-core not per-RTOS-thread, at TLS-access cost (lines 702–714);
  plain `flags[2]` + `get_core_num()` with in-SDK precedent
  `hw_divider_results[NUM_CORES]` (lines 715–720); watchdog SCRATCH0–7
  shared + APB-cost (lines 721–726); scratch X/Y shared SRAM (lines
  727–731); 32 spinlocks exist but locking inside an AEABI helper that
  IRQs also call "invites deadlock on same-core re-entry" (lines
  732–738); PRIMASK masking precedent `PICO_DIVIDER_DISABLE_INTERRUPTS`
  (lines 739–745). Closing warning: shared mutable FP state would be
  "new failure surface that the incumbent simply does not have" (lines
  747–754).
- Oracle flag cover: every TestFloat case carries expected value + five
  flags (READ, S2 §1.3, lines 144–147), but TestFloat-general §8
  tolerates variation in exactly tininess, NaN payloads, float→int
  behaviour (READ contents, lines 152–155) — a TestFloat gate inherits
  those tolerances unless tightened. SoftFloat tininess/flag globals are
  **BELIEVED** interface shape ("verify in header at build", lines
  148–151). Host MXCSR accumulates five IEEE flags + non-IEEE denormal
  flag to mask out (S2 §3.3, lines 413–415).
- Unmeasured/blocking unknowns: IRQ re-entry semantics for flags on the
  same core (no survey runs board code; S3 Appendix, lines 802–805);
  RTOS task-switch handling explicitly "Not investigated" (S3 Appendix,
  lines 806–810); per-call (stateless, flags returned) design is never
  surveyed as an alternative to per-core state — PROJECT Q4 names
  "per core, per call, or global" but S3 §6 inventories only stateful
  homes (AUDIT INFERENCE). AEABI helpers (`__aeabi_fadd` etc., S3 §1.2)
  have no flags channel in their signatures, so a drop-in alone cannot
  deliver C `fenv` semantics without additional API/linking decisions
  no survey prices.
- Judgement: **Clause 8 out is sufficient to propose. Flag/mode state
  home is NOT sufficient to close on surveys alone** — SF-0 must put
  per-core vs per-call vs global to Logan with the IRQ/RTOS unknowns
  named, and P0 must freeze the choice before any kernel parcel (see §4).

### Q5 — Tininess (before/after rounding); NaN payloads, signaling NaNs, canonical NaN (PROJECT Q5)

- Tininess (READ 7.5): implementer **shall choose** after-rounding or
  before-rounding and **shall use that same choice for all radix-two
  operations, including conversions**; choice never changes delivered
  result, only whether underflow is signaled at the smallest-normal
  boundary (S1 §3.3, lines 316–322). **BELIEVED**: a binary library
  "must make once, document, and apply uniformly — including in its
  conversion paths" (lines 323–324). Underflow default handling always
  delivers the rounded result; flag only if inexact (S1 §3.2, lines
  300–302). There is "no conforming default flush-to-zero" (S1 §0, lines
  56–57).
- NaNs required (READ 6.2/6.2.1/6.2.3): quiet + signaling shall be
  supported; invalid → quiet NaN; signaling signals invalid except 5.12
  conversions; quiet-only inputs to general/quiet ops deliver a
  **canonical quiet NaN** (except as stated; FMA may signal invalid,
  7.2(c)); NaN result canonical even from non-canonical operand (S1
  §3.4, lines 330–337). First trailing bit shall exclusively distinguish
  quiet/signaling in binary interchange (3.4(a)) (lines 338–340).
- NaNs recommended only (all `should`): **payload propagation is not
  required** (single-NaN preserve-if-representable; multi-NaN one
  unspecified payload; narrow-wide-back preservation; diagnostics) (S1
  §3.4, lines 344–349); even quiet-bit **polarity** is only recommended
  (lines 350–352); NaN sign unspecified (line 353). S1 **BELIEVED**: one
  fixed canonical qNaN for every computational NaN result meets the
  letter; "any test oracle must not require a particular payload except
  where the implementation itself promises one" (lines 355–358). S1
  brief correction 6 repeats this for oracles (lines 526–528).
- Oracle interaction: TestFloat §8 tolerates tininess + NaN-payload
  variation (S2 §1.3, lines 152–155); x86 underflow "after rounding" is
  **BELIEVED**, with SoftFloat `8086-SSE` specialization existing to
  match that class — spec, specialization, and expectation "must be
  chosen together" or the tolerance hides the difference (S2 §3.3, lines
  415–419). NaN control: "compare NaNs by class … not by payload bits,
  whichever oracle pair" (S2 §3.4f, lines 463–469; x86 QNaN-indefinite
  + `cvttsd2si` overflow value **BELIEVED**).
- Incumbent/workload: ROM treats input NaNs as infinities, renders output
  NaNs as infinities (READ, S3 §2.2, lines 350–353); SDK default build
  does **not** propagate NaNs (`PICO_*_PROPAGATE_NANS` undefined ⇒ 0,
  MEASURED; SDK's own test defines both to 1) (S3 §1.4, lines 186–195).
  IAS15 executes Kahan residuals even under BASIC gravity with zeroed
  residuals (S4 §1.4, lines 170–174) and relies on NaN-comparison-false
  + `isnormal` filtering to survive div-by-zero (S4 §2.6 items 2–3,
  lines 298–311) — a flush/NaN-as-Inf softfloat changes chosen `dt`.
- Undecided: tininess choice itself (no survey recommends one side;
  performance on M0+ unmeasured); canonical NaN bit pattern(s) per
  format incl. sign; whether to promise payload propagation as a
  project-quality decision (9.7 payload ops then become testable scope,
  §5); FMA 0×Inf-with-qNaN-addend proviso is implementation-defined in
  7.2(c) (S1 §3.2, lines 283–284) and needs a project ruling.
- Judgement: **sufficient to propose** (canonical-qNaN-minimal is fully
  conforming per S1). SF-0 must record tininess + NaN policy as P0 seam
  constants and require the vector format to encode expected-flag
  sensitivity to tininess, or TestFloat tolerances will silently pass
  either choice (§3).

### Q6 — Interface: toolchain drop-in vs own API vs both; binary16 storage type (PROJECT Q6)

- Foundational caveat (READ Clauses 1.5/3.1): conformance is a property
  of a programming-environment implementation; "A bare soft-float
  library is not, by itself, the standard's unit of conformance. Mapping
  any requirement below onto a library API is therefore always
  **BELIEVED**" (S1 lines 22–27). SF-0's conformance claim must be
  phrased as library-level semantics, never as unqualified environment
  conformance. Clauses 10/11 (expression evaluation, reproducibility)
  were "not surveyed" (S1 Evidence index, lines 496–497) — exactly the
  clauses a C-interface claim would lean on.
- Drop-in mechanism (READ): GNU-ld `--wrap`, not weak symbols —
  `pico_wrap_function` emits exactly `LINKER:--wrap=<name>` (S3 §1.1,
  lines 27–29); replacements named `__wrap_<name>` via `WRAPPER_FUNC`
  (lines 30–34); assembler replacements are strong globals (lines
  35–40). Consequence (every reference resolves to `__wrap_`, original
  reachable as `__real_`) is **BELIEVED** standard ld semantics, "not
  re-verified on target here" (lines 41–46).
- Interposition surface (READ): float wrap list (S3 §1.2, lines 53–70)
  and double mirror (lines 71–82), incl. asymmetries (`fma` in double
  SCI_EXTRA vs `fmaf` own `NO_FMAF` group; `sincosf`/`sincos` group
  split, lines 80–82). "Wrapped" ≠ "in ROM": Tier A tail-calls ROM via
  copied pointer table (lines 98–113, MEASURED grep), Tier B SDK asm
  (compares, 32-bit conversions, lines 115–145), Tier C SDK C libm with
  accuracy-relevant facts — `fmaf` double-rounded via double
  intermediates "so not exact", double `fma` plain unfused `x*y+z`,
  naive `expm1`/`log1p` (lines 147–157). S3 brief correction 1: "There
  is no direct libgcc->ROM interposition" (lines 758–762).
- Flavours/selection (READ): `pico`/`compiler`/`none` per precision
  (S3 §1.4, lines 161–166); per-executable `PICO_DEFAULT_*_IMPL` /
  `pico_set_*_implementation` (lines 167–173); `pico_stdlib` pulls the
  wrapped impl by default (lines 174–179); `PICO_FLOAT_IN_RAM` moves
  only SDK wrapper code, ROM stays (lines 180–185).
- What stays with toolchain (READ+**BELIEVED** mix): unwrapped list incl.
  `fabs/frexp/modf/scalbn/rint/erf/tgamma/nan`, all `*l`, half helpers
  (S3 §1.6, lines 257–265); non-FP `__aeabi` divide/lmul/bit-ops wrapped
  by *other* SDK libs a replacement need not supply (lines 266–271);
  only `__aeabi_*` names on Arm, `__addsf3`-style only on RISC-V path
  (lines 272–278, LLVM name claim **BELIEVED**); no `__aeabi_fneg`
  (lines 279–282).
- Three interposition routes (S3 §5, lines 626–683) — **all recipes
  BELIEVED, none built**: (1) new `pico_float_<name>` flavour via
  `wrap_*_functions` + `pico_set_*_implementation` (lines 639–655,
  incl. non-wrapped `int2float` etc. obligation and `LIB_PICO_FLOAT_*`
  "BELIEVED detail — flag for whoever implements"); (2) `compiler`
  flavour + own `--wrap` (lines 656–661); (3) direct strong symbols, no
  `--wrap`, "Most fragile" (lines 662–671). Partial replacement +
  layering warnings are **BELIEVED** ld semantics, untested (lines
  673–683), incl. the load-bearing fact that unwrapped libm will execute
  wrapped AEABI ops internally, so subnormal/NaN/flag semantics
  propagate (lines 679–683).
- binary16 storage type: **no survey answers this**. Evidence stops at
  interchange bit layout 1/5/10, bias 15 (S1 §6 item 1, lines 442–447)
  and "half helpers unwrapped" (S3 §1.6). Whether `arm-none-eabi-gcc`
  14.2.1 on Cortex-M0+ offers `_Float16` arithmetic, storage-only
  `__fp16`, or neither (forcing `uint16_t` + explicit API) was measured
  by nobody — S4's ARM probe measured REBOUND struct sizes only (S4
  §4.1, lines 454–465). This is a one-probe P0 question SF-0 must list
  as open, not assume.
- IAS15 interface fact: REBOUND has **no `REAL` typedef, no precision
  switch, zero `long double`, zero source-level `fma`** in 31,692 LOC
  (MEASURED) (S4 §2.5, lines 273–288); "A softfloat port changes the
  *implementation* of `double`, not a typedef" (lines 280–283). A
  drop-in therefore serves the workload unmodified; an own-API-only
  library forces a workload rewrite (AUDIT INFERENCE).
- Judgement: **sufficient to propose** drop-in-first (route 1 or 2) with
  own API as additive surface for flags/modes/binary16; **insufficient**
  to promise link-level behaviour (partial wrap, `__real_` fallback,
  header extras) until P0 builds one route. SF-0 must name the owned
  symbol list as the contract surface (S3 §5, lines 673–674).

### Q7 — Targets: speed/size + yardstick; flash vs RAM; C vs Thumb asm (PROJECT Q7)

- Yardstick candidate (READ, with caveats): datasheet ROM *average*
  cycles over random input (S3 §4.1, lines 531–539), full tables float
  (lines 541–551, e.g. `_fadd` 71, `_fdiv` 71, `_fsqrt` 63) and double
  (lines 553–562, e.g. `_ddiv` 183, `_datan2` 2168). Three reasons these
  cannot be carried unqualified: (a) caption says µs, columns say Cycles
  — cycles reading is **BELIEVED** plausibility (lines 533–539); (b) they
  exclude SDK wrapper overhead, SDK-asm compares/conversions, all Tier C
  libm (lines 564–570); (c) "I found no published SDK-level cycle table"
  (MEASURED grep, lines 569–571). What exists is a *harness*:
  `float_benchmark.c`/`double_benchmark.c` using SysTick, built
  `copy_to_ram` + `*_IN_RAM=1`, so "the SDK's own yardstick excludes XIP
  effects by construction" (lines 571–578). Any comparable benchmark
  must state placement, clock (125 MHz default READ, lines 578–580),
  cache state (**BELIEVED** methodology note).
- Memory model (READ): ROM 16 kB single-cycle (S3 §4.2, lines 584–587);
  SRAM 264 kB striped + scratch X/Y (lines 588–595); XIP flash 16 MB
  behind 16 kB cache, 1-cycle hit, **no fixed wait-state number** — miss
  cost depends on SSI divider (default 4 ⇒ 31.25 MHz at 125 MHz) and
  working set, quantification **BELIEVED**, "I measured nothing" (lines
  596–607). Placement idioms `__not_in_flash_func`,
  `__time_critical_func`, `__scratch_x/y`, `float_section` macro
  pattern (lines 608–624). S3 brief correction 4: "'XIP flash wait
  states' is the wrong mental model" (lines 771–774). Correction 5: "the
  yardstick must be produced with the SDK benchmark harnesses" (lines
  775–779).
- SIO kernel resources: divider one 32/32 (q,r) per ~8 cycles + traffic,
  wide divisions software-multi-stepped (S3 §3.1, lines 457–464,
  **BELIEVED** synthesis); interpolators fuse shift/mask/sign-extend/add
  in 1 cycle but no >31/left shifts, no multiply except 8-bit blend, no
  64-bit, plus claim/save cost on every use (S3 §3.2, lines 519–527,
  **BELIEVED** assessment). No survey measures divider-assisted vs
  pure-software division for binary64 widths; divider early-read value
  undefined in extracted text (**BELIEVED**, S3 §3.1, lines 429–435).
- Workload cost shape: IAS15 step = 7 gravity evaluations per PC
  iteration + 1 initial, up to 12 iterations ⇒ up to 85 per attempted
  step (READ arithmetic, S4 §1.3, lines 139–141); workspace 1,176 B/
  particle dominates particles ~10:1 (S4 §4.2, lines 479–488); on M0+
  "cost drivers are the O(N²) sqrt/div pairs … and the long Horner
  chains" (**BELIEVED**, S4 §6.4, lines 754–758). No on-board timing of
  anything exists in any survey.
- Language: incumbent precedent is Thumb asm wrappers/shims (~2,000-line
  double V1 shim alone, S3 §1.5, lines 238–240) + C SCI_EXTRA (S3 §1.3).
  Divider save/restore macros are asm to reuse (S3 §3.1, lines 451–456).
  No survey compares C vs asm kernels for size/speed/verifiability; no
  code-size figures for any option exist. PROJECT Q7's BELIEVED premise
  ("pico-sdk … uses the bootrom's routines") is now **refuted as a
  blanket statement** by S3 §1.3 tiers — SF-0 must restate the yardstick
  as three tiers, not "the bootrom".
- Judgement: **insufficient to set numeric speed/size goals**. Sufficient
  to propose a *measurement plan*: produce SDK-level baselines with the
  SDK harness (RAM + flash placements stated), then set goals relative
  to Tier A/B/C separately. Any SF-0 sentence of the form "within X% of
  pico-sdk" today rests on unmeasured ground.

### Q8 — Dependencies and licence: pico-sdk + toolchain; output licence; copy vs read (PROJECT Q8)

- Pinned inputs (MEASURED/READ): pico-sdk 2.3.1 at the host path (S3
  header, lines 5–6); RP2040 datasheet `RP-008371-DS-1` build 2025-02-20,
  642 pp., 5,301,205 bytes MEASURED (S3 header, lines 7–11);
  `arm-none-eabi-gcc 14.2.1` present (MEASURED, S2 §1.5, lines 242–243;
  corroborated by lead ledger Phase 0 entry); board RP2040 rev B2 = ROM
  V3 (S3 §1.5, lines 199–205). ROM-version consequence: V1 (B0) has no
  double table, no float entries ≥0x54, gap filled only when
  `PICO_*_SUPPORT_ROM_V1 && PICO_RP2040_B0_SUPPORTED` both 1, board
  headers frequently negate (S3 §1.5, lines 222–253). Whether SF-0
  supports B0 at all is a scope decision the surveys price but do not
  make.
- Berkeley (READ licence text fetched): SoftFloat + TestFloat 3e both
  UC Regents BSD-3-Clause in substance; copying code allowed with
  notice, linking `libsoftfloat.a` into a test harness allowed,
  distributed binary triggers only notice-in-docs; nothing distinguishes
  test-only from production (S2 §1.2, lines 79–97). Generated vectors:
  **BELIEVED** no separate output licence claim; regenerate-from-seed
  "avoids the question entirely" (lines 98–103). Release-2 terms are a
  different trap text; pin must stay 3e (lines 104–107). Licence permits;
  "Whether muse-softfloat's *own* code may contain copied Berkeley code
  is a project-integrity decision … S2 takes no position; SF-0 should
  state the project's rule explicitly" (lines 108–112). Pinning hazard
  (READ/MEASURED fetch): GitHub `ucb-bar` `master` Makefile lists
  bfloat16 objects absent from 3e docs ⇒ master drifted past pristine
  3e; "Pin the jhauser.us 3e archive … and record its hash" (S2 §1.1,
  lines 65–75). Any pin older than 3d is a defective sqrt oracle (READ
  history: 3d fixed 64/80/128 sqrt bugs, lines 59–64).
- Other code (S2 §5, lines 563–600, READ per source): compiler-rt
  builtins Apache-2.0 WITH LLVM-exception per-file headers — trust
  headers, project web page stale (lines 571–582); libgcc soft-fp
  GPLv3+ with Runtime Exception — linking compiled runtime ≠ copying
  source; READ ✔ COPY ✘ for a non-GPL library (lines 583–592); MPFR
  LGPLv3+ — test-only link fine, static distribution carries obligations
  (S2 §2.1, lines 281–286). IBM Haifa FPgen mirror licence: **not found**
  in what was fetched, "**BELIEVED** gap, verify before use" (S2 §4 item
  1, lines 496–508). pico-sdk's own licence/copy terms for reusing SDK
  asm/macros (e.g. divider macros S3 recommends reusing) were surveyed
  by nobody (AUDIT INFERENCE — S3 reads SDK code without a licence row).
- REBOUND (READ): `LICENSE` is GPL-3.0 text, headers "version 3 … or any
  later version" ⇒ GPL-3.0-or-later (S4 §0, lines 17–21); consequence
  **BELIEVED** standard reading: linking into distributed firmware makes
  the combination GPL; clean-room reimplementation from papers avoids
  it, copying tables/code does not (lines 22–24); pinned commit
  `262a9cc…`, v5.2.2 MEASURED (lines 13–16). Coefficient tables are
  hard-coded `static const double` (S4 §1.2, lines 79–88) — copying them
  is copying GPL code under S4's reading (S4 §6.4, line 766).
- Project licence: **none exists yet** (MEASURED listing: no `LICENSE`
  in `muse-softfloat/`) so all COPY verdicts are "in the abstract"
  (S2 §5, lines 594–600; brief correction 9, lines 661–665). IEEE PDF:
  owner's licensed copy at workspace root, read in-workspace only, never
  copied into a repo, cited by clause/page (S1 header, lines 4–9).
- Judgement: **sufficient to propose** copy/read rules per source,
  provided SF-0 (a) picks/proposes the project licence *before* any
  parcel is briefed to copy, (b) records the Berkeley pin by archive
  hash not by mirror branch, (c) keeps REBOUND extraction vs
  reimplementation as an explicit GPL decision for Logan, (d) treats
  IBM vectors as blocked until terms are verified.

### Q9 — Authority and oracles (PROJECT Q9; WORKFLOW Phase 2 "authority and oracles")

- Contract vs authority split: standard is the contract; authority must
  be runnable (`WORKFLOW.md` Phase 2; PROJECT "The standard" section).
  S1 supplies the contract surface (above). S2 supplies the runnable
  candidates; no survey *selects* the authority — that is SF-0's
  proposal for Logan to approve.
- Berkeley SoftFloat/TestFloat 3e (S2 §1): formats f16/f32/f64/extF80/
  f128, no decimal (lines 116–119); operations add/sub/mul/div/sqrt,
  FMA except extF80, remainder, round-to-integral, comparisons,
  FP↔FP + FP↔int32/64 conversions, sNaN tests; decimal conversions
  explicitly not covered (lines 121–128); five roundings + optional
  round-to-odd (lines 134–142); value+flags per case (lines 144–147);
  programs `testfloat`/`testsoftfloat`/`testfloat_gen`/`testfloat_ver`
  (lines 157–167). Self-declared weakness (READ verbatim in substance):
  "not especially good at testing difficult rounding cases for divisions
  and square roots", no SRT-bug search (S2 §1.4, lines 187–193).
- MPFR 4.2.2 (S2 §2): correctly-rounded claim READ from manual (lines
  255–263); genuinely foreign codebase vs Hauser (lines 264–269);
  **emulation contract** — native model has wide exponent, no
  subnormals; binary64 needs prec 53 + `emin=-1073`/`emax=1024` +
  `mpfr_subnormalize` after *each* op or the oracle is silently
  non-IEEE exactly where the gate cares (lines 270–278); binary32
  numbers **BELIEVED** arithmetic (lines 278–280). Availability
  MEASURED: already installed `mingw-w64-x86_64-mpfr 4.2.2-3`, headers/
  libs present, link+run smoke prints 4.2.2 (S2 §2.2, lines 290–302;
  headline 3, lines 33–35). "The SF-0 step 'obtain a foreign oracle' is
  already done" (S2 brief correction 3, lines 629–632).
- mpmath (MEASURED, S2 §2.3, lines 306–351): default prec-53 decides no
  binary64 product rounding (lines 309–318); unbounded exponent, no
  subnormals/flags (lines 319–324); CPython `float()` correctly rounded
  RNE incl. ties/subnormals but RNE only (lines 325–334); directed
  roundings need exact-rational or hand-emulated route (**BELIEVED**
  recommendation, lines 334–338); no correct-rounding claim for
  transcendentals (**BELIEVED**, lines 344–348); throughput fit for
  thousands of adversarial cases, not 10⁷ gates (**BELIEVED**, lines
  349–351). Brief correction 4: mpmath is "an ingredient for an oracle,
  not an oracle out of the box" (lines 633–639).
- Host SSE2 (S2 §3): CPU supports sse2/avx/avx2/fma MEASURED (lines
  359–364); **default `gcc` is i686 x87 `FLT_EVAL_METHOD=2`, wrong by
  default** (MEASURED, lines 368–375; headline 2, lines 27–32); absolute-
  path 64-bit gcc with wrong PATH fails silently exit-1-empty (MEASURED,
  lines 376–382); fix MEASURED: mingw64-first PATH ⇒ x86_64,
  `FLT_EVAL_METHOD=0` (lines 383–390); `long double` still 80-bit
  (lines 391–394). Bit-exact scope: binary32/64 + − × ÷ √, explicit FMA,
  conversions, comparisons in RNE+3 directed (summary lines 481–486),
  reached only with pinned `-ffp-contract=off`, explicit MXCSR,
  NaN-payload masking; FMA contraction MEASURED flipping answers (S2
  §3.4c, lines 437–449). Architectural detail block is tagged
  **BELIEVED** where not re-derived from the SDM (lines 398–401).
- Supplements (S2 §4, lines 490–559): IBM Haifa FPgen 754R vectors
  (item 1); exhaustive binary16 all-pairs + binary32 unary as a method
  (item 2, lines 509–515, feasibility **BELIEVED**); Kahan Paranoia as
  oracle-path smoke, not a vector gate (item 3, lines 516–522);
  MPFR-directed near-midpoint div/sqrt/FMA incl. Boldo–Muller regime
  (item 4, lines 523–531); UCBTEST, Lefèvre/Muller + CORE-MATH `.wc`,
  ELEFUNT/Beebe named to refuse/park (items 5–7, lines 532–554).
- Build route (S2 §1.5, lines 195–247): prerequisites MEASURED (Git
  Bash, Make 4.4.1, both gcc flavours) but route steps READ+**BELIEVED**
  assembly — S2 did not build (lines 202–204); TestFloat Makefile
  variables unfetched, "confirm … don't transcribe from memory" (lines
  220–226); gcc-16-vs-2018-code risk **BELIEVED** small, unmeasured
  (lines 236–240). On-board oracle use: host-side primary, board
  consumes pre-generated vectors (**BELIEVED**, lines 242–247).
- Judgement: **sufficient to propose** a layered authority (Berkeley
  primary + MPFR foreign + SSE2 second foreign for its subset +
  exhaustive/directed supplements), provided SF-0 includes an
  oracle-disagreement procedure (S2 §1.5 step 5, lines 232–235 calls it
  an SF-0 design item) and the coverage gaps in §3 below are closed by
  project-owned references, not by assertion.

### Phase 2 extras beyond the nine questions

**Refusals (WORKFLOW Phase 2; P0 refusal table in Phase 3).** No survey
drafts a refusal table; the evidence supports these refusals by name
(AUDIT INFERENCE assembling survey facts): Clause 8 alternate handling
as a 754 requirement (S1 §4); flush-to-zero as default (S1 §0 lines
56–57, §4 lines 383–384); payload-exact NaN equality as conformance
(S1 §3.4; S2 §3.4f); correctly-rounded transcendentals without
MPFR/CORE-MATH oracles (S2 §2.3 lines 344–348, §3.4g lines 470–475,
§4 item 6 lines 540–548 — S2 explicitly recommends refusing worst-case
files "by name with provenance rather than by omission"); host libm /
x87 transcendentals as oracle (S2 §3.4g); ROM as oracle in any
subnormal/NaN/directed case (S3 §2.2); whole-file `cmp` of REBOUND
archives as bit test (S4 §4.3 caveats, lines 535–555). SF-0 must also
decide refusals the surveys price without recommending: B0/V1 support,
decimal *formats* (vs decimal *conversions*), binary128, 2008 min/max
semantics. Judgement: **ingredients sufficient; table itself is SF-0
authoring, not survey evidence.**

**Gates and negative controls (WORKFLOW Phase 2).** Surveys supply gate
*ingredients*, not gates: TestFloat levels/seeds mechanism READ but
per-function counts **BELIEVED** order-of-magnitude with explicit
"**Do not gate on these numbers**. First build task: measure" (S2 §1.4,
lines 178–186); exhaustive sweeps as method (S2 §4 item 2); Paranoia as
smoke (item 3); MPFR-directed hard cases (item 4); S4 field-parsed
bit-comparison protocol as a workload gate pattern (**BELIEVED**
recommendation, S4 §4.3, lines 557–565). No survey defines pass/fail
budgets, runtime budgets, or a single named negative control with an
expected-failure demonstration. Negative-control *candidates* with
measured teeth exist: wrong-PATH gcc silently voids the oracle (S2
§3.2); FMA contraction flips results (S2 §3.4c); missing
`mpfr_subnormalize` silently non-IEEE (S2 §2.1); FTZ/DAZ inherited modes
(S2 §3.4b). Judgement: **insufficient to copy gates from surveys** —
SF-0 must author gates + negative controls and P0 must measure real
vector counts before any "level 2" phrase enters a brief.

**P0 contents (WORKFLOW Phase 3 list: format parameters defined once
and generated; runner/front door with budgets; vector format + replay;
board harness; refusal table — `WORKFLOW.md` lines 68–74).** Evidence
constraints are detailed in §4 below. Headline: surveys fully determine
*what P0 must freeze* (parameters, rounding/tininess/NaN policy, state
home, symbol surface, oracle discipline) but contain **zero** built or
run P0 artifacts. Judgement: **sufficient to specify P0; nothing in
S1–S4 de-risks P0 execution.**

**Parcels and waves (owned files, time box, scope ceiling each).**
Surveys imply natural seams but propose no parcel split: S1 operation
classes (§1.1–§1.6) × formats; S3 interposition tiers + symbol groups
(§1.2 groups map to `NO_*` exclusions, S3 §1.2/§5); S4 extract pieces
with upstream LOC MEASURED but kept-LOC **BELIEVED** 750–950 total (S4
§6.2, lines 698–711). IAS15 needs only `double` + − × ÷ √ +
`fabs/copysign/isnormal` (S4 §2.1–§2.2, §5.3 lines 655–658) — a workload
wave can land long before full Clause 5 (AUDIT INFERENCE). No survey
estimates softfloat kernel LOC, decimal-conversion LOC, or parcel
durations; WORKFLOW calendar (10 days, `WORKFLOW.md` lines 183–193)
and draft caps (study ≤3 drafts + 2 re-checks, lines 175–178) are kit
proposals, not survey measurements. Judgement: **seams sufficient;
time boxes must be lead judgements labelled as such, never cited as
survey-derived.**

**Metrics capture (WORKFLOW Phase 2; `METRICS.md`).** S1–S4 contribute
only probe discipline (script files + logs retained: S2 Appendix A,
lines 604–614; S3 Appendix, lines 794–801; S4 scratch artifacts, lines
807–810). The actual metrics machinery (extractor, JSONL, tables) is
evidenced in `ledger/lead.md` (extractor entry 2026-10-26 11:37:23;
Wave 0 pushed entry 12:06:41), **outside** the four-survey audit base.
SF-0's metrics section must cite the lead's measurements as its source,
not S1–S4. Token figures rest on harness counters/transcripts per
`METRICS.md` table — no survey validates them. Judgement: **surveys
neither support nor block metrics; do not cite them there.**

### Workload decision hidden inside Q6/Q7: IAS15 configuration

S4 does not map to a single PROJECT question; it constrains Q6/Q7/Q9
jointly and SF-0 must pin its configuration explicitly:

- Step surface (READ/MEASURED): IAS15 + gravity need `sqrt` (1/pair),
  `fabs`, `copysign`, `isnormal`, own `sqrt7` 7th-root Newton (no `pow`)
  (S4 §2.1, lines 201–214; §2.2, lines 221–239; §3.1, lines 354–382).
  "Nothing in the subset needs `pow`/trig/exp softfloat routines at all
  (the decisive fact of this survey)" (**BELIEVED** Pico note, S4 §6.4,
  lines 754–758; the zero-call inventory itself is MEASURED).
- IEEE assumptions checklist (READ): exact `isnormal` incl. subnormals,
  div-by-zero → Inf/NaN filtered never trapped, NaN-comparison loop
  control, real Inf, signed-zero via `copysign`, correctly-rounded
  `sqrt`/`/`, RN + no reassociation/excess precision, decimal-literal
  conversion, no `fenv` (S4 §2.6 items 1–10, lines 292–345). Kahan
  primitive + persistent `csx`/`csv` residuals are saved state (S4 §1.4,
  lines 154–189).
- Timestep: four adaptive modes, default **PRS23** since Jan 2024;
  formulas + clamp/reject/cap READ exactly (S4 §3, lines 347–443).
  Wrapper `exact_finish_time` overwrites last `dt` (lines 438–443).
  Reject-retry is **unbounded** (`while(!step_try)`, S4 §1.3 line 41
  cite; §2.6 item 3, lines 304–311) — on-device hang risk; `min_dt>0`
  bounds it (**BELIEVED** mitigation, S4 §6.4, lines 763–765).
- Gravity choice changes bits *before* compensation: BASIC
  `G/(r*r*r)` vs COMPENSATED `G/(r2*r)` (READ, S4 §2.2, lines 229–234);
  default gravity is **uncompensated BASIC** (S4 §1.1, lines 60–61).
  "IAS15 bit-identical" is meaningless until SF-0 pins gravity,
  adaptive mode, MEGNO off/on, `exact_finish_time`, OpenMP off (S4 §5.2,
  lines 633–640: OpenMP changes summation order, generally not
  bit-identical).
- Strict build: upstream default is `-std=c99 -O3` with **no**
  `-ffp-contract` control; `-ffp-contract=off` opt-in via
  `FFP_CONTRACT_OFF` in Python build only (READ, S4 §5.1, lines
  569–608). S4's strict flag set is **BELIEVED** recommendation (S4
  §5.2, lines 610–631). Portability claim assessed sound for the core
  but **BELIEVED, not MEASURED** — "I did not run a cross-compiler
  bit-comparison myself" (S4 §5.3, lines 655–675).
- Bit-comparison: whole-file `cmp` is wrong (git hash, walltime, raw
  pointers, native `size_t`, diff-append, `-0==+0`/NaN comparator
  semantics — all READ, S4 §4.3, lines 535–555); compare parsed FP
  payloads: first 88 B/particle + `t/dt` + 13 IAS15 arrays for restart
  (**BELIEVED** protocol, lines 557–565). Struct sizes MEASURED on
  host32 + M0+ (`reb_particle` 112 B both; workspace 1,176 B/particle)
  (S4 §4.1–§4.2, lines 447–494).
- Judgement: **sufficient to specify** a minimal IAS15 demonstration
  (extract ~750–950 LOC **BELIEVED**, zero alloc/printf per step at
  fixed N MEASURED counts S4 §6.3, lines 730–750). **Insufficient** to
  claim demonstrated bit-reproduction — that requires running both
  builds, which no survey did.

## 2. Contradictions and unsupported claims SF-0 must not carry unqualified

Ordered by damage if SF-0 repeats them as flat facts. Each gives the
claim, the tag/status in its own report, and the qualification SF-0 must
attach.

### Cross-survey (highest risk first)

1. **Decimal conversions are required but have no oracle.** S1 requires
   correctly-rounded decimal-character conversions for every arithmetic
   format with `H>=20` for this format set (S1 §1.3, lines 149–172).
   S2 states TestFloat "cannot test decimal floating-point" (S2 §1.3,
   lines 118–119) and lists decimal conversions as "the one 1985
   requirement omitted" (lines 127–128). S3 leaves decimal/stdio-side
   conversion with the toolchain unwrapped (S3 §1.6). No survey names a
   decimal-conversion oracle (MPFR decimal strings, exact-rational
   reference, or published vector set) or measures incumbent behaviour.
   **SF-0 must not claim a gated full-Clause-5 surface until a decimal
   oracle + digit-range plan is named.** This is the largest silent hole
   between S1's requirement and S2's cover.
2. **"Passes TestFloat" ≠ "754-2019 conformant".** S2 brief correction 6
   (lines 645–649) + self-declared div/sqrt weakness (S2 §1.4, lines
   187–193) + BELIEVED post-1985 absence (S2 §1.3, lines 128–132).
   TestFloat 3e operation families as READ (§6.1–6.6, S2 lines 121–123)
   do not obviously include S1-required `nextUp/Down`, `scaleB/logB`,
   `totalOrder`, classification, flag ops, version predicates, hex
   conversions. **SF-0 must enumerate which Clause 5 names each gate
   covers; "level 2" alone proves nothing about the tail (§3).**
3. **FMA correctness has no workload cover and a non-conforming
   incumbent.** S1: FMA required, single-rounding (S1 §1.2, lines
   124–126). S3: incumbent `fmaf` double-rounded, `fma` unfused (S3
   §1.3, lines 152–154). S4: zero source-level `fma` anywhere in REBOUND
   (MEASURED, S4 §2.5, lines 275–277); FMA enters only via contraction,
   which the strict build forbids. **IAS15 bit-success must never be
   cited as FMA evidence; FMA needs its own Berkeley + MPFR-directed
   (Boldo–Muller) gate (S2 §4 item 4).**
4. **Tininess/NaN differences are designed to be invisible to the
   default gate.** TestFloat §8 tolerates tininess, NaN payloads,
   float→int variation (S2 §1.3, lines 152–155). S1 requires one
   documented tininess choice incl. conversions (S1 §3.3). x86 tininess
   side is only BELIEVED (S2 §3.3, lines 415–419). **A green TestFloat
   run under default tolerances does not confirm SF-0's tininess or NaN
   policy at all.** The harness must tighten or add targeted cases.
5. **Host-oracle validity is PATH-conditional, retroactively.** S2
   MEASURED: Git Bash default `gcc` is i686/x87 and absolute-path 64-bit
   invocation fails silently (S2 §3.2, lines 368–390); lead ledger's
   "host gcc 16.1" is ambiguous between two installs (S2 brief
   correction 1, lines 618–624; `ledger/S2.md` Notes). S4's sizes were
   compiled on "host32 gcc" (S4 §4.1, lines 454–456) — struct *layout*
   survives (integer property), but **no FP execution on a host32 path
   may be cited as IEEE evidence**, and SF-0 briefs must require every
   oracle script to export mingw64-first PATH and assert
   `x86_64-w64-mingw32` + `FLT_EVAL_METHOD==0` (S2 §3.2, lines 387–390).
6. **Nothing has run on the board.** S3: "Nothing was compiled, linked,
   or run on the board" (Appendix, lines 802–805). S2 is host-only
   (Appendix A, lines 604–614). S4 ARM numbers are `nm -S` sizes, not
   executions (S4 §4.1 table header, lines 458–465). Lead ledger Phase 0
   records only that the B2 board "answers picotool, only COM1
   enumerates so far". **Every SF-0 sentence about on-board numerics,
   timing, IRQ behaviour, or harness throughput is currently
   unmeasured and must be labelled a plan, not a finding.**
7. **ROM "correctly rounded" contradicts ROM flush rules in the same
   datasheet section.** S3 quotes both "always correctly rounded" (five
   basic ops) and denormal-flush/NaN-as-Inf, noting "the datasheet does
   not reconcile them further" — the reconciliation is the surveyor's
   reading (S3 §2.2, lines 350–362). S3 Appendix: datasheet accuracy
   claims "untested by me" (lines 804–805). **SF-0 must not use ROM as
   a basic-ops oracle even in the normal range without first measuring
   the boundary, and never in subnormal/NaN/directed cases.**

### Within S1 (standard)

8. **"81 operations" is a name count, not a work count.** Tally is
   READ-by-enumeration with only 22 comparisons + 39 Table 9.1 names
   script-verified (S1 §1, lines 79–81; Evidence index lines 492–493);
   instantiation surface larger, true-surface claim BELIEVED (lines
   82–87). Page relation printed = PDF−1 MEASURED only "on every
   checked body page" / "sampled body pages" (lines 15–18, 492–493).
   **Size parcels by instantiations (formatOf crosses, integer-format
   set), and re-verify any load-bearing page cite in SF-0.**
9. **Hex conversions: shall vs should tension left open.** 5.4.3/5.12
   implementation text uses `shall`; 5.12.3 addresses languages with
   `should`; S1 BELIEVED hex belongs in the required set and an omitting
   claim "must say which sentence it rests on" (S1 §1.3, lines 152–158).
   **SF-0 must pick a sentence and record it; neither "hex required"
   nor "hex optional" is flatly READ.**
10. **Interchange-only conversion extent + partial-arithmetic boundary
    are BELIEVED readings** (S1 §6 items 3–4, lines 450–478), as is every
    library-API mapping (S1 lines 22–27) and the `H>=20` consequence
    arithmetic (lines 171–172). Language-defined choices (`logBFormat`,
    conversion spec, NaN spellings, payload sets) recur without library
    answers (S1 §1.1 lines 105–110, §1.3 lines 178–182, §5 lines
    426–428). **Present §6 to Logan as S1's reasoned reading; list the
    language-defined choices as SF-0 decisions.**
11. **Unsurveyed standard surface:** Clauses 10, 11, Annexes A/B (S1
    Evidence index, lines 496–497). Expression-evaluation and
    reproducibility expectations for a C drop-in therefore have no S1
    evidence. Monitor-watcher process note: ledger README bash watcher
    "did not run under this harness's Monitor shell" for S1 (S1 lines
    531–535) — consistent with lead ledger's "NOT yet watched-to-work";
    escalation latency claims must not assume the watcher works.

### Within S2 (oracles)

12. **Vector volumes are explicitly do-not-gate BELIEVED numbers**
    (~10⁵–10⁶/function/rounding level 1, 10⁸-class full level-2 sweep,
    gigabytes as text) — source tables unfetched (S2 §1.4, lines
    178–186). **No brief may budget runtime/storage from these; P0's
    first build task is `testfloat_gen … | wc -l` measurement.**
13. **Build route never executed.** Steps READ+BELIEVED (S2 §1.5, lines
    202–204); TestFloat Makefile variables unseen (lines 220–226);
    gcc-16 compatibility BELIEVED (lines 236–240); silent-failure
    mechanism (wrong-arch DLLs) BELIEVED, fix MEASURED (lines 379–390);
    SSE architectural block BELIEVED in part (lines 398–401); FTZ/DAZ
    CRT inheritance, `minsd/maxsd` semantics, x87 transcendental error,
    `rcpps` exclusion tagged BELIEVED/architectural (S2 §3.4, lines
    423–479). **SF-0 must schedule an oracle bring-up spike with
    `testsoftfloat` self-check (S2 §1.5 step 4, lines 227–231) before
    any parcel depends on vectors.**
14. **MPFR recipe details partly BELIEVED.** Binary32 `emin/emax`
    derived by arithmetic, "verify in the manual's table" (S2 §2.1,
    lines 278–280); manual text itself reached partly "via search
    extract" (lines 255–263). mpmath transcendental + throughput claims
    BELIEVED (lines 344–351). Vector-redistribution licence reading
    BELIEVED (lines 98–103); Berkeley-vs-project-policy split explicitly
    undecided (lines 108–112). IBM FPgen terms unknown (lines 496–508).
    Exhaustive-sweep feasibility ("hours-class") BELIEVED (lines
    509–515). **Each needs a P0 verification line, not an SF-0 assertion.**

### Within S3 (target)

15. **All `--wrap` consequences and all three drop-in recipes are
    BELIEVED/unbuilt** (S3 §1.1 lines 41–46; §5 lines 635–637,
    662–683), incl. `__real_` fallback, partial-wrap composition,
    `LIB_PICO_FLOAT_*` header behaviour (lines 652–655), unwrapped-libm
    propagation (lines 679–683). `__aeabi_f2uiz` −Inf-rounding
    coincidence reading BELIEVED (lines 129–133); trig large-argument
    bound BELIEVED (lines 390–396); divider early-read BELIEVED (lines
    429–435); interpolator utility + per-call cost BELIEVED (lines
    519–527); ROM reentrancy BELIEVED — datasheet never says
    "reentrant" (lines 747–754). **P0 must build one interposition route
    end-to-end before SF-0 wave briefs assume it.**
16. **Cycle yardstick triple-qualified** (µs-vs-cycles caption
    contradiction, averages-only, ROM-only) (S3 §4.1, lines 533–580);
    XIP miss quantification BELIEVED, nothing measured (lines 596–607);
    worst-case ROM timings published nowhere (Appendix, lines 806–810).
    Header-vs-table traps (deprecated compare slots named respectably,
    `pico/double.h` misnames, `_dix642double` typo) (S3 §7 item 6, lines
    780–787) mean **SF-0 must cite tables/source lines, not header docs,
    for any incumbent claim.**
17. **Interpolator ownership is not AEABI-shaped:** global (not per-core)
    claim byte, 7-word manual save/restore, no DIRTY fast path; whether
    the global claim is "a known SDK wart or intended, I did not
    investigate" (S3 §3.2, lines 500–517). Float/double code uses
    interpolators nowhere (MEASURED grep, lines 515–517). **Budget
    claim/save on every helper call before planning interpolator
    kernels (S3 §7 item 7, lines 788–792).**

### Within S4 (workload)

18. **Portability argued, never run.** "I did not run a cross-compiler
    bit-comparison myself … portability beyond the code-level argument
    is therefore BELIEVED, not MEASURED" (S4 §5.3, lines 672–675).
    Strict flag set BELIEVED (lines 610–631); why upstream gets away
    with opt-in contraction control BELIEVED (lines 604–608);
    literal-conversion bit-identity an assumption to pin via hex bit
    patterns (S4 §1.2, lines 96–101); `sqrt7` out-of-range behaviour
    BELIEVED arithmetic (lines 371–377); LP64 particle size BELIEVED
    (lines 467–471); kept-LOC 750–950 BELIEVED (lines 698–711); Pico
    notes incl. hang mitigation BELIEVED (lines 752–766). **SF-0 may
    promise a bit-comparison *experiment*, not a reproduced result.**
19. **Default-build trap mirrors S2's:** upstream default does not forbid
    FMA contraction on FMA-baseline targets (READ, S4 §5.1, lines
    604–608); `make` alone is not a strict reference (S4 §7 item 6,
    lines 792–796). Combined with S2's measured contraction flip (S2
    §3.4c), **any desktop reference built without explicit
    `-ffp-contract=off` + asserted toolchain is void as an IAS15
    oracle.** Also: `reb_particle_cmp` compares `name` pointer despite
    "ignoring pointers" header comment (READ, S4 §4.3, lines 527–533) —
    do not trust upstream comparator comments.
20. **Brief-presupposition corrections SF-0 must absorb** (S4 §7, lines
    768–805; S1 lines 501–535; S2 lines 616–665; S3 §7, lines 756–792):
    no `pow` in IAS15 (own `sqrt7`); no `REAL`/`fma` source surface;
    four timestep formulas, default PRS23 not legacy `(eps/error)^(1/7)`;
    no `OPTIMIZE` variable; two independent Kahan layers (integrator
    always, gravity only non-default COMPENSATED); file-granular link
    pulls all 12 integrators; min/max not Clause-5-required in 2019;
    binary16 not basic; FMA required; five attributes but four required
    for binary; wrapped ≠ in-ROM; RP2040 ≠ ROM V1 (board is V3). Any
    SF-0 draft still containing the corrected presuppositions fails its
    own survey base.

## 3. Oracle-coverage gaps by operation class

Method (AUDIT INFERENCE): rows are S1's operation classes (§1.1–§1.6,
§5); columns summarise S2's evidence per oracle. "Berkeley" means
SoftFloat/TestFloat 3e as READ in S2 §1.3 — where S2 lists only family
headings (§6.1 conversions, 6.2 basic, 6.3 FMA, 6.4 remainder, 6.5
round-to-integer, 6.6 comparisons, S2 lines 121–123) and post-1985
absence is BELIEVED (lines 128–132), this audit marks tail families as
*unconfirmed*, never as covered. SF-0 must replace every "unconfirmed"
cell with a header-level check at oracle bring-up. IAS15 (S4) is listed
to prevent workload-success overclaiming; it oracles almost nothing.

| Operation class (S1 cite) | Berkeley 3e (S2) | MPFR (+ rationals) | Host SSE2 | IAS15 | Gap / required closer |
|---|---|---|---|---|---|
| add/sub/mul/div/sqrt, all formats (S1 §1.2) | Covered incl. f16; div/sqrt hard-rounding weak by declaration (S2 §1.4) | Foreign correct rounding with subnormalize recipe (S2 §2.1) | f32/f64 bit-exact RNE+directed; no f16 (S2 §3.3) | f64 +−×÷√ RN only (S4 §2) | Div/sqrt near-midpoint: MPFR-directed (S2 §4.4) + exhaustive f16/f32-unary (S2 §4.2). No gap if supplements gated. |
| FMA single-rounding (S1 §1.2) | Covered except extF80 (S2 §1.3) | Foreign via MPFR FMA (S2 §2.1 foreignness list) | Explicit FMA3 only; contraction trap MEASURED (S2 §3.4c) | None (S4 §2.5) | Cancellation triples `a·b≈−c` need directed generation; 7.2(c) ruling needed. |
| remainder (S1 §1.1) | Covered (§6.4) | Derivable exactly (AUDIT INFERENCE: quotient + exact remainder; S2 does not claim an MPFR remainder gate) | No single IEEE-remainder instruction claimed in S2 | Only via libm `remainderf` in SDK Tier C context (S3), not IAS15 step | Confirm Berkeley remainder flag/edge expectations vs S1 §3.2 (zero divisor, Inf dividend). |
| roundToIntegral* 6 + Exact (S1 §1.1) | "round-to-integral-value" covered (S2 §1.3); named-variant granularity unconfirmed | Exact-rational reference trivial (AUDIT INFERENCE) | Partial via SSE rounding instructions — not inventoried in S2 | None | Verify each named rounding incl. ties-away *operation* + inexact-on-Exact-only (S1 lines 94–100). |
| nextUp/nextDown (S1 §1.1) | Unconfirmed (not in S2 family list) | Integer bit-step reference (AUDIT INFERENCE) | Bit-step (AUDIT INFERENCE) | None | **Project-owned reference required** until Berkeley headers prove otherwise. Cheap; resists exactly the "forget the tail" failure. |
| scaleB/logB (S1 §1.1) | Unconfirmed | Exact reference modulo `logBFormat` decision (AUDIT INFERENCE) | Partial (`ldexp` in SDK Tier C is incumbent, not oracle) | None | **Gap until confirmed.** `logB` special values split on integral-vs-float `logBFormat` (S1 lines 109–110, §3.2). |
| convertFormat FP↔FP, formatOf crosses (S1 §1.2–§1.3) | Conversions among five formats covered (S2 §1.3) | Foreign via precision/emin recipe per destination (AUDIT INFERENCE from S2 §2.1; binary32 constants BELIEVED) | f32↔f64 covered; no f16 (S2 §3.3) | None | Widening-exact vs narrowing-rounded + sNaN-canonicalize-on-same-format (S1 lines 146–148) need targeted cases; f16 crosses Berkeley/exhaustive only. |
| convertFromInt; 10× convertToInteger* (S1 §1.2) | To/from int32/64 covered (S2 §1.3); §8 tolerates float→int variation (lines 152–155) | Exact reference (AUDIT INFERENCE) | Covered with overflow-value caveat BELIEVED (S2 §3.4f) | Small exact casts only (S4 §2.6 item 9) | Overflow/NaN/Inf invalid behaviour + Exact-vs-non-Exact inexact split (S1 §3.2) must be tightened beyond TestFloat tolerance. Integer-format set undecided (S1 lines 138–139). |
| Decimal-char both ways, digits 1..H (S1 §1.3) | **Not covered** (S2 lines 118–119, 127–128) | No decimal-string gate claimed in S2 | No (`printf`/`strtod` never proposed as oracle in S2) | None; literals are compile-time (S4 §2.6 item 8) | **TOTAL GAP (§2 item 1).** Needs named oracle: exact big-integer reference and/or MPFR string paths + round-trip properties at Pmin/H (S1 lines 163–174). Largest unpriced item in SF-0. |
| Hex-char both ways (S1 §1.3) | Unconfirmed/absent from S2 families | Exact hex reference straightforward (AUDIT INFERENCE) | `float.fromhex` RNE datapoint MEASURED for CPython, not SSE2 (S2 §2.3) | None | **Gap + normative tension (§2 item 9).** Exactness (no-precision output exact) is property-testable; directed rounding needs reference. |
| copy/negate/abs/copySign (S1 §1.4) | Unconfirmed as named ops | Bit-reference (AUDIT INFERENCE) | Bit ops (AUDIT INFERENCE); IAS15 uses `fabs/copysign` (S4 §2.1) | f64 `fabs/copysign` exercised | Trivial but must be gated: non-canonical propagation + "negate ≠ 0−x" (S1 lines 189–193). Easy to omit from vectors. |
| 22 comparisons; cross-format (S1 §1.5) | Comparisons covered (§6.6); quiet/signaling split per-predicate unconfirmed | Exact reference (AUDIT INFERENCE) | `comiss/ucomiss` quiet/signaling behaviour claimed (S2 §3.3) | Ordering via C `<`/`>` + `isnormal` guards only (S4 §2.6) | Verify invalid-on-sNaN vs qNaN per predicate (S1 lines 204–208); cross-format pairs (line 208). |
| totalOrder/totalOrderMag (S1 §1.5) | Unconfirmed | Bit-order reference (AUDIT INFERENCE) | Bit-order (AUDIT INFERENCE) | None | **Project-owned reference required.** Signed-zero/NaN placement (S1 lines 210–213); signals nothing incl. sNaN. |
| class + 10 predicates; radix (S1 §1.6) | Unconfirmed (sNaN *tests* mentioned, S2 line 127, ≠ classification API) | Bit-decode reference (AUDIT INFERENCE) | Bit-decode; `isnormal` semantics load-bearing for S4 | `isnormal` 12 sites (S4 §2.1) | **Gap until confirmed.** Ten-class `class` (S1 lines 222–224) needs exhaustive-per-encoding-class vectors; f16 exhaustive closes it for f16. |
| Flag ops ×6; version ×3 (S1 §1.6) | Flags compared per case (S2 lines 144–147) ≠ flag *operations* tested | N/A (state machine, not arithmetic) | MXCSR ops exist but never proposed as flag-op oracle | None (no fenv, S4 lines 341–345) | **Gap.** Needs project-owned state-machine tests over arbitrary subsets (S1 lines 228–230) + save/restore. Version predicates trivial once edition decided. |
| Rounding: 4 required attrs | 5 modes + opt. odd (S2 lines 134–142) | 5 modes (S2 line 263) | 4 modes (RNE+directed) | RN only | Covered. Round-to-odd vectors must be excluded from 754 gates (non-754 mode). |
| Rounding: ties-away *attribute* (opt.) | Covered as 5th mode | `RNDA` covered | **No mode** | No | Berkeley/MPFR-only if Tier 2 adopts it (§5). |
| Subnormals / tininess boundary | Tolerated (§8) | Correct only with subnormalize recipe | Gradual underflow FTZ/DAZ-cleared; tininess side BELIEVED | Residual-scale values routine (S4 §1.4) | **Policy-invisible by default (§2 item 4).** Add smallest-normal-boundary flag cases per format × mode × conversion. |
| NaN payloads / sNaN quieting | Tolerated (§8); sNaN tests listed | No payload model claimed | Payload BELIEVED impl-defined | NaN-filtering behaviour only | Gate by class (quiet/signaling; sign only if promised) per S2 §3.4f + S1 §3.4. Payload-promising = new scope (§5). |
| Clause 9.2 transcendentals ×39 (S1 §5) | Absent (BELIEVED post-1985) | MPFR claims correct rounding (S2 §2.1); mpmath does not (BELIEVED, S2 §2.3) | **Barred** as oracle (S2 §3.4g) | None in step (MEASURED zero) | **Total gap for any Tier 2 claim** without MPFR-elementary + worst-case program (§5). |
| 9.4 reductions; 9.5 augmented; 9.6 min/max; 9.7 payload; 9.3 modes (S1 §5) | Absent (BELIEVED); `minsd/maxsd` ≠ 754 semantics (S2 §3.4e) | Min/max + augmented exactly referenceable (AUDIT INFERENCE); reductions implementation-defined by standard (S1 lines 411–414) | No 2019 min/max (S2 §3.4e) | None | Per-family Tier 2 gates (§5). Reductions cannot be conformance-gated bit-exactly at all. |

Reading of the table (AUDIT INFERENCE): the *arithmetic core*
(add/sub/mul/div/sqrt/FMA/conversions/comparisons in four modes) is
double- or triple-oracled once S2's supplements are included. The
*conformance tail* (decimal/hex, next/scaleB/logB, totalOrder,
classification, flag ops) has **no confirmed third-party oracle** in
survey evidence and will stand or fall on small project-owned exact
references (integers/rationals/bit-decodes) that P0 must provide. SF-0
should budget those references explicitly; they are cheap individually
and collectively are the difference between "core correct" and "Clause 5
complete".

## 4. P0-seam constraints and board-harness unknowns

WORKFLOW Phase 3 fixes P0 as "the seam, not a refactor: what every parcel
will share, made once", listing format parameters (defined once,
generated), runner/front door with budgets, vector format + replay,
board harness, refusal table (`WORKFLOW.md` lines 66–76). Constraints
below are what S1–S4 force that seam to contain; unknowns are what no
survey settles.

### 4.1 Seam must freeze before any parcel that reads it

1. **Format parameters, single generated source.** `k/p/emax/emin/w/t/
   bias` per format (S1 §0 table, lines 45–51) + `Pmin` 5/9/17, global
   `M`/`H` (S1 §1.3, lines 163–172) + supported integer-format set +
   `logBFormat`. Generated-once matters because S1's instantiation
   warning (lines 82–87) means hand-copied constants will diverge
   across formatOf crosses. IAS15 tables give the cautionary parallel:
   >17-digit literals whose stored bits depend on conversion correctness
   (S4 §1.2, lines 96–101) — seam constants should be bit patterns,
   generated and checked, not retyped decimals.
2. **Rounding + tininess + NaN policy as seam constants.** Four
   attributes + default (S1 §2); one tininess side applied to ops *and*
   conversions (S1 §3.3); canonical qNaN pattern(s), quiet-bit polarity
   (adopt the recommended polarity explicitly — `shall` fixes only the
   bit's role, S1 §3.4 lines 350–352), payload promise-or-refusal, FMA
   7.2(c) ruling. Every kernel parcel rounds/packs through these; a
   post-hoc change reopens every parcel. The SoftFloat specialization
   must be chosen to match (S2 §1.5 step 4, lines 227–231; §3.3 lines
   415–419) — specialization file belongs to P0, not to parcels.
3. **Flag/mode state contract (highest-risk seam).** P0 must embody the
   Q4 decision (per-core array `flags[2]` precedent vs TLS `__thread`
   vs per-call return) **with IRQ re-entry semantics stated**: AEABI
   helpers run in IRQ context; divider precedent shows the required
   shape (DIRTY check → save/restore via `save_div_state_and_lr` macros
   or PRIMASK masking, S3 §3.1 lines 441–456, §6 lines 739–745). Seam
   must state: who clears flags, nesting behaviour, second-core
   isolation test, RTOS-agnosticism-or-not (unsurveyed, S3 Appendix).
   Spinlock-in-helper is refused by evidence (deadlock, S3 §6 lines
   732–738). No parcel may invent its own state touch.
4. **Divider/interpolator usage contract.** If any kernel uses the SIO
   divider it must follow the save/restore-or-mask pattern wrappers
   already use for `fdiv`/`ddiv`/`tanf` (S3 §2.3, lines 397–403) and
   reuse SDK macros (S3 §3.1, line 456). Interpolator use requires
   exclusive claim or 7-word save/restore per call incl. IRQ re-entry
   (S3 §3.2, lines 509–517) — P0 should default-refuse interpolators in
   AEABI helpers unless a kernel proves the inner-loop win case (data
   resident in ACCUM/BASE, S3 lines 519–527). 64-bit division strategy
   (multi-step over 32/32, S3 lines 457–464) is a seam utility, not
   per-parcel reinvention.
5. **Symbol/interposition surface.** Owned list = S3 §1.2 wrap groups
   (float lines 53–70, double lines 71–82) plus non-wrapped exports
   (`int2float` family) if flavour route 1 is chosen (S3 §5 lines
   649–652), plus own-API symbols for flags/modes/binary16. P0 builds
   *one* route (S3 §5) and proves: wrap resolution, `__real_` behaviour
   or its refusal, `compiler`-flavour fallback, header-extra presence.
   ROM-version gate: target B2/V3 (S3 §1.5); B0 shim machinery
   (`shimmable_table_tail_call`, ~2,000-line double shim, lines
   231–245) enters only via explicit B0 decision. `sf_table` copy/init
   priority `"00350"` precedent (lines 212–221) is the pattern if P0
   needs runtime init.
6. **Vector format + replay.** Must encode per case: operation (incl.
   `formatOf` destination/source formats), rounding attribute (incl.
   named-rounding ops), operands/results as bit patterns, expected
   flags, tininess expectation, NaN comparison class (never raw payload
   equality by default — S1 §3.4, S2 §3.4f), integer-format identity,
   decimal digit-count/spec where applicable. Generation model is
   seeded pseudo-random, pipe-don't-store (S2 §1.4, lines 171–177);
   counts unmeasured (§2 item 12) so the format/runner must stream and
   subsample by seed. Three-way disagreement procedure (Berkeley vs
   SSE2 vs MPFR) is an SF-0/P0 design item (S2 lines 232–235) — replay
   output must preserve the failing bit patterns for adjudication.
   S4's field-parsed payload comparison (S4 §4.3, lines 557–565) is the
   model for workload vectors: fixed little-endian width-free framing,
   never whole-struct bytes (pointers/padding/`size_t`, lines 541–551).
7. **Runner/front-door discipline (all MEASURED failure modes).** Pin
   mingw64-first PATH + assert `dumpmachine`/`FLT_EVAL_METHOD` (S2
   §3.2); set `TMPDIR` (POSIX) + `TMP`/`TEMP` (Windows) into workspace
   scratch (lead ledger Phase 0; S2 §1.5 lines 209–212); script files
   not inline `bash -c` for ledger/build (lead ledger 10:12:37 entry:
   inline refused once, "script files only from here"); pin
   `-ffp-contract=off`, never fast-math, explicit `_mm_setcsr`
   (FTZ=DAZ=0) per batch (S2 §3.4a–c); MPFR subnormalize after every op
   (S2 §2.1); operands as runtime bit patterns, one op per statement
   (S2 §3.4a). Budgets cannot be set until vector counts are measured.

### 4.2 Board-harness unknowns (nothing below is measured)

Kit `BOARD.md` requires every board result to name ELF sha256, commit
(SHA + content apart), build flags, board id, under a `<ledger>/board.lock`
single-holder protocol, checked against the authority (kit `BOARD.md`
lines 9–20). Against that, survey+ledger evidence leaves open:

- **Transport:** how vectors reach the board and results return.
  S2 BELIEVED "on-board runs consume pre-generated vectors" (S2 lines
  246–247) — mechanism (UF2-embedded tables? USB CDC stream? SWD
  semihosting?) chosen by nobody. Lead ledger: board answers picotool,
  only COM1 enumerates (Phase 0), COM5 is Bluetooth not board
  (10:27:25 entry) — i.e. **no proven serial channel to the Pico exists
  yet** in evidence. Kit BOARD details table (probe, serial settings,
  flash command, output-read command, reset-to-known-state, board id)
  is still a template.
- **Throughput/timing:** no board cycle measurement of anything; SDK
  SysTick harness precedent runs `copy_to_ram` (S3 §4.1, lines
  571–578) so flash-vs-RAM harness placement changes numbers; XIP miss
  costs BELIEVED only (S3 §4.2). Full TestFloat-class volumes (even
  BELIEVED counts) cannot run on-board in reasonable time over an
  unproven link (AUDIT INFERENCE) — SF-0 must define the board *sample*
  (which seeds/classes run on silicon vs host) as a gate decision.
- **State/IRQ/dual-core on silicon:** flag-home candidates are desktop
  readings (S3 §6); IRQ-during-helper, second-core concurrent FP,
  divider contention under interrupt load — all unrun. P0 board harness
  needs a dual-core + IRQ self-test as its own negative control.
- **Silicon variance:** evidence covers one B2/V3 board. B0/B1 boards,
  if ever claimed, need the V1/V2 divergence matrix (missing tables,
  `_fsqrt` sign, `_fsincos` slot — S3 §1.5, lines 222–253) exercised or
  refused. Worst-case timings exist nowhere (S3 Appendix).
- **Workload on board:** IAS15 memory fits (N=10 ≈13 KB, N=100 ≈129 KB
  workspace+particles, S4 §4.2 lines 479–488, Pico arithmetic BELIEVED)
  but step cost on M0+ softfloat, unbounded-retry hang behaviour
  (watchdog? `min_dt>0` deviation?), and payload-framing implementation
  are all unbuilt. GPL extraction decision (§1 Q8) gates what code may
  even be flashed for distribution.

SF-0 consequence (AUDIT INFERENCE): board conformance runs sit on day 9
of the kit calendar (`WORKFLOW.md` line 192) but the harness unknowns
above are P0-shaped (day 3–4). If SF-0 leaves transport/serial/reset to
Phase 5, the first board evidence arrives after the waves that needed
it. P0's board item should be scoped as "prove flash→run→read-back of
one vector batch on the named B2 board", with full sampling gates
deferred explicitly.

## 5. Risks in adding expanded IEEE 754 Tier 2 scope "if time allows"

**Definition used here (AUDIT INFERENCE — the brief and kit do not
define Tier 2).** Tier 1 (minimal defensible claim) = 754-2019 Clause 5
for the arithmetic formats SF-0 selects (incl. decimal/hex conversions,
four rounding attributes, default exception handling, canonical-qNaN
policy), plus interchange obligations for any interchange-only format.
Tier 2 = everything beyond that which surveys price: (a) binary16
promoted to arithmetic if Tier 1 made it interchange-only; (b)
`roundTiesToAway` *attribute*; (c) Clause 9 families (9.2 ×39, 9.3, 9.4,
9.5, 9.6, 9.7); (d) payload-propagation promise; (e) Clause 8 alternate
handling; (f) B0/V1 support; (g) IAS15 beyond minimal BASIC+PRS23
(COMPENSATED gravity, MEGNO, variational). If the lead's Tier 2 differs,
this section must be re-read against that definition — an undefined
"expanded scope" cannot be risk-assessed. Note added at final ledger
read: `ledger/lead.md` entry 2026-10-26 12:26:47 (written while this
audit was running) records Logan's "more IEEE 754 compliance if time
allows it" and the lead's **Believed** reading that expanded compliance
is "best carried as tiered scope", to be put to the owner. That confirms
the provenance of "Tier 2" but does not define its contents; the
definition above remains this audit's coinage for Logan to ratify.

### Per-family risk

- **9.2 transcendentals ×39 — highest risk, do not bundle.** Correct
  rounding is a `shall` for anything calling itself conforming (S1 §5,
  lines 388–394) and "far harder than the Clause 5 core" (S1 lines
  430–431). Oracle: Berkeley absent, host libm/x87 barred (S2 §3.4g,
  lines 470–475), mpmath makes no correct-rounding claim (BELIEVED, S2
  §2.3 lines 344–348); only MPFR-elementary + Lefèvre/Muller worst-case
  files (`.wc`, S2 §4 item 6, lines 540–548) gate it, and S2 recommends
  refusing them by name for the basic-op library. Incumbent comparison
  is 1-ULP-class with named weak spots and range-limited trig (S3 §2.2,
  lines 363–367; §2.3 lines 390–396) — beating it proves nothing about
  correct rounding. IAS15 needs none of them (S4 §2). A single
  correctly-rounded `exp`/`log`/`sin` for binary64 is a research-grade
  parcel (argument reduction + Table Maker's Dilemma search); 39 across
  three formats does not fit any reading of the 10-day calendar
  (`WORKFLOW.md` lines 183–193) alongside Clause 5. **Recommendation:
  refuse correctly-rounded 9.2 in Tier 2; if libm-compatible
  approximations are wanted for drop-in completeness (SDK Tier C wraps
  `sinf`/`expf`/… S3 §1.2), scope them as explicitly non-754-conforming
  with ULP budgets, gated against MPFR values, never as Clause 9
  conformance.**
- **binary16-as-arithmetic (if Tier 1 is interchange-only) — medium
  risk, best Tier 2 value.** Cost is full Clause 5 at `p=11` (S1 §6
  pull-in, lines 473–476 BELIEVED boundary) but verification is
  uniquely strong: exhaustive unary + all-pairs binary (2^32 pairs)
  feasible in C (S2 §4 item 2, lines 509–515, feasibility BELIEVED)
  plus Berkeley `f16` cover (S2 §1.3). Risks: storage-type probe still
  open (§1 Q6); decimal conversions for binary16 join the §3 total gap
  (`Pmin=5`, global `H` unchanged, S1 §6 lines 457–460); formatOf
  crosses multiply (16↔32, 16↔64 destinations/sources). Fits as a late
  wave *after* binary32/64 kernels generalise; fits badly as a parallel
  first wave.
- **9.6 min/max ×8 — low implementation risk, medium claim risk.**
  Semantics are small and READ exactly (propagating vs `Number` forms,
  signed-zero ordering, S1 §5 lines 419–425) but oracle is
  project-owned (no Berkeley, `minsd/maxsd` wrong semantics S2 §3.4e)
  and the 2008-vs-2019 confusion is live (S1 lines 501–506). Cheap to
  add *after* NaN policy freezes; dangerous to add before, because
  `minimumNumber`'s sNaN-signal-but-ignore rule (S1 lines 421–423)
  exercises exactly the signaling path Tier 1 may have simplified.
- **9.5 augmented ×3 — medium risk.** Returns (rounded, exact-error)
  pairs under a clause-local ties-toward-zero-at-ties rounding defined
  nowhere else (S1 §5, lines 415–418) — i.e. a *sixth* rounding
  behaviour in the rounding/packing seam, plus specified tiny-error
  underflow interplay with the chosen tininess side. No oracle. Only
  after Tier 1 rounding seam is proven; error-pair oracles need
  exact-rational references (AUDIT INFERENCE).
- **9.7 payload access + payload-propagation promise — medium risk,
  seam-freezing.** Ops themselves are quiet/exception-free with
  implementation-defined admissible sets (S1 §5, lines 426–428), but
  adopting them credibly requires *promising* propagation that Tier 1
  deliberately refuses (S1 §3.4). That promise invalidates compare-by-
  class gating (S2 §3.4f), forces payload-exact vectors everywhere,
  and makes every prior "canonical qNaN" shortcut a defect. **Never
  add as an afterthought; it reopens Tier 1 gates.**
- **9.3 dynamic modes (`get/setBinaryRoundingDirection`, `saveModes`…)
  — low-medium risk.** Conditional `shall` only if dynamic modes are
  defined (S1 §5, lines 406–410; §2 lines 248–254). If Tier 1 already
  implements per-core mode state (Q4), 9.3 is thin API; if Tier 1 chose
  per-call stateless rounding, 9.3 *reintroduces* the state seam. Decide
  with Q4, not after.
- **9.4 reductions ×7 — claim risk without gate.** Results are
  implementation-defined approximations (any association/intermediate)
  (S1 §5, lines 411–414) — there is no bit-exact conformance to gate;
  only exception discipline (sNaN anywhere → invalid) is testable.
  Adding them buys API surface and review load with no verifiable
  conformance content. Park unless a workload needs them (IAS15 does
  not; its sums are hand-ordered, S4 §2.2 lines 226–228).
- **`roundTiesToAway` attribute — low-medium risk.** Touches every
  rounding site + decimal paths; oracle Berkeley/MPFR only (no host
  mode, §3). The *operations* are already Tier 1 (S1 §1.1–§1.2) so
  rounding machinery exists. Main risk is documentation confusion
  (attribute vs operation, S1 lines 522–525) and 25% more rounding-mode
  vector volume atop unmeasured counts (§2 item 12).
- **Clause 8 alternate handling — refuse in Tier 2.** Not a 754
  implementation requirement (S1 §4); it is language-block machinery
  (resuming attributes, handler blocks, abrupt underflow) with no C
  library shape surveyed and no oracle. Abrupt-underflow (FTZ-like)
  directly contradicts IAS15's subnormal-residual assumptions (S4
  §2.6). No workload pulls it.
- **B0/V1 support — medium risk, zero board to prove it.** Requires
  shim-on-use machinery + full software double fallback precedent
  ~2,000 lines (S3 §1.5, lines 231–245) for silicon the project does
  not hold (board is B2/V3). Unverifiable on available hardware;
  support would be host-only assertion. Refuse or explicitly label
  untested-on-silicon.
- **IAS15 expansions — low-medium risk, GPL-sensitive.** COMPENSATED
  gravity changes bits (S4 §2.2) and adds second Kahan layer (S4 §7
  item 7); MEGNO flips velocity prediction + `w[8]` table (S4 §2.4,
  lines 259–265); each multiplies bit-comparison configurations
  (gravity × adaptive mode × MEGNO × exact-finish). Every copied table
  deepens GPL-3.0-or-later exposure (S4 §0). Keep Tier 2 workload to
  one additional pinned configuration, gated the same way as the first.

### Systemic Tier 2 risks (AUDIT INFERENCE from WORKFLOW + surveys)

- **Calendar/cap collision:** study cap 3 drafts + 2 re-checks, P0 days
  3–4, waves days 5–8, board day 9 (`WORKFLOW.md` lines 175–193).
  Tier 1 already contains the unpriced decimal-conversion program (§3)
  and unbuilt oracle/board harnesses (§4). "If time allows" Tier 2
  without per-family entry criteria (oracle built, seam frozen, gate
  measured) will consume verifier passes the loose cap then pressures
  to waive (OWNER rule 6 via `WORKFLOW.md` line 177).
- **Planted-fault surface:** verifiers run on planted copies
  (`WORKFLOW.md` planted-fault protocol); each Tier 2 family multiplies
  plant shapes and grading load at the single end-of-round reveal.
  Tail families with project-owned references (min/max, augmented) are
  exactly where a verifier cannot borrow Berkeley to catch a plant.
- **Board-time contention:** single-holder lock protocol (kit
  `BOARD.md`) + unproven transport (§4.2) means board samples are the
  scarcest resource; Tier 2 families should be host-gated with board
  spot-samples only, or they starve Tier 1 board conformance.
- **Claim creep:** every Tier 2 family added under a "754" banner
  inherits correct-rounding/canonical/exception `shall`s (S1 §5
  headnote). SF-0 should require each Tier 2 line to state its claim
  level (754-conforming / ULP-budgeted approximation / API-compatible
  only) — the SDK incumbent's vague "don't support all the features of
  a fully compliant implementation" (S3 §2.2, lines 384–386) is the
  anti-pattern.

## Auditor's closing notes

- Evidence health overall: S1 (contract) and S2 (oracles/host traps) are
  strong enough to write SF-0 proposals today; S3 (target) is strong on
  *reading* and explicit that nothing ran; S4 (workload) is strong on
  inventory and explicit that portability is unrun. The gaps are
  concentrated where this report marks them: decimal oracle, conformance
  tail references, flag-state/board execution, numeric targets.
- Suggested SF-0 open-findings list (for the WORKFLOW Phase 2 exit:
  "verifier finds no (a)/(b), or draft cap with open findings listed"):
  (1) decimal-conversion oracle unnamed; (2) Berkeley tail coverage
  unconfirmed pending header check; (3) vector counts/budgets
  unmeasured; (4) interposition route unbuilt; (5) binary16 storage
  type unprobed; (6) board transport/serial unproven; (7) SDK-level
  cycle baselines unproduced; (8) project licence unchosen; (9) IBM
  FPgen terms unverified; (10) hex shall/should sentence unpicked.
  None blocks Logan approving SF-0 *as a plan* if listed; each blocks
  the wave that first depends on it.

## Anything this brief got wrong

1. **"Tier 2" is undefined** in the brief, `WORKFLOW.md`, `PROJECT.md`,
   and S1–S4. Section 5 had to coin a definition; SF-0 must ratify or
   replace it before sizing. An undefined expansion noun in a study
   brief is how scope ceilings fail.
2. **"Audit only [the four reports]" vs ledger discipline:**
   `ledger/README.md` requires reading every ledger file (and re-reading
   before the final report). This audit read `ledger/S1.md`–`S4.md` as
   context while keeping S1–S4 reports as the evidence base; a strict
   "only" reading would have violated the ledger's floor. Future briefs
   should distinguish evidence base from required ledger reads.
3. **Ledger-append shorthand omits measured necessities:** "TMPDIR
   there" alone is insufficient on this host — lead ledger Phase 0 +
   S2 brief correction 8 (S2 lines 655–660) require POSIX `TMPDIR` plus
   Windows-form `TMP`/`TEMP`, Git Bash (sandboxed PowerShell refuses),
   script-file route (inline `bash -c` refused once per lead ledger),
   and author as a plain name (`sf0-evidence-auditor`, tool appends
   `.md`). This audit's append script follows the measured route.
4. **No background work existed to stop:** this parcel started no jobs,
   watchers, or servers (deliberately — S1 recorded the README watcher
   failing under this harness, S1 lines 531–535, and lead ledger records
   the Monitor path as not-yet-watched-to-work). Escalation floor for
   this parcel was therefore ledger reads + this report, stated here so
   the lead does not assume a live watcher covered the audit window.
5. Nothing else in the brief was found wrong: the four reports exist at
   the named paths, Phase 2 + nine questions frame them without forcing,
   and the clean-room/scratch restrictions were followable as written.
