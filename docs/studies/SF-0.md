# SF-0: The plan of record for Muse-Softfloat

Status: **draft for independent verification, then owner approval. No P0 work
starts on this document until Logan approves it.**

Date: 2026-10-26. Author: the lead (Muse Code, muse-wonder-full-1.0).
Evidence: the bootstrap kit's WORKFLOW/PROJECT, the owner's words in
`docs/KICKOFF.md`, surveys S1 (the standard), S2 (authorities and oracles),
S3 (RP2040 and pico-sdk), S4 (REBOUND IAS15), the Wave 0 record in
`docs/RECORD.md`, and the ledger outside this repository. Claims carry
READ / MEASURED / COMPUTED / BELIEVED where the distinction matters. IEEE
754-2019 is cited by clause only; the licensed PDF is never copied here.

## Contents

0. The short answers
1. Why, in the owner's words
2. The conformance contract
3. Architecture, API, and state
4. The authority, the oracles, and discrepancy resolution
5. Gates, controls, and refusals
6. P0: the shared seam, exactly
7. Waves and parcels after P0
8. Board, performance, and size
9. The IAS15 workload and byte identity
10. Metrics and the record
11. What this project does not do
12. Questions for Logan, with recommendations
13. Sources
14. Send-backs: what each draft changed for its verifier

## 0. The short answers

The lead's proposals. Each is argued in the section named; Logan approves or
corrects them at the end of this study (Section 12).

1. **Edition (Section 2.1): IEEE 754-2019.** The owner's PDF is the 2019
   revision (MEASURED: its metadata during Phase 0). No 2008-only operation
   or behaviour is claimed.
2. **Formats (Section 2.2): binary16, binary32, and binary64 are arithmetic
   formats** and their interchange encodings are supported. The required
   claim is staged by wave, but the target is the full Clause 5 required set
   for all three — S1 counted 81 required operation names per arithmetic
   format before cross-format and integer-width instantiation. Clause 9
   recommended functions are Tier 2, added only behind correct-rounding
   gates if time allows (Section 2.7).
3. **Rounding (Section 2.3): all four required binary rounding attributes
   everywhere they apply** (ties-to-even, toward zero, toward +inf, toward
   -inf). Ties-to-away is provided in the operation-named forms the standard
   requires (roundToIntegral and integer-conversion variants); a fifth
   dynamic attribute is Tier 2.
4. **Exceptions and state (Sections 2.4, 3.3): the five Clause 7 flags live
   in caller-owned state.** The core API is pure: rounding and flags are
   explicit inputs/outputs, no hidden globals, no traps. The drop-in layer
   may own per-core state. Clause 8 alternate exception handling is out.
5. **Tininess and NaNs (Section 2.5): tininess detected after rounding**,
   aligning the library, Berkeley specialization/TestFloat mode, and the
   fenced host oracle, and stated in every test expectation. Arithmetic
   NaN results with no NaN input are the default quiet NaN; payload
   propagation follows an explicit SF-0 matrix (Section 2.5) rather than
   an accidental implementation choice.
6. **Interface (Section 3): a small deterministic C API over bit containers
   is the library** (`msf16_t`/`msf32_t`/`msf64_t` as unsigned integers,
   explicit rounding/flags). AEABI helpers and pico-sdk drop-in wrappers
   are a later compatibility layer over that API, never a second semantics.
7. **Targets (Section 8): correctness outranks speed.** Portable C11 core,
   zero core allocation, report cycles/size against the RP2040 bootrom and
   libgcc baselines with placement and clock named. Performance thresholds
   are descriptive budgets set from P0 measurements, not conformance gates;
   assembly only behind the same correctness gates and after evidence.
8. **Dependencies and licence (Sections 4.5, 12): no third-party softfloat
   source is copied into the library** — clean-room implementation from the
   standard. Berkeley SoftFloat/TestFloat and MPFR are test authorities,
   fetched by pinned hash into scratch, never vendored as library source.
   Toolchain pins: Arm GNU Toolchain 14.2.1, pico-sdk 2.3.1, CMake 4.4.4,
   host oracle compiler only through the pinned x86-64 MinGW path. The
   library's own licence is Logan's decision (recommendation in Q12.8);
   REBOUND stays a GPL-3.0-or-later demo workload outside the library.
9. **Authority (Section 4): three authorities with a stated order when they
   disagree** — the standard for meaning, pinned Berkeley SoftFloat 3e as
   the executable semantic authority for what it covers, MPFR (with exact
   rational generation) as the foreign correctly-rounded oracle for decimal
   conversions and hard cases Berkeley does not decide. Host SSE2 is a
   bit-exact foreign oracle only inside its proven envelope. Decimal
   conversions, unspecified-by-Berkeley corners, and our own vectors are
   gated against MPFR/exact arithmetic, never against the implementation.

## 1. Why, in the owner's words

The project and its two halves are stated in `docs/KICKOFF.md`:

> I plan to take part in a hackathon hosted by Meta AI, the goal is to develop an IEEE-754 compliant softfloat for RP2040, for binary16/32/64. The math library is only one portion of the project, the other portion is testing how Meta models handle the methods and systems I use, along with heavy metrics tracking ...

The impact workload and video, added 2026-10-26:

> my idea is to port REBOUND IAS15 to run on the Pico, proving byte identical to the unmodified desktop run in order to utilize that as both a visual demonstration and workload for the library showing actual usecases rather than just a functional library. The demo video will have to carry a significant portion of the weight of the submission, with the math library standing beside it and its product.

And the scope instruction for this study, same day: "Go ahead with SF-0" /
"Looks good, go ahead. The only slight change is more IEEE 754 compliance
if time allows it". The lead reads that as: maximize defensible compliance
breadth in gated tiers (Section 2.7), never by weakening the required-set
claim or its evidence.

## 2. The conformance contract

### 2.1 Edition

IEEE 754-2019 (`is754version2019` true; 1985/2008 false where the API
exposes them). Differences that bite and are therefore designed for, all
READ in S1: there is **no required min/max family** in 2019 (the 2008
`minNum`/`maxNum` moved to recommended 9.6); fusedMultiplyAdd is required;
decimal character conversions are required for arithmetic formats; canonical
encodings and result-canonicalization rules are as 2019 states them. Code
or vectors written against 2008 names are refused unless SF-0 names the
2019 operation they realise.

### 2.2 Formats and the meaning of "supported"

Arithmetic and interchange support is claimed for binary16 (k=16, p=11,
w=5, emax=15), binary32 (p=24, w=8, emax=127), and binary64 (p=53, w=11,
emax=1023), with the exponent widths the standard's Table 3.5 defines.
binary16 is a
non-basic interchange width (S1 section 0): calling it an arithmetic format
is a project choice, and it costs the full Clause 5 surface — homogeneous
operations, every same-radix `formatOf` instantiation, every ordered
format-conversion pair, integer conversions for every supported integer
format, classification, comparisons, and character conversions. SF-0 takes
that cost deliberately; the staged claim in Section 2.7 says what may be
claimed at each wave boundary. Interchange-only binary16 is the recorded
fallback only if Logan accepts it at approval (Q12.2) — the fallback still
owes flag-correct binary32/64 <-> binary16 and decimal/hex character
conversions (S1 section 6, marked BELIEVED application there); direct
binary16-integer conversions are not owed in that posture and would route
through an arithmetic format. It saves arithmetic instantiations, not the
conversion engine.

Integer formats supported by the API: signed and unsigned 8, 16, 32, and
64 bits, realized as the exact-width C integer types. The standard does not
define integer formats; the width set is a library contract and is
exhaustive in the generated header so no conversion is silently missing.

`logBFormat` is fixed as binary64 (the widest supported arithmetic format),
with `logB` results and special cases following the floating-destination
rules S1 recorded. SF-0 refuses a second, integer-`logBFormat` personality
in the core API; an integer-exponent convenience may be a wrapper later.

### 2.3 Rounding

All four binary rounding-direction attributes — `roundTiesToEven`,
`roundTowardZero`, `roundTowardPositive`, `roundTowardNegative` — apply to
every general-computational operation, conversion, and character conversion
the standard subjects to an attribute. Rounding is an explicit value in
the core API (Section 3), never process state. Operations that name their
direction (the five `roundToIntegral*` forms, the ten integer-conversion
forms, ties-to-away variants included) ignore the attribute exactly as
specified. `roundTiesToAway` as a dynamic attribute, and
`roundToOdd`-style internal helpers exposed publicly, are Tier 2 only.

Correct rounding is defined against the infinitely precise result for
every operation the standard subjects to it, including fusedMultiplyAdd
(exact product plus addend, one rounding), squareRoot, scaleB, remainder
(exact when defined), and the character conversions within the Section 2.6
digit limits. No double rounding through a wider supported format is
permitted as an implementation shortcut unless a proof and a gate in SF-0's
successor record show it cannot differ; the default is wide exact integer
intermediates with sticky capture (Section 3.2).

### 2.4 Exceptions, flags, and Clause 8

The five flags — invalid operation, division by zero, overflow, underflow,
inexact — are raised exactly under Clause 7 conditions, including the
overflow/underflow coupling to the rounding attribute and the
overflow-to-infinity vs overflow-to-max-finite outcomes. There are no
traps, no trap handlers, and no resumption: Clause 8 alternate exception
handling is **out of the conformance claim** (its conformance clause is
conditional; refusing it is cheaper than faking it, and neither the RP2040
environment nor IAS15 needs it).

Flag state is data, not a place: the core API takes a caller-supplied
`msf_flags_t *` (bitwise-OR accumulation; NULL means "do not record" only
where SF-0's header explicitly permits it — the default generated
signatures require a non-null pointer so a caller cannot lose flags by
accident). `lowerFlags`, `raiseFlags`, `testFlags`, `testSavedFlags`,
`restoreFlags`, and `saveAllFlags` operate on that same caller-owned word
plus an opaque saved-flags value. The drop-in layer (Section 3.4) owns one
flag word per core and documents the interrupt caveat; the core never does.

### 2.5 Tininess, zeros, infinities, NaNs

- **Tininess: after rounding**, for every operation and conversion, on
  every format. Rationale: it is Berkeley SoftFloat's default detection
  mode and the believed x86 SSE choice (S2 section 3.3), so the semantic
  authority, foreign FPU oracle, and library can be configured to one
  side; more importantly the choice is explicit. The specialization,
  TestFloat mode, and report header must all state it, because the
  default vector tolerance would otherwise pass either side silently.
  Underflow is then signaled exactly as Clause 7 requires for that choice
  (tiny after rounding and inexact, subject to the stated exact cases).
  Targeted smallest-normal-boundary cases per format, mode, and
  conversion direction are part of every gate.
- **Zeros and infinities** follow Clause 6 sign rules as extracted by S1;
  product/quotient sign XOR, sum-of-zeros rules per rounding attribute, and
  the specified signed results for squareRoot, remainder, conversions, and
  character output are table-driven in tests, not rediscovered per parcel.
- **NaNs:** every supported encoding with all-ones exponent and non-zero
  trailing field is a NaN. The project adopts the recommended polarity:
  the trailing field's most significant bit is 1 for quiet and 0 for
  signaling. The **default quiet NaN** per format is positive, quiet bit
  set, all other trailing bits zero. Results use this matrix:
  (a) an invalid operation with no NaN input delivers the default quiet
  NaN; (b) a signaling NaN input signals invalid (outside the character
  conversions) and delivers that operand quieted, preserving sign and
  the payload bits that survive conversion; (c) quiet NaN inputs deliver
  the first NaN operand in operand order, preserving sign and payload —
  for fusedMultiplyAdd the order is multiplicand, multiplier, addend,
  and the project ruling for the implementation-defined 0 x infinity
  with a quiet-NaN addend is: signal invalid and deliver the addend.
  Every delivered NaN is a canonical encoding of its format; where
  narrowing would truncate a quiet payload to the infinity pattern, the
  default quiet NaN is returned (no invalid is claimed for truncating a
  quiet payload itself; signaling inputs still signal under (b)).
  Copy-class
  operations move bits exactly. Payload propagation beyond (a) is a
  standard `should`, adopted here as a project promise from the start —
  therefore NaN cases in project-owned vectors compare payloads exactly,
  while third-party oracle comparisons state their masking explicitly
  (Section 4.3). Signs follow the operation rules and otherwise this
  matrix; no operation invents a NaN sign exception the standard does
  not name.
- **Canonicalization:** non-canonical encodings do not exist for these
  binary interchange formats beyond the NaN rules above; `isCanonical`
  is therefore true for every bit pattern of the three widths, and
  `convertFormat` same-format still quiets signaling NaNs with invalid
  signaled (S1 section 1.3), unlike `copy`.

### 2.6 Character conversions

Decimal: `convertFromDecimalCharacter` and `convertToDecimalCharacter`
are correctly rounded for significant-digit counts 1..H in both
directions with correct exceptions, where **H = 20** (Pmin(64)=17, +3;
the combined-format consequence S1 marked BELIEVED and SF-0 adopts as the
floor — implementations may accept more only through the standard's
beyond-H route). Output at or above Pmin digits (5/9/17) round-trips. Output
spellings are lowercase `inf` and `nan` (with a leading sign where the
format/sign requires one); input acceptance is the exact case-insensitive
grammar S1 extracted from 5.12.1, enumerated as a test table in P0
including payload suffixes this implementation emits.
The conversion specification is a small explicit struct in the API
(precision, scientific/fixed style selector, minimum digits), not a
printf format string; `printf`-family formatting is a separate later
layer and is refused as the conformance surface. String conversion may
allocate nothing: callers pass buffers, and the exact required length is
returned on truncation with no partial-write ambiguity (the header in P0
fixes the rule; the study decision is: return the would-be length, write
nothing if the buffer cannot hold the result plus NUL).

Hexadecimal-significand conversions are in the required set (S1 section
1.3 records the shall/should tension; SF-0 rests on the implementation-
level `shall` in 5.4.3/5.12): exact output with enough digits by default,
correctly rounded explicit-precision output and input.

### 2.7 Compliance tiers (the owner's "more if time allows", made safe)

- **Tier 1 (the conformance claim):** everything in Sections 2.1-2.6 for
  all three arithmetic formats, gated per Section 5. Nothing outside
  Tier 1 may be described as required, and no Tier 1 item may be dropped
  to fund Tier 2.
- **Tier 2 (expanded compliance, only after Tier 1 gates hold):** in
  order — Clause 9.6 minimum/maximum family and 9.7 NaN payload
  get/set operations; dynamic rounding-mode get/set wrappers and a
  `roundTiesToAway` attribute in the wrapper layer and any public
  `roundToOdd`-style helper; augmented addition, subtraction, and
  multiplication; reduction operations (exception discipline
  only — their numeric results are implementation-defined, so no
  bit-exact conformance claim attaches); then correctly rounded
  Clause 9 mathematical functions **one function at a time**, each only
  with a Table-Maker-grade worst-case argument and MPFR/CORE-MATH-class
  oracle evidence (S2 section 4 item 6). Entry criteria per item: its
  oracle is built, its claim level is declared in its brief
  (754-conforming, ULP-budgeted approximation, or API-compatible only —
  the latter two never under a conformance banner), and its negative
  controls exist. A Tier 2 function that cannot meet its bar is refused,
  not shipped approximately under a conforming name.
- **Never in this project:** binary128 or decimal formats, Clause 8
  alternate exception handling, traps, non-IEEE fast-math modes, flush-
  to-zero/denormals-are-zero modes, and any "mostly compliant" marketing
  label. If schedule forces a narrower claim, the record says exactly
  which tier and wave held at submission.

## 3. Architecture, API, and state

### 3.1 The shape

Portable C11, clean-room from the standard. One public header
(`include/muse_softfloat.h`, generated in part from the operation table in
Section 6 so the cross-format matrix cannot drift), a format-parameter
header generated from one machine-readable format table, per-format
translation units over shared exact-integer kernels, and a separate
compatibility directory for AEABI/pico-sdk wrappers. No third-party
softfloat source in the library tree: Berkeley SoftFloat is legally
copyable (BSD-3) and is refused anyway as project policy, because the
deliverable is our implementation and its measured process; libgcc
soft-fp source is refused on licence; compiler-rt is a read-only design
reference at most, with per-file header checks if ever consulted (S2
section 5).

### 3.2 Internal model

Every operation decodes to (sign, class, exponent, significand) and
computes on exact integers wide enough that the only rounding event is
the final pack: at minimum 128-bit intermediates for binary64 products,
wider fixed accumulators (P0 fixes the exact widths per operation class,
with a proof note per width) for fusedMultiplyAdd alignment and decimal
scaling, and remainder/sticky capture for division and square root so
ties and directed modes are decided from exact information. Wide integer
helpers are implemented in-tree over 32-bit limbs; compiler `__int128`
may be used on host builds only, and the target build must not silently
acquire floating-point helpers — P0's symbol scan (Section 5.3) is the
gate, not a hope. Decimal conversion uses exact big-integer scaling
bounded by H and the destination exponent range; no floating-point
arithmetic anywhere in `src/` (the scan refuses float/double-typed
operations in core translation units by construction and by symbol).

### 3.3 Public API

Types: `typedef uint16_t msf16_t; typedef uint32_t msf32_t; typedef
uint64_t msf64_t;` — bit containers, with `_from_float`/`_to_float`
bit-cast helpers only in the wrapper layer. `msf_rounding_t` enumerates
the four attributes. `msf_flags_t` is a `uint32_t` mask with the five
Clause 7 bits named. Homogeneous operations read
`msf64_add(msf64_t a, msf64_t b, msf_rounding_t rm, msf_flags_t *flags)`;
`formatOf` operations name destination then operation then sources
(`msf32_add_f64_f64`, `msf64_fma_f32_f32_f64`-style generated spellings
fixed once in P0's operation table and not improvised per parcel);
integer and format conversions follow the same spelling rule. Sign-bit
operations and classification take no rounding and no flags pointer.
Character conversions take the Section 2.6 specification struct and a
caller buffer. This is deliberately not `<fenv.h>` and not C operator
overloading: determinism and testability outrank familiarity at the core.

### 3.4 Compatibility layers (after the core)

1. **AEABI/toolchain helpers** (`__aeabi_fadd` and family, the exact wrap
   surface S3 section 1.2 enumerates) implemented over the core with
   per-core wrapper state (rounding fixed to ties-to-even there unless a
   documented setter changes it; flags accumulated per core and readable
   through the same flag operations). The interrupt caveat is part of
   that contract: per-core state is shared by thread and IRQ execution on
   the same core, never between cores; the wrapper does not implicitly
   save or restore it across interrupts or RTOS task switches, so an IRQ
   or task layer that uses these helpers must save/restore the exposed
   state itself or call the stateless core API with its own state. P0's
   wrapper self-test covers second-core isolation and same-core IRQ
   interleaving. This is what IAS15 links against.
2. **pico-sdk drop-in:** a NEW float/double implementation flavour in the
   SDK's own CMake shape (not an edit of SDK files), selected per target
   like `pico`/`compiler`/`none`, reusing the SDK's divider save/restore
   convention if — and only if — a kernel uses the SIO divider (S3
   sections 1, 3, 5). Bootrom FP routines are never called by the core or
   the drop-in; S3 section 2.2 documents why (denormal flushing, NaNs as
   infinities, no flags).
3. **`float`/`double` operator use** in application code arrives only
   through layer 1/2; the library never asks a user to trust compiler
   floating semantics on Cortex-M0+ beyond helper calls.

## 4. The authority, the oracles, and discrepancy resolution

### 4.1 Three authorities, in this order

1. **Meaning: IEEE 754-2019**, cited by clause. Where the standard leaves
   a choice (tininess, NaN payload details, H, logBFormat), SF-0's stated
   choice above is the meaning for this library.
2. **Executable semantic authority: Berkeley SoftFloat Release 3e**,
   pinned to the official archive by SHA-256 at P0 fetch time (never a
   moving branch), built only as a host test oracle in scratch with the
   specialization matching Section 2.5's tininess choice and this
   library's NaN matrix configured or, where it cannot be configured,
   compared under the masking rules of Section 4.3. Its coverage is the
   basic operations, conversions among binary formats and integers,
   rounding modes and flags (S2 sections 1-2; the official page confirms
   the format/operation span and that decimal character conversion is
   outside it).
3. **Foreign correctly-rounded oracle: MPFR** (4.2.2 already installed on
   this host, MEASURED by S2; version pinned in the fetch record) driven
   through exact rational/integer construction for: decimal character
   conversions, hardest-to-round division/square-root/FMA case
   generation, cross-checks of Berkeley on sampled classes, and any
   Tier 2 mathematical function. mpmath may prototype generators but is
   never the deciding oracle (S2 measured its model limits).

### 4.2 Host FPU oracle: a narrow, fenced envelope

Host SSE2 is bit-exact for binary32/64 add/subtract/multiply/divide,
square root, explicit FMA, float/int conversions, and comparisons in the
four hardware modes — **only** through the pinned x86-64 compiler path
with `-ffp-contract=off`, no fast-math, explicit MXCSR state (FTZ/DAZ
clear), no `long double`, and NaN comparison by class not payload (the
compiler-path trap and contraction refusal are MEASURED in S2 section 3;
parts of the architectural exactness and tininess account there are READ
or BELIEVED, as tagged). It decides nothing outside that envelope:
no ties-to-away, no binary16 arithmetic, no transcendentals, no decimal.
Every oracle build script asserts `-dumpmachine` and `FLT_EVAL_METHOD==0`
before compiling; the 32-bit x87 default compiler on this host is refused
by name in Section 5.3.

### 4.3 Vectors and comparison rules

Gate order per operation class (S2 section 4): Berkeley TestFloat vectors
at the highest level the budget allows with per-case provenance retained;
exhaustive binary16 unary and binary32 unary sweeps; directed
hardest-to-round binary64 division/square-root/FMA families generated
against MPFR; IBM Haifa FPgen vectors only after their licence/terms are
verified at fetch (unverified today — refused until then); project-
generated adversarial families (cancellation, binade boundaries, subnormal
crossings, sticky patterns, conversion extremes) with seeds recorded.
Comparison is exact on result bits and flag word after the oracle's own
declared tolerances are removed by configuration where possible; where an
oracle tolerates NaN payload/sign or tininess differences, the runner
applies the SF-0 matrix explicitly and prints the masking it used. A
vector whose provenance (source, generator, seed, oracle version) cannot
be printed by the runner does not count toward a gate.

Coverage is per **instantiation**, never per family name. P0 generates a
coverage ledger from the operation table: every instantiation names its
deciding authority (Berkeley, MPFR/exact, fenced host FPU, or a named
project-owned exact reference), its vector set, and its comparison rule.
The conformance tail that survey evidence leaves unconfirmed in Berkeley
(nextUp/nextDown, scaleB/logB, totalOrder family, classification,
sign-bit operations, flag operations as a state machine, hex conversions)
gets small project-owned exact references over integers, rationals, and
bit decoding — test code only, independently reviewed like any oracle,
and replaced if Berkeley header-level bring-up proves coverage. No
instantiation may sit in the ledger as "unconfirmed" at a wave gate.

Decimal character conversions have their own exact authority design
(proposal, to be built and gated in P0 before any decimal parcel):
binary-to-decimal expands the
value exactly as an integer times a power of two and rounds the resulting
decimal digit sequence once; decimal-to-binary parses the digit string
and decimal exponent as arbitrary integers, forms the exact rational,
and scales/rounds once with remainder evidence. MPFR cross-checks the
same cases at increasing precision — starting at least 64 bits beyond the
destination precision and doubling until two precisions agree — with an
exponent range wide enough that MPFR's range does not impose the answer
and subnormalization represented in the checker. Any split among exact
integer computation, MPFR, and the implementation stops the gate under
Section 4.4. The designed sample covers every format and rounding mode
at digit counts {1, 2, Pmin-1, Pmin, Pmin+1, H-1, H}, tie digit strings,
subnormal/exponent boundaries, wide-exponent inputs, and malformed or
special-value grammar; exhaustive binary16 output/input and binary32
round-trip sweeps join at their wave gates where runtime permits.

### 4.4 When authorities disagree

Stop the parcel; do not average. The lead classifies the disagreement as
implementation defect, oracle defect/limit, or standard-reading dispute,
in that investigation order, and records it in the ledger before any code
changes. A standard-reading dispute is decided by the clause text with a
second reader (a verifier task), and SF-0 is restated if the reading
changes. An oracle defect is fenced by naming the exact operation class
and input family in the refusal table; the gate for that family moves to
the remaining authority. No authority is ever outvoted by test count.

### 4.5 Sources, licences, and the clean room

The library is implemented from the standard and this study. Third-party
material may be **read** for interface facts (SDK headers/CMake, AEABI
names, REBOUND source for the separate workload) and **executed** as
oracles (Berkeley, MPFR, host silicon). It may not be copied into `src/`
or `include/` — including BSD-3 Berkeley code (policy), Apache-2.0-with-
LLVM-exception compiler-rt code (policy; design reference only), and
GPL libgcc soft-fp (licence). Fetch records (URL, version, archive
SHA-256, licence file hash) live in the metrics/provenance record P0
creates; fetched trees live in scratch, outside the repository. REBOUND
is GPL-3.0-or-later: the extracted workload is a separate program that
links the library through its public/wrapper interface, carries its own
licence notices, and no REBOUND code or tables enter the library tree;
the coefficient tables the workload needs stay on the workload side of
that line, pinned as hex bit patterns there (Section 9). The forbidden
clean-room source named in the kit remains forbidden in every brief; any
landing on it is disclosed in the ledger and escalated immediately.

## 5. Gates, controls, and refusals

### 5.1 The runner P0 must deliver

One front door (`tools/run.sh`, driven from Git Bash on this host) with
named budgets, printed before results: what ran by category, how many
vectors by provenance, skips by name with reasons, oracle versions and
hashes, compiler identification, board identity for board budgets, and
the tininess/NaN-matrix choices. Budgets:
- `smoke` (minutes): build host+target, symbol/type scans, unit vectors
  per implemented operation class, board hello/hash if the board is free;
- `standard` (the merge gate): full vector sets for everything claimed so
  far, exhaustive sweeps scheduled per wave, oracle cross-checks;
- `board` (lead-run under the board lock): the same sampled vectors on
  RP2040 through the serial harness, compared bit-for-bit with host results;
- `bench` (never a correctness verdict): cycles and sizes with placement,
  clock, and cache state printed.
Exit status only counts with the printed inventory; a green run that
cannot name its vectors is a failed run.

### 5.2 Negative controls (permanent, named in briefs)

At minimum, each watched to fail before it is trusted: one corrupted
expected-result bit; one wrong-rounding-mode run; the RP2040 bootrom's
documented denormal-flush and NaN-as-infinity cases (must be caught as
nonconformances, proving the gate can see the delta we exist to close);
one deliberately wrong flag bit; one stale-binary replay (manifest hash
mismatch must refuse); one skipped-vector count mismatch; one wrong
board-identity run; one host-oracle run under the refused x87 compiler
path (must be refused by the startup assertions); one wrong-tininess-
polarity build at the smallest-normal boundary; one wrong NaN payload or
missing signaling-NaN invalid flag; one wrapper-state leak (same-core IRQ
interleaving and second-core cross-talk); one decimal-oracle run with a
too-narrow exponent range or subnormalization disabled. Planted faults in
parcels follow the kit protocol from Wave 1 onward (Section 7), keys in
the lead's scratch only, revealed once near the end.

### 5.3 Refusals by name

Refused in the library and its gates: host `float`/`double` arithmetic in
core code; compiler floating helpers in target core objects (symbol scan
over a named denylist); bootrom FP entry points; `-ffast-math` and
friends anywhere; FMA contraction in any build that produces compared
results; the 32-bit x87 host compiler for oracle work; dynamic allocation
in the core; traps/signals; claiming an operation whose wave gate has not
closed; vectors without provenance; benchmarks quoted without placement
and clock; copying third-party softfloat source (Section 4.5); and any
use of the forbidden clean-room source. A refusal can be lifted only by
restating this study with the owner.

## 6. P0: the shared seam, exactly

P0 is the lead's own work, committed and verified before any parcel is
dispatched. It delivers, and only what follows:

1. `docs/studies/SF-0.md` approved form linked from the README status and
   `AGENTS.md` (front door, authority, discipline paragraph filled from
   Sections 4-5 of this study).
2. The operation table (one machine-readable file) enumerating every
   Tier 1 operation instantiation, from which `include/muse_softfloat.h`
   declarations and the vector-runner dispatch are generated; a
   generated-file check in the runner refuses drift.
3. Format parameter generation from one table (widths, precisions,
   exponent ranges, Pmin, canonical NaN patterns) with the same drift
   check; no hand-typed duplicate constants in per-format files.
4. Internal exact-integer helpers (wide add/sub/mul/shift with sticky,
   normalize, round-and-pack for one format end-to-end as the exemplar),
   plus classification and sign-bit operations, the six flag operations
   over caller-owned state, and the `is754version*` predicates for all
   three formats as the first gated operations.
5. Oracle bring-up, before any parcel depends on a vector: fetch the
   pinned Berkeley archives into scratch with hashes recorded, build
   through the Section 4.2 pinned compiler path, run `testsoftfloat` as
   the build self-check, verify at header level which operation families
   the build actually covers (closing Section 4.3's unconfirmed cells),
   and measure real vector counts/runtimes on sampled functions so the
   Section 5.1 budgets are priced from measurement. Vectors stream
   (generate-and-replay, seeded subsampling); nothing budgets storage
   from survey estimates.
6. The runner of Section 5.1 with budgets wired, vector format + replay
   for the operations in item 4, the coverage ledger of Section 4.3, and
   the negative controls of Section 5.2 that apply to them.
7. The board harness: picotool load under `ledger/board.lock`, USB CDC
   vector replay with whole-run hash back to the host, board unique ID
   read into `docs/BOARD.md`, reset/re-entry procedure measured and
   written down, one smoke vector set passing on the rev B2 board. At
   study date no board serial channel has been proven (the enumerated
   COM1/COM5 are not the board), so establishing CDC is itself P0 scope
   and risk. P0
   proves flash -> run -> read-back for one batch and defines which seeds
   and operand classes form the later on-silicon sample; full-volume
   board replay is explicitly not promised. One interposition route is
   also built end-to-end in P0 (a hello executable proving `--wrap`
   resolution to the new flavour for the exemplar operations, including
   the Section 3.4 second-core/IRQ wrapper self-test), so Wave 3
   does not discover the mechanism.
8. Metrics scaffolding for waves: briefs/corrections/escalations/plants
   JSONL shapes beside the shipped extractor outputs, so Wave 1 numbers
   are recorded as they happen.
9. Benchmark skeleton only: placement/clock-labelled cycle and size
   reporting for the exemplar operations, including producing the
   SDK-harness bootrom/libgcc baseline numbers those reports quote.
   No performance claim in P0.

P0 acceptance (its own verifier, Spark): the runner refuses each named
negative control; generated files regenerate byte-identically; the
symbol scan is clean; board smoke hashes match host; the interposition
hello and Section 3.4 wrapper-state tests pass; every Wave 1 brief can
name its owned files without overlap.

## 7. Waves and parcels after P0

One round, several waves. Parcels own per-format or per-subsystem files;
shared helpers and generated tables are lead-owned after P0 (a parcel that
needs them changed escalates instead of editing). Every brief carries a
time box, a scope ceiling, named negative controls, and this study's
section numbers instead of restated semantics. Verifiers are Spark
(Workflow), parcels are Wonder unless a brief says otherwise; verifier
passes are capped by the loose cap, and only (a) regressions and
(b) wrong answers send work back — false sentences in reports are
restated at merge. Merges are serial by the lead with the `standard`
budget after each; `board` budget runs are lead-only under the lock.

- **Wave 1 — binary32 and binary64 homogeneous core.** Two format parcels
  in parallel (add/sub/mul/div/sqrt/FMA, format conversions between the
  pair, integer conversions, comparisons including the totalOrder family,
  roundToIntegral family,
  nextUp/nextDown, remainder, scaleB/logB), each gated by TestFloat +
  exhaustive binary32-unary + directed binary64 hard families. Exit:
  binary64 basic operations are strong enough to start the IAS15
  extraction in parallel with Wave 2.
- **Wave 2 — binary16 arithmetic and the formatOf matrix.** The binary16
  parcel (full homogeneous set by widening through exact internal forms,
  never by double rounding through binary32 unless the gate proves the
  specific operation immune), plus the generated cross-format
  instantiations for all ordered pairs. Planted-copy verification is in
  force from Wave 1, so Wave 2 continues it rather than introducing it;
  keys stay in the lead's scratch.
- **Wave 3 — character conversions and compatibility.** Decimal (H = 20)
  and hex conversions for all formats against MPFR/exact generation;
  AEABI helpers and the pico-sdk flavour; board conformance budget over
  the claimed set so far; benchmarks against bootrom/libgcc baselines.
- **Wave 4 — Tier 2, only on slack:** Section 2.7's ordered list, one
  gated item at a time, planted-copy verification continuing. Anything unfinished
  here is recorded as not claimed, never half-claimed.
- **Workload track (parallel after Wave 1):** IAS15 extraction, desktop
  reference, Pico port, byte-identity gate, then the programmatic video
  build. It consumes the library; it never feeds semantics back into it.

## 8. Board, performance, and size

The board is the owner's RP2040 rev B2 (ROM V3) on this desktop, lead-held
under `ledger/board.lock` (`docs/BOARD.md`). The conformance delta is the
yardstick's reason: the bootrom correctly rounds its five basic operations
only subject to flushing subnormals and treating NaNs as infinities, with
one rounding mode and no flags (S3 section 2.2) — so cycle comparisons are
reported as "cost of conformance" against published ROM averages (READ:
e.g. _fadd 71, _ddiv 183 cycles, S3 section 4.1) and libgcc, never as a beat-
the-ROM gate. Benchmarks state placement (flash vs RAM sections), clock
(default 125 MHz unless the run changes it), cache state, and code/RAM
sizes from the linker map; the SDK's own RAM-resident benchmark
methodology is the comparison shape. Working budgets, to be tightened
from P0 measurements and recorded as goals rather than conformance gates:
basic binary64 operations within 2x of ROM averages when RAM-resident,
core static RAM of zero bytes (wrapper per-core state excluded and
counted), stack bounded and measured per operation class, whole-library
flash reported per format so a user can link one format without paying
for three. The SIO hardware divider may be used only behind the SDK's
save/restore convention (S3 section 3.1); interpolators are refused in
AEABI-helper paths until a claim/save design is separately verified
(S3 section 3.2).

## 9. The IAS15 workload and byte identity

Source pin: REBOUND 5.2.2 at commit 262a9cc (S4 section 0), GPL-3.0-or-
later, extracted subset only (~750-950 lines: IAS15 step core, one direct
gravity core — upstream-default BASIC unless the workload brief chooses
COMPENSATED and says why — minimal simulation state, warning sink stub;
S4 section 6.2). The desktop reference is the **same extracted source**
built with the strict flag set of S4 section 5.2 (`-std=c99`,
`-ffp-contract=off`, no fast-math family, no `-march=native`, OpenMP/MPI/
server/OpenGL off), and "unmodified desktop run" in every claim means
exactly that build — SF-0 refuses the phrase for distribution-default
builds whose contraction behaviour is target-dependent. Two different
kinds of pin are kept apart: extraction pins delete the variational,
collision, and additional-force branches from the subset on both sides;
runtime configuration pins BASIC gravity, the upstream-default PRS23
timestep criterion, OpenMP off, and no MEGNO particles instantiated.
Initial conditions are supplied as binary64 bit patterns (hex), never
decimal text. Coefficient tables are generated from the source decimal
literals by an MPFR conversion at no less than 256-bit precision and
independently checked against the strict-host compiler's literal
conversion for every entry; only the resulting verified hex bit patterns
are carried on both sides, and any disagreement stops the workload brief
(S4 sections 1.2, 6.2). Comparison is field-parsed: full particle state
plus simulation time and integrator internal state named in the workload
brief, hashed (SHA-256 over a specified little-endian field order) at
specified step counts; whole upstream archive files are **not** compared
byte-for-byte (S4 section 4.3 shows why they cannot match). A mismatch
bisects by step hash to the first divergent step, then by operation
replay against the Section 4 authorities — the workload is a consumer of
conformance evidence, never its source. The demo system (particle count,
timescale, duration) is chosen in the workload brief for visual clarity
inside measured Pico step costs; accuracy claims quote the hash evidence,
not the picture.

## 10. Metrics and the record

The measured half continues on the shipped rails: `round_metrics.py`
tables from JSONL in `docs/metrics/`, transcript extraction by
`tools/extract_session_metrics.py` with explicit cutoffs and annotations,
one append-only entry per wave in `docs/RECORD.md` in the Wave 0 skeleton
(owner asks verbatim beside lead readings, the chain with verifier counts,
measured numbers with units, slips attributed, known limits merged). P0
adds the missing input shapes (briefs with time boxes and scope ceilings,
brief corrections, escalations, plants with reveal accounting) so later
entries are recorded as events happen. Model tiers are part of the data:
lead and parcels on muse-wonder-full-1.0, verifiers/re-checkers on
muse-spark-1.3 via Workflow (measured dispatchable; native spawns have
no model knob), any exception named in its brief. Commit bodies state
what occurred, the verification behind the commit, and the ledger files
and entry stamps to open first (owner rule, 2026-10-26), and every
AI-authored commit carries its model's Co-Authored-By trailer.

## 11. What this project does not do

No binary128, no decimal formats, no Clause 8 alternate handling, no
traps, no approximate/fast math modes, no dynamic allocation or floating
arithmetic in the core, no bootrom floating-point calls, no copied
third-party softfloat source, no compliance claim for an operation
before its gate closes, no performance claim from `bench` alone, and no
video claim stronger than the hash evidence under it.

## 12. Questions for Logan, with recommendations

SF-0 asks for approval of the whole; these are the decisions inside it
that are the owner's to correct individually.

1. **Edition:** approve IEEE 754-2019 as the sole contract? (Recommend
   yes — it is the edition in hand and the surveys are built on it.)
2. **binary16 posture:** approve full arithmetic binary16 as Tier 1,
   staged after binary32/64, over the cheaper interchange-plus-conversions
   fallback? (Recommend full arithmetic; the fallback saves less than it
   appears because conversions remain.)
3. **Tier 2 order:** approve Section 2.7's order (min/max + payloads,
   dynamic modes, augmented ops, reductions, then one-at-a-time
   correctly rounded mathematical functions) as the only way extra time is
   spent? (Recommend yes.)
4. **State model:** approve caller-owned flags/rounding in the core, with
   per-core state confined to the compatibility layer? (Recommend yes.)
5. **Authority order:** approve standard > pinned Berkeley > MPFR/exact
   generation > fenced host FPU, with the stop-and-classify disagreement
   protocol? (Recommend yes.)
6. **Copy policy:** approve "no third-party softfloat source in the
   library tree" even where licences would allow copying? (Recommend
   yes — it is the clean-room claim the submission stands on.)
7. **IAS15 definition:** approve "unmodified desktop run" = same
   extracted source, strict flags of Section 9, field-parsed hash
   comparison (not whole archive bytes)? (Recommend yes.)
8. **Library licence:** choose the library's licence (recommend a
   permissive licence — MIT or BSD-3-Clause — to keep the library cleanly
   separable from the GPL workload); and confirm the standing-rule/cap
   defaults in `docs/KICKOFF.md` as amended by your standing git
   permission, Spark-verifier direction, commit-body rule, and this
   study. The kit-zip builder hash (`d530b3ce...d33d8f01`) and any
   clean-room fencing beyond rule+disclosure+audit can be settled in the
   same reply.
9. **Settled-in-body choices:** approve or correct individually the
   recommendations the eight questions above would otherwise carry only
   by whole-study approval: tininess after rounding; the NaN matrix of
   Section 2.5; Clause 8 out; no fifth dynamic rounding attribute in
   Tier 1; binary16 stored as `uint16_t`; portable C11 first with
   descriptive (not conformance-gating) performance goals and the
   toolchain pins of Sections 0 (items 7-8) and 8; and the language-defined choices
   H = 20, `logBFormat` = binary64, integer formats 8/16/32/64 signed
   and unsigned, and lowercase `inf`/`nan` output spellings.
   (Recommend approving as a package unless one item is named.)

## 13. Sources

Local, by file: the kit's WORKFLOW.md and PROJECT.md; `docs/KICKOFF.md`,
`docs/RECORD.md`, `docs/HARNESS.md`, `docs/BOARD.md`, `AGENTS.md` in this
repository; surveys S1-S4, the independent SF-0 evidence audit, and proofs
in the (non-repository) scratch and
ledger named in the Wave 0 record and Section 14; IEEE 754-2019 (owner's licensed PDF,
cited by clause through S1); the RP2040 datasheet and pico-sdk 2.3.1
checkout as cited by S3; REBOUND 5.2.2 tree as cited by S4.

Web (inspected during study preparation):
- Berkeley SoftFloat: https://www.jhauser.us/arithmetic/SoftFloat.html
- GNU MPFR: https://www.mpfr.org/
- REBOUND: https://github.com/hannorein/rebound
- Raspberry Pi Pico SDK: https://github.com/raspberrypi/pico-sdk

## 14. Send-backs: what each draft changed for its verifier

Draft 1: initial study. Verifier findings and the changes
they force are appended here per pass, keeping each pass's (a)/(b) counts
beside the new text, until the owner approves; after approval this file
is restated only by a new dated section, never silently.

Draft 2 (after verifier-sf0 pass 1 on draft 1: NOT READY, (a) 0, (b) 6,
notes 15; ledger/verifier-sf0.md 2026-10-26 13:16:25
and scratch/verifier-sf0/report.md): B1 tininess in Section 0 corrected
to after rounding (Section 2.5 already proposed it); B2 exponent widths
stated per format (5/8/11); B3 host-oracle evidence retagged; B4
interchange-only fallback no longer owes direct binary16-integer
conversions; B5 quiet-payload truncation no longer claims an invalid
signal the cited text does not record; B6 augmented subtraction named.
Notes dispositioned in the same pass: decimal authority and sampling are
now designed in Section 4.3; coverage is per instantiation with
project-owned exact references for the tail; planted-copy verification
runs from Wave 1; board scope reads "sampled"; tininess/NaN/IRQ/decimal
negative controls added; totalOrder, flag operations, and version
predicates have named homes; the Section 1 quotation is ellipsized; the
interrupt contract and unproven serial channel are written down; IAS15
extraction pins are separated from runtime configuration and its
coefficient converter is named; Q12.9 puts settled-in-body choices to
Logan explicitly. The independent evidence audit that preceded draft 1
(scratch/sf0-evidence-auditor/report.md, ledger 2026-10-26 12:37:24) is
dispositioned by the same changes; its remaining open items are the
licence/timing decision in Q12.8 and the SDK-level benchmark baseline,
whose production P0 item 9 now tasks. No proposal reversed; corrections
and obligations added in this pass are the design detail listed above.

Draft 3 (after rechecker-sf0 on draft 2: NOT READY, (a) 0, (b) 2,
notes 4; report in scratch/rechecker-sf0/report.md, ledger entry filed
by the lead from the rechecker's staged body because its sandbox could
not run the ledger tool): the approval-question count in the commit
message is corrected to nine at commit time; the sentence above that
claimed no substance changed is replaced; the Sections 0/8 citation,
SDK-baseline production task, decimal-design proposal tag, and READ tag
on the published ROM averages are corrected. No conformance proposal
changed in this pass.



