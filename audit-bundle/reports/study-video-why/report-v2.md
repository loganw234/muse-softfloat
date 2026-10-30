READY

Segment B (rework) "why a custom softfloat", stretched 16.0 s ->
32.0 s at 2560x1440, 30 fps, 120 BPM grid, purely for reading time.
Same SF-0-sourced claim pool and discipline as v1 (options-facts.md
unchanged and still the per-claim source table; not-measured stays
not-measured; no performance framing; every v1 dropped claim stays
dropped). v1 artifacts preserved untouched (why-1440p.mp4 still
2,220,829 bytes; report.md / render_why.py / stills/ as they were).
New files: render_why2.py, why2-1440p.mp4, why2-1080p.mp4,
stills2/, this report.

## Clip (probe-verified)

- why2-1440p.mp4: 32.0 s, 2560x1440, 30 fps, H.264, silent,
  960/960 frames decoded clean (video/probe.py via
  scratch/study-video-idea/verify_v2.py, decode_rc 0), 2,453,116
  bytes. Render: $MSF_PYTHON render_why2.py (workspace .venv
  python; one frame buffered at a time). why2-1080p.mp4 twin
  (1,465,385 bytes).
- Bookends measured: stills at 0.2 s and 31.8 s exactly
  (255,255,255) on all 3,686,400 px. Opens white (idea hand-off),
  ends with a 0.75 s exact-white hold (git hand-off).
- Zoom (lineup 26.5-28.0) parametric draw-time scale 1.00->1.22;
  no bitmap crop-upscale anywhere.

## Dwell rule (stated, then followed)

All scene cuts and holds are multiples of the 0.5 s beat. Reading
budget per text block: each new line/card is the only new text for
at least 1.0 s before anything else appears, remains on screen for
the rest of its scene, and each scene's completed state holds
>= 1.5 s before the cut. Longest single line is 9 words (option-1
rounding line); at a conservative ~3 words/second first-read that
needs ~3 s on screen, which accumulation provides (it lands at
16.0 s and stays to 19.0 s). Known sub-1.5 s completed-state holds,
named rather than hidden: job-spec last row completes 1.0 s before
its cut (the 7 short rows accumulate over 4.0 s); option-3 example
line 1.0 s (9 short words, third element of a 2.0 s scene); the
lineup is a 1.5 s symbol recap of rows already read in full.

## Beat sheet (120 BPM; all cuts on beats)

| t (s) | beats | content |
|---|---|---|
| 0.0-0.5 | 0-1 | pure-white hold (idea hand-off) |
| 0.5-2.5 | 1-5 | title WHY NOT USE WHAT ALREADY SHIPS? + subtitle |
| 2.5-8.5 | 5-17 | workload cards one at a time, 2.0 s apart: IAS15 / interval geometry / KissFFT Fork B (NEEDS lines) |
| 8.5-12.5 | 17-25 | job spec: 7 IEEE 754-2019 requirements, one per beat, then hold |
| 12.5-19.0 | 25-38 | OPTION 1 pico->bootrom: honest check, then 4 sourced lacks at 1.0 s intervals; e.g. line 17.5; stamp ELIMINATED 18.5 |
| 19.0-24.5 | 38-49 | OPTION 2 compiler->libgcc: ? rows + contraction lacks at 1.0 s intervals; e.g. line 23.0; stamp NOT MEASURED 24.0 |
| 24.5-26.5 | 49-53 | OPTION 3 none: panic stub; e.g. line; stamp NO FLOATS AT ALL 26.0 |
| 26.5-28.0 | 53-56 | lineup matrix vs spec, parametric zoom 1.00->1.22 |
| 28.0-31.0 | 56-62 | settle: MUSE-SOFTFLOAT card, lines 28.5/29.0/29.0/29.5, punchline dwells to 31.0 |
| 31.0-32.0 | 62-64 | fade to white; 0.75 s exact-white hold out |

## What changed vs v1 and why

1. Timing only, for reading: v1 popped cards 1.0 s apart and option
   rows 0.28 s apart inside 2.0 s scenes; v2 arrives one element at
   a time (cards 2.0 s, spec rows 0.5 s, option rows 1.0 s) with the
   completed-state holds above. Type grew slightly (option rows
   43->45, spec 44->46 at the 1080p scale) since less competes.
2. Sourced depth instead of padding: one concrete consequence line
   per doomed option, each a direct consequence of a statement
   already in options-facts.md, worded as "e.g.", NOT a new
   measurement:
   - bootrom: "a tiny subnormal result -> 0, silently" (datasheet
     flush rule via SF-0 8; options-facts option-1 subnormal row).
   - libgcc: "a*b+c may fuse on one target, not another - different
     bits" (SF-0 9 contraction is target-dependent; fused vs
     unfused roundings can differ - definitional).
   - none: "the first a+b in any workload never returns" (every
     entry point is the panic stub, S3 1.4 via SF-0 3.4).
3. The lineup CUSTOM column stays "?" into the settle card, as v1.
   The "* subject to those flush rules" footnote shortened to fit
   beside the stamp; meaning unchanged.
4. Nothing else: identical claim pool, identical dropped-claims
   list (options-facts.md items 1-6 still off screen), identical
   white bookends, same style idiom and palette.

## Exact durations vs the 180 s budget

idea 14.5 s + why2 32.0 s = 46.5 s, replacing the 16.0 s v1 why in
the 115 s assembly -> film now ~145.5 s, 34.5 s under the 180 s
target. 32.0 s is the top of the brief's honest 28-32 s band: with
sequential 1.0 s row reveals and >= 1.5 s completed holds, the
content does not honestly fit in less. If trims are asked for,
cheapest first: workload stagger 2.0->1.5 s (-1.5 s), lineup
(-0.5 s), settle hold (-0.5 s), spec hold (-0.5 s) -> ~29.0 s
without dropping a claim; dropping the three e.g. lines saves a
further ~1.5 s but loses the concrete wrong answers.

Stills eyeballed from the MP4 (stills2/): 002.2s title, 008.2s
workloads, 012.2s job spec, 018.7s option 1, 024.2s option 2,
026.3s option 3, 027.7s lineup, 030.8s settle, 000.2s/031.8s white.

## Known limits

- Silent; 120 BPM grid, no track auditioned against it.
- Sub-1.5 s holds named in the dwell section above.
- Copy still terse/technical; owner polish pass as for v1.
