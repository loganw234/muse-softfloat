**Role:** text/pacing revision agents (two, parallel)

**Owner direction:** text pacing is a general concern;
there is a bit too much text in general; pacing based
on WORD COUNT to keep a good pace; shift to more
plain language. Lead-defined uniform rule below.

**THE RULE (apply exactly, state deviations):**
- Dwell for any text block = the smallest 0.5s-grid
  multiple >= max(1.5s, 0.5s + words/2.5). (2.5
  words/s reading allowance with motion on screen.)
- Headlines <= 6 words. Body lines <= 10 words. At
  most 2 NEW lines of text per beat; old text may
  persist dimmed but new reading load is capped.
- Cut total on-screen words per segment by roughly
  a third vs current. Source stamps: keep at most
  one short source tag per scene (not per claim);
  full sourcing lives in reports, not on screen.
- Plain language: replace jargon on first use with
  the plain fact, keeping the technical term once in
  parentheses only where it is the actual name of the
  thing. Worked examples of the target register:
  "next value A + 1 ULP" -> "the next number the chip
  can hold"; "subnormals flushed to zero" -> "tiny
  results silently become zero"; "NaNs rendered as
  infinities - payloads gone" -> "error values turn
  into infinity"; "compiler FMA contraction varies
  by target" -> "the same code can give different
  bits on different targets"; "correctly rounded"
  stays (it was defined in the idea segment) but its
  definition line gets plainer too.
- Facts do not move: same claim pools, same sources,
  same numbers. Plain does not mean vague where a
  number is the point.

**Agent A (intro/outro + idea + why):** revise copy
in render_v2.py (intro/outro), render_idea.py,
render_why2.py; re-render ALL at 2560x1440 native -
including intro/outro, whose masters are still
1920x1080 (this is the production resolution fix:
parametric rendering at 1440p, period targeting and
camera curves unchanged in shape, re-measured at the
new scale; handoff frame values unchanged). Outputs:
intro3.mp4, outro3.mp4, idea2-1440p.mp4,
why3-1440p.mp4 beside prior versions; stills; a copy
table (old -> new, word counts, dwell before/after).

**Agent B (git visual v5):** revise popup/window/
label/stamp text in render_gitvisual4.py -> v5:
popup bodies become title + <=2 short lines; window
captions trimmed; per-claim src stamps collapse to
one micro-source per scene; legend stays. Marble
sync machinery untouched in behavior (re-measure sync
after text changes: still 0.0px class). 1440p as v4.
Outputs: gitvisual5.mp4, stills5/, copy table.

**Both:** scratch only (existing study dirs), repo
untouched, nothing committed, prior versions
preserved; never open/search/list anything with `cft`
in its name; probe-verify; eyeball stills; durations
reported against the 180s film (assembly v4 was
145.5s; dwell growth must be bought with the word
cuts - target: film stays <=160s before music).
Reports: `<dir>/textrev-report.md` (A) /
`polish5-report.md` (B) with READY line, the copy
table, dwell audit (every block: words, dwell given,
rule minimum - violations zero or named), ledger
append. Script files, Git Bash, MSF_PYTHON pinned,
memory ceilings, moderate load (you run concurrently;
stay in your dirs).
