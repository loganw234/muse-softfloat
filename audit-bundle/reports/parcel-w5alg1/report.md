READY

# parcel-w5alg1 report: SF-2 Step 2a seam + correctly rounded rSqrt (binary16/32/64)

Branch `wave5-alg1` in `worktrees/w5-alg1`, base `7c3819c`.
Two commits, clean tree at `b886e03`:

- `628a18d` - seam (own commit, builds standalone).
- `b886e038d095bfad643ccb937f44abd03bcaaa7f` - rSqrt kernel + evidence.

Brief `ledger/briefs/w5-alg1.md` obeyed exactly. Governing:
`docs/studies/SF-2.md` Secs. 1, 3, 6-9 and
`scratch/sf2-algebraic/report.md` in full. Design entry was
written to `ledger/parcel-w5alg1.md` BEFORE any code; results
entry appended there after. All runs from script files in
`scratch/parcel-w5alg1/` (Git Bash, `MSF_PYTHON` pinned to the
workspace `.venv`, TMPDIR/TMP/TEMP in `scratch/parcel-w5alg1/tmp`,
explicit `ulimit -v 2097152` ceilings on the long sweeps):
`01_seam.sh`, `02_kernel.sh`, `03_vectors.sh`,
`04_regen_gates.sh`, `05_controls.sh` (+ `make_controls.py`),
`06_differentials.sh`, `07_target.sh`, `08_exact_leg.sh`
(+ `make_f16_exhaustive_exact.py`), `09_final.sh`,
`check_seam.py`. Logs in `scratch/parcel-w5alg1/out/`.
Nothing with `cft` in its name was opened, searched, or
listed. No third-party source was used as design input.
Nothing pushed or merged; no board work or flashing.

## Seam evidence (commit 628a18d)

- `math_bin` signature class in `tools/gen_tables.py`:
  homogeneous binary `f(f,f)->f` with the minmax expansion
  shape under its own token; added to expand(), REPLAYABLE,
  SIGS (dispatch gains `MSF_SIG_MATH_BIN`).
- `tables/operations.tsv`: the study Sec. 7.2 rows verbatim
  (wave 5): `r_sqrt` (math_un) and `hypot` (math_bin), tier 2,
  `C-754`, `mpfr-exact`, `directed-alg;ties;seeded-random`.
- `tools/run.sh` Tier 2 expected total 39 -> 45 with the
  freeze comment restated (`45 registered / 42 implemented`
  is the post-kernel headline; the seam tree itself printed
  45 registered / 39 implemented / 6 planned by name).
- Regeneration stamped all generator outputs that changed
  (`include/muse_softfloat.h`, `tests/msf_dispatch.h`,
  `docs/COVERAGE.tsv`; `src/msf_formats.h` byte-unchanged),
  twice, byte-identical (01_seam.sh).
- Seam negative controls watched: unknown sig token refused
  by expand() ("unknown sig class: bogus_sig"); generator
  and run.sh inventory print Tier 1 = 783 implemented of
  783; standing inventory mutants (tier1-planned-flip,
  tier2-row-deleted) still refused under the new total.
- Seam-tree `tools/run.sh smoke` PASS (171,423 cases, 6
  planned rows named, all standing controls refused).

## Kernel (commit b886e03)

New `src/msf_alg.c`: `rsqrt_core(fmt, bits, rm, flags)` +
`msf{16,32,64}_r_sqrt`. Exact integer decision per study
Sec. 3.1: normalize to M' * 2^E' (E' even, M' < 2^(p+1));
bit-search Q = floor(2^S/sqrt(M')), S = p+9+(p-1)/2
(25/44/88); candidates tested by the exact compare
cand^2*M' vs 2^(2S) as a split over `msf_u128_mul_u64_u64`
(178-bit logical width at binary64, 128-bit storage; WIDTHS
row `r_sqrt` states the realization as required). One
unmodified `msf_pack_generic` call decides all five
rounding attributes from birth; sticky is the compare's
equality test. `msf_roundpack.c`/`msf_wide.c` untouched
(no inadequacy found). Test-only `MSF_ALG_TEST_TRUNC`
macro exists solely for the truncated-width control.

Specials as shipped (study Sec. 5.1; identical all modes):

| input | result | flags |
|---|---|---|
| +0 | +inf | divideByZero |
| -0 | -inf | divideByZero |
| +inf | +0 | none |
| -inf, finite < 0 | default qNaN | invalid |
| qNaN / sNaN | SF-0 2.5 matrix delivery | invalid iff sNaN |
| finite > 0 | correctly rounded kernel value | inexact iff non-square |

The one [2R] cell, `rSqrt(-0) = -inf`, was second-read in
the design entry (clause paired-sign cell; composition
through the shipped `sqrt(-0) = -0` and division pole
cells) - it does NOT flip; it is table-decided in kernel,
`tests/alg_decider.c`, and the generator, never
MPFR-sourced (MPFR gives +inf; the flip-mutant control
below proves the committed lines carry the clause cell).
No other rSqrt cell is [2R]. No unadjudicated disagreement
occurred at any gate (study stop rule never engaged).

## Evidence counts

Committed vectors (all five modes per input), regenerated
twice byte-identically, and the committed tree is clean
after a full post-commit regeneration (09_final.sh):

| file | lines | specials | directed | ties | seeded |
|---|---|---|---|---|---|
| alg-f16.vec | 1,195 | 145 | 545 | 190 | 315 |
| alg-f32.vec | 1,200 | 145 | 715 | 255 | 85 |
| alg-f64.vec | 1,200 | 145 | 740 | 305 | 10 |
| total | 3,595 | 435 | 2,000 | 750 | 410 |

(Per-file tag counts from `out/vec_counts.log`, agreeing
with the smoke provenance inventory. `ties` =
midpoint-adjacent constructions; exact ties are
unattainable for rSqrt. Inputs per format: 239/240/240.)

Decider split: `tests/alg_decider.c` decides finite
positives by the Step 0b MPFR operation recipe
(11/-23/16, 24/-148/128, 53/-1073/1024; readback asserted;
subnormalize skipped on zero/inf/NaN; flags derived from
the ternary, MPFR flags never read; a non-finite-nonzero
intermediate aborts). `tests/gen_vectors_alg.py`
cross-decides every committed input in all five modes with
an exact integer decider (midpoint compares by rational
squaring) and refuses on any disagreement - including the
ta column, which the C decider prints as te (raw MPFR
RNDNA prohibited, unused; equality verified per case).

Gate-only differentials (kernel vs decider, counts
printed in the logs):

- binary16 EXHAUSTIVE: all 65,536 encodings x 5 modes =
  **327,680 checked, 0 mismatches, PASS**
  (`out/f16_exhaustive_final.log`). Second independent
  leg, same 327,680 expectations from exact-Python alone
  through the real runner: PASS
  (`out/f16_exact_verify.log`).
- binary32 seeded: 250,000 + 100,000 finite-positive
  inputs x 5 = 1,750,000 checked, 0 mismatches.
- binary64 seeded: 250,000 + 100,000 finite-positive
  inputs x 5 = 1,750,000 checked, 0 mismatches.

Negative controls watched refused by the real runner
(05_controls.sh; the unmutated files pass 3,595/3,595 in
the same script):

| control | outcome |
|---|---|
| 1-ulp-moved midpoint-adjacent expectation | REFUSED (1 FAIL line) |
| specials: rSqrt(-0) -> +inf (MPFR cell) | REFUSED (1) |
| specials: qNaN payload bit mangled | REFUSED (1) |
| specials: rSqrt(-1) made finite | REFUSED (1) |
| inexact stripped on midpoint-adjacent case | REFUSED (1) |
| directed tp<->tn swap (whole f32 file) | REFUSED (384) |
| truncated stage width (MSF_ALG_TEST_TRUNC) | REFUSED (745 on f64) |

Budgets on the committed tree: `smoke` PASS (175,018
committed cases, type + symbol scans clean, inventory
tier1 783/783, tier2 42 implemented / 3 planned / 45
registered, every standing control refused); `standard`
PASS (+ 1,117,504 generated cases), re-run post-commit in
09_final.sh with the same verdicts.

Target compile (07_target.sh, measurement only):
arm-none-eabi-gcc 14.2.1, `-mcpu=cortex-m0plus -mthumb
-Os -ffreestanding`, clean under -Wall -Wextra -Werror.
`msf_alg.o`: text 1,032 B, data 0, bss 0. Undefined
symbols: `__aeabi_llsl`, `__aeabi_llsr`, `memcpy`, plus
`MSF_FMT_PARAMS`, `msf_pack_generic`,
`msf_u128_{from_u64,mul_u64_u64,to_u64_trunc}` - no
refused helpers. `-fstack-usage` static frames:
`rsqrt_core` 192 B, `alg_cmp_sq` 128 B, wrappers 16 B,
`msf_nan_to_dest` (header inline) 32 B. No performance
claims.

## Not done / escalations / for the lead

- **hypot: registered PLANNED only** (msf16/32/64_hypot
  declared, dispatch NULL, named in every inventory). Its
  kernel, evaluation-order specials, the (inf, sNaN) [2R]
  second read, vectors, and the binary16 second-operand
  sweep are the follow-on A2 parcel per the study split.
  Nothing here implements or claims it.
- **Board build lists (escalated, not owned):**
  `board/CMakeLists.txt` (MSF_SRC) and
  `board/run_board.sh` (host replay source list) do not
  yet name `src/msf_alg.c`; add it where `src/msf_math.c`
  rides before any board budget on the merged tree, or
  firmware links that pull dispatch will miss the rSqrt
  symbols. `tools/run.sh` SRC (host + ARM symbol-scan
  builds) already carries it. Board sampled replay of the
  alg vectors is lead work under the board lock; not run.
- Recorded binary32-exhaustive rSqrt differential against
  a foreign fast decider (study Sec. 6 item 2): NOT run -
  it was priced as an optional one-time run in the study,
  is not in this brief's evidence list, and was not
  needed: binary32 carries 1,750,000 seeded MPFR-decided
  comparisons here.
- Planted-copy verifier parcel: separate work, as in
  every wave so far. Not run.
- `math_int` signature: not built (the pown/compound/
  rootn parcels' seam, deferred with those families per
  SF-2 Sec. 1).
