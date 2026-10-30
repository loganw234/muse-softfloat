# verifier-w1prep report: Wave 1 lead-prep commit de2d48c

Stance: disconfirm-only. Target: `de2d48c59a11c3b1dc94ba88a6cb74d6817745da`
(parent `36ca82e`). Workspace `C:\Users\logan\source\repos\Muse-Softfloat`,
repo `muse-softfloat/`. Push gate verdict: **READY** — zero (a), zero (b),
8 notes (N1–N8 below, none blocking).

Counts: replay 18590/18590 lines agree; directed 12160 kept, 0 mismatches;
decode 2016 cases + 13 NaN checks pass; cmp 214/214; status rows 63/783;
smoke 29982/29982; standard 1117504/1117504; attacks 8/8;
oracle 2136/2136 lines, 0 mismatches; mutations 3/3 refused.

## 0. Environment (all in scratch/verifier-w1prep/, tree untouched)

- `git status --short` inside `muse-softfloat/` is empty after all work.
- mingw64 gcc 16.1.0 needed `C:\msys64\mingw64\bin` first on PATH
  (else cc1 dies 0xC0000135) and scratch TMPDIR/TMP/TEMP
  (sandbox denies the default Local\Temp).
- `git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat`
  used for every git read. No `cft*` file anywhere under
  `muse-softfloat/`, `scratch/`, `ledger/`.

## 1. Pack generalization: msf_pack_generic vs independent rational reference

Own reference `wv_packref.py` (no import/reuse of `tests/gen_vectors.py`;
integer/Fraction organization of my own: exact value as
`(sig+f)*2^exp2` with `f` in `{1/4,1/2,3/4}`, ulp grid from clamped
exponent, integer round per mode, then overflow/underflow/pack with
tininess AFTER). C driver `wv_packdrv.c` calls `msf_pack_generic`
directly (linked `src/msf_roundpack.c` + `src/msf_wide.c`).

Outcome-invariance discipline kept: a case counts only if all three `f`
fractions agree (non-invariant cases are dropped and counted).

Part A — replay of committed vectors (exact command):

    .venv/Scripts/python.exe scratch/verifier-w1prep/wv_packref.py \
      scratch/verifier-w1prep/wv_packdrv.exe scratch/verifier-w1prep/wv_packdiff.txt

Output (`wv_packdiff.txt`):

    replay muse-softfloat/tests/vectors/pack16.vec: 6160 lines recomputed, 0 mismatches, 0 domain-skips
    replay muse-softfloat/tests/vectors/pack32.vec: 6160 lines recomputed, 0 mismatches, 0 domain-skips
    replay muse-softfloat/tests/vectors/pack64.vec: 6270 lines recomputed, 0 mismatches, 0 domain-skips

Part B — directed differential, own design, per width (kept = sticky-
invariant; LCG section seeds differ per width):

    directed f16: 4060 generated, 4060 kept-invariant, 0 dropped, 0 C-vs-ref mismatches
    directed f32: 4040 generated, 4040 kept-invariant, 0 dropped, 0 C-vs-ref mismatches
    directed f64: 4060 generated, 4060 kept-invariant, 0 dropped, 0 C-vs-ref mismatches
    TOTAL mismatches (replay+differential): 0

Design coverage per width: (a) smallest-normal crossings, exact 2^emin
and +-6 ulp-scales x 6 sig shapes x sticky x 5 modes x 2 signs;
(b) overflow deliveries, 3 sigs x 4 exp2 x sticky x 5 modes x 2 signs
(all mode/sign overflow directions: to-inf vs max-finite per the kernel
rule); (c) exact subnormals 6 sigs x 5 exp2 x 5 modes x 2 signs, sticky 0;
(d) ties both ways at 7 binades x 5 modes x 2 signs (guard=1, rest 0);
(e) sticky-sensitivity pairs (same tuple sticky 0 vs 1);
(f) zero/domain edges; (g) 1600-case deterministic LCG sweep.
Sticky-sensitivity measured in-ref: per width 950-960 sticky 0/1 pairs,
270-310 with outcomes that flip on sticky — every one matched the C
kernel exactly (the 0-mismatch total includes them).

Binary64 vs P0: `git diff 36ca82e de2d48c --numstat -- tests/vectors/pack64.vec`
is empty and both revisions list blob `59ce6e6...` — byte-identical.
Runner replay of pack64.vec inside smoke: 6270 vectors, 0 failures.
Claim "binary64 behaviour is unchanged (P0 pack64 vectors byte-identical)"
HOLDS. New widths gate 6160+6160 committed lines, all replayed green in
smoke (files `pack16.vec`/`pack32.vec` compare=exact).

Verdict probe 1: no (a), no (b). Method limit N7: my LCG sigs carry ~32
bits of entropy (top bits zero); huge-sig paths are covered by sections
(a)/(b)/(d) with 2^127-scale sigs, not by the sweep.

## 2. msf_decode.h: decode, finite compare, NaN delivery

Self-checking C probe `wv_decode.c` (built with mingw64, linked roundpack
+ wide). Decode checks re-derive sign/class/exp/sig from field
definitions: 2 signs x 7 exponents x 12 fracs = 2016 cases across f16/f32/f64.

    ./scratch/verifier-w1prep/wv_decode.exe
    part_decode done
    INFO neg-tiny-quiet f64->f32 = 00000000ffc00000 (default would be 7fc00000)
    part_nan done
    WV_DECODE: ALL PASS

`wv_cmpref.py` (exact Fraction oracle) vs `wv_cmpdrv.c` (calls
`msf_cmp_finite`): 214 adversarial pairs, 0 mismatches
(`wv_cmpdiff.txt`: "cmp pairs: 214, mismatches: 0"). Pairs: signed-zero
all-combos all formats; largest-subnormal vs smallest-normal both signs;
f64 exponent gaps >2000 (min-subnormal vs max-normal, vs zero);
adjacent encodings across exponents; cross-format same-value pairs.

NaN matrix checks (all pass): (i) qNaN-first + sNaN-second delivers the
sNaN quieted + invalid — header behavior confirmed; (ii) sNaN-first wins;
(iii) two sNaNs -> FIRST wins; (iv) quiet-only -> first quiet, no invalid,
f64->f32 payload >>29 + quiet bit; (v) no-NaN + invalid_without_nan ->
default qNaN + invalid; (vi) no-NaN w/o invalid -> returns 0, untouched;
(vii) widening f32->f64 payload <<29; (viii) narrowing with payload bits;
(ix) payload 1 narrowing to zero -> 0x7fc00000; (x) negative sNaN sign
preserved + invalid; (xi) FMA (inf, zero, qNaN): helper delivers the
addend with flags==0, caller-side invalid OR gives (invalid, addend) —
exactly the header's split contract ("the caller raises invalid for the
product and this helper delivers the addend under (c)"); (xii) f16->f64
widening exact.

Two of my first-draft expectations were wrong, both my test-constant bugs
(f64 quiet bit is 2^51; I first wrote 0x7ff4... patterns = signaling),
fixed before the green run — recorded so a re-reader is not confused.

N1 (note, spec-gray, not a (b)): `msf_nan_to_dest`'s truncate-to-default
branch is unreachable as coded — `dpayload |= df->quiet_bit` precedes
`if ((dpayload & df->frac_mask) == 0u)`, and quiet_bit lies inside
frac_mask, so the condition is always false. Observably: positive inputs
truncating to zero yield inf|quiet == default_qnan (identical), but
negative inputs yield sign-preserved 0xffc00000 (measured INFO line),
whereas the header prose says "the default quiet NaN is returned".
SF-0 2.5 simultaneously says "preserving sign and the payload bits",
so both readings live in the same paragraph; IEEE 754-2019 leaves NaN
propagation implementation-defined beyond quieting. Recommend the lead
restate the header prose (sign-preserved quiet NaN; equals default for
positive inputs) rather than change code. No verdict impact.

N2 (note): the (b)/(c) priority reading does NOT contradict SF-0 2.5.
The matrix is an ordered list; (b) is existential ("a signaling NaN
input ... delivers that operand") while (c) delivers "the first NaN
operand" in the branch where no sNaN exists. The header's if/else chain
(first sNaN in operand order, else first quiet) is a faithful
disambiguation. The misreading (first-NaN-overall-wins, i.e. quiet-first
beats a later sNaN) is rejected by the matrix order. Honestly classified
as note, not finding.

Verdict probe 2: no (a), no (b).

## 3. Status mechanism (mutate copies; tree untouched)

`wv_status.py` output (`wv_status.txt`):

    operations.tsv columns: op|std_name|clause|sig|rounding|flags|wave|authority|vectors|comparison
    implemented.tsv rows: 63 (header name|wave)
    COVERAGE.tsv rows: 783
    operations.tsv has no status column: CONFIRMED
    operations.tsv doc comments agree (status lives in implemented.tsv): CONFIRMED
    implemented.tsv header claims single status source: CONFIRMED
    COVERAGE implemented=63 planned=720
    COVERAGE status matches implemented.tsv 1:1: CONFIRMED
    dispatch rows parsed: 783
    implemented+dispatch-bound(non-NULL call): 57
    implemented but NULL call (non-replayable sigs): 6 [msf_lower_flags, msf_raise_flags, msf_test_flags, msf_test_saved_flags, msf_restore_flags, msf_save_all_flags]
    dispatch binds exactly implemented(+replayable) set: CONFIRMED
    mutate unknown-name: rc=1 refused=True
    mutate duplicate-row: rc=1 refused=True
    mutate wave-mismatch: rc=1 refused=True
    generator refuses all three mutations: CONFIRMED

"Dispatch binds exactly the implemented+replayable set": the 63
implemented split into 57 bound trampolines (every replayable sig) plus
the 6 flag_op entries (non-replayable by design, NULL call); all 720
planned rows carry NULL and the runner reports them not-implemented by
name. Status/wave in dispatch match COVERAGE row-for-row (783/783).

Verdict probe 3: no (a), no (b).

## 4. Runner: budgets, compare directives, ingest

Re-ran from a clean tree under Git Bash (commit's front door):

    tools/run.sh smoke    -> budget smoke: PASS in 7s; total 29982 passed
                             29982 failed 0 malformed 0 skipped-planned 0;
                             VERDICT: PASS; 9/9 controls refused
    tools/run.sh standard -> total 1117504 passed 1117504 ... VERDICT: PASS
                             (917504 f16-exhaustive + 200000 pack-sweep)

29,982 = 2352*3 encodings + 4336 copysign + 6270 pack64 + 6160 pack32 +
6160 pack16 — matches the commit count exactly.

Compare-directive attacks (`wv_cmpattack.py`, fresh runner binary,
8/8 as designed):

    A nan-class still compares flags exactly: OK [rc=1 verdict=FAIL]
    B nan-class rejects sNaN where quiet expected: OK [rc=1 verdict=FAIL]
    B2 nan-class accepts quiet for quiet-expectation: OK [rc=0 verdict=PASS]
    C berkeley-int compares result w/o invalid: OK [rc=1 verdict=FAIL]
    C2 berkeley-int still compares flags w/ invalid expected: OK [rc=1 verdict=FAIL]
    D directive not retroactive (pre line fails): OK [rc=1 verdict=FAIL]
    D2 directive scoped + reset works: OK [rc=0 verdict=PASS]
    E flags compared for real (exact): OK [rc=1 verdict=FAIL]

N4 (note): the berkeley-int result-skip half cannot fire on any
currently-implemented op (pack never sets invalid; no integer conversions
land yet), so C2 pins the flags half and code reading pins the skip half
(`expect_flags & INVALID` -> result_ok=1). Exercisable once Wave 1 lands
to_int ops.

Ingest (`tests/berkeley_ingest.py`, pinned testfloat_gen.exe):

    --fn f32_to_f64 --rm te --level 1      -> 600 cases, compare=nan-class
    --fn f64_to_i32 --rm te --level 1      -> 768 cases, compare=berkeley-int
    --fn f64_roundToInt --rm te --level 1  -> 768 cases, compare=nan-class
    --fn f64_add --rm te --level 1 --take 500 -> 500 cases (commit's "500
      well-formed lines" reproduces with --take 500; full level-1 is 46464)
    replay of the 500-line f64_add file: total 500 passed 0 failed 0
      malformed 0 skipped-planned 500, VERDICT: FAIL (zero passes), runner
      rc=1, skips named ("msf64_add not implemented (planned wave 1)").

Oracle validation: fresh Windows objects built from the pinned
`scratch/oracles/SoftFloat-3e/source` (+8086-SSE, platform header from the
pinned Linux-x86_64-GCC build dir, P0's flag set) into
`scratch/verifier-w1prep/oracle/` (326/345 files; N8 below), archived to
`wv_oracle.a`; `wv_oracle_check.c` recomputes every ingested line through
direct SoftFloat calls (`f32_to_f64`, `f64_to_i32(..., near_even, false)`,
`f64_roundToInt(..., near_even, false)`) with MY flag translation (written
from the measured header order softfloat.h: inexact=1, underflow=2,
overflow=4, infinite=8, invalid=16) and MY masking implementation:

    oracle-check wv_f32_to_f64.vec: 600 lines, 0 mismatches, inexact=0 invalid=5
    oracle-check wv_f64_to_i32.vec: 768 lines, 0 mismatches, inexact=0 invalid=267
    oracle-check wv_f64_roundToInt.vec: 768 lines, 0 mismatches, inexact=0 invalid=7

2136/2136 agree; inexact=0 everywhere corroborates the commit's
"exact=false semantics (no inexact ever appears)". Berkeley's flag order
independently confirmed from `source/include/softfloat.h` lines 85-89.

Refusals: `--fn f64_to_i32_exact_ties_to_even` -> rc=1, 0 cases;
`--fn f64_roundToInt_exact` -> clean "no ingest mapping" rc=1;
`--fn bogus_op` -> clean "no ingest mapping" rc=1;
`--fn f64_to_i32 --rm -` -> maps to ties_to_even (lenient default).
N3 (note): exact-int variants are refused only incidentally — map_fn
prints a garbage op name (`msf32_exact_ties_to_even_from_f64`) and the
refusal comes from testfloat_gen rejecting the function (0 cases, rc=1,
and the runner would FAIL a 0-case file anyway). Suggest a clean refusal
in map_fn. The `--rm -`-means-te leniency is consistent with
testfloat_gen's own default; observation only.

Verdict probe 4: no (a), no (b).

## 5. Commit-message claims vs tree; clean room; harness

- counts: smoke 29,982 vectors (recomputed above from the per-file
  inventory) incl. new pack widths; 9/9 controls; `pack64.vec`
  byte-identical to parent (empty numstat, blob `59ce6e6...` both revs);
  `pack16.vec`/`pack32.vec` 6160 lines each ("6,160 each" HOLDS).
- `tables/implemented.tsv` = 63 rows ("seeded with the P0 63" HOLDS).
- "No operation's status changes": COVERAGE parent->HEAD diff
  (`wv_claims.py`): 783 rows both, 0 status flips, 0 added, 0 removed.
  Authority flips: exactly 63, every one berkeley->mpfr-exact on an
  exact-family row (3 `round_to_integral_exact` + 60 `to_<int>_exact_*`
  = the "authority corrections ... on the 6 named rows", which are the 6
  FAMILY rows in operations.tsv: `round_to_integral_exact`,
  `to_<int>_exact_{ties_to_even,ties_to_away,toward_zero,
  toward_positive,toward_negative}` — `berkeley`/`auto-int` -> `mpfr-exact`).
- "family-level status column left operations.tsv": header row now
  `op|std_name|clause|sig|rounding|flags|wave|authority|vectors|comparison`
  (no status), doc comment reads "(status lives in
  tables/implemented.tsv, per instantiation)". HOLDS.
- Clean room: word-exact `float|double` in `src include` -> no matches;
  `hauser|jhauser|uc regents|softfloat-3e` in `src include` -> no matches;
  `berkeley|testfloat` in `src include` -> no matches; no `*cft*` names.
- Harness (`board/harness_main.c` read in full): same `find_op` +
  `op->call` trampolines + status gate + `E unknown/planned/malformed/noshape`
  replies; pack path calls `msf_pack_generic` with the same arg/hash
  folding as the runner; `R %016llx %02x` replies and the running SHA-256
  now fold real flags (previously hardcoded `00`) — "mirrors the same
  calls and flags" HOLDS by source reading. Deltas noted, both benign:
  harness `kind_width` folds F64/I64/U64 into `default: 64` (equivalent);
  no `# compare=` handling on-board (correct — masking is a host-oracle
  concern; the board returns raw result+flags). Board untouched: no
  serial interaction, no `run_board.sh` invocation.
- Firmware rebuilds: `build/board-fw/fw/msf_board_harness.{elf,bin,hex,uf2}`
  all stamped 19:53, newer than the harness source (19:48); `.ninja_log`
  records `harness_main.c.obj` built. HOLDS without rebuilding.
- N5 (note): commit's "500 well-formed lines" for f64_add level 1 is the
  `--take 500` measurement (full level-1 streams 46464 cases); the
  parenthetical behaviors (flags translated, malformed=0, named skips,
  FAIL on zero passes) all reproduce exactly.
- N6 (note, cosmetic): dispatch header comment says planned entries
  "carry NULL" but `gen_tables.py` emits literal `0` (equivalent null
  pointer constant; runner tests `== NULL`). Suggest aligning word or
  token.
- N8 (note, pre-existing, not this commit): 19 f128M/extF80M `*M` oracle
  sources fail to compile under the 8086-SSE specialization headers
  (implicit declarations, e.g. `softfloat_tryPropagateNaNExtF80M`);
  untouched by this commit and unneeded for the validated functions
  (link + 2136/2136 agreement prove sufficiency). Filed so the gap is
  on record.

Verdict probe 5: no (a), no (b).

## 6. Classification and what was not done

- (a) regressions: none — 0 lines.
- (b) wrong answers: none — 0 lines.
- Notes N1–N8 above (header-prose precision, incidental refusal path,
  unexercisable masking half, measurement precision, cosmetic comment,
  method limits, pre-existing oracle gap). None blocks the push.
- Ledger: entry appended via kit `tools/ledger.sh` (or staged body —
  see reply).
- Did NOT do: touch the board (no serial/lock interaction); rebuild
  firmware (timestamps + ninja log sufficed); run `board`/`bench`
  budgets; modify any project file (git status clean); use any file
  with `cft` in its name; spawn background work (nothing running).
