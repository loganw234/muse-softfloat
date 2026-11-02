# Study: tokens visual (owner messages vs project tokens)

Feasibility study + prototype for a video/site visual comparing the owner's
own message tokens against the tokens the project billed. Held for the video
rework. Verdict: **FEASIBLE WITH WORK** (see report).

- Human side: 40 owner-typed lead prompts (7,713 chars / 1,361 words),
  estimator chars/4 +/-30% -> **~1,928 tokens [1,350-2,507]**.
  Rule: include only non-empty non-template `run/started` prompts; exclude
  77 empty wake/resume prompts + 8 goal-continuation injections.
- Project side: `usage.jsonl` (39 rows, waves 0-3) **CONFIRMED STALE**
  (ends 2026-10-27T11:16:42-07:00, 481.3M billed). Fuller total reconstructed
  from lead + 241 subagent logs + 3 surviving rows of pruned sessions:
  **1,514,499,184 billed (input+output), 8,951 model responses**,
  span -> 2026-10-28T20:07:54-07:00. Method validated by byte-exact
  reproduction of one usage.jsonl row.
- Headline: **~1 : 785,000 (band 1:604k-1:1.12M), 0.00013% human share**.
- Prototype (scratch only, repo untouched, nothing committed):
  `scratch/study-tokens-visual/` - `data/tokens.json` derivation,
  1920x1080 `still_scale.png` / `still_timeline.png`, `tokens_canvas.html`
  (browser, no server), `tokens_zoom.mp4` (4 s, 120/120 frames clean).
  Every surface prints both definitions + as-of stamp.
- Production: one parcel at video-rework time; load-bearing item is the
  regeneration step (`aggregate.py` + `gen_data.py` re-run at freeze time,
  needs an `--until` cutoff flag), since numbers go stale as work continues.
- Full derivations, design, and weaknesses:
  `scratch/study-tokens-visual/report.md`.
