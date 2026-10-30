READY

Polish pass on v1 per ledger/briefs/study-video-gitvisual-polish.md.
v1 (gitvisual.mp4, beats.md, report.md, stills/) untouched; v2 lives
beside it: render_gitvisual2.py, gitvisual2.mp4, stills2/, beats2.md,
regen_gate2.py + gate2_numbers.json, measure_camera.py +
camera_measurements.json, verify_handoff2.py.

## Clip (probe-verified)

- gitvisual2.mp4: 83.0 s (**+5.0 s vs v1's 78.0**), 1920x1080, 30 fps,
  H.264, silent, 2,490/2,490 frames decoded clean (video/probe.py,
  decode_rc 0), 11,405,379 bytes. Render wall 60 s on this run.
- Run: $MSF_PYTHON regen_gate2.py ; $MSF_PYTHON render_gitvisual2.py
  --out gitvisual2.mp4 (MSF_PYTHON = workspace .venv python; frames
  stream to ffmpeg, peak memory is a few full-res PIL/numpy layers).
- Stills: stills2/ 18 MP4 grabs covering every brief beat (2D open,
  3D transition, mid-chase popups, axis-switch mid+end, up-growth
  replay A/B/C, each gate working + PASS, box open/shut, near-black);
  all eyeballed this session. Defects found by eyeballing and fixed
  before final render: flat-open camera orientation, replay lane
  elbows, stray guide lines in the turn, PASS label placement.

## Handoffs (measured on the MP4, verify_handoff2.py)

- IN t=0.5: all 2,073,600 px exactly (255,255,255).
- OUT t=82.5: 2,073,572 px (2,3,8), identical to outro2.mp4's first
  frame (measured here: 1 unique color (2,3,8)); 28 px read (2,2,10)
  - encoder noise within 2 levels, no visible difference.

## Owner direction - what was done

1. 2D -> 3D transition (1.0-6.5 s): opens as v1's flat top-down
   white plane; over 3.0-6.5 s (smootherstep) the camera lowers to a
   behind-side chase position, the up-vector blends Y->Z, and the
   trail/branches lift 130/240 world units off the ground grid,
   which stays behind with the trail's shadow - parallax separates
   plane, shadow and line continuously. No cut.
2. Chase camera (6.5-30 s): camera position = head + eased offset,
   lookahead +380 units, aim drifts 45% toward the active node,
   distance closes 20% while its popup holds, roll banks +-0.1 rad
   slowly. Every component is smootherstep (6u^5-15u^4+10u^3, zero
   velocity and acceleration at both ends - same family as the
   intro polish). Measured (measure_camera.py, 30 fps sampling):
   head/camera speed 0.6 -> peak 1,309-1,343 -> 11.7 units/s;
   at all 15 head keyframe joins the sampled one-frame velocity is
   0.0-7.4 on BOTH sides (analytic 0) - no velocity steps; the
   largest frame-to-frame speed change (183 units/s mid-leg) is
   4.4x the median nonzero change, a smooth build/decay not a spike.
3. Pull-back + axis switch (30-34 s): the full real tree is shown
   left-to-right, then a single continuous move - in-plane rotation
   0->90 deg (smootherstep, angular speed 0->1.1->0 rad/s, max
   per-frame dv 0.041 rad/s) with progression rescaled 1660->800 px
   and lane spacing 62->112 px (plus a 30% scale dip mid-turn) -
   ends with the tree filling the frame vertically, oldest at the
   bottom. Replays then grow DOWN-TO-UP (cursor rises, NEWEST ^ /
   OLDEST v labelled). The 30 s boundary itself is an on-beat scene
   change (as v1's pull-back was); the axis switch inside the shot
   is not a cut.
4. Energy on the 120 BPM grid: beat_pulse (exp decay per 0.5 s
   beat) drives halo width/core brightness, node pops
   (ease_out_back + pulse ring), merge rings in the replay, gate
   PASS impact (expanding ring + decaying shake) at 52.5/68.5 s.
   Popup dwell is NOT shrunk: 2.3 s holds (v1: 2.25 s), same copy,
   same sizes; speed lives in camera/light.

## 3D route and its limits

Choice: custom perspective projection in numpy + PIL line drawing
(class Cam: position/target/up-hint -> basis, roll for banking;
points projected in bulk, widths scaled by median 1/depth). This was
the lightest honest route: zero new dependencies, no network, the
same renderer family as v1/video, and 60 s render for 2,490 frames.
Limits, stated plainly: wireframe only - no surfaces, shading,
occlusion sorting (draw order is hand-set per scene) or true HDR
bloom (glow = 3-pass halo lines, S12); the replay/box use the same
projection ideas in flattened graph/isometric form rather than the
full camera; text is screen-space billboards (S9) so labels never
foreshorten - a readability choice, not a rendering limit.

## Carry-overs from v1 (no regressions)

- Real history only: same history.json at a73e97d (141 commits,
  27 merges, 25 into main; true order/parentage/second-parent
  re-gate connectors). Popup copy + short sources identical to v1;
  full sources in report.md Sec. "Popup sources" still apply.
- Both gates with the six Pico mockups (1 genuine GP25 square LED +
  5 RP2040-Zero WS2812, labelled not footage). PASS now holds ALL
  SIX LEDs solid for the last 1.5 s of each gate (explicit
  state machine, still_053.2s/069.2s show it) - v1's named debt paid.
- Gate 2 REGENERATED (regen_gate2.py): muse-softfloat/docs/metrics/
  usage.jsonl at HEAD a73e97d has 93 rows, all labeled. Measured:
  input 1,190,490,305 + output 5,638,465 = billed 1,196,128,770;
  cached 1,165,653,139 inside input; 7,756 logged messages. NOTE:
  the brief's parenthetical calls 1,196,128,770 the "input" sum -
  it is input+output; the frame prints the true definition and both
  parts. v1's 1,514,499,184 and its derived 1:785,000 / 8,951 are
  retired: v2 shows ~1:620,399 and 0.00016% against the tokens
  study's frozen owner estimate (~1,928 chars/4 tokens, labelled
  frozen on frame).
- Box ending rebuilt isometric with a hinge-arc lid (v1 asked for
  the arc); ends lid-shut, neon dark, near-black hold as before.

## Simplifications (S1-S8 carried from v1, updated; S9-S12 new)

- S1. Progression axis = committer-date RANK (uniform per commit),
  now drawn vertically in the replay; overnight gaps compressed.
- S2. One lane per merge; lane side/spacing is layout only; elbows
  are geometry. Short-lived branches read as sideways wedges in
  vertical aspect - that is their true short rank span, not data loss.
- S3. The 2 lead-fix re-gates drawn as red second-parent connectors.
- S4. Replay colour = wave family; green = merge to main, red = re-gate.
- S5. Only branch labels on lanes; per-commit text is the cursor readout.
- S6. Gate 1 at its true merge 32bbd93 (rank 69); Gate 2 anchored
  editorially at metrics merge a1a888f (rank 134), numbers now the
  regenerated a73e97d aggregate (owner estimate still the study's
  frozen chars/4 figure, labelled as such). No merge invented.
- S7. Day separators = first commit of each calendar day in rank order.
- S8. The chase's seven nodes are a sourced teaching diagram, not
  seven literal branches; section titles keep diagram and replay apart.
- S9 (new). Popups, legend, gate panels and all text are screen-space
  billboards anchored to projected 3D points; they do not tilt with
  the world, by design for readability.
- S10 (new). Chase heights, shadows, banking and ghost-ahead lines
  are presentation only; they encode no data (extends S8).
- S11 (new). The axis turn also rescales (1660->800 px progression,
  30% mid-turn dip) to fit the vertical frame; topology/order unchanged.
- S12 (new). Glow is multi-pass halo strokes, not HDR bloom; gate
  impact ring/shake and LED blink phase are illustrative (mockup
  label rides every gate frame, as in v1).

## Assembly needs / open items

- Duration 83.0 s (+5.0 vs v1). Against the brief's "film targets
  180 s total, currently 89 s spoken for": if the +5 must come back,
  cheapest trims that keep every owner move: chase travels 1.0->0.8 s
  and final leg (-1.7 s), turn 4->3 s (-1 s), replay legs at 1.15x
  (-3.3 s) - popup holds and gates untouched.
- Joins: intro white -> t=0 exact; t=82.5 near-black -> outro2 exact
  value (28-px encoder noise noted above). Silent, cuts on the
  120 BPM grid; music/VO not attempted, as v1.
- Known visual debts (eyeballed, not hidden): mid-turn diagonal is
  dense/"caterpillar" for ~1 s; a few dense-wave5 lane labels still
  sit on neighbouring lanes (greedy nudge, gate lines now avoided);
  box lid hinges on its left depth edge. None block comprehension.
- Production route unchanged from v1: port scenes into video/ at
  freeze, regenerating history.json + gate2_numbers.json then.
- Fences: scratch only + ledger append; muse-softfloat status clean
  after the run; nothing committed; no path with cft in its name
  opened, searched or listed; renders bounded/streamed.
