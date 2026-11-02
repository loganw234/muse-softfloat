READY

Rough-draft "git visuals" main segment for the demo video. Programmatic
only (PIL + bundled ffmpeg via imageio-ffmpeg, `video/style.py` fonts /
palette / 0.5 s beat grid). Structure, timing, real-data plumbing and
readable popups are in place for lead assembly + owner iteration;
motion/ease/copy polish is still owed (listed at the end).

## Clip (probe-verified)

- `gitvisual.mp4`: 78.0 s, 1920x1080, 30 fps, H.264, silent,
  2,340/2,340 frames decoded clean (`video/probe.py`, decode_rc 0),
  4,712,409 bytes. Render wall 65 s (a fact about this run, not a rate).
- Run: `$MSF_PYTHON extract_history.py` then
  `$MSF_PYTHON render_gitvisual.py --out gitvisual.mp4`
  (`MSF_PYTHON` = workspace `.venv` python; script files only, bounded:
  frames stream to ffmpeg, nothing buffers the whole film).
- Stills at every beat: `stills/still_*.png`, grabbed from the MP4 by
  `video/probe.py` and visually inspected (chase popups, pull-back,
  replay A/C, both gates working + PASS, box open/shut, near-black).
- Timing/beat sheet: `beats.md`. Dataset: `history.json` (86 KB).

## Handoff contract (measured on the MP4, not the source frames)

- IN: starts EXACTLY on the intro's final frame - full-frame pure white
  (255,255,255) held 1.0 s. Measured on the t=0.5 s MP4 grab: all
  2,073,600 px are (255,255,255). Spec: scratch/study-video-intro/report.md.
- OUT: box lid shut, neon dark, flat near-black held the last ~2 s.
  Measured on the t=77.5 s grab: all px (2,3,8) - the same value the
  intro study measured for the outro's first frame after round-trip.

## Colour / system legend (printed on screen during the chase)

Deep variants are used on the white plane so neon reads on white;
brighter equivalents on the dark replay. Meaning per `history.json`:

| System | Chase colour (on white) | Meaning |
|---|---|---|
| lead / main | deep blue (29,78,216) | the lead's main line; only READY work merges |
| parcels | deep cyan (8,145,178) | boxed work parcels on their own branches/worktrees |
| verifiers | deep pink (190,24,93) | disconfirm-only checks; NOT READY = sendback |
| plants | amber (217,119,6) | planted defects grading verifiers (caught/missed) |
| gates | emerald (5,150,105) | smoke / standard / board gates |
| studies | violet (124,58,237) | read-only feasibility studies in scratch |
| escalations | red (220,38,38) | a parcel stops and asks the lead to rule |

Replay lane hue is by wave family (w1 cyan, w2 teal, w3/IAS15 amber,
wave4 violet, wave5 pink, lead-* blue) - simplification S4 below.

## Popup sources (every chase popup is a real, sourced example)

1. PARCEL - parcel-f32: 173 binary32 instantiations, owned
   `src/msf32.c` only, kernels lead-owned.
   Source: muse-softfloat/docs/RECORD.md Wave 1 entry, lines 323-332.
2. ESCALATION - parcel-f32 escalates on pack tininess (Clause 7.5);
   Berkeley disagreed while every self-consistent gate passed; ruled
   for the parcel, lead fixes 53acb1a / b37fb12.
   Sources: RECORD.md Wave 1 lines 334-347; docs/metrics/escalations.jsonl
   (wave1 parcel-f32 sent 2026-10-26T22:11:37-07:00, answered 22:14:00).
3. VERIFIER - SENDBACK (the brief's example) - verifier-w5twiddledoc
   NOT READY: the printed SHA-256 in docs/TWIDDLES.md is 56 hex chars,
   truncated/invalid; the measured 64-char value is what the demo
   tooling enforces.
   Source: ledger/verifier-w5twiddledoc.md (blocking findings list).
   Fix landed as commit a41f026 on wave5-twiddledoc (git log).
4. PLANTS GRADED - Wave 1: 9 of 10 caught; the miss is a weakened
   boundary value in the f32 generator pool, seen as regen drift but
   filed benign (detection without the byte-identity norm).
   Sources: RECORD.md Wave 1 lines 348-363; docs/metrics/plants.jsonl
   (wave1, verifier-w1f32, plant 5, grade=missed, with the note).
5. GATES - Wave 1 close state: smoke 52,168 committed vectors,
   standard adds 1,117,504, 9/9 negative controls refused; board:
   2,767 sampled vectors on RP2040 e66440a2cb6f5c2b, whole-run SHA-256
   4d7c2a28... identical host and board. Labelled on frame as the
   Wave 1 example. Source: RECORD.md Wave 1 lines 364-374.
6. STUDY - feasibility first, read-only, in scratch; two study visuals
   wait ahead as gates. Sources: scratch/study-kissfft-visual/report.md
   and scratch/study-tokens-visual/report.md (both "FEASIBLE WITH
   WORK"); the survey-first pattern is Wave 0 S1-S4, RECORD.md lines
   13, 64-67.
7. LEAD MERGE - only READY work rejoins main: merge 2843792
   "Merged Wave 1 binary32 parcel (173 instantiations, READY 26c76aa)",
   2026-10-27 05:17:07 -0700, parents 52a6715 + 26c76aa (w1-f32 tip).
   Source: git -C muse-softfloat log (also history.json merges[]).

Gate content sources:
- GATE 1 (KissFFT idiom): waveform = the study's own LCG input replica
  (scratch/study-kissfft-visual/input_n256.json, cfg 0); spectrum =
  spectrum_n256.json (numpy FFT, stated on frame: "NOT KissFFT
  output"); twiddles = exact e^(-2 pi i k/N) points; end stamp
  "12/12 CONFIGURATIONS - HASHES RECORDED" per that report Sec. 2/4
  (12 KF rows in demo/expected-kissfft.txt; no KissFFT source or any
  path with `cft` in its name was opened, searched, or listed).
- GATE 2 (tokens idiom): every number from
  scratch/study-tokens-visual/data/tokens.json + report.md - project
  1,514,499,184 billed (input+output; cached inside input), owner
  ~1,928 [1,350-2,507] by chars/4 over 40 prompts / 7,713 chars,
  ratio ~1:785,000, human share 0.00013%, 8,951 model responses,
  frozen 2026-10-28. Definitions ride on the frame, as in the study.
- Six Picos (both gates): mockup labelled "not footage". 1 genuine
  Pico with a distinct square GP25 LED + 5 RP2040-Zero clones with
  round WS2812 LEDs, all blinking green while "working". Basis: the
  brief's six-board story; RECORD.md hardware note (six-board IAS15
  sweep: genuine board + clones); scratch/study-video-intro/report.md
  ("all 6 chips (genuine Pico + 5 RP2040-Zero clones)"); git commits
  bc15593 "Blink the onboard LED while board firmware is working" and
  5f308c4 "Drive the RP2040-Zero WS2812 (GP16) alongside the Pico LED".
  Blink phase/rate is illustrative, not a recording - said here so the
  mockup never reads as board evidence.

## The replay is the repo's actual history (with named simplifications)

Dataset extracted by `extract_history.py` from
`git -C muse-softfloat log --all` (+ branch / merge-base / rev-list
reads) at HEAD a73e97d: 141 commits, 92 on main's first-parent chain,
27 merges (25 into main, 2 lead-fix re-gates into w1-f32/w1-f64),
26 branches, 2026-10-26T10:50 -> 2026-10-29T14:21 (-0700). Counts
cross-checked independently (`rev-list --all --count` = 141,
`--merges --count` = 27). Every non-main commit belongs to exactly
the exclusive chain(s) of its merge (0 unplaced). Shown merges keep
true order and true parentage: each lane forks at its real
merge-base, carries its real exclusive commits as dots in date order,
and lands on its real merge commit (green dot). Branch attribution:
the branch whose tip is the merge's second parent (25/25 into main;
the 2 re-gates are attributed by their subjects, "into w1-f32/f64").

Simplifications (every one, per the brief):
- S1. X axis = committer-date RANK (uniform per commit, ties by topo
  order), not elapsed wall-clock - overnight gaps are compressed.
  The axis was machine-checked parent-before-child for all 141
  commits (0 violations), so replay order never violates parentage.
- S2. One lane per merge; lane side/height is layout only (greedy
  non-overlap). Lane elbows (plateau before the merge) are geometry,
  e.g. wave5-exp2's long plateau is the real ~10 h it sat unmerged.
- S3. The 2 re-gate merges are drawn as red second-parent connectors
  from the lead fix b37fb12 on the spine into the w1 lanes, instead
  of duplicating 53acb1a/b37fb12 as lane commits (they were authored
  on main). Parentage shown is the true second-parent edge.
- S4. Replay lane colour = wave family, not the chase's system
  colours (every lane is a work branch; system colours would say
  nothing). Green dot = merge into main; red = lead-fix re-gate.
- S5. Only branch-name labels ride the lanes; per-commit text is the
  single cursor readout (date + short hash + subject) - 141 labels
  would be illegible. Full subjects are in history.json.
- S6. Gate placement: GATE 1 sits at its true chronological point,
  the KissFFT merge 32bbd93 (rank 69). GATE 2's tokens study was
  scratch-only and never a repo merge; it is anchored editorially at
  the Wave 5 metrics merge a1a888f (rank 134) and its numbers stay
  frozen at the study's 2026-10-28 stamp. No merge is invented.
- S7. Day separators (10-26..10-29) mark the first commit of each
  calendar day in rank order; they are guides, not a time scale (S1).
- S8. The chase's seven system branches/nodes are a teaching diagram
  built from the sourced examples above - they are not seven literal
  git branches, and the segment says so by separating "1 - THE CHASE"
  from "2 - THE REPO, AS IT HAPPENED", whose data is pure git.

## Assembly / polish still needed

1. Assembly joins: intro white frame -> t=0 (exact, measured);
   t=77.5 near-black -> outro t=0 (exact value matched). Total film
   timing/music: this segment is 78.0 s silent on the 120 BPM grid,
   same terms as video/MUSIC.md; VO/captions not attempted.
2. Owner/lead calls: popup copy trims; whether Gate 2's editorial
   anchor (S6) is the right beat; whether the white->dark dim during
   the pull-back is wanted or the replay should stay on white.
3. Motion polish: chase camera easing/branch draw-on curves, popup
   pop easing, replay cursor easing is smoothstep-per-segment (speed
   varies within a replay leg), gate LED pass state should go solid
   on all six boards (currently re-blinks), box lid wants a hinge
   arc instead of a lerp, label collision nudging in the dense
   wave4/wave5 middle is greedy and can detach a label from its lane.
4. Production route (mirrors both study reports): port the three
   scene families into `video/scenes.py` as timeline kinds fed by a
   regenerated history.json at freeze time (numbers here freeze at
   a73e97d; tokens numbers additionally need the study's re-aggregate
   step), add the STORYBOARD section, then final probe + stills.
5. If the segment must shrink for the 3-minute cut: the chase can
   drop to 4 popups (-10 s) and replay legs can run 1.5x (-9 s)
   without touching gate or ending timings.

## Effort estimate to final

One focused parcel (production port into video/ + polish items 3-4),
plus one owner review round on copy and the S6/white-dark calls. No
board or firmware work. Data plumbing (the risky part) is done and
re-runnable in seconds.

## Fences honoured

Scratch only (`scratch/study-video-gitvisual/` + this ledger file);
`git -C muse-softfloat status` clean before and after; nothing
committed; no board use; no file with `cft` in its name opened,
searched, or listed (extractor/renderer read git, RECORD.md, the
ledger, metrics JSONL, and the two study dirs only); renders bounded
(streamed frames, pre-rendered static layers, 2,340 frames total).
