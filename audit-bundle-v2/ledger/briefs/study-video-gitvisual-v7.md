**Role:** study-video-gitvisual-v7 (owner-directed redesign: process graph)

**Base:** your own r2 renderer in `scratch/study-video-gitvisual-v6/`
(gitvisual6.py @ r2, gitvisual6_r2.mp4). Continue in that
scratch; repo stays read-only. Output `gitvisual7.mp4`.

**Owner critique (the brief):** the flyby shows merged git
topology only - 25 branch trees - while the actual process
had 93 distinct agent episodes through Wave 5 alone
(`docs/metrics/passes.jsonl`: 20 author, 36 verifier, 35
surveyor, 3 fixer; 61 worktree directories still on disk).
Studies, the verifier after every parcel, and sendback
rounds are missing. Worse, colour semantics swap at the
bridge: the introduction's LEGEND - SYSTEMS (DEEP colours)
defines roles, then the replay colours lanes by wave. Fix
both: the replay becomes the real process graph, coloured
by role everywhere, and the tree becomes as large as the
records say it was.

**Data (build it, prove it):** retained prep script
`prep_process_graph.py` -> `process_graph.json`, sources in
the copy's repo tree only: `history.json` (spine: 141
commits to a73e97d - film scope unchanged, Wave 6 stays the
dated epilogue gate), `docs/metrics/passes.jsonl` (94 rows
= 93 episodes; anchor each episode start/end to fractional
spine rank by commit timestamps; if the row's `commit` is
in history, that rank is exact), `docs/metrics/briefs.jsonl`
(author base/tip joins onto git merge branches),
`docs/metrics/plants.jsonl` (per-verifier plant ticks:
count + caught/missed). Accounting is part of the
deliverable: every passes row maps to exactly one episode,
every plants verifier attaches to a verifier episode or is
named unmapped in the report - nothing silently dropped.

**Visual model:**
- One branch lane + one travelling marble per episode,
  spawn at its start rank, coloured by DEEP role everywhere
  (author=parcels teal, verifier=pink, surveyor=studies
  purple, fixer=escalations red, agent `lead`=lead/main
  blue). `lane_color` wave colouring is deleted; waves
  survive only as the existing day separators / background.
  A compact DEEP legend persists through the replay (the
  introduction teaches it, the replay must keep meaning it).
- Endpoints honest by role: author lanes return at their
  merge rank (join onto the existing git branch geometry
  where a brief maps to a merge - do not double-draw);
  verifier lanes end at their verdict just before that
  merge, with their plant ticks (small orange marks, filled
  = caught, hollow = missed) at the lane end; surveyor
  lanes terminate in a small node (a document, not a merge)
  and stop; fixer lanes are the red return loops. Existing
  curated sendback loops/labels stay where the data agrees.
- Lane packing by computed concurrency (state the max
  concurrent episodes your layout needed); episode marbles
  smaller than the head marble; labels only where v6 labels
  exist today plus study nodes that gate a later parcel
  (SF-0/1/2 class), sparse by design. HUD gains an agent
  counter (episodes lit / 93) next to commits/merges.
- Everything r2 fixed stays fixed: chase replay camera,
  spine clipping, bridge cross-fade, red persistence rule,
  falling opening + on-plate label, interval epilogue gate,
  IAS15/KissFFT gates, gate ranks [44, 69, 140], TOTAL
  102.0 s, open white, end near-black, sync = pure function
  of the cursor clock (episode activity is a function of
  fractional rank from the same cursor - no second clock).
  If 102 s cannot carry the density readably, render at
  102.0 anyway and make the case with stills in the report;
  do not change TOTAL on your own.

**Outputs:** updated renderer (v7 file, keep r2 files),
`gitvisual7.mp4`, `process_graph.json` + prep script,
stills: dense mid-replay (busiest concurrency moment, say
when), a verifier lane ending with plant ticks readable, a
study node termination, interval gate, final label; sync
re-measurement incl. episode spawn/return at-event checks;
`report_v7.md` (data accounting table by role, mapping
choices + every unmapped row, concurrency/layout numbers,
what the tree still omits - e.g. Wave 6 episodes are outside
passes.jsonl's frozen Wave-5 scope and appear only as the
epilogue gate; say so on screen if a counter implies
otherwise). View every still. Structured
complete/evidence/unresolved mandatory. MSF_PYTHON =
workspace .venv for all renders/prep. ~720 min.
