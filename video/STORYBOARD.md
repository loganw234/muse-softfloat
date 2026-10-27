# Storyboard - AS BUILT (final cut, rendered 2026-10-27)

This is the as-built record of `out/final.mp4`: 180.0 s, 1920x1080,
30 fps, H.264, silent. Timeline data: `timeline.FINAL` (29 scenes,
exported as `final.timeline.json`). High energy: hard cuts on the
0.5 s beat grid of a 120 BPM bar (`style.BPM = 120`), kinetic type,
live-data charts, no scene longer than 14 s. Every on-screen number
names its source; the per-scene `source` string prints bottom-right
on the frame, and the trace table below pins each figure to the file
and entry it was read from (all re-verified 2026-10-27, before the
render). Live series (charts, ticker, plant dots, plant score) are
computed at render time by `video/data.py` from
`muse-softfloat/docs/metrics/*.jsonl` and `git log`; headline
constants carry `data.SOURCES`.

All repo paths are relative to `muse-softfloat/` unless stated.
"RECORD" = `docs/RECORD.md`.

| Time | Segment | Scenes |
|---|---|---|
| 0:00-0:08 | 1. Hook | kinetic x2 |
| 0:08-0:30 | 2. The problem | kinetic x4 |
| 0:30-0:55 | 3. The contract | counter, stat, kinetic x2 |
| 0:55-1:25 | 4. The method | kinetic, barchart, ticker, linechart, kinetic |
| 1:25-1:50 | 5. The catch | kinetic x4 |
| 1:50-2:15 | 6. The scale | counter, stat x2, kinetic |
| 2:15-2:32 | 7. The board proof | hash, stat, kinetic |
| 2:32-2:54 | 8. IAS15 climax | orbit (fig8), hashlock |
| 2:54-3:00 | 9. Close | kinetic |

## 1. Hook - 0:00-0:08

- 0:00-0:04 kinetic (cyan, zoom): "NO **FPU.** / NO **EXCUSES.**",
  sub "IEEE 754 softfloat for the RP2040". Source: README.md.
- 0:04-0:08 kinetic (amber, zoom): "THE WHOLE **STANDARD.** / ON A
  CHIP WITH **NONE.**", sub "built by Muse models - verified by
  Muse models - in public". Source: README.md (built with Meta's
  Muse models; public remote) + git commit trailers.

## 2. The problem - 0:08-0:30

- 0:08-0:14 kinetic (red): four strikes, one per ~1.2 s: "DENORMALS
  IN: **ZERO** / DENORMALS OUT: **ZERO** / NaNs: **INFINITIES** /
  EXCEPTION FLAGS: **NONE**". Source: RECORD Wave 0, survey S3
  summary (bootrom flushes output denormals to zero, treats input
  denormals as zero and NaNs as infinities, no exception flags).
  Wording not strengthened beyond S3.
- 0:14-0:20 kinetic: "FINE FOR AN **LED.** / FATAL FOR AN
  **INTEGRATOR.**" (rhetoric; the delta it points at is S3's).
- 0:20-0:26 kinetic: "AND THE SDK? / FMA: **UNFUSED.** / fmaf:
  **DOUBLE-ROUNDING.**", sub "recorded in its own source comments -
  survey S3". Source: RECORD Wave 0 (S3: SDK `fma` unfused, `fmaf`
  double-rounding, recorded in its own comments).
- 0:26-0:30 kinetic (cyan): "THAT'S THE **BOOTROM.** / OURS DOES THE
  **STANDARD.**"

## 3. The contract - 0:30-0:55

- 0:30-0:36 counter 0 -> **783**, label "OF 783. ALL OF THEM.", sub
  "every Clause 5 instantiation - binary16, binary32, binary64".
  Sources: RECORD Wave 3 ("783 of 783 instantiations implemented");
  `docs/COVERAGE.tsv`; README Status ("full Clause 5 surface").
- 0:36-0:44 stat cards: **3** FORMATS (binary16/32/64); **4**
  ROUNDING MODES (+ ties-to-away operations); **H=20** DECIMAL
  DIGITS (correctly rounded conversions). Sources: RECORD Wave 0
  (S1: four binary rounding attributes, ties-to-away operations
  required, decimal conversions correctly rounded to H >= 20);
  RECORD Wave 3 (project H=20).
- 0:44-0:50 kinetic: "754-2019 IS THE **CONTRACT.** / NOT THE
  **ORACLE.**" Source: README ground rules.
- 0:50-0:55 kinetic: "THE ORACLE IS **EXECUTABLE.**", sub "each row
  gated vs Berkeley TestFloat 3e, MPFR, or an exact reference".
  Source: README Status (same wording, including the "or").

## 4. The method - 0:55-1:25

- 0:55-1:00 kinetic: "PARCELS, / NOT **PROMPTS.**"
- 1:00-1:08 barchart, live: tool uses per agent from
  `docs/metrics/passes.jsonl`. At this render: verifier-w3str 273,
  verifier-w1f64 266, lead 231, parcel-f64 188, verifier-w2xf 185,
  ias15-port 168, parcel-str 165, ias15-pico 160 (top 8 of 37 rows).
- 1:08-1:14 ticker, live: three scrolling rows of real `git log`
  subjects (40 commits at render).
- 1:14-1:20 linechart, live: cumulative tool uses, final value
  **3,357** at this render.
- 1:20-1:25 kinetic: "EVERY PARCEL GETS A **VERIFIER.** / ITS ONLY
  JOB: **DISCONFIRM.**" Source: README ground rules ("a verifier
  that only disconfirms").

## 5. The catch - 1:25-1:50 (cuts slow ~20%)

- 1:25-1:32 kinetic (red): "OUR KERNEL WAS **WRONG.** / OUR
  REFERENCE **AGREED.**", sub "the lead's code, twice over - kernel
  and Python reference". Source: RECORD Wave 1, Slips.
- 1:32-1:38 kinetic: "EVERY SELF-CONSISTENT / GATE **PASSED.**"
  Source: RECORD Wave 1 ("every self-consistent gate passed").
- 1:38-1:44 kinetic (cyan): "**BERKELEY** DISAGREED.", sub "a parcel
  escalated against its own lead's code - and was upheld". Source:
  RECORD Wave 1 (parcel-f32 escalation upheld).
- 1:44-1:50 kinetic (green): "TININESS, CLAUSE **7.5.** / FIXED.
  **RE-GATED.** PUSHED.", sub "commit 53acb1a - Spark recheck:
  oracle differential 2400/2400". Source: RECORD Wave 1 (Clause 7.5
  tininess on the delivered value; fixes `53acb1a`/`b37fb12`; Spark
  rechecker-tininess READY). The same bullet's second find - the
  ingest `eq` mis-mapping with the 46,464-case proof - is in RECORD
  Wave 1 and in `data.SOURCES["tininess"]`; it did not fit this cut
  without rushing the centrepiece and is named here so the omission
  is a decision, not an accident.

## 6. The scale - 1:50-2:15 (fastest cutting)

- 1:50-1:55 counter 0 -> **85,148**, "VECTORS IN THE SMOKE GATE.",
  sub "the standard merge gate adds **1,117,504** more (Wave 1
  count)". Sources: RECORD Wave 3 (smoke 85,148 committed vectors);
  RECORD Wave 1 ("standard adds 1,117,504"). The same pair was
  re-printed at Wave 3 close (`ledger/lead.md` 2026-10-27 10:32:
  "smoke 85,148 + 1,117,504 standard, 9/9 controls"), so the
  on-screen "(Wave 1 count)" parenthetical is conservative.
- 1:55-2:02 stat cards: **37M+** BERKELEY CASES ("combined post-fix
  - 'exceeds'"; RECORD Wave 1: "exceeds 37M cases" - never an exact
  figure); **6.1M x5** F16 FMA, BERKELEY L1 (RECORD Wave 2: "f16 fma
  6.1M x 5 modes"; per-mode reading per RECORD P0 pricing: mulAdd
  level 1 = 6,133,248 per rounding slice); **65,536** BINARY16
  ENCODINGS (RECORD Wave 2: exhaustive 65,536-encoding unary
  sweeps).
- 2:02-2:10 stat cards + plant dots: **24/25** PLANTS CAUGHT; **3**
  WAVES PLANTED ("9/10, then 10/10, then 5/5"); **1** MISS ("kept,
  named, learned from"). Dots drawn grouped by verifier in
  `plants.jsonl` file order - W1 f32 (miss = plant 5, red), W1 f64,
  W2 f16, W2 xf, W3 str - counted live at render (24 caught of 25).
  Sources: `docs/metrics/plants.jsonl`; RECORD Waves 1-3 (9 of 10,
  10 of 10, 5 of 5; the miss = weakened generator boundary filed
  benign, detection without the byte-identity norm).
- 2:10-2:15 kinetic: "NOT READY IS A **VERDICT** / WE **SHIP.**",
  sub "**9** named negative controls - all refused, every smoke
  run". Sources: `tools/run.sh` `controls()` (9 named controls,
  "negative controls: all refused"); RECORD Wave 1 ("9/9 negative
  controls refused").

## 7. The board proof - 2:15-2:32

- 2:15-2:23 hash reveal: SHA-256
  `729f495d3e92bcd82931bd42b237705ad5333fe3ffeba4f5e3b39b0b2583f2b9`
  types out; stamp "HOST == RP2040 - BYTE-IDENTICAL"; sub
  "**2,489**-vector f16/xf sample - a sample, said plainly; not
  full-volume replay"; kicker carries board ID `e66440a2cb6f5c2b`.
  Sources: RECORD Wave 2 (2,489 sampled vectors, this hash, host ==
  board); RECORD Wave 3 (same sample re-replayed on the final tree,
  hash identical). "Sample" stays on screen - RECORD is explicit
  that board evidence is sampled, not full-volume.
- 2:23-2:29 stat cards: **2,767** WAVE 1 SAMPLE (binary32/64,
  hash-identical - RECORD Wave 1); **2,489** WAVE 2 SAMPLE (f16/xf,
  re-run on final tree); **47,107** AEABI CHECKS (RECORD Wave 3:
  AEABI selftest on the RP2040). Kicker carries the scope note:
  "string rows host-gated (RECORD Wave 3)" - the CDC harness
  protocol is numeric-only today.
- 2:29-2:32 kinetic: "THEN THE **REAL** / **WORKLOAD.**"

## 8. IAS15 climax - 2:32-2:54 (the only segment allowed to breathe)

- 2:32-2:46 orbit (`fig8`): three equal masses chase each other
  around the figure-8; lines "REBOUND'S IAS15 / UNMODIFIED SOURCE /
  SAME BITS OUT"; sub "period: **944** board steps - time-lapsed
  here". **The orbit frames are an illustration, labelled on every
  frame** ("ILLUSTRATION: same figure-8 ICs, Python float64 - proof
  = hash-lock, next"): no position dump exists (the run recorded
  IAS15FH1 hash records only, and positions cannot be decoded from
  hashes), so `scenes.simulate_fig8` integrates the exact initial
  conditions of the proven run - binary64 bit patterns from
  `scratch/ias15/work/ic_fig8.txt` (Chenciner-Montgomery, G=1, N=3)
  - in Python float64 (Yoshida-4, dt=0.002; period-closure error
  ~1e-4 measured), over the run's own span t = 12.651827085113784
  (`compare.log` t_final). The illustration claims nothing; the
  next scene carries the claim. Sources for the claim text: README
  ("REBOUND's IAS15 ... bit-identical to the unmodified desktop
  run"); `ledger/lead.md` 2026-10-27 09:44 (full period t=6.33 =
  944 steps); RECORD Wave 3 ("the video treats as time-lapse with
  hash-lock beats, never a real-time claim").
- 2:46-2:54 hashlock: IAS15FH1 `H_state` digests type out at steps
  **0, 944, 2,000** (full 64-hex values, loaded from
  `scratch/ias15/out/hashes_native.txt`), each stamped
  "desktop == RP2040"; final stamp "**2,001 / 2,001** RECORDS -
  BIT-IDENTICAL ON SILICON"; sub "measured: **1.58 steps/s at
  125 MHz** (1,000-step block) - one period = **944** steps,
  ~10 min". Sources: RECORD Wave 3 (`matched=2001
  first_divergence=None`; step rate 1.58 at 125 MHz; step-2000
  `H_state 4d4530a6...f48abb`); `ledger/lead.md` 09:44 (elapsed_us
  631495596 per 1,000-step block; step 0 `62bb23b0...333e01`).
  At render time `data.ias15_digests()` re-compared all 2,001
  records against the board capture
  `worktrees/w-ias15/build/ias15-board/hashes_board.txt` and
  asserted 2,001/2,001 equal before any frame was drawn.

## 9. Close - 2:54-3:00

- Kinetic (amber, zoom): "IEEE 754, / **HONESTLY.**", sub
  "github.com/loganw234/muse-softfloat - MIT - Meta AI Developer
  Hackathon 2026". Sources: the repo's `origin` remote (verified
  with `git remote -v` at render); `LICENSE` (MIT, (c) 2026
  Logan W.); README (hackathon, 2026-10-26 to 2026-11-04). No
  REBOUND (GPL) assets or visuals anywhere in the film - the
  orbit is our own integration of published initial conditions.

## Production notes

1. **Silent as rendered.** Music options (licence-checked, nothing
   downloaded) are in `MUSIC.md`, with a cue sheet keyed to these
   segment times. All cuts sit on the 120 BPM / 0.5 s grid
   (`style.BPM`); a non-120 track means re-deriving `style.BEAT`
   and re-rendering, or choosing a 120 BPM track. Captions carry
   every line - VO is optional, never required.
2. **Stills package:** `out/stills/` - frames grabbed from the
   rendered MP4 (not from the scene renderer) at the named times in
   the final report, each visually inspected.
3. **Re-render:** `..\.venv\Scripts\python.exe render.py --which
   final --out out\final.mp4` from `video/` (or `--timeline
   final.timeline.json`). Live data (metrics, git log, IAS15 hash
   files) is re-read then; if the metrics grow, segment 4/6 figures
   on screen change with them - by design.
4. **Render wall time:** 327.7 s (render.py DONE line, scratch/video/render-final.log) (5,400 frames on a
   loaded machine; a fact about this run, not a rate).
