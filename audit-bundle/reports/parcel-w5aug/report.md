READY
P1=R2 (exact tiny residual raises NO flag), P4=fixed, P5=internal RTTZ mode 5. Branch wave5-aug (worktrees/w5-aug), base bce49e0, 3 commits: 2c89edd seam, 0ecdd11 kernel, 3741453 evidence. Tier2 66/66, 849 instantiations. Flag table as shipped = ledger/parcel-w5aug.md entry-gate table (implemented in src/msf_aug.c from exact-residual tests).

## Done this run (stage checkpoints)

- [x] Brief ledger/briefs/w5-aug.md read in full.
- [x] Governing reads: docs/studies/SF-2.md Secs 1,5,6-9;
  scratch/sf2-augmented/report.md Secs 0-2, 5 (and 6 pins).
- [x] Worktree verified: worktrees/w5-aug on branch wave5-aug,
  HEAD bce49e0, clean status, before any edits.
- [x] Independent Sec 1.3 second read against S1 extracts
  (p069 9.5-add/sub, p070 9.5-mul, combined.txt 7.1 L2298-2365,
  7.4-7.6 L2420-2460). R2 ratified from three anchors: 9.5 says
  "signaled" not "flag raised"; mul-inexact paragraph adds
  explicit "raises the underflow flag" only there; 7.5 exact
  branch + "only case in this standard" universality. Exact
  cell: residual nonzero strictly between +-b^emin, representable
  (flags raised: none under default handling).
- [x] P5 verified in tree: src/msf_internal.h modes 0..4 taken,
  no round-to-odd value; 5 free; round_inc shape pinned.
- [x] Design entry written: ledger/parcel-w5aug.md.

## Continuation checkpoints (2026-10-29, parcel-w5aug cont.)

- [x] Seam slice implemented (own first commit): aug_pair sig
  in tools/gen_tables.py (+ rounding=fixed validation, reserved
  to aug_pair), three table rows x3 formats (66 Tier 2
  registered / 57 implemented / 9 planned; 849 instantiations),
  pair structs + msf64_pair_t hidden-pointer ABI + pair-inexact
  note in generated header prelude, two-result runner lines +
  msf_pair_* trampolines (dispatch pair_call field), board
  harness two-result reply `R <head> <tail> <flags>` +
  host_replay pair check, run.sh TIER2 count 66, regen twice
  byte-stable (logs/regen*.{log,sha}), smoke PASS 24s with the
  9 rows named planned (logs/seam-smoke.log).

- [x] Kernel: src/msf_aug.c (exact 127-span window +
  verbatim branch, mul 2p split, flags from exact-residual
  tests; six MSF_AUG_TEST_* mutants built in), internal RTTZ
  mode 5 (src/msf_internal.h + src/msf_roundpack.c round_inc
  and overflow-to-inf), WIDTHS augmented rows with proof
  (window/verbatim gap lemma incl. binade-crossing step,
  representability, residual extraction bounds), 9 rows
  implemented (66/66, 849/849), src wiring in run.sh,
  board/CMakeLists.txt, board/run_board.sh. Regen twice
  byte-stable.
- [x] Vectors first pass: tests/gen_vectors_aug.py
  (Fraction reference + independent neighbour checker,
  refuses on disagreement) -> aug-f16 46,088 / aug-f32
  46,146 / aug-f64 46,146 lines. Smoke PASS (411,213 total,
  logs/kernel-smoke2.log). Standard PASS 63s including the
  new standing pool leg: aug_exhaustive pool 5,505,024
  cases, 0 mismatches vs the independent C binary16
  reference (logs/kernel-standard1.log).

- [x] Mutants watched refusing (logs/mutants/summary2.txt;
  control PASS 138,380): te-head 5,478 fails, zero-tail-sign
  30,727, swap-pair 105,583, jam-window 30,458, p1-opposite
  14,558 (flags byte /08 vs /00 on P1 cells - the R2
  discriminant), pack-leak 39,626; corrupted pair tail
  expectation refused (1 fail).
- [x] Generator regen twice byte-stable and byte-identical
  to committed vectors (cmp in logs via evidence_misc.sh,
  exit 0; logs/vec.sha). ARM target-compile of all core TUs
  clean at -Os AND -O3 (Arm GNU 14.2.1, logs/arm*.log).
  Board firmware build-only (no flash): harness links with
  pair reply (uf2 sha bb39c13b..., logs/board-*). Host
  replay pair logic exercised with a fake serial board:
  clean PASS + corrupted-tail refused, pair hash captured
  (logs/host-replay.log). On-silicon replay remains lead
  work under the board lock, as briefed.

## Final evidence (2026-10-29 continuation)

- Exhaustive binary16 pairs (one-time, 256 shards/op, ulimit -v 262144 KB, BelowNormal, counts printed in logs/exh-summary-{add,sub,mul}.txt): add 4,294,967,296 PASS 0 mismatches (751s); sub 4,294,967,296 PASS 0 (758s); mul 4,294,967,296 PASS 0 (704s, incl. mul-inexact-tail 1,258,291,200; tiny-exact/P1 cells add/sub 754,232,664 each, mul 487,736,456). Kind sums check to 2^32 each.
- Fresh final gates this run: smoke PASS 24s (logs/final-smoke.log), standard PASS 54s incl. standing pool 5,505,024 0 mismatches (logs/final-standard.log). Study-reference crosscheck: 20,640 cases 0 disagreements (logs/crosscheck.log).
- Earlier this parcel (logs retained): regen twice byte-stable; vectors aug-f16 46,088 / f32 46,146 / f64 46,146 directed+seeded (RTTZ ties, overflow tie+above, verbatim, zero signs, P1 cells, mul below-step, NaN/inf x2); six mutants refused (te-head 5478, zero-tail-sign 30727, swap-pair 105583, jam-window 30458, p1-opposite 14558, pack-leak 39626 fails; control PASS 138380); ARM -Os and -O3 clean; board build-only links, host-replay fake-serial pair PASS + corrupt refused.

## Not done

- On-silicon board replay: lead work (no flashing per brief).
- Interval workload integration: not this parcel; op-count benefit remains the study's measured model, not a shipped claim.
