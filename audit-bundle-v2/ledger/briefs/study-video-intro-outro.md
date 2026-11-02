**Role:** study-video-intro-outro (rough-draft scenes, Spark)

**Task (owner):** Rough-draft the demo video's intro and
outro scenes. Concept: closely mimic a phone messenger
app. INTRO: the user's sent message "Hey Muse, I've got
an idea..." appears in the chat; the camera then flies
INTO the final period of that message, which becomes
the next scene's starting point (the git-visual's flat
white plane). OUTRO (reverse): the camera exits from
the typical "..." typing indicator shown while AI apps
reply, pulls back to the phone frame, and the reply
message appears detailing the project, its deliverables,
and the method's metrics along the way - kept to a
reasonable message length, not thoroughly extensive.

**Handoff contract (another agent builds the middle):**
- 1920x1080, 30 fps, 120 BPM beat grid idiom of
  `video/` (read video/style.py, scenes.py,
  timeline.py, STORYBOARD.md for furniture; reuse
  render/probe shapes).
- Intro's final frame: full-frame flat white plane
  (the period zoomed past), specified exactly (color,
  any gradient) so the git visual can start there.
- Outro's first frame: near-black (the git visual ends
  with a box lid shutting and neon going dark) ->
  typing dots emerge as the exit point. Specify your
  opening frames so a cut from dark works.
- Programmatic only (PIL/ffmpeg as the existing
  pipeline does). Rough draft: timing, motion, layout,
  copy - polish happens at assembly.

**Copy:** draft the outro reply message text yourself
from RECORD/README facts (owner will edit): what was
asked, what shipped (softfloat library 849
instantiations, RP2040, workloads bit-identical), the
method in one breath (parcels/verifiers/plants), a few
metrics. Reasonable chat-message length. Numbers must
be true at `a73e97d` or labelled draft placeholders.
The intro message is verbatim: "Hey Muse, I've got
an idea..." - keep the trailing dots; the fly-in
targets the final period char.

**Look:** recognizable modern messenger chat on a
phone (rounded bubbles, blue sent bubble, grey typing
indicator with three animated dots, status bar
suggestion) drawn programmatically - generic shapes,
no copied assets/logos/fonts from any app. Name in the
report what is evoked vs invented.

**Fences:** scratch only (`scratch/study-video-intro/`),
repo untouched, nothing committed; never open/search/
list anything with `cft` in its name; light load; no
network installs (use video/'s bundled ffmpeg path and
.venv as prior studies did).

**Outputs:** prototype clips (intro + outro mp4,
probe-verified 1920x1080/30fps), key stills (chat
frame, mid-zoom, white-plane frame, typing frame,
reply frame), the drafted message texts as .txt,
`scratch/study-video-intro/report.md` (first line
READY/NOT READY as a rough draft; scene timings;
handoff frame specs; what assembly still needs),
`ledger/study-video-intro-outro.md`. Structured
complete/evidence/unresolved. Script files, Git Bash,
MSF_PYTHON pinned.
