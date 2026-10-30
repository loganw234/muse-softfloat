# Audit Wave 2 — method adherence (disconfirm-only)

Auditor: auditor-wave2. Kit: softfloat-bootstrap-kit v1 (frozen; not modified).
Method read in full: WORKFLOW.md, ROLES.md, METRICS.md, PROJECT.md, OWNER.md,
CLEAN-ROOM.md, AGENTS.md (plus GLOSSARY/MANIFEST via wave-1 audit, unchanged kit).
Wave 1 re-check list from scratch/audit-wave1/report.md closed item by item below.
Project record read: ledger/lead.md (06:52:00 onward in full, earlier entries as needed),
ledger/parcel-f16.md, ledger/parcel-xf.md, ledger/ias15-port.md, ledger/video-tools.md,
ledger/verifier-w2f16.md, ledger/verifier-w2xf.md, ledger/briefs/ (w2-f16, w2-xf,
verify-w2f16, verify-w2xf, ias15-pico, w3-str), ledger/urgent/ (all four files),
scratch/parcel-f16/report.md, scratch/parcel-xf/report.md, scratch/verifier-w2f16/report.md,
scratch/verifier-w2xf/report.md, scratch/ias15/report.md, scratch/video/report.md,
muse-softfloat/docs/RECORD.md (Wave 1 + Wave 2 entries), muse-softfloat/docs/metrics/*.jsonl
(all seven files), git log/show/status/ls-files in muse-softfloat.
Keys: sha256 only via sha256sum (scratch/lead/keys/*.json); contents never opened.
No cft-named path opened, searched, or listed.

## Verdicts per method area

1. Verify-then-merge sequencing — ADHERED (correction of Wave 1's SEV-1).
- Parcel tips 44c770c (07:33:03) and 7935fab (07:36:31) sat unpushed in worktrees while
  planted-copy verifiers reported NOT READY at 08:08:16 (ledger/verifier-w2f16.md) and
  08:11:16 (ledger/verifier-w2xf.md); serial merges a05412f (08:12:45) and 71fbd53
  (08:14:27) came after both verdicts. WORKFLOW.md Phase 4 step 6 and ROLES.md
  "never merge on the strength of a report" hold this wave.

2. Ledger practice (append-only, per-agent, at-event) — DIVERGED (repeat of Wave 1 SEV-1,
   now with a false record claim; see finding 1).
- Shape held: every entry carries Measured/Believed/For lines; per-agent files held;
  verifier-w2f16 states its append provenance (direct file write, no ledger tool in
  sandbox); urgent test files retained (both Wave 2 channel tests + the xf objection
  present in ledger/urgent/).
- But six Wave 2 commits share one batched entry: e393bb0 + a05412f (both 08:12:45),
  6720f9a (08:13:45), 71fbd53 (08:14:27), e905868 (08:15:27), 548a1b9 (08:18:19) are
  covered only by ledger/lead.md 08:18:23, written after the fact. Commit 8a8021c
  (AGENTS.md sqrt landmine note, 07:42:31) has no lead entry at all — no entry exists
  between ledger/lead.md 07:41:35 and 07:46:37. The 06:27:24 Wave 1 pledge ("from here,
  every commit or merge gets a lead entry in the same step") was not kept.

3. Verifier briefs — ADHERED (closes Wave 1 finding 4).
- ledger/briefs/verify-w2f16.md and verify-w2xf.md exist as files, name the planted
  copies (9a414ec, 5f41c0c), the base dd48b08, the byte-identity regen norm (the Wave 1
  miss shape), and the xf wrapper format-index audit probe. Both verifiers applied the
  norm: generator-drift plants filed as (a) findings this wave.

4. Plant grading — ADHERED, 10/10, both generator plants filed as findings.
- plants.jsonl rows 11-20: 5/5 w2f16 + 5/5 w2xf, all caught, graded_by lead,
  checked_by integration. Key hashes in plants.jsonl (824cb884…f16, c589a477…xf)
  match sha256sum of scratch/lead/keys/key-9a414ec.json and key-5f41c0c.json.
- Cross-check: verifier-w2f16 report verdict (a)1 (b)4 maps to 3 code plants + 1 vector
  plant + 2 regen-drift plants (one counted under (a) with the wrong-line (b));
  verifier-w2xf report (a)3 (b)3 maps to 3 code plants + 1 vector + 1 regen plant,
  the sixth (a) being the parcel READY-claim falsehood graded as a plant consequence.
  No non-plant defect stands per lead ledger/lead.md 08:11:57; xf sNaN-adjacent and
  f16 exhaustive sNaN-payload deltas adjudicated as allowed delivery choice, plausible
  on the face of SF-0 2.5 (final word belongs to the integration verifier).

5. Board replay — ADHERED as run.
- muse-softfloat/build/board-fw/replay-w2.log: 2,489 vectors, board SHA-256
  729f495d…b2583f2b9 COUNT 2489, "whole-run hash matches host"; host-hash-w2.log and
  host-verify-w2.log show the same hash with 2,489/2,489 PASS and per-provenance
  counts. Matches RECORD Wave 2 entry's 2,489/hash claim. Lead board-w2.sh ran under
  board.lock per ledger/lead.md 08:18:23.

6. Metrics rows — ADHERED for the six Wave 2 agents, with two gaps named.
- passes.jsonl rows 28-33 + usage.jsonl rows 28-33: parcel-f16, parcel-xf, ias15-port,
  video-tools (Wonder) and verifier-w2f16, verifier-w2xf (Spark), with transcript
  session ids, sha256, tool uses, and honest per-row notes (extractor role_for gaps
  restated by lead fold; wave-2 verifiers needed no UUID relabel — "label via Role:
  in first started prompt"). Times match boxes: f16 ~34/360 min, xf ~42/300,
  ias15-port ~36/240, video ~10/240. briefs.jsonl carries both Wave 2 parcel rows
  (base dd48b08, boxes/ceilings correct). corrections.jsonl gains both Wave 2 brief
  faults, accepted. escalations.jsonl gains 2 tests + the 1-minute xf trap ruling.
  fetches.jsonl gains the REBOUND row (GPL, archive + licence hashes, "never enters
  muse-softfloat").
- Gaps: (a) no briefs.jsonl rows exist for ias15-port/video-tools tasking (they had no
  briefs — see area 8); (b) their passes.jsonl role is "surveyor" for builder work
  (closest available label, undisputed in any note — the honest-label norm of
  METRICS.md would want one line saying so).

7. Clean-room — ADHERED on evidence available.
- git ls-files in muse-softfloat shows no rebound/ias15/extract sources;ias15/rebound
  mentions in the repo are prose only (RECORD.md, SF-0, KICKOFF, metrics). ias15-port
  ledger entries record scratch-only confinement and a clean tree at close
  (ledger/ias15-port.md 07:37:11). Key contents never opened by this audit.

8. Non-parcel work (ias15-port, video-tools) method fit — PARTIAL, method gap named.
- What held: design entries before build (ledger/ias15-port.md 07:04:37 with pin,
  flags, hash spec, extraction-owed tension named; ledger/video-tools.md 07:02:40),
  escalation-adjacent reporting, time-box containment, clean-room, scratch-only GPL,
  close-out reports with reproduction paths.
- What diverged: neither pass had a brief file, time box/scope ceiling in a brief,
  named negative control, verifier pass, or send-back path — the core of ParcelRound
  §3-7. They built (shim code, video pipeline) under the Phase 1 "surveyor" label,
  but Phase 1 surveyors "edit nothing" (WORKFLOW.md) while ias15-port compiled and
  ran interposed builds and video-tools wrote video/ at the workspace root. The kit
  has no "parallel feasibility/tooling" shape: this is a method gap, not just a
  lapse. Mitigating: the follow-on ias15-pico DOES have a proper brief
  (ledger/briefs/ias15-pico.md: extraction, host gate, compat surface, no-flash
  rule). No owner decision scoping unbriefed build work in or out was found.

## Wave 1 re-check list — closed item by item

1. Wave 1 RECORD entry exists — CLOSED. docs/RECORD.md carries the Wave 1 entry with
   deviations named (pre-verification merges; 22:14→05:23 ledger gap + same-step
   pledge), slips attributed, and the auditor-wave1 re-check pointer.
2. Wave 1 passes/usage rows — CLOSED. passes.jsonl rows 20-27 + usage.jsonl rows 20-27
   (parcel-f32/f64, both regaters, rechecker-tininess, both planted verifiers,
   auditor-wave1), relabels noted per row.
3. Regate brief rows — CLOSED. briefs.jsonl rows 3-4 (120-min boxes, ceiling_text).
4. Integration merge-tree re-make + plant-check — STILL OPEN. No merge-tree evidence in
   git log or ledger; RECORD repeats "owed at final wave". Accepted deferral, not done.
5. Merge-time standard/board logs cited by path — OPEN, repeats. Wave 1 entry names
   counts, not log paths; Wave 2 repeats the shape (finding 3).
6. Verifier briefs as files Wave 2+ — CLOSED (area 3).
7. Urgent test files retained to wave close — CLOSED for Wave 2 (all three Wave 2
   urgent files present); Wave 1's own test files remain absent (only the Phase 0
   channel test predates Wave 2), so the Wave 1 trail still rests on
   escalations.jsonl alone — unrecoverable, noted.
8. Parcel READY vs planted NOT READY reconciliation — CLOSED. Wave 2 RECORD entry
   maps verifier findings onto plants with the byte-identity norm; Wave 1 entry maps
   its (a)s onto copy artifacts. Final word is the integration verifier's (open, item 4).
9. Owner fingerprint clean-room audit at wave close — OPEN. No owner-audit result in
   the record for Wave 1 or Wave 2 (finding 4).

## Severity-ordered falsifiable findings (one per line)

1. SEV-1: RECORD Wave 2 entry asserts "every commit and merge has a same-step lead
   ledger entry" — false: e393bb0/a05412f/6720f9a/71fbd53/e905868/548a1b9 share one
   batched entry (ledger/lead.md 08:18:23) and 8a8021c has none; OWNER.md rule 1
   requires restating the false sentence, not standing it.
2. SEV-2: ias15-port and video-tools built without briefs, gates, or verifier passes
   (no files in ledger/briefs/, no briefs.jsonl rows, passes.jsonl role "surveyor"
   for builder work) — unbriefed build work outside every kit shape; needs an owner
   decision scoping it in (brief+verify) or out.
3. SEV-2: integration verifier's merge-tree re-make still owed with no evidence
   (git log shows no merge-tree; RECORD defers to final wave) — wave-1 item kept open
   into a second wave.
4. SEV-3: merge bodies a05412f/71fbd53 claim standard PASS without citing log paths
   and build/standard/ holds no per-merge logs (only controls/, gen-check/) — repeats
   wave-1 finding 7; lead 08:18:23 cites a directory, not the two merge-time logs.
5. SEV-3: no owner fingerprint clean-room audit result in the record for either wave
   (CLEAN-ROOM.md: Logan checks at each wave's close) — open for both waves.
6. SEV-3: plant grading/reveal again precedes round end (ledger/lead.md 08:11:57;
   keys live in scratch/lead/keys/, hashes only in ledger/record) — contained as in
   wave 1 (WORKFLOW.md schedules the reveal "near the end"), standing practice to
   confirm or correct at final wave.
7. SEV-4: ledger/verifier-w2xf.md carries no append-provenance note (verifier-w2f16.md
   does) — one line owed on how the entry reached the ledger.
8. SEV-4: Wave 1 urgent test files still absent from ledger/urgent/ (Wave 2 retention
   held) — Wave 1 escalation evidence permanently single-sourced to escalations.jsonl.

## What the final audit must re-check

- That finding 1's false RECORD sentence is restated (OWNER.md rule 1) and the
  same-step-entry pledge is either kept for Wave 3 or explicitly renegotiated.
- That the integration verifier re-made every wave merge with git merge-tree, ran
  plant.py check over all four keys, and read keys from the ledger/record — with the
  reveal completing the round's plant table via round_metrics.py.
- That merge-time standard/board logs are cited by path for every merge (all waves)
  and replayed, and that wiring commits regenerated tables byte-clean.
- That ias15-pico / parcel-str (Wave 3, briefs filed, tips w3-str + w-ias15 cut at
  548a1b9 per ledger/lead.md 08:20:23) verify-then-merge with briefs as files, and
  that an owner decision on unbriefed parallel work (finding 2) is recorded.
- That the owner's fingerprint clean-room audit ran at least once with its dated
  result in the record, and that no GPL source entered muse-softfloat (ls-files +
  commit contents, not claims alone).
- That Wave 2's push is confirmed (no push-confirmation entry stands at 08:20:23;
  working tree clean with cc71d73/548a1b9 local) and the final record carries full
  chain/time/token/plant/correction/escalation tables with the lead's slips.
