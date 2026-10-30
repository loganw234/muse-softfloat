READY

Full-model rework of v2 per ledger/briefs/study-video-gitvisual-v3.md.
v1/v2 untouched; v3 beside them: render_gitvisual3.py, gitvisual3.mp4
(+ gitvisual3-1080.mp4 downscale twin via make_twin3.py), stills3/,
beats3.md, measure_camera3.py + camera_measurements3.json,
verify_handoff3.py, render_checks3.py (eyeball-still driver).

## Clip (probe-verified)

- gitvisual3.mp4: 88.0 s (**+5.0 s vs v2's 83.0**), **2560x1440**,
  30 fps, H.264, silent, 2,640/2,640 frames decoded clean
  (video/probe.py, decode_rc 0), 28,205,015 bytes. Render wall 122 s.
- Run: $MSF_PYTHON render_gitvisual3.py --out gitvisual3.mp4
  (MSF_PYTHON = workspace .venv python; frames stream frame-by-frame
  to ffmpeg - peak memory is a few 1440p PIL/numpy layers, the film
  is never buffered). Twin: $MSF_PYTHON make_twin3.py (1920x1080
  Lanczos downscale, probe-clean 2,640 frames, 23,233,408 bytes).
- Stills: stills3/ 25 MP4 grabs covering every brief item (angled
  upward flow, marble split, sendback loops, each gate-window open +
  PASS + green-check close, box open/shut, both handoffs); all
  eyeballed this session (defects found and fixed below).

## Duration vs the 180 s film budget

88.0 s replaces 83.0 s (+5.0: +8.0 IAS15 window, -4.0 pull-back/
axis-turn deleted, +1.0 bridge/box rebalance). Against "~110 s
spoken for including the new 16 s why-segment": the film becomes
~115 s of 180 s - **no overrun; ~65 s headroom remains**. If the
+5 must come back anyway, cheapest trims keeping every owner move:
replay legs at 1.2x (-4.0 s), bridge 2.4 -> 1.9 s (-0.5), box roll
3.2 -> 2.7 s (-0.5); popup holds, windows and PASS holds untouched.

## Handoffs (measured on the MP4, verify_handoff3.py)

VALUES unchanged from v1/v2, now at 2560x1440 (3,686,400 px):
- IN t=0.5: all 3,686,400 px exactly (255,255,255).
- OUT t=87.5: 3,685,376 px (2,3,8), identical dominant value to
  outro2.mp4's first frame (measured 1 unique color (2,3,8));
  1,024 px read (2,3,6) - within 2 levels, encoder noise.

## Owner direction - what was done

1. **No full-tree reveal.** The v2 pull-back + 90-degree turn is
   deleted. From t=28.6 one continuous flight carries the chase
   camera into a closer angled replay camera that rides the cursor
   for the rest of the film; only ranks [cursor-18, cursor+48] are
   drawn (S13), so the tree is implied by the stream, never framed
   whole. The track bed climbs (17 world units/rank, S14): near/old
   sits low in frame, far/new high - marbles and the cursor travel
   UP-screen, down-to-up progression kept (NEWEST ^ / OLDEST v).
2. **Marble-track model as built.** One world (X = progression,
   Y = lane, Z = up) from the first chase frame to the box: chase
   trail X 90..5600, real history from X 5600 (rank x 85), box at
   rank 156 on the same spine. Marbles are depth-scaled shaded
   spheres with bed shadows: an amber head marble + blue trailing
   stream on the spine; at every true merge-base a lane marble
   splits off in the lane's wave colour, rides that lane's true
   exclusive-commit polyline, and follows the elbow back into the
   spine at the true merge rank (green pop), where it rejoins the
   stream (S15). Chase branches got the same split marbles. During
   a gate window the marbles queue and bob behind the gate line.
3. **Corrections/sendbacks visible.** Five sourced events ride the
   flow as red loop-backs: the marble detours up and BACKWARD along
   the loop, a SENDBACK - FIXED - REJOIN stamp pops at the apex
   with a small label + source, then a small check persists:
   rank 7 4cdb912 "Fixed unreachable truncate-to-default NaN branch
   (verifier-w1prep N1)" (history.json, main); rank 12 tininess
   re-gate - fixes 53acb1a/b37fb12 merged into w1-f32/w1-f64 as
   9bb8723/80cbc97, re-gated READY 26c76aa/cb10ee2 (RECORD Wave 1;
   the red second-parent connectors still draw too, S3); rank 38
   83622cf runner char-to width fix (+ f3c48b8, history.json);
   rank 99 048aa29 exp2 delta/near-1 fix (wave5-exp2); rank 114
   a41f026 TWIDDLES.md SHA-256 fix after verifier-w5twiddledoc
   NOT READY (56 hex chars; ledger/verifier-w5twiddledoc.md).
   Loop geometry/timing is presentation (S16); ranks, lanes,
   commits and labels are the real events.
4. **Gates are windows.** At each gate rank the cursor holds and a
   window rises from the gate line on the track plane (rect grows
   out of the projected gate point on an amber stem; world darkens
   to 62% but stays visible - no scene exit), plays its viz beside
   the six blinking Pico mockups (1 genuine GP25 square LED +
   5 RP2040-Zero WS2812, labelled mockup), then shrinks back into
   the persistent green check on the track and the stream resumes.
   PASS holds ALL SIX LEDs solid for the last 1.5 s of every window
   (v2 state machine kept). IAS15 is NEW at its true beat (merge
   d9718cf, rank 44, t 39-47): figure-8 orbit from the real ICs in
   video/data.py integrated float64 (scenes.simulate_fig8,
   Yoshida-4) and LABELLED an illustration, beside the video/
   hash-rows idiom - real IAS15FH1 H_state digests for steps
   0/944/2,000 typing out with "desktop == RP2040" and the
   2,001/2,001 BIT-IDENTICAL stamp (data.ias15_digests() re-asserts
   2001 rows + step pins at import; board match re-compared 2001
   this session). KissFFT (rank 69) and tokens (rank 134) keep the
   v2 viz, redrawn parametrically inside the window.
5. **2560x1440, parametric.** Every frame is projected and
   rasterised at output scale (vector projection; fonts sized in
   output px; window content scale feeds font sizes each frame).
   Nothing is ever resized up: **max crop-upscale factor 1.0**
   (the tokens "x500,000 ZOOM" callout is a drawn inset, labelled
   "drawn parametrically"). Line widths scale by median
   focal/depth clamped to [0.25, 1.15].

## Measured camera (measure_camera3.py, 30 fps sampling, t 1-88)

Smootherstep everywhere (analytic zero velocity + acceleration at
joins). Sampled: master-cam pos/target speed 0.56 -> peak 1,509 ->
0.0 units/s; cursor 0 -> 17.4 ranks/s -> 0; at all ten timeline
joins (6.5/28.6/31/39/47/52/60/67/75/79) the one-frame velocity is
0.0-0.35 on BOTH sides; cursor max frame-to-frame dv 0.255 ranks/s
(smooth build/decay). The measurement caught a real half-rank jump
at gate exits during development; legs now start at gate_rank-0.5
and re-measurement is clean (camera_measurements3.json).

## Carry-overs (no regressions)

- Real history only: same history.json at a73e97d (141 commits,
  27 merges, 25 into main; true order/parentage/merge-bases).
  Chase popup copy + sources identical to v1/v2; legend kept.
- Gate 2 numbers are the regenerated set with definition on frame:
  billed 1,196,128,770 = input 1,190,490,305 + output 5,638,465,
  93 labeled rows @ a73e97d, cached 1,165,653,139 inside input,
  ~1:620,399, 7,756 msgs (gate2_numbers.json, unchanged).
- Box ending in-world: marbles arc over the rim and drop in, lid
  shuts on its hinge arc, neon dims to the near-black hold.

## Simplifications (S1-S10, S12 carried; S6/S11 updated; S13-S18 new)

- S1-S5, S7-S10, S12: as polish-report.md (rank axis, one lane per
  merge, red re-gate connectors, wave colours, cursor readout, day
  guides, teaching diagram, billboards, halo glow).
- S6 (updated): IAS15 window at its TRUE merge d9718cf (rank 44);
  KissFFT at true merge 32bbd93 (rank 69); tokens still anchored
  editorially at metrics merge a1a888f (rank 134), said on frame.
- S11 (retired): the axis-turn rescale is gone with the turn.
- S13 (new): the replay draws only ranks [cursor-18, cursor+48];
  history outside the window exists in history.json but is off-
  camera (behind = streamed past, ahead = ghost). This is the
  owner-requested close view, stated on frame.
- S14 (new): the 17 units/rank bed climb is presentation so that
  "newer" reads as "up-screen" in perspective; it encodes no data.
- S15 (new): one marble per active lane rides AT the cursor rank
  (plus three trailing spine marbles); marble count/size/colour
  beyond lane identity encodes no data.
- S16 (new): sendback loop shape, stamp timing and the marble's
  backward ride are presentation; the event rank, lane, commit
  and label are real (sources above + on frame).
- S17 (new): window rise/close is a screen-space interpolation out
  of the projected gate point; content is redrawn at native size
  per frame (never a scaled bitmap). The figure-8 is an
  illustration of the proven run - hashes are the proof, said on
  frame (video/ idiom kept verbatim in spirit).
- S18 (new): the box hop arc is presentation; box position (past
  HEAD on the spine) and the lid hinge arc carry over v2.

## Assembly needs / open items

- Joins: intro white -> t=0 exact; t=87.5 near-black -> outro2
  exact value. Silent, 120 BPM grid; music/VO not attempted.
- Resolution: this segment is now 1440p while video/ scenes are
  1080p - assembly either upscales the other segments (owner's
  pixelation concern) or uses gitvisual3-1080.mp4. Flagging for
  the lead; the 1440p master is the deliverable of record.
- Known visual debts (eyeballed, not hidden): (a) lanes exiting
  the bottom edge render chunky for ~1 rank (halo strokes are
  solid-colour passes, S12 - same family as v1/v2); (b) the PASS
  impact ring renders solid and briefly crosses window captions;
  (c) a branch label can still kiss its marble in dense wave-5
  frames; (d) far-field top-left is sparse by design (close
  window). None block comprehension.
- Production route unchanged: port into video/ at freeze,
  regenerating history.json + gate2_numbers.json then.
- Fences: scratch only + ledger append; muse-softfloat status
  clean after the run; nothing committed; v1/v2 files untouched
  (sizes verified); no path with cft in its name opened, searched
  or listed; renders streamed/bounded (122 s, few-layer frames).
