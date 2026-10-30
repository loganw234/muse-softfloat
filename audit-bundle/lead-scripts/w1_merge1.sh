#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
git add docs/metrics/briefs.jsonl
git commit -m "Recorded the Wave 1 briefs in the metrics inputs" -m "Two rows (parcel-f32, parcel-f64; base 4cdb912, 300-minute boxes, 3,000-line ceilings) matching ledger/briefs/w1-f32.md and w1-f64.md. Folded in at merge time per the dispatch record, so no unverified lead commit moved main during the wave.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>"
echo briefs_rc=$?
git merge --no-ff w1-f32 -m "Merged Wave 1 binary32 parcel (173 instantiations, READY 26c76aa)" -m "Parcel-f32 implemented all 173 msf32_ wave-1 instantiations at 6c1bc01, escalated the shared pack-tininess and ingest-eq defects instead of editing around them, and regater-f32 closed it at 26c76aa after the lead fixes (53acb1a, b37fb12): Berkeley 27,305,248 cases PASS complete, project-exact 371,729 replayed, 4/4 controls, smoke+standard green in the worktree. Evidence: scratch/parcel-f32/report.md, ledger/parcel-f32.md. Standard re-run at this merge by the lead before it counts.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>"
echo merge_rc=$?
git log --format='%h %s' -4
git status --short | head
