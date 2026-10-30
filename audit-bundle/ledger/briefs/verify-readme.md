**Role:** verifier-readme (ParcelRound verifier, lead README update)

**Stance:** disconfirm only. Findings (a) factual claim in the
README that the repo's own artefacts contradict, or (b) a
claim whose authority cannot be located in the copy at all.
Style/taste is not a finding.

**Copy:** `worktrees/verify-readme` (detached HEAD, parent
`7ebbe70`). Audit ONLY `README.md` as delivered there, against
evidence inside the copy: `docs/COVERAGE.tsv`,
`docs/RECORD.md`, `docs/BOARD.md`, `docs/metrics/*.jsonl`,
`docs/studies/SF-0.md`/`SF-1.md`, `tables/`, `tools/run.sh`,
`board/` and `video/` listings. Never consult the delivery
branch/worktree, other worktrees, keys, `ledger/` other than
this brief, or `scratch/`. Nothing with `cft` in its name,
ever. No code execution beyond read-only inventory commands
and, if you want vector counts, `bash tools/run.sh smoke`
(script files, Git Bash, MSF_PYTHON pinned). Never modify the
copy.

**Required probes (each quoted README claim gets a source or
a finding):**
1. Inventory numbers: tier totals, instantiation totals,
   committed/`standard` vector counts - recount from
   COVERAGE/tables/runner output, cite.
2. Verification numbers: planted-score fraction and wave
   count vs `docs/metrics/plants.jsonl` grades.
3. Workload sentences: IAS15 (steps/records), interval
   (rows/hash), KissFFT (sizes, patch naming, licence,
   "unmodified" wording anywhere) vs RECORD/BOARD/fetches.
4. Trig claims: which formats, correct rounding, evidence
   shape vs RECORD.
5. Deferred/refused list vs SF-1 Sec.7 and SF-0 Sec.2.7 -
   anything omitted that reads as implemented, anything
   listed that is actually shipped.
6. Location table: every path exists and holds roughly what
   its cell says; studies dir contents; video status line vs
   `video/` state in the copy.

**Outputs:** `scratch/verifier-readme/report.md` (first line
`READY` or `NOT READY`; per-claim table: claim -> source ->
agree/disagree; findings with line refs; not-done list) and
`ledger/verifier-readme.md`. Structured
complete/evidence/unresolved.
