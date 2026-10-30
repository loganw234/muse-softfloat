**Role:** verifier-sf2 (ParcelRound verifier, SF-2 draft)

**Stance:** disconfirm only. Findings (a) an SF-2 claim the
input studies or the repo contradict, (b) an internal
inconsistency (counts, sequencing, a stop rule that cannot
bind), (c) a load-bearing item the studies priced or fenced
that SF-2 silently drops. Wording taste is not a finding.

**Copy:** `worktrees/verify-sf2` (detached HEAD, parent
`3a12b71`). Object: `docs/studies/SF-2.md` as delivered
there. Authorities you may read: the four input studies
(`scratch/sf2-{attribute,algebraic,explog,augmented}/
report.md`), the copy's repo (`docs/studies/SF-0.md`,
`SF-1.md`, `docs/COVERAGE.tsv`, `docs/RECORD.md`, `src/`,
`tables/`, `tests/`, `tools/run.sh`), and this brief.
Never consult the delivery branch/worktree
(`worktrees/lead-sf2`), other worktrees, keys,
`scratch/lead/`, or `ledger/` other than writing your own
ledger file. Nothing with `cft` in its name, ever. Never
modify the copy.

**Required probes (counts/claims each; skips named):**
1. Arithmetic: step row counts, closure total, price sums
   vs the studies' own tables (recompute; name deltas).
2. Every measured number SF-2 cites (op counts, case
   volumes, margins, widths) traced to its study table -
   a number with no source, or a source that says
   otherwise, is a finding.
3. Code-state claims (internal modes, string-path trap,
   seam needs) checked against the copy's `src/` directly.
4. Decision fidelity: SF-2 Sec. 9 vs SF-1 Sec. 7 deferrals
   and the studies' verdicts - anything SF-2 authorises
   that its study refused, or fences it forgot (F1/H1,
   rSqrt(-0), stop conditions), is a finding.
5. Sequencing: can each step's brief actually be written
   from SF-2 + its study without inventing a pin? List
   every under-specified point that would force a parcel
   to guess (name them as notes, not blockers, unless the
   guess changes semantics).
6. Refusals/deferrals list vs SF-1 Sec. 7 + study NO-GOs:
   nothing silently promoted, nothing silently dropped.

**Outputs:** `scratch/verifier-sf2/report.md` (first line
`PASS` or `FAIL`; findings with SF-2 section refs and the
contradicting source; under-specification list; not-done
list) and `ledger/verifier-sf2.md`. Structured
complete/evidence/unresolved.
