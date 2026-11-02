# verifier-w6ci report: CI-on-Linux parcel (copy `worktrees/verify6-ci` @ `3cec27c`)

**VERDICT: NOT READY.** The parcel's core claim — a revision fixing the CRLF
`$NF` failure on Linux — is a no-op in the committed code: the Linux gate
still passes the wrong-nan mutant (`NOT REFUSED` → `RUN.SH: FAIL`). The CI
workflow additionally does not run what its header claims (wrong OS, wrong
budget, non-enforcing inventory, dead artifact path), and a portability guard
regresses the Windows host run. Nothing below consults the parcel branch,
other worktrees, keys, `scratch/lead/`, `scratch/parcel-w6ci/`,
`ledger/lead.md`, GitHub run history, `docs/metrics/plants.jsonl`, or any
`cft` path. The copy was never modified; all gates ran in
`scratch/verifier-w6ci/dup/`.

## Findings

- F1 | `.github/workflows/ci.yml:57` | claimed Ubuntu CI for both jobs;
  re-derived `standard` job `runs-on: windows-latest` (only `smoke:26` is
  `ubuntu-latest`). Header lines 3–4 ("runs the library gate on Ubuntu")
  and parcel ledger ("ubuntu-latest" for both) contradict the file.
- F2 | `.github/workflows/ci.yml:74` | claimed merge gate runs the
  `standard` budget (header lines 5–6, ledger); re-derived run step is
  `MSF_PYTHON=python3 bash tools/run.sh smoke`. The exhaustive binary16 +
  pack-sweep + aug-pool leg never executes in CI. Both jobs run the identical
  command; they differ only in name and artifact path.
- F3 | `.github/workflows/ci.yml:35-42,67-72` | claimed inventory "fails
  loudly on a missing tool"; re-derived each version probe is piped to
  `head` with no `pipefail`, so a missing tool exits 0. Measured on Linux
  channel (WSL): `nonexistent-tool --version | head -n 1` →
  `pipeline-status=0`. No `dumpmachine`/x86-64 or `FLT_EVAL_METHOD`
  enforcement in the step; a machine with no ARM toolchain prints a green
  inventory then `symbol scan: SKIP-BY-NAME` (observed in WSL run).
- F4 | `.github/workflows/ci.yml:80-84` | `standard` job uploads
  `build/standard/*`, but per F2 it runs the `smoke` budget which writes
  `build/smoke/*`; the path matches nothing (`if-no-files-found: warn`), so
  the merge-gate job keeps no logs even when it fails. (`smoke` job path is
  consistent.)
- F5 | `tools/run.sh:28` | PATH guard inverted vs its own comment ("only
  prepend when they are actually there"): `[ ! -d ... ] && export ...`
  prepends nonexistent MSYS dirs on Linux and skips the prepend on Windows
  where the dirs exist. Measured: plain `bash tools/run.sh standard` under
  Git Bash on this host FAILs `compiler REFUSED: gcc
  dumpmachine=i686-w64-mingw32 (need x86_64-*)`; the gate passes only with
  the msys64 `mingw64/bin` PATH restored (pre-revision behavior).
- F6 | `tools/run.sh:130` | `write_expect_counts` computes stripped `t` but
  prints `$NF`, so the CR-strip is dead code. Measured Linux (WSL gawk
  5.1.0): NEW output has 10 tag lines carrying CR and is byte-identical to
  OLD (`OLD==NEW`). Benign only because the runner consumes tags with
  `sscanf %s` and expect-counts are generated/consumed on the same channel.
- F7 | `tools/run.sh:186` | control-2 computes stripped `t` but matches
  `$NF=="exact-py:directed-encodings"`, so on Linux ($NF is 28 chars with
  trailing CR) it still matches nothing. Measured: NEW program output
  byte-identical to `encodings-f32.vec` input (0 diff bytes) under WSL gawk
  and under MSYS gawk 5.4.0 semantics; full WSL smoke gate ends
  `control wrong-nan-expectation: NOT REFUSED` →
  `RUN.SH: FAIL - a negative control was not refused`. The parcel's proof
  ("NEW exactly 1 byte differs, offset 64779") is irreproducible from the
  committed code. A corrected `t==` variant differs in exactly 1 byte
  (`cmp`: byte 64780, `0`→`1`, line 1024, 2353 CRLFs preserved) and yields 0
  CR tags — proving the idiom works and the committed placement is wrong.
  On the Windows channel OLD==NEW byte-identical (MSYS text mode
  `len($NF)=27` vs Linux `28` — masking mechanism confirmed).
- F8 | `tools/run.sh:39` (`python3` fallback) re-derived OK: guarded by
  `command -v`, unreachable when `MSF_PYTHON`/`.venv` resolve; no finding.

## Probes (all four ran; numbers measured)

- P1 ci.yml vs header: YAML parses (`YAML-OK`, job/step dump verified).
  Triggers `push/pull_request/workflow_dispatch` and `if: always()` uploads
  match the header; findings F1–F4 above. `windows-latest` + `sudo apt-get`
  (F1+F2) means the `standard` job fails before the gate on a real runner.
- P2 run.sh diff vs parent `50aac59` re-derived hunk by hunk (Windows AND
  Linux semantics): PATH guard (F5), python3 fallback (F8 OK), tag print
  (F6), control-2 match (F7). `encodings-f32.vec`: 2353/2353 lines CRLF,
  150556 bytes, `len($NF)` 28 Linux vs 27 MSYS-text.
- P3 gate `tools/run.sh standard` in duplicate, `MSF_PYTHON` = workspace
  `.venv` python 3.12.15: Windows channel PASS in 51 s — every negative
  control refused (12 `refused as required`, incl. x87 refusal and
  tier-inventory `783/783 + 66/66`), totals `411213 passed` committed and
  `1117504 passed` generated,0 failed; aug-pool `5505024/0`. Linux channel
  (WSL, Ubuntu gcc 11.4.0, python3 3.10.12): committed vectors still
  `411213 VERDICT: PASS`, but gate FAILs at F7. Plain host invocation FAILs
  at F5 before any of this.
- P4 parcel-ledger inventory/assumptions re-derived from the copy:
  `COVERAGE.tsv` counts 783×`1 implemented` + 66×`2 implemented` (matches
  `TIER1/2_TOTAL_EXPECTED`); compiler-refusal shape confirmed live (i686
  `dumpmachine` refused); `SKIP-BY-NAME` paths confirmed
  (`arm-none-eabi-gcc` absent → symbol-scan skip; `/c/msys64/mingw32`
  present here → x87 refusal ran, absent on Ubuntu → skip by design);
  `ubuntu-latest` float and `mawk`-vs-`gawk` risks stand (WSL has gawk 5.1.0
  only — parcel's own "advance-unproven" item).

## Not done / gaps

- `mawk` execution of the `substr` idiom untested (no mawk on this host).
- Ubuntu `gcc 13/14 -Werror` build unproven (WSL gcc 11.4.0 built clean;
  CI's exact toolchain never ran here, and per fences no GitHub history).
- `FLT_EVAL_METHOD!=0` refusal path not triggered live (x87 refusal here
  fired at the `dumpmachine` stage first).
- `BINMODE=3` emulation on the MSYS gawk would not engage in this shell
  (`len($NF)` stayed 27); irrelevant — WSL is the real Linux channel and
  carries P2/P3 there.
- Normalized verdict surface vs parent byte-compare not run as full-gate
  A/B; substituted by OLD-vs-NEW program-output identity on both channels
  (identical Windows, identically-broken Linux).
