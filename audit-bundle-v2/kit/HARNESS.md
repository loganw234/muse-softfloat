# The harness, mapped (a template)

**Fill a copy of this on day 1, with Logan,** as docs/HARNESS.md in the project repository. This file stays as it
is: the kit is frozen, and a changed file fails the gate's check 1.

The methods were written in another harness. Each row names a mechanism they assume, the fallback the method already
has for a harness without it, and a blank for yours. The filled copy is part of the record, because which fallbacks
were used is one of the results.

| mechanism the methods assume | where the method says so | its fallback | this harness: how, or "none" | used? |
|---|---|---|---|---|
| a separate checkout (worktree) for each agent | ParcelRound METHOD.md, sections 2 and 3 | `git worktree add`, by the lead, one for each agent, outside each other | | |
| messages between agents | section 4, "Escalation: one rule, whatever carries it" | the file channel: `urgent/` and a watcher | | |
| a background watch whose output wakes an agent | section 4, "Reading it is a polling schedule; add a push channel" | the three read moments, which are the floor anyway | | |
| resuming an agent with its context | section 8, "A send-back needs no re-brief" | a newly briefed agent, given the verifier's findings, the parcel's report, its ledger file and its worktree | | |
| agents that start agents of their own | section 3, "A parcel's own subagents are invisible to you" | every parcel's brief forbids it, or asks for each in the ledger | | |
| a transcript of each agent: its tool uses and its stamps | METRICS.md | the ledger's stamps, marked as the ledger's | | |
| a usage log: tokens and the model of each message | METRICS.md | the harness's counters, transcribed and marked | | |
| a network policy that can keep cft-fp256 out | CLEAN-ROOM.md | the rule, and disclosure | | |
| the board's debug link | BOARD.md | the lead runs every board job itself | | |
| a git remote, and who may push | OWNER.md, rule 7 | local commits only, until Logan's word | | |
| what the harness puts in an agent's context by itself: agent notes, project instructions, the files of a directory it was given | CLEAN-ROOM.md, "A copy on the machine" | no clone of cft-fp256 in, under or beside any directory the harness is given | | |
| whether an agent can read another agent's scratch directory, the lead's included | ParcelRound METHOD.md, section 3; WORKFLOW.md, the planted-fault protocol | the instruction, and disclosure: the record says the blinding rests on them | | |
| the clock each agent reads | the ledger's README, "Write each heading's time from `date`" | `tools/ledger.sh`, which reads it | | |
| how long a session lasts, and what ends one | section 4, "When a pause is announced" | resume notes in the ledger | | |

**Where the agents run:**

**Where the ledger is:**

**Each agent's scratch directory:**

**The usage log's format,** and the adapter that reads it into `round_metrics.py`'s input:
