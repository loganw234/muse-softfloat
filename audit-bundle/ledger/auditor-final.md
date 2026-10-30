
## 2026-10-27 - Final adherence audit filed: Wave 3 held, IAS15 proven, video verified; 1 SEV-2 + 2 SEV-3 + 4 SEV-4 findings

Final method audit complete (disconfirm-only): verify-then-merge HELD wave 3
(merge 1357863 35 s after 5/5 grading, verifier done ~30 min prior; ias15
merge 40 s after the silicon proof); grading followed the verdict this wave;
plant totals re-derived 24/25 with all five key hashes matching sha256sum;
merge-tree re-make independently re-run (4/6 identical, 2 conflict merges
union-clean 0 missing/0 extra); origin/main == d1bfe38 corroborates the
final push; GPL boundary clean (zero cft mentions in history/tree, tables
header is data-only with provenance); 783/783 mechanically confirmed
(COVERAGE.tsv header + 783 rows); final.mp4 independently probed (180.0 s,
single h264 stream = silent, 1920x1080@30) with 5 stills' numbers traced to
sources; MUSIC.md licence-clean, nothing downloaded. Divergences,
severity-ordered: (1) SEV-2: this ledger's 11:09:14 "video-final metrics
fold in this step" is false — metrics JSONL untouched since 10:34, no
video-final/auditor-final rows; restatement + fold or deferral owed.
(2) SEV-3: metrics-w3 ceiling table counts generated vectors against an
exclusionary ceiling (11,611 vs 3,500; true hand-written 2,156 compliant).
(3) SEV-3: parcel-str's 3 brief faults have no corrections.jsonl rows.
(4-7) SEV-4s: 4ceffa9/cc71d73 precede their announcing entries by 3 s/19 s
(pre-rule, self-disclosing); verifier-w3str.md lacks timestamp/shape/
provenance (w2xf provenance still open); merge-log paths uncited third wave
running; no verifier/video brief rows in briefs.jsonl (standing pattern).
Owner-owed: fingerprint audit, music/VO, retrospective tooling-scope
decision. Full report: scratch/audit-final/report.md.

Measured: kit WORKFLOW/ROLES/METRICS/PROJECT/OWNER/CLEAN-ROOM/AGENTS read
(targeted lines); lead.md 08:20:23-11:09:14, parcel-str + ias15-pico ledgers
whole, verifier-w3str + video-final + auditor-wave2 ledger entries, all four
Wave-3 briefs, all Wave-3 urgent files, all four Wave-3 scratch reports,
RECORD all entries, COVERAGE.tsv (783 data rows), all eight metrics JSONL,
metrics-w3-final.md, git log/show/ls-files/merge-tree over 548a1b9..d1bfe38
(14 commits), video/out/final.mp4 + 5 stills viewed, MUSIC.md,
hashes_native.txt steps 0/2000 read, board tables/provenance scan; key
hashes only, nothing cft-named opened.
Believed: nothing material beyond the 7 falsifiable findings in the report;
Wave-2 items closed except the owner-owed three carried above.
For: lead
