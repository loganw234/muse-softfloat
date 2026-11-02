**Role:** study-video-intro-polish (intro/outro polish pass, full model)

**Input:** the Spark rough draft in
`scratch/study-video-intro/` (intro.mp4, outro.mp4,
stills, message txts, report.md with handoff specs).
Owner reviewed it: direction approved, needs polish to
be smoother and more accurate. Produce v2 clips beside
v1 (never overwrite v1): `intro2.mp4`, `outro2.mp4`,
new stills with `2` suffixes.

**Owner fixes (verbatim intent, all required):**
1. INTRO accuracy: the fly-in currently misses the
   final period by a bit. Track the actual final "."
   glyph of "Hey Muse, I've got an idea..." - compute
   its rendered pixel position from the text layout
   (measure, don't eyeball), and land the zoom dead
   center on it. Prove it with a mid-zoom still where
   the period is centered (crosshair check in your
   report: period centroid vs frame center, in px).
2. INTRO smoothness: it feels abrupt. Proper camera
   move: eased push-in (slow start, accelerate into
   the period, brief settle), no velocity steps; the
   message send beat gets a breath before the move.
   Keep the 120 BPM grid landing points musical.
3. OUTRO camera: fix placement issues - the exit from
   the "..." typing dots should be the true reverse of
   the intro move (match scale/position curve family),
   settling into a well-composed phone frame (phone
   placement deliberate, not dead-center by default).
4. OUTRO copy: the reply message is too long. Trim to
   a genuine chat-length reply (target roughly half or
   less of v1; every number still true at `a73e97d`).
   Also: LOSE the initial user message in the outro -
   the chat should imply more conversation happened
   during the middle portion (scroll position/history
   hint: the "Hey Muse..." bubble scrolled off or
   cropped at top, maybe a faint intervening exchange
   suggested, not readable).
5. OUTRO side space: use the left/right space beside
   the phone for supporting graphics as the reply
   lands - e.g. the human:AI work split (data:
   `scratch/study-tokens-visual/` + refreshed metrics
   `docs/metrics/usage.jsonl` at `a73e97d`; the study
   grand total double-counted 38.6M - use refreshed
   numbers, definitions on-frame) and/or deliverable
   stat cards (849 instantiations, 411,213 vectors,
   six boards). Restraint: they support the message,
   not compete; sequence them with the reply beats.

**Handoff contract (unchanged):** 1920x1080 30 fps;
intro ends full-frame pure white (255,255,255)
pixel-verified; outro opens near-black cutting from
the git visual's dark end; the git-visual agent is
building to these specs RIGHT NOW, so final-frame
specs must not move - if you think they should, say
so in unresolved instead of changing them.

**Method:** same programmatic idiom (PIL + bundled
ffmpeg, video/ style). Measure twice: glyph metrics
for the period target, frame-center proofs, probe
decode counts, pixel checks on hold frames. Eyeball
every key still yourself before claiming it.

**Fences:** scratch only (`scratch/study-video-intro/`),
repo untouched, nothing committed, v1 artifacts
preserved; never open/search/list anything with `cft`
in its name; generic messenger idiom, no copied
assets; light-moderate load (another agent is
rendering concurrently).

**Outputs:** intro2.mp4 + outro2.mp4 (probe-verified),
v2 stills incl. the period-centroid proof still,
trimmed message txt(s), `scratch/study-video-intro/
polish-report.md` (first line READY/NOT READY; per-fix
evidence with measurements; what assembly still
needs), append to `ledger/study-video-intro-outro.md`.
Structured complete/evidence/unresolved. Script files,
Git Bash, MSF_PYTHON pinned.
