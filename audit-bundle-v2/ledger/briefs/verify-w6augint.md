**Role:** verifier-w6augint (ParcelRound verifier, augmented stage 3)

**Stance:** disconfirm only. Findings: a classification that
differs from the base implementation, an exactness guard that
does not guard, a build that does not link.

**Copy:** `worktrees/verify6-augint` (detached HEAD, parent
`50aac59`). Never consult the parcel branch/worktree, other
worktrees, keys, `scratch/lead/`, `scratch/parcel-w6augint/`,
or `ledger/lead.md`. Authorities: this brief,
`ledger/parcel-w6augint.md`, the copy's tree itself (the
parent commit in the copy is your base-implementation oracle).
**Fence by name: `docs/metrics/plants.jsonl` must not be
opened, read, grepped, or cited by you, in the copy or
anywhere.** Nothing with `cft` in its name. Never modify the
copy; build in a duplicate under your own scratch. Board is
lead-only - do not flash anything.

**Required probes:**
1. Full-stream differential: build interval_host from the
   copy and from the parent tree (in your duplicate), run
   both over the full `tests/interval_catalogue.tsv`, diff
   the complete result streams field by field. Every
   classification must be identical; only stage-3 ops counts
   (and hashes through them) may move. Report both hashes.
2. Exactness: independently check the stage-3 expansion
   sums against an exact oracle (Python Fractions/integers
   over dumped terms or your own exact discriminant) on a
   stated subset that includes the guard rows and
   near-tangent rows; decided rows must never be wrong.
3. Guard semantics by code reading against
   `ledger/parcel-w6augint.md`: which flag bits trip, what an
   exact tiny residual does (P1=R2), what a non-finite pair
   member does. Any mismatch between the header comment,
   the code, and the design entry is a finding.
4. Each primitive by reading: aug_sum/aug_prod must consume
   head/tail in the right order and call the right augmented
   operation; call sites must match.
5. Builds: the board/interval_run.sh host build line and the
   demo SRC list must actually link the new workload (run
   the host build exactly as those files spell it, in your
   duplicate); ARM compile-only of the workload objects.
6. Claim discipline: ops deltas in the parcel report are
   records from the workload counter - recount them from
   your own runs; no performance framing anywhere changed.

**Outputs:** `scratch/verifier-w6augint/report.md` (READY/NOT
READY; findings F1..Fn with file:line; probes; not-done) +
`ledger/verifier-w6augint.md`. Structured
complete/evidence/unresolved mandatory, evidence carries
finding ids. Script files, Git Bash, MSF_PYTHON pinned to
workspace .venv, memory modest. ~360 min.
