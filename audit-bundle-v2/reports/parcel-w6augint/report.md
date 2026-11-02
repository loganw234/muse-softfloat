READY

# parcel-w6augint report (Wave 6 queue item 1: augmented stage 3)

Base `50aac59f6035d56c37340ff07c59252cfd22d5d4`, branch
`wave6-augint`, worktree `worktrees/w6-augint`. Design entry
(pre-code) and close entry: `ledger/parcel-w6augint.md`.
Board is lead-only: nothing flashed, no board script run.

## What changed (3 files, +54/-26)

- `board/interval_workload.c`: stage-3 primitives are now the
  public Clause 9.5 calls. `aug_sum` wraps
  `msf64_augmented_add`, `aug_prod` wraps
  `msf64_augmented_mul` (counted wrappers `augadd64`/`augmul64`,
  one counted op per call), replacing the 6-op Knuth TwoSum and
  the 3-op FMA TwoProduct (`f64fma` removed; `msf64_fma` is no
  longer referenced by this file). VecSum/distill/assembly/
  sign-of-terms, capacities, and the containment contract are
  untouched. A non-finite pair member poisons the guard word
  with INVALID (bit test, no library call), because an exact
  infinity or quiet NaN from a 9.5 call raises no flag where the
  old internals raised invalid.
- Guard re-derived for augmented semantics: trips on
  overflow|underflow|invalid|inexact. Every write to the
  stage-3 flags word now comes from an augmented call (or the
  poison), where inexact means exactly "the pair is inexact"
  (overflowed head, or mul residual below the subnormal step);
  an exact tiny residual raises nothing (P1 = R2) and enters
  the expansion as an exact term. Guard quiet iff every pair
  consumed was exact and finite. `IW_STAGE3_GUARD` hook kept.
- `board/interval_workload.h`: stage-3 doc comment updated to
  match. No signature, hash-layout, or capacity change;
  `interval_main.c`/`interval_host.c` untouched.
- `docs/metrics/briefs.jsonl`: own row appended in binary
  (wave6, base above); prior rows byte-preserved (asserted).

## Acceptance, measured

Scripts in `scratch/parcel-w6augint/` (`build-run.sh`,
`compare_streams.py`, `make_dump.py`, `dump_main.c`,
`check_expansions.py`, `dump-run.sh`, `mutants.sh`,
`extra_probes.py`, `standard.sh`, `arm-check.sh`), Git Bash,
`MSF_PYTHON` pinned to the workspace `.venv`. Scratch ceiling:
catalogue streams + a 147 KB term dump; nothing GB-scale.

Base build first reproduced the recorded stream exactly:
IW1 `ce81d66e9b0b0a4b654c4eb82664417780c6f09c3f866901002b286980ba9aec`,
616,754 total ops (matches the w4interval ledger).

(a) Full-stream diff, base vs new, all 710 catalogue rows:
zero mismatches in every field except `s3ops` (s1/s2/box/torus
ops also identical per row). Stage-3 classifications identical;
sphere UNCERTAIN counts 488/139/4 at s1/s2/s3 in both. New IW1
`ae04caf012294919c432aedd6d80f2a04e6416010291ca83110e4757a66c1422`
-differs from base only because the hash covers s3 ops.

(b) Exact oracle over the actual expansions: a scratch
instrumented copy (20-line diff, saved) dumps distilled A/B/C
lists and the assembled D list per sphere row; a Fraction
oracle from the raw bit patterns checks list sums against
exact a, b, c, disc. Stated subset: all 693 sphere rows,
including the tangent400 family (400 decided rows; also limb
260, adv2k 21, ordinary 8). Result: all four sums exact on
every one of the 689 decided rows; the 4 guard rows
(682-685) have inexact sums and return UNCERTAIN; computed
disc equals the catalogue `exact_extra` Fraction on 693/693
rows; zero failures, zero decided-wrong.

(c) Counted ops, base -> new: stage 3 total 283,314 -> 63,305
(-220,009; 408.8 -> 91.3 per sphere ray); catalogue total
616,754 -> 396,745 (same delta; stages 1-2/box/torus ops
unchanged). Consistent with the SF-2 study's remove-it model
(394,666 / 61,226 with augmentedSubtraction for O-C; the 2,079
difference is exactly 3 counted negates x 693 rays, since this
parcel keeps negate+augmentedAdd). A counted-calls record,
never a performance claim. Measured extra: no decided
catalogue row carries a subnormal expansion term (the study
also measured exact tiny residuals 0 here), so on this
catalogue the realized benefit is the call count and pair-
tracked exactness, not a changed UNCERTAIN rate.

(d) Negative controls rebuilt on the new code, watched
failing: `IW_RM_LO/HI` swapped gives 1,892 field mismatches
and decided-wrong 2 vs catalogue exact (ids 402, 404, s1 HIT
vs MISS); `IW_STAGE3_GUARD=0` decides guard rows 684/685 and
gets 685 wrong (HIT vs exact MISS) - the re-derived guard is
load-bearing under augmented semantics. Stock build:
decided-wrong 0. Extra probe: 4-row non-finite mini catalogue
(+inf/-inf/qNaN/sNaN inputs) is UNCERTAIN at stage 3 in both
base and new builds (poison path exercised).

(e) `tools/run.sh standard` PASS in the worktree (59 s;
411,213 + 1,117,504 vectors, negative controls refused,
inventory 783/783 and 66/66). Also compile-only probe:
`interval_workload.c` builds clean for cortex-m0plus
(-Werror); its undefined-symbol list shows
`msf64_augmented_add`/`msf64_augmented_mul` and no
`msf64_fma`. No board script was run.

(f) No board run (lead-only at merge gate).

## Lead actions at merge (unowned files, not edited here)

- `board/interval_run.sh` host-build line and
  `demo/run_demo.sh` `SRC=` both lack `src/msf_aug.c` and will
  fail to link `interval_host` until it is added (one word
  each). Firmware is fine: `board/CMakeLists.txt` `msf_core`
  already includes `src/msf_aug.c`.
- Record the new host IW1 (`ae04...1422`) and rerun the board
  sample under the board lock; the board replays stage 3 with
  the same ops counts, so host and board hashes move together.
- README/RECORD updates are lead work per the brief.

## Not done

Board run (lead-only). No other gaps against the brief.
