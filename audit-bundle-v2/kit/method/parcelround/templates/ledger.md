# Ledger template

Drop this in as the ledger directory's own `README.md`, with the two
`<...>` filled. It is the text that ran, plus what METHOD.md has added
since - [METHOD.md](../METHOD.md) section 4 says why the ledger exists.
(own)

The ledger's rules reach every agent in one of two ways: as this README,
or as the same rules in every brief. Either is allowed, and the second
only if every brief carries them, the three read moments included,
verifiers' and fixers' briefs as much as parcels'. (§4)

Each rule ends with the METHOD.md section it comes from, as `(§4)`.
`(own)` marks this template's own guidance, which METHOD.md does not
state, and `(§4, own)` a rule that is both. A tag covers what stands
since the previous tag. Delete the tags with the other parenthesised
notes.

---

# The round ledger

The round's record. Ignored by version control while it runs; at the end
of the round the lead folds anything durable into `<the project's own
records>`, then archives this directory from its working copy, with its
timestamps, beside the case study (or with the round's other records,
where there is none), and keeps it: neither the archive nor the working
copy is deleted at the round's end. (§4)

It exists because **a brief is written once, at dispatch, and cannot be
updated.** Anything learned while the parcels are running otherwise
reaches them never — it arrives in a final report, after the sibling who
needed it has finished. (§4)

## How to use it

This directory is **outside every worktree**. Agents work in separate
checkouts and cannot see each other's files, so reach this by its
absolute path: (§4)

    <absolute path to the ledger directory>

**One file per author, append only.** Yours is `<your-name>.md` —
`P1.md`, `verifier-P2.md`, `lead.md`. Read every file in the directory (a
verifier reads the lead's file first, and a parcel's only once it has
formed its own view); write only to your own. Never edit anyone else's,
and never edit an entry you already wrote: append a correction underneath
instead. (§4, own)

**Link a correction from the entry it corrects**: an appended "see
`<time>`" line beneath the old entry is an append, not an edit. A number a
sibling might reuse is restated in the form the sibling would search for.
(§4)

**Write each heading's time from `date`, never from memory.** Write the
entry with a placeholder and let the append substitute the clock. (§4)

**Read at three moments** — the floor, not the mechanism; the escalation
channel below is the rest of it:

1. once before starting anything;
2. again before designing anything that touches a file your brief
   called shared or forbidden;
3. again before writing your final report.

They stay the floor whatever carries the push, and whatever carries these
rules. (§4)

**Write when this clears the bar:** *would it have changed another
parcel's work, or the lead's?* Three things do.

1. **Environment and setup** — what the tree needs before it builds,
   what your base commit actually turned out to be, a tool that is not
   where it looks.
2. **A brief that turned out wrong** — the moment you find it, not in
   your report. A sibling may be acting on the same wrong premise right
   now.
3. **A finding about shared code** — behaviour in a function another
   parcel owns, an upstream defect, a constraint that will bind someone
   else. (§4, own)

**Do not write** progress, plans, or anything only your own parcel cares
about. A ledger full of status is one nobody reads. (§4, own)

**When a pause is announced, each agent records where it is** before it
stops: what is committed, what is half done, what it was about to do. A
pause is the exception to "progress and plans do not" above, because the
entry is a resume note for its writer as much as for the lead. On
resuming, do a full read, check your tree before you trust your memory of
what you had done, re-arm your watch, and say where you were interrupted.
(§4)

**Mark what you measured.** Every entry says which claims were
*measured* and which are *believed*, to the same standard as your
report. Other agents build on these, and an unverified claim propagates
faster than a verified one. (§4, own)

**A background job that writes to the ledger stamps at write and says
what it describes.** (§4)

## Escalation: one rule, whatever carries it

**What cannot wait for a read moment goes to its reader at once, and is
written in the ledger.** That is the lead's correction of a brief after
dispatch, and a parcel's question or finding that only the lead can act
on. A parcel's question goes this way, not into its own file to wait for
the lead's next read: send it and wait for the answer, rather than
holding it for your final report. (§4)

Two means carry it, and either is allowed: the file channel, a file in
`urgent/` and a watch on it, described next; or the runtime's own messages
between agents, with the question written in the sender's own file first.
(§4) On either means:

- **The ledger entry comes first**, then the message: the lead's
  decisions go in the ledger first, and an agent's question in its own
  file. The file channel meets this by being a file in the ledger. (§4)
- **A verifier is sent only the lead's messages**, as it watches only the
  lead's channel. (§4)
- **The three read moments stay the floor**, whatever carries the push.
  (§4)
- **Where the lead learns of escalations from the runtime instead of from
  a watch, the channel is watched to work.** A test escalation at
  dispatch must reach the lead, and the lead's record says how it learned
  of each escalation, the test included. (§4)

**Verifiers watch the lead's channel only.** A verifier is paid for
independence, and a stream of "the parcel says this is fine" is exactly
what erodes it. Environment facts and lead corrections should reach it;
parcel self-reports should not, until it has formed its own view. (§4)

**The lead watches too, and watches more.** The lead arms its watch with
the first dispatch, and keeps it armed: it watches the escalation channel
continuously, and re-arms on expiry. Where the runtime tells the lead of
escalations instead of a watch, the same moment is the test escalation.
(§4)

**The lead watches the whole directory**, not just `urgent/` — only the
lead can see a pattern across parcels. Its watcher skips the lead's own
file. Whatever replaces that watch, the lead reads every author's file
before each merge and at each wave boundary. (§4)

## `urgent/` — the push channel

This section is the file channel, one of the two means above. (§4) (Delete
it if the round uses the runtime's messages only.)

The three moments above are a **polling schedule**, and its latency is
its interval. A correction posted ten minutes after you start sits
unread until your next read moment. `urgent/` is the way past that. (§4,
own)

**Arm a watcher on it before you start anything**, persistently, so a
new message becomes a notification rather than something you find later:
(§4, own)

```bash
U=<ledger path>/urgent; mkdir -p "$U"
seen=$(ls "$U" 2>/dev/null | sort)
while true; do
  cur=$(ls "$U" 2>/dev/null | sort)
  comm -13 <(echo "$seen") <(echo "$cur") | while read -r f; do
    head -1 "$U/$f"; grep -m1 '^For:' "$U/$f" 2>/dev/null || true
  done
  seen=$cur; sleep 20
done
```

**Arm it inline rather than from a script file.** Where agents in a round
share a scratch directory (§3 gives each its own), the watcher is the one
script everyone writes, so it is the one filename everyone collides on —
that happened on this mechanism's first use. If you must use a file, put
your own name in it. (§4)

**Re-arm from the snapshot you kept, and run one watch at a time, on
files of its own.** The shape above takes its snapshot when it starts, so
it does not announce what arrived while no watch ran; the full read is
what finds that. (§4)

**The watch is not the mechanism, it is latency reduction.** A watcher
that has died — timed out, killed, stopped for volume — looks exactly
like a directory with nothing new in it. If you notice yours is gone
while you are still working, re-arm it **and do a full read**, because
you cannot tell how long it was dead. Where every watch expires, the
expiry notice is the moment for an agent still working to re-arm it and do
a full read, not a later noticing. (§4)

**The bar for writing here is "stop what you are doing and read this",**
and it is mostly the lead's: a brief that turned out wrong, a merge that
invalidated an assumption, a thing you were told to delete that turns
out to be load bearing. Everything else goes in your own file. A channel
that fires for things that could have waited is one people learn to
ignore. (§4, own)

**One file per message, renamed into place.** Compose it somewhere else
and `mv` it in, so a watcher can never catch a half-written file, and so
a new message is an unambiguous event: (§4)

    <who>-<short-slug>.md

First line is the headline. Include a `For:` line — the watcher prints
those two and nothing else, so they are what someone decides on. (§4)

**Escalating to the lead is what this channel is *for* as much as the
other direction**: if your brief is wrong, if you are in the wrong place,
if something you were told is load bearing turns out not to be, put it
here rather than in your final report. An escalation that turns out to be
your own misreading costs nothing; one that waits two hours for a report
costs whatever the sibling did in the meantime. (§4, own)

## Entry format (own)

    ## <date time> — <one-line headline>

    Measured: ...
    Believed: ...
    For: <who this is likely to matter to, or "anyone">

Write `<date time>` from `date`, never from memory. (§4)
