# Timing / beat sheet - gitvisual4.mp4 (88.0 s, 2560x1440, 30 fps, silent)

All boundaries on whole seconds of the 0.5 s / 120 BPM grid
(video/style.py), IDENTICAL to v3 (88.0 s, delta +0.0): the
packaging beat was bought inside the existing box window
(79-88 s) by trading the old roll-in/lid timings, not by adding
time. v4 = v3 + marble sync (one clock for marbles and the events
they ride) + packaging ending (every legend marble files in).
One continuous space throughout; no scene exit after t=1.0.
Stills are MP4 grabs by video/probe.py into stills4/, eyeballed.

| Time | Beat | What happens | Still |
|---|---|---|---|
| 0.0-1.0 | white hold | Full-frame pure white (255,255,255), intro handoff, held exactly. | still_000.5s.png |
| 1.0-3.0 | flat 2D open | Flat white plane: marble trail runs left-to-right, first branches as grey ghost nodes ahead. | still_002.0s.png |
| 3.0-6.5 | 2D -> 3D lift | Camera lowers behind-side; tracks lift off the plane; smootherstep, no cut. | still_005.0s.png |
| 6.5-28.6 | 1 - THE CHASE | Camera chases the head marble; each node lights on the exact frame its split marble arrives (v4: lighting gated on head_x, the marble's own clock; the marble then parks ON its node); seven sourced teaching popups hold 2.3 s each (copy unchanged); legend throughout. | still_009.8s.png, still_014.0s.png, still_027.0s.png |
| 28.6-31.0 | bridge (no cut) | One continuous flight into the dark stage and the closer angled replay camera. No full-tree reveal. | still_030.0s.png |
| 31.0-39.0 | replay A (up-stream) | Real topology, ranks 0 -> 44; marbles are pure functions of the cursor: split at true merge-bases, absorb on merge frames, sit ON node centers; sendback loops at rank 7 (4cdb912) and rank 12 (tininess re-gate) entered/exited on their event ranks, stamps land on the loop apex; lead fix rank 38. Wave-1 lane-split snap (v1-v3) fixed. | still_033.5s.png, still_033.9s.png, still_037.0s.png |
| 39.0-47.0 | WINDOW - IAS15 | Window rises at merge d9718cf (rank 44); the cursor (and head marble) wait exactly ON the gate rank - no half-rank gap, no bob. Figure-8 illustration + IAS15FH1 hash rows 0/944/2,000 + six Pico mockups; PASS solid 45.5-47.0; closes into the green check. | still_042.0s.png, still_045.8s.png, still_046.7s.png |
| 47.0-52.0 | replay B | Ranks 44 -> 69 (SF-1 waves). | still_050.0s.png |
| 52.0-60.0 | WINDOW - KISSFFT | Same mechanics at merge 32bbd93 (rank 69); PASS solid 58.5-60.0. | still_055.0s.png, still_058.8s.png, still_059.7s.png |
| 60.0-67.0 | replay C | Ranks 69 -> 134; defect-fix loop rank 99 (048aa29), verifier sendback loop rank 114 (a41f026). | still_063.4s.png, still_064.8s.png |
| 67.0-75.0 | WINDOW - TOKENS | At metrics merge a1a888f (rank 134, S6): billed 1,196,128,770 = input 1,190,490,305 + output 5,638,465, 93 labeled rows @ a73e97d (cached 1,165,653,139 inside input); PASS solid 73.5-75.0. | still_070.0s.png, still_073.8s.png, still_074.7s.png |
| 75.0-79.0 | replay D | Ranks 134 -> 140 to HEAD a73e97d; 141/141 commits, 25/25 merges. | still_077.0s.png |
| 79.0-88.0 | 3 - BOXED (packaging) | Every legend system marble files into the box in queue order (parcels, verifiers, plants, gates, studies, escalations, lead/main last), each arcs over the front rim and drops in (79-83.2); as they land the box front stamps what is kept - RECORD, LEDGERS, VECTORS, METRICS; the lid waits for 7/7, then shuts on its hinge arc (84.0-85.3); neon dims; fade to near-black hold (86-88). | still_080.6s.png (first hop), still_081.8s.png (3/7), still_082.9s.png, still_084.8s.png (7/7, lid closing), still_085.8s.png (shut), still_087.5s.png (near-black) |

Handoffs measured on the MP4 (verify_handoff4.py), VALUES unchanged
from v1-v3 at 2560x1440 (3,686,400 px):
- t=0.5 s: all 3,686,400 px exactly (255,255,255).
- t=87.5 s: 3,685,376 px (2,3,8) = outro2's first frame (measured
  1 unique color (2,3,8)); 1,024 px at (2,3,6), within 2 levels -
  the identical encoder-noise fingerprint as v3.

Sync (measure_sync4.py -> sync_measurements4.json): at the
continuous event time (cursor/head exactly on the event), marble
centroid vs node center = 0.0 px for all 7 chase lightings, 25
splits, 25 absorbs, 17 sampled exclusive nodes, 5x3 sendback
entry/apex/exit, 3 gate arrivals (v3: 14.3-35.0 px, plus a ~101 px
one-frame lane teleport on the two Wave-1 splits). On the nearest
rendered 30 fps frame the residual is ≤25.7 px - pure frame
quantization of a moving cursor (marble, lighting and lane are
evaluated from the same cursor value on that frame). BPM pulse
moves no center: measured centroid drift during a gate hold
0.0 px (v3: 1.76 px from its gate bob).
