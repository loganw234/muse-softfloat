# parcel-w6ci - library CI on Linux (Wave 6 queue item 2)

Brief: `ledger/briefs/w6-ci.md`. Base:
`50aac59f6035d56c37340ff07c59252cfd22d5d4`. Branch `wave6-ci`
in `worktrees/w6-ci`. Full report:
`scratch/parcel-w6ci/report.md`.

## Result

Tip `eda5812d2803b113fe0eaa37b626d5d097a4a979` (one commit,
**not pushed** - the lead pushes to trigger the real Actions
run). Files: `.github/workflows/ci.yml` (new),
`tools/run.sh` (2 portability-only guards, +9/-1),
`docs/metrics/briefs.jsonl` (own wave6 row, binary append,
prefix hash-verified). No src/include, no HARNESS/AGENTS
pointer (ci.yml header documents it; judged not truly
needed). No subagents started.

CI shape: jobs `smoke` (20 min) and `standard` merge gate
(60 min) on ubuntu-latest, triggers push/pull_request/
workflow_dispatch; apt install gcc + libc6-dev + python3 +
gcc-arm-none-eabi; toolchain-inventory step fails loudly on
a missing tool so the symbol scan cannot silently skip;
`MSF_PYTHON=python3 bash tools/run.sh <budget>`; build logs
uploaded as artifacts on every run.

## Acceptance probes (all run on this host)

- (a) standard PASS pre-edit 62 s and post-edit 60 s (Git
  Bash, MSF_PYTHON = workspace .venv, machine under wave
  load); normalized outputs byte-identical (cmp clean, 9169
  bytes). 411213 committed + 1117504 generated vectors, 0
  failed; drift 4/4; inventory tier1 783/783, tier2 66/66;
  all controls refused incl. x87. Smoke post-edit PASS 26 s.
- (b) YAML parsed with PyYAML 6.0.3 (scratch-only install).
  Inventory + both gate commands run locally in equivalent
  form; checkout/upload actions and apt-get are CI-only.
- (c) Green-run shape and Ubuntu risks written out in the
  report. Headlines: package versions under -Werror (Ubuntu
  gcc 13.x vs host 16.1.0), ubuntu-latest floats, mawk vs
  gawk; the x87 control will print SKIP-BY-NAME on Ubuntu
  by design while its dumpmachine + FLT_EVAL_METHOD
  refusals still run. No identified path to a false green.

## Next step (lead)

Push `wave6-ci`; judge the Actions run by its inventory
lines (expected totals above), not the tick alone.

## Revision round (CRLF $NF failure, Actions 41052508849)

Lead pushed; first Ubuntu run: 411,213 vectors PASS, one
control NOT refused - wrong-nan-expectation. Cause:
encodings-f32.vec fully CRLF; Linux awk leaves CR on $NF,
the control's `$NF==` matched nothing, mutant unmutated,
runner passed it; MSYS text mode had masked it on Windows
(original-round inventory item 15 verified identical
checkout bytes, not identical awk parsing - wrong
property).

New tip `5b53bf3db94100b401eb6f7bef516472d9d28dc1` on
`wave6-ci` (**not pushed**; lead re-pushes). tools/run.sh
only (+11/-3, LF-only, metrics untouched by instruction).
Both fixes compare/print the last field CR-stripped on a
copy via POSIX substr string ops (no regex escape, no
field assignment, records otherwise byte-identical):
(1) control 2 compare (L186) - the bug; (2)
write_expect_counts tag print (L130) - the one other real
instance (41,871/411,213 tags carried CR into expect.txt
on Linux; benign only because 0 of 77 tags span CRLF+LF
files and the runner's sscanf %s stops at CR). Full
per-pattern audit of all 12 awk programs + 1 sed with
measured input endings in the report: everything else
matches start-anchored/interior fields ($1, $2, $(NF-1),
$9, $13, header-named interior cols), coerces numerically,
or reads LF-by-construction inputs (COVERAGE.tsv via
gen_tables write_bytes; same-run generated files); none
can silently pass on CRLF, and all refused on Ubuntu.

Proof: (1) standard PASS 56 s on this host (Git Bash,
MSF_PYTHON = .venv), wrong-nan-expectation refused,
normalised summary byte-identical to pre-revision run.
(2) Linux semantics via gawk BINMODE=3 (binary in/out,
gate's own MSYS awk 5.4.0; channel check len($NF)
27 text-mode vs 28 binary on line 1024): OLD program
output byte-identical to input (0 diff bytes - failure
reproduced here); NEW exactly 1 byte differs (offset
64779 '0'->'1', line 1024, 2353 CRLFs preserved, 150,556
bytes both); tag-stage NEW output byte-identical across
Windows/Linux channels and OLD==NEW on Windows. Scripts
+ outputs in scratch/parcel-w6ci/ (rev_*). Remaining
advance-unproven item: Ubuntu mawk executing the substr
idiom (pure POSIX; any surprise fails loud, never a
false green). Expect at re-push: run-1 inventory plus
wrong-nan-expectation refused, controls all refused,
x87 SKIP-BY-NAME by design.
