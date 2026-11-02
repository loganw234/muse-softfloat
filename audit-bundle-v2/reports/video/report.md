# video-tools report — READY

## Verdict

READY. The tooling renders and the proof clip is verified end-to-end.
Nothing was installed; `muse-softfloat/` and the kit were read-only
(`git -C muse-softfloat status` clean at close). Nothing with `cft` in
its name was opened, searched, or listed.

## (1) Inventory — what renders video here (Measured: `video/inventory.py`)

- **No `ffmpeg`/`ffprobe` on PATH** (`shutil.which` → None for both).
- **Bundled ffmpeg works:** imageio-ffmpeg 0.6.0 in the workspace `.venv`
  ships `ffmpeg-win-x86_64-v7.1.exe` (ffmpeg 7.1 essentials build,
  `--enable-libx264`, AAC present). No ffprobe anywhere, so `probe.py`
  verifies via `ffmpeg -i` + full decode instead.
- Python 3.12.15 (`.venv\Scripts\python.exe`), Pillow 13.0.0, numpy 2.5.4,
  imageio 2.38.1, matplotlib 3.11.2 (unused; Pillow draws everything).
- Fonts: Windows system Arial Bold / Segoe UI / Consolas — adequate.
- **Missing (named, not installed):** nothing essential for this pass.
  For the final: (a) a music track with a submittable licence + a VO
  decision (proof is silent by design); (b) optionally a display font.
  Both are lead/owner choices, flagged in `video/STORYBOARD.md`.

## (2) Pipeline — `video/` (new top-level dir, outside `muse-softfloat/`)

- `style.py` — palette, type scale, fonts, 120 BPM / 0.5 s beat grid,
  easings (cubic-out entrances, back-ease word pop), 1920×1080 @ 30 fps.
- `data.py` — read-only real data: `passes.jsonl` (27 rows; tool-uses per
  agent, cumulative series = 1,922), `usage.jsonl` (token series),
  `plants.jsonl` (counted live: 9 caught / 10), `git log` subjects.
  Headline constants (52,168; 37M+; 2,767; board hash; 409/783) carry a
  `SOURCES` map to `docs/RECORD.md` / `README.md` wording.
- `scenes.py` — 8 primitives behind one registry: kinetic per-word pop-in,
  animated counter, bar chart, line chart, 3-row git ticker, 2D Newtonian
  n-body orbit trails (leapfrog, fading glow trails, labelled
  PLACEHOLDER on-frame), stat cards + plant dots in file order, typing
  hash reveal. Shared furniture: panning dot grid, cut flash, progress
  bar, per-scene `source` caption, subtle zoom on kinetic/orbit scenes.
- `timeline.py` + `proof.timeline.json` — timeline **is data**
  (`{kind, t0, t1, params}`); validated contiguous and on-beat; the JSON
  path was smoke-rendered (3.0 s, 90/90 frames) to prove re-cutting needs
  no code.
- `render.py` — frames → rawvideo stdin pipe → libx264 MP4
  (`yuv420p`, faststart); `--still`, `--max-seconds`, `--fps/--crf/--preset`.
- `probe.py`, `inventory.py` — verification and stack report.
- `README.md` (how to render, schema, knobs, limits), `STORYBOARD.md`.

## (3) Proof — `video/out/proof.mp4` (Measured)

9 scenes, 26.5 s: hook → 0→52,168 counter → agent bar chart → cumulative
line chart → git ticker → orbit placeholder → 9/10 · 37M+ · 409 stat
cards → board-hash reveal → close. Render wall time **47.2 s** for 795
frames on a loaded machine — a fact about that run, not a rate claim.

Verified by `probe.py` (ffmpeg 7.1): duration 26.5 s, codec h264,
1920×1080, 30.0 fps, **795/795 frames decoded, rc 0**, 3,722,368 bytes.
Six stills (`scratch/video/stills/still_*.png`, at 1.5/5.0/10.4/17.5/
22.0/25.8 s) extracted from the MP4 and inspected: kinetic type, counter,
line fill, orbit trails with fade, stat cards (miss dot correctly on
plant #5 in file order), close — all legible, no overlaps standing.

Bugs caught by still inspection before the full render, all fixed:
PIL RGBA alpha-replace flattening (trail fades/chart fills resurrected at
full strength — fixed by compositing over the stage colour); orbit inner
bodies stepping ~64°/frame (spirograph jaggies — retimed to ~12°/frame);
plant dots implying the wrong plant missed (now plants.jsonl order/grade);
an untraceable "$4 chip" line replaced with "ON AN RP2040".

## (4) STORYBOARD.md — 3-minute beat sheet

Nine timed segments summing to 3:00 (hook, problem/bootrom, contract,
method, the tininess catch as the drama beat, scale numbers, board proof,
IAS15 climax with byte-identical hash reveal, close). Every segment names
its scene kinds, draft VO/caption copy, and the exact repo source for
every number, plus picture-lock rules: re-derive figures, say "exceeds
37M" (no exact count is recorded), keep "2,767-**sample**" wording, and
gate the IAS15 segment on what the actual board run has recorded.

## Gaps / for the lead

1. **Silent proof.** Music + VO/captions decision needed; storyboard is
   written captions-first so any choice works. Beat grid is one constant
   (`style.BPM`) if a track dictates tempo instead.
2. **Orbit is simulated** (labelled on-frame). Swap in recorded IAS15
   (x, y) samples as `ctx["orbit"]` when the run exists.
3. No board photo/footage exists in-repo; segment 7 wants some if shot.
4. Numbers will move (Wave 2/3): the pipeline re-reads the jsonl and git
   log at render time; only `data.HEADLINE` constants need a manual
   re-check against the latest RECORD entry at picture-lock.
