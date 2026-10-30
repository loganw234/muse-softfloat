#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
git add tools/run.sh
git commit -m "Wired the binary32 directed sets into the smoke budget" -m "The six parcel-f32 directed files (11,129 cases) join the fixed smoke vector list, as the parcel report left for the lead at merge. Standard PASS at the f32 merge before this wiring; re-run after.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>"
echo wire_rc=$?
git merge --no-ff w1-f64 -m "Merged Wave 1 binary64 parcel (173 instantiations, READY cb10ee2)" -m "Parcel-f64 implemented all 173 msf64_ wave-1 instantiations at 5153324, independently proved the ingest eq defect (46,464-case quiet-remap), and regater-f64 closed it at cb10ee2 after the lead fixes: blocked Berkeley re-run 10,418,176 PASS, project-exact 491,057 replayed, controls re-demonstrated (directed set gained four second-shape tininess cases so all three definitions are discriminated). Evidence: scratch/parcel-f64/report.md, ledger/parcel-f64.md. Conflicts in tables/implemented.tsv and generated files are resolved by union + regeneration in the follow-up; standard re-run at this merge before it counts.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>"
echo merge_rc=$?
git status --short | head -20
