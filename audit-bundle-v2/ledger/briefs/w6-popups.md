**Role:** parcel-w6popups (owner film note: generalise the chase popup cards)

**Base:** `f01dc96055f24b4aa5450bdadabf44fa5308abb9`, branch
`wave6-popups`, worktree `worktrees/w6-popups`. Work only there.

**What changes:** only the seven chase popup cards in
`video/segments/gitvisual.py` (`POPUP5`, ~line 99). Today each card
shows one specific historical example (e.g. PARCEL /
"173 binary32 routines" / "one file: msf32.c"). The owner wants
**general descriptions** instead — the process replay that follows
already shows the specifics — and each card should also carry the
**total count of that metric in the project** (how many parcels,
verifiers, etc.).

Card shape (title + at most 2 short lines, as today):
- Title: the system name, matching the on-screen LEGEND - SYSTEMS
  (lead/main, parcels, verifiers, plants, gates, studies,
  escalations). Pluralise if you like; stay one or two words.
- Line 1: the general description in plain language (owner's
  example for parcels: "Work is divided"). Say what the thing
  *is/does* in the method, no incident specifics, no hashes,
  no file names, no per-example numbers.
- Line 2: the project total for that system, as a short counted
  phrase (e.g. "20 parcels" — derive the real number, below).

**Numbers discipline (hard):** every count must be derived by a
script you run against the segment's own frozen data or HEAD
metrics, and quoted in your report with its source file and the
exact query. Prefer the counts that match what the following
replay actually draws (`video/segments/process_graph.json` /
`history.json` are frozen at a73e97d: 93 episodes); where a HEAD
`docs/metrics/` total differs from the frozen-graph count, list
both in the report, put the frozen-graph-consistent one on the
card, and say why. Never invent or round a count. (For GATES a
test-volume total is the natural "count"; derive it from the
numbers the tree already carries, e.g. `tools/run.sh` budget
output / RECORD, and cite it.)

**Timing freeze (hard):** popup word counts drive
`POPUP_DWELL -> ARRIVALS -> T_BRIDGE -> SHIFT -> TOTAL`. The film
is sealed at 185.0 s native / 179.03 s with music already muxed
to it, so this parcel must not move a single timing. Constraint:
**the per-card `POPUP_WORDS` values must be identical to base,
card by card** (title + lines token count via the file's own
`word_count`). Write copy that fits the existing word budgets
exactly. Prove by importing the module before and after:
`POPUP_WORDS`, `POPUP_DWELL`, `ARRIVALS`, `T_BRIDGE`,
`T_REPLAY`, `SHIFT`, `GATES` (ranks/t0/t1), `LEGS`, `TOTAL`
all identical; quote both dumps in the report.

**Owned files:** `video/segments/gitvisual.py` (`POPUP5` strings
and their comment only — no other code), the regenerated
`video/segments/gitvisual7.mp4`, `docs/metrics/briefs.jsonl`
(own row, wave "wave6", binary-append). Do NOT touch assemble.py
or produce an assembly — the lead assembles at merge. Do not
touch any audio/music files.

**Acceptance:** (a) the before/after copy table with per-card
word counts (identical) and each count's derivation + source;
(b) the timing-constant equality proof above; (c) rendered
`gitvisual7.mp4` probed (108.0 s, 2560x1440@30, silent) and one
still per new card, viewed: text inside the card, no overflow,
title/lines legible at 1440p; (d) cursor/gate spot check by
import at the new render (cursor exactly on each gate rank at
t0; TOTAL 108.0); (e) `tools/run.sh standard` PASS unchanged
in the worktree; (f) diff vs base limited to owned files.

**Copy rules:** plain language, headlines <=6 words, lines <=10
words, no claim the following replay doesn't show (the replay
is the evidence; the card is the label). Timings in your report
are records, never performance claims.

**Outputs:** tip commit(s) on `wave6-popups`, detailed body +
`Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>`; `scratch/parcel-w6popups/report.md` +
`ledger/parcel-w6popups.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git Bash,
MSF_PYTHON = workspace .venv. Nothing with `cft` in its name;
do not open `docs/metrics/plants.jsonl` row contents (you may
count its lines/grades mechanically if a plants total needs it,
citing only the totals). ~240 min.
