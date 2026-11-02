# Timing / beat sheet - gitvisual2.mp4 (83.0 s, 1920x1080, 30 fps, silent)

All scene cuts on whole seconds of the 0.5 s / 120 BPM grid
(video/style.py). Duration delta vs v1 (78.0 s): **+5.0 s** (+3 chase
lift/travel, +2 pull-back/axis-turn; gates/box unchanged lengths).
Stills are MP4 grabs by video/probe.py into stills2/, eyeballed.

| Time | Beat | What happens | Still |
|---|---|---|---|
| 0.0-1.0 | white hold | Full-frame pure white (255,255,255), intro handoff, held exactly. | still_000.5s.png |
| 1.0-3.0 | flat 2D open | v1's flat white plane (top-down camera): lead/main trail runs left-to-right, first branches as grey ghost nodes ahead. | still_002.0s.png |
| 3.0-6.5 | 2D -> 3D transition | Camera lowers behind-side, trail+branches lift off the plane (shadows stay on the ground grid); smootherstep lift, no cut. | still_005.0s.png |
| 6.5-30.0 | 1 - THE CHASE (3D chase cam) | Camera chases the neon head (behind-side, banking, closes ~20% on each lit node); nodes pop on the beat; screen-space popups hold 2.3 s each, legend throughout. | still_007.5s.png, still_014.0s.png, still_027.0s.png |
| 6.5-8.8 | popup 1 PARCEL | parcel-f32, 173 binary32 rows, owns src/msf32.c only. | |
| 9.8-12.1 | popup 2 ESCALATION | parcel-f32 tininess (Clause 7.5), Berkeley disagreed, fixes 53acb1a/b37fb12. | |
| 13.1-15.4 | popup 3 VERIFIER - SENDBACK | verifier-w5twiddledoc NOT READY: printed SHA-256 is 56 hex chars. | |
| 16.4-18.7 | popup 4 PLANTS GRADED | Wave 1: 9 of 10 caught; the miss named. | |
| 19.7-22.0 | popup 5 GATES | smoke 52,168; standard +1,117,504; 9/9 controls; board 2,767 host==RP2040. | |
| 23.0-25.3 | popup 6 STUDY | feasibility first, in scratch; two study visuals wait as gates. | |
| 26.3-28.6 | popup 7 LEAD MERGE | 2843792 - Wave 1 binary32 (READY 26c76aa); branch rejoins main. | |
| 30.0-34.0 | pull-back + axis switch | Whole tree revealed left-to-right, then one continuous 90-degree turn (rotation + rescale, scale dips mid-turn to stay in frame) until time runs DOWN-TO-UP and the tree fills the screen. White dims to dark stage. | still_032.0s.png (mid-turn), still_033.5s.png (turned) |
| 34.0-46.0 | 2 - replay A (grows UP) | Real topology, ranks 0 -> 68 upward; cursor rises; merges pop green rings. Stops at GATE 1 (KissFFT merge 32bbd93, rank 69). | still_040.0s.png |
| 46.0-54.0 | GATE 1 - KISSFFT STUDY | v1 idiom (waveform/twiddles/spectrum, labelled numpy illustration) + six Pico mockups blinking; at 52.5 gate PASS impact (ring/shake), gate lifts, ALL SIX LEDs HOLD SOLID 52.5-54.0. | still_051.0s.png (working), still_053.2s.png (PASS solid) |
| 54.0-62.0 | replay B | Ranks 69 -> 133 upward (SF-2 waves). Stops at GATE 2 (metrics merge a1a888f, rank 134). | still_058.0s.png |
| 62.0-70.0 | GATE 2 - TOKENS, RECOUNTED | REGENERATED numbers (definition on frame): billed 1,196,128,770 = input 1,190,490,305 + output 5,638,465 over 93 labeled rows, usage.jsonl @ a73e97d (cached 1,165,653,139 inside input); owner ~1,928 frozen study est.; ~1:620,399; 0.00016%; 7,756 logged msgs. Six Picos; PASS solid 68.5-70.0. | still_067.0s.png, still_069.2s.png |
| 70.0-75.0 | replay C | Ranks 134 -> 140 to HEAD a73e97d; 141/141 commits, 25/25 merges. | still_074.0s.png |
| 75.0-83.0 | 3 - BOXED | Trail into isometric open box (75-78); lid swings shut on hinge arc (78.2-79.6); neon dims (79.6-81); fade to near-black hold (81-83). | still_077.0s.png (open), still_079.8s.png (shut), still_082.5s.png (near-black) |

Handoffs measured on the MP4 (verify_handoff2.py):
- t=0.5 s: all 2,073,600 px exactly (255,255,255).
- t=82.5 s: 2,073,572 px (2,3,8) = outro2's first frame (measured
  1 unique color (2,3,8)); 28 px at (2,2,10), within 2 levels (encoder
  noise in the held near-black, not a picture difference).

Camera smoothness (measure_camera.py -> camera_measurements.json):
smootherstep everywhere; sampled head velocity at every keyframe join
is 0.0-7.4 units/s on both sides vs 1,309 peak (analytic 0); axis-turn
angular speed 0 -> 1.1 -> 0 rad/s, max frame-to-frame dv 0.041 rad/s.
