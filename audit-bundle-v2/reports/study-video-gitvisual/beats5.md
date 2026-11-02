# Timing / beat sheet - gitvisual5.mp4 (102.0 s, 2560x1440, 30 fps, silent)

v5 = v4 + text/pacing revision (ledger/briefs/study-video-textpacing.md,
Agent B). Identical events, ranks, gates (8.0 s each), legs (8/5/7/4 s)
and box mechanics; the only timing change is in the chase: each popup
hold grows from 2.3 s to its rule dwell (smallest 0.5 s-grid multiple
>= max(1.5, 0.5 + words/2.5)) and the head marble waits on its node.
Everything after the chase shifts by SHIFT = +14.0 s (dwell sum
16.1 -> 30.0 s = +13.9, bridge 2.4 -> 2.5 s = +0.1 so the replay
still starts on a whole second). Total 88.0 -> 102.0 s.
Stills are MP4 grabs by video/probe.py into stills5/, eyeballed.

| Time | Beat | What happens | Still |
|---|---|---|---|
| 0.0-1.0 | white hold | Full-frame pure white (255,255,255), intro handoff, held exactly. | still_000.5s.png |
| 1.0-3.0 | flat 2D open | Flat white plane: marble trail runs left-to-right, first branches as grey ghost nodes ahead. Strip: "1 - THE CHASE \| flat plane"; one scene src tag bottom-right. | still_002.0s.png |
| 3.0-6.5 | 2D -> 3D lift | Camera lowers behind-side; tracks lift off the plane; smootherstep, no cut. | still_005.0s.png |
| 6.5-42.5 | 1 - THE CHASE | Seven teaching popups (title + 2 short lines, plain copy, no per-popup src stamp). Arrivals 6.5 / 11.0 / 16.5 / 21.5 / 26.5 / 32.5 / 38.0; rule dwells 3.5 / 4.5 / 4.0 / 4.0 / 5.0 / 4.5 / 4.5 s; each node still lights on the exact frame its split marble arrives (lighting gated on head_x); legend unchanged throughout. | still_008.0s.png, still_013.0s.png, still_018.5s.png, still_023.5s.png, still_029.0s.png, still_034.5s.png, still_040.0s.png |
| 42.5-45.0 | bridge (no cut) | One continuous flight into the dark stage and the closer angled replay camera (2.5 s; v4: 2.4). No full-tree reveal. | still_044.0s.png |
| 45.0-53.0 | replay A (up-stream) | Real topology, ranks 0 -> 44; marbles pure functions of the cursor; sendback loops at ranks 7 (4cdb912), 12 (tininess) and lead fix rank 38 - same events, shorter labels ("SENDBACK FIX 4cdb912 / error-value branch fixed"), no per-label src lines, labels persist readable then dimmed to rank+18. HUD: "2 - AS IT HAPPENED", one replay src tag in the footer. | still_047.0s.png, still_048.5s.png, still_051.0s.png |
| 53.0-61.0 | WINDOW - IAS15 | "IAS15 RUNS ON THE CHIP" at merge d9718cf (rank 44); cursor waits ON the gate rank. Figure-8 picture + real hash rows 0/944/2,000 (rows type faster: complete at lt 1.2/2.2/3.2) + stamp "2,001 / 2,001 IDENTICAL" at lt 3.5 + six Pico mockups; PASS (one word, six LEDs solid) 59.5-61.0; closes into the green check. One src tag in the title bar. | still_056.0s.png, still_059.7s.png, still_060.7s.png |
| 61.0-66.0 | replay B | Ranks 44 -> 69 (SF-1 waves). | still_063.5s.png |
| 66.0-74.0 | WINDOW - KISSFFT | "KISSFFT STUDY" at merge 32bbd93 (rank 69); wave/twiddle/spectrum captions staggered (<=2 new lines per beat); stamp "12 / 12 SETUPS CHECKED" now at lt 3.6 (was 6.3) so it gets its dwell; PASS 72.5-74.0. | still_070.0s.png, still_073.7s.png |
| 74.0-81.0 | replay C | Ranks 69 -> 134; defect-fix loop rank 99 (048aa29), verifier sendback rank 114 (a41f026), short labels. | still_077.5s.png, still_079.0s.png |
| 81.0-89.0 | WINDOW - TOKENS | "TOKENS, RECOUNTED" at metrics merge a1a888f (rank 134): billed 1,196,128,770 = input 1,190,490,305 + output 5,638,465, cached 1,165,653,139 inside input, 93 rows - same numbers, plainer captions, final ratio lines now at lt 2.6 (was 4.8); PASS 87.5-89.0. | still_084.0s.png, still_087.7s.png, still_088.7s.png |
| 89.0-93.0 | replay D | Ranks 134 -> 140 to HEAD a73e97d; 141/141 commits, 25/25 merges. | still_091.0s.png |
| 93.0-102.0 | 3 - BOXED (packaging) | Unchanged mechanics: every legend system marble files into the box (labelled), stamps RECORD / LEDGERS / VECTORS / METRICS, lid waits for 7/7 then shuts (98.0-99.3); captions trimmed ("every system packed away", counter only); fade to near-black 100-102. | still_094.6s.png, still_095.8s.png, still_098.8s.png, still_099.8s.png, still_101.5s.png |

Handoffs measured on the MP4 (verify_handoff5.py), VALUES unchanged
from v1-v4 at 2560x1440 (3,686,400 px):
- t=0.5 s: all 3,686,400 px exactly (255,255,255).
- t=101.5 s: 3,685,908 px (2,3,8) = outro2's first frame (measured
  1 unique color (2,3,8)); 492 px at (2,2,10), within 2 levels per
  channel - encoder noise of the same class as v3/v4.

Sync (measure_sync5.py -> sync_measurements5.json): at the continuous
event time, marble centroid vs node center = 0.0 px for all 7 chase
lightings, 25 splits, 25 absorbs, 17 sampled exclusive nodes, 5x3
sendback entry/apex/exit, 3 gate arrivals - identical to v4 (events
asserted equal: NODE_X, gate ranks, leg rank spans and durations,
sendback ranks). Nearest-30fps-frame residual <=26.1 px (v4: <=25.7)
- pure frame quantization at the shifted wall times. BPM-pulse
centroid drift during a gate hold: 0.0 px.
