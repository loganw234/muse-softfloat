# study-video-why-v2 — idea breakdown + slowed comparison

Status: READY (both segments). Brief:
ledger/briefs/study-video-why-v2.md. Facts pinned at
muse-softfloat a73e97d (HEAD verified this run). Scratch only;
repo untouched (muse-softfloat git status clean); nothing
committed; v1 why artifacts preserved.

## Deliverables

- Segment A (new): scratch/study-video-idea/idea-1440p.mp4,
  14.5 s, 2560x1440@30, 435/435 frames, 1,051,203 B (+1080p twin).
  Script render_idea.py; stills/; report.md (READY; beat sheet;
  claims+sources). White at 0.2 s and 14.3 s measured exact
  (0 non-white of 3,686,400 px).
- Segment B (rework): scratch/study-video-why/why2-1440p.mp4,
  32.0 s (top of the 28-32 s honest band), 960/960 frames,
  2,453,116 B (+1080p twin). Script render_why2.py; stills2/;
  report-v2.md (READY; dwell rule; vs-v1 changes; durations).
  White at 0.2 s and 31.8 s measured exact.
- Verification: scratch/study-video-idea/verify_v2.py (video/
  probe.py decode + stills + white counts); beat stills eyeballed
  by the author (two overlap defects found in stills and fixed:
  idea number-line label collision; why2 option-1 stamp/example
  collision and option-2 example timing past scene end).

## Assembly / budget

Order: intro -> idea (14.5) -> why2 (32.0) -> git -> outro; all
joins on measured pure white. Pair 46.5 s replaces 16.0 s v1 why:
115 s assembly -> ~145.5 s vs 180 s target. Trim candidates listed
in report-v2.md (to ~29 s for why2 without dropping claims).

## Discipline held

SF-0-only claim pool per options-facts.md (unchanged);
not-measured stays not-measured; no performance framing; dropped
claims stay dropped; three new "e.g." lines are labelled direct
consequences of already-sourced statements, not measurements.
No cft-named path opened/searched/listed; no third-party
softfloat source consulted. Parametric zooms only; frames
streamed one at a time (memory ceiling); MSF_PYTHON = workspace
.venv python for every run; all work via script files.

## Open for owner/lead

Copy polish, VO/music sync (silent, 120 BPM grid), "in a minute"
footer in idea segment presumes git-visual length, named
sub-1.5 s holds in report-v2.md dwell section.


## v3 text/pacing pass (study-video-textpacing, Agent A)

Status: READY (both segments). Brief:
ledger/briefs/study-video-textpacing.md (dwell from word count:
smallest 0.5 s multiple >= max(1.5, 0.5 + words/2.5); headlines
<=6 w; body <=10 w; <=2 new lines/beat; plain language; ~1/3
word cut). Same a73e97d facts / SF-0 discipline; priors
byte-identical; repo untouched; nothing committed. Report:
scratch/study-video-intro/textrev-report.md (READY; copy table;
dwell audit 0 violations on the persistence convention stated
there, with the stricter solo-dwell reading named: 59/73 blocks
under on solo intervals - lead/owner call).

- Segment A': scratch/study-video-idea/idea2-1440p.mp4, 22.5 s
  (was 14.5), 675/675 frames rc 0, 881,976 B. Script
  render_idea2.py; stills-idea2/. Words 195 -> 132 (-32%).
  Jargon plain per brief ("the next number the chip can hold",
  number-line prompt line cut). White 0.2/22.3 s exact.
- Segment B': scratch/study-video-why/why3-1440p.mp4, 33.5 s
  (was 32.0), 1005/1005 rc 0, 1,574,914 B. Script render_why3.py;
  stills3/. Words 337 -> 198 (-41%). Lineup recap scene CUT
  (zero unique claims; its dwell could not fit the 160 s film);
  bootrom asterisk + two "e.g." lines cut as redundant (named
  in the copy table); one source tag per option scene.
  White 0.2/33.3 s exact.
- Budget: front pair (incl. intro3/outro3) 57.5 -> 71.5 s;
  with gitvisual4 88.0 s the film is 159.5 s <= 160 s before
  music (v4 assembly 145.5 s). gitvisual5 (Agent B) duration
  was still in flight at this writing.
