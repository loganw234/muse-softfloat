# Ledger: verifier-w5demo (ParcelRound demo reproducibility)

Copy `worktrees/verify5-demo` @ `b21510b` (parent `26e86ce`).
Full evidence: `scratch/verifier-w5demo/report.md`.

Verdict NOT READY - five findings, copy left clean (`git status`
empty, no board touched):

1. `demo/expected-ias15.txt` step-2000 H_state first nibble wrong
   (`5d45...` committed; pinned archives recompute `4d45...`,
   agreeing with the RECORD quote). Fresh native run: 2000/2001.
2. `demo/expected-kissfft.txt` row 1 last nibble wrong (`...67e`
   committed; ledger/parcel-w4kissfft results + live rebuild give
   `...67d`). Fresh run: 11/12.
3. `demo/fetch.py:188` licence check guarded by `if False:` -
   zeroed licence_sha still prints `licence-sha256 OK`, exit 0.
4. `demo/run_demo.sh` summary: `host_ok` never updated
   (`[ ... ] || true`); all-red run still prints `demo host:
   PASS`, exit 0; board stage not gated on green host.
5. `.gitignore` has `demo/cache2/` instead of `demo/cache/` -
   fetch refuses in any real clone; parcel gate used `git archive`
   (check skipped outside a work tree) and missed it.

Control: with exactly those two nibbles fixed in scratch only,
`run_demo.sh board --offline` goes IAS15 native+soft 2001/2001
(SHIMOPS 26083624 traps=0, as parcel-quoted), KissFFT 12/12,
interval IW1 identical, then board preflight refuses by name with
no lock and no flash. Generators and proofs are sound; the five
defects above are the complete blockers.

Traces: IW1 full hash in parcel-w4interval ledger + live match;
12 KF rows in parcel-w4kissfft ledger + live 12/12; patched-tree
hashes reproduce from pinned archive (= parcel-w5demo quotes);
extract set == board/CMakeLists.txt inputs; claim surface 18
brief-owned files only. Not done: board flashing (no hardware),
MPFR/float/non-x86-64 scope-outs, RECORD step-0 quote
unfindable, nibble-flip origin undeterminable in-bounds.
