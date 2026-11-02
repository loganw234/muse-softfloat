# study-video-gitvisual-v6 - report

Base: production `muse-softfloat/video/segments/gitvisual.py` (v5)
at main `97e10a4` (git HEAD verified), copied to
`scratch/study-video-gitvisual-v6/gitvisual6.py` with its data JSONs
and edited there. Repo untouched (read-only for this parcel).
Renderer: `gitvisual6.py` (68,275 B, sha256 `0483b429f11c...`).
Video: `gitvisual6.mp4`, 102.0 s, 2560x1440 @ 30 fps, 3,060 frames,
32,232,109 B, sha256 `3351e8ae492f...`, rendered with the workspace
.venv python (MSF_PYTHON). Render wall time: 135 s (record, not a
rate). Stills in `stills6/`. Handoffs measured on the MP4
(`verify_handoff6.py` -> `handoff6.json`): t=0.5 s all 3,686,400 px
exactly (255,255,255); t=101.5 s 3,686,220 px (2,3,8) + 180 px
(2,2,10) encoder noise (v5 measured 492 px of the same class).

## Owner change 1 - replay in the introduction's chase language

`replay_cam` rewritten: camera offset from the cursor point
`R3(cur,0)` is now chase_cam's lifted offset (-980,-760,+500) with
the same ~380-unit look-ahead and focal px(1150), riding the
climbing track (offset taken from the ramp point, so the camera
climbs DZ per rank with the head marble). Measured camera-to-head
depth over the replay: 1049-1319 world units, against 1044-1321
sampled in the chase itself (`measure_sync6.py`) - the same
language, numerically. Gate holds get the chase's node-arrival
emphasis (20% close-in while a window is up, roll damped). The
bridge still lands without a cut; its focal is now constant
px(1150), removing v5's small 1300->1200 focal step at T_REPLAY
(both ends are chase now). Replay draw window recentred
cur-18..+48 -> cur-30..+36 (same span) for the closer framing.

Invariants held and measured (`sync_measurements6.json`): topology/
lanes/colours/`cursor_rank`/gate holds/leg wall times untouched;
at-event marble-vs-node distance 0.000 px for all 7 chase
lightings, 25 splits, 25 absorbs, 17 sampled exclusive nodes, 5x3
sendback entry/apex/exit, 3 gate arrivals - now under the new
camera. Nearest-frame residual grows to <=57.2 px (v5: <=26.1):
pure 30 fps quantisation magnified by the closer camera (plus leg
C, see change 3); at-event it is exact.

Readability (brief asked for stills, not silent widening):
- Two collisions appeared at chase distance and were fixed without
  touching the camera: sendback label blocks are clamped fully
  on-frame, and a branch-name billboard is skipped while it would
  overdraw a sendback label block (it returns when clear). Before/
  after: `stills6/test_048.5s.png` vs
  `stills6/still_048.5s_replay_chase.png`.
- Residual, accepted and flagged for the owner: at chase distance
  the nearest lanes sweep very large past the frame edges during
  gate close-ins (visible behind the IAS15 window,
  `stills6/test_056.0s.png`), and on the busiest Wave-5 stretch the
  head marble can briefly cover a branch name
  (`stills6/test_077.2s.png`). Lane identity mid-leg rests more on
  colour + the HUD commit ticker than on the wide tree shape v5
  showed. No leg was widened back out.

Rejected: keeping v5's up-ramp target (look 900 ahead) at a closer
offset - it kept the "looking up a hill" read the owner asked to
leave; the chase look-ahead along the ramp is what makes it read
like the introduction.

## Owner change 2 - ending: opening, not a box

`draw_box` replaced by `draw_opening`: a slab in the (climbing)
track plane at the same end position (BOX_RANK = LAST+16) with a
600x640 opening and a 520-deep shaft. Same `PACK_ORDER`, labels and
stamps. Each of the seven marbles rides v5's travel timing to the
near rim, tips 0.15 s, then free-falls: `z_off = -(8 + g dt^2/2)`,
g = 3400 units/s^2 (plane to floor ~0.55 s; second difference
measured -8.5 = -g*0.05^2 exactly). Marbles below the plane are
drawn before the slab so the near rim swallows them; landed
marbles glint on the shaft floor in their system colours - what
falls in is kept, nothing scattered. The `muse-softfloat` label
stands on a plate beyond the opening, stamps RECORD/LEDGERS/
VECTORS/METRICS under it as the count fills; label is drawn
through the whole fade (only its ink dims). HUD: "3 - KEPT" /
"every system drops in, kept" / counter. T_BOX 93.0, T_FADE 100.0,
TOTAL 102.0 unchanged; end handoff measured above. All 7 inside
by lt 5.5 (t=98.5), before dimming starts at lt 5.8.
Stills: `still_096.3s_midfall.png` (plants tipping, verifiers
falling, studies approaching), `still_099.3s_final_label.png`
(7/7, all stamps, label legible).

Rejected: a flat (non-climbing) slab - the marbles ride the ramp,
so a level slab would sit 60 units off the track plane at the rim;
the slab follows `plane_z(x)` instead. Rejected: a bounce/settle
on the shaft floor (extra motion language; gravity + swallow
reads cleaner). Note: landed marbles on the floor are only dimly
visible from this camera (the floor is a deep sliver) - the
disappearance reads, the kept pile mostly does not; flagged below.

## Owner change 3 - tokens out, augmented-interval epilogue in

The TOKENS window, `viz_tokens`, `G2_RANK` and the
`gate2_numbers.json` load are deleted; the renderer imports and
runs with the file absent (smoke-tested; the copied JSON was
removed from this scratch). No token figures remain anywhere in
the segment (the word survives only in two source comments
recording the removal).

Chronology (the brief's preferred option): the interval gate is
an EPILOGUE after the last frozen-history rank. Replay leg C
(74-81 s) now runs 69 -> 140 (HEAD); the gate sits in the tokens
window's exact wall time (81-89 s) with its hold exactly on
LAST_RANK; 89-93 s is the parked settle at HEAD before the
opening. On screen it is labelled "epilogue - Wave 6, after HEAD".
Gate ranks measured: [44, 69, 140]; cursor == 140.0 at every
sample through window + settle. Anchoring it at the old tokens
rank (134) was rejected: it would date a Wave 6 result inside the
frozen a73e97d history. Price of honesty: leg C carries 6 more
ranks in the same 7.0 s (~9% faster marble stream on that leg
only); gate windows and all other leg timings keep v5 wall times.

Sample (retained prep: `prep_augint_sample.py` ->
`augint_sample.json`): `tests/interval_catalogue.tsv` row id 1
(family tangent400, sphere; provenance "tangent-by-construction
seed=4242 trial=1 k=16 eps_ulps=1"). Selection rule: first sphere
row in file order whose stage-1 and stage-2 intervals both
straddle zero. Exact discriminant by Fraction arithmetic on the
stored bit patterns, cross-checked in-script against the row's
`exact`/`exact_extra` columns (script asserts equality):
-10843225/70368744177664 = -1.54e-7 -> MISS (the row's naive
column says TANGENT0). On screen: row id, the three stages
tightening around zero, exact stage-3 point + "negative: a true
MISS". Stage-1/2 endpoints shown (-1536/+1024, -9.54e-7/+9.54e-7)
come from the prep's directed-rounding replay (exact Fraction ops
rounded outward onto the binary32/64 grids, C op order); the bars
use a signed-log axis because the widths span ~9 decades, and are
labelled on screen "bars: illustration (log scale)" - the stage-3
value/verdict are the exact claim, the bar widths are the picture
of it. The C workload's own counted stage endpoints were not
re-run for this still-life; see Unverified.

## Every number on screen, sourced

New/changed copy only (everything else is v5's, sourced in
`scratch/study-video-gitvisual/polish5-report.md`):

| On screen | Source |
|---|---|
| catalogue row 1 of 710 | tests/interval_catalogue.tsv row id 1; 710 rows per docs/RECORD.md Wave 6 entry |
| stage 1 [-1536, +1024] | prep_augint_sample.py replay (illustration-labelled) |
| stage 2 [-9.54e-7, +9.54e-7] | prep_augint_sample.py replay (illustration-labelled) |
| stage 3 -1.54e-7, MISS | exact Fraction disc -10843225/70368744177664, = TSV exact_extra + exact column |
| 710 / 710 rows - same answers | RECORD.md Wave 6: "Classifications are identical ... over all 710 frozen catalogue rows"; BOARD.md "all 710 rows again host == board" |
| stage-3 calls: 283,314 -> 63,305 | RECORD.md Wave 6: "(stage 3: 283,314 -> 63,305)" |
| host == board: ae04caf0...c1422 | RECORD.md `ae04caf01229...66c1422`; BOARD.md `ae04caf0...66c1422` (screen keeps head...tail-c1422 form) |
| marbles in: n / 7 | pack_state count of the 7 legend systems (DEEP/PACK_ORDER, v5) |
| src tag "src: RECORD + BOARD, Wave 6" | docs/RECORD.md + docs/BOARD.md as above |

Text pacing RULE applied to all new copy (dwell = smallest 0.5 s
multiple >= max(1.5, 0.5 + words/2.5); measured against each
block's on-screen residence until the next beat/window close;
headlines <=6 words, body <=10, <=2 new lines per beat, one src
tag): title+sub 6 words/8 s; row line 8 words (needs 3.7 s, has
~7.6); question 5 words; stage captions 5 and 4 words (need
2.5/2.5 s, have 2.2/2.2 s to the next beat and persist to window
end); verdict 4 words (needs 2.5, has 1.9 to close - old text may
persist, and PASS + 6 solid LEDs carry the close as in v5);
aggregates 5+4+3 words land at lt 2.4 as their own beat and read
for 5.6-6.4 s (per-line needs 2.5/2.5/2.0). "3 - KEPT" headline 3
words, sub 5 words, 7 s scene. Numbers/hashes are not prose;
counted as one token each in the word tallies above.

## What could not be verified

- Motion judgement is from stills + the analytic sync/camera
  measures; I did not watch the MP4 play. Perceived speed of leg C
  at chase distance and of the fall (~0.55 s per marble) wants
  owner eyes.
- Stage-1/2 interval endpoints are my directed-rounding replay,
  not values captured from `iw_sphere_stage1_f32/stage2_f64`
  running. They rigorously enclose the exact discriminant
  (asserted in the prep), and the window labels them
  illustration; capturing the C endpoints would need a host build
  of the workload, out of this parcel's scope.
- The kept marbles on the shaft floor are barely visible from the
  end camera; "kept, not scattered" reads mainly via the stamps
  and the 7/7 counter. If the owner wants the pile seen, the
  opening dolly would need to end higher/more overhead.
- ffprobe is not bundled with imageio-ffmpeg; container facts
  come from the render log + ffmpeg decode pass (3060 frames,
  time=00:01:42.00) in verify_handoff6.py's fallback path.
- Assembly with neighbouring segments (intro/outro joins) is
  unchanged in VALUES but not re-assembled here; that is the
  lead's integration step after owner review.

## Files (scratch/study-video-gitvisual-v6/)

gitvisual6.py (renderer), gitvisual6.mp4, history.json /
spectrum_n256.json / input_n256.json (copied data), augint_sample.json
+ prep_augint_sample.py (exact prep), measure_sync6.py ->
sync_measurements6.json, verify_handoff6.py -> handoff6.json +
handoff6_{open,end}.png, stills6/ (4 named deliverable stills +
test_* working stills), report.md (this file).
