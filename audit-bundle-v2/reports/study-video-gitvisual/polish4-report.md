READY

Owner fixes on v3 per ledger/briefs/study-video-gitvisual-v4.md.
v1-v3 untouched (sizes verified); v4 beside them:
render_gitvisual4.py, gitvisual4.mp4 (+ gitvisual4-1080.mp4 twin
via make_twin4.py), stills4/, beats4.md, measure_sync4.py +
sync_measurements4.json, verify_handoff4.py, render_checks4.py.

## Clip (probe-verified)

- gitvisual4.mp4: **88.0 s exactly (delta +0.0 vs v3)**,
  2560x1440, 30 fps, H.264, silent, 2,640/2,640 frames decoded
  clean (video/probe.py, decode_rc 0), 28,236,272 bytes.
  Render wall 125 s, frames streamed to ffmpeg (never buffered).
- Run: $MSF_PYTHON render_gitvisual4.py --out gitvisual4.mp4
  (workspace .venv). Twin: $MSF_PYTHON make_twin4.py (1920x1080
  Lanczos, probe-clean 2,640 frames, 23,233,268 bytes).
- Stills: stills4/ 29 MP4 grabs (sync event frames, packaging
  sequence, gates, box, both handoffs); eyeballed this session.

## Duration

88.0 s - no change. The packaging beat was bought INSIDE the
existing 79-88 s box window: seven marbles file in over
~4.2 s (was: 3 marbles roll in over 3.2 s), the lid arc moved
82.4-83.8 -> 84.0-85.3, dim/fade unchanged (t>86 blend to
near-black untouched). Nothing elsewhere was trimmed.

## Handoffs (measured on the MP4, verify_handoff4.py)

VALUES unchanged from v1-v3 at 2560x1440 (3,686,400 px):
- IN t=0.5: all 3,686,400 px exactly (255,255,255).
- OUT t=87.5: 3,685,376 px (2,3,8) = outro2 first frame;
  1,024 px (2,3,6) within 2 levels - identical fingerprint to v3.

## Fix 1 - marble sync (one clock, proven numerically)

Sync model: EVERY marble position is now a pure function of the
same clock that lights its event - head_x(t) in the chase,
cursor_rank(t) in the replay. No offsets were fudged; the v3
desync sources were removed at the model level:

1. Ride-height offset (replay): v3 drew every marble 26 world
   units above its node center (~16.3-16.7 px everywhere, the
   constant "hovering off the track" component). marble_pos is
   now exactly R3(rank, slot).
2. Gate bob (replay): v3 added a time-based 4*sin(5t+rank) bob
   while held at gates - position depended on wall time, not the
   cursor. Removed.
3. Gate hold gap: v3 held the cursor at gate_rank-0.5, so the
   head marble stopped half a rank short of the gate line it was
   "arriving" at (14.3-14.6 px). Legs and holds now land exactly
   ON each gate rank; the lane marble for that merge absorbs on
   the same frame the window opens.
4. Wave-1 lane teleport (found by the measurement, present
   v1-v3): lanes 2843792 (w1-f32) and 06fdec8 (w1-f64) carry
   exclusive commits whose TIME ranks (8, 9) precede the
   merge-base rank (11); lane_pts_rs built a backwards first
   segment and slot_at snapped the marble a full lane (165 world
   units, ~101 px) within one frame of the split instead of
   forking smoothly. Elbows are now clamped monotonic inside
   (base, merge); slot goes 0 -> 0.2 -> 1.0 over base..base+0.5.
5. Sendback stamps: v3 fired the stamp at phase 0.25 of a
   6-rank window while the marble rode a 4-rank window - stamp
   landed up to 35.0 px of marble travel away from the apex.
   One window now ([rank-1, rank+3] = the loop's own join/rejoin
   ranks); the stamp lands at the computed arc-length apex rank,
   the frame the marble crests it. Loop ends coincide with the
   straight ride, so entry/exit are seamless by construction.
6. Chase two-clock lighting: v3 lit nodes on wall time
   (arrival-0.1 s) while marbles moved on head_x, and the head
   stopped 14 units past each node. Lighting is now gated on
   head_x >= NODE_X itself, KEYS stop exactly at NODE_X, and
   the split marble (always the end of the lit branch polyline)
   parks ON its node after lighting it instead of vanishing
   320 units later.

Measured (measure_sync4.py, each version with its own camera and
marble model; distance = marble centroid vs node center, px at
1440p, at the continuous event time / nearest 30 fps frame):

| event set | n | v3 at-event max (mean) | v4 at-event max | v4 nearest-frame max (mean) |
|---|---|---|---|---|
| chase node lightings | 7 | 0.08 (0.01) | 0.0 | 0.0 (0.0) |
| merge splits (true bases) | 25 | 16.49 (16.29) + ~101 teleport x2 | 0.0 | 21.8 (5.8) |
| merge absorbs | 25 | 16.49 (16.30) | 0.0 | 24.4 (4.7) |
| exclusive-commit sample | 17 | 17.72 (16.51) | 0.0 | 25.7 (5.5) |
| sendback entries / exits | 5+5 | 16.71 / 16.69 | 0.0 | 7.5 / 5.0 |
| sendback apex vs stamp | 5 | 35.03 (34.63) | 0.0 | 23.5 (7.6) |
| gate arrivals | 3 | 14.60 (14.31) | 0.0 | 0.0 (0.0) |

Worst v3 offenders: sendback stamp-vs-apex at ranks 99/12/38
(35.0/34.9/34.7 px), then the universal ~16.5 px hover, then the
~101 px Wave-1 teleports (one frame past the split, so they sit
in lane_snap_check rather than the at-event rows). v4 at-event
residual is 0.0 px on every row - marble, node lighting, lane
clipping and stamps are all evaluated from the same cursor/head
value, so coincidence is exact, not tuned. The nearest-frame
column is the honest on-film number: ≤25.7 px worst case, which
is purely how far the (shared) cursor travels in half a 30 fps
frame at peak leg speed - on the first frame a node shows lit,
its marble is on it up to that quantization, with zero
systematic component. BPM pulse: beat_pulse enters only the
drawn radius (r += 2px*pulse); measured centroid drift across a
pulse cycle during a gate hold: v4 0.0 px (v3 1.76 px, its bob).

## Fix 2 - packaging ending

The box beat now files EVERY legend system marble in, in queue
order along the spine (front-most first so no marble passes
through another): parcels, verifiers, plants, gates, studies,
escalations, lead/main last - each in its legend colour
(lightened 30% for the dark stage), name-labelled while it
travels, arcing over the front rim and dropping in. The lid
does not start to shut until 7/7 are in (counter on frame:
"marbles in: n / 7"). As they land, the box front stamps what
the process retains - only real artefacts of this repo, named
here as required: **RECORD** (the project record), **LEDGERS**
(the ledger/ notes), **VECTORS** (the retained test vectors),
**METRICS** (usage.jsonl session metrics); stamps appear at
1/3/5/7 marbles in. Lid hinge arc, box geometry, dim and the
near-black fade are v3's; end-frame values did not move (above).
New presentation note (S19): pack order, hop arc and stamp
thresholds are presentation; the seven systems and four
artefacts are the real legend/record sets. (Also fixed en
passant: the front face used to paint over hopping marbles;
painter order now matches depth, so each arc reads.)

## Carry-overs (no regressions)

Real history at a73e97d (141 commits, 25 merges into main) with
v3 simplifications S1-S18 (+S19 above); chase popup copy/sources
and legend identical; three gate windows (IAS15 d9718cf rank 44,
KissFFT 32bbd93 rank 69, tokens a1a888f rank 134) with PASS
holding all six LEDs solid 1.5 s; tokens numbers unchanged -
billed 1,196,128,770 = in 1,190,490,305 + out 5,638,465,
93 labeled rows @ a73e97d (still_073.8s.png eyeballed); 1440p
parametric (max crop-upscale 1.0); one continuous space, no
full-tree reveal. Small intended consequences of the sync model:
during a gate window the HUD commit counter reads the gate
commit itself (cursor ON the rank), and marbles now sit centered
on the track line rather than resting on it.

## Open items / debts

- Carried v3 visual debts, unchanged: PASS impact ring briefly
  crosses window captions; chunky lane exits at the bottom edge
  for ~1 rank; a branch label can kiss its marble in dense
  Wave-5 frames; the packaging queue's rearmost marbles start
  just off-frame low-left and roll into view (by camera design).
- The artefact stamp row can touch the box front's left edge by
  a few px in perspective at 7/7 (still_085.8s.png) - legible.
- Assembly resolution flag from v3 stands (1440p master vs
  1080p siblings; twin provided).
- Fences: scratch only + ledger append; nothing committed;
  v1/v2/v3 files untouched (sizes verified); no path with cft
  in its name opened, searched or listed; renders streamed and
  bounded (125 s, few-layer frames), own directory only.
