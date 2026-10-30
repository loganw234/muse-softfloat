# Ledger: parcel-w5demo (Wave 5 reproducible workloads demo)

## 2026-10-28 design entry (before code)

Base `26e86ce`, worktree `worktrees/w5-demo`, branch `wave5-demo`
(verified clean at base before writing). Brief:
`ledger/briefs/w5-demo.md`, read first and obeyed exactly. No
board flashing in this parcel; board stage is syntax-check +
dry-refusal only. Nothing with `cft` in its name was opened,
searched, or listed. Machine load kept light: sequential
single-threaded builds, no parallel make.

The gap, verified by reading the named files: `board/ias15_run.sh`
needs `IAS15_EXTRACT_DIR` + `IAS15_REF_HASHES` + `IAS15_COMPARE`;
`board/kissfft_run.sh` needs `MSF_KISSFFT_DIR` + `KISSFFT_EXPECT`;
today all of those exist only under `scratch/ias15/` and
`scratch/parcel-w4kissfft/`. The interval workload needs nothing
outside the repo. `demo/` closes exactly that gap; REBOUND and
KissFFT source live only in the gitignored `demo/cache/`, fetched
and patched/extracted at run time.

Brief correction found while verifying (brief said find the
values, do not trust it): the brief's patched-KissFFT prefixes
`cf9d011f...` / `1e03a1c7...` appear nowhere in RECORD or the
ledger. The board-run log (`muse-softfloat/build/kissfft-board/
tree-inputs.sha256`, the lead's 2026-10-28 silicon run) records
`kiss_fft.c` `8fcc496897ce...62305`, `kiss_fftr.c`
`b34ff3b21594...744f`, `_kiss_fft_guts.h` `42fd7132fdb1...9402`,
identical to a fresh hash of the live scratch tree this session.
Those are the values the demo pins.

Decisions frozen here, before implementation:

- **Cache and tracking refusal.** Everything fetched or generated
  from third-party source lives under `demo/cache/` (archives,
  pristine trees, `ias15-extract/`, `kissfft-tree/`, build output).
  One `.gitignore` entry (`demo/cache/`). `demo/fetch.sh` refuses
  to run when inside a git work tree and the cache path is not
  ignored or any cache file is tracked; outside a work tree (the
  `git archive` gate shape) it says the check was skipped and why.
- **Fetch.** Only the `REBOUND` and `KissFFT` rows of
  `docs/metrics/fetches.jsonl`, selected by name; no other URL is
  ever touched. Archive sha256 verified on the downloaded bytes,
  then licence sha256 verified on the licence member read from
  inside the archive (`LICENSE` for REBOUND,
  `LICENSES/BSD-3-Clause` for KissFFT - both confirmed against the
  recorded `licence_sha256` values this session) before the tree
  is extracted. `--offline` never invokes a downloader: a missing
  or hash-mismatched cached archive is a clean failure naming the
  file. Downloads go to a temp name and move into place only after
  both hashes pass.
- **IAS15 extract** (`demo/make_ias15_extract.py`). Output file
  set is exactly what `board/CMakeLists.txt` consumes:
  `integrator_ias15_min.c`, `gravity_basic_min.c`, `sim_min.c`,
  `ias15x.c`, plus `reb_min.h`. The two upstream-derived files are
  produced from the fetched 5.2.2 sources by the same anchored
  line-range keeps and asserted text transforms as the scratch
  reference (`scratch/ias15/scripts/pico_21_extract.py`), rewritten
  clean with no scratch paths; every transform asserts its hit
  count. Coefficient tables are emitted as binary64 bit patterns
  parsed from the committed `board/ias15_tables.h` (h/rr/c/d) - no
  mpmath, no scratch tables file. The three hand-written wrapper
  files are project-authored (ias15-pico parcel) and are emitted
  from templates carried in the generator with demo-accurate
  provenance headers; the expected diff against the scratch
  extract is provenance comments only, checked by diff in dev and
  by the host hashes as final arbiter. `driver_extract.c` is not
  generated: the board build never consumed it.
- **KissFFT tree** (`demo/make_kissfft_tree.py`). Copies the
  pristine fetched tree, applies the three Fork B exact-string
  patches (hard fail unless each anchor occurs exactly once),
  then requires: only those three files differ from pristine, and
  their sha256 equal the board-run-log values above. Any mismatch
  is a hard failure, never a warning.
- **IAS15 host proof.** Firmware-path shape (scratch Gate C):
  `demo/ias15_host_main.c` drives the extract through the repo's
  own `board/ias15_api.h` + `board/ias15_hash.c` +
  `board/ias15_ic.h` + `tests/sha256.c`, integer/hex I/O only.
  Two builds of the same sources: native (desktop-reference flags
  `-O3 -march=x86-64 -ffp-contract=off -fno-fast-math
  -fno-unsafe-math-optimizations -fexcess-precision=standard`;
  `-O3` is load-bearing - it keeps sqrt on inline `sqrtsd`, the
  libmingwex `sqrt` body is 1 ulp wrong on recorded operands) and
  soft-interposed (`-msoft-float -mno-sse2` + `demo/
  ias15_host_shim.c` routing every binary64 libcall into the
  core, no FMA contraction anywhere). The soft binary must report
  a non-zero shim operation count or the run is vacuous and
  fails. `demo/expected-ias15.txt` carries the FULL 2,001
  IAS15FH1 records (source `scratch/ias15/out/hashes_native.txt`,
  file sha256 `9bedb078...93ab3`, 373,196 B): full records chosen
  over a prefix because 373 KB is small next to the repo's
  committed vector sets and step-level divergence localisation is
  the point of the format. `demo/compare_ias15.py` compares data
  rows and requires the candidate's END line to show zero
  non-finite hashed fields; it doubles as the board stage's
  `IAS15_COMPARE`.
- **KissFFT host proof.** `demo/kissfft_host_main.c` is the clean
  repo version of the scratch host proof: same shared LCG inputs
  as `board/kissfft_main.c`, 12 configurations in frozen order,
  same analytic anchors. Built against the patched tree with
  `--wrap=sinpi,cospi,floor` over `compat/msf_aeabi.c` +
  `demo/kissfft_host_shim.c` (host stand-in for the pico-bound
  parts of `compat/msf_wrap.c`), `-Dkiss_fft_scalar=double`,
  `-ffp-contract=off`. `demo/expected-kissfft.txt` is the 12 KF
  rows from the parcel-w4kissfft results entry (identical in
  scratch `hashes-main.txt`) under a provenance header; the file
  is directly usable as `KISSFFT_EXPECT` because
  `board/kissfft_host.py` regex-filters KF rows.
- **Interval.** Wired in, not rebuilt: `board/interval_host.c` +
  `board/interval_workload.c` + core + `tests/sha256.c` over
  `tests/interval_catalogue.tsv`. `demo/expected-interval.txt`
  pins the full IW1 sha256 `ce81d66e...a9aec` (ledger
  parcel-w4interval results; BOARD.md's truncated form agrees at
  both ends) and the 710-row count.
- **run_demo.sh.** `host` = prereq check -> fetch -> extract/
  patch -> IAS15 host identity (native and soft vs expected) ->
  KissFFT host proof -> interval host run -> summary table with
  one PASS/FAIL line per workload, non-zero exit on any failure.
  `board` = host stages, then a preflight (PICO_SDK_PATH,
  arm-none-eabi-gcc, cmake, picotool, ledger layout) that must
  fully pass BEFORE any board script runs - a refusal names every
  missing item and never takes the lock or flashes. Board env is
  wired to the cache (`IAS15_EXTRACT_DIR`, `IAS15_REF_HASHES`,
  `IAS15_COMPARE`, `MSF_KISSFFT_DIR`, `KISSFFT_EXPECT`,
  `MSF_PYTHON`); existing board scripts run unmodified, stopping
  at the first failure. Prerequisite failures everywhere name the
  exact missing item. Demo scripts find python as `$MSF_PYTHON`,
  then `python3`, then `python` - portable for strangers.
- **Gate.** `git archive` of the branch tip into
  `scratch/parcel-w5demo/fresh/` with an empty cache:
  `bash demo/run_demo.sh host` green end-to-end with network;
  `bash demo/run_demo.sh host --offline` on an empty cache fails
  cleanly before any network use; branch `git status` /
  `ls-files` shows zero third-party source tracked. Board mode
  is exercised only where it must refuse (no ledger/toolchain),
  proving no lock file appears and nothing flashes.

## 2026-10-28 results entry

Verdict READY (report: `scratch/parcel-w5demo/report.md`).
Commits on `wave5-demo` (not pushed, not merged): `094538a`
fetch/regeneration, `3d3bfc0` host proofs + expected hashes,
`3feebb9` runner + docs. 18 files, only owned paths; branch
`git status` clean, `git ls-files demo/cache` empty.

- **Gate, as designed, all green.** Archive of tip `3feebb9`:
  `--offline` empty-cache exit 1 pre-network naming the missing
  archive (interval still passed, summary FAIL); online host
  exit 0 in 52 s with real downloads and `IAS15 PASS` /
  `KissFFT PASS` / `interval PASS`; board mode refused after a
  green host run naming ledger + SDK + pyserial, no lock file
  before or after. Tracked-cache refusals proven in a
  disposable clone (force-tracked file; removed ignore entry).
  `tools/run.sh smoke` PASS (34 s).
- **Numbers behind the PASS lines.** IAS15 native and soft:
  2,001/2,001 records identical, first divergence none; soft
  `SHIMOPS total=26083624 traps=0`. KissFFT 12/12 KF rows +
  anchors. Interval rows=710, IW1 `ce81d66e...a9aec`.
- **Extract equivalence.** Demo extract vs silicon-proven
  scratch extract: diff is provenance comments only (code bytes
  identical, 663/153-line files match). Demo-extract sha256s
  recorded in the report for future board-run provenance.
- **Brief correction stood up.** KissFFT patched hashes pinned
  from the board-run log (`8fcc4968...`, `b34ff3b2...`,
  `42fd7132...`), reproduced from the archive by the generator;
  the brief's prefixes exist nowhere in the record.
- **Two host traps hit and fixed in the runner:** GitHub
  archive URLs end in bare commit/tag (cache filenames now
  key-prefixed), and MSYS2's x86-64 gcc needs its bin dir first
  on PATH or cc1 exits silently (prepended after selection;
  the 32-bit bare `gcc` fallback already existed by design).
- **Not done, by design/brief:** board flashing (lead; first
  real board run also first-tests the demo extract's firmware
  build - inputs code-identical to the proven extract); MPFR
  twiddle provenance stays scratch evidence (demo proves KF
  identity, does not re-derive twiddles); non-x86-64 hosts
  refused by name (pinned-path scope); float KissFFT config
  untouched, as before.
