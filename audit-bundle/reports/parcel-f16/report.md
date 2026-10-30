# parcel-f16 report (wave-2 binary16 parcel)

Verdict: **READY**. Branch `w2-f16`, worktree `worktrees/w2-f16`,
base `dd48b08c7cb2f1aa957d15972d919c6d3051ad78`, head
`44c770c7c57a394685f9a9a9bc3069ccd98af78a` (one commit, never pushed).
Design entry: `ledger/parcel-f16.md` 2026-10-27 07:14:23 -0700
(time box started then; this report ~07:34, far inside the 360-minute
box, so no 300-minute checkpoint was reached). Escalation channel
test: `ledger/urgent/parcel-f16-test.md` (written 07:07:55 via
ledger.sh; lead recorded receipt in `ledger/lead.md` 2026-10-27
07:09:41). The machine was under third-party load throughout; every
wall time below is a record, not a rate claim.

## What landed

All 236 wave=2 `msf16_*` instantiations (count re-measured from
`docs/COVERAGE.tsv` at base; authorities measured berkeley 39,
mpfr-exact **126**, project-exact 35, project-exact+berkeley-check 36
— the brief's "mpfr-exact 130" sums its own split to 240; recorded as
brief-wrong item 1 in the design entry, coverage file followed).

Committed files (12; only brief-owned files plus regenerated output):

| file | note |
|---|---|
| `src/msf16.c` | 866 lines; mirrors `src/msf32.c` kernel shape at f16 dest |
| `tests/gen_vectors_f16.py` | 1,256 lines; self-contained Fraction references |
| `tests/vectors/{arith,fma-sqrt,conv-int,toint,rint-misc,compare}-f16.vec` | 12,765 lines, 936,199 bytes total |
| `tables/implemented.tsv` | append-only at the end, 236 rows, LF, 0 CR bytes |
| `docs/COVERAGE.tsv`, `include/muse_softfloat.h`, `tests/msf_dispatch.h` | regenerated (`tools/gen_tables.py`: 783 instantiations, 645 implemented); `src/msf_formats.h` regenerated unchanged |

Hand-written lines: 866 + 1,256 = 2,122 of the 3,500 ceiling.
Committed vector bytes 936,199 of 1 MB. No off-limits file touched
(`git diff --stat` vs base lists exactly the files above).

Design deviations from the sibling kernel (both in the design entry):
the remainder early-return threshold is `s >= 12` (= p+1 at p=11,
bound proved there) in place of `msf32.c`'s 25; everything else is a
structural mirror (dest f16; source grids widened 2x2→3x3, fma
2x2x2→3x3x3, comparison wrappers 2→3 source pairs). Symbol audit:
all 236 coverage names are defined symbols in `msf16.o`, with no
extra new `msf16_*` symbols (`scratch/parcel-f16/check_symbols.py`).

## Gate results, by provenance

Runner for all replays: `build/smoke/msf_runner.exe` built by
`tools/run.sh smoke` in the worktree (host gcc x86_64-w64-mingw32
16.1.0, FLT_EVAL_METHOD=0). Every set below ends `VERDICT: PASS`
with `failed 0 malformed 0 skipped-planned 0` unless a control is
supposed to fail.

### 1. Berkeley (`berkeley:testfloat_gen-*`, pinned testfloat_gen via `tests/berkeley_ingest.py` into `build/w2/`)

Driver: `scratch/parcel-f16/berkeley_driver.py`;
log: `scratch/parcel-f16/berkeley-results.log`; consoles:
`berkeley-l1-console.log`, `berkeley-big-console.log`.
Comparison masks are the ingest's stated ones (`nan-class` for
arithmetic payloads, `berkeley-int` for invalid integer deliveries,
`exact` for comparisons) — printed per file by the runner.

Brief batch: **102 jobs, 41,992,248 cases, 0 fails**
(L1: 92 jobs, 31,951,128 cases, wall 144.1s; L2: 10 jobs,
10,041,120 cases, wall 43.5s; both under load).

| Berkeley fn | level | cases (per-mode detail in the results log) | outcome |
|---|---|---|---|
| f16_add/sub/mul/div | 1, te tz tp tn ta | 232,320 each fn (46,464/mode) | PASS |
| f16_sqrt, f16_roundToInt | 1, 5 modes | 2,040 each (408/mode) | PASS |
| f32_to_f16 / f64_to_f16 | 1, 5 modes | 3,000 (600/mode) / 3,840 (768/mode) | PASS |
| f16_to_i32/i64/ui32/ui64 | 1, 5 named modes | 2,040 each (408/mode) | PASS |
| i32/ui32_to_f16 | 1, 5 modes | 1,860 each (372/mode) | PASS |
| i64/ui64_to_f16 | 1, 5 modes | 3,780 each (756/mode) | PASS |
| f16_mulAdd | 1 complete, 5 modes | 30,666,240 (6,133,248/mode) | PASS |
| f16_rem | 1 | 46,464 | PASS |
| f16_eq, eq_signaling, le, lt, le_quiet, lt_quiet | 1 | 46,464 each (278,784) | PASS |
| f16_add/sub/mul/div | 2 `--take 2000000` te+tz | stream ends first: 1,254,528 per slice, run complete (2,509,056 each fn) | PASS |
| f16_sqrt | 2 `--take 2000000` te+tz | stream ends at 2,448 per slice, complete (4,896) | PASS |

Bonus beyond the brief (`scratch/parcel-f16/bonus-berkeley.log`,
script `bonus_berkeley.sh`): f16_rem, f16_eq, f16_le_quiet,
f16_lt_quiet at level 2 `--take 2000000`, each complete at
1,254,528 cases — **5,018,112 more cases, all PASS**.

Berkeley total replayed: **47,010,360 cases, 0 fails, 106 jobs**.

Authority coverage within this: of the 39 berkeley-authority rows,
38 were Berkeley-run (above). One named skip:
`msf16_from_f16` — probe measured `testfloat_gen: Invalid argument
'f16_to_f16'`, ingest wrote 0 cases, rc=1
(`scratch/parcel-f16/f16_to_f16-probe.log`); the row is gated on the
exhaustive exact sweep below (65,536 encodings × 4 attributes).
Of the 36 project-exact+berkeley-check comparison rows, Berkeley
generators exist only for the homogeneous spellings that map to
quiet_equal, signaling_equal, quiet_less, quiet_less_equal,
signaling_less, signaling_less_equal at (f16,f16) — those 6 were run
at L1, quiet_less{,_equal} and quiet_equal also at L2. The remaining
30 rows (other predicates and all (f16,f32)/(f16,f64) pairs) have no
Berkeley generator; they are gated on the project-exact sets, with
the shared predicate logic cross-checked by the 6 above. Berkeley
`eq` is ingested as the quiet equality at base (Wave 1 ruling);
`eq_signaling` ran as its own job and passed.

### 2. Project-exact (`exact-py-f16:*` from `tests/gen_vectors_f16.py`)

References are Fraction computations from the decoded integers
(independent shape from the C kernels; remainder/rint references
assert exactness case by case at generation).

Committed directed (replayed from `tests/vectors/` after generation;
log `scratch/parcel-f16/directed-final-verify.log`):

| file / provenance | lines |
|---|---|
| arith-f16.vec (`dir-arith`) | 4,320 |
| fma-sqrt-f16.vec (`dir-fma-sqrt`) | 1,674 |
| conv-int-f16.vec (`dir-conv-int`) | 1,144 |
| toint-f16.vec (`dir-toint`) | 1,840 |
| rint-misc-f16.vec (`dir-rint-misc`) | 985 |
| compare-f16.vec (`dir-compare`) | 2,802 |
| total | **12,765 PASS / 0 fail** |

Name coverage: 236 of 236 present, min 23 cases per name, no foreign
names (`check_coverage.py`). Regeneration into scratch first was
byte-identical to the committed copies.

Exhaustive 65,536-encoding sweeps into `build/w2/` (gen log
`exhaustive-gen2.log`; verify logs `exhaustive-verify.log`,
`totalorder-verify.log`):

| file | lines | contents |
|---|---|---|
| ex-rint-next-logb-f16.vec | 1,048,576 | 16 cases per encoding: 5 named roundToIntegral + Exact at 4 attributes + nextUp/Down + logB + from_f16 at 4 attributes |
| ex-sqrt-f16.vec | 262,144 | sqrt at 4 attributes |
| ex-toint-f16.vec | 5,242,880 | all 80 to-int forms per encoding |
| ex-totalorder-f16.vec | 197,116 | ranked-chain adjacent pairs over all encodings, both directions, totalOrder + totalOrderMag, + self-pairs |
| total | **6,750,716 PASS / 0 fail** | |

Seeded sweeps into `build/w2/` (`sweeps-verify.log`):
`sweep-f16-20261027.vec` 200,000 and `sweep-f16-777.vec` 100,000
(cross-format add/sub/mul/div/sqrt/fma/convert templates over the
full {f16,f32,f64} grid) and `sweep-misc-f16-424242.vec` 112,500
lines from 100,000 draws (remainder, scaleB, comparisons, to/from-int,
rint, next, logB, totalOrder) — **412,500 PASS / 0 fail**.

Project-exact total replayed: **7,175,981 cases**.
The mpfr-exact authority token is discharged by these exact rational
references ("MPFR / exact-integer generation decides" per
`tools/gen_tables.py`), the same reading the Wave 1 parcels gated
under; the MPFR binary itself was not invoked.

### 3. `tools/run.sh` budgets (regression; logs `smoke1.log`, `standard1.log`, `smoke-final.log`)

- `smoke` PASS 14s pre-commit and 13s post-commit: drift clean
  (4 generated files byte-identical), unit PASS, 52,168 committed
  vectors PASS, type scan clean, symbol scan clean (22 undefined
  symbols, integer helpers only), 9/9 permanent negative controls
  refused (control 9 names `msf16_from_decimal`).
- `standard` PASS 37s: smoke plus 917,504 exhaustive-binary16
  (P0 encodings set) and 200,000 pack64 sweep, all PASS.
- The fixed smoke `VECS` list does not name the six new directed
  files (`tools/run.sh` is off-limits to this parcel — the Wave 1
  lesson): they were replayed explicitly with the same runner
  binary (Section 2) for the lead to wire at merge.
- `board` budget: not run (lead-only per AGENTS.md) — skip by name.

### 4. Parcel negative controls (`scratch/parcel-f16/controls.py`, log `controls.log`)

All required refusals observed (script exits 0):

1. Flipped result bit in a kept Berkeley file
   (`build/w2/f16_div-te-l1.vec`, `7c00`→`7c01`, compare=nan-class):
   `total 1 passed 0 failed 1`, `VERDICT: FAIL`, rc=1.
2. Flipped flag bit (inexact, `14`→`04`, same line): refused the
   same way.
3. Generator-math mutation: a scratch copy of
   `tests/gen_vectors_f16.py` with exactly one line changed —
   ties-to-even parity `q % 2 == 1` → `q % 2 == 0` in
   `_round_inc_mag` — regenerated the directed sets into scratch;
   replay of its arith file FAILS with exactly 3 result-bit
   disagreements (the three tie-at-2049 add cases across source
   formats), while the unmutated file passes 4,320/4,320. The
   mutated copy was then deleted by the script (the revert); the
   committed generator still contains the original line exactly
   once (asserted in the log).
4. Extra: the `-DMSF_TININESS_AFTER_ROUNDING=0` build is refused on
   the directed arith set (4 cases, flags `18` vs `10`, result bits
   equal — the Clause 7.5 boundary is load-bearing at f16 too).

## Skips by name (nothing skipped silently)

- Berkeley `f16_to_f16` ingest — generator refuses the function
  name (measured); `msf16_from_f16` gated exhaustively instead.
- Berkeley checks for 30 of the 36 berkeley-check comparison rows —
  no generator exists for those predicates/pairs (Berkeley
  comparisons are homogeneous); project-exact coverage stands.
- `tools/run.sh board` — lead-only.
- Berkeley beyond the brief: other seeds, mulAdd level 2, level-2
  slices for roundToInt/conversions were not run (roundToInt and
  conversions are exhaustive-cheap at f16 and were covered at
  65,536 by the exact sweeps where unary).
- Host-FPU oracle cross-checks — not used (outside the brief).

## Process notes for a regater

- Regenerate everything with `.venv/Scripts/python.exe`:
  `tools/gen_tables.py`; `tests/gen_vectors_f16.py directed
  tests/vectors` (byte-identical, 936,199 bytes);
  `exhaustive build/w2` (~22s, writes ~640 MB across all build/w2
  artifacts incl. kept Berkeley L1 files — transient, delete to
  reclaim); `sweep … 200000 20261027`, `sweep … 100000 777`,
  `sweep-misc … 100000 424242`.
- Berkeley rerun: `scratch/parcel-f16/berkeley_driver.py` (L1) then
  with `--no-l1 --with-big --append` (L2); needs
  `build/smoke/msf_runner.exe` from a smoke run and sets
  `MSF_TESTFLOAT_GEN` itself. Kept L1 files are in `build/w2/`.
- All scratch scripts/logs live in `scratch/parcel-f16/`; this
  report's numbers are reproducible from `inventory.py`
  (`inventory.txt`), `berkeley-results.log`, and the per-set verify
  logs named above.
- The urgent watcher (Monitor, PowerShell loop) was armed at start
  but delivered no wake lines to this agent during the run; the
  urgent directory was checked manually at the pre-report read
  (parcel-xf's objection and the lead's 07:09 ruling were seen
  there; neither touches dest-f16). Recorded so the lead knows the
  wake path was not the evidence.
