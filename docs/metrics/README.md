# Metrics inputs

One JSON object per line. The tables in `docs/RECORD.md` are made from
these files by the kit's `round_metrics.py` (kept frozen outside this
repository); its module docstring is the schema of record, and a field
it does not list is refused, so a misspelt field cannot drop a figure.
Times are ISO 8601 with an offset, or the ledger's own stamp form.

| file | one row per | key fields (see the kit tool for the full schema) |
|---|---|---|
| `usage.jsonl` | agent (tokens) | wave, agent, model, output_tokens, input_tokens, source |
| `passes.jsonl` | pass of an agent | wave, agent, role, work, pass, start, end, tool_uses, source; authors add commit, verifiers add a, b, verdict, sent_back |
| `briefs.jsonl` | brief | wave, work, author, base, time_box_min, ceiling_lines |
| `corrections.jsonl` | "what this brief got wrong" report | wave, brief, by, at, text, accepted |
| `escalations.jsonl` | escalation | wave, from, to, sent, means, test |
| `plants.jsonl` | plant, written at the reveal | wave, verifier, work, key_sha256, plant, shape, grade, graded_by |
| `fetches.jsonl` | fetched third-party archive (project record, not a round_metrics input) | name, url, version, archive_sha256, licence, licence_sha256, fetched, by |

`usage.jsonl` and `passes.jsonl` rows are produced by
`tools/extract_session_metrics.py` from session transcripts with an
explicit cutoff, annotated by hand from the ledger where authorship
and verdicts are concerned. The briefs/corrections/escalations/plants
shapes were added in P0 (SF-0 Section 6 item 8) so Wave 1 events are
recorded as they happen; rows begin with Wave 1. Fetched trees live in
scratch outside this repository (SF-0 Section 4.5); only their hashes
land here.
