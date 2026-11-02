**Role:** verifier-readme2 (ParcelRound verifier, Wave 5 README restatement)

**Stance:** disconfirm only. Findings (a) a README claim
the copy's artefacts contradict, (b) a claim with no
locatable authority in the copy.

**Copy:** `worktrees/verify-readme2` (detached HEAD,
parent `7c3819c`). Audit ONLY the README.md diff surface
(the Status section, deferred list, studies location row)
against in-copy evidence: `docs/COVERAGE.tsv` (attr-row
census), `docs/RECORD.md`, `docs/metrics/plants.jsonl`
(grades), `docs/studies/SF-2.md` (step order + landed
state), committed vector recount, header enum. Never
consult the delivery branch/worktree, other worktrees,
keys, `ledger/` other than this brief, or `scratch/`
other than your own output dir. Nothing with `cft` in
its name, ever. Never modify the copy.

**Probes:** (1) vector total recount from
`tests/vectors/`; (2) plant score from plants.jsonl
grades; (3) attr-row census from COVERAGE; (4) landed vs
planned steps vs RECORD + COVERAGE (nothing claimed
landed that is only registered/planned); (5) refusals/
deferrals wording vs SF-1 Sec.7 + SF-2 Sec.1; (6) SF-2
exists in studies/ and is a plan of record.

**Outputs:** `scratch/verifier-readme2/report.md` (first
line READY/NOT READY; per-claim table; findings with line
refs) and `ledger/verifier-readme2.md`. Structured
complete/evidence/unresolved. Script files for counts
(Git Bash, MSF_PYTHON pinned).
