# Metrics

Half of this hackathon is the measurement of how the methods were handled. Every figure in the record comes from a
named source, and the table below says, for each, whether an agent writes that source and what checks it. An
agent's own estimate of its cost is never the source.

## Where each figure comes from

| figure | source | does an agent write it? | cross-check |
|---|---|---|---|
| tokens (output, input, cached), messages, the model of each | the harness's usage log or the API's, whichever docs/HARNESS.md finds on day 1; failing both, the harness's own counters, transcribed and marked as transcribed | no; a transcription is marked | the sums against the harness's totals |
| tool uses | the transcript | no | |
| minutes per pass | the transcript's stamps, from each prompt of the lead's to the pass's last line | no | |
| commits; the size of a change against its scope ceiling; files outside the ownership list | git | no | |
| gate runs | the runner's record (its JSONL) | no | the log, read against it |
| findings, and their classes | the verifier's report, each finding confirmed or rejected by the lead in the ledger | yes | the integration verifier reads both |
| plants caught | the lead's grading of each report against its key | yes | the key's sha256, recorded before dispatch; the integration verifier |
| brief corrections | each report's "what this brief got wrong", counted, with the lead's acceptance | yes | |
| escalation latency | the ledger's stamps, written by `tools/ledger.sh` from `date` | yes, by a tool | the transcript's stamps |
| conduct, and the lead's slips | the record's lists | yes | git, the filesystem, and the integration verifier |
| Logan's words | the record, verbatim, with dates | yes, as a transcription | the harness's conversation log, where it keeps one |

Six of these rows rest on what agents write (COMPUTED from the table). That is why each has a cross-check, and why the record says which
rows rest on what.

## The tables the record carries

`tools/round_metrics.py` makes them as Markdown, per wave and for the whole hackathon. They take the shape of Logan's
recent records (examples/cases/20-record-skeleton.md):
- **the chain:** each piece of work, its author, each verifier pass as (a), (b), and how often it was sent back;
- **time and tokens:** each agent, its model, its passes, its minutes for the first pass and in all, its tool uses,
  and its output and input tokens;
- **time boxes and scope ceilings,** each against its actual;
- **plants:** caught and missed, per verifier. Plants are graded at the reveal (WORKFLOW.md), so this table is
  made then, in the round's last entry, not in each wave's;
- **brief corrections,** per brief, with those the lead accepted;
- **escalations:** how many there were, and how long each took to answer.

Each table names the kit's version (from MANIFEST.txt) and the first twelve hex digits of the sha256 of each input
it read. The inputs are JSONL files the lead keeps in the project repository's record. `tools/round_metrics.py
--help` gives their fields, and refuses a field it does not know, so that a misspelt one cannot drop a figure.
Every row comes from the sources above, and a transcribed row is marked in the table.

## How Logan's recent waves counted

"Time and tokens (MEASURED, the agents' transcripts: output tokens summed from the last line of each response, tool
uses as distinct ids, minutes from each prompt of the lead's to the pass's last line, a message mid-pass splitting
nothing in the sum" (examples/cases/20-record-skeleton.md, 20b).

Count the same way where the harness allows it. Where it does not, say how you counted, beside the figures.

## Comparing

How many tokens are read depends on a harness's caching. So compare output tokens and minutes across harnesses,
and compare tokens read only within one harness. Logan's earlier waves were other work, in another harness, on other
models, so any comparison with them is qualitative.

## The audit

Logan checks the project repository against fingerprints of cft-fp256's sources (CLEAN-ROOM.md). It is his, it
runs outside this kit, and its result goes in the record with its date.
