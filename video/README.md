# video/ — programmatic demo-video tooling

Frame-render pipeline for the Muse-Softfloat hackathon film: Python draws
frames, pipes them raw to ffmpeg, gets an H.264 MP4. Two cuts exist:
`out/final.mp4` (180.0 s, 1920x1080, silent — the original 3-minute cut,
documented as-built in [STORYBOARD.md](STORYBOARD.md) with a source per
on-screen number) and `out/assembly_v5.mp4` (169.0 s, 2560x1440, silent —
the current segment-based cut, assembled by `assemble.py` from the
renderers in `segments/`; storyboarded in STORYBOARD.md's v5 section).
The 26.5 s proof (`out/proof.mp4`) remains as the machinery proof. Music
options (owner decision, nothing downloaded): [MUSIC.md](MUSIC.md).

Zero new installs. The stack is whatever this machine already has — run
`inventory.py` to see it; at first render: workspace `.venv` Python 3.12.15,
Pillow 13.0.0, numpy 2.5.4, and the ffmpeg 7.1 binary bundled with
imageio-ffmpeg 0.6.0 (no ffmpeg/ffprobe on PATH; fonts are the Windows
system Arial/Segoe/Consolas).

## Layout

| File | What it owns |
|---|---|
| `style.py` | Palette, type scale, fonts, beat grid (120 BPM / 0.5 s), easing. The only style file. |
| `data.py` | Read-only loaders for real project data: `muse-softfloat/docs/metrics/{passes,usage,plants}.jsonl`, `git log`, IAS15 hash files, plus headline constants traced to `docs/RECORD.md` / `tools/run.sh` (`SOURCES` says where each was read; the board-vs-desktop hash comparison is asserted at load). |
| `scenes.py` | Scene primitives + registry: `kinetic, counter, barchart, linechart, ticker, orbit, stat, hash, hashlock`. Each draws one frame given a scene dict and absolute time. |
| `timeline.py` | Timelines **as data** (`PROOF`, `FINAL` = the 180 s cut) + validation (contiguous, cuts on the beat grid). |
| `proof.timeline.json` / `final.timeline.json` | JSON exports of the timelines; edit these to re-cut without touching Python. |
| `render.py` | CLI: frames to ffmpeg pipe to MP4; `--which proof\|final`; also single-still mode and timeline export. |
| `probe.py` | ffprobe substitute (there is none bundled): duration/codec/size via `ffmpeg -i`, exact frame count via full decode, still grabs. |
| `inventory.py` | Prints exact versions/paths of the render stack found on this machine. |
| `STORYBOARD.md` | The as-built 3-minute record; every number names its repo source. |
| `MUSIC.md` | Licence-checked music options + cue sheet (final is silent by brief). |
| `segments/` | The v5 segment renderers + data: `intro_outro.py`, `idea.py`, `why.py` (+ `render_why.py` base), `gitvisual.py` (+ `history.json`, `gate2_numbers.json`, spectrum/twiddle JSONs). Production copies of the study scripts in `scratch/study-video-*` (paths repointed HERE-local); each writes its MP4 beside itself. |
| `assemble.py` | Renders any missing segment, concatenates intro → idea → why → git → outro at 2560x1440 into `out/assembly_v5.mp4`, pixel-checks the joins. `--force` re-renders. |
| `out/proof.mp4` | The rendered proof (26.5 s, 1920x1080, H.264, silent). |
| `out/final.mp4` | The original final cut (180.0 s, 1920x1080, H.264, silent) + `out/stills/` (12 MP4 grabs). |
| `out/assembly_v5.mp4` | The current segment-based cut (169.0 s, 2560x1440, H.264, silent). |

## Render

From the workspace root, with the project venv (PowerShell):

```powershell
.\.venv\Scripts\python.exe muse-softfloat\video\inventory.py          # what renders here
.\.venv\Scripts\python.exe muse-softfloat\video\data.py               # real numbers the charts will show
.\.venv\Scripts\python.exe muse-softfloat\video\timeline.py           # validate both timelines
.\.venv\Scripts\python.exe muse-softfloat\video\render.py             # -> muse-softfloat\video\out\proof.mp4
.\.venv\Scripts\python.exe muse-softfloat\video\render.py --which final --out muse-softfloat\video\out\final.mp4
.\.venv\Scripts\python.exe muse-softfloat\video\assemble.py           # -> muse-softfloat\video\out\assembly_v5.mp4 (segments + joins)
.\.venv\Scripts\python.exe muse-softfloat\video\probe.py muse-softfloat\video\out\final.mp4 --stills muse-softfloat\video\out\stills --at 2.5 13.0 34.5 66.0 102.0 108.5 120.0 128.0 141.5 160.0 172.5 178.0
```

The final render reads live data (metrics jsonl, git log, IAS15 hash
files incl. the board capture under `worktrees/w-ias15/` when present)
and asserts the 2,001-record hash identity before drawing a frame.

Re-cut without code: copy `proof.timeline.json`, edit times/text/params,
then `render.py --timeline your.json --out out\your.mp4`. The same JSON
schema is what `timeline.py` validates: scenes contiguous, cuts on
multiples of `style.BEAT`.

Useful flags: `--still 7.2 --out frame.png` (one frame, fast iteration),
`--max-seconds 3` (smoke render), `--fps/--crf/--preset` (encode knobs),
`--export-timeline f.json`.

## Scene schema (per kind, beyond `kind/t0/t1/accent/kicker/source`)

- `kinetic`: `lines:[{text, at, size?, color?}]` — `*word*` renders in the
  accent; words pop in `word_gap` s apart; optional `sub/sub_at`, `zoom`.
- `counter`: `target, count_dur, label, sub?, size?` — eased 0→target.
- `barchart`: `title, series` (a `data.py` series key: `tool_uses_by_agent`
  or `output_tokens_by_agent`), `sub?`.
- `linechart`: `title, sub?` — cumulative tool uses from `passes.jsonl`.
- `ticker`: `title` — three scrolling rows of live `git log` subjects.
- `orbit`: `lines_rgb:[[text, size, [r,g,b]], ...], sub?, tag?, scale?,
  trail?` - n-body trails. Default is the proof's simulated placeholder
  (`scenes.simulate_orbits`). With `fig8: true` it integrates the real
  IAS15 figure-8 ICs (`data.fig8_ics`, float64 Yoshida-4) - an
  illustration, labelled by `tag` on every frame; hashes carry the claim.
- `stat`: `stats:[{value, label, sub?}], plant_dots?` - dots are drawn
  grouped by verifier in `plants.jsonl` order, green caught / red missed.
- `hash`: `title, hash?, type_dur?, stamp?, sub?` (hash defaults to the
  RECORD Wave 1 board hash in `data.HEADLINE`).
- `hashlock`: `title, steps?, stamp?, sub?` - IAS15FH1 digests at named
  steps type out with a desktop == RP2040 line each; digests come from
  `data.ias15_digests()` (re-compared at load).

Every scene gets the shared furniture automatically: panning dot-grid +
accent slash background, kicker top-left, a 2-frame accent flash on the
cut, a progress bar, and the `source` line bottom-right (the film's
traceability device — keep it filled in).

## Style knobs

All in `style.py`: `W/H/FPS`, palette (`BG, INK, CYAN, AMBER, ...`,
`ACCENTS` cycle for charts), type scale (`T_MEGA … T_TICKER`), font files,
`BPM`/`BEAT`, easings (`ease_out_cubic` is the house entrance;
`ease_out_back` for word pop). Nothing scene-local hard-codes a colour or
size that matters — change `style.py`, re-render, everything follows.

## Verify (what was run)

Proof: `probe.py` on `out/proof.mp4`: 26.5 s, h264, 1920x1080, 30 fps,
795/795 frames decoded clean; six stills eyeballed; first render 47.2 s
wall on a loaded machine - a fact about that run, not a rate.

Final (2026-10-27): `probe.py` on `out/final.mp4`: 180.0 s, h264,
1920x1080, 30.0 fps, **5,400/5,400 frames decoded, rc 0**, 17,014,776
bytes, one video stream and no audio stream (silent by design). Twelve
stills grabbed from the MP4 into `out/stills/` and visually inspected,
plus 39 pre-render scene stills in `scratch/video/final-stills/`.
Render wall 327.7 s on a loaded machine - not a rate claim. Full
number-by-number trace: `scratch/video/final-report.md`.

## Known limits

- **Silent.** Music/VO is an owner decision (see `MUSIC.md` for
  licence-checked options and the cue sheet). ffmpeg has AAC; muxing
  is a small step once a track exists. Cuts sit on the 120 BPM grid.
- **Final-cut orbit is an illustration**, labelled on-frame: the IAS15
  run recorded hashes only, so figure-8 frames integrate the run's
  exact ICs in float64. The hash-lock scene after it carries the
  board claim. (The proof's orbit remains a labelled placeholder sim.)
- Text is Arial/Segoe/Consolas (what's installed). A display font would
  lift the kinetic scenes; that's an install decision for the lead, not
  needed for correctness.
- Frames render single-threaded on CPU; the 180 s final (5,400 frames)
  took 327.7 s wall under load. Parallel frame sharding is possible
  but unnecessary until it hurts.
