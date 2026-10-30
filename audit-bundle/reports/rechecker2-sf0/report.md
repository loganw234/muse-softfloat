# rechecker2-sf0 report — SF-0 draft 3 (828b8f1), scoped re-check, disconfirm-only

Verdict: **READY**. (a) 0. (b) 0. Notes: 1 (carried, non-blocking).
Target: `828b8f13e63351ecdce5ca94a0550b4545a35160` in `muse-softfloat/`
(amended commit; parent `2bac8e9`). One file changed vs draft 2:
`docs/studies/SF-0.md`, 21 insertions, 9 deletions (819 lines total;
807 + 21 - 9 = 819 checks out). No project file touched by this
rechecker; all probes read-only. Ledger append was **blocked**
(bash spawn denied — see Method), so the ready-made body waits at
`scratch/rechecker2-sf0/ledger-body.txt` for the lead to append; no
ledger file touched directly. Stance: disconfirm only. I went looking
for survivors and new breakage and found none that blocks: F1/F2 and
three of the four notes are fully fixed in tree and message, the fourth
note is narrowed but accurately described, and the draft-3 diff adds no
new false sentence.

## Method and environment limits

Read `ledger/verifier-sf0.md`, `ledger/rechecker-sf0.md`,
`scratch/verifier-sf0/report.md`, and `scratch/rechecker-sf0/report.md`
first, then formed my own view from the full draft-3 file (819 lines,
read whole in three windows) and the complete `4f7f870..828b8f1` diff
(69 lines / 4260 bytes, read whole). Corroborated against ledger stamps
(`ledger/lead.md` 12:06:41 + 12:26:47, `ledger/sf0-evidence-auditor.md`
12:37:24, `ledger/verifier-sf0.md` 13:16:25), S3 section 4.1 (for the
new READ tag only), and the rechecker-sf0 staged body. Never read
`scratch/lead/` or any other non-allowed scratch; nothing with `cft`
in its name opened, searched, or listed; spawned nothing; no background
work exists to stop.

Tooling route (stated exactly): Windows PowerShell for all probes —
`bash.exe` exists on PATH (`C:\Windows\system32\bash.exe`) but spawning
it failed once (exit -1, empty output) and was not retried, so kit
`tools/ledger.sh` could not run here either. Every git probe ran as
PowerShell with identical argv and `git -c
safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat`
per call; git config never touched. Probe commands are recorded as
`scratch/rechecker2-sf0/r1.sh` (Git Bash form, same argv as executed).

Hash hygiene: short hashes resolve cleanly (`4f7f870` ->
`4f7f870818eb2a0e736af264bb069f6306c7d744`; `33c59f9` ->
`33c59f9f971f95715dc3bdcc3a2c8dfd3595272`; `828b8f1` ->
`828b8f13e63351ecdce5ca94a0550b4545a35160`). Both prior reports carry
single-character transcription typos in the printed full hashes
(rechecker-sf0: extra `d` in draft-2 `...069df6306...`;
verifier-sf0: dropped `b` in draft-1 `...3a2c8dfd...`). Harmless —
short-hash resolution plus `rev-parse` above is the ground truth — but
future citations should copy from `rev-parse`, not from those reports.

## (1) F1/F2 and the four notes: fixed in tree AND in the message

- **F1 (question count) — FIXED both sides.** Tree holds nine numbered
  questions (Q12.1–Q12.9, file lines 721–750; `9.` is `Settled-in-body
  choices`, lines 750–759). Commit message (`git log -1 --format=%B`
  on 828b8f1, saved to `commitmsg.txt`) reads `nine numbered approval
  questions for Logan`. The old `eight` appears nowhere in tree or
  message (sweep: 0 hits).
- **F2 (no-substance-changed) — FIXED in tree.** Section 14 lines
  805–806 now read `No proposal reversed; corrections and obligations
  added in this pass are the design detail listed above.` The old
  sentence (`No proposal's substance changed except removing ...`)
  has 0 hits file-wide. The message describes F2 accurately as
  history (`a no-substance-changed claim in SF-0 Section 14`).
- **N-i (Sections 0.8/8 cite) — FIXED.** Q12.9 line 756 now reads
  `toolchain pins of Sections 0 (items 7-8) and 8`. `Sections 0.8/8`
  has 0 hits. Referents exist: §0 items 7–8 (lines 66–76), §8 whole.
- **N-ii (SDK-baseline pointer) — FIXED both sides.** Section 14 lines
  804–805 now read `whose production P0 item 9 now tasks`, and P0
  item 9 (lines 582–585) was strengthened in the same diff to task
  `producing the SDK-harness bootrom/libgcc baseline numbers those
  reports quote`. Old `assigned to P0 item 9` wording: 0 hits. This
  closes the mispointing, not just the sentence: production is now
  explicitly tasked where the pointer lands.
- **N-iii (partial N10 tagging) — NARROWED, accurately described,
  residual carried as the single note.** Two tags added exactly as
  the draft-3 paragraph claims: decimal design wrapped as `(proposal,
  to be built and gated in P0 before any decimal parcel)` (lines
  435–436), ROM averages tagged `(READ: ...)` (lines 639–640; tag
  matches S3's own `READ` on section 4.1 and the numbers `_fadd`
  71 / `_ddiv` 183 check out against S3 lines 542/554). Residual:
  §8's 2× budget (an explicit goal, so the §0 promise's `where the
  distinction matters` arguably excuses it) and per-sentence
  claim-level tags on §4.3 recipe details remain untagged. The
  paragraph claims only the two added tags, so it does not overclaim;
  non-blocking, same as before.
- **N-iv (stale What-occurred) — FIXED.** Message now reads `Draft 1
  wrote docs/studies/SF-0.md ...` plus `Drafts 2-3 in this amended
  commit restate the two Spark send-backs below.` No `Wrote ...
  (draft 1)`-while-holding-draft-2 staleness remains.

Commit message vs reality (all TRUE): `(a) 0, (b) 6, notes 15`
(matches verifier ledger + report N1–N15); `(a) 0, (b) 2, notes 4`
(matches rechecker ledger + report); stamps verifier `2026-10-26
13:16:25 -0700`, audit `2026-10-26 12:37:24`, lead `12:26:47`
drafting + `12:06:41` Wave-0 (each confirmed against its ledger
file); `1205 lines` for the auditor report (reused from
rechecker-sf0's exact re-measurement — auditor scratch not re-opened
per scope limits); `Section 14 keeps each pass's counts beside the
changes` (lines 784–786, 808–810 do); `Draft 3 ... fixes those and
its notes` (verified above); `Re-check 2 scoped to draft 3 follows`
(this task).

## (2) The draft-3 diff: nothing newly false

Five content hunks, all clean: (a) decimal `(proposal...)` wrapper —
a status clarification of the already-accepted `P0 deliverable`
wording, no tier/claim movement, and compatible with §14's `now
designed` (designed-but-unbuilt proposal); (b) P0 item 9 baseline
production — new obligation, consistent with §8's `SDK's own
RAM-resident benchmark methodology is the comparison shape`; (c)
`(READ: ...)` on ROM averages — verified true against S3; (d) Q12.9
citation fix — trivially correct; (e) §14 rewrite + new draft-3
paragraph. The paragraph's every checkable clause verified: counts
`(a) 0, (b) 2, notes 4` match; report path exists (17,325 bytes);
`ledger entry filed by the lead from the rechecker's staged body`
corroborated (`ledger-body.txt` 1,254 bytes matches the entry text,
and bash-denial is reproduced in this session); all four named
corrections present in tree; closing `No conformance proposal changed
in this pass` TRUE (no rounding/flag/NaN/tier/authority sentence
touched). Own fault hunt in touched sentences (proposal-vs-designed
tension, `tasks` verb, double-`and` in Q12.9 line 756, READ-tag
scope, `corrected ... at commit time` phrasing): all cleared, none
filed.

## (3) Whole-file sweeps: no B-claim survives in any variant

Zero hits file-wide for each: `before rounding`; `emax + 2`;
`all MEASURED`; `invalid signaled`; `Sections 0.8/8`; `eight numbered
approval`; `No proposal's substance changed`; `assigned to P0 item 9`;
`(draft 1)`; `canonical quiet NaN`. `augmented` occurs only in the
corrected three-item form (line 272) plus §14 history. `after
rounding` is uniform (lines 56/190/198/752 + §14). `integer...binary16`
occurs only in the corrected fallback (lines 130–134, routed via
arithmetic formats).

## Commands run (read-only)

1. `git log --oneline --all` (3 commits) + `rev-parse` on all three
   shorts (full hashes above); `log -1 --format=%B 828b8f1` saved to
   `commitmsg.txt`.
2. `diff --stat/--numstat 4f7f870 828b8f1` → `21 9, 1 file`; full diff
   saved to `full.diff`, read whole (69 lines).
3. Full draft-3 read (819 lines, three windows); targeted re-reads of
   §§4.3/5.2/P0-9/8/Q12.9/14.
4. Granted-reader regex sweeps quoted in §(3); Q12 numbering count
   (nine `^[0-9]. **` hits in §12, lines 721–750).
5. Stamp greps in `ledger/` (all four confirmed); `ledger-body.txt`
   read (matches entry); S3 §4.1 read (READ tag + 71/183 confirmed);
   line counts (`SF-0.md` 819, `rechecker-sf0/report.md` 17,325,
   `ledger-body.txt` 1,254 bytes).

## What was not done (limits)

- Bash spawn denied session-wide, so kit `tools/ledger.sh append`
  could not run: **no ledger entry was written** (nothing
  hand-appended, per the tools-only rule); `ledger-body.txt` staged
  for the lead. Single `bash --version` spawn attempted once (exit
  -1, no output), not retried.
- Auditor report not re-opened (outside allowed scratch); its
  1205-line count is reused inspected evidence from rechecker-sf0.
- S1's 81-name enumeration and the licensed IEEE PDF not re-verified
  (prior-verified authorities reused as scoped). No builds/board work
  (textual study). No other-agent scratch read; no `cft` contact; no
  processes started, none to stop.

Report path: `scratch/rechecker2-sf0/report.md` (this file).
Ledger intent: `ledger/rechecker2-sf0.md` via kit `ledger.sh` —
BLOCKED, body staged at `scratch/rechecker2-sf0/ledger-body.txt`.
