# parcel-w6captions report — captions + stills for the final cut

Branch `wave6-captions`, base `cdc40aec9b11eeab61ab3c6cc9940b5dbbac4a67`,
worktree `worktrees/w6-captions`. Brief: `ledger/briefs/w6-captions.md`.

## Retry circumstances

A previous attempt died on a provider quota error leaving four
UNCOMMITTED drafts in the worktree: `video/captions.py`,
`video/out/assembly_v6.srt`, `video/out/assembly_v6.vtt`,
`video/out/stills_v6/` (30 PNGs + INDEX.md). Per the retry brief I
treated them as untrusted: I re-ran the generator from scratch
(`captions.py`, then `captions.py --validate`, then
`captions.py --stills`), re-proved byte-stability, and re-validated
every acceptance probe myself. Outcome: the drafts were sound — the
fresh runs reproduce them exactly (same .srt/.vtt byte counts
5323/5112, same 30 still filenames/times), and every probe below
passes on the regenerated artifacts with zero content fixes needed.
No mismatches were found, so none were "noted instead of fixed";
there was simply nothing to fix.

## Deliverables (all generated, reproducible)

- `video/captions.py` — derives cues from the segment modules' own
  audit data (imports `assemble`, `idea`, `why`, `intro_outro`,
  `gitvisual`; native offsets derived from `assemble.SEGMENTS`/
  `assemble.ORDER`: intro 0, idea 7, why 33, gitvisual 65, outro 173,
  total 185.0 s; scaled x120/124 to 179.03 s). Header states the
  inclusion rule (readable headline/body beats in sequence) and the
  named exclusions (HUD counters, ticker, branch/lane/marble labels,
  retained-plate label, hashes/check-values, legends, source tags,
  phone chrome, gate-window interiors except the title bar). The one
  beat no audit table expresses (gitvisual opening headline) is the
  single `EXTRA_CUES` entry with its source named
  (`gitvisual.draw_opening` inline literal, times from imported
  `T_BOX`/`PACK_DIM_LT`).
- `video/out/assembly_v6.srt` (5323 bytes) + `video/out/assembly_v6.vtt`
  (5112 bytes), byte-stable across re-runs (proven below).
- `video/out/stills_v6/` — 30 stills `NN_t<sec>_<slug>.png` +
  `INDEX.md`, grabbed from the committed `assembly_v6.mp4`.
- One-line `video/README.md` layout-table pointer for `captions.py`
  (the brief's allowed single line; says so here as required).
- `docs/metrics/briefs.jsonl` own row (wave "wave6"), binary-appended
  (40 rows total; `git diff` shows exactly +1 line, prior bytes intact).

## Acceptance

(a) Strict parse: `captions.py --validate` re-parses both files:
`validate: PASS (77 cues, srt == vtt == generated, monotonic, no
overlaps, 0 < start < end <= 179.03s)`. Cue split:
intro=1 idea=25 why=32 gitvisual=11 outro=8. VTT escaping verified
by the parser (`true bar <1 px wide` ships as `&lt;`; raw `<>`
rejected). Byte-stability: two consecutive runs give identical
sha256 — srt `490568F222663F1D792134018458FD489F2AB754C2283B8CC72124834A6C4590`,
vtt `AA53BC4D3BE781131410A3F302BFBC84DE7C9EE66BF0D34857D91B2CAB992CE0`.
Assembly probed at 179.03 s / 2560x1440 / 30 fps / 5371 frames
decode rc 0, so the `<= 179.03` cap is the true container length.

(b) Sampled truth check: 15 cues over all five segments (req: >= 12),
frame grabbed at each cue midpoint from `assembly_v6.mp4` (scripts:
`scratch/parcel-w6captions/sample_pick.py`,
`grab_probe_frames.py`; frames in `probe_frames/`). All 15 viewed;
every cue text is the readable text on screen at its midpoint:

| cue | seg | mid (s) | frame shows | cue text | verdict |
|---|---|---|---|---|---|
| 1 | intro | 2.904 | phone bubble "Hey Muse, I've got an idea..." | same | MATCH |
| 6 | idea | 10.403 | card line "Same answer everywhere." (new beat; earlier beats persist) | same | MATCH |
| 12 | idea | 15.967 | "Exact, not close." landed at bottom | same | MATCH |
| 19 | idea | 21.774 | KISSFFT card "Correctly rounded / sinPi/cosPi" | same | MATCH |
| 34 | why | 37.258 | spec row 7 "Exact leftovers (augmented)" | same | MATCH |
| 41 | why | 43.548 | "ELIMINATED" stamp (source tag `(SF-0 §8)` visible, correctly without a cue) | same | MATCH |
| 49 | why | 50.322 | "NOT MEASURED" stamp | same | MATCH |
| 54 | why | 56.855 | "SO BUILD THE FOURTH OPTION / MUSE-SOFTFLOAT" (rows not yet landed) | same | MATCH |
| 59 | git | 71.129 | "PARCELS / work is divided / 19 parcels total" | same | MATCH |
| 62 | git | 87.338 | "PLANTS / traps test the checkers / 150 planted bugs" | same | MATCH |
| 66 | git | 121.936 | gate title bar "IAS15 RUNS ON THE CHIP" (hashes/counters/ticker visible, correctly cue-excluded) | same | MATCH |
| 69 | git | 160.190 | headline "every system drops in, kept" ("marbles in: 3/7", marble labels visible, correctly excluded) | same | MATCH |
| 70 | outro | 170.565 | reply bubble "Done — it held up." (reply 2 mid-typing "Identi") | same | MATCH |
| 72 | outro | 172.258 | "HUMAN : AI SPLIT / PROJECT 1,196,128,770 tokens" | same | MATCH |
| 77 | outro | 177.822 | stat card "6 boards / IAS15 · 2,001/2,001 checks" | same | MATCH |

15/15 match, zero mismatches to fix.

(c) Stills: all 30 viewed against their INDEX rows (phone message,
5 idea beats, 5 why beats, chase start, 7 popups, bridge, 2 replay
beats, 3 gate windows open with complete content, opening fall +
plate with "marbles in: 7/7", 3 outro beats). INDEX times
independently recomputed from the raw audit tables WITHOUT
`captions.build_stills` (`scratch/parcel-w6captions/verify_index.py`,
own formulas from BLOCKS/ARRIVALS/POPUP_DWELL/T_BRIDGE/T_REPLAY/
GATES/T_BOX/PANEL_T): 30/30 filenames + scaled/native/local times
match exactly. Stills regenerated via `captions.py --stills` in this
session (same 30 filenames/times as the drafts).

(d) `tools/run.sh standard` in the worktree (Git Bash, MSF_PYTHON =
workspace `.venv`): exit 0. Logs in `worktrees/w6-captions/build/
standard/`: smoke `total 411213 passed 411213 failed 0 / VERDICT:
PASS`; extras `total 1117504 passed 1117504 failed 0 / VERDICT:
PASS`; aug pool `VERDICT: PASS`; all negative controls refused.

(e) Diff vs base `cdc40ae` limited to owned files: modified
`docs/metrics/briefs.jsonl` (+1), `video/README.md` (+1); new
`video/captions.py`, `video/out/assembly_v6.srt`,
`video/out/assembly_v6.vtt`, `video/out/stills_v6/` (30 PNGs +
INDEX.md). No segment code, renders, assembly, or audio touched.
`build/standard/` logs are gitignored test residue, uncommitted.

## Commit

Tip commit on `wave6-captions` (detailed body + `Co-Authored-By:
Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>`), not pushed.
Nothing with `cft` in any name; `docs/metrics/plants.jsonl` never
opened.
