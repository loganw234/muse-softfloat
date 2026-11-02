**Role:** parcel-w6sanitize (Wave 6 queue item 3, from study-w6sanitize)

**Base:** `537b08edce17112da8f84353abcb2c693f2a5e65`, branch
`wave6-sanitize`, worktree `worktrees/w6-sanitize`. Work only there.

**Authority:** `scratch/study-w6sanitize/report.md` (read it
in full first; its measured facts are your starting point,
its S1+S3 shapes your design - argue with it in your report
where the tree disagrees). S2 (MSVC script) is out of scope.

**Job:** ship the sanitizer pass as a gate citizens can run.
- `tools/run.sh`: a fifth budget `sanitize` next to
  smoke|standard|board|bench, honouring the house rules
  (full inventory before verdict, refusals named). It builds
  the host runners with sanitizer instrumentation through the
  seam the study identified (never the compiler probe, never
  the ARM objects) and runs: unit tests, the committed vector
  set, the standard extras, and the augmented pool - the
  study's measured sets. Two flavours via `MSF_SANITIZE`:
  `trap` (default on this Windows host:
  -fsanitize=undefined -fsanitize-undefined-trap-on-error,
  zero installs) and `full` (-fsanitize=address,undefined
  with halt-on-error diagnostics, for Linux/CI). A flavour
  whose runtime is absent SKIPs-BY-NAME loudly in the
  inventory, never silently passes. Include canaries: small
  deliberate-UB programs (tests/ is yours for these) that
  must be watched trapping/reporting under the active
  flavour, so a green run proves instrumentation was live -
  the study's proven boundaries (e.g. trap flavour's
  size-lost-across-call blind spot) stated in the run's
  inventory text, not hidden.
- `.github/workflows/ci.yml`: an additive `sanitize` job on
  Ubuntu running the `full` flavour.
- AGENTS.md + run.sh usage text: the new budget named with
  its measured cost (yours to measure on this host).

Any real sanitizer finding is a STOP: minimal repro in the
report, no library fix attempted inside this parcel (that
becomes its own briefed work). The study found zero; expect
zero, prove the canaries make that meaningful.

**Owned files:** tools/run.sh, .github/workflows/ci.yml
(additive job), AGENTS.md (budget list only), tests/
(canary sources only), docs/metrics/briefs.jsonl (own row,
wave "wave6", binary-append). Library src/include frozen.

**Acceptance:** (a) `bash tools/run.sh sanitize` PASS on this
host (trap flavour): canaries trap, all sets zero findings
with totals printed; (b) `standard` still PASS with
byte-identical normalized verdicts (your budget must not
perturb the others); (c) `MSF_SANITIZE=full` on this host
SKIPs-BY-NAME (runtime absent) rather than failing or
silently passing - shown in a log; (d) the lead pushes the
branch to prove the CI sanitize job. Memory: state the peak
you measure; stay well under the study's 4 GB ceiling.

**Outputs:** tip commit(s) with detailed body +
`Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>`;
`scratch/parcel-w6sanitize/report.md` +
`ledger/parcel-w6sanitize.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv. Nothing with
`cft` in its name. ~480 min.
