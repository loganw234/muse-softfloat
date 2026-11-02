# verifier-w2xf report - Wave 2 cross-format parcel (copy `worktrees/verify2-xf`)

Verdict: **NOT READY**. Three wrong-answer defects in the copy's new
wrappers (two wrong-format decodes, one wrong signaling flag), one
wrong committed expectation, and four directed files that do not
regenerate byte-identically. Everything else verified clean across
three independent oracles. Verifier work only: nothing fixed, nothing
committed, no file in the copy modified.

Copy: `worktrees/verify2-xf`, detached HEAD `5f41c0c`, parent (base)
`dd48b08`. Machine under third-party load throughout; wall times are
records, not rates. Scratch: `scratch/verifier-w2xf/` (scripts
`00`-style `scripts/`, TMPDIR/TMP/TEMP into `scratch/verifier-w2xf/tmp`).

## Findings (one claim per line; class a/b send work back)

- (b) `msf32_add_f16_f64` decodes its binary64 operand as binary32:
  `src/msf32.c` `DEF_ADD(msf32_add_f16_f64, msf16_t, FMT16, msf64_t, FMT32)`
  (second format index must be FMT64). Smallest repro
  `msf32_add_f16_f64 te 0 3ff0000000000000 -> 3f800000` (got 00000000;
  committed `arith-xf.vec:302`). 105 directed + 3 trap failures.
- (b) `msf32_fma_f16_f32_f64` decodes its binary64 addend as binary32:
  `src/msf32.c`
  `DEF_FMA(msf32_fma_f16_f32_f64, msf16_t, FMT16, msf32_t, FMT32, msf64_t, FMT32)`
  (third format index must be FMT64). Smallest repro
  `msf32_fma_f16_f32_f64 te 3c00 3f800000 bff0000000000000 -> 0` (got
  3f800000; committed `fma-sqrt-xf.vec:282`). 31 directed + 3 trap failures.
- (b) `msf64_compare_signaling_less_f16` never signals invalid on quiet
  NaN: `src/msf64.c` `DEF_CMP_F16(signaling_less, PRED_LT, 0)` (SIG must
  be 1; every other signaling row, and the landed
  `DEF_CMP(signaling_less, PRED_LT, 1)`, use 1). Smallest repro (quiet
  NaN first operand)
  `msf64_compare_signaling_less_f16 - 7ff8000000000000 3c00 -> 0 01`
  (got 00; committed `compare-xf.vec:1726`). 6 directed + 2,506
  differential failures, all with a quiet NaN operand.
- (a) `tests/vectors/arith-xf.vec:6` committed expectation is
  arithmetically wrong:
  `msf32_add_f16_f16 te 0 3c00 -> 3f800001` (0 + 1.0 is exactly 1.0 =
  0x3f800000). Implementation, fresh regeneration, and the independent
  reference below all agree on 0x3f800000. The line also fails replay.
- (a) Four directed files do not regenerate byte-identically from the
  copy's own generator (project norm: finding even when both sides are
  arithmetically correct): `arith-xf.vec` 1 line (the finding above),
  `fma-sqrt-xf.vec` 46 lines, `conv-xf.vec` 8 lines, `compare-xf.vec`
  44 lines; `traps-xf.vec` regenerates identically. 98 of the 99 lines
  differ only in one operand, committed `0xff45` vs regenerated
  `0xff44` (generator constant `0x12344` in `POOLS["f16"][25]` vs the
  `0x12345`-derived value the committed files were built with); both
  sides are arithmetically self-consistent there. The parcel's
  "regenerates byte-identically" claim is false in this copy.
- (a) Claim surface: the parcel's READY / "11,066 passed" does not hold
  for this copy: independent replay of the five committed xf sets is
  10,920 passed / 146 failed (`arith-xf.vec` 103, `fma-sqrt-xf.vec` 31,
  `compare-xf.vec` 6, `traps-xf.vec` 6). The smoke/standard and
  landed-bit-identity claims below re-verified true.

## Probes (counts; skips by name)

1. Budgets in the copy: `tools/run.sh smoke` PASS in 12 s
   (`scratch/verifier-w2xf/smoke.log|.txt`): drift check 4/4
   byte-identical; units pass; committed Wave 1 vectors **52,168 passed
   / 0 failed** (16 provenance tags); type scan clean; symbol scan
   clean; 9/9 permanent negative controls refused incl. planned-only.
   `tools/run.sh standard` PASS in 37 s: smoke contents plus
   **1,117,504 passed / 0 failed** in the standard leg. Board not run
   (lead-only).
2. Claim surface vs base (`git diff dd48b08`): 12 files changed, all
   parcel-owned or regenerated outputs (`src/msf32.c` +83/-0,
   `src/msf64.c` +77/-1 where the 1 deletion is a comment-line reword,
   `tables/implemented.tsv` +126/-0 pure LF append at end,
   `tests/gen_vectors_xf.py` new, five `tests/vectors/*xf*.vec` new,
   regenerated `include/muse_softfloat.h`, `tests/msf_dispatch.h`,
   `docs/COVERAGE.tsv`; `src/msf_formats.h` byte-identical). No
   off-limits file touched (no `src/msf16.c`, shared kernels, `tools/`,
   `tests/runner.c`, existing generators, `board/`, `compat/`, or
   `docs/` beyond COVERAGE.tsv). No landed wrapper or kernel body
   changed; landed bit-identity rests on the smoke/standard replays.
3. Independent replay (copy runner over the five committed xf files):
   11,066 total, 10,920 passed, 146 failed, VERDICT: FAIL
   (`scratch/verifier-w2xf/replay-xf.log`). Regeneration of each from
   its generator into `scratch/verifier-w2xf/regen/xf`, byte-compared:
   `traps-xf.vec` IDENTICAL; `arith-xf.vec` differs line 6,
   `fma-sqrt-xf.vec` 46 lines, `conv-xf.vec` 8 lines,
   `compare-xf.vec` 44 lines (detail above).
4. Berkeley-decided rows (2: `msf32_from_f16`, `msf64_from_f16`,
   authority `berkeley`): `tests/berkeley_ingest.py` rerun from the
   pinned `scratch/oracles` build into `scratch/verifier-w2xf/berkeley/`,
   level 1 complete, every attribute mode (te/tz/tp/tn), 8 jobs x 408
   cases = **3,264 passed / 0 failed** (`07_berkeley.sh`,
   `berkeley-run.txt`). The 24 `project-exact+berkeley-check`
   comparison rows: own exact differential (`08_diff.py`) — pinned
   `testfloat_gen` f16 eq/eq_signaling/le/lt/le_quiet/lt_quiet level-1
   seed-1 streams (46,464 cases each), first operand widened exactly in
   own code (value-asserted per case), greater rows read swapped,
   notEqual complemented; every derived expectation (1,115,136)
   cross-checked against the independent exact reference:
   transform==exact **1,115,136/1,115,136**. Copy verify of the emitted
   vectors: dest f32 **557,568/557,568 PASS**; dest f64 555,062/557,568
   (2,506 failures, all `msf64_compare_signaling_less_f16` with a quiet
   NaN operand — finding 3, with NaN repros as required). No predicate
   besides signaling_less shows wrong invalid behavior.
5. Independent exact reference (fresh code, `03_indref.py`, no generator
   imports; decode-exact/Fraction/pack-once; NaN matrix calibrated to
   sNaN-truncate 0x7fc00000 vs qNaN-truncate sign-preserved 0xffc00000):
   calibration over all 11,066 committed lines: **11,065/11,066 agree**
   (the 1 mismatch is finding 4). Seeded sweeps per dest across all 126
   names (seeds 101/202 f32, 303/404 f64; 40 cases/name/seed; edge-heavy
   pools incl. f64 danger significands, f32 ties, NaN payloads at the
   truncation threshold, subnormals, signed zeros, infinities):
   **10,080 vectors, 9,976 passed / 104 failed**, failures only in the
   three finding-1/2/3 instantiations (46 + 45 + 13); exposing-operand
   coverage 10,061/10,080 cases carry an operand whose exact value
   differs under a wrong format index. Double-rounding discriminators
   independently constructed (convert-first to f32, unfused fma,
   evaluate-at-f32-then-widen): all **114/114 committed trap lines
   discriminate** (committed expectation differs from the wrong-pipeline
   answer; counts per family/dest match the parcel table). Mutant proof:
   13 trap expectations flipped to the wrong-pipeline answer (one per
   family/dest on correct rows) are all FAILed by the runner
   (`mutants.vec`: 0 passed / 13 failed). Lead dest-f64 trap-shape
   ruling corroborated: convert-to-f64-first vs exact over 4,500
   edge-heavy dest-f64 cases shows 0 numeric/flag differences (see
   note).
6. Wrapper-table audit (`04_audit.py`): every DEF/wrapper line's format
   indices read-checked against the instantiation name — **126/126
   names covered, 123 lines OK, exactly the 3 problems of findings 1-3**
   (all other 123 instantiations correct, corroborated by the sweep
   failures clustering exactly on those 3). All 126 coverage names are
   present in `tables/implemented.tsv` and wired in the dispatch table.

## Notes (not findings)

- Lead-ruling refinement: convert-to-f64-first differs from
  exact-then-round in 22/4,500 sampled cases, all NaN-payload selection
  (first-sNaN vs first-qNaN priority inversion, e.g. add of f64 sNaN
  after an f16 qNaN; flags identical). Zero value/flag differences.
  Trap inputs are finite-only by construction, so trap discrimination
  is unaffected; the ruling's numeric substance holds exactly.
- The copy's HEAD (`5f41c0c`) is a single squashed commit, not the
  parcel's two reported commits; content-equivalent except the defects
  above are present here. Judged as delivered work per the brief.
- Independent-reference self-checks: two of my own bugs (tp/tn swap,
  sNaN-vs-qNaN narrowing rule) were caught by calibration against the
  committed vectors and fixed before any sweep ran; final calibration
  agreement 11,065/11,066.

## Not done

- Board budget (lead-only, per brief skips).
- Berkeley level 2 (brief gates the berkeley rows at level 1).
- Direct Berkeley generators for the 80 mpfr-exact + 20 project-exact
  rows (none exist; those rows rest on the exact references + sweeps +
  neighbor reasoning above, not on Berkeley).
- Host-FPU oracle cross-checks (not used).
- Parcel-scale reseed sweeps / exhaustive binary16 unary (replaced by
  the independent 10,080-vector sweeps, 1,115,136-vector differential,
  and 3,264-vector Berkeley rerun above).
- Standard-scope exhaustive/pack64 legs beyond the budget's own run:
  covered by the standard PASS itself.
