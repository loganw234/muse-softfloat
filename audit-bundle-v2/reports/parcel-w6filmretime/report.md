# parcel-w6filmretime report — film retime (dedupe, zoom quality, 3-minute cap)

Base `101b4aa`, branch `wave6-filmretime`, worktree `worktrees/w6-filmretime`.
Brief: `ledger/briefs/w6-filmretime.md`. All three owner items done; every
acceptance probe (a)-(e) below was run in the worktree with the workspace
`.venv` python; raw outputs in this scratch directory.

## Item 3 first (it sizes the others): allocation

Native (120 BPM grid) durations, before -> after, all on the 0.5 s grid:

| segment | before | after | added time lands as |
|---|---|---|---|
| intro (`intro3.mp4`) | 7.0 | 7.0 | unchanged duration (brief) |
| idea (`idea2-1440p.mp4`) | 22.5 | 26.0 | scene-end holds: idea +0.5, correct +1.0, prove +1.0, method +0.5, question +0.5 |
| why (`why3-1440p.mp4`) | 29.0 (25.5 after item 1) | 32.0 | 0.5 white lead; spec +1.0, opt1 +1.5, opt2 +1.5, opt3 +1.0, settle (pre-fade) +1.0 |
| gitvisual (`gitvisual7.mp4`) | 102.0 | 108.0 | popup dwell +0.5 x7 = +3.5; gate windows ias15/kissfft 8->9 s, augint 8->8.5 s = +2.5 (PASS dwells longer; window close follows window length) |
| outro (`outro3.mp4`) | 8.5 | 12.0 | panel spacing 0.5->1.0 s and first panel 3.5->4.5 (after reply2 completes); final hold unchanged at 2.0 s of full panel |
| **total** | 169.0 | **185.0** | 185 x 120/124 = 179.03 s at 124 BPM |

No uniform internal stretch anywhere. Typing speeds, the intro dive
(4.5-6.5 s), the outro pull-back (0.5-2.5 s), gitvisual chase travel legs
(1.0 s) and replay leg wall durations (8.0/5.0/7.0 s, verified in probe
output) are unchanged; only holds lengthened. Implementation per segment:
idea scenes are drawn at `t - SH_*` under new cut times so each scene's
internal beats are untouched and the extra seconds are post-completion
holds; why's `frame()` maps output time to each scene's internal start
(8.0/13.5/18.5/24.0/28.0) under new output boundaries
(0.5/7.0/13.5/20.5/25.5, fade 31.0); outro `PANEL_T` respaced; gitvisual
`POPUP_DWELL = rule + 0.5`, gate `t1` values extended with legs shifted to
preserve their durations, `T_BOX/T_FADE/TOTAL` now derived from the moved
timeline (`T_BOX = 79 + SHIFT = 96.5`, `TOTAL = 108.0`).
`video/assemble.py` SEGMENTS updated to 7/26/32/108/12 (assembly NOT
produced, per brief; the lead assembles at merge).

BLOCKS audits recomputed: idea `BLOCKS` remapped by `_BSH/_BGONE` (e.g.
correct 5.0-11.0, prove 11.0-17.0, question 21.5-25.0); why `BLOCKS`
remapped by `_MAP` into output time (spec 0.5-7.0 ... settle 25.5-31.0);
outro `BLOCKS_OUTRO` follows `PANEL_T`/`OUTRO_DUR` (panels at 4.5..9.5,
gone 12.0); gitvisual popup dwell is the audit (`POPUP_DWELL`
[4.0,5.0,4.5,4.5,5.5,5.0,5.0] vs rule [3.5,4.5,4.0,4.0,5.0,4.5,4.5]).
An independent word-count rule check over the new idea/why BLOCKS
(`check_constants.txt`) reports zero violations — the RULE is a minimum
and every dwell grew or held.

## Item 1: duplicate question removed

Before (`before_scenes.txt`, recorded pre-edit): idea `BLOCKS` ends
`("question", 18.5, 21.5, [Q_KICK, Q_H1])`, `("question", 19.0, 21.5,
[Q_H2])` ("BUT FIRST — / WHY NOT USE WHAT / ALREADY SHIPS?"); why
`BLOCKS` opened `("title", 0.5, 3.5, list(T_H))`, `("title", 1.0, 3.5,
[T_SUB])` posing the same question again.

After: `scene_title`, `T_H`, `T_SUB`, the two title BLOCKS rows, and the
old `SHIFT` map are deleted from `why.py` (`hasattr(why, "scene_title")`
is False; no `T_H`/`T_SUB`/`SHIFT` tokens remain). Why `BLOCKS` scenes
are now exactly `[spec, opt1, opt2, opt3, settle]`; the segment opens
white (frame @0.2 s all-white, `probe_why_02.png`) then on the spec
(`probe_why_spec.png` @2.0 s: "TOGETHER: A JOB SPEC" + first rows).
Idea's question is the single posing, retimed to 21.5/22.0-25.0
(`probe_idea_question.png` @24.0 s).

## Item 2: phone-zoom supersampling (SS=2 chosen)

`intro_outro.py` gains a `canvas(ss)` scale context: the phone-camera
sources — the intro dive plate (via the file's own `measure_period`)
and the outro pull-back scenes (t < 2.5) — render at SS x (5120x2880 at
SS=2) with fonts/coords scaled parametrically (`K`, `PHONE_I/O`, `sc`),
and `camera()` downscales crops from that canvas to the 2560x1440
output (LANCZOS when downscaling, BILINEAR when still upscaling). All
other frames render native; output files stay 2560x1440 (probed).
`intro_cam`/`clamp_check` take explicit source dims; the period
centroid and both clamps are re-derived at SS through the file's own
measurement path (`measurements3.json` regenerated: period centroid
SS=2 `[3121.33, 725.5]` = output `[1560.66, 362.75]` pre-render probe,
render record target `[1560.91, 363.0]`; proof error **0.2 px** (was
0.6 at SS=1); intro clamp 0.0, outro clamp 0.25 SS px = 0.125 out px).

Probe stills (`ss_probe.json`, `ss{1,2,3}_mid{800,400}.png` + crops;
depth = dive point whose crop is 800 (resp. 400) output px wide, bubble
text readable): effective upscale at crop-800 is SS1 3.19x, SS2 1.60x,
SS3 1.06x; gradient energy (edge sharpness) 13.4 / 25.1 / 34.2.
Visually, SS1 letters and the bubble curve are stair-stepped/soft at
both depths; at SS2 the bubble text edges are smooth and clean; SS3
adds only slight curve smoothness. **SS=2 is the smallest SS where the
text is no longer visibly pixelated.** Costs (records, not rates):
plate+measure wall 0.12/0.31/0.74 s and one outro SS scene
0.02/0.08/0.17 s (est. pull-back 75 frames 1.7/5.9/12.5 s) for
SS 1/2/3; tracemalloc peak 55/221/498 MB (process-peak API returned 0
under the sandbox, so tracemalloc is the recorded number — all far
under the ~6 GB ceiling); the full SS=2 intro+outro render took 51.3 s
wall. Join colours: full-frame solid downscale through the SS camera
returns exactly `(255,255,255)` and `(3,4,9)` at SS 1/2/3 (no tint);
decoded `intro3.mp4` @6.9 s is all-white every pixel; decoded
`outro3.mp4` @0.0 s is `(2,3,8)` — the x264 yuv420 round-trip of source
`(3,4,9)`, identical to the untouched gitvisual end frame's decoded
`(2,3,8)`, so the two sides of the join match in decoded space and the
sources are exact.

## Acceptance probes

(a) Durations (`segment_probe.json`, ffmpeg header + packet frame count;
all 2560x1440 @ 30 fps): intro 7.0 (210 f), idea 26.0 (780 f), why 32.0
(960 f), gitvisual 108.0 (3240 f), outro 12.0 (360 f). Sum = **185.0**
by header, by frames/30, and by construction. At 124 BPM: 179.03 s,
inside the 3-minute cap.

(b) Duplicate question: quoted before/after scene lists above; still
proof `probe_idea_question.png` (idea @24 s) vs `probe_why_02.png` /
`probe_why_spec.png` (why opens white -> spec, no title).

(c) SS probe: table + stills above; chosen SS=2; encoded mid-dive still
`probe_intro_middive.png` (intro @5.2 s) shows the bubble text legible
with smooth edges; centroid re-measured at SS=2 with proof error 0.2 px;
join colours exact as detailed above.

(d) Gitvisual sync (`measure_sync_w6.py`, adapted from
`scratch/study-video-gitvisual-v6/measure_sync7.py` — import pointed at
the worktree `gitvisual.py`, plate-quad probe retimed to `T_BOX + 7.8`,
old-spine probe times moved onto the new legs; checks otherwise
byte-identical): **at-event distance 0.000 px for every kind** (chase
node lighting n=7, merge split/absorb n=25/25, exclusive sample n=17,
sendback entry/apex/exit n=5 each, gate arrival n=3, episode spawn
n=79, episode endpoint n=80). Gate ranks [44, 69, 140] with
`cursor_at_gate_t0 == [44, 69, 140]`, gates 56.5-65.5 / 70.5-79.5 /
86.5-95.0, legs 8.0/5.0/7.0 s (unchanged durations), cursor monotonic
True, augint rank == LAST_RANK, slot clashes [], DEEP colours match,
pre-root episodes on spine/endpoint nodes, plate text quad inside
plate, fall second-difference matches expectation, TOTAL 108.0.

(e) `tools/run.sh standard` in the worktree under Git Bash:
**PASS** (`run_standard.log`; standard extras 1,117,504/1,117,504
exact, aug pool 5,505,024 mismatches=0, budget string "budget
standard: PASS in 59s"). Nothing outside video/ moved: the diff is the
five segment scripts (`render_why.py` owned but unchanged — it is the
shared 1440p base lib and its standalone 16 s main is not an assembly
segment), `assemble.py` durations, the regenerated segment MP4s /
stills / `measurements3.json`, and the appended `briefs.jsonl` row.

Render wall records (this host, one job at a time): intro+outro 51.3 s
(Measure-Command), gitvisual 155 s (its own log line); idea/why renders
were not individually timed (logs in scratch). Framing/memory: SS2 probe
peak (tracemalloc) 221 MB; the frame pipelines stream one frame at a
time as before, far under the ~6 GB stop line.

Not done, by brief: the assembly (`video/out/assembly_v6.mp4`) is not
regenerated — the lead assembles at merge with the updated SEGMENTS
durations.
