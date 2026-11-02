# parcel-w6filmretime — film retime (dedupe, zoom quality, 3-minute cap)

Branch `wave6-filmretime` on base `101b4aa`; brief
`ledger/briefs/w6-filmretime.md`; full evidence in
`scratch/parcel-w6filmretime/report.md`.

- Item 1: why title scene deleted entirely (`scene_title`, `T_H`,
  `T_SUB`, both BLOCKS title rows, old SHIFT map). Why opens white then
  on the spec; idea's closing question is the single posing. Before/
  after scene lists and stills in the report.
- Item 2: phone-camera supersampling inside `intro_outro.py` only.
  Camera sources (intro dive plate, outro SS pull-back scenes) render
  on an SSx canvas via a scale context; `camera()` downscales to
  2560x1440. Probed SS 1/2/3 at dive crops 800/400 output px
  (effective upscale 3.19/1.60/1.06 at 800); **SS=2 chosen** (text
  edges smooth; gradient energy ~1.9x SS1; SS3 marginal at 498 vs
  221 MB tracemalloc peak). Period centroid re-derived at SS=2 through
  the file's own measurement path; proof error 0.2 px; clamps 0.0 /
  0.25 SS px; full-frame solid downscale exact (255,255,255)/(3,4,9)
  at every SS.
- Item 3: native total exactly **185.0 s** = intro 7 + idea 26 +
  why 32 + gitvisual 108 + outro 12 (179.03 s at 124 BPM), all added
  time as dwell (scene-end holds, popup dwell +0.5 x7, gate windows
  9/9/8.5 s with legs still 8/5/7 s, outro panels at 1.0 s spacing);
  no typing/marble/camera slowing, no uniform stretch. BLOCKS audits
  recomputed; independent RULE check: zero violations. Segment MP4s
  probed by ffmpeg header and frame count (210/780/960/3240/360).
- Gitvisual sync re-measured with the adapted v7 script: at-event
  0.000 px on every kind, gate ranks [44,69,140] with cursor on rank
  at each gate t0, cursor monotonic.
- `tools/run.sh standard` in the worktree: PASS.
- Assembly not produced (lead assembles at merge); `video/assemble.py`
  SEGMENTS durations updated. `render_why.py` owned but unchanged.
