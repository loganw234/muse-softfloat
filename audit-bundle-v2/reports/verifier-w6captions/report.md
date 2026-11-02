# verifier-w6captions report — ParcelRound verification of w6-captions

**Verdict: NOT READY** (5 blockers, 3 notes). Details below; numbered
findings F1–F8 at the end (blocker vs note marked).

Copy: `worktrees/verify6-captions`, detached HEAD
`c537e0d84410b5c6d7d6a5c01e776bd0523d4519`, parent `cdc40ae`.
The copy was never modified (reads + imports only). All generative
work ran in the duplicate `scratch/verifier-w6captions/work/`
(robocopy of the copy, `.git` excluded). Fences honored: no
`docs/metrics/plants.jsonl`, nothing with `cft`, no parcel
branch/worktree, no `scratch/lead/`, no `scratch/parcel-w6captions/`,
no `ledger/lead.md`, no GitHub, no board. Own scripts in
`scratch/verifier-w6captions/scripts/` (`strict.py`, `dumpcues.py`,
`grabframes.py`, `stillscheck.py`, `stillsbytes.py`), run under Git
Bash with `MSF_PYTHON` pinned to the workspace `.venv` python.
Assembly duration probed independently: **179.030 s** (limit 179030 ms).

## Probe 1 — Reproducibility: FAIL (blocker)

Running the copy's `video/captions.py` in the duplicate dies before
writing anything:

```
AssertionError: (191.16666666666669, 179.03)
```

Cause: `captions.py:64` carries `SCALE = 124.0 / 120.0` with the
comment "the assemble.py setpts tempo scale", and `_scaled()` (line
107-108) multiplies by it. `assemble.py:74` applies
`tempo = 120.0 / 124.0` (`setpts=PTS*0.9677419355`). The generator's
scale is the reciprocal of the assembly's: native total 185.0 s scales
to 191.17 s, tripping the `build_cues()` guard
`abs(_scaled(NATIVE_TOTAL_S) - ASSEMBLY_DUR_S) < 0.01` (line 162).
Offsets re-derive identically on both sides (intro 0 / idea 7 / why 33 /
gitvisual 65 / outro 173, native total 185.0), so the scale constant is
the sole divergence.

The committed artifacts were NOT produced by the committed generator:
every committed cue start matches the 120/124 scale (e.g. intro beat
native 1.5 s -> 1452 ms = 1.5*120/124; idea beats 7.5/8.0/8.5 s ->
7258/7742/8226 ms). With the committed SCALE they would land at
1550/7750/8276 ms. So "byte-identical twice in a row" is unprovable —
generation fails 100% of the time, zero bytes written.

Ancillary: committed `assembly_v6.srt` is 5321 bytes, sha256
`0e285a72741965c178937aece973d71fa3bdd1cdc74ebf84dfd04c61377568b5`;
`.vtt` is 5112 bytes, sha256
`24bc4e719e209a2f48d53986bbd9c9d5b8730bf02fdf9645895191436ed923c2`.
Neither matches the hashes claimed in the commit message / parcel
brief (`490568F2…4590`, `AA53BC4D…992CE0`; brief also says 5323 bytes).

## Probe 2 — Format strictness (own parser): FAIL (blockers)

Independent parser (`scripts/strict.py`, not the generator's
validator): 77 cues in each file; per-segment histogram by start
intro 1 / idea 25 / why 32 / gitvisual 11 / outro 8 (counts as claimed).
Three errors:

- **SRT overlap:** cue 2 `07.258–08.742` vs cue 3 starting `07.742`
  (`srt cue 3: OVERLAP start 7742 < prev end 8742`). The generator's
  own `_blocks_to_cues` trims each cue to the next cue's start, so the
  committed SRT is not generator output.
- **VTT cue 1 comma timestamps:**
  `00:00:01,452 --> 00:00:04,355` (invalid WebVTT; all other cues use
  dots). YouTube would reject/misparse the first cue.
- **srt != vtt:** cue 1 text `Hey Muse, I have an idea...` (srt) vs
  `Hey Muse, I've got an idea...` (vtt); cue 2 end 8742 (srt) vs 7742
  (vtt). The two upload files disagree with each other.

Numbering (1–77), VTT `WEBVTT` header, and `0 < start < end <= 179030`
hold; starts are strictly monotonic in both files.

## Probe 3 — Frame truth: 13/15 match, 2 mismatches (blocker)

15 cues sampled over all five segments (req >= 12), midpoint frames
grabbed from the committed `assembly_v6.mp4` with an own script and
each viewed (`scripts/grabframes.py`, `scratch/verifier-w6captions/frames/`).
Intro 1, idea 2/6/12/19/24, why 27/41/49, gitvisual 59/63/66/69,
outro 70/77 — includes the first cue and an outro cue.

Matches (cue text is the readable new text at that instant):
6 `Same answer everywhere.` (card complete, green footer);
12 `Exact, not close.`; 19 `Correctly rounded / sinPi/cosPi`;
24 `Watch it land.`; 27 `TOGETHER: A JOB SPEC / what the three jobs
need (IEEE 754-2019)` (headline only on screen); 41 `ELIMINATED`
(stamp); 49 `NOT MEASURED` (stamp; `src:` tag correctly excluded);
59 `PARCELS / work is divided / 19 parcels total`; 63 `GATES /
nothing merges unless all green / 411,213 smoke + 1,117,504 standard`;
66 `IAS15 RUNS ON THE CHIP` (gate window open, interior hashes excluded
per the rule); 69 `every system drops in, kept`; 70 `Done — it held
up.` (second reply still typing `Identi…`, correctly not yet cued);
77 `6 boards / IAS15 · 2,001/2,001 checks` (all three stat cards +
phone + HUMAN:AI panel on screen).

Mismatches:
- Cue 1: frame shows `Hey Muse, I've got an idea...`; the **SRT** says
  `Hey Muse, I have an idea...` (wrong). The VTT (`I've got`) and the
  audit constant (`intro_outro.INTRO_MSG`) agree with the frame.
- Cue 2 (mid 8.000 s): the frame already shows cue 3's line `Precise
  number maths in software (IEEE 754)` as the newest text — cue 2's
  headline text is stale at its own midpoint. This is the visible
  consequence of the SRT overlap (probe 2): the overlapping cue pair
  2/3 (midpoints 16 ms apart) cannot both be "the readable new text".

## Probe 4 — Stills: times 29/30 rows, bytes stable, content 30/30

Independent recompute from the raw audit tables without `build_stills`
(`scripts/stillscheck.py`, scale 120/124, offsets re-derived from
`assemble.py` durations): filenames, native times, and segment-local
times match all 30 INDEX.md rows; scaled column matches 29/30. **Row 25
(`25_t152.42_git-gate-augint.png`) prints Scaled `162.42` where the
recompute gives `152.42`** (native 157.50, gitvisual local 92.50) —
a +10.00 typo in the column; the filename (152.42) is correct, and the
row's own filename-vs-scaled self-check fails for this row only.

Byte-compare (`scripts/stillsbytes.py`, 6 stills spread over intro /
why / gitvisual-chase / gate / augint-gate / outro): 5/6 byte-identical
at the filename-stated scaled time (07, 13, 22, 25, 30); still 01
grabbed at the 2-decimal filename time (2.900) differs from committed
(173694 vs 177078 bytes), but grabbed at the generator's exact `.3f`
seek (2.903) is byte-identical (`cmp` clean), as is the cue-01 frame
(2.904). So the stills are byte-stable; only the 2-decimal filename
rounding is coarser than the exact grab instant for still 01.

All 30 stills viewed against their INDEX "Shows" text: 30/30 match
(phone message; idea card / number line / prove cards / method rows /
two-line question; spec checklist seven rows; opt1 ELIMINATED / opt2
NOT MEASURED / opt3 panic + NO FLOATS / settle four lines; chase-start
track + legend; PARCELS / ESCALATIONS / VERIFIERS / PLANTS / GATES /
STUDIES / MAIN popups mid-dwell; bridge cross-fade with HUD live;
replay early; IAS15 / KISSFFT / AUGMENTED-INTERVALS gate windows open
with content complete before the PASS footer; replay late; opening
fall + headline; opening plate 7/7; outro replies; HUMAN:AI panel;
final stats hold). No content mismatch; the sole row-25 column typo is
the only INDEX defect.

## Probe 5 — Gate and scope: PASS

- `tools/run.sh standard` in the duplicate (Git Bash, pinned
  `MSF_PYTHON`): **PASS** — smoke + 1,117,504 extras + aug pool PASS,
  all negative controls refused (`budget standard: PASS in 60s`).
- `git diff cdc40ae..c537e0d --name-only`: exactly the owned files —
  `video/captions.py`, `video/out/assembly_v6.srt`/`.vtt`,
  `video/out/stills_v6/**` (30 PNG + INDEX.md),
  `docs/metrics/briefs.jsonl` (own wave6 row binary-appended, +1 line),
  plus the single declared `video/README.md` pointer line. No segment
  code, renders, or assembly changes. Scope PASS.

## Findings

- **F1 (blocker, probe 1):** `video/captions.py` cannot run — `SCALE`
  is inverted (124/120 vs assemble.py's 120/124); `build_cues()`
  aborts at the duration guard, nothing is written, so regeneration
  byte-identity is unprovable and the committed artifacts demonstrably
  did not come from the committed generator.
- **F2 (blocker, probe 2+3):** SRT cue 2 (ends 08.742) overlaps cue 3
  (starts 07.742); at cue 2's midpoint the frame's newest text is
  already cue 3's. Violates the no-overlap acceptance rule.
- **F3 (blocker, probe 2):** VTT cue 1 uses comma timestamps
  (`00:00:01,452 --> 00:00:04,355`) — invalid WebVTT.
- **F4 (blocker, probe 2):** srt and vtt disagree (cue 1 text, cue 2
  end) — the two upload files are mutually inconsistent.
- **F5 (blocker, probe 3):** SRT cue 1 text `Hey Muse, I have an
  idea...` contradicts the frame (`I've got`) and the audit source
  (`INTRO_MSG`); VTT is correct.
- **F6 (note, probe 4):** INDEX.md row 25 Scaled column `162.42`
  should be `152.42` (filename and recompute agree; row self-check fails).
- **F7 (note, probe 4):** still-01 filename time (2.90) is coarser than
  the exact grab instant (2.903); grabs at the exact time are
  byte-identical, so stills are stable — methodology note only.
- **F8 (note, probes 1–2):** committed hashes/sizes (srt 5321 bytes
  `0e285a72…`, vtt 5112 bytes `24bc4e71…`) match neither the claimed
  `490568F2…/AA53BC4D…` hashes nor the claimed 5323-byte SRT size.

Frame pipeline stayed far under the ~6 GB ceiling (15 PNG grabs +
ffmpeg-only stills checks; the copy was never modified).
