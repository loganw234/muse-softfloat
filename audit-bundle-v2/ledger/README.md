# The round ledger

The round's record. Ignored by version control while it runs (it is not in
any repository); at the end of the round the lead folds anything durable
into the project's own records (`muse-softfloat/docs/RECORD.md`), then
archives this directory from its working copy, with its timestamps, with the
round's other records, and keeps it: neither the archive nor the working
copy is deleted at the round's end.

It exists because **a brief is written once, at dispatch, and cannot be
updated.** Anything learned while the parcels are running otherwise reaches
them never — it arrives in a final report, after the sibling who needed it
has finished.

## How to use it

This directory is **outside every worktree**. Reach it by the path your
brief states (Windows form and the Git Bash `/c/...` form name the same
directory). In entries and reports, call it `<ledger>/`.

**One file per author, append only.** Yours is `<your-name>.md` —
`P1.md`, `verifier-P2.md`, `lead.md`. Read every file in the directory (a
verifier reads the lead's file first, and a parcel's only once it has formed
its own view); write only to your own. Never edit anyone else's, and never
edit an entry you already wrote: append a correction underneath instead.

**Write with the kit's `tools/ledger.sh`** (Git Bash; it stamps from `date`,
never from memory, and refuses a body that is not in the entry format):

    bash <kit>/tools/ledger.sh append <ledger> <your-name> "<one-line headline>" < bodyfile
    bash <kit>/tools/ledger.sh urgent <ledger> <your-name> <slug> "<headline>" < bodyfile

Write the body to a file first (heredocs lose backslashes on this host).
The tool only appends at the end; a "see `<time>`" line linking a correction
from the entry it corrects is written by hand, and is an append, not an edit.

**Read at three moments** — the floor, not the mechanism:

1. once before starting anything;
2. again before designing anything that touches a file your brief called
   shared or forbidden;
3. again before writing your final report.

**Write when this clears the bar:** *would it have changed another parcel's
work, or the lead's?* Three things do: environment and setup facts; a brief
that turned out wrong (the moment you find it, not in your report); a finding
about shared code. **Do not write** progress or plans. A ledger full of
status is one nobody reads.

**When a pause is announced, record where you are** before you stop: what is
committed, what is half done, what you were about to do. On resuming, do a
full read, check your tree before you trust your memory, re-arm your watch,
and say where you were interrupted.

**Mark what you measured.** Every entry says which claims were *measured*
and which are *believed*. A background job that writes here stamps at write
time and says what it describes.

## Escalation: one rule, whatever carries it

**What cannot wait for a read moment goes to its reader at once, and is
written in the ledger first.** This round's means: **the file channel** —
`urgent/` below — because a child agent has no mid-run message to the lead
in this harness; the harness's own messages carry lead→agent corrections
*in addition*, always after the ledger entry exists. On either means:

- the ledger entry comes first, then the message;
- a verifier is sent only the lead's messages, as it watches only the lead's
  channel (lead's file + urgent messages from the lead);
- the three read moments stay the floor;
- **a test escalation at dispatch must reach the lead**: your brief names
  the test message; send it when you start. The lead's record says how it
  learned of each escalation, tests included.

**Verifiers watch the lead's channel only.** Parcel self-reports reach a
verifier only after it has formed its own view.

**The lead watches too, and watches more**: the whole directory, skipping
`lead.md`, armed with the first dispatch and re-armed on expiry; and it
reads every author's file before each merge and at each wave boundary
whatever the watch showed.

## `urgent/` — the push channel

The three moments are a polling schedule, and its latency is its interval.
**Arm a watcher on `urgent/` before you start anything**, persistently,
inline (never from a script file — the watcher is the one filename everyone
collides on):

```bash
U=<ledger>/urgent; mkdir -p "$U"
seen=$(ls "$U" 2>/dev/null | sort)
while true; do
  cur=$(ls "$U" 2>/dev/null | sort)
  comm -13 <(echo "$seen") <(echo "$cur") | while read -r f; do
    head -1 "$U/$f"; grep -m1 '^For:' "$U/$f" 2>/dev/null || true
  done
  seen=$cur; sleep 20
done
```

In this harness the watcher runs as a Monitor whose lines wake you; watches
expire (30 min ceiling) — the expiry notice is the moment to re-arm **and do
a full read**. A dead watcher looks exactly like a quiet directory. Run one
watch at a time, re-arm from your kept snapshot.

**The bar for writing here is "stop what you are doing and read this"** —
mostly the lead's: a brief that turned out wrong, a merge that invalidated
an assumption. Escalating *to* the lead is what this channel is equally for:
a wrong brief, a wrong worktree, a load-bearing falsehood — here, not in
your final report. An escalation that turns out to be your own misreading
costs nothing and is never held against you.

**One file per message, renamed into place** — `ledger.sh urgent` does this;
never write an urgent file directly. Name: `<who>-<short-slug>.md`. First
line is the headline; include a `For:` line — those two are all the watcher
prints, so they are what someone decides on.

## Entry format

    ## <date time> - <one-line headline>

    Measured: ...
    Believed: ...
    For: <who this is likely to matter to, or "anyone">
