# parcel-w6popups — generalise the chase popup cards (report)

Branch `wave6-popups`, base `f01dc96`. Brief
`ledger/briefs/w6-popups.md`. Work confined to
`worktrees/w6-popups`; only owned files changed:
`video/segments/gitvisual.py` (`POPUP5` strings + comment),
regenerated `video/segments/gitvisual7.mp4`,
`docs/metrics/briefs.jsonl` (own row, wave `wave6`, binary-append).
No assembly; no audio touched.

## (a) Before/after copy table (per-card POPUP_WORDS identical)

Word counts use the file's own `word_count` (whitespace split).
Base budgets: `[7, 9, 8, 8, 11, 9, 9]` — new copy hits each exactly.

| # | before (words) | after (words) | count on the card: derivation + source |
|---|---|---|---|
| 0 | PARCEL (1) / "173 binary32 routines" (3) / "one file: msf32.c" (3) = 7 | PARCELS (1) / "work is divided" (3) / "20 parcels total" (3) = 7 | 20: `docs/metrics/passes.jsonl` rows with `role==author` = 20 at HEAD (script `derive_counts2.py`); frozen `process_graph.json` `accounting.by_passes_role.author` = 20 = 19 author lanes + the wave0 lead spine whose `passes_role` is `author` (replay draws all 20: 19 teal lanes + blue spine) |
| 1 | ESCALATION (1) / "tiny results packed wrong" (4) / "fixes: 53acb1a / b37fb12" (4) = 9 | ESCALATIONS (1) / "questions go up to lead" (5) / "3 escalations total" (3) = 9 | 3: frozen lane `by_role.fixer` = 3 = HEAD passes `fixer` = 3; the replay draws 3 red fixer lanes. `docs/metrics/escalations.jsonl` holds 20 individual filings (messages, counted by script) — context only, not drawn episodes |
| 2 | VERIFIER (1) / "SHA-256 too short" (3) / "56 characters, needs 64" (4) = 8 | VERIFIERS (1) / "recheck every parcel independently" (4) / "36 verifiers total" (3) = 8 | 36: frozen lane `by_role.verifier` = 36 = HEAD passes `verifier` = 36; replay draws 36 verifier lanes |
| 3 | PLANTS (1) / "9/10 planted bugs caught" (4) / "one miss, harmless" (3) = 8 | PLANTS (1) / "traps test the checkers" (4) / "150 planted bugs" (3) = 8 | 150: frozen `process_graph.json` `accounting.plants_rows` = 150 (110 mapped, drawn as 110 ticks: 105 caught / 5 missed; 30 plant verifiers, 22 mapped). HEAD `docs/metrics/plants.jsonl` = 155 lines (mechanical line count, contents unopened): +5 from verifier-w6filmretime grades landed in `8ce5f27`, after the graph prep. HEAD grades by mechanical grade-field count only: 148 caught / 7 missed. Card carries the frozen-graph-consistent 150 |
| 4 | GATES (1) / "52,168 quick + 1,117,504 standard tests" (6) / "chip matches computer exactly" (4) = 11 | GATES (1) / "nothing merges unless all green" (5) / "411,213 smoke + 1,117,504 standard" (5) = 11 | 411,213: mechanical `awk '!/^#/ && NF>0' tests/vectors/*.vec` (= run.sh `$VECS`) = 411213; `docs/RECORD.md` wave5-close "committed total 411,213"; this parcel's `standard` run `build/standard/verify.log` prints `total 411213 passed 411213`. (Base "52,168" was the wave1 smoke total, RECORD line 367.) 1,117,504: run.sh `standard()` generates f16-exhaustive (917,504 lines) + pack-sweep (200,000 lines, seed-priced); RECORD "standard adds 1,117,504"; this run `build/standard/verify-standard.log` prints `total 1117504 passed 1117504` |
| 5 | STUDY (1) / "try in scratch first" (4) / "two studies wait ahead" (4) = 9 | STUDIES (1) / "scout the ground before building" (5) / "35 studies total" (3) = 9 | 35: frozen lane `by_role.surveyor` = 35 = HEAD passes `surveyor` = 35; replay draws 35 surveyor lanes |
| 6 | LEAD MERGE (2) / "finished work joins main" (4) / "first merge: 2843792" (3) = 9 | MAIN (1) / "finished work joins here" (4) / "25 merges to main" (4) = 9 | 25: frozen `history.json` `merges_into_main` = 25 (`merge_count` 27; `accounting.git_merges_into_main` 25 = 19 author-owned + 6 lead-only). Title MAIN is the legend's "main" half (the slash form "LEAD / MAIN" is 3 tokens and would have forced a weaker count line; "lead" is still named on card 1) |

Copy rules: titles 1 word (legend plurals, or the legend's "main");
lines <= 6 words; no hashes, file names, or per-example numbers in
line 1 (all such specifics removed); every claim is shown by the
replay that follows (episode lanes, plant ticks, merges).
Timings below are records, never performance claims.

## (b) Timing-constant equality proof

`dump_timings.py` imports the module and prints `POPUP_WORDS`,
`POPUP_DWELL`, `ARRIVALS`, `T_BRIDGE`, `T_REPLAY`, `SHIFT`, `TOTAL`,
`T_BOX`/`T_FADE`, `GATES` (rank/t0/t1), `LEGS`, and `POPUP5`.
Before dump: `before_timings.txt` (run on base `f01dc96` before the
edit). After dump: `after_timings.txt`. First 11 lines of both files
are byte-identical (`fc.exe` shows differences only inside the
`POPUP5` copy section):

```
POPUP_WORDS [7, 9, 8, 8, 11, 9, 9]
POPUP_DWELL [4.0, 5.0, 4.5, 4.5, 5.5, 5.0, 5.0]
ARRIVALS [6.5, 11.5, 17.5, 23.0, 28.5, 35.0, 41.0]
T_BRIDGE 46.0
T_REPLAY 48.5
SHIFT 17.5
TOTAL 108.0
T_BOX 96.5 T_FADE 106.0
GATES [(44.0, 56.5, 65.5), (69.0, 70.5, 79.5), (140.0, 86.5, 95.0)]
LEGS [(48.5, 56.5, 0.0, 44.0), (65.5, 70.5, 44.0, 69.0), (79.5, 86.5, 69.0, 140.0)]
```

The film stays sealed at 185.0 s native: no timing moved.

## (c) Render probe + stills

Render: `render_gitvisual.sh` (Git Bash, `MSF_PYTHON` = workspace
`.venv` python), 3240 frames, `DONE rc=0 ... 50.6 MB wall 193s`.
Probe `probe_mp4.py` (two routes — ffmpeg header text, and decoded
frame count + first-frame shape via imageio):

- `Duration: 00:01:48.00`, `2560x1440`, `30 fps`, no `Audio:` stream
- decoded frames 3240 (= 108.0 * 30); frame0 shape (1440, 2560, 3)
- `MP4 PROBE: PASS`

Stills `make_stills.py`, one per card at mid-dwell (card fully up):
card0 t=8.50, card1 t=14.00, card2 t=19.75, card3 t=25.25,
card4 t=31.25, card5 t=37.50, card6 t=43.50 (`stills/*.png`).
All 7 viewed: title + 2 lines inside the card, no overflow, title
and lines legible at 1440p, border colour matches the LEGEND system.

## (d) Cursor/gate spot check

`check_cursor.py` (import at the new render): cursor exactly on each
gate rank at its t0 — `(44.0 @ 56.5, 69.0 @ 70.5, 140.0 @ 86.5)`,
`TOTAL 108.0`, cursor monotonic over the film. `CURSOR SPOT CHECK: PASS`.

## (e) `tools/run.sh standard` in the worktree: PASS

`run_standard.sh` (Git Bash, pinned `MSF_PYTHON`):
`budget standard: PASS in 74s (logs in build/standard/)`,
`STANDARD_EXIT=0` (full log `run_standard.log`). Corroborating card
totals from its inventory: smoke `total 411213 passed 411213`,
standard extras `total 1117504 passed 1117504` (917,504 f16-exhaustive
+ 200,000 pack-sweep), aug pool `total=5505024 mismatches=0`,
unit PASS, 9/9 negative controls refused, tier inventory 783/783 +
66/66.

## (f) Diff vs base limited to owned files

`git diff --stat f01dc96 -- .` after all work:

- `docs/metrics/briefs.jsonl` (+1 row, this parcel)
- `video/segments/gitvisual.py` (13 insertions, 11 deletions: POPUP5 + comment only)
- `video/segments/gitvisual7.mp4` (regenerated, 50,568,834 -> 50,550,833 bytes)

`git status --short` shows only those two modified tracked files
besides the briefs row (build artefacts are git-ignored). No
assembly produced; `video/assemble.py` untouched; audio untouched.
No file with `cft` in its name was created; `plants.jsonl` row
contents were never opened (only mechanical line/grade-field counts,
totals cited above).

## Scripts (all in this dir, Git Bash + pinned MSF_PYTHON)

`dump_timings.py`, `before_timings.txt`, `after_timings.txt`,
`derive_counts2.py`, `render_gitvisual.sh`, `render_gitvisual.log`,
`check_cursor.py`, `probe_mp4.py`, `make_stills.py`, `stills/`,
`run_standard.sh`, `run_standard.log`, `append_brief.py`.
(`probe_mp4_tmp.py` is a one-line superseded stub.)

## Fixer send-back (lead brief `ledger/briefs/fix-w6popups.md`, one commit on `wave6-popups`)

Only the two popup-card counts the lead named; everything else in
the parcel stands (timing freeze held, stills clean, standard PASS).

### (a) Before/after copy for the two cards, with recounts

Word counts use the file's own `word_count` (whitespace split).
Budgets unchanged: card 0 = 7, card 1 = 9.

| # | before (words) | after (words) | recount quoted with source |
|---|---|---|---|
| 0 | PARCELS (1) / "work is divided" (3) / "20 parcels total" (3) = 7 | PARCELS (1) / "work is divided" (3) / "19 parcels total" (3) = 7 | 19: frozen `video/segments/process_graph.json` `accounting.by_role.author` = 19 (script `fix_recount.py`); `accounting.by_passes_role.author` = 20 only because it includes the wave0 lead spine (`kind spine, agent lead, passes_role author`). The replay draws 19 author-role parcel lanes, so the 20th "author" pass (the lead's own spine episode, not a parcel) left the card. HEAD `docs/metrics/passes.jsonl` still counts `role==author` = 20 for the same reason |
| 1 | ESCALATIONS (1) / "questions go up to lead" (5) / "3 escalations total" (3) = 9 | ESCALATIONS (1) / "questions go to lead" (4) / "20 filed, 3 fixes" (4) = 9 | 20 filings: `docs/metrics/escalations.jsonl` = 20 rows by wave — wave1: 5, wave2: 3, wave3: 6, wave4: 4, wave5: 2 (script `fix_recount.py`), all inside the frozen window. 3 fixes: frozen `by_role.fixer` = 3 lanes, the red fixer lanes the replay draws. The old card paired a filings description ("questions go up") with a fixer-lane count (3); the new card names both numbers, one per clause, inside the same 9-token budget (lead's preferred fit, adopted verbatim) |

Copy rules still hold: titles 1 word; lines <= 6 words; no
hashes, file names, or per-example numbers in line 1.

### (b) Timing-equality dump identical to base

`fix_dump.sh` re-ran `dump_timings.py` in the worktree after the fix
(`scratch/parcel-w6popups/fix_after_timings.txt`); `fix_compare.py`
decodes the parcel's UTF-16 base dump and the new dump and compares:
first 11 lines byte-identical to base `f01dc96`
(`POPUP_WORDS [7, 9, 8, 8, 11, 9, 9]`, `POPUP_DWELL`,
`ARRIVALS`, `T_BRIDGE` 46.0, `T_REPLAY` 48.5, `SHIFT` 17.5,
`TOTAL` 108.0, `T_BOX`/`T_FADE`, `GATES`, `LEGS`) —
`TIMING_EQUALITY_PASS`. The only differing dump lines are the two
fixed `POPUP5` card strings. (One supporting note: an early
normalisation attempt with shell `tr` ate every letter `r`; it was
discarded and the proof re-done with the UTF-16-aware `fix_compare.py`
above — the committed evidence is the clean run.)

### (c) Regenerated mp4 probe + stills of the two changed cards

Render: `render_gitvisual.sh` (Git Bash, `MSF_PYTHON` = workspace
`.venv` python), 3240 frames, `DONE rc=0 ... 50.5 MB wall 178s`.
Probe `probe_mp4.py` (same two routes — ffmpeg header text, decoded
frame count + first-frame shape via imageio):

- `Duration: 00:01:48.00`, `2560x1440`, `30 fps`, no `Audio:` stream
- decoded frames 3240 (= 108.0 * 30); frame0 shape (1440, 2560, 3)
- `MP4 PROBE: PASS`

Stills re-rendered with the fixed copy (`make_stills.py`); the two
changed cards viewed at mid-dwell: card0 t=8.50 (`card0_PARCELS_t8.50.png`,
"19 parcels total") and card1 t=14.00 (`card1_ESCALATIONS_t14.00.png`,
"20 filed, 3 fixes") — title + 2 lines inside the card, no overflow,
legible at 1440p, border colour matches the LEGEND system
(teal parcels, red escalations).

### (d) Restated rows

- `docs/metrics/briefs.jsonl` (worktree): the parcel's own
  `parcel-w6popups` row restated in place (byte-level substring swap,
  `fix_restate2.py`; CRLF bytes elsewhere untouched) from
  "(20 parcels, 3 escalations," to
  "(19 parcels, 20 escalation filings with 3 fixes," — still 39 rows,
  `git diff` is exactly 1 insertion / 1 deletion.
- This report: this fixer section appended. Ledger
  `ledger/parcel-w6popups.md`: counts restated (see that file).

### (e) `tools/run.sh standard` not re-run

The fixer diff vs the parcel tip is copy-strings only
(`gitvisual.py` 2 lines), the regenerated mp4, and the restated
briefs row — the same passing tree the parcel's standard run already
covered (PASS in 74 s, smoke total 411,213, standard extras total
1,117,504). No code, vector, or harness path changed, so standard was
not re-run; stated, not verified afresh.

### Fixer diff vs parcel tip `0708e2e` (owned files only)

- `video/segments/gitvisual.py` (2 insertions, 2 deletions: the two
  POPUP5 card strings; CRLF endings preserved)
- `video/segments/gitvisual7.mp4` (regenerated, 50,550,833 ->
  50,547,482 bytes)
- `docs/metrics/briefs.jsonl` (1 restated row, in place)

No assembly produced; `video/assemble.py` untouched; audio untouched.
No file with `cft` in its name was created.

### Fixer scripts (all in `scratch/parcel-w6popups/`, Git Bash + pinned MSF_PYTHON)

`fix_recount.py`, `fix_dump.sh`, `fix_after_timings.txt`,
`fix_compare.py`, `fix_restate2.py`, `fix_eol_check.py`.
(`fix_restate.py` is superseded: it normalised the file's CRLF
endings to LF and was reverted — `fix_restate2.py` is the run of
record. `fix_before_u8.txt` / `fix_after_u8.txt` /
`fix_parcelafter_u8.txt` intermediates from the discarded attempt were
removed.)
