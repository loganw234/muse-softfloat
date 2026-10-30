# Timing / beat sheet - gitvisual3.mp4 (88.0 s, 2560x1440, 30 fps, silent)

All boundaries on whole seconds of the 0.5 s / 120 BPM grid
(video/style.py). Duration delta vs v2 (83.0 s): **+5.0 s**
(+8.0 new IAS15 window, -4.0 pull-back/axis-turn removed,
+1.0 bridge/box rebalance). ONE continuous space throughout:
the chase trail runs into the real-history track (rank 0 sits just
past the chase head) and on into the box; gates rise as windows
from the track plane - there is no scene exit after t=1.0.
Stills are MP4 grabs by video/probe.py into stills3/, eyeballed.

| Time | Beat | What happens | Still |
|---|---|---|---|
| 0.0-1.0 | white hold | Full-frame pure white (255,255,255), intro handoff, held exactly. | still_000.5s.png |
| 1.0-3.0 | flat 2D open | Flat white plane (top-down camera): the marble trail runs left-to-right, first branches as grey ghost nodes ahead. | still_002.0s.png |
| 3.0-6.5 | 2D -> 3D lift | Camera lowers behind-side; tracks lift off the plane (shadows stay on the grid); smootherstep, no cut. | still_005.0s.png |
| 6.5-28.6 | 1 - THE CHASE | Camera chases the head marble; branch marbles split off at each fork; seven sourced teaching popups hold 2.3 s each (copy unchanged from v1/v2); legend throughout. | still_014.0s.png, still_027.0s.png |
| 28.6-31.0 | bridge (no cut) | One continuous flight: white dims to the dark stage, the teaching track runs on into the REAL history track ahead; camera settles into the closer angled replay position. No full-tree reveal anywhere. | still_030.0s.png |
| 31.0-39.0 | replay A (up-stream) | Real topology, ranks 0 -> 43.5; angled camera rides the cursor, marbles split at forks / rejoin at merges (green pops); sendback loops at rank 7 (4cdb912) and rank 12 (tininess re-gate) bounce back, get stamped, rejoin; lead fix at rank 38. | still_033.8s.png, still_034.5s.png, still_037.0s.png |
| 39.0-47.0 | WINDOW - IAS15 (NEW) | Window rises from the gate line at the true beat (merge d9718cf, rank 44): figure-8 orbit (real ICs, float64 illustration) + IAS15FH1 H_state hash rows (steps 0 / 944 / 2,000, desktop == RP2040) + six Pico mockups blinking; 2,001/2,001 stamp; PASS holds all six LEDs solid 45.5-47.0; window closes into the green check on the track, flow resumes. | still_042.0s.png (open), still_045.8s.png (PASS solid), still_046.7s.png (check close) |
| 47.0-52.0 | replay B | Ranks 43.5 -> 68.5 (SF-1 waves); passed IAS15 check rides the track behind. | still_050.0s.png |
| 52.0-60.0 | WINDOW - KISSFFT | Same window mechanics at merge 32bbd93 (rank 69): waveform -> twiddles -> spectrum (labelled numpy illustration) beside the six Picos; PASS solid 58.5-60.0; closes into a green check. | still_055.0s.png (open), still_058.8s.png (PASS), still_059.7s.png (close) |
| 60.0-67.0 | replay C | Ranks 68.5 -> 133.5 (SF-2 waves); defect-fix loop at rank 99 (048aa29), verifier sendback loop at rank 114 (a41f026, SHA-256 56 -> 64 chars). | still_063.8s.png, still_064.8s.png |
| 67.0-75.0 | WINDOW - TOKENS | Same mechanics at metrics merge a1a888f (rank 134, editorial anchor S6): regenerated numbers with definition on frame - billed 1,196,128,770 = input 1,190,490,305 + output 5,638,465, 93 labeled rows, usage.jsonl @ a73e97d (cached 1,165,653,139 inside input); owner ~1,928 frozen; ~1:620,399; PASS solid 73.5-75.0; closes into a green check. | still_070.0s.png, still_073.8s.png, still_074.7s.png |
| 75.0-79.0 | replay D | Ranks 133.5 -> 140 to HEAD a73e97d; 141/141 commits, 25/25 merges. | still_077.0s.png |
| 79.0-88.0 | 3 - BOXED (in-world) | Camera dollies along the same spine to the box past HEAD; marbles roll in and arc over the rim (79-82.4); lid shuts on its hinge arc (82.4-83.8); neon dims; fade to near-black hold (86-88). | still_081.0s.png (open), still_084.5s.png (shut), still_087.5s.png (near-black) |

Handoffs measured on the MP4 (verify_handoff3.py), VALUES unchanged
from v1/v2, now at 2560x1440 (3,686,400 px):
- t=0.5 s: all 3,686,400 px exactly (255,255,255).
- t=87.5 s: 3,685,376 px (2,3,8) = outro2's first frame (measured
  1 unique color (2,3,8)); 1,024 px at (2,3,6), within 2 levels
  (encoder noise in the held near-black, not a picture difference).

Camera (measure_camera3.py -> camera_measurements3.json):
smootherstep everywhere; sampled cursor/head velocity at every
timeline join (6.5 / 28.6 / 31 / 39 / 47 / 52 / 60 / 67 / 75 / 79 s)
is 0.0-0.35 units/s on both sides vs peaks of 1,309 (head) and
17.4 ranks/s (cursor); cursor max one-frame dv 0.255 ranks/s.
All rendering is parametric at 2560x1440 - max crop-upscale 1.0.
