# parcel-w6sanitize - sanitize budget (Wave 6 queue item 3)

Brief: `ledger/briefs/w6-sanitize.md`. Authority:
`scratch/study-w6sanitize/report.md` (S1+S3 shipped; S2
out of scope). Base:
`537b08edce17112da8f84353abcb2c693f2a5e65`. Branch
`wave6-sanitize` in `worktrees/w6-sanitize`. Full report:
`scratch/parcel-w6sanitize/report.md`.

## Result

Tip `1bc097977e44f86be4d3c984bbaf19ca8225fd63` (one
commit, **not pushed** - lead pushes to prove the CI
sanitize job, acceptance (d)). Files: `tools/run.sh`
(fifth budget `sanitize`, MSF_SANITIZE trap|full,
canaries-first, per-file verify, SKIP-BY-NAME on absent
runtime), `tests/sanitize_canary_*.c` (5 new),
`.github/workflows/ci.yml` (additive Ubuntu sanitize job,
full flavour), `AGENTS.md` (budget list + measured cost),
`docs/metrics/briefs.jsonl` (own wave6 row, binary
append, prefix verified). src/include untouched.

Semantics to know: `MSF_SANITIZE` with a non-sanitize
budget REFUSES (exit 2) - the merge gate cannot be
re-flavoured. An absent-runtime flavour SKIPs-BY-NAME:
exit 0, **no PASS verdict printed**, no findings claimed.
Judge any sanitize run by the `budget sanitize: PASS`
line, never the tick/exit alone.

## Acceptance probes (this host, Git Bash, venv pinned)

- (a) sanitize trap PASS x3 (44-56 s): canaries ub/
  ub_shift/heap trapped exit 132, clean exit 0, heap_far
  printed NOT CAUGHT (trap's proven blind spot, stated in
  inventory); unit + 411213 + 1117504 + aug 5505024, zero
  findings; corrupt control refused on sanitized twin.
  Unsanitized ub canary exits 0, so traps = live
  instrumentation. Peak WS 3.9 MB (ceiling 4 GB).
- (b) standard PASS before/after; normalized verdicts
  byte-identical (9169 B).
- (c) MSF_SANITIZE=full here: SKIP-BY-NAME in 1 s
  (`cannot find -lasan/-lubsan` in log), no PASS.
- YAML parsed (PyYAML 6.0.3, scratch install); negative
  probes for the new refusals all refused.

## Next step (lead)

Push `wave6-sanitize`; expect the sanitize job to print
`budget sanitize: PASS` under flavour full with heap_far
caught and the totals above. If Ubuntu cannot link the
sanitizer runtime from the shared apt line, it will say
SKIP-BY-NAME instead - that is a loud non-pass, not a
green.

## Revision (CI run 41061712195)

Pushed 1bc0979: smoke+standard PASS; sanitize job FAIL at
host build (canaries all caught under full first - not a
finding): gcc 15 + sanitizer flags + -Werror promoted
-Wstringop-truncation at tests/runner.c:477 strncpy. Fixed
in `77e6e647cac519a35975b1adadecfb157e0c93b5` (one hunk,
+6/-2, **not pushed**): bounded length + memcpy + zero-fill
reproducing strncpy's bytes on all 4096 (incl. zero-padding
and L>=4095 truncation; only caller fgets(buf[4096]) so
L<=4095 in practice; full-4096 memcmp probe PASS). Length
spelled with memchr (= strnlen(line,4095)) not strnlen:
strnlen is POSIX, undeclared under -std=c11 on glibc
without _POSIX_C_SOURCE>=200809L - would break the same
Linux build; macro would need a top-of-file edit outside
the hunk. raw's only observable read is printf %s via
fail_line. Proofs here: standard PASS, normalized surface
byte-identical to pre-revision (9169 B); sanitize trap
PASS zero findings (canaries caught, totals
411213/1117504/5505024); full-SANFLAGS build of runner.c +
library compiles clean, fails only at link
(-lasan/-lubsan absent here), -Werror=stringop-truncation
compile-only rc=0. No full-flavour run claimed. Next:
lead re-pushes wave6-sanitize (new tip 77e6e64); judge by
`budget sanitize: PASS` in CI, not the tick.
