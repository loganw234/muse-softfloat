# Verifier-w5demo report (copy: worktrees/verify5-demo @ b21510b, parent 26e86ce)

NOT READY

Five disconfirming findings. A fresh clone can never go green: two
single-nibble corruptions in the committed expected files fail the
host proofs, the licence check is dead code, the summary always
prints PASS with exit 0, and the .gitignore typo makes fetch refuse
inside any real git clone. With exactly two nibbles corrected in
scratch only, the same tree goes fully green (native+soft 2001/2001,
SHIMOPS 26083624 traps=0, 12/12 KF, IW1 identical), so the defects
are precisely the five below - the generators and proofs are sound.

## Fresh-run summary (git archive HEAD -> scratch, empty cache, network)

- `bash demo/run_demo.sh host` (MSF_HOST_CC=mingw64 gcc, MSF_PYTHON=python):
  fetch OK (~7 MB real downloads); IAS15 extract OK; FORKB-PATCH OK
  (3 sites, hashes match recorded values); native IAS15
  2000/2001, DIVERGE step 2000 only; KissFFT 11/12 (row 1 last
  nibble); interval rows=710 IW1 identical. Summary printed
  `IAS15 FAIL / KissFFT FAIL / interval PASS` followed by
  `demo host: PASS`, exit 0.
- `--offline` with empty cache (separate archive tree): exit 1
  pre-network, naming the missing archive. PASS.
- `--offline` with seeded cache: proceeds, no network. PASS.
- Tampered cached archive (one bit flipped): exit 1 naming the
  file; restored byte-identical afterwards. PASS.
- Board stage: never past preflight; no hardware touched, no lock
  file created (swept scratch - none).

## Findings (smallest repro each; all in scratch, copy untouched)

1. **expected-ias15.txt step 2000 H_state corrupted.** Committed
   line 2013 starts `5d4530a6...f48abb`; the pinned archives
   recompute `4d4530a6...f48abb` (H_full, t/dt bits identical -
   a 252-of-256-bit agreement no real divergence produces), and
   docs/RECORD.md quotes `4d4530a6...f48abb`. Repro: fresh native
   run -> `DIVERGE step 2000`, matched=2000. One nibble.
2. **expected-kissfft.txt row 1 corrupted.** Committed ends
   `...36067e`; ledger/parcel-w4kissfft.md results and the live
   rebuild from the pinned archive both give `...36067d`
   (other 11 rows match everywhere). Repro: `diff kf-expect kf-got`
   -> `1c1`. One nibble.
3. **Licence verification is dead code.** demo/fetch.py line 188
   guards the licence comparison with `if False:`, yet prints
   `licence-sha256 OK`. Repro: zero the REBOUND licence_sha256 in
   a scratch fetches copy, `--offline` -> `FETCH ... OK`, exit 0.
   The README/fetch.sh "verifies licence sha256" claims are false.
4. **Summary never goes red.** run_demo.sh sets `host_ok=1`, then
   `[ PASS-check ] || true` discards the test. Repro: corrupt the
   interval hash in scratch -> all three FAIL, still
   `demo host: PASS`, exit 0 (captured without pipe). Consequence:
   board stage is not gated on a green host either (only the
   missing-SDK preflight stopped it here).
5. **.gitignore covers `demo/cache2/`, scripts use `demo/cache/`.**
   So `demo/cache/` is not ignored: `git check-ignore` fails, and
   fetch.sh refuses inside ANY real clone
   (`demo/cache/ is not gitignored here`). Repro: `git clone` the
   copy -> `bash demo/fetch.sh --offline` -> exit 1 with that
   refusal. The parcel gate used `git archive` (outside a work
   tree the check is skipped), so it never saw this. Positive
   control: correcting the entry lets the gate pass. `git ls-files
   demo/cache` is empty and the 9 kiss/rebound/extract/cache
   name-matches are all owned files - nothing third-party tracked.

## Traces (expected values -> record)

- IAS15 step 2000: expected file (`5d45...`) matches NEITHER the
  live recomputation nor RECORD (`4d45...`). RECORD's truncated
  quote agrees with the pinned-source truth at both ends.
- 12 KF rows: ledger/parcel-w4kissfft.md lines 237-248 match the
  live rebuild 12/12; expected file matches 11/12 (row-1 nibble).
- IW1: full `ce81d66e...a9aec` in ledger/parcel-w4interval.md,
  BOARD.md truncated form agrees at both ends, live run identical.
- Patched-tree hashes equal the parcel-w5demo ledger quotes and
  reproduce from the pinned archive; the board-run log itself was
  not consulted (out of bounds).
- Extract file set (4 .c + reb_min.h, no driver_extract.c) is
  exactly what board/CMakeLists.txt consumes. Verified by reading.
- Claim surface vs parent 26e86ce: 18 files, all brief-owned
  (demo/**, .gitignore, README one line, BOARD.md pointer,
  briefs.jsonl row). No scope creep. README/BOARD links all
  resolve; every README-named file exists in the copy.

## Not done (by design or out of reach)

- Board flashing: no hardware (parcel scope is dry-refusal; the
  refusal path was observed live, naming ledger/SDK/pyserial).
- MPFR twiddle re-derivation, float KissFFT config, non-x86-64
  hosts: out of the demo's stated scope.
- Step-0 RECORD quote: `62bb23b0...` appears nowhere in RECORD,
  so the expected-file header's "step 0 ... quoted in the project
  record" could not be cross-checked (step-2000 quote checked).
- Origin of the two nibble flips (gate-green-then-edited vs
  misreported gate) is not determinable from allowed sources.
