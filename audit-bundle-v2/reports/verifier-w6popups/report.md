# verifier-w6popups report — ParcelRound verify of `8507695` (parent `f01dc96`)

**Verdict: NOT READY.** The committed `video/segments/gitvisual.py` card
strings contradict the parcel ledger, the briefs row, the frozen source
data, and the committed `gitvisual7.mp4` on five of seven cards, and the
over-long STUDIES line breaks the timing freeze (code TOTAL 108.5 s vs
the sealed 108.0 s the mp4 actually has).

Copy: `worktrees/verify6-popups` (detached `8507695`, clean, never
modified). All work done in duplicate `worktrees/dup-v6popups` (detached
`8507695`), MSF_PYTHON = workspace `.venv` python, Git Bash for
`tools/run.sh`. Fences honoured: no parcel branch/worktree, no
`scratch/lead/`, no `scratch/parcel-w6popups/`, no `ledger/lead.md`, no
GitHub, nothing with `cft`; `docs/metrics/plants.jsonl` only counted
mechanically (lines + grade values), contents never opened.
Scripts: `scratch/verifier-w6popups/scripts/probe*.py`.

## Recounts (probe 1, all from the duplicate at 8507695)

Frozen graph `video/segments/process_graph.json` accounting plus direct
episode recount (scripts `probe1a/1b/1c/1d/1e`):

- 94 episodes = 93 `lane` + 1 `spine` (E001, agent `lead`, role `lead`,
  `passes_role` `author`, wave0). Drawn-lane roles: surveyor 35,
  verifier 36, author 19, fixer 3 (recounted from episodes; matches
  `accounting.by_role`). `by_passes_role`: author 20 (= 19 lanes +
  spine), surveyor 35, verifier 36, fixer 3. Spine is not a parcel lane.
- `history.json`: `merge_count` 27, `merges_into_main` 25; 25
  `target==main`, 2 into `w1-f32`/`w1-f64` (`9bb8723`, `80cbc97`).
  `commit_count_all` 141.
- `docs/metrics/escalations.jsonl`: 20 filings, waves 1–5 =
  5+3+6+4+2. Fixer lanes drawn: 3
  (`E033 regater-f32`, `E034 regater-f64`, `E088 parcel-w5twiddledoc`).
- Plants: graph `accounting.plants_rows` = **150**
  (`plants_verifiers` 30, mapped 110/22). Fenced file mechanical total:
  **155** lines (grades: caught 148, missed 7). Parcel discipline puts
  the frozen-graph-consistent count on the card and lists the delta.
- Gates: smoke = data rows (`!/^#/`, non-blank) summed over the exact
  51-file `VECS` list in `tools/run.sh` = **411,213** (matches live
  `verify.log`: `total 411213 passed 411213`). Standard extras from
  generator parts: `f16-exhaustive` = 65536 encodings × (1 class + 9
  `ref_preds` + copy/negate/abs/radix = 14) = **917,504**, plus
  `pack-sweep` N=**200,000** → **1,117,504** (matches live
  `verify-standard.log`: `total 1117504 passed 1117504`; `RECORD.md`
  records 1,117,504 four times; sanitize briefs row: 411213 + 1117504).
- `STUDY_LABELS` (code predicate) = 12, so the STUDIES "35" derives from
  surveyor lanes (35), not the label set.

Card truth table (code = imported `POPUP5`; mp4 = frames viewed at
§probe 3; true = recount above; row = briefs row 39):

| card | code string | mp4 shows | true value | row 39 |
|---|---|---|---|---|
| PARCELS | 20 parcels total | 19 parcels total | **19** drawn lanes | 19 ✓ |
| ESCALATIONS | 20 filed, 3 fixes | same | **20** filings + **3** fixer lanes | same ✓ |
| VERIFIERS | 35 verifiers total | 36 verifiers total | **36** lanes | 36 ✓ |
| PLANTS | 155 planted bugs | 150 planted bugs | **150** frozen-graph | 150 ✓ |
| GATES | 411,213 + 1,171,504 | 411,213 + 1,117,504 | **411,213 + 1,117,504** | 1117504 ✓ |
| STUDIES | scout the ground **very carefully** before building / 35 | scout the ground before building / 35 | **35** lanes; 9-word budget | 35 ✓ |
| MAIN | 25 merges to main | same | **25** into main | 25 ✓ |

Briefs row 39 numbers match every recount. The code matches the row on
only ESCALATIONS and MAIN.

## Timing freeze (probe 2, `probe2_timing.py`, by import)

Imported copy module vs parent (`f01dc96:video/segments/gitvisual.py`
from the copy's own git history; shared `style`/`data`/`scenes`
preloaded; data files identical since the diff touches only 3 files):

- `POPUP_WORDS`: copy `[7,9,8,8,11,11,9]` vs base `[7,9,8,8,11,9,9]`.
  STUDIES line is 1+7+3 = 11 (`scout(1) the(2) ground(3) very(4)
  carefully(5) before(6) building(7)`), budget is 9.
- Consequently ALL of `POPUP_DWELL` (`[4.0,5.0,4.5,4.5,5.5,5.5,5.0]`
  vs `[...,5.0,5.0]`), `ARRIVALS` (last two `35.0,41.5` vs
  `35.0,41.0`), `T_BRIDGE` (46.5 vs 46.0), `T_REPLAY` (49.0 vs 48.5),
  `SHIFT` (18.0 vs 17.5), `GATES` t0/t1 (+0.5 s each), `LEGS`, `TOTAL`
  (**108.5** vs **108.0**) differ. Ranks identical (44.0/69.0/140.0).
- Cursor checks on the copy module pass internally: `cursor_rank(t0)`
  equals each gate rank; monotonic non-decreasing over `[0, TOTAL]`.
  But the gates sit 0.5 s later than the sealed timeline the mp4 and
  the assembly were built against.

## Render truth (probe 3)

Committed mp4 (`probe3a/3b`): 108.0 s, 2560×1440, 30 fps, h264,
**no audio stream** (silent) ✓. Seven frames extracted at copy-code
mid-dwells (8.5/14.0/19.75/25.25/31.25/37.75/44.0) and viewed:

- Rendered text matches the **ledger/row numbers**, NOT `POPUP5`:
  PARCELS "19 parcels total", VERIFIERS "36 verifiers total", PLANTS
  "150 planted bugs", GATES "411,213 smoke + 1,117,504 standard",
  STUDIES "scout the ground before building / 35 studies total".
  ESCALATIONS and MAIN match the code. → exact-match rule fails on
  5 of 7 cards; code and artifact are out of sync (mp4 is the correct
  side; its 108.0 s duration equals the *base* TOTAL, i.e. the
  9-word-STUDIES timeline).
- Every card: text fully inside its card, no overflow, legible at
  1440p; titles match the on-screen legend (`parcels, verifiers,
  plants, gates, studies, escalations`, `MAIN` ↔ `lead / main`).
- So the mp4 is a *correct* render of strings the committed code does
  not contain.

## Copy discipline (probe 4)

Code strings are general (no hashes, file names, incident specifics),
headlines 1 word (≤6), lines ≤10 words. Truthfulness vs the replay the
parcel brief demands: code's 20/35/155 are not what the replay draws
(19 author lanes + lead spine; 36 verifier lanes; 150 graph plants),
and `1,171,504` matches no source anywhere (transposed digits of
1,117,504). The mp4/ledger strings pass: 19 lanes drawn; 20 filings +
3 fixer lanes (combo the fixer brief explicitly allows); 36 lanes;
150 frozen-graph plants; 411,213 + 1,117,504 gate volumes; 35 surveyor
lanes; 25 merges into main.

## Gate and scope (probe 5)

- `tools/run.sh standard` in the duplicate: **PASS in 60 s**
  (`budget standard: PASS`; smoke `total 411213 passed 411213
...[truncated 1583 chars]