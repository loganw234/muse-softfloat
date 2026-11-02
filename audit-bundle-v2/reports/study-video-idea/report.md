READY

Segment A (new) "idea breakdown": 14.5 s at 2560x1440, 30 fps,
120 BPM grid, programmatic only (PIL + bundled ffmpeg via
imageio-ffmpeg; helpers/palette shared with the why segment so the
pair reads as one hand). Sits in assembly order messenger intro ->
THIS -> comparison (why2) -> git visual -> outro. Opens on pure
white (intro hand-off) and ends on pure white (why2 opens white, so
the idea->comparison join is a plain hard cut on white). Owner edit
still needed on copy polish and VO/music sync, as with v1.

## Clip (probe-verified)

- idea-1440p.mp4: 14.5 s, 2560x1440, 30 fps, H.264, silent,
  435/435 frames decoded clean (video/probe.py via verify_v2.py,
  decode_rc 0), 1,051,203 bytes. Render: $MSF_PYTHON render_idea.py
  (MSF_PYTHON = workspace .venv python; frames stream to ffmpeg one
  at a time). idea-1080p.mp4 downscale twin rendered same run
  (657,923 bytes).
- Bookends measured on the MP4: stills at 0.2 s and 14.3 s are
  exactly (255,255,255) on all 3,686,400 px (verify_v2.py). Forced
  keyframe at frame 415 keeps the 0.75 s white hold-out exact.
- All motion parametric (draw-time coordinates/font sizes); no
  bitmap is ever crop-upscaled; every frame drawn natively.

## Beat sheet (120 BPM, BEAT = 0.5 s; cuts/dwells on the grid)

| t (s) | beats | content |
|---|---|---|
| 0.0-0.5 | 0-1 | pure-white hold (intro hand-off frame) |
| 0.5-3.0 | 1-6 | THE IDEA: card lines reveal every 0.5 s (software IEEE 754 library; RP2040, no FPU; every float already software; so science runs bit-identically, same bits out) |
| 3.0-6.5 | 6-13 | WHAT "CORRECT" MEANS: number line - representable A vs A+1 ULP (3.0), exact-result dot between them (4.0), arrow lands on A "correctly rounded" / neighbour crossed out (5.0), "right value, right flags" line (5.5), holds to 6.5 |
| 6.5-10.0 | 13-20 | WHAT WILL PROVE IT: IAS15 / interval geometry / KissFFT Fork B cards, one per 1.0 s, last dwells to 10.0 |
| 10.0-12.0 | 20-24 | HOW IT GETS BUILT (method teaser): briefed agents parcel by parcel; every piece independently verified; a verifier whose only job is to disconfirm; "watch it land, commit by commit" (git-visual payoff) |
| 12.0-13.5 | 24-27 | BUT FIRST - WHY NOT USE WHAT ALREADY SHIPS? (hands the question to why2) |
| 13.5-14.5 | 27-29 | fade to white; 0.75 s exact-white hold out |

Dwell (same rule as report-v2.md): every new readable block is the
sole new text for >= 1.0 s and stays on screen; each scene's
completed state holds >= 1.5 s before the cut (idea card complete
2.5->3.0 is 0.5 s at full state but its 5 short lines arrive over
2.0 s and are re-read as a sentence; question holds 1.5 s and is
repeated as why2's title). Stills eyeballed from the MP4:
stills/still_002.8s (idea), 006.2s (correct), 009.5s (prove it),
011.8s (method), 013.0s (question), 000.2s/014.3s (white).

## Claims with sources (facts at muse-softfloat a73e97d only)

| On screen | Source |
|---|---|
| Software IEEE 754 library for the RP2040, binary16/32/64 family project; chip has no FPU, every float is software | README.md title/status; SF-0 3.4 (Cortex-M0+ helper-call model) |
| Real science code bit-identical: same source desktop and chip, same bits out | README.md: IAS15 "bit-identical to the unmodified desktop run - same integrator source, same bits out, on a chip with no FPU"; SF-0 1/9 |
| Correct = correctly rounded vs the infinitely precise result; a 1-ULP neighbour is a wrong answer (number-line, labelled "illustrative" on screen) | SF-0 2.3 definition; the graphic illustrates the definition, it is not a measurement |
| Every flag exact | SF-0 2.4 (five Clause 7 flags, exact conditions) |
| Prove-it workloads: IAS15 binary64 bit-identical every step; interval directed rounding down/up per end; KissFFT Fork B sinPi/cosPi runtime, correctly rounded | SF-0 1/9; SF-1 0.2/2.2; SF-1 0.4/6.4 (as tabulated in scratch/study-video-why/options-facts.md) |
| Briefed agents, parcel by parcel; independently verified; verifier that only disconfirms | README.md ground rules: "Work is split into parcels with briefs; a verifier that only disconfirms stands between each parcel and the push" |

No performance claims, no numbers beyond the sources above, nothing
from any third-party softfloat source (none consulted).

## Budget note

Pair total 14.5 + 32.0 = 46.5 s replacing the 16.0 s v1 why: the
115 s assembly becomes 145.5 s against the 180 s target (34.5 s of
headroom for git/outro growth). If trims are later wanted, cheapest
first: question+white-out -0.5 s, prove-it card stagger 1.0->0.5 s
(-1.0 s), method rows stagger -0.5 s.

## Known limits

- Silent; beats placed for 120 BPM music, no track auditioned.
- "in a minute" in the method footer presumes the git visual's
  current length; re-word if the git segment's timing changes.
- Copy is plain but still technical (ULP); owner may re-word.
