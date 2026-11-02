**Role:** regater-f64 (close the binary64 Wave 1 parcel after the lead fixes)

**Situation:** parcel-f64 implemented all 173 instantiations at
checkpoint commit `5153324` on branch `w1-f64` in
`worktrees/w1-f64`, then correctly stopped NOT READY on three
lead-owned items: pack tininess definition, ingest `eq` row, and
smoke control 9 naming a now-implemented op. All three are fixed
and pushed on main at `b37fb12` (via `53acb1a`), Spark-READY with
an oracle differential (scratch/rechecker-tininess/). The parcel's
full report is `scratch/parcel-f64/report.md` - read it first; its
PENDING-POSTMERGE marks are your work list. The original brief is
`ledger/briefs/w1-f64.md`; you inherit its owned files and
ceilings (120 fresh minutes; hand-written total currently
1,780/3,000). Commits end `Co-Authored-By: Muse Code
(muse-wonder-full-1.0) <noreply@meta.ai>`; never push.

**Work, in order:**
1. In `worktrees/w1-f64`: `git merge b37fb12` (or main). Expected
   conflicts only in generated files and `tables/implemented.tsv`
   (main LF-normalised it): resolve implemented.tsv as the union
   of rows with LF endings; resolve generated files by re-running
   `tools/gen_tables.py` and committing its output. Any other
   conflict: escalate.
2. The parcel already restated its generator's pack reference to
   unbounded-rounded tininess (report test group 3); verify that
   restatement is what the committed `tests/gen_vectors_f64.py`
   contains, regenerate the directed files if they change, and
   re-run both seeded sweeps (0xF64, 0xC0FFEE) and the misc sweep.
   The one pre-fix directed failure (arith-f64.vec:1824) must now
   pass.
3. Re-run every blocked Berkeley case with the fixed kernel and
   ingest (mul/div te,tp,tn,ta level 1 + mul te level 2 slice,
   mulAdd te,tp,tn,ta, f64_eq as ingested). Set
   MSF_TESTFLOAT_GEN explicitly. All must pass complete; classify
   any failure before proceeding. The f64_to_f32 skips stay named
   skips (sibling parcel's rows).
4. Final rerun of the four negative controls
   (scratch/parcel-f64/run-controls.sh) post-merge.
5. `tools/run.sh smoke` and `standard` green in the worktree
   (control 9 now names msf16_add).
6. Restate scratch/parcel-f64/report.md's PENDING-POSTMERGE
   sections with measured outcomes and a final verdict; commit in
   the worktree (subject naming the re-gate, body with counts);
   ledger entry in `ledger/parcel-f64.md` via kit ledger.sh
   script file (stage the body in scratch/parcel-f64/ if the tool
   refuses in your sandbox).

Scratch: `scratch/parcel-f64/` (existing). Escalate real questions
via `ledger/urgent/` files (`For: lead`). READY means every
numbered item above is green with counts in the report; anything
less is NOT READY with the gaps named.
