# study-video-why — ledger

Task: draft 10–20 s "why a custom softfloat" segment, scratch only.
Brief: ledger/briefs/study-video-why.md (read first, obeyed).

Delivered in scratch/study-video-why/:
- why-1440p.mp4 — 16.0 s, 2560x1440, 30 fps, 480/480 decoded,
  H.264 silent, 2,220,829 B; probe-verified via video/probe.py.
- why-1080p.mp4 — downscale twin, probe-verified.
- stills/ — beat stills from the MP4, eyeballed (title, workloads,
  job spec, options 1–3, lineup pre/post-zoom, settle, bookends).
- options-facts.md — per-claim SF-0/SF-1/SF-2/RECORD pointers +
  dropped claims. Key honesty call: SF-0 measured no libgcc
  semantics, so Option 2 is a "not measured" beat, not invented lacks.
- render_why.py (+ check_bookends.py, check_tail.py) — MSF_PYTHON
  pinned to workspace .venv; frames stream to ffmpeg.
- report.md — READY; beat sheet; placement recommendation.

Designed for SLOT B (after messenger intro, on the white plane):
opens and closes on exact (255,255,255), measured 0 non-white px
at both ends of the MP4, so it hard-cuts between intro and
gitvisual; slot-A safe. Zoom is parametric (draw-time scale
1.00→1.22), no crop-upscale. No performance framing. Repo
(muse-softfloat/) untouched; nothing committed. No third-party
softfloat source consulted.
