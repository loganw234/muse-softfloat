**Role:** study-video-why-v2 (idea breakdown + slowed comparison)

**Owner direction:** (1) The comparison segment
(`scratch/study-video-why/why-1440p.mp4`, 16s) needs
slowing quite a bit - stretch to ~30 seconds for
reading time. (2) Add an "idea breakdown" segment
immediately BEFORE it, giving the concept of what the
project is and why it is being compared at all.
Assembly order becomes: messenger intro -> idea
breakdown -> comparison (stretched) -> git visual ->
outro. Both segments from you, one authorial hand.

**Segment A - idea breakdown (NEW, target 10-16s):**
Establish, in plain energetic terms: the idea (a
software IEEE 754 floating-point library for a chip
with no FPU - the RP2040 - so real science code runs
bit-identically there), what "correct" even means here
(every result the correctly rounded one, every flag
exact - show it, e.g. one operation landing on the
exact answer vs a neighbour), what will prove it
(workloads: IAS15, interval geometry, KissFFT), and
the method teaser (built by briefed agents, every
piece independently verified - the git visual pays
this off). End by posing the question the comparison
answers: why not use what already ships? Facts from
README/RECORD/SF-0 at `a73e97d`; no new claims.

**Segment B - comparison stretched (REWORK of
why-1440p.mp4 -> why2-1440p.mp4, target ~30s):**
Same sourced content and claim discipline as v1
(SF-0 only; not-measured stays not-measured; no
performance framing), re-timed for reading: cards
arrive one beat at a time, each "lacks" line gets its
own dwell (minimum ~1.5-2.0s per text block a viewer
must read; count words and state your dwell rule in
the report), type may grow since fewer simultaneous
elements compete. Keep the ~120 BPM grid (dwells in
0.5s multiples). If 30s needs more air than content,
add sourced depth (e.g. one concrete wrong-answer
example per doomed option from SF-0's measurements)
rather than padding - or say plainly that N seconds
is the honest length and land within 28-32s.

**Shared specs:** 2560x1440 masters, 30 fps,
parametric zooms only (no crop-upscale >1.5x), video/
style idiom. Bookends: idea opens on pure white
(intro handoff), idea->comparison join on white,
comparison ends on pure white (git handoff) - all
measured. Both probe-verified with beat stills you
eyeballed yourself.

**Budget awareness:** film targets 180s; current
assembly is 115s with the 16s why. Your pair landing
at ~40-46s puts the film ~141-147s - state your exact
durations and where trims could come from if asked.

**Fences:** scratch only (`scratch/study-video-why/`
for segment B + new `scratch/study-video-idea/` for
segment A; v1 artifacts preserved), repo untouched,
nothing committed; never open/search/list anything
with `cft` in its name; no third-party softfloat
source consulted; memory ceilings; light-moderate
load.

**Outputs:** idea-1440p.mp4 + why2-1440p.mp4 (+1080p
twins optional), stills, `scratch/study-video-idea/
report.md` (READY/NOT READY; beat sheet; claims with
sources) and an addendum section in
`scratch/study-video-why/report-v2.md` (dwell rule;
what changed vs v1 and why; exact durations),
`ledger/study-video-why-v2.md`. Structured
complete/evidence/unresolved. Script files, Git Bash,
MSF_PYTHON pinned.
