FEASIBLE WITH WORK

# Tokens visual feasibility study (+ prototype)

Headline: **~1,928 owner tokens [1,350-2,507] vs 1,514,499,184 project billed tokens -
about 1 : 785,000, a 0.00013% human share.** Both sides built from primary
data by our own scripts; every visual stamps its definitions and date.

## 1. Human side: owner-typed message tokens (exact derivation)

Source: the lead session log
`C:\Users\logan\.local\share\muse\sessions\2026\10\26\01a17907-4147-7333-a565-56071da9d971\session.jsonl`
(135 MB, 88,110 lines, streamed - never slurped; sizes checked first).
Owner text arrives as `payload.kind == 'run'` + `event.kind == 'started'`
`prompt` fields: 125 such prompts total, span
2026-10-26T09:28:26-07:00 -> 2026-10-28T20:01:15-07:00.

Inclusion rule (published, auditable):
- INCLUDE a prompt iff it is non-empty and not the machine goal-continuation
  template - i.e. genuinely owner-typed text, including `*` mid-work notes.
- EXCLUDE (a) 77 empty prompts (run wake/resume/approval follow-ons, no user
  text), (b) 8 goal-continuation injections (template
  "Continue working toward the active session goal." + appended objective),
  (c) everything else machine (skill-body context blocks, inbox deliveries,
  reminders - none of which are `run/started` prompts).
- Result: **40 owner / 77 empty / 8 goal-continuation / 125 total.**
- One owner prompt was sent twice verbatim (duplicate resend); both copies
  entered the model, both counted. A `request_user_input` round (machine-asked
  question, owner picked 2 labels) is negligible (<15 words) and excluded;
  noted here so it is not silently dropped.
- No other session holds owner text: all 28 other top-level session dirs were
  scanned for non-empty non-template `run/started` prompts - zero found; the
  only two project-workspace sessions besides the lead (13 KB / 9 KB) contain
  login/startup records only (no model calls, no prompts).

Justifying snippets (<=120 chars each, 3 total): the injection template
"Continue working toward the active session goal."; a `*` mid-work note
"*The cables used on a few were power only, the full range test will have to wait
till I get a few more cables" [truncated]; a short directive "Go ahead with SF-0".

Counts: 40 prompts, **7,713 chars, 1,361 words** (per-message lengths kept in
`owner_msg_lengths.json`; full texts not retained).
Tokenizer: no token library in the offline `.venv` (tiktoken and transformers
both absent, verified by import probe) -> **chars/4 heuristic, +/-30% band**:
1,928 [1,350-2,507]. Cross-check: words x 1.33 = 1,810, inside the band.

## 2. Project side: tokens tracked by metrics (exact derivation + staleness)

(a) `muse-softfloat/docs/metrics/usage.jsonl` (frozen project input):
39 rows, waves 0-3 only. Sums: input 479,208,343 + output 2,063,706 =
**481,272,049 billed**, cached 468,544,417, 2,890 messages.
Span from `passes.jsonl`: **2026-10-26T09:24:41-07:00 ->
2026-10-27T11:16:42-07:00**.
**STALENESS VERDICT: CONFIRMED STALE.** No wave4/wave5, site-demo, video-rework,
or study rows; everything after 2026-10-27 11:16 PT is missing (~2/3 of billed
tokens to date). Never mix this span with the fuller total below.

(b) Fuller total reconstructed from session logs (this study):
summed `model_completed` provider usage over the lead + all 241 subagent
transcripts (`aggregate.py`, same counting rule as
`muse-softfloat/tools/extract_session_metrics.py`: only usage-dict completions,
per-file exact-duplicate suppression). Method validated: recomputed the
`reader-parcelround-cases` session byte-identically to its usage.jsonl row
(in 1,496,621 / out 30,233 / 20 msgs). Tree: input 1,469,302,586 +
output 6,444,124, cached 1,424,594,514 (subset of input, NOT additive),
reasoning 2,697,352 (excluded from billed), 8,709 messages, 241/242 sessions
with usage (1 with none), span -> **2026-10-28T20:07:54-07:00**.
Three usage.jsonl sessions (verifier-w2xf, auditor-wave2, auditor-final;
in 38,594,472 / out 158,002 / 242 msgs) no longer exist on disk - their rows
are added back from usage.jsonl. **Grand total: 1,507,897,058 in +
6,602,126 out = 1,514,499,184 billed, 8,951 model responses.**
Top-level session-dir copies carry no `model_completed` records (different
persistence) and are excluded to avoid double-count; 11 unmapped top-level
sessions mention the project but carry zero billed tokens (non-model views).

Definitions (printed on every visual): owner = chars/4 heuristic over 40
owner-typed lead prompts (+/-30%); project = API-billed input+output from
`model_completed` logs (cached is a subset of input, not additive).

## 3. Headline ratio with error band

1,928 [1,350-2,507] : 1,514,499,184 -> **~1 : 785,427 (band 1:604k-1:1.12M),
human share 0.00013%**. Per-message view: 40 owner prompts vs 8,951 model
responses (~1:224); ~37.9M billed tokens per owner message on average.
Per-wave multiplier (owner words -> wave billed): wave0 454 -> 68.8M;
wave1 73 -> 171.3M; wave2 35 -> 104.9M; wave3 0 -> 136.2M (fully autonomous);
post-wave3 799 -> 1,033.2M. The zero-word wave3 row is the story: the machine
kept billing while the owner slept.

## 4. Design (video/site idiom, style.py furniture, 1920x1080)

Two stills + HTML canvas + 4 s mp4, mirroring the IAS15 orbit -> hashlock arc
(evidence first, illustration labelled):
1. `still_scale.png`: full-width project bar; human = 1-px sliver; x500,000
   zoom panel makes the human tick visible ("YOU: ~1,928 tokens").
2. `still_timeline.png`: 40 owner ticks on a time rail over a log-scale
   cumulative billed step curve; steps land on wave aggregates only, labelled
   "within-wave shape NOT reconstructed"; per-wave word->token multipliers.
3. `tokens_canvas.html`: standalone canvas proof, zoom toggle, no server.
4. `tokens_zoom.mp4`: 4.0 s, 30 fps, 120/120 frames decode clean
   (`video/probe.py`), 1920x1080 exact. No number shown that is not derived.

## 5. Prototype artifacts (this directory; view how)

- `data/tokens.json` - sole numbers source (full derivation, spans, bands).
- `tree_usage.json` - lead-tree aggregate output; `owner_msg_lengths.json` -
  per-message lengths/timestamps (no full owner text retained).
- `aggregate.py` - log re-sum; `gen_data.py` - tokens.json builder;
  `render_frames.py` - stills + HTML (+ `--mp4` for video).
- `still_scale.png`, `still_timeline.png` - open in any image viewer.
- `tokens_canvas.html` - open directly in a browser (no server needed).
- `tokens_zoom.mp4` - play in any player.
- Run: `MSF_PYTHON=.venv/Scripts/python.exe` (Pillow/numpy/imageio-ffmpeg
  present); gen then render. Light load except `aggregate.py` (~570 MB
  stream, run when idle - a parcel sweep was running during this study).

## 6. Effort to production quality (video-rework time)

Small: one `video/scenes.py` scene kind (scale bar + zoom + tick rail, reusing
base_frame/kicker/footer furniture) + timeline entry fed by a refreshed
`data/tokens.json` + STORYBOARD section; site canvas mirroring `drawOrbit`.
The load-bearing item is the **regeneration step**: numbers go stale as work
continues (they already did once - Sec. 2), so production needs
`aggregate.py --until <freeze-ISO>` + `gen_data.py` re-run at video-freeze
time, with the new freeze timestamp stamped on-frame. Add `--until` cutoff
support (mirroring the extractor's flag) so the production number is
reproducible. Estimate: one focused parcel, no board/firmware work.

## 7. Honest weaknesses

- Owner side is a heuristic (chars/4, +/-30%): no offline tokenizer, so the
  human number is the fuzziest on the page; the band is load-bearing.
- Project side mixes provider-billed tokens with an estimated human number -
  different rulers, stated on every surface, but a purist objection stands.
- The cumulative curve is wave-aggregated steps, not a true per-hour curve;
  within-wave shape is unknown (a full per-completion time series needs
  another heavy pass and would still be wave-lumpy).
- 241 sessions share one lead tree; three usage.jsonl sessions are gone from
  disk - the grand total depends on their surviving rows.
- The visual flatters the project (1.5B looks productive) while saying
  nothing about waste: billed != useful.
- Numbers expire: any video frame is stale the next day unless regenerated.
