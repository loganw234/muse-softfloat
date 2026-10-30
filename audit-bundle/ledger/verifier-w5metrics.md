# Ledger: verifier-w5metrics (Wave 5 metrics refresh verification)

## 2026-10-29 verification: NOT READY (4 row/annotation errors in appended data)

Role: verifier-w5metrics. Copy `worktrees/verify5-metrics` (detached HEAD
`091c890`, parent `5142594`; read-only, unmodified). Full record:
`scratch/verifier-w5metrics/report.md` (first line NOT READY) with per-probe
scripts (Git Bash, MSF_PYTHON pinned to the workspace `.venv`, ulimit
ceilings, streamed logs).

Measured (every brief probe run, no sampling of the method):

- Append-only PASS: all four metrics prefixes byte-identical to the parent
  blobs; rows 39->93 / 39->94 / 13->20 / 27->30; 119 insertions, 0 deletions.
- Extractor selftest 8/0 (from the copy). Resample over waves 0/4/5 plus
  verifiers/studies/multi-session folds: 7/8 agents exact on every
  token/message/tool-use number, model, span, and note sha.
- All 14 author/fixer commits exist, are ancestors of HEAD, are landing
  merges' second parents (twiddledoc pass 1 per parcel rule 5), and are
  cited in RECORD and/or a parcel ledger.
- All 26 appended verifier verdicts match their ledger + full reports; a/b
  totals match (explicit tags where given; kit-rule mapping otherwise).
  sent_back true sourced for the sf0 chain, verifier-readme (`d87c87c`),
  verifier-sf2 (`f3eea91`), verifier-w5twiddledoc (`a41f026`); all falses
  consistent (tips predate sessions; landing merges content-empty).
- Escalations: all 7 sent stamps sourced (urgent files / parcel results
  entries); alg1/alg2 answered = commit dates with confirming messages; 4
  tier2 answered omitted per the rule.
- Briefs: trigspike + metrics rows fully sourced (bases exist, time boxes
  from briefs). Reconciliation re-derived in numbers: fold-vs-recount delta
  decomposes exactly (lead-main continuation + recount-probe frozen error −
  extractor slip); study tree = work+internal recounts combined, exact;
  span bridge itemised per session (645 msgs / 380,917 out /
  106,378,696 in); 38.6M double-count confirmed (frozen sums match the
  study's missing block to the token; sessions present under near-ids).
- Kit `round_metrics.py` selftest 43/0; tables all-waves + wave4 + wave5 on
  the copy's files all exit 0. `tools/run.sh smoke` PASS in 26s, exit 0, on
  a byte-identical isolated code tree outside the copy.

Findings (all in the appended rows, none edited per append-only):

- F1: appended usage verifier-w5exp2 model `muse-wonder-full-1.0`, transcripts
  (both sessions) `muse-spark-1.3` — numbers exact, label wrong.
- F2: appended usage verifier-extractor `output_tokens` 84,350 vs transcript
  34,350 (+50,000; all else exact). Parcel results-entry total matches the
  corrected sum, not the committed rows.
- F3: appended briefs parcel-w5exp2 `base` 5a80126… nonexistent; intended
  4a80126… (hypot merge). Kit table echoes "fatal: bad object 5a80126…".
- F4: appended passes verifier-w5aug `sent_back=true` with no post-verdict
  revision (pre-verdict tip merged unchanged 24 s after the verdict); the
  identical exp2 shape is false. Breaks the planted-copy-NOT-READY rule.
- F5–F8 (minor): w5exp2 pass-note/span mismatch; w5aug 6th count (5th (a))
  untagged; study-id garbling is 4/1/2 digits not one each; study-tree
  "diff 0" needs the work+internal qualifier (internal usage quantified).

Not reconstructed / unresolved: video-final escalation `answered` receipt
source lives in off-limits `ledger/lead.md` (U1); a/b splits for untagged
reports are the natural kit-rule reading, stated per row in the report.
Resample covered 8 agents directly + all 93 per-session from row notes.

Believed: the numbers underneath are sound (fold sums, spans, verdicts,
reconciliation all re-derive); the four errors above are confined to
annotation/label/base fields, fixable by single-field corrections on top
of the frozen prefixes.

For: lead.
