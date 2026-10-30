READY
# parcel-w5demo report: reproducible workload demo (demo/)

Branch `wave5-demo` in `worktrees/w5-demo`, base `26e86ce`, tip
`3feebb9` (3 commits: `094538a` fetch/regeneration, `3d3bfc0`
host proofs + expected hashes, `3feebb9` runner + docs). Not
pushed, not merged. Ledger: `ledger/parcel-w5demo.md` (design
entry before code + results entry). No board flashing; board
stage verified on syntax + dry-refusal paths only. Machine load
kept light throughout (sequential builds; slowest stage ~9 s).

## Fresh-clone gate (the parcel's own gate) - PASS

`git archive` of tip `3feebb976d4df2b4da972fa2810d4e25c0ba13d6`
unpacked to `scratch/parcel-w5demo/fresh/clone` (empty cache, no
.git), logs in `scratch/parcel-w5demo/fresh/`:

- `bash demo/run_demo.sh host --offline` on the empty cache:
  exit 1 before any network use, naming the missing pinned
  archive; interval (repo-native) still ran and passed, summary
  honestly FAIL.
- `bash demo/run_demo.sh host` with network: exit 0 in 52 s.
  Real downloads (REBOUND 6,112,479 B, KissFFT 52,477 B),
  archive + licence sha256 verified, then:

```
  IAS15      PASS
  KissFFT    PASS
  interval   PASS
demo host: PASS
```

  IAS15 lines behind the verdict: native and soft both
  `steps_compared=2001 matched=2001 first_divergence=None`,
  soft with `# SHIMOPS total=26083624 traps=0` (interposition
  counted, not vacuous). KissFFT: 12/12 KF rows identical,
  anchors PASS. Interval: rows=710, IW1 identical.
- `bash demo/run_demo.sh board --offline` in the same tree:
  host stages green, board stage REFUSED naming all missing
  items (ledger layout, forced-absent PICO_SDK_PATH, pyserial),
  exit 1; no `board.lock` existed before or after, nothing
  flashed. (SDK/picotool env were additionally pointed at
  nonexistent paths as a belt-and-braces no-flash guarantee;
  the ledger refusal alone also fires - see log.)
- Tracked-cache refusals, in a disposable clone: a force-tracked
  file under `demo/cache` and a removed `.gitignore` entry each
  make `demo/fetch.sh` refuse with the exact reason; clean
  checkout proceeds to the archive check.
- `git status` of the branch: clean; `git ls-files demo/cache`
  empty - zero third-party source tracked. `tools/run.sh smoke`
  PASS in 34 s in the worktree (no src/tests/board changes).

## What was built

- `demo/fetch.sh` + `demo/fetch.py`: only the REBOUND/KissFFT
  rows of `docs/metrics/fetches.jsonl`; download to
  `demo/cache/archives` (temp name, moved only after hashes
  pass); archive sha256 then licence sha256 (`LICENSE`,
  `LICENSES/BSD-3-Clause` - confirmed to be the recorded
  licence files) verified before extraction; `--offline` never
  downloads. Refuses when the cache would be tracked (in a
  work tree); outside one it says the check was skipped.
- `demo/make_ias15_extract.py`: the board file set
  (integrator_ias15_min.c 663 lines, gravity_basic_min.c 153,
  sim_min.c, ias15x.c, reb_min.h) by anchored transforms over
  the fetched 5.2.2 tree; tables parsed from committed
  `board/ias15_tables.h`. Diff vs the silicon-proven scratch
  extract: provenance comments only, every code byte identical
  (`scratch/parcel-w5demo/extract-diff.txt`). Demo-extract
  sha256 (for future board-run provenance): integrator
  `c6e8b090...7d61e3`, gravity `b988e305...3394a`, reb_min.h
  `996fb9c1...75d4e`, sim_min.c `b3966dcf...93405`, ias15x.c
  `4e6a2b49...a2197`.
- `demo/make_kissfft_tree.py`: 3-site Fork B patch, hard hash
  gate. **Brief correction, with evidence:** the brief's
  patched prefixes (`cf9d011f...`, `1e03a1c7...`) appear
  nowhere in RECORD/ledger. The board-run log
  (`muse-softfloat/build/kissfft-board/tree-inputs.sha256`)
  records kiss_fft.c `8fcc496897ce...62305`, kiss_fftr.c
  `b34ff3b21594...744f`, _kiss_fft_guts.h `42fd7132fdb1...9402`
  - identical to the live scratch tree hashed this session.
  Those are pinned; regeneration from the archive reproduces
  them exactly.
- Host proofs (ours, SPDX MIT): `ias15_host_main.c` (firmware
  path incl. TABLES bit check; native strict `-O3` flags and
  soft `-msoft-float -mno-sse2`, `-ffp-contract=off`
  everywhere), `ias15_host_shim.c` (libcalls over the core,
  loud traps, op counter), `kissfft_host_main.c` (12 configs +
  anchors), `kissfft_host_shim.c` (host stand-in so
  `compat/msf_aeabi.c` wraps sinpi/cospi/floor unchanged),
  `compare_ias15.py` (also the board stage's IAS15_COMPARE;
  requires candidate nonfinite_hashed_fields=0).
- Expected data with provenance headers: `expected-ias15.txt`
  (full 2,001 records, 371,896 B; chosen over a prefix for
  step-level divergence naming; source file sha256
  `9bedb078...93ab3` verified at generation), `expected-kissfft.txt`
  (12 KF rows; ledger and recorded host output cross-checked
  equal; doubles as KISSFFT_EXPECT), `expected-interval.txt`
  (rows=710 + full IW1 `ce81d66e9b0b...a9aec` from the parcel
  ledger, ends matching BOARD.md's truncated form).
- `demo/run_demo.sh host|board [--offline]`: prerequisites
  named exactly (incl. FLT_EVAL_METHOD and soft-flag probes;
  compiler bin dir prepended after measuring the MSYS2 cc1
  silent-exit trap); board mode = host green required, then
  full preflight before any board script (never half-flash),
  env wired to the cache, interval leg skipped with reason
  outside the main-checkout layout its script requires.
- `demo/README.md`, one README line, BOARD.md pointer section,
  `.gitignore` cache entry, briefs.jsonl row.

## Ours vs fetched

Ours, tracked (18 files per `git diff --stat 26e86ce..HEAD`):
all of `demo/` listed above plus `.gitignore`, `README.md` (1
line), `docs/BOARD.md` (pointer), `docs/metrics/briefs.jsonl`
(1 row). Fetched/generated, never tracked (all under
`demo/cache/`): 2 archives, pristine REBOUND/KissFFT trees,
the GPL IAS15 extract, the patched KissFFT tree, build output.

## Not done (by design or by brief)

- Board flashing / silicon run: lead work per brief. The board
  stage is wired and refusal-tested; its first real run will
  also be the first test of the demo extract's firmware build
  (code-byte-identical to the proven scratch extract, so build
  inputs differ only in comments and provenance hashes).
- MPFR twiddle-provenance gate: not part of the demo (remains
  scratch evidence). The demo proves KF hash identity against
  the recorded values, which transitively covers the twiddles
  the proof exercised, but does not re-derive twiddle
  correctness.
- Non-x86-64 hosts: the IAS15 identity claim is scoped to the
  project's pinned x86-64 soft-interposition path; the runner
  refuses other compilers by name instead of approximating.
- Float KissFFT configuration: not attempted (as before).
