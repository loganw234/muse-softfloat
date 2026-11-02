**Role:** surveyor-epidemiclicense (licence-fact study, Spark)

**Stance:** verify or refute from Epidemic Sound's own published
terms. Quote the controlling text (short excerpts) with the URL
you read it at; distinguish licence-agreement text from
help-centre summaries; anything you cannot ground in a fetched
page is "unresolved", not a guess.

**Facts of the use (owner-supplied):** track "Sunflower Dance"
by Helmut Schenker, Epidemic Sound track page
https://www.epidemicsound.com/music/tracks/5002d052-2046-4b83-b126-5f4de70ea97e/
(ISRC SE5Q52402720 per the file's tags), downloaded under the
owner's **Pro** subscription. Use: synchronised as the music
bed of a ~3-minute hackathon demo video (Meta AI Developer
Hackathon submission). The video will live in a public GitHub
repository and be submitted via the hackathon platform; Meta
or the organisers might republish/showcase it. The track may
be time-compressed by ~2.7% (183.9 s -> 179.0 s) or trimmed
with a fade to fit.

**Owner's reading to test, clause by clause:**
(i) "use here is valid under my Pro subscription";
(ii) "if Meta intends to publish the video it would require
my disclosure to Epidemic but would otherwise be allowed".

**Questions (answer each from fetched sources):**
1. What does the Pro plan cover for online video: which
   platforms/channels, channel limits or whitelisting/
   clearlisting requirements, monetisation, and is a video
   file hosted on GitHub / a hackathon platform (not a
   whitelisted social channel) inside the grant?
2. Third-party republication: if Meta/organisers publish the
   same video on their own channels, is that covered, does it
   need notification/disclosure to Epidemic (owner's clause
   ii), a separate licence, or is it outside Pro entirely?
   Any client-work / transfer provisions that bear on this?
3. Credits/attribution: required anywhere for Pro sync use?
4. Edits: is time-stretching/trimming/fading the track to fit
   the picture permitted; any restrictions (e.g. no remixes,
   no standalone redistribution)? State the raw-track
   redistribution rule explicitly (can the .mp3 sit in a
   public git repo? can the muxed video?).
5. Term: does content published during an active subscription
   stay licensed after it ends? Any Content ID claim handling
   the owner should expect on YouTube etc.?
6. Track page facts: title/artist/BPM/duration as listed, and
   any per-track restrictions shown there.

**Fences:** web research only (epidemicsound.com pages first;
their licence agreement and help centre). Do not modify the
repo tree; write only your two output files. No legal advice
framing: report what the terms say, per clause, with quotes
and URLs, and flag where only Epidemic support could settle
it. Nothing with `cft` in its name; do not open
`docs/metrics/plants.jsonl` (irrelevant here).

**Outputs:** `scratch/study-epidemic-license/report.md` +
`ledger/study-epidemic-license.md`. Structured
complete/evidence/unresolved mandatory; verdict per owner
clause (CONFIRMED / PARTLY / REFUTED / UNRESOLVED) in both.
~120 min.
