**Role:** parcel-w6metrics (seal: final metrics refresh)

**Base:** `cdc40aec9b11eeab61ab3c6cc9940b5dbbac4a67`, branch
`wave6-metrics`, worktree `worktrees/w6-metrics`. Work only there.
Modelled on `ledger/briefs/w5-metrics.md` — same discipline, new span.

**Deliverable:** `docs/metrics/{usage,passes,escalations,briefs}.jsonl`
brought current through the Wave 6 close (film v6 integration, music
docs, popup round: main `cdc40ae`). **Append-only:** never edit or
reorder an existing row; frozen rows are history (usage 93 rows /
passes 94 rows stop at Wave 5 close; escalations 20 rows stop at
Wave 5; briefs carries Wave 6 rows only for parcels that appended
their own).

**Governing:** `tools/extract_session_metrics.py` (the sanctioned
extractor — its header is the counting contract; read it before
running anything), the kit metrics shapes the existing rows carry,
`scratch/parcel-w5metrics/report.md` for the prior fold's method
and pitfalls.

**Work:**
1. Usage + passes: re-run the extractor over the Muse session
   stores for every agent session since the frozen rows. Enumerate
   the expected agent list FIRST from `ledger/briefs/` + git log +
   per-agent ledger files (Wave 6 parcels/verifiers/studies/fixers,
   the polish-audit + cleanup rounds between Wave 5 close and
   Wave 6, film studies and integrations, side studies), so
   coverage is auditable against a list, not whatever the store
   happens to retain. Annotations (--author-commit/--verdict)
   sourced from ledger/RECORD/git log ONLY; the extractor's
   refusals are features — satisfy them from records, never
   invent. Sessions the extractor cannot see (pruned/rotated)
   stay named in the report as not-reconstructed, never guessed.
   Wave labels in the existing idiom ("wave6").
2. Totals reconciliation: state the refreshed billed/input/output
   token totals at your cutoff and reconcile against the prior
   authority (1,196,128,770 billed at the tokens-study span; the
   film's outro card carries that figure as of its freeze — your
   refresh supersedes it in docs, the film does not change).
   Differences must be explained by span in numbers; anything
   else is a finding.
3. Escalations: append Wave 6 rows only if reconstructable from
   ledger files with citable sources (same field shape). If none
   are sourceable, say so in the report with what you searched;
   never guess a row.
4. Briefs: audit the full Wave 6 (and polish-round) parcel/study
   list against `docs/metrics/briefs.jsonl` + `ledger/briefs/`
   and append every missing row you can source; your own row last.
5. Anything the refresh exposes as wrong in EXISTING rows:
   report it, do not edit (append-only).

**Fences:** session logs read for counting/annotations only (no
owner-text quoting beyond role labels); never open/search/list
anything with `cft` in its name; do not open `docs/metrics/
plants.jsonl` (not your file); stream large logs with explicit
memory ceilings; light-moderate load. Owned files:
`docs/metrics/{usage,passes,escalations,briefs}.jsonl` only.
Extractor/tool changes escalate to the report, never edit tools.
Commits with detailed bodies + Co-Authored-By trailer. Never
push/merge.

**Acceptance:** (a) per-file rows before/after with spans and the
expected-vs-found agent coverage table; (b) totals reconciliation
per (2); (c) every appended row's annotation sources cited;
(d) not-reconstructed list; (e) frozen-prefix proof: each file's
bytes before your append are an exact prefix after (hash or cmp);
(f) `tools/run.sh standard` PASS unchanged in the worktree;
(g) diff vs base limited to owned files.

**Outputs:** tip commit(s) on `wave6-metrics`;
`scratch/parcel-w6metrics/report.md` + `ledger/parcel-w6metrics.md`.
Structured complete/evidence/unresolved mandatory. Script files,
Git Bash, MSF_PYTHON pinned. ~480 min.
