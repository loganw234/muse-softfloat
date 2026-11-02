**Role:** verifier-w5log2 (ParcelRound verifier, SF-2 Step 3b)

**Stance:** disconfirm only. Findings: (a) one wrong
result or flag in any mode/format, (b) a proof artefact
that does not re-derive (tables/generator/vectors drift),
(c) a claim the evidence does not carry.

**Copy:** `worktrees/verify5-log2` (detached HEAD, parent
`54ac1bb`). Never consult the parcel branch/worktree,
other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5log2/`, or `ledger/lead.md`.
Authorities: this brief, `ledger/parcel-w5log2.md`, the
copy's `docs/studies/SF-2.md` Secs. 1,4,6-9, IEEE Clause
9.2 extracts the ledger cites, and your own decider.
Nothing with `cft` in its name. Never modify the copy
(build/probe outside it; keep `git status` clean).

**Required probes:**
1. Own MPFR decider (adaptive precision, recipe
   cross-checked on known cells; raw RNDNA prohibited).
   One-cell + families: powers of two (incl. subnormal
   x), recentring boundary neighbourhood (mm near
   sqrt(2)), log2p1 pole -1 and its flag, tiny-|x|
   relative path, +-0, negatives, NaN/inf, all 6 ops x
   5 modes.
2. Exhaustive legs: binary16 exhaustive (all 4
   explog fns or at least the log pair - state which);
   binary32: the shard claim (256 shards, 2^32 x 2fn x
   5 modes) - re-add the arithmetic from what the copy
   carries, run sampled shards yourself ( contiguous
   ranges, counts printed), and state plainly that full
   re-exhaustion was not re-executed if so;
   final_undecided must be 0 in everything you run.
3. Regen stops: `tools/gen_explog_tables.py` and
   `tests/gen_vectors_explog.py` re-run - committed
   tables/vectors must be byte-stable (run twice);
   committed EK values vs what the generator proves;
   Step-3a exp lines byte-prefix preserved.
4. Seam: inventory claims (Tier 2 57/57), gen_tables
   drift, operations/implemented/COVERAGE rows vs the
   header/API surface; claim surface vs parent.
5. Full runner over committed vectors; `standard`
   extras if cheap; target compile -Os AND -O3 clean.
6. Negative-control sanity: at least two parcel-claimed
   controls re-run in spirit (a 1-ulp mutant and one
   named NC) must actually bite, or say they don't.

**Outputs:** `scratch/verifier-w5log2/report.md` (first
line READY/NOT READY; per-probe evidence file:line;
findings; not-done) and `ledger/verifier-w5log2.md`.
Structured complete/evidence/unresolved - submitting it
is mandatory. Script files only (Git Bash, MSF_PYTHON
pinned), explicit memory ceilings (ulimit -v), moderate
load. Timebox ~600 min.
