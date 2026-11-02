**Role:** verifier-w5demo (ParcelRound verifier, demo reproducibility)

**Stance:** disconfirm only. Findings (a) a reproducibility
break (fresh-clone run fails or lies), (b) wrong evidence
(expected data or verification that would pass a broken
workload), (c) third-party source at risk of being tracked.

**Copy:** `worktrees/verify5-demo` (detached HEAD, parent
`26e86ce`). Never consult the parcel branch/worktree,
other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5demo/`, `scratch/ias15/`,
`scratch/parcel-w4kissfft/`, or `ledger/lead.md`. The
parcel ledger + copy's docs (RECORD, BOARD, fetches.jsonl)
are governing. Clean room: nothing with `cft` in its name.
Never modify the copy. No board flashing. **Light load**
(host stage is short; keep it sequential).

**Required probes:**
1. Fresh-clone truth: `git archive` the copy into your
   scratch, empty cache, run `bash demo/run_demo.sh host`
   end-to-end; all three PASS lines reproduced; then
   corrupt one input of your choice (flip a bit in a
   cached archive) and watch it refuse; `--offline` with
   empty cache refuses pre-network.
2. Verification integrity: fetch.py checks BOTH hashes
   (source-read + a tampered-licence cache probe);
   summary logic - force one workload red in your
   archive copy (corrupt an expected line at runtime in
   scratch) and watch the summary + exit code go red;
   expected-* values traced to RECORD/ledger-quoted
   hashes (IAS15 step-2000, the 12 KF rows, IW1).
3. Tracking safety: `.gitignore` covers the cache path
   the scripts actually use; fetch refuses when the
   cache path would be tracked (exercise it); `git
   ls-files` shows no third-party source; the patched
   KissFFT tree hashes match the recorded board-run
   values; the IAS15 extract file set matches what
   `board/CMakeLists.txt` consumes.
4. Docs honesty: demo/README claims vs behavior (what
   host stage does NOT prove stated; prerequisites
   complete; GPL note present); README/BOARD links
   resolve; claim surface vs parent = brief-owned files.

**Outputs:** `scratch/verifier-w5demo/report.md` (first
line READY/NOT READY; fresh-run summary; findings with
smallest repro; not-done) and `ledger/verifier-w5demo.md`.
Structured complete/evidence/unresolved. Script files
(Git Bash; demo scripts use portable python).
