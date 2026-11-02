# S1 — Surveyor (the standard): IEEE 754-2019 required vs recommended surface for binary16/32/64

Author: S1 (read-only surveyor). Date of work: 2026-10-26.
Source read: `754-2019.pdf` at the workspace root (owner's licensed copy, outside every repo).
It was read only in this workspace, via `.venv/Scripts/python.exe` + pypdf, script files under
`scratch/S1/` (`extract_pdf.py`, `search_extract.py`, `count_ops.py`), extracted text under
`scratch/S1/extract/`. The PDF was not copied into any repo and no paragraph of it is reproduced
here; findings are paraphrased and cited by clause and page. Operation names (e.g.
`fusedMultiplyAdd`) are single technical terms of the standard, cited as names.

## How to read this report

- Every substantive claim is tagged **READ** (read in the cited clause), **MEASURED** (produced
  by running the extraction/count scripts named above), or **BELIEVED** (inference by S1).
- Page cites give both numbers as `(printed p. N / PDF p. N+1)`. MEASURED: the extracted
  standalone page numeral on every checked body page equals PDF page minus one
  (`count_ops.py` output, `scratch/S1/extract/counts.txt`); the PDF has 84 pages and a
  104-entry outline (`extract_pdf.py`).
- Normative vocabulary, READ Clause 1.6 (printed p. 12 / PDF p. 13): `shall` is mandatory,
  `should` is recommended, `may` is permitted, NOTEs are informative. The required/recommended
  distinction in this report follows that vocabulary, not intuition.
- Scope caveat, READ Clauses 1.5 and 3.1 (printed pp. 12, 16 / PDF pp. 13, 17): conformance is
  a property of an implementation of a programming environment, and many obligations are
  addressed to language standards. A bare soft-float library is not, by itself, the standard's
  unit of conformance. Mapping any requirement below onto a library API is therefore always
  **BELIEVED**, even when the underlying clause fact is READ. Which formats an environment
  supports at all is language- or implementation-defined (READ 3.1.1).

## 0. Format status of binary16, binary32, binary64

READ 3.1.1 (printed p. 16 / PDF p. 17), 3.3 Table 3.2 (printed p. 18 / PDF p. 19),
3.6 Table 3.5 (printed p. 23 / PDF p. 24), 2.1 definitions (printed pp. 13-15 / PDF pp. 14-16):

- There are five **basic formats**: binary32, binary64, binary128 and two decimal formats.
  **binary16 is not a basic format.** It is defined only as a 16-bit binary **interchange
  format** in 3.6/Table 3.5. MEASURED: the string for binary16 occurs in the body only in
  Table 3.5 and in the 5.12.2 digit-count rule (`search_extract.py`).
- Any format *can* be supported as an **arithmetic format** (usable for operands/results);
  an **interchange format** is one with a fixed-width encoding defined by the standard.
  The two statuses are independent choices per format.
- A programming environment conforms **in a radix** by implementing at least one basic format
  of that radix as **both** arithmetic and interchange (READ 3.1.2). So binary-radix
  conformance needs binary32, binary64, or binary128 in both roles; binary16 can never be
  the (only) basis of binary conformance.
- Parameters (READ Table 3.5; emin = 1 - emax by READ 3.3):

    | format | k | p | emax | emin | w | t | bias |
    |---|---|---|---|---|---|---|---|
    | binary16 | 16 | 11 | 15 | -14 | 5 | 10 | 15 |
    | binary32 | 32 | 24 | 127 | -126 | 8 | 23 | 127 |
    | binary64 | 64 | 53 | 1023 | -1022 | 11 | 52 | 1023 |

- All binary formats represent signed zeros, normals, subnormals, two infinities, and quiet
  and signaling NaNs (READ 3.3, 3.4; printed pp. 17-19 / PDF pp. 18-20). Binary interchange
  encodings are unique and all canonical; subnormals use reserved exponent field 0 with
  implicit leading 0 (READ 3.4). There is no conforming default flush-to-zero: subnormal
  results are part of the format and of underflow default handling (READ 7.5, below).
- Conformance hooks that drive everything else (READ 3.1.2, printed p. 16 / PDF p. 17):
  (a) any **supported format**: means to initialize it, plus conversions between it and all
  other supported formats; (b) a supported **arithmetic format**: **all** Clause 5 operations
  for that format; (c) a supported **interchange format**: means to read/write it in the
  encoding of Clause 3.

**Conditional reading used below.** Sections 1-3 state what follows *if* binary16, binary32,
and binary64 are each supported as arithmetic formats (and, where relevant, interchange).
Section 6 states the smaller residue if binary16 is interchange-only.

## 1. Clause 5 required operation set (per supported arithmetic format)

READ 5.1 (printed p. 29 / PDF p. 30): conforming implementations shall provide the Clause 5
operations for all supported arithmetic formats, and each numeric computational operation is
performed as if correctly rounded from an infinitely precise, unbounded-range intermediate
(Clauses 4 and 7), subject to Clause 6 rules for zeros/infinities/NaNs. Results shall be
canonical except where 5.5 provides otherwise. Operations divide into general-computational
(round + may signal), quiet-computational (float result, never signal), signaling-computational
(no float result, may signal), and non-computational (neither); and into homogeneous (one
format throughout) vs `formatOf` (destination format named independently of sources).

READ-by-enumeration count (S1 tally of the `shall provide` lists in 5.3-5.7, binary-relevant
names only; comparisons and Table 9.1 counts script-verified as noted): **81 distinct
operation names** are required for a binary arithmetic format, itemised below. The
*instantiation* surface is larger: `formatOf` operations are required for every supported
destination format crossed with every supported same-radix source format (5.4.1), binary
format conversions for every ordered pair of supported floating formats (5.4.2), and integer
conversions for every supported signed/unsigned integer format (5.4.1, 5.8). BELIEVED: for a
library realising binary16+32+64 as arithmetic formats, the per-name instantiations, not the
81-name count, are the true conformance surface.

### 1.1 Homogeneous general-computational (5.3.1, 5.3.3) — 11 names

READ 5.3.1 (printed p. 31 / PDF p. 32) and 5.9 (printed p. 41 / PDF p. 42). Required (`shall`)
for all supported arithmetic formats:

- `roundToIntegralTiesToEven`, `roundToIntegralTiesToAway`, `roundToIntegralTowardZero`,
  `roundToIntegralTowardPositive`, `roundToIntegralTowardNegative` — rounding direction is
  named by the operation, independent of the rounding attribute; no exception except for a
  signaling NaN input (5.9). Note that the ties-to-away *operation* is required even though
  the ties-to-away *attribute* is not required for binary (see Section 2).
- `roundToIntegralExact` — uses the applicable rounding-direction attribute; signals inexact
  when the value changes (and invalid for signaling NaN).
- `nextUp`, `nextDown` — adjacent float in the format; quiet except signaling NaNs.
- `remainder` — the IEEE remainder with ties-to-even quotient choice, always exact when
  defined, independent of the rounding attribute; zero result takes the sign of the dividend.

READ 5.3.3 (printed p. 32 / PDF p. 33): required for all formats available for arithmetic,
with a language-defined `logBFormat` wide enough for the stated integral range:

- `scaleB` (significand times radix to an integral power, correctly rounded as one operation).
- `logB` (unbiased exponent as an integral value; special-value behaviour differs by whether
  `logBFormat` is floating or integer, see Sections 1.6 and 3).

Decimal-only in 5.3.2 (not required for a binary-only implementation): `quantize` shall be
provided for decimal, `quantum` only should. READ note in 5.3.1: the 2008 operations named
`minNum`/`maxNum` no longer exist in Clause 5; they were replaced by the **recommended**
operations of 9.6. **There is no required min/max family in 754-2019** (see Section 5).

### 1.2 formatOf arithmetic and integer conversions (5.4.1) — 7 + 10 names

READ 5.4.1 (printed pp. 33-34 / PDF pp. 34-35): for every supported arithmetic destination,
and for operands of every supported arithmetic format **of the same radix**, implementations
shall provide `addition`, `subtraction`, `multiplication`, `division`, `squareRoot`,
`fusedMultiplyAdd`, and `convertFromInt`. In particular:

- **FMA is required, not optional.** `fusedMultiplyAdd` is a single-rounding operation over
  the exact product-plus-addend; at most one exception arises from rounding that exact value.
  It is explicitly not a multiply followed by an add.
- `squareRoot` is required; its result is non-negative except that the root of negative zero
  is negative zero.
- `convertFromInt`: from all supported signed and unsigned integer formats to all supported
  arithmetic formats; exact when representable, otherwise rounded per the applicable
  attribute with inexact/overflow as in Clause 7.

READ 5.4.1 (continued) and 5.8 (printed pp. 39-40 / PDF pp. 40-41): to every supported
integer destination, from every supported arithmetic format, ten operations are required:
five non-inexact-signaling `convertToInteger*` and five inexact-signaling
`convertToIntegerExact*`, each in ties-to-even, toward-zero, toward-positive,
toward-negative, and ties-to-away variants named by the operation (not the attribute).
NaN, infinity, or out-of-range results signal invalid where the destination cannot otherwise
indicate them (5.8). The standard does not define integer formats themselves (READ 1.4).

### 1.3 Format and character-sequence conversions (5.4.2, 5.4.3, 5.12) — 3 + 2 names

READ 5.4.2 (printed p. 34 / PDF p. 35): required from all supported floating formats to all
supported floating formats, plus to/from decimal character sequences:

- `convertFormat` — cross-radix or narrowing conversions are rounded per Clause 4; widening
  within a radix with wider precision **and** range is always exact. A same-format conversion
  canonicalizes and signals invalid on a signaling NaN (unlike `copy`).
- `convertFromDecimalCharacter`, `convertToDecimalCharacter` — the latter takes a
  language-defined conversion specification (precision/formatting).

READ 5.4.3 (same page): implementations shall provide `convertFromHexCharacter` and
`convertToHexCharacter` to/from all supported **binary** formats. READ tension, recorded
as found: 5.12.3 (printed p. 47 / PDF p. 48) addresses **language standards** with a
`should`. The implementation-level text read in 5.4.3 and in 5.12 (printed p. 44 / PDF
p. 45, exact binary-to-hex conversions with exact round trip, signaling NaN possibly
quieted) uses `shall`. BELIEVED: hex conversions belong in a conformance claim's required
set; a claim that omits them must say which sentence it rests on.

Required digit counts and round-trip guarantees, READ 5.12 and 5.12.2 (printed pp. 44-46 /
PDF pp. 45-47):

- Round-trip minima: `Pmin(binary16)=5`, `Pmin(binary32)=9`, `Pmin(binary64)=17`
  (`Pmin(binary128)=36`; other binary formats by the stated ceiling formula in `p`).
- Let `M` be the maximum `Pmin` over supported binary formats. An implementation-defined
  correctly-rounded digit limit `H` is permitted but shall satisfy `H >= M + 3`; `H` should
  be unbounded. Correctly rounded conversions are required for all significant-digit counts
  from 1 through `H`, both directions, with correct exception signaling; beyond `H`, output
  pads with trailing zeros and input takes the specified two-step rounding route, which
  preserves directed-rounding sign and monotonicity (5.12.2 with its informative NOTE 1).
  BELIEVED consequence for a binary16+32+64 implementation: `M = 17`, so `H >= 20`; a
  binary64-only claim is the same, a binary32-max implementation would need only `H >= 12`.
- Binary format to decimal characters and back recovers the original representation under
  round-to-nearest attributes when at least `Pmin` digits are used (5.12, 5.12.2); decimal
  formats convert with correct rounding for any digit count (decimal formats only; stated
  here because cross-radix `convertFormat` inherits the 5.12.2 limits, READ 5.12 first
  paragraph).
- Zeros, infinities, quiet NaNs round-trip with signs of zeros/infinities preserved; the
  spellings for infinity and NaN (case-insensitive language-defined choices) and input
  acceptance rules are specified in 5.12.1 (printed p. 45 / PDF p. 46). A signaling-NaN
  payload suffix on output is a `should` for language standards, but any such output shall
  be accepted on input.
- Hex-significand sequences (5.12.3): grammar and value are normatively defined; with no
  explicit precision, binary-to-hex output uses enough digits to be exact; explicit-precision
  and input conversions are correctly rounded under the binary attribute with exceptions.

### 1.4 Quiet sign-bit operations (5.5.1) — 4 names

READ 5.5.1 (printed p. 35 / PDF p. 36): `copy`, `negate`, `abs`, and `copySign` shall be
provided for all supported arithmetic interchange formats, and for non-interchange arithmetic
formats at the representation level. They affect only the sign bit, treat numbers and NaNs
alike, signal nothing, and may propagate non-canonical encodings. `negate` is not subtraction
from zero (cf. sign rules, Clause 6.3). Decimal re-encoding operations in 5.5.2 are
decimal-only.

### 1.5 Comparisons (5.6.1, 5.11, 5.10) — 22 names plus totalOrder family

READ 5.6.1 (printed p. 37 / PDF p. 38) with 5.11 (printed pp. 43-44 / PDF pp. 44-45):
**22 named comparison predicates** are required for all same-radix arithmetic operand pairs
(MEASURED: `count_ops.py` counted 22 distinct compare names in 5.6.1; Tables 5.1-5.2 in 5.11
present them as negation pairs over the four relations less/equal/greater/unordered). The
families are the `compareQuiet*` and `compareSignaling*` spellings of equal, not-equal,
greater, greater-equal, less, less-equal, and their unordered-aware negations, plus
`compareQuietUnordered`/`compareQuietOrdered`. Semantics (READ 5.11): every NaN is unordered
with everything including itself; signed zeros compare equal; same-sign infinities compare
equal; invalid is the only exception a comparison can signal — all predicates signal it on a
signaling NaN, `Quiet` predicates on nothing else, `Signaling` predicates also on quiet NaNs.
Cross-format comparison within a radix is required (5.11 first paragraph).

READ 5.7.2/5.10 (printed pp. 38, 42 / PDF pp. 39, 43): `totalOrder` and `totalOrderMag` are
required non-computational predicates giving the specified total order over canonical members
of a format, including negative-zero-below-positive-zero and signed-NaN placement rules;
they signal nothing, even on signaling NaNs.

### 1.6 Classification, conformance, and flag operations (5.7) — 3 + 11 + 6 names

READ 5.7.1 (printed p. 37 / PDF p. 38): `is754version1985`, `is754version2008`,
`is754version2019` shall be provided (translation-time availability is a `should`).

READ 5.7.2 (printed p. 38 / PDF p. 39): shall be provided for all supported **arithmetic**
formats, and only **should** be provided for supported interchange formats (the distinction
matters in Section 6); never exceptional, even for signaling NaNs: `class` (ten classes:
signaling/quiet NaN, signed infinities, signed normals, signed subnormals, signed zeros),
`isSignMinus`, `isNormal`, `isFinite`, `isZero`, `isSubnormal`, `isInfinite`, `isNaN`,
`isSignaling`, `isCanonical`, and `radix` (plus `totalOrder`/`totalOrderMag` counted in 1.5).
`sameQuantum` in 5.7.3 is decimal-only.

READ 5.7.4 (printed p. 39 / PDF p. 40): shall be provided, non-exceptional: `lowerFlags`,
`raiseFlags`, `testFlags`, `testSavedFlags`, `restoreFlags`, `saveAllFlags`, acting on
arbitrary subsets of the Clause 7 flags.

## 2. Required rounding attributes for binary

READ 4.3.1-4.3.3 (printed pp. 27-28 / PDF pp. 28-29) with 4.1-4.2 (printed p. 26 / PDF p. 27):

- Five attributes are defined: two to-nearest (`roundTiesToEven`, `roundTiesToAway`) and
  three directed (`roundTowardPositive`, `roundTowardNegative`, `roundTowardZero`), with the
  to-nearest overflow threshold and tie rules specified in 4.3.1.
- **Required for every implementation: `roundTiesToEven` and all three directed attributes.**
  **`roundTiesToAway` is required only for decimal implementations; it is expressly not
  required for binary.** The default attribute for binary results shall be `roundTiesToEven`
  (READ 4.3.3).
- The attribute governs all possibly-inexact computational operations except where an operation
  names its own rounding (1.1, 1.2); it also fixes the sign of exact zero sums (Clause 6.3:
  positive except under `roundTowardNegative`, with the same-signed zero-arithmetic proviso)
  and the overflow/underflow thresholds. Inexact results keep the sign of the exact result;
  NaNs are not rounded. READ 4.3 (printed p. 27 / PDF p. 28), 6.3 (printed p. 50 / PDF p. 51).
- Mechanism: constant (block-scoped) attribute specification shall be supported (4.1, 4.2);
  dynamic-mode specification should additionally be supported by language standards (4.2),
  with dynamic variables initialized to defaults and the get/set operations conditional in
  9.3. A dynamic-mode implementation with suitable scope can satisfy the constant-specification
  requirement (informative NOTE in 4.2). Implementations supporting both radices shall keep
  separate binary and decimal rounding attributes, selected by the radix of the result — or,
  for float-to-integer and float-to-character conversions, of the operand (READ 4.3).
  BELIEVED for a binary-only library: one binary rounding attribute with four selectable
  values and ties-to-even default discharges the numerical content; how a host language
  spells block scope is outside a library's control and outside this survey's evidence.

## 3. Exceptions: flags, default results, tininess, NaN behaviour

### 3.1 The five exceptions and their flags

READ 7.1 (printed p. 51 / PDF p. 52): exactly five kinds shall be signaled when they arise,
each with a corresponding status flag — **invalid operation, divideByZero, overflow,
underflow, inexact** (flag list also READ in 2.1 definition of status flag, printed p. 15 /
PDF p. 16). Default handling is non-stop: deliver the Clause 7 default result, continue, and
raise the flag — with one exception: an **exact** (tiny but exact) underflow raises no flag
and has no observable effect under default handling (7.1, 7.5). Flags are lowered only at
user request; the user shall be able to test/alter them individually or collectively and
save/restore all at once (7.1, via 5.7.4 operations); execution begins with all flags lowered
unless inherited. One required-operation invocation signals at most one exception; its default
handling may signal a second (overflow signals inexact; inexact underflow signals inexact;
invalid-from-signaling-NaN in signaling comparisons may re-signal), so at most two flags rise
per invocation under all-default handling, apart from user flag operations (READ 7.1).

### 3.2 Default results per exception

READ 7.2-7.6 (printed pp. 52-54 / PDF pp. 53-55):

- **Invalid operation (7.2)** — signaled exactly when no usefully definable result exists.
  Default floating result: a **quiet NaN** (which should carry diagnostics). Enumerated binary
  cases include: any general-computational operation on a signaling NaN (except some 5.12
  conversions); zero times infinity in `multiplication`/`fusedMultiplyAdd` (with the 7.2(c)
  implementation-defined proviso when the addend is a quiet NaN); magnitude subtraction of
  infinities in `addition`/`subtraction`/`fusedMultiplyAdd`; 0/0 and infinity/infinity;
  `remainder` with zero divisor or infinite dividend; `squareRoot` of a negative operand;
  plus (no floating result) signaling-computational operations on signaling NaNs (re-evaluated
  with quieted operands under default handling), float-to-integer conversion of NaN/infinity/
  out-of-range values, unordered-signaling comparisons on unordered operands, and `logB` of
  NaN/infinity/zero when `logBFormat` is integral.
- **divideByZero (7.3)** — signaled exactly when an exact infinite result is defined from
  finite operands (`division` by zero of a finite non-zero, and floating-`logB` of zero).
  Default result: correctly signed infinity (sign by exclusive-OR for division; negative for
  `logB`).
- **Overflow (7.4)** — signaled exactly when the unbounded-exponent rounded result would
  exceed the largest finite magnitude. Default result by attribute: nearest modes give signed
  infinity; toward-zero gives the largest finite of the result's sign; toward-negative gives
  largest finite for positive and negative infinity for negative; toward-positive mirrors.
  The overflow flag rises and inexact is also signaled.
- **Underflow (7.5)** — see 3.3. Default handling always delivers the rounded result (zero,
  subnormal, or smallest normal magnitude); if that result is inexact, the underflow flag
  rises and inexact is signaled; if exact, no flag and no inexact.
- **Inexact (7.6)** — an operation signalling no other exception signals inexact exactly when
  its rounded delivered result differs from the unbounded-precision-and-range result, except
  where specified otherwise (notably the non-`Exact` integer/integral conversions of 5.8/5.9).
  The rounded result is delivered. Informative consequence: under all-default handling the
  inexact flag rises whenever overflow or underflow does.

Infinity operands are otherwise exact and exception-free where the affine limit exists;
READ 6.1 (printed p. 48 / PDF p. 49) lists the everyday cases and the only infinity-related
exception routes (invalid operand, creation by overflow/divideByZero, and underflow from
`remainder` of a subnormal by infinity).

### 3.3 Tininess detection

READ 7.5 (printed p. 53 / PDF p. 54): **for binary, the implementer shall choose** one of two
detections — *after rounding* (unbounded-exponent rounded result non-zero and strictly below
the smallest normal magnitude) or *before rounding* (unbounded-exponent-and-precision result
in the same interval) — **and shall use that same choice for all radix-two operations,
including conversions under a binary rounding attribute.** The choice never changes the
delivered rounded result; it changes only whether underflow is signaled in boundary cases
(results rounding to the smallest normal). For decimal, detection is fixed as before-rounding.
BELIEVED: the choice is a conformance-visible implementation decision that a binary library
must make once, document, and apply uniformly — including in its conversion paths.

### 3.4 NaNs: what is required vs recommended

Required (READ 6.2, printed p. 48 / PDF p. 49; 6.2.1, 6.2.3):

- Both quiet and signaling NaNs shall be supported in all floating-point operations.
- Under default handling, a floating result of an operation signaling invalid is a quiet NaN
  (except as stated otherwise).
- Signaling NaNs signal invalid for every general- and signaling-computational operation
  except the 5.12 conversions. General/quiet operations with only quiet NaN inputs signal
  nothing (except `fusedMultiplyAdd` may signal invalid, 7.2(c)) and, if they deliver a float,
  deliver a **canonical quiet NaN** except as stated otherwise. A NaN result is canonical even
  from a non-canonical NaN operand (6.2.3, excepting 5.5).
- In binary interchange encodings, the first trailing-significand bit shall exclusively
  distinguish quiet from signaling (READ 3.4(a)); conversion of a quiet NaN to a format that
  cannot preserve its payload shall still return a quiet NaN (6.2.3).

Recommended only (READ 6.2, 6.2.1, 6.2.3; all `should`):

- **Payload propagation is not required.** Single-NaN propagation should preserve the payload
  if representable; multi-NaN results should carry one input's payload (which one is
  unspecified); narrow-to-wide-and-back quiet-NaN conversion should preserve the payload up
  to canonicalization; a payload-losing conversion should return language-defined diagnostics;
  payload character-sequence access should exist. A quiet NaN should afford retrospective
  diagnostics by implementer-chosen means.
- Even the **polarity** of the distinguishing bit is only recommended in 6.2.1 (leading
  trailing bit 1 for quiet, 0 for signaling, with the stated quieting rule under that
  preferred encoding) — the `shall` in 3.4 fixes only that this bit does the distinguishing.
- The sign of a NaN result is unspecified for almost all operations (READ 6.3).

BELIEVED: a conforming binary implementation may therefore return one fixed canonical quiet
NaN for every computational NaN result and still meet the letter; payload preservation is a
quality/recommendation decision, and any test oracle must not require a particular payload
except where the implementation itself promises one.

## 4. Clause 8 alternate handling: not required by 754

READ Clause 8 (printed pp. 55-57 / PDF pp. 56-58) and 4.1 (printed p. 26 / PDF p. 27),
7.1 (printed p. 51 / PDF p. 52):

- Every operative sentence is addressed to **language standards** with `should`: languages
  should define block-scoped alternate-exception attributes (any subset of the five exceptions,
  all-exceptions, and sub-exceptions), should define all attributes of the clause, and in
  particular at least one delayed attribute per exception (8.1). Clause 4.1 mirrors this:
  languages shall specify rounding attributes and **should** specify alternate handling.
  Clause 7.1 says a language **might** require some of them. **Nothing in Clause 8 is a
  `shall` on a floating-point implementation as such.** BELIEVED, as a direct reading of the
  three cites together: an implementation offering only Clause 7 default, non-stop handling
  (with flags) conforms to 754 on this point; alternate handling becomes obligatory only if a
  governing language standard makes it so.
- What is specified (for languages that adopt it): resuming attributes in 8.2 (default with
  flag, no-flag and may-flag variants, exception recording, result substitution in two forms,
  abrupt underflow — replacing tiny results with signed zero/smallest-normal per attribute),
  and immediate vs delayed handler blocks and control transfers in 8.3, including the rule that
  immediate underflow handling fires even for exact tiny results while delayed handling fires
  only for flag-raising inexact ones. Two conditional `shall`s exist *inside* that machinery
  (abrupt-underflow result choice in 8.2/8.3 text, immediate-underflow invocation in 8.3) —
  they bind only implementations of those attributes.
- Consequence worth recording (BELIEVED): flush-to-zero-style behaviour exists in the standard
  only as the 8.2 abrupt-underflow alternate attribute; it is not a conforming *default*.

## 5. Clause 9 recommended operations

READ Clause 9 headnote (printed p. 58 / PDF p. 59): Clause 5 completely specifies the required
operations; Clause 9 operations are **recommended**. The pattern inside is uniform: language
standards `should` define them, but anything that calls itself a conforming version of one
**shall** meet the accuracy/exception rules of 9.1-9.2 (notably correct rounding for the
applicable attribute, canonical results, Clause 7 exceptions with the 9.2 adjustments —
signaling NaN signals invalid, out-of-domain gives quiet NaN + invalid, simple poles give
divideByZero, inexact only as a `should`).

Itemised (name counts: enumerations READ; Table 9.1 count MEASURED by `count_ops.py`):

- **9.2 / Table 9.1 — 39 mathematical operations** (printed pp. 58-64 / PDF pp. 59-65):
  exponentials (base e/2/10, plain and minus-one forms: 6), logarithms (base e/2/10, plain
  and plus-one forms: 6), `hypot`, `rSqrt`, `compound`, `rootn`, `pown`, `pow`, `powr` (7),
  circular trig and inverses in radians and half-revolutions including two-argument arctangent
  (14: `sin`, `cos`, `tan`, `sinPi`, `cosPi`, `tanPi`, `asin`, `acos`, `atan`, `atan2`,
  `asinPi`, `acosPi`, `atanPi`, `atan2Pi`), hyperbolic trig and inverses (6). Extensive
  special-value tables are given in 9.2.1; preferred exponents (decimal relevance) in 9.2.2.
  6+6+7+14+6 = 39, agreeing with the script count.
- **9.3 — dynamic-mode operations** (printed p. 65 / PDF p. 66): conditional shall — a language
  that defines dynamic-mode rounding *shall* define get/set for it
  (`getBinaryRoundingDirection`/`setBinaryRoundingDirection` for binary) and the collective
  `saveModes`/`restoreModes`/`defaultModes`. Recommended in effect because dynamic modes
  themselves are only recommended (4.2).
- **9.4 — reduction operations** (printed pp. 66-67 / PDF pp. 67-68): 7 names over vectors —
  `sum`, `dot`, `sumSquare`, `sumAbs`, `scaledProd`, `scaledProdSum`, `scaledProdDiff`.
  Unusually, results are implementation-defined approximations (any association, any wider
  intermediate format); one exception per invocation, signaling NaN anywhere signals invalid.
- **9.5 — augmented arithmetic** (printed pp. 68-69 / PDF pp. 69-70): binary-only
  recommendation; `augmentedAddition`, `augmentedSubtraction`, `augmentedMultiplication`
  returning (rounded value, exact error) pairs under a clause-local ties-toward-zero-at-ties
  rounding defined only there, with specified underflow behaviour on tiny errors.
- **9.6 — minimum/maximum** (printed pp. 69-70 / PDF pp. 70-71): 8 names —
  `minimum`/`maximum`, `minimumNumber`/`maximumNumber`, and the four `*Magnitude*` forms.
  Key semantics: the plain forms propagate any NaN (quiet NaN result per 6.2); the `Number`
  forms return the non-NaN operand when exactly one operand is NaN (signaling NaN still
  signals invalid but is otherwise ignored, not quieted-and-propagated); signed zeros are
  ordered (negative zero is the minimum). This is the family that replaced 2008's Clause 5
  min/max — in 2019 it is recommended only.
- **9.7 — NaN payload access** (printed p. 71 / PDF p. 72): `getPayload`, `setPayload`,
  `setPayloadSignaling` — quiet, exception-free, with implementation-defined admissible
  payload sets.

BELIEVED: Clause 9's correct-rounding demand on the 39 Table 9.1 operations is far harder
than the Clause 5 core; nothing in a minimal conformance claim needs any of Section 5.

## 6. binary16 as interchange-only: what would still be required

Assumption for this section: binary16 is a supported **interchange** format but **not** a
supported arithmetic format, alongside at least one basic binary format carried as both
arithmetic and interchange (without which there is no binary-radix conformance at all;
READ 3.1.2, Section 0).

Still required, with triggering text:

1. **Encoding read/write.** Means to read and write binary16 bit strings in the Clause 3
   encoding (READ 3.1.2(c); layout in 3.4, parameters in Table 3.5: 1/5/10 fields, bias 15).
   Byte order and the signaling/quiet distinction are inter-implementation parameters the
   standard explicitly does not define how to communicate (READ 3.6 NOTE, printed p. 24 /
   PDF p. 25). All 2^16 encodings have defined meanings as zeros, subnormals, normals,
   infinities, quiet/signaling NaNs (READ 3.4); all are canonical.
2. **Initialization.** Means to initialize the format (READ 3.1.2, first sentence — it applies
   to "any supported format", not only arithmetic ones).
3. **Conversions to/from every other supported format.** The same sentence requires
   conversions between any supported format and all other supported formats. Read with 5.4.2
   and 5.12 (whose obligations are phrased over supported formats / "each supported binary
   format", printed p. 44 / PDF p. 45), BELIEVED requirements for interchange-only binary16
   include: `convertFormat` to and from each supported arithmetic format (widening to
   binary32/64 exact by 5.4.2 since both precision and range strictly increase; narrowing
   correctly rounded under the binary attribute with Clause 7 overflow/underflow/inexact and
   the implementation's single tininess choice, 7.5), correctly rounded decimal-character
   conversions both directions with `Pmin(binary16) = 5` round-trip behaviour and the global
   `H >= M+3` limit (5.12.2 — note `M` is taken over *all supported binary formats*, so
   adding interchange binary16 to a binary64 implementation does not lower `H`), and exact
   hex-character conversions (5.12, subject to the 5.12.3 language-level `should` recorded
   in 1.3). NaN/zero/infinity character round trips per 5.12.1 likewise. Each such conversion
   remains a general-computational operation for exception purposes wherever it is provided:
   signaling NaN input behaviour, canonical quiet NaN results, and flags follow 6.2 and
   Clause 7 (READ 5.1 operation classes; BELIEVED application to these conversions).
4. **Recommended-but-not-required for the interchange role:** the 5.7.2 classification family
   (`class`, `isFinite`, etc.) is only `should` for supported interchange formats (READ
   5.7.2 first sentence). Everything whose triggering text says "arithmetic format" drops
   away: the full Clause 5 homogeneous/`formatOf` arithmetic *with binary16 operands or
   destination qua arithmetic operation*, `roundToIntegral*`, `nextUp`/`nextDown`,
   `remainder`, `scaleB`/`logB`, comparisons as binary16 arithmetic operands, and direct
   binary16-integer conversions under 5.4.1/5.8 (which are phrased over arithmetic formats).
   BELIEVED boundary warnings: (i) the moment any binary16 arithmetic operation is exposed
   as a *supported* operation, 2.1's definition makes binary16 an arithmetic format and
   3.1.2(b)/5.1 pull in all of Clause 5 for it — partial arithmetic support has no conforming
   middle position in the text read; (ii) "supported" vs merely "provided" formats are
   distinguished in 2.1, so a format offered explicitly as non-conforming could escape even
   items 1-3 — but then no 754 claim of any kind attaches to it.

BELIEVED summary: interchange-only binary16 is not "just a bit layout". The inescapable core
is layout + initialize + correctly rounded, flag-correct conversions among binary16, the
supported arithmetic formats, and decimal/hex character sequences. It escapes binary16
*computation* only.

## Evidence index

- MEASURED: PDF identity (84 pp., 2019 IEEE title/author metadata), outline-to-clause page map,
  extraction of every page to `scratch/S1/extract/p001.txt`-`p084.txt` — `extract_pdf.py`,
  output `scratch/S1/extract/inventory.txt`, `outline.txt`, `combined.txt`.
- MEASURED: term occurrences for binary16 / basic format / interchange format —
  `search_extract.py`, output `scratch/S1/extract/search1.txt`.
- MEASURED: 22 comparison names in 5.6.1; 39 Table 9.1 operation names; printed = PDF-1 page
  relation on sampled body pages — `count_ops.py`, output `scratch/S1/extract/counts.txt`.
- READ directly (full pages, not samples): printed pp. 11, 13-19, 23-29, 31-41, 42-47,
  48-54, 55-65, 66-71; TOC pp. 9-10. Annex C (informative) operation list, printed pp. 81-82 /
  PDF pp. 82-83, was used only as a name cross-check. Clauses 10, 11 and Annexes A/B were not
  surveyed; nothing in the brief asked about expression evaluation or reproducibility.

## Anything this brief got wrong

1. **Min/max is not in the required operation set in 754-2019.** The brief's item (1) lists a
   "min/max family" among clause-5 required operations. In 2019 those operations live in
   **recommended** Clause 9.6 (8 names), and the text of 5.3.1 (printed p. 31 / PDF p. 32)
   notes that the 2008 required operations were replaced by them. Any project plan that
   treats min/max as core-required (or that tests the 2008 NaN-suppressing semantics as if
   required) inherits this error. (READ)
2. **binary16 is framed too symmetrically with binary32/64.** Item (1) groups
   "binary16/32/64 as arithmetic formats" without noting that binary16 is not one of the five
   basic formats and cannot ground binary-radix conformance (Section 0). Support of binary16
   as an arithmetic format is permitted but is a choice; support of at least one of
   binary32/64/128 as both arithmetic and interchange is the actual conformance floor in the
   binary radix. This also sharpens item (6): the interesting interchange-only question
   exists only because binary16 is defined *solely* as an interchange width. (READ)
3. **FMA's "?" resolves to required**, and it is a single-rounding operation, not a
   multiply-add sequence (READ 5.4.1) — if the project had budgeted FMA as optional or as a
   composed pair, that budget is wrong.
4. **The brief's item (1) checklist omits required operations** that are easy to miss and
   material to sizing: `remainder`, `nextUp`/`nextDown`, `scaleB`/`logB`, the ten named
   `convertToInteger*` variants, hex-character conversions, the three `is754version*`
   predicates, `totalOrder`/`totalOrderMag`, and the six flag operations. None of these is
   exotic; all are `shall` for a supported arithmetic format. (READ, Section 1.)
5. **Item (2) could be misread as "five rounding modes" for binary.** Five attributes exist
   in the standard, but only four are required for binary; ties-to-away is a decimal
   requirement (READ 4.3.3) — while the ties-to-away *operations* (round-to-integral and
   integer conversion) remain required for binary. Confusing the two cuts both ways.
6. **Item (3)'s phrase "NaN propagation requirements" overstates what is required.** A
   canonical quiet NaN result is required; payload propagation and even the quiet-bit polarity
   are `should` (6.2.1, 6.2.3). Oracles must not assert payloads as conformance facts.
7. Nothing found wrong in items (4)-(6) as questions; their answers are: clause 8 is not
   required by 754 (Section 4), clause 9's list is in Section 5, and interchange-only binary16
   still requires the conversion core in Section 6. Process note (MEASURED): the brief's
   scratch and tooling assumptions all held — `.venv` + pypdf read the PDF cleanly; the
   ledger's Git-Bash/bash watcher snippet did not run under this harness's Monitor shell
   (bash form exited immediately twice; a PowerShell equivalent armed successfully and
   reported "watcher armed"), which is recorded in the S1 ledger entry.





