# Audit-final: Wave 3 + IAS15-pico + video-final method adherence (disconfirm-only)

Auditor: auditor-final (Spark). Kit: softfloat-bootstrap-kit v1 (frozen;
MANIFEST sha `37d2139240af` cited identically in metrics-w1/w2/w3-final.md;
kit file dates 1980-01-01, unmodified). Method read: WORKFLOW.md, ROLES.md,
METRICS.md, PROJECT.md, OWNER.md, CLEAN-ROOM.md, AGENTS.md (targeted lines
re-grounded: OWNER "a sentence that claims more than is true is restated at
the merge"; WORKFLOW merge-tree step, reveal "when every verifier ... has
reported", "keys are revealed once, near the end"; CLEAN-ROOM "Logan checks
... at each wave's close and at the end").
Project record read in full: ledger/lead.md 08:20:23-11:09:14, ledger/
parcel-str.md, ledger/ias15-pico.md (both, whole), ledger/verifier-w3str.md,
ledger/video-final.md, ledger/auditor-wave2.md, ledger/briefs/{w3-str,
ias15-pico,verify-w3str,video-final}.md, ledger/urgent/* (Wave-3 four),
scratch/parcel-str/report.md, scratch/ias15/pico-report.md,
scratch/verifier-w3str/report.md, scratch/video/final-report.md,
muse-softfloat/docs/RECORD.md (all entries, esp. Wave 3 + erratum),
muse-softfloat/docs/COVERAGE.tsv, docs/metrics/*.jsonl (all eight),
scratch/lead/metrics-w3-final.md, scratch/lead/entry-*.md + append_*.sh +
mergetree_check.sh + check_plants_w3.sh, git log/show/ls-files/merge-tree in
muse-softfloat (all 14 commits 548a1b9..d1bfe38), video/out/final.mp4
(probed), video/out/stills/ (5 of 12 viewed: 034.5/102.0/120.0/141.5/160.0),
video/MUSIC.md, scratch/ias15/out/hashes_native.txt (step 0/2000 read),
board/ias15_tables.h + api/main/hash (provenance + GPL-marker scan).
Keys: sha256 only (`sha256sum` of scratch/lead/keys/*.json); contents never
opened. Nothing cft-named opened, searched, or listed (history scan:
`git log --all -- '*cft*'` empty, `grep -ci cft` over log = 0).

## 1. Wave 3 + IAS15-pico + video-final verdicts

1. Verify-then-merge — ADHERED. Parcel tips 945217c/8712ec1 (09:02:58) sat
   in branch w3-str while planted-copy verifier-w3str reported (~10:26
   report mtime; ledger entry undated, see finding F5); grading 10:28:21,
   merge 1357863 10:28:56. ias15 merge d9718cf 09:45:02 follows the silicon
   proof entry 09:44:26 by 40 s. No planted-copy verification existed for
   ias15-pico (same method gap as wave-2 finding 2, carried): substituted
   host gates A-C + on-silicon hash identity, disclosed in the merge body.
2. Briefs / boxes / ceilings — ADHERED as run, with two metrics-recording
   faults (findings F2, F3). w3-str + ias15-pico + verify-w3str +
   video-final briefs exist as files with owned/forbidden lists, negative
   controls, READY defs, what-got-wrong sections. Active times: parcel-str
   ~35/360 min, ias15-pico ~33/360, video-final ~31/300; no checkpoint
   reached anywhere. Hand-written: parcel-str 2,156/3,500, vectors 896,090
   B/1 MB; ias15-pico 1,506 changed/3,500 (metrics-w3 table). Off-limits
   held: runner wiring escalated twice, lead-fixed on main (f3c48b8,
   83622cf); parcel never touched tools//board//docs/.
3. Escalations — ADHERED. 5 wave-3 rows (2 channel tests + design rulings +
   2 runner bugs + video test counted in urgent/ though post-metrics, see
   F1): rulings answered in ~2 min (08:28:15->08:30:16), runner fixes in
   12-16 min with same-step ledger entries. Urgent files retained (4 wave-3
   files present in ledger/urgent/).
4. Verifier independence — ADHERED on evidence. Fresh exact-rational
   reference (vw_ref.py, "no generator imports"), MPFR within-H
   triangulation 1,146/1,146 + 1,084/1,084, 400k fuzz + 262,144-line
   exhaustive sweep, fault isolation to 3 one-line causes with fixed-TU
   collapse to zero, copy never modified. Beyond-H judged against the
   literal two-step reference per the brief — the exact norm the Wave-1
   miss shape required.
5. Plant grading — ADHERED, 5/5. plants.jsonl rows 21-25 all wave3, key
   `63fe450a...` matching `sha256sum scratch/lead/keys/key-f58f299.json`
   (ledgered pre-dispatch 09:08:19). Grading 10:28:21 came AFTER the
   verifier reported (~10:26) — the sequencing that waves 1-2 got wrong is
   right this wave. Keys confined to scratch/lead/keys/ (drafts beside
   finals, finals only referenced). 24/25 re-derived: 9/10 + 10/10 + 5/5.
6. Clean-room / GPL — ADHERED. No REBOUND-derived file entered
   muse-softfloat in any commit: `git log --all --diff-filter=A --
   '*rebound*' '*ias15*'` shows only the board-glue commit adding OUR
   files; `ls-files` has no rebound/extract/cft names; no GPL license text
   in repo; board/ias15_tables.h carries only hex bit-pattern data with a
   generator+source-hash provenance comment (the constants provenance claim
   holds: data, not code). Zero cft mentions in history or tree.
7. Video-final — ADHERED. final.mp4 independently probed with the bundled
   ffmpeg 7.1: Duration 00:03:00.00, ONE stream (video only = silent),
   h264 High yuv420p 1920x1080 30 fps; size 17,014,776 B matches report +
   lead entry. 12 stills present; 5 viewed, each with on-screen source
   caption. Spot-checks: 783/783 (COVERAGE.tsv: 784 non-blank non-#
   lines = header + 783 data rows); 37M+ / 6.1M x5 / 65,536 (RECORD
   Wave-1/2 lines as cited); board hash full 64-hex on screen identical to
   RECORD Wave-2 line; sample scope stated on-frame ("a sample, said
   plainly"); 944-step period + time-lapse + ILLUSTRATION label on the
   orbit frame; step-0 `62bb23b0...333e01` / step-2000 `4d4530a6...f48abb`
   digests read by this audit directly from hashes_native.txt (2001 data
   records) — match. MUSIC.md: 3 named-licence options (CC BY 4.0,
   Pixabay Content License, ccMixter CC-BY-only) + ruled-out FreePD, no
   audio downloaded, re-verify-at-download caveat — no unlicensed claim.
8. RECORD/README claims — ADHERED as checked. 783/783, 24/25, 85,148 +
   1,117,504 (re-printed at Wave-3 close, lead 10:32:42), board hash
   prefix, 47,107 AEABI, 2,001/2,001, 1.58 steps/s @125 MHz, UF2 prefixes —
   all trace to ledger/board/report sources read this pass. README status
   restated at d1bfe38.

## 2. Wave-2 audit items — closed one by one

W2-1 (SEV-1, false "same-step" sentence) — CLOSED. Erratum appended at
RECORD:503-505 by 4ceffa9, false sentence stands in history + appendix =
exactly OWNER rule 1 ("restated at the merge, not left standing").
W2-2 (unbriefed ias15-port/video-tools, owner decision) — HALF-OPEN. New
work this wave properly briefed (w3-str, ias15-pico, verify-w3str,
video-final as files); the retrospective owner decision scoping Wave-2
tooling work in or out is still nowhere recorded (see F8).
W2-3 (merge-tree re-make) — CLOSED. Lead entry 10:36:44 + script
scratch/lead/mergetree_check.sh; mechanically re-run by this audit:
a05412f/d9718cf/1357863/2843792 IDENTICAL; 71fbd53/06fdec8 differ exactly
as conflict-resolutions must — union verified directly: 0 missing, 0 extra
both (772/410 sets). Lead's false-start disclosure (MSYS git-less "pass")
is honestly recorded, not evidence.
W2-4 (merge-time log paths) — OPEN, downgraded (see F6).
W2-5 (owner fingerprint audit) — OPEN (see F8).
W2-6 (early grading) — CLOSED this wave: grading followed the verdict.
W2-7 (verifier-w2xf append provenance) — OPEN (see F5).
W2-8 (Wave-1 urgent files) — CLOSED as unrecoverable; Wave-3 urgent files
retained (4/4 present).
Wave-2 push — CLOSED: 08:24:22 entry cites ls-remote 548a1b9...; origin/main
now at descendant d1bfe38, consistent. Final push CLOSED: 10:36:03 entry
claims ls-remote d1bfe38; locally corroborated (origin/main == d1bfe38...,
HEAD -> main).
Same-step rule over 548a1b9..d1bfe38 (14 commits) — HELD with disclosed
edges (see F4).

## 3. Severity-ordered falsifiable findings (one per line)

1. SEV-2: Lead ledger 11:09:14 claims "video-final brief row + usage/passes
   fold in this step" — false: docs/metrics/*.jsonl unmodified since
   10:34, zero video-final rows in passes/usage/briefs, zero auditor-final
   rows anywhere; same false-sentence class as wave-2 SEV-1, owes
   restatement + the actual fold or an explicit deferral.
2. SEV-3: metrics-w3-final.md ceiling table scores parcel-str 11,611 lines
   vs the 3,500 ceiling ("3.3 times") by counting generated vector files the
   quoted ceiling text explicitly excludes; hand-written 2,156 is compliant
   — measurement-definition bug in the metrics artifact, RECORD does not
   repeat it.
3. SEV-3: parcel-str report's 3-item "What this brief got wrong" has zero
   corrections.jsonl rows, violating METRICS.md "each report's 'what this
   brief got wrong', counted" (metrics-w3 corrections table covers only the
   ias15-pico brief); the parcel ledger also lacks the brief-mandated
   ledger section (lives only in the scratch report).
4. SEV-4: commits 4ceffa9 (08:24:19) and cc71d73 (08:20:04) precede their
   announcing ledger entries (08:24:22 rule-creating entry; 08:20:23
   dispatch) by 3 s and 19 s — pre-rule and self-disclosing, but the rule's
   letter ("no commit before its ledger entry") postdates them; merges
   d9718cf/d1bfe38 share their entry's exact second (order unresolvable,
   consistent); all other 10 commits have a prior same-step entry (1 s to
   35 s margins, smallest 6a5f95c at 1 s).
5. SEV-4: ledger/verifier-w3str.md has no timestamp, no
   Measured/Believed/For lines, no append-provenance note — ledger-shape
   divergence; wave-2 finding 7 (verifier-w2xf provenance line) still open
   alongside it.
6. SEV-4: merge bodies 1357863/d9718cf/6a5f95c cite ledger entries and
   counts but no per-merge log file paths; build/standard/ overwrites by
   design (honestly disclosed in the Wave-2 erratum) — third wave running,
   ledger evidence exists, only path citation missing.
7. SEV-4: no briefs.jsonl rows for any verifier brief in any wave, and none
   for video-final/iast15-port/video-tools tasking — standing pattern, not
   a Wave-3 regression; METRICS.md mandates correction counting, not brief
   rows, so recorded as pattern, not breach.

## 4. What remains unproven or owner-owed at submission

Owner-owed: (a) fingerprint clean-room audit at wave close/end
(CLEAN-ROOM.md control, "not yet exercised" per RECORD Wave-3 entry);
(b) music/VO decision for the silent cut; (c) retrospective scope decision
for unbriefed tooling/feasibility work (wave-2 item 2, video-final metrics
fold belongs to the same decision). Lead-owed (non-blocking): restate the
11:09:14 metrics-fold sentence and fold video-final + auditor-final rows
(or defer explicitly); file parcel-str's 3 corrections rows; fix the
ceiling-measurement definition (exclude generated vectors); add the
verifier-w3str timestamp/shape + w2xf/w3str provenance lines; cite
per-merge log paths or adopt a retention convention. Unproven by design:
silicon behavior beyond the 2,001 compared records; step-rate
generalization beyond the measured 1,000-step blocks. Nothing above blocks
the submission facts: 783/783 pushed at d1bfe38, IAS15 bit-identical on
silicon, 24/25 plants, silent 180.0 s video verified.
