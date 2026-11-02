# parcel-w6captions — captions + stills for the final cut

Branch `wave6-captions` on base `cdc40ae`; brief
`ledger/briefs/w6-captions.md`; full evidence in
`scratch/parcel-w6captions/report.md`.

- Retry note: a previous attempt died on a provider quota error
  leaving four uncommitted drafts (`video/captions.py`,
  `video/out/assembly_v6.srt`/.vtt, `video/out/stills_v6/`). Treated
  as untrusted: generator re-run from scratch (`--validate`,
  `--stills`), byte-stability re-proved, every probe re-validated.
  Drafts were sound — regenerated artifacts match exactly; zero
  content fixes needed.
- `video/captions.py` derives 77 cues from the segment audit tables
  (idea/why BLOCKS, intro/outro BLOCKS, gitvisual POPUP5 +
  gate-window titles; offsets intro 0 / idea 7 / why 33 / gitvisual
  65 / outro 173 scaled x120/124 to 179.03 s). Header states the
  inclusion rule and named exclusions; the one non-audit beat
  (gitvisual opening headline) is the single sourced `EXTRA_CUES`
  entry — nothing hand-transcribed, nothing guessed.
- `video/out/assembly_v6.srt` (5323 bytes) + `.vtt` (5112 bytes):
  strict-parser PASS (77 cues, monotonic, no overlaps,
  0 < start < end <= 179.03, srt == vtt == generated); sha256
  identical across two runs
  (srt `490568F2…4590`, vtt `AA53BC4D…992CE0`).
- Sampled truth check: 15 cues over all five segments (req >= 12),
  midpoint frames grabbed from `assembly_v6.mp4` and all viewed —
  15/15 cue text matches the readable on-screen text (incl. the
  exclusion spots: source tags, HUD/ticker, hashes, marble labels);
  zero mismatches.
- `video/out/stills_v6/`: 30 stills (one per scene beat) + INDEX.md,
  all 30 viewed; INDEX times independently recomputed from the raw
  audit tables without `build_stills` — 30/30 match exactly.
- One-line `video/README.md` layout pointer for `captions.py` (the
  brief's allowed line; stated here as required).
- `tools/run.sh standard` PASS in the worktree (smoke 411,213;
  extras 1,117,504; aug pool PASS; all controls refused).
- Diff vs base limited to the owned files; `docs/metrics/briefs.jsonl`
  own row appended (wave "wave6", binary-append, +1 line only).
