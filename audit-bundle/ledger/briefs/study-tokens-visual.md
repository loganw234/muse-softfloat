**Role:** study-tokens-visual (feasibility study + prototype, Spark)

**Question (owner):** Build a visual comparison between the
token count of the owner's own messages and the tokens
tracked by the project metrics - to visually show how
limited the human input was compared to the project as a
whole. Same treatment as study-kissfft-visual: feasibility
+ prototype in scratch only, held for the video rework.

**Data inventory (research first, name exact files):**
1. Human side: the owner's user messages. Sources: Muse
   session logs under
   `C:\Users\logan\.local\share\muse\sessions\` (find the
   session(s) for this project; there may be more than one,
   and one long session was compacted - the log still holds
   the raw messages). Count ONLY genuine owner-typed
   messages. EXCLUDE machine-generated text that arrives in
   the user role: goal-continuation injections ("Continue
   working toward the active session goal..."),
   system-reminders, workflow/tool reconciliations, task
   notifications. Owner messages sometimes start with `*`
   (mid-work notes) - those ARE human. Publish your
   inclusion/exclusion rule with per-class counts so the
   number is auditable.
2. Project side: tokens tracked by metrics -
   `muse-softfloat/docs/metrics/usage.jsonl` (+ the
   extractor that produced it; find it), session-log usage
   records if present, and any per-agent totals. CRITICAL:
   the adherence audit found usage.jsonl FROZEN at 39 rows
   (Wave 3 era) - if you confirm it is stale, say loudly
   what span it covers, reconstruct the fuller total from
   session logs if the fields exist, and present BOTH
   numbers; never silently mix spans.
3. Tokenizer honesty: owner-message tokens need an
   estimator. Name it (e.g. a specific tokenizer if
   available offline in the .venv, else a stated char/word
   heuristic with an error band). If the metrics side uses
   API-billed tokens (input+output+cache?), state exactly
   which categories are summed. The comparison is only
   honest if both sides' definitions are printed on the
   visual itself.

**Design + prototype:** A visual in the video/site idiom
(read study-kissfft-visual's report Sec. 1 for the IAS15
visual's shape; video/style.py furniture at 1920x1080).
Ideas: scale-bar where the human sliver is nearly
invisible then zooms; per-message timeline (each owner
message a tick against cumulative project tokens/waves);
"one sentence -> N tokens of verified work" per-wave
multiplier. Prototype artifacts in
`scratch/study-tokens-visual/` only: data JSON with full
derivation, 1920x1080 still(s), browser-openable HTML
canvas proof, short mp4 if cheap. Every surface carries
its definitions + "as of <date/commit>" stamp. This is
evidence-style content (numbers ARE the claim): no
illustration-only fudge - if a number cannot be derived,
the visual must not show it.

**Fences (hard):**
- Scratch only; repo untouched; nothing committed. Light
  CPU (a parcel sweep is running). No board access.
- Session logs are read for COUNTING only. Do not quote
  owner message text into the report beyond 3-4 short
  illustrative snippets (<=120 chars each) if needed to
  justify a classification; lengths/timestamps are fine.
  No other-person data exists here; still, minimum
  necessary.
- Never open/search/list anything with `cft` in its name.
- No network installs; use what the workspace .venv has,
  else the stated heuristic.

**Outputs:** `scratch/study-tokens-visual/report.md` (first
line FEASIBLE / FEASIBLE WITH WORK / NOT WORTH IT; both
sides' exact derivations with spans + staleness verdict;
headline ratio with error band; design; prototype paths +
how to view; effort to production at video-rework time
 incl. the refresh problem - numbers go stale as work
continues, so the production version needs a regeneration
step, name it; honest weaknesses) and
`ledger/study-tokens-visual.md`. Structured
complete/evidence/unresolved. Script files, Git Bash,
MSF_PYTHON pinned, explicit memory ceilings (session logs
can be large - stream, never slurp whole files into one
string per file if >100 MB; check sizes first).
