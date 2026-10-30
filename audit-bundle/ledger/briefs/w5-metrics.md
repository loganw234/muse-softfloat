**Role:** parcel-w5metrics (Wave 5 close: metrics refresh)

**Deliverable:** `docs/metrics/{usage,passes,escalations,
briefs}.jsonl` brought current through SF-2 close
(Step 4 merged `4a0b0d4`, plants `7d0ed81`), merge-ready
on branch `wave5-metrics` (worktree
`worktrees/w5-metrics`, cut by the lead from `5142594`).
**Append-only:** never edit or reorder an existing row;
frozen rows are history (usage/passes stop at Wave 3,
escalations at Wave 3, confirmed by study-tokens-visual).

**Governing:** `tools/extract_session_metrics.py` (the
sanctioned extractor - its header is the counting
contract), `scratch/audit-adherence-2/report.md` (the
slips list this close must answer), the kit metrics
shapes the existing rows carry.

**Work:**
1. Usage + passes: re-run the extractor over the Muse
   session stores for every agent session since the
   frozen rows (Waves 4-5 parcels, verifiers, studies,
   side parcels: trig, kissfft, interval, attr, alg1/2,
   exp2 incl. its dead first verifier, log2, aug x3
   attempts, site, demo, twiddledoc + fix, the two
   visual studies, audits). Annotations
   (--author-commit/--verdict) sourced from ledger/
   RECORD/git log ONLY; the extractor's refusals are
   features - satisfy them from records, never invent.
   Wave labels in the existing idiom. Sessions the
   extractor cannot see (pruned) stay named as such in
   your report, not reconstructed.
2. Cross-check your totals against
   `scratch/study-tokens-visual/data/tokens.json`
   (their span ends 2026-10-28T20:07; yours runs later -
   reconcile the difference by span, in numbers).
   Their method validated byte-identical on one
   session; disagreements beyond span are findings.
3. Escalations: append Wave 4-5 rows reconstructed from
   ledger files (parcel/verifier ledgers carry the
   escalations; lead answers in commits/ledger). Every
   row needs a citable source; anything you cannot
   source goes in the report as not-reconstructed,
   never guessed. Same field shape as existing rows.
4. Briefs: append missing rows (at minimum
   parcel-w5exp2, named missing by parcel-w5log2;
   audit the full wave4/5 parcel list against
   docs/metrics/briefs.jsonl + ledger/briefs/ and fill
   every gap you can source; your own row last).
5. Anything the refresh exposes as wrong in EXISTING
   rows: report it, do not edit (append-only).

**Fences:** session logs read for counting/annotations
only (no owner-text quoting beyond role labels);
never open/search/list anything with `cft` in its name;
stream large logs, ulimit ceilings; light-moderate load.
Owned files: `docs/metrics/{usage,passes,escalations,
briefs}.jsonl` only (+ your briefs row). Tools changes
escalate. Commits with detailed bodies + Co-Authored-By
trailer. Never push/merge.

**Report:** `scratch/parcel-w5metrics/report.md` (READY/
NOT READY; per-file rows before/after + spans; totals
reconciliation vs the tokens study; annotation sources;
not-reconstructed list; frozen-row errors found if any)
+ `ledger/parcel-w5metrics.md`. Script files, Git Bash,
MSF_PYTHON pinned. ~480 min.
