READY

Rough-draft 16.0 s "why a custom softfloat" segment at 2560x1440,
30 fps, 120 BPM grid. Programmatic only (PIL + bundled ffmpeg via
imageio-ffmpeg, video/style.py fonts/eases; deep-ink variants on the
white plane). No performance framing anywhere; every option claim is
sourced in options-facts.md. Owner/lead edit still needed on copy
polish, VO/music sync, and final placement.

## Designed-for slot

SLOT B — right after the messenger intro, on the white plane.
The intro ends on a pure-white hold (scratch/study-video-intro/report.md)
and the gitvisual segment begins from that same white frame, so this
segment opens AND closes on exact (255,255,255): drop it between them
with hard cuts, no transition needed. It remains slot-A safe (before
the intro) since white bookends cut cleanly anywhere, but B is the
designed intent: the phone's "idea" lands, then this justifies it,
then the gitvisual shows it happening.

Placement recommendation: slot B. In slot A the segment must carry
the cold open alone and its title question ("why not use what already
ships?") presumes a project the viewer has not met yet; after the
intro the question has a referent.

## Clip (probe-verified)

- why-1440p.mp4: 16.0 s, 2560x1440, 30 fps, H.264, silent,
  480/480 frames decoded clean (video/probe.py, decode_rc 0),
  2,220,829 bytes. Render: $MSF_PYTHON render_why.py
  (MSF_PYTHON = workspace .venv python; frames stream to ffmpeg,
  one frame buffered at a time).
- why-1080p.mp4: downscale twin, 1920x1080, probe-verified same run.
- Bookends measured on the MP4: first still (0.25 s) and last still
  (15.95 s) are exactly (255,255,255) on all 3,686,400 px
  (check_bookends.py; last 6 decoded frames all 0 non-white,
  check_tail.py). A forced keyframe at frame 460 makes the white
  hold exact through yuv420p.
- Zoom (lineup, 11.3–13.0 s) is parametric: draw-time scale
  1.00→1.22 over coordinates and font sizes. No bitmap is ever
  crop-upscaled (every frame is drawn natively at 2560x1440).

## Beat sheet (120 BPM, BEAT = 0.5 s; all cuts on beats)

| t (s) | beats | content |
|---|---|---|
| 0.0–0.5 | 0–1 | pure-white hold (intro hand-off frame) |
| 0.5–1.5 | 1–3 | title: WHY NOT USE WHAT ALREADY SHIPS? |
| 1.5–4.5 | 3–9 | workload cards pop 2 beats apart: IAS15, interval geometry, KissFFT Fork B (+ NEEDS lines) |
| 4.5–6.0 | 9–12 | job spec: 7 IEEE 754-2019 requirements tick in |
| 6.0–8.0 | 12–16 | OPTION 1 SDK pico→bootrom: honest ✓ then 4 sourced ✗; stamp ELIMINATED (7.55) |
| 8.0–10.0 | 16–20 | OPTION 2 SDK compiler→libgcc: ? rows "not measured" + contraction ✗; stamp NOT MEASURED (9.55) |
| 10.0–11.0 | 20–22 | OPTION 3 SDK none: panic stub; stamp NO FLOATS AT ALL (10.55) |
| 11.0–13.5 | 22–27 | lineup matrix vs spec (✓/✗/?), parametric zoom 1.00→1.22 |
| 13.5–15.0 | 27–30 | settle: MUSE-SOFTFLOAT card, 849 instantiations, bit-identical on silicon |
| 15.0–16.0 | 30–32 | fade to white; 0.75 s exact-white hold out |

Stills eyeballed from the MP4: stills/still_001.0s (title),
003.8s (workloads), 005.7s (job spec), 007.9s (option 1),
009.9s (option 2), 010.9s (option 3), 011.4s/013.2s (lineup
pre/post-zoom), 014.9s (settle), 000.2s/015.9s (white bookends).

## Claims dropped for lack of source

Full list with reasons in options-facts.md. Headlines: every
specific libgcc "lacks" (SF-0 measured none — replaced by the
honest not-measured beat); SDK fmaf/fma double-rounding (S3-only,
excluded by the SF-0-only rule); all cycle/size comparisons
(no-performance fence).

## Known limits

- Copy is terse/technical; owner may want plainer workload lines.
- The CUSTOM column of the lineup stays "?" until the settle card
  (deliberate suspense); if VO names the custom column earlier,
  flip it at 11.0 s instead.
- Silent; beats are placed for 120 BPM music but no track was
  auditioned against it.
