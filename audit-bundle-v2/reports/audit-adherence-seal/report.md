ADHERENT WITH SLIPS — Wave 6 + seal: all 10 parcel merges planted-verified before merge with key hashes committed pre-dispatch (timestamp-proven), metrics append-only perfect (0 deletions, prefixes intact), trailers 50/50, clean-room and licensing clean, public tallies independently re-derived exact (162/170, Wave 6 44/45, tokens 1,418,065,198); slips are two post-verification fixes merged without re-verification (disclosed), three brief-directed parcel-branch pushes, a briefs 44-vs-45 miscount propagated to RECORD, three unrowed Wave-6 revision rounds in escalations, and un-stamped film freeze figures — plus the immutable Wave-1 history items still open.

# Methods audit: seal (auditor-adherence-seal, Wave 5 close -> submission seal)

Freeze: `muse-softfloat` HEAD = `751d1d6` (2026-11-01 17:17:07 -0700),
"Land seal parcels: verifier grades 5/5 + 4/5, tallies restated".
`origin/main` == HEAD (pushed), tree clean (`git status` empty).
Span `bc807e6..751d1d6` = 50 commits, 31 first-parent.
Base `bc807e6` = the audit-adherence-final freeze.

Method: read-only. Never opened `ledger/lead.md`, `scratch/lead/`,
anything with `cft` in its name, or any `Muse`-audit branch
(none encountered). Counting scripts beside this report
(Git Bash via PowerShell, `MSF_PYTHON` = workspace `.venv`
Python 3.12.15): `census.py`, `prefix.py`, `timing.py`,
`objects.py`, `claims.py`, `followups.py`, `graph.py`,
`resolve.py`, `dispatch.py`, `u1.py`, `cleanroom.py`.
Authorities read in full: `ledger/briefs/audit-adherence-seal.md`,
`scratch/audit-adherence-final/report.md` (all of it),
all 10 `ledger/verifier-w6*.md` + `ledger/verifier-polish1.md`,
all 10 `ledger/parcel-w6*.md` + `ledger/parcel-polish1.md`
(openings + design entries; augint + w6metrics in full),
all `ledger/briefs/w6-*.md` + `verify-w6*.md` + `verify-polish1.md`
+ `fix-w6popups.md` + `polish-stale1.md` (existence + fence lines;
not re-read whole), `docs/RECORD.md` seal entries (lines ~990-1249),
`docs/metrics/*.jsonl` at HEAD, `docs/metrics/plant_keys.sha256`,
`README.md` claim surface, `docs/BOARD.md` 1-40/110-135,
`docs/HARNESS.md:15-34`, `video/MUSIC.md`, git history of the span
(all 10 merge bodies + all 10 landings + key-record commits +
revision commits, full bodies). Sampling boundaries at the end.

## 1. Re-grade of the 15 audit-adherence-final debts at HEAD

### D1. corrections.jsonl frozen at 16 — PARTIALLY REPAIRED, 1 still open, 4 rejected-with-reason (corroborated), 2 new candidates
- `a73e97d` appended 6 sourced rows (5x verifier-sf2 SF-2-draft
  corrections + 1x tokens-visual double-count): 16 -> 22 rows.
  Verified present at HEAD (`wc -l` = 22).
- C1-C4/C6 rejection ("the planted defects themselves; merged rows
  already correct") CORROBORATED by new span evidence:
  verifier-w6judgemap finding (5) blames "the lead restamp" for the
  `...66c1423` nibble, but HEAD `demo/expected-interval.txt` carries
  the correct `...66c1422` (`git show HEAD:...`, `e1b0b46` body) —
  the copy's plant flipped the nibble and the verifier misattributed
  it. Same shape as the rejected C-candidates. Also popups F1-F4 vs
  merged-tip POPUP5 (merged reads 19/36/150/1117504/"scout the ground",
  exactly the verifier's "correct" values — findings were copy-only).
- C7 (w5site residue): CLOSED. verifier-w6judgemap re-walked the site
  (`ledger/verifier-w6judgemap.md:29-37`: 822/849 ops, live 200,
  buttons present) and verifier-polish1 F2's site-figure fix landed
  in the parcel. No residue found at HEAD.
- C5 (twiddledoc `a41f026` hash correction): STILL UNROWED. Genuine
  parcel correction, still absent from corrections.jsonl. Carried
  (debt SD-9).
- NEW candidates NC1/NC2 in section 3.

### D2. 65 old `checked_by: integration` — REPAIRED (erratum stands, new rows honest)
- RECORD erratum at `docs/RECORD.md:1004-1012` restates all 65 as
  lead-run, append-only (rows stand). New span rows: all 50 carry
  `checked_by: lead-merge` (script-counted, 0 exceptions).

### D3. `sent_back` semantics — REPAIRED IN SUBSTANCE, erratum count stale, 2 new `true` rows honest
- Erratum (`RECORD.md:1009-1012`) rule ("true only on proven revision
  rounds") covers the 8 old `true` + 58 missing-field rows.
- At HEAD 85/131 passes rows lack the field (was 58/94: the w6 fold's
  27 unmarked rows inherited the idiom). The erratum's "58" is now
  stale; its semantic rule still covers every missing-field row.
  One-line appendix note owed (debt SD-8).
- Two NEW `sent_back: true` rows are HONEST, not relapses:
  verifier-w6ci (F3 pipefail -> `caf00b0` revision) and
  verifier-polish1 (twiddle_gate observation -> `8751b11` revision) —
  both verdicts caused proven pre-merge revision rounds, exactly the
  erratum's `true` condition. Full rows sourced in
  `scratch/audit-adherence-seal/resolve.py` output.

### D4. False universals — REPAIRED, one new precision nit
- README now states the exception (`README.md:293-298`: lead
  wiring/record commits "are not planted-verified parcel-style; they
  are gated by `standard` and named as lead work in RECORD").
- `docs/HARNESS.md:23` corrected (sanctioned, not only, writer).
- NIT (new): `docs/HARNESS.md:20` still says pushes happen "only
  after a verifier READY", but direct-to-main lead landings
  (`0eca989`, `f01dc96`, `cdc40ae`, `751d1d6` grade landings) carry
  no verifier of their own — only `standard` + prior parcel
  verdicts. One-line precision restatement owed (debt SD-7).

### D5. README plants pin — REPAIRED AND CURRENT
- `README.md:146-147` pins 162/170 (Wave 6 44/45) at the current
  tree. Independently recounted from `plants.jsonl` at HEAD:
  170 rows, 162 caught, 8 missed; wave6 44+1=45 (`claims.py`).
  Earlier pins (153/160, 148/155, 138/145) kept as dated history
  (`README.md:149`). The pin-then-drift pattern is now pin-at-seal.

### D6. Key-hash pre-commitment — ADOPTED AND TIMESTAMP-PROVEN
- All 10 seal key hashes committed hash-only to main BEFORE dispatch
  (`c558fb5`, `9010f60`, `03f18a8`, `7752e58`, `98c58db`, `06808c9`,
  `a2241fc`, + `400b271`-era polish entry). `plant_keys.sha256`
  carries all 10 with copy/base/date; every one of the 50 seal
  plants rows names a key present in that file (0 seal mismatches;
  the 120 old-row "mismatches" are the known pre-rule keys living in
  `scratch/lead/keys/` + the audit bundle — S2 history, unchanged).
- `dispatch.py`: 8/8 verifiers with passes rows show key-commit time
  < session-start time by 13 s-2 min (`verifier-w6ci`: 05:30:13 <
  05:30:34; `verifier-w6popups`: 15:34:29 < 15:35:07; etc.).
  Captions/metrics (no passes rows by cutoff design): copies cut
  17:42:40/42, keys committed 17:43:15, merges next day — same shape.
- Companion rule adopted: all 10 verifier briefs fence
  `docs/metrics/plants.jsonl` by name (`u1.py`: 10/10).
- Copies: all 10 worktrees present, detached HEAD, `status` clean
  (`graph.py`). Early-6 copy objects live in the worktrees (pruned
  from the main ODB); late-4 survive as main-repo commits. Verifiable
  either way; note the split (debt SD-10, informational).

### D7. Per-wave reveal history — STILL OPEN (immutable), caveat stands
- Git history still lets a reader reconstruct plant shapes
  retroactively. RECORD caveat (`RECORD.md:1001-1003`) stands.
  Nothing further is possible; keep the sentence.

### D8. Bodies lacking ledger refs — STILL OPEN, regressed
- 34/50 span commits lack "ledger" in the body (`census.py`; was
  36/91). Dominated by key-record commits, lead-direct work commits,
  and grade landings. Merge bodies DO cite parcel/verifier
  reports + ledgers. Future-only rule stands; no history rewrite.

### D9. RECORD restatement — HELD, no new silent restatements
- `docs/RECORD.md` prefix-intact vs `bc807e6` (+12580 B, 0 deletions
  proven by byte-prefix check `prefix.py`; numstat 272+/0- on RECORD).
- In-span in-place edits all pre-push AND disclosed in bodies:
  `ef0215b` (briefs row restated, POPUP_WORDS unchanged statement),
  `227f69f` (LF->CRLF apply-slip restored, caught at merge gate),
  `1cfed36` (CRLF restore). Site/data.json + README regenerated at
  landings, each disclosed in its landing body.
- Both `briefs.jsonl` merge conflicts (`6675fec`, `47f5ea7`) resolved
  as clean unions, both sides kept, `# Conflicts:` kept in the body.
  Byte-prefix check on all 7 metrics files: intact, 0 deletions.

### D10. kit-zip + standing rules — CLOSED
- `RECORD.md:1028-1030`: kit-zip sha256 matches the owner's retained
  hash (confirmed 2026-10-28); P1=R2 adopted same day.

### D11. Boxes/ceilings — PARTIALLY improved, hard ceilings still absent
- All 14 wave6/polish/fixer briefs rows carry `time_box_min`
  (120/240/360/480/720) and an explicit `ceiling_text`
  ("no line ceiling stated in brief ...; owned-files list is the
  bound"). Explicit-instead-of-absent; hard ceilings still future-only.

### D12. Unreconstructed study/audit rows — PARTIALLY repaired, residue named
- w6metrics fold added honest late rows (auditor-adherence-final,
  study-w6sanitize, study-video-gitvisual-v6, fixer-w6popups, each
  "row authored late" noted). Parcel ledger (`ledger/parcel-w6metrics.md:76-81`)
  names what stays unrowed (nine 10/29 film studies, gitvisual-v7,
  epidemic licence study, Spark audit, lead-polish1 pass row, own rows).

### D13. Board lock/serial evidence — PARTIALLY repaired
- Serial `E66440A2CB6F5C2B` now corroborated 3 ways in granted
  authorities: `docs/BOARD.md:33-37,112,130` (two measurement methods
  + serial-targeted flash), landing `bc70d10` ("genuine board ...",
  710/710 host==board), RECORD augint/seal entries.
- NOT met: no `board.lock` file in any granted authority
  (`ledger/board.lock` absent; nothing tracked in-repo), and neither
  `ledger/parcel-w6augint.md` nor `ledger/verifier-w6augint.md` cites
  lock/serial (the rule's letter: "in a parcel/verifier ledger").
  Commit bodies + BOARD.md + RECORD carry it instead. Debt SD-6.

### D14. No integration role — CLOSED (kept honest)
- All 50 new plants rows `checked_by: lead-merge`; D2 erratum covers
  history. Cheaper-than-dispatch stands.

### D15. Gate-log paths in merge bodies — ADOPTED (sampled)
- ci/augint/captions landings cite Actions run numbers
  (41052508849/41054249115/41057237264/41064095464),
  `scratch/lead/board_augint_interval.log`,
  `scratch/lead/gate_w6_main_standard.log`, per-parcel standard logs.

## 2. Wave 6 + seal fresh-eyed adherence

### Planted-verification coverage: HELD 10/10 (2 with a re-proof caveat)
Every parcel merge names verifier + copy + grades:
polish `f766e0f` (4/5, attr-count miss), augint `47a405f` (5/5),
ci `6675fec` (5/5+1 real), examples `b85e037` (5/5), sanitize
`4486cb5` (5/5), judgemap `870b82f` (5/5), filmretime `3dfa3d8`
(5/5), popups `f36e171` (5/5; 6th ledger line is plant-consequence),
captions `5b9fff3` (5/5), metrics `47f5ea7` (4/5, wave-label miss).
Cumulative 114/120 -> 162/170; Wave 6 44/45; misses honestly graded
(`plants.jsonl` notes name both). Copy-vs-tip diffs sampled:
`fe04000..e7087dc` = exactly the 5 plants (3 files, 5+/5-);
`ef0215b..8507695` = exactly the 5 plants (1 file, 5+/5-).
- Caveat (2 instances): a genuine finding was fixed on the branch
  AFTER the copy was cut and merged WITHOUT re-verification.
  (i) w6ci F3 (inventory pipefail): copy `3cec27c` cut 05:3x,
  fixed `caf00b0` 05:41:23, merged `6675fec` 05:51:33.
  Re-proof = Actions run 41057237264 green + merged-tree standard
  PASS (both cited in the merge body). (ii) polish-stale1
  twiddle_gate observation: fixed `8751b11` 20:33:11 post-dispatch.
  Both disclosed in their merge bodies; risk accepted on lead
  re-proof, not independent re-check. Slip, honestly disclosed.

### Key-hash timing: HELD (proven, not merely asserted)
See D6: 8/8 timestamp-proven (key commit < session start), 2/2
structural (copies 17:42:40/42 < keys 17:43:15 < merges next day).

### Append-only: HELD (proof, not sampling)
`prefix.py`: all 7 metrics files byte-prefix-intact vs `bc807e6`
(passes +24425, plants +22508, usage +13322, briefs +9111,
corrections +1751, escalations +0, RECORD +12580), numstat 0
deletions on every metrics file. Two conflict merges = clean unions.

### Briefs-before-dispatch / ownership / send-back: HELD with one exception
- All 10 parcels + fixer + all 10 verifiers briefed as files;
  design entries before edits confirmed in augint + w6metrics parcel
  ledgers (dated sections); all parcel ledgers carry base/branch/
  worktree/brief; no parcel merged its own work (all merges lead,
  author Logan throughout, Co-Authored-By 50/50).
- Time boxes on all 14 wave6/polish/fixer briefs rows; explicit
  ceiling_text (D11).
- Send-back inventory (all on-branch, pre-merge except the D-caveat
  two): `ef0215b` wrong-answer counts (fix-w6popups brief) — allowed
  class; `5b53bf3` parcel self-revision (real Ubuntu CRLF failure);
  `93886a8` lead SRC fix (verified after); `e1b0b46` lead restamp of
  a parcel-found real regression (verified after); `1cfed36` style;
  `227f69f` merge-gate restore (disclosed). Only
  regression/wrong-answer/gate classes. HELD.
- EXCEPTION (fresh finding F1): three parcel branches exist on
  origin (`origin/wave6-ci` @ `caf00b0`, `origin/wave6-examples` @
  `b6e08fd`, `origin/wave6-sanitize` @ `77e6e64`) vs HARNESS:20
  "Parcels commit in their own worktrees, never push." All three sit
  exactly at merged tips; the examples push was brief-directed
  (`ledger/parcel-w6examples.md:5`: "push the branch for the
  example-host CI job's remote run ... by brief design"). Recorded
  reason, limited blast radius — but the letter of the rule broke
  three times. Name it; cheapest fix is a HARNESS line allowing
  brief-directed CI pushes (debt SD-5).

### Board-lock discipline: PARTIAL (see D13)
Serial corroborated; lock file + ledger citations still missing.

### Commit discipline: trailers HELD 50/50, ledger-refs regressed (D8)
Bodies detailed (counts/hashes/ledger paths/reports); second-parent
fixups named (`93886a8`, `caf00b0`, `5b53bf3`, `77e6e64`,
`8751b11`, `227f69f`, `e1b0b46`, `1cfed36`, `ef0215b` all explained).

### Clean-room: HELD (re-scanned, `cleanroom.py`)
869 tracked files: 0 audio, 0 `cft`-named, no vendored third-party
source (13 name-hits all project-owned: board/demo harnesses,
ingest scripts, one still filename; kit-internal zips + reference
bundle only). Repo film cuts verified silent by verifiers
(2560x1440@30, single video trak); raw track + music muxes live
outside the repo (workspace-root mp3 untracked). Terms chain:
`study-epidemic-license` -> `video/MUSIC.md` (Pro grant read as
PARTLY: muxed sync covered, standalone distribution + unlisted-repo
venue not; owner disposition: silent repo cuts, soundtrack on the
owner's unlisted YouTube, linked from README:36 + MUSIC.md:10-11).

### Public-claim discipline: HELD with freeze-stamp debt
Independently re-derived at HEAD (`claims.py`, `graph.py`):
plants 162/170 (Wave 6 44/45) exact; tokens 1,418,065,198 exact
(in+out = 1,410,803,658+7,261,540; frozen 1,196,128,770 + appended
221,936,428); passes 131 / usage 128 / briefs 45 / escalations 20
exact; SRT 77 cues; stills 30 + INDEX; YouTube link live in two
places; no release tag (owed, RECORD says so).
Film popup cards (19 parcels / 20+3 / 36 verifiers / 150 plants /
411,213+1,117,504 / 35 studies / 25 merges): each verified
mp4=ledger=row by verifier-w6popups, and each re-derives from the
frozen graph (`process_graph.json` episodes: lead 1 / surveyor 35 /
verifier 36 / author 19 / fixer 3; `history.json`:
head `a73e97d`, merges_into_main 25; plants 150 = total at judgemap
landing; escalations/vectors current-at-seal). Method disclosed in
the popup brief row + RECORD popup entry ("script-derived from the
frozen process graph or HEAD tree") + RECORD seal entry (outro keeps
freeze-time figures). Debt: the CARDS carry no freeze stamp and
RECORD names no per-number freeze point — at HEAD `git log` shows 35
merges and `plants.jsonl` 170 rows, so a re-counter sees 25/150 as
wrong without the appendix (debt SD-1). Vectors/durations rest on
verifier probes + CI (no gate re-run in this audit — boundary).

### U1 (final-audit unsourced suspicion): RESOLVED, merge claim stands
verifier-w5demo's 5 findings map 1:1 onto its 5 plants
(licence-bypass, summary-PASS, IAS15 nibble, KissFFT nibble,
cache-ignore; `u1.py`), all graded caught; merge `eac88b0`'s "no
non-plant defect" holds. At HEAD `if False` is absent and
`run_demo.sh:263-267` fails properly. U2 stands excluded with reason
(copy-side fallout, judgemap-(5) corroborates the shape); U3 (ledgers
undated) persists as a boundary.

## 3. Candidate corrections.jsonl rows for the span

File state first: `docs/metrics/corrections.jsonl` = 22 rows at HEAD
(16 + 6 appended at `a73e97d`, all Wave 3-5).

| # | wave | brief (corrected) | by | at (sourced) | one-line text | accepted | exact source |
|---|------|-------------------|----|--------------|---------------|----------|--------------|
| NC1 | wave6 | merge `47f5ea7` body + RECORD seal entry ("briefs 39->44") | auditor-adherence-seal | 2026-11-01T17:11:17-07:00 (merge committer time) | union added 6 rows, not 5: 39+1 (captions side) +5 (metrics side) = 45 nonempty rows, not 44 | false (lead to adjudicate; file itself is correct, the claim about it is not) | `git log -1 --format=%B 47f5ea7` vs `git show 47f5ea7:docs/metrics/briefs.jsonl` (45 nonempty, `resolve.py`); RECORD ~line 1235 repeats 44 |
| NC2 | wave6 | `ledger/parcel-w6metrics.md:43-44` ("Spans now end 2026-10-29T15:43:55") | auditor-adherence-seal | 2026-10-30 (ledger entry date; session stamp below) | date is a typo: the named session (verifier-w6popups) ended 2026-10-30T15:43:55-07:00 | false (lead to adjudicate; unversioned ledger file, fixable in place with a note) | `ledger/parcel-w6metrics.md:43-44` vs passes row verifier-w6popups start/end 2026-10-30T15:35:07/15:43:55 (`u1.py`) |
| C5 (carried) | wave5 | parcel-w5twiddledoc | verifier-w5twiddledoc | pre-merge 2026-10-28 (fix `a41f026`) | TWIDDLES.md:370 kiss_fftr.c sha 56->64 chars | false (still unrowed; genuine) | `ledger/verifier-w5twiddledoc.md:15-18` + `a41f026` + merge `97d1cbe` (per final audit s3) |

Schema note: existing rows are `by` parcel/verifier agents with
`accepted: true`. NC1/NC2 are auditor-found with `accepted: false`
(lead adjudication needed); if the lead wants author-purity, the same
texts can be re-filed by the lead with these sources.

Unsourceable / rejected-with-reason (NOT rows, listed separately):
- w6metrics B1-B3+N1, popups F1-F5(+#6 consequence), judgemap (1)-(4)
  (+(5) misattributed to the lead restamp — tree already correct),
  augint F5 (plant-consequence numbers; base values reproduce),
  captions F1-F5(+F4/F7/F8 consequences), filmretime F1-F3
  (F4/F5 pre-existing, RECORD-disclosed): all copy-side plant fallout;
  merged tips already correct. Same rejection reason as C1-C4/C6.
- Escalation-shaped Wave-6 events (F3 fix, twiddle_gate fix, judgemap
  restamp) belong to `escalations.jsonl`, not corrections — debt SD-4.

## 4. Remaining submission debts (cheapest honest disposition each)

- SD-1. Film cards unstamped freezes (25 merges vs 35 at HEAD; 150
  plants vs 170). -> One RECORD appendix paragraph naming each
  card-number's freeze point (merges@a73e97d, plants@judgemap
  143/150, episodes@94-row passes, vectors/escalations live). Do NOT
  re-render the sealed mp4.
- SD-2. NC1 (44 vs 45). -> Same appendix line (merge bodies immutable).
- SD-3. NC2 ledger date typo. -> Fix in place + "(typo, auditor-flagged
  2026-11-01)" note (workspace ledger file, unversioned).
- SD-4. Three Wave-6 revision rounds unrowed in escalations.jsonl
  (F3->caf00b0, twiddle_gate->8751b11, interval restamp->e1b0b46;
  all citable via git committer times, contra the "no citable
  stamps" line). -> Lead appends 3 late rows or records why the W5
  bar (fast send-backs rowed) does not apply. Note the W5-precedent
  tension in the same entry.
- SD-5. Three parcel branches on origin vs "never push". ->
  One-line HARNESS exception for brief-directed CI pushes (the
  examples brief already directs it) + keep tips at merged commits.
- SD-6. D13 residue: `board.lock` in no granted authority; no
  lock/serial line in any parcel/verifier ledger. -> Next silicon run
  appends lock-holder + serial to its parcel ledger (rule already
  adopted in RECORD; first use still owed).
- SD-7. HARNESS:20 "only after a verifier READY" vs direct-to-main
  lead landings. -> Restate to "parcel merges ... ; lead
  wiring/record/grade landings gated by `standard` + named in RECORD".
- SD-8. `sent_back` field missing on 85 passes rows; erratum says 58.
  -> One-line appendix: count grew to 85, semantics unchanged.
- SD-9. C5 twiddledoc row still unrowed. -> Append the sourced row.
- SD-10 (informational). Early-6 planted-copy objects live in
  worktrees only (main ODB pruned); audit via worktrees (present,
  detached, clean). -> None; or pin the 6 SHAs in the v2 bundle manifest.
- SD-11. audit-bundle v2 (CRLF manifest breaks `sha256sum -c` under
  Git Bash) + release tag. -> Still open per RECORD; both owed before
  submission. No in-span progress (0 audit-bundle changes).
- SD-12. Immutable history (Wave-1 inverted merges, unverified lead
  commits, per-wave reveal, old labels): disclosed via D2/D3 errata +
  D7 caveat. -> Nothing further; keep the sentences.
- SD-13. D8 (ledger refs) + D11 (hard ceilings): future-only rules. ->
  Next brief template requires ceilings; commit template keeps the
  ledger line.
- SD-14. Seal-verifier/parcel sessions (4) unrowed in usage/passes by
  the cdc40ae-cutoff design (named in `ledger/parcel-w6metrics.md:58-61,
  quantified, not rowed). -> Already disclosed; judges counting
  sessions/passes see 35 agents vs 37 — the parcel report + RECORD
  cutoff line cover it. No action.

## Not audited (sampling boundaries)
- Kit METHOD texts not re-read (final audit's readings reused).
- No gate re-run (`tools/run.sh` budgets, board, CI reruns); counts
  taken from verifier probes + cited logs. Transcripts unopened
  (usage rows shape-checked only). Push timing rests on bodies +
  `origin/main`==HEAD. Anything after `751d1d6` outside scope.
- Parcel design-entry depth: confirmed dated entries in augint +
  w6metrics ledgers; remaining parcel ledgers confirmed for
  base/branch/worktree/brief + report pointers only.
- `ledger/lead.md`, `scratch/lead/`, `*cft*`, `Muse`-audit branches:
  never opened/listed (fence compliance).
