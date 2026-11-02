**Role:** fixer-w6popups (lead send-back on parcel-w6popups, two card counts)

**Base:** parcel tip `0708e2e` on branch `wave6-popups`,
worktree `worktrees/w6-popups`. Add ONE fixer commit on the same
branch. Parcel brief: `ledger/briefs/w6-popups.md`; parcel report:
`scratch/parcel-w6popups/report.md`. Everything else in the parcel
stands (timing freeze held, stills clean, standard PASS).

**Lead findings (the only changes wanted):**

1. **PARCELS count 20 -> 19.** The 20th "author" pass is the lead's
   own wave0 spine episode (process_graph `accounting.by_role.author
   = 19` lanes; `by_passes_role.author = 20` includes the spine,
   agent `lead`). The spine is not a parcel and the replay draws 19
   parcel lanes. Card must read "19 parcels total" (same token
   count; budget 7 unchanged).
2. **ESCALATIONS count/description mismatch.** Line 1 "questions go
   up to lead" describes escalation *filings*; `docs/metrics/
   escalations.jsonl` has **20** filings (waves 1-5, all inside the
   frozen window), while "3 escalations total" counts fixer lanes.
   Align them inside the 9-token budget. Lead's preferred fit:
   title `ESCALATIONS`, line1 "questions go to lead" (4), line2
   "20 filed, 3 fixes" (4) = 9. An equally honest fit of the same
   budget is acceptable if your report justifies it against the
   file; what may not stand is a filings description over a
   fixer count (or vice versa).

**Constraints:** all parcel-brief hard fences still apply —
per-card `POPUP_WORDS` identical (re-prove the timing-constant
equality dump against base `f01dc96`), diff limited to
`video/segments/gitvisual.py` POPUP5 strings, regenerated
`gitvisual7.mp4`, and restating the parcel's own
`docs/metrics/briefs.jsonl` row numbers in place (branch is
unpushed; restate, don't append a second row). No assembly, no
audio, no other copy changes.

**Acceptance:** (a) before/after copy for the two cards with the
recounts quoted (process_graph by_role; escalations.jsonl row
count by wave); (b) timing-equality dump identical to base;
(c) regenerated mp4 probed 108.0 s 2560x1440@30 silent + stills
of the two changed cards viewed; (d) restated report sections in
`scratch/parcel-w6popups/report.md` (append a fixer section) and
`ledger/parcel-w6popups.md`; (e) `tools/run.sh standard` not
required to re-run (diff is copy-strings only vs the parcel's
passing run — state that).

**Outputs:** one fixer commit on `wave6-popups`, detailed body +
`Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>`. Structured complete/evidence/unresolved.
Script files, Git Bash, MSF_PYTHON = workspace .venv. Nothing
with `cft` in its name. ~120 min.
