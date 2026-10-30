# study-video-intro-outro

Rough draft delivered in `scratch/study-video-intro/` (repo untouched).

- `intro.mp4` — 4.0 s, 1920x1080, 30 fps, H.264, silent; 120/120 frames
  decoded, rc 0. Sent message "Hey Muse, I've got an idea..." types out,
  camera dives into the final period, ends on a flat white plane held 0.5 s
  (all pixels 255,255,255 — the git visual's start point).
- `outro.mp4` — 6.0 s, 1920x1080, 30 fps, H.264, silent; 180/180 frames
  decoded, rc 0. Opens near-black (source 3,4,9), typing dots emerge,
  pulls back to the phone, reply message types out (copy drafted from
  README/RECORD at a73e97d; all numbers true, plants labelled bc807e6).
- Key stills in `stills/intro/` + `stills/outro/` (MP4 grabs via
  `video/probe.py`); message texts in `intro_msg.txt` / `outro_msg.txt`;
  full timings, handoff specs, evoked-vs-invented list, and assembly needs
  in `scratch/study-video-intro/report.md` (first line READY as rough draft).
- Script `render_intro_outro.py` re-renders both with the workspace .venv.
- Programmatic only, generic messenger idiom, no copied assets/logos.
- Assembly needs: middle join values (in-white / out-dark agreed here),
  music/VO, polish pass, owner copy sign-off.

## v2 polish pass (study-video-intro-polish)

Delivered beside v1 in `scratch/study-video-intro/` (v1 untouched, repo
untouched, nothing committed). Full evidence in `polish-report.md`
(first line READY); script `render_v2.py`, measurements
`measurements2.json`.

- `intro2.mp4` — 5.0 s (v1 4.0 s), 150/150 decoded rc 0. Period target
  raster-measured (1170.49, 272.0); v1 was 13.0 px high (`ty+ascent/2`).
  Mid-zoom proof centroid error 0.4 px (`still2_period_proof.png`).
  Breath beat 2.0-2.5 s; smootherstep log-scale dive 2.5-4.5 s;
  white hold re-verified all-255 on decoded still.
- `outro2.mp4` — 6.0 s, 180/180 decoded rc 0. Camera is the intro curve
  time-reversed out of the typing dots (centroid 990.5, 409.8) into a
  composed phone frame at x 880-1420. First frame re-verified (2,3,8)
  decoded. Reply trimmed 370 -> 160 chars (`outro_msg2.txt`); initial
  user message scrolled off (header-cropped sliver + unreadable bar
  bubbles). Side graphics on beats: left human:AI split card at 3.5 s
  (project 1,196,128,770 billed from refreshed `docs/metrics/usage.jsonl`
  @ a73e97d, 93 rows; owner ~1,928 est.; definitions on-frame; the
  tokens study's double-counted 38.6M not used), right stat cards at
  4.0/4.5/5.0 s (849/849, 411,213, 6 boards IAS15 2,001/2,001).
- Handoff specs NOT moved. Assembly: intro +1.0 s vs v1 (total 11.0 s),
  owner copy/panel sign-off, music/VO, at-speed watch-through.


## v3 text/pacing pass (study-video-textpacing, Agent A)

Delivered beside v1/v2 in `scratch/study-video-intro/` (priors
byte-identical; repo untouched; nothing committed). Full evidence:
`textrev-report.md` (first line READY; copy table; dwell audit 0
violations under the stated persistence convention, solo-reading
risk named); scripts `render_v3.py` (+ idea/why siblings below),
`audit_textrev.py`/`audit3.json`, `verify3.py`/`verify3.json`,
`measurements3.json`.

- `intro3.mp4` - 7.0 s, NATIVE 2560x1440 (v2 master was 1080p),
  210/210 decoded rc 0. Whole design scaled parametrically (K=4/3);
  period centroid RE-MEASURED at 1440p: raster (1561.46, 361.5),
  metrics agrees within 0.5 px; mid-dive proof error 0.6 px
  (`still3_period_proof.png`, eyeballed); intro clamp 0.0 px.
  Message holds 1.5-4.5 s (rule dwell 3.0 s for 6 words), same
  2.0 s dive, white hold re-verified 0 non-white px.
- `outro3.mp4` - 8.5 s, 2560x1440, 255/255 rc 0. First frame
  decoded (2,3,8) dominant (source 3,4,9, spec unchanged). Dots
  centroid re-measured (1320.0, 545.3); outro clamp 0.146 px.
  Reply bubble cut to "Identical on all 6 boards." (849/411,213
  stay on the stat cards); left panel definitions block collapsed
  to one tag (full definitions quoted in the report); panels now
  reveal in 6 staged beats, <=2 new lines each.
- Frames stream (v2 buffered all frames; at 1440p that breaks the
  memory ceiling). Words intro+outro 97 -> 52 (-46%).
- Assembly: intro+outro now 15.5 s (was 11.0 s); handoff VALUES
  unchanged (white / near-black); owner copy sign-off still open.
