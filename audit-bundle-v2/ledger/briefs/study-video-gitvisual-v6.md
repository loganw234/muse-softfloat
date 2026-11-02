**Role:** study-video-gitvisual-v6 (video segment revision, owner-directed)

**Base:** production segment `muse-softfloat/video/segments/gitvisual.py`
(v5, 102.0 s, 2560x1440) at main `97e10a4`. **Work in
`scratch/study-video-gitvisual-v6/` only** - copy the segment and
its data JSONs there and edit the copy. The repo tree is read-only
for you; the lead integrates after the owner sees your draft.
Read the v5 header + `ledger/parcel-polish1.md`-era constraints in
the file itself, `video/STORYBOARD.md` (v5 section), and
`video/style.py` before touching anything.

**Three owner-directed changes, nothing else moves:**

1. **Replay handled like the introduction.** Today the segment
   has two camera languages: the introduction "chase" (close
   follow of one head marble along a near-horizontal track,
   `chase_cam` offsets ~(-980,-760,500), node-arrival emphasis)
   and the replay (pulled-back up-ramp climb, `replay_cam`
   ~(-1900,-1080,+1050) looking up a climbing track). The owner
   likes the introduction's view better: rework the replay so
   the live history is presented in the chase language - the
   camera stays in close follow of the cursor/head marble at a
   chase-like distance and angle, travelling with it, instead
   of the distant up-ramp framing. Hard invariants: real
   topology/lanes/colours unchanged; every marble position
   remains a pure function of the same clock that lights its
   event (`cursor_rank`); gate holds stay exactly on their
   ranks; the bridge flight still lands without a cut; leg
   timings/gate windows keep their wall times (camera/framing
   change, not a retime). If the chase framing at replay speed
   makes lanes unreadable at some leg, say so with stills
   rather than silently widening back out.

2. **Ending: opening, not a box.** Replace `draw_box`'s box+lid
   with an opening in the track plane at the same end position:
   the seven system marbles (same `pack_state` order/labels)
   travel in and **fall into the opening** (a drop with
   believable gravity, each marble visibly entering and
   disappearing), and the `muse-softfloat` label is retained -
   legible beside/above the opening through the fade. Same
   T_BOX/T_FADE/TOTAL timing, same end handoff (near-black
   (3,4,9) -> (2,3,8) after encode). The retained-documents
   meaning must still read: what falls in is kept, nothing
   scattered.

3. **Final gate: tokens out, augmented interval in.** Remove
   the TOKENS, RECOUNTED gate window entirely (no token figures
   anywhere in the segment afterwards; drop the gate2_numbers
   dependency if it becomes unused). Replace it with an
   augmented-interval sample gate in the same window style:
   one real sample from `tests/interval_catalogue.tsv` (name
   its row id on screen or in your prep script) showing the
   interval tightening across stages to the exact stage-3
   sign, closing on the sourced aggregates: 710/710 rows,
   classifications identical, stage-3 counted calls
   283,314 -> 63,305, host == board hash `ae04caf0…c1422`
   (sources: docs/RECORD.md Wave 6 entry + docs/BOARD.md -
   cite on screen, one short tag). Chronology must stay
   honest: history.json is frozen at a73e97d and the augint
   merge is later, so either (preferred if clean) place this
   gate as an epilogue beat after the last rank, explicitly
   dated Wave 6, reusing the tokens window's wall time; or
   state in your report why you anchored it where you did.
   The other two gates (IAS15, KissFFT) and the sendback
   loops are untouched. Any computed sample values come from
   a prep script you retain in your scratch (exact
   arithmetic, printed inputs) - no invented numbers; if a
   drawing is schematic, label it illustration like the
   existing gates do.

**Frozen constraints:** TOTAL stays 102.0 s @ 2560x1440/30fps;
open pure white; 0.5 s / 120 BPM grid; text pacing RULE for any
new copy (dwell = smallest 0.5 s multiple >= max(1.5 s,
0.5 + words/2.5); headlines <=6 words, body <=10, <=2 new lines
per beat, one short source tag); parametric rendering only
(no crop-upscale > 1.0); frames stream, never buffered.

**Outputs (all under your scratch):** the edited renderer,
`gitvisual6.mp4` (full 102.0 s render), stills at: mid-replay
(new framing), interval gate open, marbles mid-fall, final
label frame; a sync measurement (positions vs event clock at
gate/node events - adapt or rewrite the v5 analytic approach,
script retained); `report.md` (what changed per owner item,
design decisions + rejected alternatives, exact sources for
every number on screen, what you could not verify).
Structured complete/evidence/unresolved mandatory.
MSF_PYTHON = workspace .venv python for every render. State
your render wall time as a record, not a rate. ~480 min.
