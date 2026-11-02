**Role:** verifier-w6ci (ParcelRound verifier, Linux CI parcel)

**Stance:** disconfirm only. Findings: a CI job that does not
run what it claims, a portability edit that changes what the
gate checks, a green path that can lie.

**Copy:** `worktrees/verify6-ci` (detached HEAD, parent
`50aac59`). Never consult the parcel branch/worktree, other
worktrees, keys, `scratch/lead/`, `scratch/parcel-w6ci/`, or
`ledger/lead.md`; never consult GitHub run history for the
real branch (your evidence is the copy plus your own runs).
Authorities: this brief, `ledger/parcel-w6ci.md`, the copy's
tree. **Fence by name: `docs/metrics/plants.jsonl` must not
be opened, read, grepped, or cited by you, in the copy or
anywhere.** Nothing with `cft` in its name. Never modify the
copy; run gates in a duplicate under your own scratch. Do
not push anything.

**Required probes:**
1. ci.yml line by line against its own header claims: both
   jobs' runner OS, the exact budget each job's run step
   invokes, toolchain installs vs inventory step (a missing
   tool must fail the job loudly, not skip a scan),
   triggers, artifact uploads on failure. YAML must parse.
2. run.sh diff vs parent: every hunk re-derived for Windows
   AND Linux semantics. For awk last-field handling, prove
   behaviour with a binary-mode demonstration (gawk
   BINMODE=3 or equivalent) on the real CRLF vector/tree
   inputs: the wrong-nan mutant must differ from its input
   in exactly the flipped field, and expect-count tags must
   carry no CR, on the Linux channel as well as Windows.
3. Gate: `tools/run.sh standard` in your duplicate PASSes
   with every negative control refused by name and totals
   411,213 + 1,117,504; normalized verdict surface unchanged
   vs the parent where the parcel claims byte-identical.
4. Any inventory/assumption list in the parcel ledger:
   re-derive the entries you can from the copy (compiler
   refusal shapes, skip-by-name paths) and flag any entry
   the tree contradicts.

**Outputs:** `scratch/verifier-w6ci/report.md` (READY/NOT
READY; findings F1..Fn with file:line; probes; not-done) +
`ledger/verifier-w6ci.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv. ~300 min.
