# verifier-w6ci (ledger record)

**VERDICT: NOT READY.** Full report: `scratch/verifier-w6ci/report.md`.
Copy `worktrees/verify6-ci` @ `3cec27c` (parent `50aac59`); copy never
modified, all gates in `scratch/verifier-w6ci/dup/`.

## Findings (path:line + re-derived)

- F1 `ci.yml:57`: `standard` job is `windows-latest`, not Ubuntu (header +
  ledger claim ubuntu). Runs `sudo apt-get` → fails on a Windows runner.
- F2 `ci.yml:74`: `standard` gate step runs `tools/run.sh smoke`, not
  `standard`; exhaustive legs never run in CI.
- F3 `ci.yml:35-42`: inventory cannot fail loudly — every version probe is
  piped to `head` without `pipefail` (measured pipeline status 0 for a
  missing tool); silent `SKIP-BY-NAME` symbol scan follows.
- F4 `ci.yml:80-84`: `standard` uploads `build/standard/*` but runs the
  `smoke` budget → no artifacts even on failure.
- F5 `run.sh:28`: PATH guard inverted (`! -d`); plain host gate FAILs
  (`compiler REFUSED ... i686-w64-mingw32`), passes only with PATH fixed.
- F6 `run.sh:130`: tag stage prints `$NF` not stripped `t` (dead strip;
  Linux: 10 CR tags, OLD==NEW).
- F7 `run.sh:186`: control-2 matches `$NF==` not `t==`; Linux output is
  byte-identical to input (0 diff bytes) and the WSL smoke gate ends
  `wrong-nan-expectation: NOT REFUSED` → `RUN.SH: FAIL`. Corrected `t==`
  variant differs in exactly 1 byte (byte 64780, line 1024). Parcel proof
  irreproducible.
- F8 `run.sh:39` python3 fallback: checked OK, no finding.

## Probes

P1 YAML parses; triggers/`always()` uploads OK; F1–F4. P2 diff re-derived
per hunk on both channels (`len($NF)` 28 Linux / 27 MSYS text; vec 2353
CRLF lines). P3 Windows-channel `standard` PASS 51 s: 12 controls refused,
totals 411213 + 1117504, 0 failed; Linux-channel FAIL at F7 (vectors alone
411213 PASS). P4 inventory 783/66 re-derived; refusal + skip-by-name shapes
confirmed live; mawk and Ubuntu-gcc-13 -Werror unproven (see report gaps).
