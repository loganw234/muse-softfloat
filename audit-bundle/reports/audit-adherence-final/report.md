ADHERENT WITH SLIPS — every Wave 4-5 parcel merge carries planted-copy verification with named copy hashes and grades, the Wave 3 metrics freeze was repaired append-only through SF-2 close (94 passes / 93 usage / 20 escalations, verifier-checked), and the tree is clean-room clean; but Wave 1's inverted merges, the per-wave plant reveal, uncommitted key hashes, the old `integration`/`sent_back` labels, and the README/HARNESS universal sentences all still stand unrepaired.

# Methods audit final: Phase 0 through Wave 5 close (auditor-adherence-final)

Freeze: `muse-softfloat` HEAD = `bc807e6` (2026-10-29 13:53:14 -0700),
"Landed verifier-w5readme3 plant grades (5 of 5)", tree clean
(`git status` empty). 140 commits reachable, 91 first-parent.
Prior audit froze at `7c3819c` (82 commits); this audit covers the
58-commit Wave 5 close (SF-2 Steps 2a-4, site/demo/twiddledoc/metrics/
readme3) plus re-grades of every audit-adherence-2 slip at the new HEAD.

Method: read-only. Never opened `ledger/lead.md`, key files,
`scratch/lead/`, or anything with `cft` in its name. Counting scripts
(Git Bash, `MSF_PYTHON` = workspace `.venv`) beside this report:
`counts.py` (metrics + git census), `cleanroom.py` (tree scan).
Authorities read in full: `scratch/audit-adherence-2/report.md`,
`docs/RECORD.md` (977 lines), `docs/metrics/*.jsonl` at `bc807e6`,
all 20 `ledger/parcel-*.md` + 32 `ledger/verifier-*.md` files for
Waves 4-5, all `ledger/briefs/w5-*.md` + `verify-w5*.md` briefs,
`muse-softfloat/README.md`, `docs/HARNESS.md`, kit METHOD texts via
the prior audit's citations (not re-read whole; sampling boundary).

## 1. Re-grade of the six audit-adherence-2 conceded slips

### S1. Wave-1 merges preceding verdicts + ~30/44 lead commits unverified + `d9718cf` with no verifier — STILL OPEN (immutable, claim fix still owed)
- `2843792` (05:17:07) / `06fdec8` (05:18:44) before the planted
  verdicts is git-immutable; no erratum was appended.
- W4-5 did NOT repeat the inversion: every Wave 4-5 merge body names
  its verifier, copy hash, and grade (e.g. `7772da7`, `cf81644`,
  `4a0b0d4`, `0de6a30`, `4a80126`, `97d1cbe`, `eac88b0`, `3a09c76`,
  `a1a888f`, `5a387e5` — bodies read). Verdicts (reports/ledgers)
  predate their merges; only the plants.jsonl grade rows land
  seconds post-merge (e.g. merge `a1a888f` 12:57:33, grades
  `e9c57fb` 12:57:43) — reported openly in the bodies, benign.
- Lead-direct commits on first-parent without a named verifier
  CONTINUE: `5f308c4`/`bc15593` (LED firmware), `a51f31e`
  (timeout), `109b814` (board wiring), `53d2265` (wording),
  `26e86ce` (RECORD note), the three SF-2 record commits
  (`54ac1bb`, `bce49e0`, `5142594`). First-parent bodies with no
  "ledger" reference ROSE from 15/58 to 36/91 (census script).
- `README.md:141-144` still states the universal
  ("a verifier ... stands between each parcel (and each of the
  lead's own commits) and the push") — disprovable from `git log`,
  unchanged since audit-2. `d9718cf` (no verifier) unchanged.
- Disposition: the history cannot be repaired; the SENTENCE can.
  Still owed (debt D4).

### S2. Per-wave plant reveal vs approved once-at-end + key hashes never pre-committed — STILL OPEN
- Wave 5 graded per step: 7+ grade landings after `7c3819c`
  (`b9ab489`, `187541a`, `b408e89`, `6078e73`, `7d0ed81`,
  `e9c57fb`, `bc807e6`). Cumulative 114/120 (6 honestly missed).
- No W5 verifier brief carries a key sha256 (searched all
  `ledger/briefs/verify-w5*.md`: zero hits) and none forbids
  reading `docs/metrics/plants.jsonl`. All 13 planted copies
  still sit in `worktrees/verify*/` (listed 2026-10-29).
  The proposed shape (sha256 in the verifier brief pre-dispatch)
  was NEVER adopted.
- Sufficiency judgment: the proposed shape is NECESSARY but NOT
  SUFFICIENT. Briefs and the ledger are unversioned files (workspace
  root is not git): hashes there prove nothing timestamped and are
  silently editable. Within the frozen kit tools the cheaper
  STRONGER shape is a hash-only commit to `muse-softfloat` pre-
  dispatch under WORKFLOW step 3's standing permission (git gives
  hash + committer timestamp), plus one line in each verifier
  brief fencing `plants.jsonl`. Cost: one commit per wave.
- Disposition: adopt going-forward (debt D6); history discloses
  itself (debt D7).

### S3. Passes/usage frozen at Wave 3 — REPAIRED. Escalations frozen — REPAIRED. Corrections frozen — STILL OPEN
- `3f29682` (branch `wave5-metrics`, parcel-w5metrics with a
  design-before-edits entry in `ledger/parcel-w5metrics.md`)
  appended 119 rows, 0 deletions: usage 39->93, passes 39->94,
  escalations 13->20, briefs 27->30. Verifier-w5metrics probe 1
  PASS: frozen prefixes byte-identical
  (`ledger/verifier-w5metrics.md:13-14`). Kit `round_metrics.py`
  selftest 43/0, all-wave tables exit 0. New rows honestly mark
  restatement provenance ("restated by w5-metrics fold").
- Escalations now cover the video-final test, four tier2 study
  tests, and both Wave 5 substantive escalations (alg1 `109b814`
  in 23 min, alg2 `53d2265` in 64 min); test rows omit `answered`
  where no receipt is stamped — honest omission, named.
- Briefs 31 rows: trigspike + parcel-w5exp2 + own row restored;
  7 study/audit rows honestly NOT reconstructed (no time box
  anywhere in brief/ledger — invention refused). Verifier briefs
  never had rows (frozen idiom, kept).
- `corrections.jsonl` still 16 rows, all Wave 1-3. Genuine W4-5
  corrections (twiddledoc `a41f026`, readme3/site fixes, metrics
  F1-F4) are unrowed. Debt D1; candidates in section 3.

### S4. `checked_by=integration` fictional — PARTIALLY REPAIRED (new rows honest, old rows stand)
- All 55 new plants rows say `checked_by: lead-merge`
  (40 wave5 + 10 site + 5 readme); the 65 old rows still say
  `integration`. No integration-verifier agent was ever
  dispatched (fix #2's "dispatch once" was NOT adopted; the
  cheaper relabel was). New passes rows use correct `sent_back`
  semantics (planted NOT READY = false, e.g. verifier-w5aug row).
- The 8 old planted `sent_back: true` rows and 65 `integration`
  labels persist (append-only forbids edits). Owed: one RECORD
  erratum restating both, à la `4ceffa9` (debts D2-D3).
- New blemish: 58 backfilled passes rows carry NO `sent_back`
  field at all (Counter: None 58 / False 23 / True 13) — the
  fold omitted the field where the kit shape wants false.
  Cosmetic; note in the same erratum.

### S5. Claim surface false at freeze (README + SF-2 approval order) — REPARIED IN SUBSTANCE, two sentences still false
- README restated twice: `0918eac` (auditor-flagged staleness
  fixed, planted-verified 5/5) and `498a916` (full re-derivation:
  849 = 783 + 66/66, 411,213 vectors = runner total, Tier 2
  66/66, attr 273 = has_rm census). Current README pins plants
  "109 of 115 at `e9c57fb`" while HEAD is `bc807e6` (114/120) —
  openly pinned, one step stale (debt D5). COVERAGE re-derived
  by verifier-w5readme3: 849 rows, 0 unconfirmed
  (`ledger/verifier-w5readme3.md:12-16`).
- Site fixed at merge `5a387e5` (pair_call regex + `msf_aug.c`
  breaks found and fixed; 9 augmented pairs excluded with the
  exclusion PRINTED; replay 1,620/1,620).
- SF-2 P1 gloss: `ledger/briefs/w5-aug.md:19-22` records P1=R2
  "owner-approved 2026-10-28" with a STOP rule if the second
  read fails — the Step-4 second read closed the live risk
  (sourced from the brief, not `lead.md`). Kit-zip sha256 still
  owed (RECORD: "does not confirm the kit-zip builder hash ...
  stay open by name"); standing rules still unconfirmed
  line-by-line.
- `docs/HARNESS.md:23` ("`tools/ledger.sh` ... is the only ledger
  writer briefs use") still false: W5 parcel/verifier ledgers
  (e.g. `ledger/verifier-w5aug.md`, `ledger/parcel-w5readme3.md`)
  carry dated `##` headings, not `ledger.sh` stamps. Debt D4.

## 2. Fresh-eyed Wave 4-5 adherence

- Planted coverage per merge: HELD. All 11 W4/W5 parcel merges
  name verifier + copy hash + plant grade; distinct key_sha256 =
  24 (13 old + 11 new verifiers x 5). Grades 114 caught / 6
  missed, misses honestly graded (incl. verifier-w5metrics'
  fair-miss U1 shape).
- Append-only: HELD for metrics (119+/0, proven); RECORD has
  ONE new 1-deletion reflow (`26e86ce`: wrapped the prior
  paragraph's last line to append the demo-page sentence —
  in-place edit of a pushed paragraph, minor, leave-and-note).
  RECORD commits now 21.
- Briefs-before-dispatch: HELD. Every W5 parcel and verifier
  has a brief; parcel-w5metrics/readme3 show design entries
  before edits; owned-file fences held (no parcel pushed/merged:
  all merges are lead first-parent; remote only `origin/main`).
  Brief SHAPE still thin: parcel briefs carry time boxes
  (120-900 min distribution in briefs.jsonl) and seam stops
  but no scope ceilings (`ceiling_lines: 0` on 18/31 rows),
  no brief-got-wrong line, no READY definition; the 2,880-min
  trig box still stands. Future-only fix (debt D11).
- Verdicts honoured: HELD for W4-5 (NOT READY = plants caught,
  zero genuine findings per merge bodies; the one genuine
  pre-merge defect, twiddledoc hash `a41f026`, was fixed ON the
  branch before merge `97d1cbe` — the loop working as designed).
- Board-lock discipline: UNCONFIRMED from granted authorities
  (all silicon-run citations live in off-limits `lead.md`;
  no `board.lock`/`MSF_BOARD_SERIAL` string in any readable
  ledger file). No contrary evidence (verifiers: "no board
  touched/flashed"). Debt D13.
- Clean-room: HELD, re-verified by scan (`cleanroom.py`): 216
  tracked files; `src/`+`include/`+`compat/` contain only the
  project's own "softfloat" name and one prose `KissFFT` word
  (`compat/msf_aeabi.h:69`); oracles executed-only; fetches 5/5
  with hashes/licences. Fingerprint waiver still recorded-open.
- Commit discipline: trailers 140/140 HELD (all author "Logan",
  model in trailer — git attribution still softer than the kit
  assumes); ledger references REGRESSED (36/91 first-parent
  bodies lack "ledger", incl. most W5 merges' second-parent
  fixups and all three SF-2 record commits). Bodies otherwise
  detailed (merges carry counts/hashes/ledger paths).
- Automation honesty: gates are scripts; negative controls run
  (`run.sh` inventory + NC battery, twiddledoc gate 8856/0
  re-run by verifier). Merge-time gate LOG PATHS still uncited
  in merge bodies (fourth-wave repeat of the finding). Board
  serial-targeting landed pre-freeze (`5e712cb`); LED followups
  (`5f308c4`, `bc15593`) are lead-direct.
- Owner gates: studies approved before waves (SF-1 `fe213fd`,
  SF-2 prefix); scope in KICKOFF appended, readings marked;
  model tiers conform (new usage rows: parcels wonder, verifiers
  spark). Owed: kit-zip sha256, standing-rules confirmation.
- Incident handling: HELD. New incidents (dead first exp2
  verifier, aug x3 attempts, site pair_call/shape breaks, demo
  nibbles, metrics F1-F4) each recorded with a corrective rule
  or fix; multi-session folds disclosed per agent+model.

## 3. Candidate corrections.jsonl rows, Waves 4-5 (sourceable only)

| # | wave | brief (corrected) | by | at | one-line text | accepted | source |
|---|------|-------------------|----|----|---------------|----------|--------|
| C1 | wave5 | parcel-w5metrics | verifier-w5metrics | 2026-10-29 | usage verifier-w5exp2 model wonder->spark | true (row = spark at bc807e6) | `ledger/verifier-w5metrics.md:42` + `docs/metrics/usage.jsonl` |
| C2 | wave5 | parcel-w5metrics | verifier-w5metrics | 2026-10-29 | usage verifier-extractor output_tokens 84350->34350 | true (row = 34350) | `ledger/verifier-w5metrics.md:44-46` + usage.jsonl |
| C3 | wave5 | parcel-w5metrics | verifier-w5metrics | 2026-10-29 | briefs parcel-w5exp2 base 5a80126->4a80126 | true (row = 4a80126...) | `ledger/verifier-w5metrics.md:47-48` + briefs.jsonl |
| C4 | wave5 | parcel-w5metrics | verifier-w5metrics | 2026-10-29 | passes verifier-w5aug sent_back true->false | true (row = false) | `ledger/verifier-w5metrics.md:49-50` + passes.jsonl (fix commit unsourced) |
| C5 | wave5 | parcel-w5twiddledoc | verifier-w5twiddledoc | pre-merge 2026-10-28 (ledger undated; fix `a41f026`) | TWIDDLES.md:370 kiss_fftr.c sha 56->64 chars | true (fixed on branch, merge cites it) | `ledger/verifier-w5twiddledoc.md:15-18` + commit `a41f026` + merge `97d1cbe` |
| C6 | wave5 | parcel-w5readme3 | verifier-w5readme3 | 2026-10-29 (merge `5a387e5` 13:53; ledger undated) | README headline 859->849 + 7 sibling findings | true (498a916 + `5a387e5`) | `ledger/verifier-w5readme3.md:21-30` + commits `498a916`/`4f39357` |
| C7 | wave5 | parcel-w5site | verifier-w5site | pre-merge 2026-10-28 (ledger undated) | F1-F5 (flag chips, data.json 80v75, landed-claim, URL, unmodified panel) | partial (pair/shape breaks fixed at `5a387e5`; residue unclear) | `ledger/verifier-w5site.md:19-29` vs merge `3a09c76` "no non-plant defect" |

Unsourceable suspicions (NOT rows — listed separately):
- U1. verifier-w5demo's 5 findings (nibbles, `fetch.py:188`
  `if False:`, `host_ok` never updated, `cache2/` gitignore) read
  genuine, but merge `eac88b0` claims "5 of 5 caught ... no
  non-plant defect". Resolution needs the scratch demo reports;
  out of bounds for this audit.
- U2. verifier-w5aug's disproved HEAD claims (pool "0
  mismatches", "six mutants refused",
  `ledger/verifier-w5aug.md:46-48`) are plant fallout on the
  planted copy, not parcel corrections — excluded with reason.
- U3. C4/C6/C7 fix commits and exact finding timestamps are
  unsourced (ledgers carry dates without times); the findings
  and their absence/correctness at `bc807e6` are sourced.

## 4. Remaining submission debts (cheapest honest disposition each)

- D1. corrections.jsonl frozen at 16 rows -> append C1-C7
  (one pass, sources above; U1-U3 stay out).
- D2. 65 old plants rows `checked_by: integration` -> RECORD
  erratum restating as lead-run (append-only, à la `4ceffa9`).
- D3. 8 old planted `sent_back: true` + 58 new rows missing the
  field -> same erratum (true only on proven revision rounds).
- D4. `README.md:141-144` + `docs/HARNESS.md:23` false
  universals -> restate at the next merge (parcels +
  named lead work planted-verified; wiring/record gated by
  `standard` + auditors; `ledger.sh` the sanctioned, not only,
  writer) + claim-surface diff in the merge gate.
- D5. README plants pin 109/115@`e9c57fb` -> re-pin
  114/120@`bc807e6` at the next merge.
- D6. Key-hash pre-commitment never adopted -> going-forward:
  hash-only commit pre-dispatch (WORKFLOW step 3) + one
  `plants.jsonl`-off-limits line per verifier brief.
- D7. Per-wave reveal history -> undisclosable-undo; keep the
  shapes-readable caveat in RECORD (one sentence).
- D8. 36/91 first-parent bodies lack ledger refs -> future-only
  rule; no history rewrite.
- D9. RECORD `26e86ce` 1-deletion reflow -> leave; note in the
  D2/D3 erratum.
- D10. Kit-zip sha256 + standing-rules line-by-line ->
  two one-line owner questions (P1 already re-confirmed
  2026-10-28 per `ledger/briefs/w5-aug.md:19-22`).
- D11. Unbindable 2,880-min trig box + missing ceilings ->
  cap boxes / require ceilings in the next brief template.
- D12. 7 study/audit briefs rows -> leave honestly
  not-reconstructed (parcel-w5metrics rule 6).
- D13. Board-lock/serial evidence only in off-limits ledger ->
  next silicon run cites lock + serial in a parcel/verifier
  ledger so a read-only auditor can verify.
- D14. No independent integration role -> keep the honest
  `lead-merge` label going forward (cheaper than dispatching
  the role; the erratum covers history).
- D15. Merge-time gate logs uncited by path -> cite log paths
  in merge bodies going forward.

## Not audited (sampling boundaries)
- Kit METHOD texts not re-read whole (prior audit's readings
  reused); case studies/examples/archives via citations only.
- No gate re-run; verifier/parcel counts taken as reported;
  re-derivations limited to the two scripts + targeted JSONL/git
  queries named above. `plant.py check` not executed (needs key
  contents). Transcripts/session logs unopened (usage rows checked
  for shape/consistency only). Board hardware not run. Push
  timing rests on bodies, not remote queries. Anything after
  `bc807e6` is outside this audit.
