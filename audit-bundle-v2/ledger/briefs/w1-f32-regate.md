**Role:** regater-f32 (close the binary32 Wave 1 parcel after the lead kernel fix)

**Situation:** parcel-f32 implemented all 173 instantiations at
checkpoint commit `6c1bc01` on branch `w1-f32` in
`worktrees/w1-f32`, then correctly stopped: its only Berkeley
failures were two lead-owned defects (pack tininess definition,
ingest `eq` row), escalated and ruled in `ledger/lead.md`. The lead
fixes are pushed on main at `b37fb12` (via `53acb1a`), Spark-READY
including an oracle differential (scratch/rechecker-tininess/).
The parcel's full report is `scratch/parcel-f32/report.md` - read it
first; its "Post-fix re-gate" section lists what you must fill. The
original brief is `ledger/briefs/w1-f32.md`; you inherit its owned
files, ceilings (you get 120 fresh minutes; the hand-written line
ceiling applies to the parcel total, currently 1,785/3,000), and
clean-room rules. You are the parcel author for the re-gate: commits
end `Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>`;
never push.

**Work, in order:**
1. In `worktrees/w1-f32`: `git merge b37fb12` (or main). Expected
   conflicts only in generated files and `tables/implemented.tsv`
   (main LF-normalised it; the parcel appended CRLF rows): resolve
   implemented.tsv as the union of rows, LF endings; resolve
   generated files by re-running `tools/gen_tables.py` after the
   merge and committing its output. Any other conflict: escalate.
2. Restate `pack_mag` in `tests/gen_vectors_f32.py` to the
   unbounded-rounded tininess (judge the p-bit rounding at the
   value's own binade against 2^emin, per the ruling); the parcel
   pre-validated this restatement in scratch (probe_patched.py,
   bad=0 over Berkeley mul/div level 1). Regenerate the committed
   directed files and the seeded sweeps; replay all.
3. Re-run the blocked Berkeley counts with the fixed ingest
   (mul/div all modes incl. level-2 te slices, mulAdd all modes,
   f32_eq as ingested, plus f32_eq_signaling as the extra job the
   report offered). Set MSF_TESTFLOAT_GEN explicitly. Every job
   must pass complete; classify any failure before proceeding.
4. Re-demonstrate the four negative controls (item 4 of the
   report), including the wrong-tininess build failing the
   complementary boundary subset.
5. `tools/run.sh smoke` and `standard` green in the worktree
   (control 9 now names msf16_add).
6. Complete scratch/parcel-f32/report.md's post-fix section and
   verdict; commit in the worktree (subject naming the re-gate,
   body with counts); ledger entry in `ledger/parcel-f32.md` via
   kit ledger.sh script file (stage the body in
   scratch/parcel-f32/ if the tool refuses in your sandbox).

Scratch: `scratch/parcel-f32/` (existing). First action: a one-line
start note appended via your first ledger entry attempt is not
needed - the channel is already proven; escalate real questions via
`ledger/urgent/` files (`For: lead`). READY means every numbered
item above is green with counts in the report; anything less is
NOT READY with the gaps named.
