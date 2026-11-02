# verifier-w164 report — wave-1 binary64 parcel (verify-f64 @ d1e9442)

Stance: disconfirm only. Nothing in the copy was fixed. Machine under
third-party load throughout; wall times are named, no rates claimed.
Oracle: `scratch/oracles/TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen.exe`
via `MSF_TESTFLOAT_GEN`, default `-tininessafter` (matches SF-0 2.5).
Brief count wins: 173. Measured: COVERAGE wave=1 `msf64_*` rows = 173,
`implemented.tsv` wave=1 `msf64_*` rows = 173, no disagreement.

Verdict: NOT READY. 6 findings ((a)x3 (b)x3), all reproduced below.

## Outliers (one claim per line)

- (a) F-divzero — `worktrees/verify-f64/src/msf64.c:201` — `div_core` returns infinity
  for finite/zero without `MSF_FLAG_DIVISION_BY_ZERO` (parcel branch
  `worktrees/w1-f64/src/msf64.c:202` has the flag line; the copy dropped
  it). All 4 div instantiations affected.
  Repro: `tests/vectors/arith-f64.vec:53`
  `msf64_div_f32_f32 tz 7fffff 80000000 -> fff0000000000000 02`
  (got `.../00`). Independent: Berkeley homogeneous `f64_div` level 1,
  329 fails / 46464 in EACH of te/tz/tp/tn/ta (e.g.
  `build/w1v/f64_div-te-l1.vec:6`
  `msf64_div te c7effff7ffffffef 0000000000000000 -> fff0000000000000 02`).
- (a) F-zerozero — `worktrees/verify-f64/src/msf64.c:93` — `add_terms` zero-zero rule
  uses `rm == MSF_IROUND_TOWARD_POSITIVE`; the Clause 6.3 rule (SF-0 2,
  brief, parcel branch line 93) is `rm == MSF_IROUND_TOWARD_NEGATIVE`.
  Exact cancellation (line 114) is correct; only (±0,∓0) operand pairs
  are inverted: tp gives −0 (want +0), tn gives +0 (want −0).
  Repro: Berkeley `build/w1v/f64_add-tp-l1.vec:272`
  `msf64_add tp 0000000000000000 8000000000000000 -> 0000000000000000 00`
  (got `8000000000000000/00`). 2 fails each in add tp/tn, sub tp/tn.
- (a) F-fmainf — `worktrees/verify-f64/src/msf64.c:281` — FMA infinite-product vs
  infinite-addend invalid condition uses `c.sign == psign`; the Clause 6
  rule (parcel branch line 282) is `c.sign != psign`. Like-signed
  inf+inf wrongly signals invalid; opposite-signed wrongly delivers.
  Repro: `build/w1v/f64_mulAdd-te-l1-t500000.vec:32046`
  `msf64_fma te 41dffffffffffffe 7ff0000000000000 7ff0000000000000`
  `-> 7ff0000000000000 00` (got `7ff8000000000000/01`).
  52 fails each in te/tz/ta, 249 each in tp/tn at take 500000.
- (b) F-genflags — `worktrees/verify-f64/tests/gen_vectors_f64.py:27` — `F_UNF = 0x04`
  (collides with `F_OVF`); the header bit is `0x08` (parcel branch line
  27 has `0x08`). Every underflow expectation the copy's generator emits
  is wrong (`14` for `18`). Committed vectors carry the correct `18`
  and pass, so the generator (not the library) is at fault.
  Repro: regenerate `tests/gen_vectors_f64.py directed` to temp and diff:
  59 changed pairs in `arith-f64.vec`, 112 in `misc-f64.vec`, all but one
  of the form `< ... 14` (regen) vs `> ... 18` (committed), e.g.
  committed `tests/vectors/misc-f64.vec:648`
  `msf64_scale_b te 800fffffffffffff bff0000000000000`
  `-> 8008000000000000 18`.
- (b) F-vec5 — `worktrees/verify-f64/tests/vectors/arith-f64.vec:5` — committed
  `msf64_div_f32_f32 te 0 80000000 -> 7ff8000000000000 00`; 0/0 signals
  invalid (Clause 7), correct flags `01`. The copy's own generator emits
  `01`, the parcel branch's committed line reads `01`, the implementation
  raises `01`. The copy's committed `00` is stale/wrong.
- (b) F-regatemsg — commit `d1e9442` message claims "the correct build passes all
  11,057" and "10,418,176 cases, 0 failures" for the re-gated Berkeley
  set. Measured in this copy with its own runner: directed 11012/11057
  (45 fail, all F-div above); `f64_div` level 1 fails 329/46464 per mode;
  `f64_mulAdd` fails at take 500000 in all 5 modes. The parcel's own
  `scratch/parcel-f64/regate-berk-f64_div-te-l1.log` claims
  `total 46464 passed 46464 failed 0` for the identical case this
  verification replays as 46135/329. The numbers do not reproduce.

## Notes (not verdicts)

- N1 negative-NaN totalOrder payload sub-order: observed descending
  payload for negatives (e.g. `total_order(fff8000000000000,`
  `fff8000000000001)` = 0), ascending for positives and in mag form.
  Implementation, parcel generator (`gen_vectors_f64.py:498`), and the
  canonical encoding-order key agree; no source in scope contradicts.
  Filed as interpretation point (Clause 5.10), not a violation.
- N2 `src/msf_roundpack.c` `round_inc` ties-to-away returns `guard`
  rather than `inexact`. Unreachable in every wave-1 msf64 path audited
  (integer forms round in `round_mag_int`; pack receives exact integers
  there); off-limits file, identical to parcel branch. No vector
  distinguishes it (1600 to-int + 358 rint probes pass).
- N3 `f64_to_f32` Berkeley level 1: 768 skipped-planned × 5 modes
  (`msf32_from_f64 not implemented (planned wave 1)` → `VERDICT: FAIL
  (no vectors passed; skips are not passes)`). Sibling parcel's rows;
  named skips, not copy defects.
- N4 symbol scan: SKIP-BY-NAME (`arm-none-eabi-gcc` absent); target gate
  not run. Type scan clean (no float/double words in `src/ include/`).
- N5 `msf64_from_f64` COVERAGE claims `testfloat-l2` vectors but
  testfloat_gen ships no same-format generator; covered by directed
  vectors only (3264 conv vectors pass; my 800 fresh convert cases pass).
- N6 tininess-UNF delivered with a min-normal result (e.g. exact-probe
  `msf64_div tn 10000000000000 bff0000000000001 -> 8010000000000000 18`):
  adjudicated CORRECT per the documented Clause 7.5 unbounded reading
  (`src/msf_roundpack.c:11-18`, lead fix 53acb1a, pack64 second-shape
  vectors). My first reference revision wrongly expected `10`; fixed.

## Probe evidence

All probes are my own script files in `scratch/verifier-w1f64/`, run
under Git Bash with TMPDIR/TMP/TEMP inside the copy/scratch and
`git -c safe.directory` for the copy path. Pinned host compiler
`x86_64-w64-mingw32 gcc 16.1.0 FLT_EVAL_METHOD=0` throughout.

### (1) Budgets, inventory, regen

- `v-smoke.sh`: `tools/run.sh smoke` in verify-f64 → PASS in 7s
  (`scratch/verifier-w1f64/v-smoke.log`). Inventory: compiler above;
  drift check 4/4 generated files byte-identical; unit sha256/flags/
  versions/wide PASS; manifest 18 entries; expect-counts 5 provenance
  tags; 29982 vectors (encodings 3×2352, copysign 4336, pack64 6270,
  pack32 6160, pack16 6160) all PASS; type scan clean; symbol scan
  SKIP-BY-NAME (N4); 9/9 negative controls refused (corrupt-bit →
  `VERDICT: FAIL`; nan-polarity/roundmode/flagbit → nonzero exit;
  stale-manifest → `MANIFEST MISMATCH`; count → `COUNT MISMATCH`;
  wrong-tininess build → `^FAIL` lines on pack64 second-shape cases;
  x87 → `compiler REFUSED ... dumpmachine=i686-w64-mingw32`;
  planned-only `msf16_add` → `SKIP ... not implemented` +
  `VERDICT: FAIL`).
- `v-standard.sh`: `tools/run.sh standard` → PASS in 38s; +917504
  f16-exhaustive +200000 pack-sweep, all PASS. Same run replays the 5
  committed f64 directed files with the copy's fresh runner:
  11057 total, 11012 pass, 45 FAIL (44 systematic div0 in cross-format
  div = finding F-div; 1 stale line = finding F-vec5).
  Per-file: arith 3984 (45 fail), compare 2302, conv 3264, misc 1222,
  nan 285 — all else pass.
- `v-regen.sh`: copy's `tests/gen_vectors_f64.py directed` to temp →
  compare/conv/nan byte-identical; arith drifts (59 pairs: 58 ×
  `14`-vs-`18` = finding F-genflags, plus line 5 = finding F-vec5);
  misc drifts (112 pairs, all `14`-vs-`18` = finding F-genflags).
  `tools/gen_tables.py` to temp → all 4 outputs byte-identical
  (`include/muse_softfloat.h`, `src/msf_formats.h`,
  `tests/msf_dispatch.h`, `docs/COVERAGE.tsv`).
- `v-branchregen.sh`: parcel-branch (`worktrees/w1-f64`) generator
  regenerates branch vectors byte-identically (all 5 files), pinning the
  drift to the copy (F-genflags, F-vec5).

### (2) Berkeley differential (independent driver `v-berk.sh`)

COVERAGE re-derivation: 38 wave-1 `msf64_*` rows name authority
`berkeley`: add/sub/mul/div/sqrt/fma (homogeneous), roundToInt ×5
named, rem, from_f32/from_f64, from/to 32/64-bit ints (20 to-int rows
use `exact-invalid-project-rule` comparison). Compares tested via the
6 testfloat fns per the parcel's mapping (eq→quiet fix verified in the
ingest diff). `ta` ingests use `-rnear_maxMag` (checked in ingest logs).

- Phase A (`v-berk-A.log`, 31 cases): add tp/tn 2 fails each, sub tp/tn
  2 each (F-zerozero); div te/tz/tp/tn/ta 329 fails each of 46464
  (F-divzero); mul/sqrt/rem/roundToInt×5 all PASS (mul 5×46464, sqrt
  5×768, rem 46464, roundToInt 5×768).
- Phase conv (`v-berk-conv.log`, 50 cases): f32_to_f64 5×600 PASS;
  all 8 int conversions × 5 modes PASS (768/768 ×20, 372/372,
  756/756 ×20); f64_to_f32 5×768 named skips (N3).
- Phase cmp (`v-berk-cmp.log`, 6 cases): 6×46464 PASS.
- Phase C (`v-berk-C.log`): f64_mulAdd level 1 take 500000 —
  te/tz/ta 52 fails each, tp/tn 249 each (F-fmainf; tp/tn excess is the
  FMA zero-sum path through finding F-zerozero).
- Berkeley totals: 3,795,688 cases, 2307 fails, 3840 named skips
  (f64_to_f32 ×5). Full per-case totals in
  `worktrees/verify-f64/build/w1v/logs/*.verify.log`.

### (3) Project-exact probe (own reference `v-exact.py`, 29,028 cases)

From-scratch Fraction reference (own decode/pack/specials; never
imports the copy's generator): Clause 6/7 specials, signed zeros, NaN
matrix SF-0 2.5 (payload widen f32→f64, quieting, FMA 0×inf+qNaN
ruling → invalid + addend), saturation rule (NaN→0, ±overflow→ends,
negatives→0 for unsigned), scaleB truncation-toward-zero + ±5000
clamp, Exact-inexact only when in-range fraction discarded (settled
against committed `to_u8_exact_toward_zero(-1.5) -> 0 01`), ties-even
remainder (incl. remainder(5,3) = −1 check present in rem-dir set),
all 22 predicates × homogeneous/cross, totalOrder/Mag (positive-NaN
payload ascending agrees over dozens of pairs; negative-payload pairs
in N1 observation file only), nextUp/Down boundary steps, logB
(incl. −inf+div0 on ±0), 8/16-bit ints + Exact, cross-format arith in
all 4 modes. Files `exact-tmp/w164-*.vec` (14 files), replayed with
the copy's runner (`v-exactrun.sh`): 28508 pass, 520 fail —
392 div0-class (F-divzero), 16 zero-zero tp/tn (F-zerozero), 96+16
FMA special (F-fmainf + FMA zero-sum). Eleven of my own reference bugs
were found and fixed during the run (documented in §Reference
self-corrections); the residue is exactly the three implementation
mutations, confirmed by class-wise audit (`v-classify2.sh`: zero
non-div arith FAILs outside (±0,∓0) tp/tn; zero div FAILs outside
got-00-want-02).

### (4) Source review (`src/msf64.c`, 879 lines, fully read)

- Single rounding: every core packs exactly once per return path
  (`add_terms` has three pack sites on disjoint paths; zero paths
  return `zero_bits`/`inf_bits` directly with no rounding event).
  No `float`/`double` types (type scan clean).
- NaN paths all enter through `msf_nan_delivery` first (2- and 3- and
  1-operand forms verified at every core); `to_int_core` handles NaN
  inline with the header rule (invalid + 0), outcome-verified.
- Flag exactness: computational families take flags only from the
  single pack except named invalid/div0 specials — except div, which
  never raises divisionByZero (F-divzero). rint named discards pack
  flags and adds Exact-inexact by hand; remainder packs exact with TE;
  compares/next/total raise only the specified invalid/none.
- Kernel window invariants commented at `add_terms` (118-bit window,
  ≤65 exponent gap) and `div_core` (122-bit quotient + sticky);
  sqrt (p+2 integer root + remainder-sticky) and FMA (exact 106-bit
  product through the shared window) follow the mandated shapes.
- Dispatch: all 173 instantiations present with correct format tags
  (add/sub/mul/div ×4, sqrt ×2, fma ×8, rint ×6, to-int 10×8,
  from-int ×8, compares 22×2, totalOrder ×2, next ×2, remainder,
  scaleB, logB, convertFormat ×2). `round_to_integral_exact` takes only
  the four dynamic modes (SF-0 2.3).
- Named wrong table entries (each with counterexample vector): F-divzero
  (`div_core` zero-divisor row), F-zerozero (`add_terms` zero-zero sign
  row), F-fmainf (`fma_core` inf/inf invalid row). No fourth wrong entry
  found across 29k exact + full level-1 Berkeley + 11k directed.

### (5) Claims

- `tables/implemented.tsv`: base data rows 63 (+header); copy 236
  (+header); new rows base→copy exactly 173, all `msf64_*\t1`, appended
  (0 removed). Copy rows ⊆ main rows (main adds only sibling `msf32_*`).
- `diff --stat 4cdb912`: 18 files. Owned: `src/msf64.c`,
  `tests/gen_vectors_f64.py`, 5 `tests/vectors/*f64*.vec`,
  `tables/implemented.tsv` (+ regenerated outputs). Off-limits diffs
  (10 files) are each byte-identical between copy and parcel branch
  `w1-f64@cb10ee2`: `src/msf_roundpack.c` (lead tininess fix),
  `tests/berkeley_ingest.py` (lead eq fix), `tests/gen_vectors.py`
  (lead Clause 7.5 reference fix), `tools/run.sh` (lead control-9 fix),
  `tests/msf_dispatch.h`, `include/muse_softfloat.h`,
  `docs/COVERAGE.tsv` (generated), `src/msf_formats.h`,
  `tests/vectors/pack{16,32,64}.vec` (lead tininess expectations).
  `dispatch`/`header`/`COVERAGE` differ from main-HEAD only by
  main-ahead f32-parcel content.
- Copy-vs-branch file diff (the mutation surface): `src/msf64.c` (3
  lines: flag drop :202, sign-rule flip :93, inf-rule flip :281),
  `tests/gen_vectors_f64.py` (1 line: F_UNF :27),
  `tests/vectors/arith-f64.vec` (1 line: :5). Everything else owned or
  generated is identical.
- Symbol/type scans: type clean (run.sh output); symbol scan SKIP-BY-NAME
  (no `arm-none-eabi-gcc` on this host) — target gate not run.

## Counts and classes

- (a) regressions: 3 (F-divzero, F-zerozero, F-fmainf).
- (b) wrong answers: 3 (F-genflags, F-vec5, F-regatemsg).
- notes: 6 (N1–N6).
- Berkeley: 3,795,688 cases / 2307 fails / 3840 named skips.
- Committed directed: 11057 / 45 fails. Exact probe: 29028 / 520 fails
  (all 520 in the three (a) classes).
- smoke 29982 PASS; standard +1117504 PASS (both exclude f64 directed).

## Reference self-corrections (my bugs, fixed, kept out of the verdict)

not_greater-on-unordered, inverted NaN totalOrder ranks, long/short
int-mode names, `0xFFE`→`0x7FE` overflow constant, from_int ignoring
rm, NaN-delivery signaling precedence, nextUp(-inf) sign, rint −0,
sqrt-f32 delivery format flag, Exact-inexact on saturation (settled by
committed vector), unbounded-7.5 tininess (settled by roundpack header
comment + pack64 second-shape vectors; implementation corroborated).

## Not done

Level-2 Berkeley takes; board/bench budgets; parcel seeded sweeps as
artifacts (superseded by my 29k independent sweep); target symbol scan
(no toolchain); the other parcel's worktrees/scratch, `scratch/lead`,
anything `cft`, the board (untouched throughout); no commits; nothing
spawned (all runs foreground, PIDs owned).
