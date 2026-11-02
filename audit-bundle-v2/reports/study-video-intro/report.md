READY

Rough-draft intro + outro for the demo video. Programmatic only
(PIL + bundled ffmpeg via imageio-ffmpeg, `video/style.py` palette/fonts/beat
grid). Owner edit still needed on copy, music/VO, and assembly transitions.

## Clips (probe-verified, 1920x1080 / 30 fps / H.264 / silent)

- `intro.mp4`: 4.0 s, 120/120 frames decoded, rc 0, 482,937 bytes.
- `outro.mp4`: 6.0 s, 180/180 frames decoded, rc 0, 432,457 bytes.

## Timings (all cuts on the 0.5 s / 120 BPM beat grid)

INTRO 4.0 s:
- 0.0-0.5 phone slides/scales in (ease_out_cubic).
- 0.5-1.5 grey typing bubble, three dots bounce (sin, phase 2.1 rad).
- 1.5-2.0 sent bubble types out verbatim: "Hey Muse, I've got an idea...".
- 2.0-3.5 camera dives at the final period glyph (crop shrinks
  1920x1080 -> ~10x6 px, quadratic ease-in, bilinear upscale).
- 3.5-4.0 flat white hold (all 2,073,600 px exactly 255,255,255).

OUTRO 6.0 s:
- 0.0-1.0 near-black field, three grey dots emerge center-frame
  (measured t=0 frame: dominant pixel 2,3,8 after H.264 round-trip).
- 1.0-2.5 pull-back: phone w/ typing bubble scales 1.6x -> 1.0x with
  fade from black.
- 2.5-3.0 reply bubble 1 ("Always. Here is the headline:").
- 3.0-5.0 reply bubble 2 types out (22 px, wrapped in-phone).
- 5.0-6.0 hold on full chat.

## Handoff frame specs (for the middle/git-visual assembly)

- INTRO final frame: flat full-frame RGB (255, 255, 255), zero gradient,
  held 0.5 s (15 frames). The git visual should start from pure white.
  Zoom target was the final "." glyph of the sent message at phone coords
  approx (1171, 259) in the 1920x1080 frame (bubble right edge, 27 px
  Segoe UI) — re-derive from `render_intro_outro.py::draw_phone` if the
  layout changes.
- OUTRO first frame: flat near-black RGB (3, 4, 9) in source
  (measures 2,3,8 after yuv420p/H.264 round-trip), three grey dots
  (150, 160, 185) fading in. A cut from the git visual's dark lid-shut
  frame lands cleanly; dots are the exit point (reverse of intro entry).

## Evoked vs invented UI elements

Evoked (generic messenger idiom, no assets copied): right-aligned blue
sent bubble, left grey received bubbles, grey three-dot typing indicator,
chat header with avatar/name/online dot, bottom message field + send button.
Invented (not copying any app): status-bar "9:41" + generic battery glyph,
"<" back chevron, "M" avatar disc in video cyan, "online" label, exact
bubble radii/colors (blue 29,101,242 / grey 44,48,66), dot-grid stage
background shared with `video/scenes.py`. Fonts are Windows system
Segoe UI / Arial only. No logos, no trademarks.

## Copy provenance (all numbers true at muse-softfloat@a73e97d)

Reply text drafted from README Status + RECORD Wave 5 close at a73e97d:
849/849 (783 Clause 5 + 66 Tier 2, b16/b32/b64, H=20); IAS15 2,001/2,001
state hashes on all 6 chips (genuine Pico + 5 RP2040-Zero clones);
KissFFT 12/12 configs; 411,213 committed vectors in the merge gate
(`standard` adds 1,117,504 — named in report, not in bubble);
114/120 plants caught, labelled pinned at bc807e6. Method in one breath:
small parcels, each met by a verifier that only disconfirms. Owner to trim.

## Key stills (grabbed from the MP4s via video/probe.py)

- `stills/intro/still_001.0s.png` — typing indicator frame.
- `stills/intro/still_001.8s.png` — chat frame, sent message shown.
- `stills/intro/still_002.8s.png` — mid-zoom into the period.
- `stills/intro/still_003.8s.png` — white-plane handoff frame.
- `stills/outro/still_000.5s.png` — emerging typing dots on near-black.
- `stills/outro/still_001.8s.png` — pull-back to phone.
- `stills/outro/still_003.5s.png` — reply typing.
- `stills/outro/still_005.5s.png` — full reply frame.
- Message texts: `intro_msg.txt`, `outro_msg.txt`.
- Script: `render_intro_outro.py` (re-run with workspace .venv python;
  Git Bash; light load: 300 frames total, no network).

## Assembly still needed

- Middle join: white-plane -> git visual first frame; git dark-end ->
  outro t=0. Middle agent owns the git visual; agree exact white/dark
  values (this draft: in 255,255,255 / out 3,4,9).
- Music/VO: silent by design; 120 BPM grid preserved (4.0 s + 6.0 s),
  so a 120 BPM track drops in.
- Polish pass: ease curves, bubble tails/read-ticks, exact dot bounce
  rate vs beat, caption track, final probe + owner copy sign-off.
