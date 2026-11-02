# Verifier-w1f32 report — ParcelRound verification of the wave-1 binary32 parcel

Stance: disconfirm only. Nothing in the copy was changed. "Found nothing"
was not the outcome.

## Verdict: NOT READY

The worktree at `worktrees/verify-f32` (HEAD `1779df0`, base `4cdb912`)
fails its own committed vectors (449 mismatches in `tests/vectors/arith-f32.vec`),
fails the independent Berkeley differential on two root causes, and carries one
stale committed expectation. Three implementation defects (two root causes in
`src/msf32.c` plus one missing flag on the same function) affect all four
`msf32_div*` and all four `msf32_sub*` instantiations. The HEAD commit message
claims "(READY)"; the evidence below contradicts it.

Findings (one claim per line; `(a)` regression/claim deviation, `(b)` wrong answer):

- `(b)` `worktrees/verify-f32/src/msf32.c:204` — every finite nonzero `msf32_div*`
  quotient is exactly 2x the correct value (`-62` should be `-63`); smallest
  repro `msf32_div te 3f800000 3f800000 -> 3f800000 00` (copy delivers `40000000`).
- `(b)` `worktrees/verify-f32/src/msf32.c:182` — finite-over-zero division never
  raises division-by-zero; smallest repro `msf32_div te 3f800000 0 -> 7f800000 02`
  (copy delivers flags `00`).
- `(b)` `worktrees/verify-f32/src/msf32.c:126` — `msf32_sub*` with an infinite
  subtrahend and finite minuend delivers the wrong-signed infinity (uses `b.sign`
  where the negated `effb` is required); smallest repro
  `msf32_sub te 0 7f800000 -> ff800000 00` (copy delivers `7f800000`).
- `(b)` `worktrees/verify-f32/tests/vectors/arith-f32.vec:5` — stale expectation:
  `msf32_add te 0 80000001 -> 80000000` should be `-> 80000001` (the copy's own
  regenerated vector agrees the implementation's `80000001` is correct; the
  implementation is right here, the committed line is wrong).
- `(a)` Claim-surface deviations vs base `4cdb912`: shared files changed although
  the brief expects them byte-identical (`src/msf_roundpack.c`, `tests/gen_vectors.py`,
  `tests/berkeley_ingest.py`, `tools/run.sh`, `tests/vectors/pack16|32|64.vec`
  64 lines each); and `tools/run.sh` smoke/standard never replays the parcel's own
  `tests/vectors/*-f32.vec` (`tools/run.sh:179` VECS lists only P0 vectors), so both
  PASSing budgets say nothing about the 173 claimed instantiations.

Counts and classes at the end are in section 7.

## 1. What was verified and how

Copy: `worktrees/verify-f32` at `1779df0` (base `4cdb912`). Sources for clause
questions: `docs/studies/SF-0.md` (clauses 2, 3, 4, 5, 7) and
`scratch/S1/report.md`. Oracle: pinned `testfloat_gen`
(`scratch/oracles/TestFloat-3e`, 8086-SSE specialization, tininess after rounding).
All probes used Git Bash with `TMPDIR`/TMP/TEMP inside the scratch dir, the
workspace `.venv` Python, and `git -c safe.directory` for the copy. The machine
was under third-party load during the runs; durations below are observed only.

Probes, all with my own script files in `scratch/verifier-w1f32/`:

1. Budgets: `tools/run.sh smoke` and `standard` in the copy (exit codes, inventory,
   failures by line); regen `tests/gen_vectors_f32.py directed` to a temp dir and
   diff vs committed; regen `tools/gen_tables.py` to temp with byte-compare of the
   4 outputs.
2. Independent differential vs the pinned Berkeley oracle: re-derived the Berkeley-
   decided set from COVERAGE (38 rows: homogeneous add/sub/mul/div/sqrt/fma,
   remainder, 5 named roundToIntegral, from_i32/u32/i64/u64, 20 non-Exact to-int,
   from_f32, from_f64); streamed testfloat_gen level-1 complete for the big four
   plus sqrt and rem across all 5 modes, mulAdd level-1 `--take 500000` te/ta, all
   Berkeley-covered conversions at level 1 (all rms, incl roundToInt), comparisons
   level 1 as a cross-check; replayed every stream through the copy's runner via
   `tests/berkeley_ingest.py`.
3. My own independent exact-rational reference (`ref3.py`, written fresh for this
   verification from S1/SF-0, no imports from the copy's generators) with directed
   encodings I chose: special values per Clauses 6/7, signed zeros, NaN matrix of
   SF-0 2.5 incl payload conversions and the FMA 0xinf+qNaN ruling, saturation rule
   for to-int; families next, scaleB, logB, totalOrder, remainder, all 22 compares
   incl cross-format, Exact variants, 8/16-bit ints, cross-format arith (incl f64
   exact-midpoint double-rounding traps). 127,958 cases.
4. Source review of `src/msf32.c` against COVERAGE/SF-0 mandates (single rounding,
   NaN paths, flag exactness, kernel window invariants); names wrong special-case
   entries with counterexample vectors (see findings).
5. Claims: `implemented.tsv` rows (173 new, all `msf32_*`), `diff --stat 4cdb912`,
   shared-file identity, symbol/type scans from the run.sh output.

## 2. Probe 1 — budgets, inventory, regen drift

`tools/run.sh smoke`: exit 0, budget PASS. Inventory observed in the log:
29982 vectors passed, 0 failed; provenance `exact-py:directed-encodings` 7056,
`exact-py:copysign-sample` 4336, `exact-py:pack64-directed` 6270,
`exact-py:pack32-directed` 6160, `exact-py:pack16-directed` 6160; manifest 18 entries
match; expect-counts 5 provenance tags; unit tests PASS; drift check 4/4 generated
files byte-identical; type scan clean; target undefined symbols 21, all benign
(`__aeabi_*`, `memcpy`, intra-library `msf_*` dispatch entries); all 9 negative
controls refused (corrupted-expected-bit, wrong-nan-expectation,
wrong-rounding-mode, wrong-flag-bit, stale-manifest, count-mismatch,
wrong-tininess-polarity, x87-compiler-refusal, planned-only-verdict).
`tools/run.sh standard`: exit 0, budget PASS (smoke plus f16-exhaustive 917504 and
pack-sweep 200000, all PASS).

Critical scoping fact: neither budget replays any of the parcel's own
`tests/vectors/*-f32.vec` files (VECS at `tools/run.sh:179`). Both budgets can PASS
while every parcel vector fails. The parcel's vectors were replayed with the
copy's own runner instead (probe 2a): `arith-f32.vec` FAILS (449 mismatches);
`fma-sqrt-f32`, `conv-int-f32`, `rint-misc-f32`, `toint-f32`, `compare-f32`,
`encodings-f32` all VERDICT: PASS.

Regen drift: `tools/gen_tables.py` to temp — all 4 outputs byte-identical to the
committed files (no drift). `tests/gen_vectors_f32.py directed` to temp:
`compare`, `fma-sqrt`, `rint-misc`, `toint` byte-identical; `arith-f32.vec` differs
in exactly 1 line (line 5, finding F4); `conv-int-f32.vec` differs in 16 lines that
are operand-choice only (`7fffffff` vs `7ffffffe`, expectations arithmetically
correct in both; benign drift, implementation matches the committed lines).

## 3. Probe 2 — Berkeley differential (approx 2.01M cases)

Re-derived from COVERAGE: 38 Berkeley-decided wave-1 rows (homogeneous add, sub,
mul, div, sqrt, fma, remainder, 5 named roundToIntegral, from_i32/u32/i64/u64,
20 non-Exact to_i32/u32/i64/u64, from_f32, from_f64). Comparisons are
project-exact(+berkeley-check) per COVERAGE, run here as a cross-check only.
`f32_to_f64` was excluded (maps to the f64 parcel's op, planned here).

Pass (exact compare after ingest, approx 1.82M cases, 0 mismatches): add 232320,
mul 232320, sqrt 3000, remainder 46464, mulAdd te+ta 1000000, f32_to_i32/i64/ui32/ui64
12000, i32/i64/ui32/ui64_to_f32 11280, f64_to_f32 3840, roundToInt 3000,
comparisons f32_eq/eq_signaling/le/lt/le_quiet/lt_quiet 278784.

Fail: `f32_sub` 335 cases x 5 modes (all involve an infinity operand; only two
got/want shapes, both the sign flip of finding F3). `f32_div`: te 37989, tz 37883,
tp 37883, tn 37883, ta 38005 (flag-only bits-match subset 335/344/354/354/364, every
one `gotflags=00 wantflags=02`, i.e. the missing divisionByZero of finding F2; the
rest are the 2x value error of finding F1, including its induced
overflow/underflow flag shifts at the boundaries). No NaN-input div mismatch and
no non-inf sub mismatch occurred anywhere.

## 4. Probe 3 — independent exact-rational attacks (127,958 cases)

My own reference (`scratch/verifier-w1f32/ref3.py`, fresh exact Fraction
decode/round/pack with Clause 7.5 after-rounding tininess, SF-0 2.5 NaN matrix,
S1 inexact rules: named roundToIntegral/convertToInteger never signal inexact,
Exact variants signal inexact only in-range). Three of my first-draft reference
rules disagreed with the copy and investigation showed my draft wrong each time
(logB small-integer f64 encoding, negative to-int two's complement, remainder
correction-direction sign); the corrected reference is what ran. Two more of my
draft vectors were invalid (out-of-range from-int inputs, a mislabeled sNaN pool
entry that is actually finite); fixed before counting.

Pass (0 mismatches): all 22 compares homogeneous and `_f64` cross-format 14784;
f32<->f64 conversions incl 136 exact-midpoint double-rounding traps 932;
from-int 8/16/32/64 708; logB 182; NaN matrix incl payload narrowing/widening,
truncation-to-default, and FMA 0xinf with quiet-NaN addend 567; next_up/down 364;
remainder 1555 (incl exact-half ties and the s>=25 early-out edge);
rint named + Exact 990; scaleB all modes incl fractional/zero/infinite N 5612;
to-int all widths/signs/modes incl Exact and saturation 11680; totalOrder class
skeleton 468. Signed-zero matrices pass except the known sub cases below.

Fail, every one at the three known-bug loci and no other: cross-format div 4918
(2x + div0), homogeneous div 800, cross sub with infinite operand 224, zero-matrix
sub with infinite operand 16. Zero NaN-payload, zero flag-rule, zero rounding-mode
mismatches outside those loci.

TotalOrder payload direction (same-class NaN pairs with differing payloads, 12
assertions over 6 unordered pairs x total/total_mag): exactly one direction
returns 1 per pair, 0 antisymmetry violations; the implementation is a consistent
total order. The direction itself (larger-payload-first for negatives,
smaller-payload-first for positives) is beyond what S1/SF-0 state in evidence and
is recorded as a ruling gap, not a finding.

## 5. Probe 4 — source review of src/msf32.c (830 lines)

Structure matches the brief: decode to exact sig*2^exp, NaN via the shared
`msf_nan_delivery` helper in the documented (signaling-first, then quiet, then
default + invalid) order with FMA operand order multiplicand/multiplier/addend,
exact integer work over `msf_u128`, then ONE pack per op (`msf_pack_f32`, except
logB which packs binary64 as SF-0 2.2 requires). No double rounding through
another format exists anywhere: cross-format paths decode f64 exactly (53-bit sig)
and pack once; mul product (<=106 bits), div long division (128 quotient bits +
sticky), sqrt integer sqrt (64-bit + sticky), fma (product aligned with jam +
single pack) all carry exact remainder evidence to the single rounding event.
Rounding-mode plumbing is consistent (public and internal enums share values
0..3). `rint`/`toint` inexact discipline matches S1 (5.8/5.9): named forms never
signal inexact, Exact forms signal it only when the rounded integer is in range;
out-of-range and non-finite signal invalid only with the header saturation rule.
`norm126` kernel-window comment holds (inputs are decoded sigs <=53 bits and
exact products <=106 bits). `msf_u128_shr_jam` absorbs shifts >=128 (shared code,
unchanged). `msf_cmp_finite` is exact (shared code, unchanged); cross-format
compares passed 14784/14784 against my independent relation computation.
`total_order_key`/`total_order_mag` implement the S1 class skeleton including
-0 < +0; verified on 468 skeleton cases plus the antisymmetry audit above.

Wrong special-case entries (each with a counterexample vector):

- `src/msf32.c:182-184`: the finite-divisor-zero path returns infinity without
  setting `MSF_FLAG_DIVISION_BY_ZERO` (Clause 7.2). Counterexample:
  `msf32_div te 3f800000 0 -> 7f800000 02` (copy gives flags `00`).
- `src/msf32.c:122-127`: the infinity fast paths in `add_impl` return
  `INF32(b.sign)` for subtraction although the operand was negated (`effb`);
  only the NaN path and the `a`-infinity path are sign-correct. Counterexample:
  `msf32_sub te 0 7f800000 -> ff800000 00` (copy gives `7f800000`).
- `src/msf32.c:204`: the division exponent `-62` should be `-63`
  (`quo = floor(num/den)` needs `a.exp - b.exp + (la - lb) - 63`; 1.0/1.0 yields
  `quo = 2^63`, `exp = -62`, i.e. 2.0). Counterexample:
  `msf32_div te 3f800000 3f800000 -> 3f800000 00` (copy gives `40000000`).

## 6. Probe 5 — claims

`tables/implemented.tsv`: 173 wave-1 rows, every one `msf32_*` (plus 63 wave-0
rows); the count matches the brief's 173. COVERAGE composition of the 173: 38
berkeley, 86 mpfr-exact, 25 project-exact, 24 project-exact+berkeley-check.
`git diff --stat 4cdb912..HEAD`: 19 files; beyond the brief's stated surface, the
shared files `src/msf_roundpack.c` (Clause 7.5 unbounded-exponent tininess fix +
comment), `tests/gen_vectors.py` (same fix in the reference), `tests/berkeley_ingest.py`
(eq mapped quiet, was signaling), `tools/run.sh` (planned-only control op
msf16_add), and `tests/vectors/pack16|32|64.vec` (64 flag lines each, `10` -> `18`
underflow additions at the smallest-normal boundary) also changed. The new tininess
behavior is independently corroborated by probe 3 (my separate Clause 7.5
implementation agrees with the copy's pack on thousands of subnormal-boundary
cases with exact flag agreement), but the "nothing off-limits changed" claim is
factually false; the HEAD commit message ("Re-gated ... (READY)") discloses a
lead tininess/ingest fix, which the brief's surface description omits.
Symbol scan (from the smoke log): 21 undefined ARM symbols, all benign
(`__aeabi_*`, `memcpy`, intra-library `msf_*`); refused-helper grep clean.
Type scan: clean (no float/double words in src/include).

## 7. Counts and classes

- Committed vectors replayed with the copy's runner: 449 mismatches in
  `arith-f32.vec` (400 div: 132 + 120 + 76 + 72 across the 4 instantiations;
  48 sub-inf-sign: 12 x 4; 1 stale add expectation where the implementation is
  correct); all other committed f32 families PASS.
- Berkeley differential: 1,823,008 pass / 191,318 fail (1,675 sub-inf-sign =
  335 x 5 modes; 189,643 div = 37,989 + 37,883 x 3 + 38,005, of which 1,751 are
  flag-only missing-div0 and the rest the 2x value error with entrained flag
  shifts at overflow/underflow edges).
- Independent probe 3: 127,958 cases; 122,000 pass; 5,958 fail, all at the three
  known loci (div 2x + div0 across all 4 instantiations, sub inf sign across all
  4 instantiations).
- Regen: tables 4/4 byte-identical; vectors 4/6 identical, 1 wrong committed line,
  16 benign operand-choice lines.
- Classes: (b) wrong answer: div 2x quotient, missing divisionByZero flag, sub
  infinity sign, 1 stale committed expectation. (a) claim/process deviation:
  shared-file changes vs base, parcel vectors unwired from run.sh budgets,
  (READY) commit message contradicted by 449 committed-vector mismatches.

## 8. What passed (so nothing good is lost)

Berkeley-clean: homogeneous add, mul, sqrt, remainder, fma (1M mulAdd), all
32/64-bit int conversions both directions, f64->f32 conversion, named roundToInt,
all six Berkeley comparison spellings. Probe-3-clean: next, scaleB, logB,
totalOrder skeleton + payload antisymmetry, remainder, all 22 compares incl
cross-format, Exact variants, 8/16-bit conversions both directions, cross-format
add/mul/sqrt/fma incl double-rounding traps, same-format and f64->f32 conversion,
the full NaN matrix incl payload conversion and the FMA 0xinf+qNaN ruling,
saturation delivery, signed-zero rules except the known sub cases. Budgets smoke
and standard PASS with all 9 negative controls refusing. The implementation's
`add(0, -tiny) = -tiny` is correct against its stale committed line.

## 9. What I did not do (named gaps)

No board/bench budgets (no board gate claimed for this parcel); no ARM-target
execution beyond the symbol scan; no review of the sibling f64 parcel, its
scratch, its worktrees, `scratch/lead`, or anything with `cft` in its name
(untouched throughout); no decimal/hex character conversions (not wave-1 scope);
no MPFR cross-check of my own reference (exact rational arithmetic is the
decider where Berkeley is silent, per SF-0 4.3); totalOrder same-class NaN
payload direction and scaleB non-integral-N beyond the recorded project ruling
were verified implementation-vs-ruling only (S1/SF-0 silent in evidence);
timings are observed wall-clock under third-party machine load, quoted as neither
rates nor claims; named negative controls were observed refusing in the copy's
own control logs, not re-broken independently.

Ledger: appended to `ledger/verifier-w1f32.md` via the kit `ledger.sh` (or staged
in `scratch/verifier-w1f32/ledger-body.md` if the tool was unrunnable — see reply).
Report path: `scratch/verifier-w1f32/report.md` (this file).

