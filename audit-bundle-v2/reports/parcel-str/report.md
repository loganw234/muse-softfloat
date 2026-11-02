# parcel-str report — Wave 3 character conversions

Branch `w3-str` in `worktrees/w3-str`, tip `8712ec1` on lead commits
`83622cf` / `f3c48b8` / `bc15b2c` on base `548a1b9`. Two parcel commits:
`945217c` (implementation + implemented.tsv + regenerated outputs) and
`8712ec1` (references + committed vectors). Nothing pushed or merged.

Deliverable: all 12 wave=3 rows — `msf{16,32,64}_from_decimal`,
`_to_decimal`, `_from_hex`, `_to_hex` — implemented in the new TU
`src/msf_string.c` (1,228 lines) with `tests/gen_vectors_str.py`
(928 lines) as the independent exact reference and generator.
Hand-written total 2,156 of 3,500 lines; committed vectors 896,090
bytes (4 files, 9,149 vectors) under the 1 MB ceiling.

## Semantics (as ruled R1–R6, ledger/lead.md 2026-10-27 08:30:16)

Design entry: ledger/parcel-str.md 2026-10-27 08:28:15 -0700. The six
ruling bundles were accepted as recommended and implemented as below.

### Grammar decisions table

| Input form | Accepted by | Result | Consumed | Flags |
|---|---|---|---|---|
| `sign? DIGITS[.DIGITS*][eE sign? DIGITS]` | from_decimal | pack of exact value | longest such prefix | pack flags only |
| `sign? . DIGITS [exp]` | from_decimal | same | longest prefix | pack only |
| `1e`, `1e+`, `1e+x` | from_decimal | 1.0 | 1 (incomplete exponent not consumed) | none/pack |
| `0x1p1` | from_decimal | +0 (the `0`) | 1 | none |
| `sign? inf` / `infinity` (any case) | both inputs | signed infinity | 3 or 8 (+sign), longest (`infi` → 3) | none |
| `sign? nan` (any case) | both inputs | signed default quiet NaN | 3 (+sign) | none |
| `sign? snan` (any case) | both inputs | signaling NaN, payload 1 (R2) | 4 (+sign) | none |
| `nan(1)` | both inputs | quiet NaN (no payload suffix, R2) | 3 | none |
| `sign? 0[xX] hexsig [pP] sign? DIGITS` | from_hex | pack of exact value | whole sequence | pack only |
| `0x1.8` (no p part), `0x1p+` | from_hex | no valid prefix (R3) → +0 | 0 | none |
| `1.5` | from_hex | +0 | 0 | none |
| leading space/tab, `+`, `.`, `e5`, `""`, `NULL` | both inputs | +0 (header no-valid-prefix rule) | 0 | none |
| all-zero mantissa, any exponent (`-0.00e999999999`) | both inputs | signed zero, exact | whole token | none |
| > 20 significant decimal digits | from_decimal | 5.12.2 two-step: digit string rounded to 20 digits under the attribute, then exact pack (R4) | whole token | pack flags, plus inexact iff step 1 dropped a nonzero digit; underflow from step 2 only |
| exponent digits unbounded (`1e999999999`) | both inputs | overflow/underflow deliveries via pack, magnitude saturated at 100001 internally | all digits | ovf/unf + inexact via pack |

Output decisions (R5 spec freeze):

| Question | Decision |
|---|---|
| decimal `precision` | significant digits; `<= 0` → Pmin (5/9/17) per header |
| `min_digits` | emitted-count floor that raises computed precision (`max(precision, min_digits)`, computed at min(N,20), zero-padded past 20) |
| style 0 scientific | `[-]d[.ddd]e±XX`, exponent signed, at least 2 digits; point iff N>1; zero exponent `+00` |
| style 1 fixed | same N significant digits positioned without exponent; place-holder zeros as position requires; unknown style values act as scientific |
| `precision > 20` | 20 correctly rounded digits then trailing-zero pad (5.12.2); inexact reflects the 20-digit rounding |
| hex `precision < 0` | exact-enough: minimal exact digits, trailing zeros trimmed, no point if no fraction |
| hex `precision >= 0` | C-`%a` semantics: fraction hex digits after the point; carry may make the leading digit 2 at the same exponent; inexact iff dropped bits nonzero |
| hex shapes | lowercase `0x`, normals `0x1.…`, subnormals `0x0.…p<emin>`, zero `0x0p+0`, exponent signed without leading zeros |
| specials out (both ops) | `inf`, `-inf`, `nan`, `-nan`, `snan`, `-snan`; spec ignored; no flags |
| NULL spec | decimal: Pmin/scientific/no floor; hex: exact-enough |
| buffer too small / NULL buf | return would-be length excluding NUL, write nothing at all; conversion flags (inexact) still signaled |

Shortest-form output is neither implemented nor claimed anywhere; the
emitted digit count is always exactly the spec count above.

## Algorithms (one paragraph each)

Fixed 96×u32-limb (3,072-bit) unsigned bigint inside the TU; width
argument in the file header (largest value is sig·5^1074 < 2^2547).
Decimal input within H=20 forms D·10^E exactly — multiply for E≥0,
binary long division to a 200-bit quotient with remainder-sticky for
E<0 — reduces to the top 128 bits plus faithful sticky, and takes one
`msf_pack_generic` rounding (all flags from the kernel). Decimal
magnitude early-outs per format (m in [10^(m-1),10^m): overflow
synthesis at m ≥ 6/40/310, underflow synthesis at m ≤ −9/−46/−325)
route through the same pack and are cross-checked against direct
exact packing across the thresholds (10,728-case corridor sweep).
Hex input streams digits into (sig, exp2, sticky) and packs once —
exact at any digit count. Decimal output builds the finite exact
decimal expansion of sig·2^exp as an integer digit string and rounds
the string once, with ties decided by exact dropped-digit comparison;
hex output rounds on exact dropped bits. Length is measured before
any byte is written (zero runs are O(1) in the measure pass, so a
precision of 1,000,000 costs arithmetic, not memory).

## Counts, by provenance

Committed (real runner, all PASS, `directed3.log`):
9,149 total — from-decimal-str.vec 3,290 (grammar-dec 372,
grammar-dec-modes 846, from-dec-ties 1,840, beyond-h 232 — line
count 3,291 incl. header), from-hex-str.vec 1,314 (grammar-hex 174,
grammar-hex-modes 552, from-hex-ties 288, from-hex-boundary 300),
to-decimal-str.vec 2,670, to-hex-str.vec 1,875. (Provenance splits
per file as printed by the runner; sums per the log.)

Scratch differentials through the real runner (logs in
scratch/parcel-str/, vector hashes in bulk/SHA256SUMS.txt):

| Set | Cases | Per dest | Result |
|---|---|---|---|
| bulk from-decimal (seed 20261027) | 600,000 | 200,000 each f16/f32/f64 | PASS |
| bulk from-hex (20261029) | 300,000 | 100,000 each | PASS |
| bulk to-decimal (20261028) | 700,002 | 233,334 each | PASS |
| bulk to-hex (20261030) | 300,000 | 100,000 each | PASS |
| f16 exhaustive output (6 dec specs + 4 hex specs × 65,536) | 655,360 | — | PASS |
| threshold corridor (early-out bands, all modes/signs) | 10,728 | — | PASS |
| long strings (21–800 dec digits, 33–300 hex digits, full midpoints) | 9,720 | — | PASS |

Round-trip property (scratch C harness `to_harness.exe rt`,
roundtrips.log): f16 exhaustive — to_decimal at precisions 5/9/17
(scientific/scientific/fixed) and back under ties-to-even is
bit-exact for finite/infinity and class+sign-exact for NaNs (payload
canonically defaults, per R2) on all 65,536 encodings; to_hex
exact-enough likewise. Seeded f32 and f64: 200,000 iterations each
(Pmin and 20 digits, both styles), 0 failures. API edges in the same
run: NULL `s`, NULL `consumed`, NULL specs, NULL buffer, exact-fit
buffers, leading/trailing whitespace — all as the table above.

Foreign-oracle cross-checks (counts separate, per brief):

| Oracle | Authority over | Cases | Result |
|---|---|---|---|
| MPFR (host libmpfr via scratch C oracle, parses at p+80 and p+200, driver packs exactly) | from_decimal + from_hex string scaling, within-H only | 30,000 dec + 10,000 hex decided, 0 two-precision disagreements dropped | 0 bit mismatches |
| MPFR `mpfr_get_str` | to_decimal output digit choice at K ∈ {1,2,5,9,17,20}, all modes | 7,857 | 0 digit/exponent mismatches |
| CPython `float()` correctly-rounded parse | from_decimal f64 te bits; to_decimal f64 outputs parse back | 40,000 + 20,832 (1,129 skipped by name: partial-consume forms where `float()` would raise) | 0 mismatches |
| exact Python ref (gen_vectors_str.py) | everything above | 2.5M+ (bulk sets) | 0 mismatches |

Budgets: `tools/run.sh smoke` and `standard` were run. Everything in
smoke passes (drift clean at 783 implemented, 75,999 pre-existing
vectors, unit tests, type scan clean, target ARM symbol scan clean
including src/msf_string.c) EXCEPT negative control 9
(planned-only-verdict NOT REFUSED), which cannot pass once these rows
land because no planned op exists; the lead retires/replaces it at
merge (ruled, and re-flagged to me in the merge message) — reported
here as that, not as a regression. The `standard` tail beyond smoke
(f16-exhaustive 917,504 + pack-sweep 200,000 generated sets) was run
separately through the same runner build: PASS (stdtail/verify.log).
Board budget not run (lead-run under the board lock).

## Negative controls (watched failing)

1. Flipped expected digit: one `OUT=` digit changed in a copy of
   to-decimal-str.vec → runner VERDICT FAIL at that line
   (controls/flip-digit.log).
2. Wrong consumed: one `C=0` changed to `C=1` in a copy of
   from-decimal-str.vec → FAIL naming got/want C (controls/wrong-c.log).
3. Truncating mutant: scratch copy of the TU with all four generic
   entries forced to toward-zero fails 728 of the 2,128 tie-set
   vectors the real build passes in full (controls/mutant.log,
   ties-real.log). Mutant lived only in scratch
   (controls/msf_string_mut.c); the worktree file hash equals the
   pre-mutant copy (4efc56fa…) and is what commit 945217c carries.
4. Regeneration byte-identity: directed vectors re-generated and
   sha256-compared identical; the four table-driven outputs pass
   run.sh's drift check.

## Skips, by name

- `control planned-only-verdict` — not run to green here; expected
  failure post-landing, lead retires it at merge (R6 follow-up).
- `board` budget — not run (lead-only under board.lock).
- VECS wiring of the four `*str*.vec` files into `tools/run.sh` —
  lead merge-time wiring (R6); until then the runner replays them by
  explicit filename as done in every run above.
- MPFR on beyond-H inputs — deliberately not used (the two-step
  result can differ from MPFR's single rounding; ruling R4). Those
  cases are decided by the exact two-step reference only.
- Berkeley — no coverage of character conversions exists there
  (SF-0 §4); not used.
- Bench — not run (never a correctness verdict; nothing here claims
  performance).

## Findings during the work (also in the ledger)

- Two lead runner bugs measured and lead-fixed on main: char-from
  flags token index (f3c48b8) and char-to operand width from
  retkind SPECIAL instead of argkinds[0] (83622cf). Both were
  invisible while the rows were planned (SKIP precedes the char
  path).
- tables/implemented.tsv as committed is CRLF throughout (779/779
  lines, measured); my 12 appended rows are LF per the brief, so the
  file is now mixed at exactly those rows. gen_tables.py tolerates
  both (drift check passes). Named here so the verifier does not
  read it as accidental.

## What this brief got wrong (for the record)

Carried from the design entry, unchanged after implementation:
(1) SF-0 §2.6 rests on "the grammar S1 extracted", but the standard
defines no finite-decimal grammar and S1 accordingly extracted none —
the input grammar is a project decision (rulings R1/R3), not a
discovered fact. (2) "Route final rounding through
msf_pack_generic wherever the exact value is in hand" cannot cover
the two output roundings (decimal digit string, hex fraction);
those round on exact digit/bit tails instead, as designed. (3) The
brief's "all 5 rounding modes" for tie sets: the API has four
attributes (ties-to-away is operation-named only, SF-0 §2.3); tie
sets cover all four.

Elapsed: first ledger entry 2026-10-27 08:28:15 -0700; commits at
09:02:58 -0700 — inside the 360-minute box with the 300-minute
checkpoint not reached.
