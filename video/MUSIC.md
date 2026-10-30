# MUSIC.md - the soundtrack decision and its licensing record

## Decision (2026-10-30, owner)

Chosen track: **"Sunflower Dance" by Helmut Schenker**, courtesy of
Epidemic Sound (track page:
https://www.epidemicsound.com/music/tracks/5002d052-2046-4b83-b126-5f4de70ea97e/;
ISRC SE5Q52402720; natively 124 BPM, 183.9 s), downloaded under the
owner's Epidemic Sound **Pro** subscription. The soundtrack version
is published as an unlisted video on the owner's YouTube account:
https://www.youtube.com/watch?v=IzLtd2_OIFo ("Muse-Softfloat | Meta
Global AI Developer Hackathon"). Credit line (recommended
practice on the study below): Helmut Schenker / Sunflower Dance /
courtesy of www.epidemicsound.com.

Licensing posture, from a terms study against Epidemic's own pages
(full evidence in the project ledger, `study-epidemic-license`,
2026-10-30; verdict PARTLY on both owner readings — not legal advice):

- The muxed sync use (music bed under the demo video) is inside the
  Pro grant; cutting/looping/fading to fit is explicitly allowed,
  and the ~2.7% time-compression used to fit the 179.0 s cut sits
  within "cut or looped to fit content" on a plain reading.
- Publication must happen while the subscription is active, with
  the video URL/channel safelisted in the owner's account; content
  published while active stays cleared permanently.
- **The raw track must never be committed to this repo** (standalone
  distribution is prohibited), and this repo is not a venue named in
  the grant — so **every cut in this repo stays silent**. The
  soundtrack version is hosted as an unlisted video on the owner's
  YouTube account.
- If Meta/organisers republish the video, the owner safelists their
  published video URLs from his Pro account (the sublicence
  clearing mechanism); organiser resharing is not explicitly
  covered in the fetched terms, so that step is the owner's to
  confirm with Epidemic support if it arises.

The free-licence options recorded below were the pre-decision survey
(retained as history); none was used.

---

(Original options survey, 2026-10-27:)

`out/final.mp4` ships silent by brief: music/VO is an owner decision.
No audio was downloaded in the video-final pass. The timeline is built
for a drop-in bed: every cut lands on the 0.5 s grid of a 120 BPM bar
(`style.BPM = 120`, quarter-note cuts; scene boundaries below are all
on whole seconds). If a chosen track is not 120 BPM, either pick the
nearest-tempo mix or re-derive the grid (`style.BEAT`) and re-render -
the timeline is data.

Licences below were checked on the sources' own pages / licence
summaries on 2026-10-27. **Re-verify the exact track's licence on its
own page at download time and keep a copy of that page with the
project** - catalogue licences change, and per-track terms rule.

## Option 1 - Kevin MacLeod, incompetech.com (CC BY 4.0)

- Where: https://incompetech.com/music/royalty-free/ (searchable by
  genre, tempo, feel; 2,000+ tracks).
- Licence: Creative Commons By Attribution 4.0 for the royalty-free
  catalogue - free with a credit line ("<Track>" Kevin MacLeod
  (incompetech.com), Licensed under Creative Commons: By Attribution
  4.0) in the video description / end card. A paid standard licence
  exists where attribution is impractical.
- Fit: filter Genre = Electronica / Techno, tempo ~120 BPM, length
  >= 3:00, then audition against the segment cues below. Confirm the
  BPM printed on the individual track page before locking the grid;
  if it is 118-122, cutting on our 0.5 s grid still reads on-beat.
- Cost: $0 with attribution.

## Option 2 - Pixabay Music (Pixabay Content License)

- Where: https://pixabay.com/music/ (search "120 bpm electronic" /
  "energetic techno"; duration filter >= 3:00).
- Licence: Pixabay Content License - commercial and non-commercial
  use, modification allowed, **no attribution required**; you may not
  redistribute/sell the track standalone. Pre-2019 uploads are CC0.
- Fit: large electronic catalogue at exact BPMs; download the track
  page's licence summary alongside the audio. No end-card credit owed,
  which suits a 3-minute submission with no credits crawl.
- Cost: $0.

## Option 3 - ccMixter (per-track Creative Commons; use CC BY only)

- Where: https://ccmixter.org/ (filter: licence = Attribution).
- Licence: per-track - use **only CC BY (3.0/4.0)** tracks. Avoid
  CC BY-NC (non-commercial - wrong for a public hackathon entry) and
  sampling+/share-alike variants unless the owner accepts their terms.
  Attribution to the artist + track title in the description.
- Fit: electronic/remix culture catalogue; BPM is listed per track.
  Smaller and more variable than options 1-2 - a fallback, not the
  first pick.
- Cost: $0 with attribution.

## Checked and ruled out

- **FreePD.com** (formerly the cleanest CC0 source): permanently
  closed - the site itself now reads "2008-2025 ... service offline"
  (read 2026-10-27). Mirrors exist, but per-file CC0 status cannot be
  verified from a mirror, so per this pass's rule nothing was taken
  from one.
- Anything labelled only "royalty-free" without a named licence, and
  any NC (non-commercial) track.

## Cue sheet for the music editor (segment boundaries)

| Time | Segment | Energy note |
|---|---|---|
| 0:00 | 1. Hook | starts loud on frame 1; hits on "FPU" (0:01) / "EXCUSES" (0:02) |
| 0:08 | 2. The problem | strikes land 0:09-0:13; turn at 0:26 |
| 0:30 | 3. The contract | counter peaks ~0:33; cards 0:36 |
| 0:55 | 4. The method | charts/ticker ride the groove |
| 1:25 | 5. The catch | **slow/thin the arrangement ~20%**; turn at 1:38, fix at 1:44 |
| 1:50 | 6. The scale | fastest cutting; numbers as hits |
| 2:15 | 7. The board proof | hash completes ~2:19, stamp lands after |
| 2:32 | 8. IAS15 climax | breathe under orbits; hash-lock 2:46, verdict stamp ~2:52 |
| 2:54 | 9. Close | final bar ends 3:00 on the cut to black |

VO remains optional: every storyboard line is already on screen as
kinetic type, so a music-only bed needs no re-cut.
