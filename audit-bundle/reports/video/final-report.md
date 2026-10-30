# video-final report - READY

## Verdict

READY. `video/out/final.mp4` is rendered, fully decoded, and stills
from the encoded file are inspected (below). First actions were in
brief order: escalation test `ledger/urgent/video-final-test.md`,
then the plan entry (ledger/video-final.md, 2026-10-27 10:37:11
-0700), then build. Nothing with `cft` in its name was opened,
searched, or listed. All shell work ran from script files in
`scratch/video/`. `muse-softfloat/` untouched (`git status` clean
at close); edits confined to `video/` + my ledger/scratch files.

## Deliverable (Measured)

- `video/out/final.mp4`: **180.0 s** (brief 170-185), **1920x1080**,
  **30.0 fps**, **H.264 High / yuv420p**, faststart, **silent**
  (one video stream, no audio stream - `ffmpeg -i` read directly).
  17,014,776 bytes; SHA-256
  `12e29ebbbb3045438416a274d3eab25d4d2de6b741bcae9d3de7511d61e42688`.
- Verification: `video/probe.py` (bundled ffmpeg 7.1): duration
  180.0, codec h264, 1920x1080, 30 fps, **decoded_frames 5400 of
  5400 expected, decode_rc 0**. Corroborated by a second route:
  direct `ffmpeg -i` banner (`Duration: 00:03:00.00`, single
  Stream #0:0 Video h264 1920x1080 30 fps, 756 kb/s).
- Render wall time **327.7 s** for 5,400 frames (render.py DONE
  line, `scratch/video/render-final.log`) on a loaded machine -
  recorded, not a rate claim.
- Structure: 29 scenes / 9 segments, `timeline.FINAL` = data
  (validated contiguous, every cut on the 0.5 s / 120 BPM grid);
  exported copy `video/final.timeline.json` verified equal to
  `timeline.FINAL`. High energy per owner steer: word-pop kinetic
  type, live charts, fastest cutting in segment 6, segment 5 slowed.
- `video/STORYBOARD.md` rewritten as-built (timings + source per
  number + 120 BPM grid + re-render instructions).
- Stills package: **12 frames in `video/out/stills/`** grabbed from
  the rendered MP4 at 2.5 / 13.0 / 34.5 / 66.0 / 102.0 / 108.5 /
  120.0 / 128.0 / 141.5 / 160.0 / 172.5 / 178.0 s - **all 12 opened
  and inspected** after probing (plus 39 pre-render stills in
  `scratch/video/final-stills/` inspected before the render; two
  defects found there and fixed pre-render: orbit tag/footer
  collision, hash-lock stamp firing before its rows completed).
- `video/MUSIC.md`: 3 licence-checked options (incompetech CC BY
  4.0; Pixabay Content License, no attribution; ccMixter CC-BY-only)
  with cue sheet; FreePD checked and ruled out (site closed
  2008-2025, read live). **No audio downloaded.** Timeline stays on
  the documented 120 BPM grid for a drop-in bed.
- IAS15 orbit: no position dump exists under `scratch/ias15/out/`
  (IAS15FH1 hash records + 3 raw record dumps only), so the orbit
  integrates the run's exact ICs (`scratch/ias15/work/ic_fig8.txt`
  bit patterns) in Python float64 and is **labelled an illustration
  on every frame**; the following hash-lock scene carries the claim
  with full digests. I re-compared the hash files myself before
  building (`scratch/video/verify-ias15.py`): native 2001 = board
  2001 = soft 2001, **board==native 2001/2001**, and
  `data.ias15_digests()` asserts the same at render load.
- Code changes in `video/`: `data.py` (final SOURCES/HEADLINE,
  `ias15_digests()`, `fig8_ics()`, `plant_groups()`), `scenes.py`
  (`simulate_fig8`, `fig8` orbit mode, grouped plant dots, `hash`
  `type_dur`/`stamp`/`sub`, new `hashlock` kind), `timeline.py`
  (`FINAL`), `render.py` (`--which`), `STORYBOARD.md`, `README.md`,
  new `MUSIC.md` + `final.timeline.json` + `out/final.mp4` +
  `out/stills/`. Proof path regression-checked: 3 s proof smoke
  render rc 0 after the scene changes.

## Number-by-number trace (onscreen -> source)

RECORD line numbers are `muse-softfloat/docs/RECORD.md` as read
in full on 2026-10-27. Live values were read at this render.

| On screen (scene) | Value | Source |
|---|---|---|
| counter 0:30 | 783 of 783 instantiations; binary16/32/64 Clause 5 | RECORD:524-529 (Wave 3 "783 of 783"); README.md:18-24 Status; docs/COVERAGE.tsv |
| stat 0:36 | 3 formats | README.md:3,20-21 |
| stat 0:36 | 4 rounding modes + ties-to-away operations | RECORD:64-66 (S1) |
| stat 0:36 | H=20 decimal digits, correctly rounded | RECORD:66-68 (S1, H >= 20); RECORD:524-528 (project H=20) |
| kinetic 0:50 | gated vs Berkeley TestFloat 3e, MPFR, or exact reference | README.md:23-25 |
| kinetic 0:08-0:26 | bootrom: denormals in/out zero, NaNs as infinities, no flags; SDK fma unfused, fmaf double-rounding "in its own comments" | RECORD:81-88 (S3) |
| barchart 1:00 | tool uses: verifier-w3str 273, verifier-w1f64 266, lead 231, parcel-f64 188, verifier-w2xf 185, ias15-port 168, parcel-str 165, ias15-pico 160 | live sum of docs/metrics/passes.jsonl (37 rows) by `data.tool_uses_by_agent()`; independently seen in `data.py` stdout this pass |
| ticker 1:08 | real commit subjects (40 commits) | live `git log` of muse-softfloat at render |
| linechart 1:14 | 3,357 cumulative tool uses | live `data.cumulative_tool_uses()` over passes.jsonl; same 3,357 in `data.py` stdout |
| kinetic 1:25-1:50 | Clause 7.5 tininess: kernel + reference wrong together; Berkeley disagreed; parcel escalation upheld; fix 53acb1a; oracle differential 2400/2400 | RECORD:334-347, 403-405 (Wave 1 + Slips) |
| counter 1:50 | 85,148 smoke vectors | RECORD:541-544 (Wave 3) |
| counter sub 1:50 | 1,117,504 standard "(Wave 1 count)" | RECORD:366-368; figure re-printed at Wave 3 close in ledger/lead.md 2026-10-27 10:32 ("smoke 85,148 + 1,117,504 standard, 9/9 controls") - on-screen parenthetical is conservative |
| stat 1:55 | 37M+ Berkeley cases, "exceeds" | RECORD:346-347 ("exceeds 37M cases"; never exact, per data.SOURCES) |
| stat 1:55 | 6.1M x5 F16 FMA Berkeley L1, "in each of 5 modes" | RECORD:454-455 ("f16 fma 6.1M x 5 modes"); per-mode per RECORD:273-275 (mulAdd level 1 = 6,133,248 per rounding slice) |
| stat 1:55 | 65,536 binary16 encodings, exhaustive unary sweeps | RECORD:431-434 |
| stat+dots 2:02 | 24/25 plants; waves 9/10, 10/10, 5/5; 1 miss; dots grouped W1 f32 (miss #5 red), W1 f64, W2 f16, W2 xf, W3 str | live docs/metrics/plants.jsonl (25 rows, read in full this pass); RECORD:354, 449-450, 536-537 |
| kinetic 2:10 | 9 negative controls, all refused every smoke run | tools/run.sh `controls()` (9 named, "# 9. full-surface inventory", "negative controls: all refused" - lines read this pass); RECORD:367 ("9/9"); re-stated ledger/lead.md 10:32 |
| hash 2:15 | SHA-256 729f495d...f2b9; 2,489 f16/xf sample; board e66440a2cb6f5c2b; "not full-volume replay" | RECORD:459-462 (hash, 2,489); RECORD:547-550 (re-replayed on final tree); RECORD:418-419 (sample scope); board ID RECORD:370 |
| stat 2:23 | 2,767 Wave 1 sample; 47,107 AEABI checks; "string rows host-gated" | RECORD:369-374; RECORD:557; RECORD:549-550 |
| orbit 2:32 | figure-8 ICs; period 944 board steps; time-lapse label; ILLUSTRATION tag | ICs: scratch/ias15/work/ic_fig8.txt (bits decoded + integrated, closure err ~1e-4, `scratch/video/probe-fig8.py`); 944 steps: ledger/lead.md:297 (09:44 entry); time-lapse: RECORD:561-564 |
| hashlock 2:46 | H_state step 0 `62bb23b0...333e01`, step 944 `44295e2f...712b7b6`, step 2000 `4d4530a6...f48abb` (full 64-hex on screen); 2,001/2,001 bit-identical; 1.58 steps/s at 125 MHz (1,000-step block); period 944 steps ~10 min | full digests loaded from scratch/ias15/out/hashes_native.txt and re-compared == worktrees/w-ias15/build/ias15-board/hashes_board.txt (2001/2001, my probe + render-time assert); prefixes RECORD:558-560 + ledger/lead.md:297; matched=2001 worktrees/w-ias15/build/ias15-board/compare.log:1; rate ledger/lead.md:297 (elapsed_us=631495596) + RECORD:561-562 |
| close 2:54 | github.com/loganw234/muse-softfloat; MIT; Meta AI Developer Hackathon 2026 | `git remote -v` this pass (origin https://github.com/loganw234/muse-softfloat.git); muse-softfloat/LICENSE; README.md:7-8 |

Not put on screen (deliberate, documentation only): the ingest `eq`
mis-mapping's 46,464-case proof (RECORD:340-341) - named in
STORYBOARD segment 5 and `data.SOURCES["tininess"]`; the Wave 3
string-row MPFR triangulation (1,146/1,146 + 1,084/1,084,
RECORD:539-540); host-side IAS15 20,001-record run (RECORD:464-468).
The cut names the numbers it has room to land honestly.

## What this brief got wrong

Nothing load-bearing - every "confirmed fact" verified at source.
Notes: (1) The brief hedged that `build/ias15-board/hashes_board.txt`
in the worktree "may be gone"; it is present (2,003 lines) and was
the board side of the render-time comparison. (2) The brief's
"85,148 + 1,117,504" understates its own currency: the pair is not
only Wave-1-counted, it was re-printed at Wave 3 close
(ledger/lead.md 10:32); the film keeps the conservative
"(Wave 1 count)" label anyway. (3) The old STORYBOARD segment-6/7/8
figures (52,168; 409/783; storyboard-only IAS15) were superseded
exactly as its own picture-lock notes predicted; the file is now
the as-built record.

## Gaps / for the lead

1. **Silent by design.** Music bed + any VO remain owner decisions;
   `video/MUSIC.md` has 3 licence-checked options and the cue
   sheet. Dropping a 120 BPM track under the current cut needs no
   re-render; another tempo means re-deriving `style.BEAT`.
2. **Orbit is an illustration** (labelled on-frame, every frame of
   the scene). No position dump exists to do better with; if a
   future board/host run dumps (x,y) samples, `sc_orbit` can take
   them via `ctx` without scene changes.
3. No board photo/footage exists in-repo; segment 7 is hash-only,
   as storyboarded.
4. Checkpoint: closed the same morning, ~35 min after the 10:37
   plan entry - far inside the 300-minute box; no 240-minute
   checkpoint was reached.
