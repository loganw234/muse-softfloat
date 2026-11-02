# Timing / beat sheet - gitvisual.mp4 (78.0 s, 1920x1080, 30 fps, silent)

All cuts on the 0.5 s / 120 BPM beat grid (video/style.py). Times are
segment-local seconds in `gitvisual.mp4`. Stills are frames grabbed from
the MP4 by `video/probe.py` into `stills/`.

| Time | Beat | What happens | Still |
|---|---|---|---|
| 0.0-1.0 | white hold | Full-frame pure white (255,255,255) - the intro handoff frame, held exactly. | still_000.5s.png |
| 1.0-27.0 | 1 - THE CHASE (slow) | Camera pans a flat white plane following the lead/main neon trail. Seven branches split off in system colours; each reaches a grey (disabled) node, lights it in the trail colour, and holds a descriptive popup ~2.3 s. Legend panel is on screen throughout. | still_003.5s.png (PARCEL), still_013.5s.png (PLANTS GRADED), still_023.5s.png (LEAD MERGE) |
| 2.2-4.4 | popup 1 PARCEL | parcel-f32, 173 binary32 rows, owns src/msf32.c only. | |
| 5.6-7.8 | popup 2 ESCALATION | parcel-f32 tininess escalation, Berkeley disagreed, lead fixes 53acb1a/b37fb12. | |
| 9.0-11.2 | popup 3 VERIFIER - SENDBACK | verifier-w5twiddledoc NOT READY: printed SHA-256 is 56 hex chars (truncated). | |
| 12.4-14.6 | popup 4 PLANTS GRADED | Wave 1: 9 of 10 caught; the miss named. | |
| 15.8-18.0 | popup 5 GATES | smoke 52,168; standard +1,117,504; 9/9 controls; board 2,767 host==RP2040. | |
| 19.2-21.4 | popup 6 STUDY | feasibility first, in scratch; two study visuals wait as gates. | |
| 22.6-24.8 | popup 7 LEAD MERGE | 2843792 - Wave 1 binary32 (READY 26c76aa); branch rejoins the main line. | |
| 27.0-29.0 | pull-back | The whole chase strip shrinks into view; the white plane dims to the dark stage. "NOW PULL BACK - the real history, replayed merge by merge. 141 commits - 27 merges - 2026-10-26 to 2026-10-29." | still_028.8s.png |
| 29.0-41.0 | 2 - replay A | Real topology replay, committer-date order, ranks 0 -> 68 (Wave 0 scaffold, P0 seam, Wave 1 f32/f64 + red lead-fix re-gates, Wave 2 f16/xf, IAS15, Wave 3 strings, wave4 seam/minmax/interval/trig). Cursor stops at GATE 1 (the KissFFT merge 32bbd93, rank 69). | still_035.0s.png |
| 41.0-49.0 | GATE 1 - KISSFFT STUDY | Main line blocked by a solid red gate. Left: study idiom - LCG waveform draws, twiddle unit circle lights, spectrum bars build bin by bin (labelled illustration, numpy, NOT KissFFT output), stamp "12/12 CONFIGURATIONS - HASHES RECORDED". Right: six Pico mockups blinking green while working (1 genuine Pico GP25 square LED + 5 RP2040-Zero WS2812). At 47.6 the gate turns green, lifts, neon passes. | still_046.0s.png (working), still_048.0s.png (PASS) |
| 49.0-57.0 | replay B | Ranks 69 -> 133: KissFFT merge lands, README/SF-2 plan, SF-2 Steps 1-4 (attr, alg1/alg2, site, demo, twiddledoc, exp2 plateau, log2, aug). Stops at GATE 2 (metrics merge a1a888f, rank 134). | still_053.0s.png |
| 57.0-65.0 | GATE 2 - TOKENS STUDY | Left: study idiom - project bar counts to 1,514,499,184 billed tokens; owner ~1,928 is a to-scale amber tick; x500,000 zoom panel; "~1 : 785,000 - human share 0.00013% - 8,951 model responses" (frozen 2026-10-28, definitions on frame). Right: six Picos blinking. Gate green at 63.6. | still_062.0s.png, still_064.0s.png (PASS) |
| 65.0-70.0 | replay C | Ranks 134 -> 140: Wave 5 close merges (metrics, readme3) to HEAD a73e97d. Final readout commits 141/141, merges 25/25 into main. | still_069.5s.png |
| 70.0-78.0 | 3 - BOXED | Neon trail travels into a simple open box (70-73); lid swings shut (73.2-74.6); neon dims to dark (74.6-76); fade to flat near-black and hold (76-78) for the outro cut. | still_072.0s.png (lid open), still_074.5s.png (lid shut), still_077.5s.png (near-black) |

Handoff measurements (from the rendered MP4, `video/probe.py` stills):
- t=0.5 s: all 2,073,600 px exactly (255,255,255) - matches intro final frame spec.
- t=77.5 s: all 2,073,600 px (2,3,8) after H.264 round-trip - matches the
  outro first-frame measurement in scratch/study-video-intro/report.md.
