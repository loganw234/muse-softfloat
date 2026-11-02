READY

v2 polish pass over the v1 rough draft. v1 artifacts untouched
(intro.mp4 448,498 B / outro.mp4 385,083 B, sizes unchanged);
all v2 work in scratch/study-video-intro/, nothing committed.
Script: render_v2.py (re-run with workspace .venv python).
Measurements: measurements2.json. Verify: verify2.py.

## Clips (probe-verified via video/probe.py, 1920x1080 / 30 fps / H.264 / silent)

- intro2.mp4: 5.0 s, 150/150 frames decoded, rc 0, 643,997 bytes.
  (v1 was 4.0 s; +1.0 s buys the breath + longer dive — see fix 2.)
- outro2.mp4: 6.0 s, 180/180 frames decoded, rc 0, 536,110 bytes.

## Handoff specs — NOT MOVED (re-verified on decoded MP4 stills)

- intro2 final hold (4.5–5.0 s): still2_004.8s.png — every pixel
  exactly (255,255,255), min=max=255 after H.264 round-trip.
- outro2 first frame: still2_000.0s.png — uniform (2,3,8) decoded
  (source 3,4,9), identical to the v1 spec. No objections.

## Fix 1 — INTRO period accuracy (measured, not eyeballed)

Root cause in v1: the zoom target y was `ty + ascent/2` (mid-cap-height),
but a period's ink sits on the baseline. Measured on the rendered
full-message plate (white-ink segmentation of the bubble, connected
components, intensity-weighted centroid):

- Final "." raster ink centroid: (1170.49, 272.0) px; ink core 2x3 px,
  bbox x 1170–1171, y 271–273 (R>150 core).
- Font-metrics cross-check (textlength advance split + textbbox of the
  lone glyph): (1171.0, 272.5) — agrees within 0.5 px on both axes.
- v1 formula point: (1171.0, 259.0) — exactly 13.0 px too high in
  source space (magnified ~200x by the dive). That was the miss.
  See still2_period_bubble.png (red cross = raster centroid on the
  final dot; yellow cross = v1 point).
- Applied the +0.5 px index->continuous shift PIL's resize box needs:
  camera target (1170.99, 272.5); subpixel float-box zoom throughout.
- Proof (still2_period_proof.png, clean copy still2_period_midzoom.png):
  pre-encode frame at t=3.40 s, crop width 95.4 px (~20x). Measured
  period-ink centroid in the output frame (959.1, 539.6) vs frame
  center (959.5, 539.5): error (-0.4, +0.1) px, |error| 0.4 px.
  An earlier iteration without the +0.5 shift measured 14.3 px off at
  a wider crop; that is what the shift fixed — kept as evidence the
  proof can actually fail.
- Final crop 1.2x0.675 px sits inside the 2x3 ink core; last camera
  frames measure mean RGB ~(246,248,254) (AA fringe only) before the
  on-beat cut to pure white at 4.5 s.

## Fix 2 — INTRO smoothness

Timeline (all cuts on the 0.5 s / 120 BPM grid): 0.0–0.5 phone enter
(0.94->1.0 ease-out fade), 0.5–1.5 typing dots, 1.5–2.0 message types
out, 2.0–2.5 BREATH (full message held, camera static), 2.5–4.5 dive,
4.5–5.0 white hold.

Camera: smootherstep (6u^5-15u^4+10u^3; zero velocity and acceleration
at both ends) driving log-scale crop width 1920 -> 1.2 px; center path
eases frame-center -> period over the first 45% then locks (aim, then
dive). The static breath joins the dive C1-smoothly because the
curve's start derivative is zero.

Measured from the per-frame camera log (verify2.py / measurements2):
first-frame log-scale step -0.00033, last -0.00226, max frame-to-frame
change in log-step 0.0118 (monotonic build/decay, no velocity steps);
center speed 4.9 -> peak 709 -> 0.0 px/s. Clamp never engages
(dense 401-sample check: max required adjustment 0.0 px).
Crop/center samples: 2.50s 1920px@(960,540); 2.83s 1478@(1017,468);
3.17s 408@(1147,303); 3.50s 48@(1171,272.5); 4.17s 1.6@(1171,272.5).

## Fix 3 — OUTRO camera (true reverse, composed frame)

Outro camera is the intro curve run backwards — same smootherstep +
log-scale family, intro_cam(1-u): 0.0–0.5 dots fade in from near-black
at the start state (200 px crop centered on the typing-dots centroid),
0.5–2.5 pull-back to full frame, settle (zero end velocity), 2.5–3.0
typing breath in the settled frame. Dots centroid raster-measured
(990.0, 409.3) vs layout (990, 410); camera target (990.5, 409.8).
Reverse-path clamp check: max adjustment 0.10 px (subpixel, final
settle only). Dots keep bouncing during the move (live scene is
camera-transformed per frame, not a frozen plate).

Composition is deliberate: phone at x 880–1420 (right of center),
leaving a wide left field and a narrow right column for fix 5.

## Fix 4 — OUTRO copy (trimmed, user message lost)

- v2 reply (outro_msg2.txt), 160 chars vs v1 370 (43%):
  "Done — it held up." / "849/849 ops across b16/b32/b64. 411,213
  vectors in the gate, IAS15 identical on all 6 boards. Small
  parcels; verifiers that only disconfirm."
- Numbers retain v1's a73e97d provenance (849/849, 411,213, 6 boards,
  IAS15); dropped detail (783+66 split, H=20, KissFFT, plants, hashes)
  moved to the side cards or cut.
- The "Hey Muse..." bubble is gone as readable text: the outro chat
  opens scrolled — a blue bubble cropped under the header divider
  (20 px sliver, no text), then two unreadable "bar" bubbles (grey,
  blue) implying intervening exchange, then the typing bubble.
  Eyeballed in still2_002.8s.png / still2_005.8s.png.

## Fix 5 — OUTRO side space (sequenced with the reply)

- 3.5 s (as reply bubble 2 starts): left card "HUMAN : AI — THE WORK
  SPLIT". Project bar full-width, owner as a 3 px amber tick labelled
  "1 px is too wide — shown 3 px"; headline ≈ 1 : 620,000.
  Numbers: project 1,196,128,770 = input 1,190,490,305 + output
  5,638,465 summed by sum_metrics.py over the refreshed
  muse-softfloat/docs/metrics/usage.jsonl at a73e97d (93 rows,
  waves 0-5; HEAD verified a73e97d). Owner ~1,928 est. from the tokens
  study (chars/4 +/-30%, 40 prompts, 2026-10-28). The study's
  double-counted 38.6M add-back is not used anywhere. Definitions
  printed on-frame at 19 px, eyeballed in still2_005.8s.png.
- 4.0 / 4.5 / 5.0 s (one per beat, tracking the reply sentences):
  right stat cards 849/849 instantiations b16/b32/b64; 411,213
  vectors in the merge gate; 6 boards · IAS15 2,001/2,001 state
  hashes. Each fades/slides 18 px over 0.5 s; restrained dark cards,
  single accent bar each. 5.0–6.0 s hold on the full composition.

## Stills (all eyeballed by me)

- still2_period_proof.png / still2_period_midzoom.png — centroid proof.
- still2_period_bubble.png — source-plate annotation (v1 vs v2 target).
- stills2/intro/still2_000.2s … 004.8s (9 MP4 grabs).
- stills2/outro/still2_000.0s … 005.8s (8 MP4 grabs).

## Assembly still needs

- Duration change: intro is now 5.0 s (was 4.0 s) — total intro+outro
  11.0 s; middle/music budget shifts by +1.0 s. Grid and both handoff
  frame values unchanged; joins are as v1 specified.
- Owner sign-off on: trimmed reply wording, "Done — it held up."
  opener, side-card wording, and the metrics-source choice in fix 5.
- Music/VO still open (silent by design); watch-through at speed for
  motion feel (smoothness here is analytic + still-based, see below).
