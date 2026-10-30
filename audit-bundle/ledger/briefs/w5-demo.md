**Role:** parcel-w5demo (owner side parcel: reproducible workloads)

**Deliverable:** a `demo/` directory on branch
`wave5-demo` (worktree `worktrees/w5-demo`, base
`26e86ce`) that lets a stranger reproduce the three
workload evidences from a fresh clone with one script -
without REBOUND or KissFFT source ever entering the
repository. Time box 600 min. **Light machine load**
(another sweep owns the box at lowered priority: single-
threaded builds, no parallel make beyond -j2).

**The gap you close (verify it yourself first):**
`board/ias15_run.sh` needs a pre-made IAS15 extract +
reference hashes + compare script; `board/kissfft_run.sh`
needs a pre-patched KissFFT tree + expected-hashes file;
today those exist only in workspace scratch
(`scratch/ias15/`, `scratch/parcel-w4kissfft/` - read
them as the reference implementation of the steps, then
write clean repo versions; your scripts must not depend
on scratch paths). Interval is already reproducible from
the repo - wire it in, don't rebuild it.

**What to build (all under `demo/` unless noted):**
1. `demo/fetch.sh` (+ helpers): reads the pinned rows
   from `docs/metrics/fetches.jsonl` (REBOUND 5.2.2
   commit archive, KissFFT 131.2.0), downloads into
   `demo/cache/` (new `.gitignore` entry; the script
   refuses to run if the cache would be tracked),
   verifies archive sha256 AND licence sha256 against
   the fetches rows before extraction, extracts. No
   network beyond those two URLs; `--offline` mode uses
   a pre-seeded cache and says so.
2. `demo/make_ias15_extract.py`: produces the IAS15
   extract (same file set + shim treatment the board
   build consumes - derive the contract from
   `board/CMakeLists.txt` + `board/ias15_*.h/.c`, and
   cross-check against the scratch extract's file
   hashes if present); `demo/make_kissfft_tree.py`:
   applies the 3-site Fork B patch (sites per
   `docs/BOARD.md` + the parcel ledger; result must
   hash-match the recorded patched file sha256s -
   kiss_fft.c cf9d011f..., kiss_fftr.c 1e03a1c7... from
   the board-run log in the RECORD trail; find them,
   don't trust this brief).
3. Host proofs as repo sources (our code, MIT header):
   `demo/ias15_host_main.c` (native + wrapped builds ->
   state hashes, compared bit-for-bit; strict flags -
   no FMA contraction, per `docs/BOARD.md` traps) and
   `demo/kissfft_host_main.c` (the 12-configuration hash
   proof vs committed `demo/expected-kissfft.txt`).
   Committed expected data: `demo/expected-ias15.txt`
   (2,001 records or a stated prefix with the full-run
   final hash - decide and justify by size) and
   `demo/expected-kissfft.txt`, both sourced from
   RECORD/ledger values, provenance lines on top.
4. `demo/run_demo.sh`: one entry point.
   `./demo/run_demo.sh host` = fetch (or offline) ->
   extract/patch -> IAS15 host identity -> KissFFT host
   proof -> interval host run -> summary table with
   PASS/FAIL per workload. `./demo/run_demo.sh board`
   additionally drives the existing board scripts with
   env wired (lock, serial targeting from `common.sh`;
   refuse clearly when no board/toolchain is present -
   never half-flash). Clear prerequisite failures
   (missing gcc/python/arm toolchain/PICO_SDK_PATH)
   with the exact missing item named.
5. `demo/README.md`: prerequisites, what each stage
   proves, what it does NOT prove (host identity != the
   board claim; board stage optional), licence notes
   (REBOUND GPL stays in your cache; nothing here
   redistributes it), expected wall times as recorded
   facts. Links: README.md gains one line under the
   demo link; `docs/BOARD.md` gains a pointer paragraph.

**Proof of done (the parcel's own gate):** from a
`git archive` of your branch tip unpacked into scratch
with an empty cache, `bash demo/run_demo.sh host` runs
green end-to-end (network on), and `--offline` fails
cleanly before touching the network. `git status` of
the branch shows zero third-party source files. Board
stage: syntax-check + dry refusal paths only (no
flashing - board time is lead work; the board may be
busy).

**Owned files:** `demo/**`, `.gitignore`, `README.md`
(one line), `docs/BOARD.md` (pointer paragraph),
`docs/metrics/briefs.jsonl` (your row). `src/`,
`board/*` (except BOARD.md), `tests/`: read-only.

**Report:** `scratch/parcel-w5demo/report.md` (first line
READY/NOT READY; fresh-clone run log summary with the
three PASS lines; file inventory stating what is ours
vs fetched; not-done) + `ledger/parcel-w5demo.md`.
Detailed commits ending the Co-Authored-By trailer.
Never push/merge. Structured complete/evidence/
unresolved. Script files for runs (Git Bash, MSF_PYTHON
pinned to the workspace .venv when in-workspace; the
demo scripts themselves must use `python3`/`python`
portably - strangers have no .venv).
