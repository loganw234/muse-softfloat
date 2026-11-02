# Checklists

Two, because the failures cluster at two moments: what you get wrong
before dispatch is structural and expensive, and what you get wrong at a
merge is procedural and recoverable. [METHOD.md](../METHOD.md) has the
reasoning behind every line that names a section. (own)

Each line ends with the METHOD.md section it comes from, as `(§2)`.
`(own)` marks this template's own guidance, which METHOD.md does not
state, and `(§2, own)` a line that is both. A tag covers what stands since
the previous tag.

---

## Before dispatch

**The split**

- [ ] A round that exists because another project asked starts by reading
      that project's *code*, not its list of asks. (§1)
- [ ] The plan went past a verifier before the owner approved it: the
      verifier read the draft against the tree, the lead answered its
      findings in a new draft, the verifier re-checked that, and the owner
      was asked after. (§7)
- [ ] Every file each parcel would touch is listed. Anything appearing
      in three or more columns became P0. (§2)
- [ ] P0 landed before any parcel started — pushed, or on the round branch
      every worktree is cut from — is behaviour-preserving, and the full
      suite is green on **both sides** of it. (§2, §7)
- [ ] P0 went past a verifier before any parcel that reads it was
      dispatched; a parcel that reads none of P0's seams need not wait for
      its fixes. (§2)
- [ ] The P0 refactor was aimed at making the shared seam **disappear**,
      not at making it small. (Can the build glob a directory? Can the
      entry points be discovered rather than declared?) (§2)
- [ ] Every shared fact has exactly one owning file. (§1)
- [ ] Every count is derived from the definition, or declared once
      beside the list and checked against it — and the brief says which
      of those two it is. (§1)
- [ ] Registries walk themselves and fail **by name, in both
      directions** — a row no test names, and a test naming a row that
      is gone. Proven with a dummy entry. (§2)
- [ ] A tool's own check that no stage runs is flagged, as a test file
      that no stage runs is. (§2)
- [ ] A trap an earlier round measured is a refusal in this round's seam,
      not a rule in its briefs. (§2)
- [ ] A seam's refusal is in every backend, not only in the one function
      the first parcel will edit. (§2)
- [ ] Each value statement in the plan names the measurement that would
      falsify it. (§2)
- [ ] Each gate prints the build time of every binary it runs. (§5)

**The owner**

- [ ] The owner's decisions are kept as the owner gave them, with their
      dates, and the lead's reading goes beside them, marked as the
      lead's. (§7)
- [ ] The owner's standing rules are carried into the part of the plan
      that says how the round is held. (§7)
- [ ] The owner is asked what they want to see first — a push that
      deploys, a remote branch deleted, a change to how results are
      counted — and the answer is recorded. (§7)

**Each brief**

- [ ] Names its owned files — by function where a file is shared. A
      document that describes the parcel's own code is among them, by
      section where a document is shared. (§3)
- [ ] Names its forbidden files **with the owner of each**, derived from
      the seam's own comments or diffed against them. (§3)
- [ ] Names the documents that state the project's claims among the files
      the parcel must not touch. (§3, §7)
- [ ] Enumerates the small edits outside its files that are expected. (§3)
- [ ] Says how to make the tree buildable, if that takes a step. (§3)
- [ ] Names the base commit "at or after", puts the exact tip in the
      dispatch message, **and says to verify it**: run `git merge --ff-only`
      to it, check the SHA again, and stop and tell the lead if the merge
      refuses. (§2, §3)
- [ ] When another session works in the same repository, says so, and says
      never to switch that checkout's branch. (§3)
- [ ] Carries the host build traps as verbatim commands. (§3)
- [ ] Writes each prohibition as the command to use. (§3)
- [ ] Puts environment facts in the brief, not in the parcel's first
      hour. (§3)
- [ ] Gives each agent its own scratch directory, named in its brief, and
      keeps any secret out of every directory an agent is given. (§3)
- [ ] Names the trap, and what will be measured at verification. (§3)
- [ ] Names its **specific** negative control, not "test it properly" —
      by the property that makes it bite, or run before the brief went
      out — and asks for the control's output. (§3, §5)
- [ ] States what READY means, in the parcel's brief and in its
      verifier's, before the first verifier pass. (§3)
- [ ] Names the divisor a cost model assumes. (§3)
- [ ] Gives the stop line, and what to measure before stopping. (§2)
- [ ] Says what regression this parcel is most likely to cause. (own)
- [ ] Asks what the brief got wrong. (§3)
- [ ] Asks for boundary crossings to be disclosed, and says they are
      expected. (§3)
- [ ] Asks for the report to end with what the parcel did not do, and for
      its own background work to be stopped before it reports. (§3)
- [ ] Says: if you spawn a subagent, say so in the ledger when you
      dispatch it, and do not finish while one is running. (§3)
- [ ] Says that the parcel tests as much as it can quickly, and hands
      large runs back to the lead to monitor. (§7)
- [ ] **Every path named in it exists**, and so does every function it
      names. (A forbidden-files list carried from another project is
      noise at best.) (§3)
- [ ] The worktree is a checkout of the **right repository** — if your
      tooling branches from the session's repo, a parcel aimed at a
      different one cannot use it. (§3)

**The ledger**

- [ ] Exists, outside every worktree, at a path every brief states. (§4)
- [ ] Ignored by version control. (§4)
- [ ] One file per author; the README says so, or, with no README, every
      brief carries the ledger's rules — verifiers' and fixers' briefs as
      much as parcels', the three read moments included. (§4)
- [ ] Read moments are stated **as moments**, not "periodically" — and
      the brief says they are the floor, not the mechanism, whatever
      carries the push. (§4)
- [ ] The stamp rule is in the ledger's template and in every brief,
      fixers' included: write each heading's time from `date`, never from
      memory. (§4)
- [ ] Every brief says that a question for the lead goes by the escalation
      channel, and how to escalate without finishing: send it and wait for
      the answer, rather than holding it for the final report. (§4)
- [ ] Every brief says that when a pause is announced, each agent records
      where it is before it stops. (§4)
- [ ] The escalation channel is chosen, and either means is allowed: the
      file channel, or the runtime's messages. (§4)
- [ ] File channel: `urgent/` exists, and every brief says to arm a
      watcher on it, persistently, and to re-arm plus do a full read if it
      dies while the agent is still working. (§4)
- [ ] File channel: the watcher emits the headline and `For:` line only —
      not the entry. (§4)
- [ ] File channel: urgent messages are one file each, renamed into place,
      never appends to a shared file. (§4)
- [ ] Runtime messages: the ledger entry comes first, then the message; a
      test escalation at dispatch reached the lead; and the lead's record
      says how it learned of each escalation, the test included. (§4)
- [ ] Verifier briefs watch the lead's channel only: a verifier is sent
      only the lead's messages. (§4)
- [ ] Seeded with whatever the lead already knows that a parcel would
      want. (own)
- [ ] **The lead's own watcher is armed with the first dispatch**, and
      stays armed: it watches the escalation channel continuously, and is
      re-armed on expiry. Where the runtime tells the lead of escalations
      instead, the test escalation is that moment. (§4)
- [ ] The lead's watcher is over the whole directory rather than just
      `urgent/` — the lead is the only one who can see a pattern across
      parcels, and the only one who can act on an escalation — and it
      skips the lead's own file. (§4)
- [ ] Whatever replaces that watch, the lead reads every author's file
      before each merge and at each wave boundary. (§4)
- [ ] A re-armed watch keeps the last one's snapshot, and only one watch
      runs at a time, on files of its own. (§4)
- [ ] The lead's decisions go in the ledger first, then in the message.
      (§4)
- [ ] An escalation is verified like any other report before the lead acts
      on it. (§4)
- [ ] Escalating is made safe: an agent whose escalation turns out to be
      its own misreading is not penalised for it. (§4)

---

## At each merge

- [ ] The lead's seam commits and fixes, its merges and its records go
      past a verifier before main moves, from the first commit of the
      round to the last. (§5, §7)
- [ ] The parcel's negative control was run, and its output reported —
      not just described. (§5)
- [ ] The diff stayed inside the ownership boundary; any crossing was
      disclosed and reasoned. (§3)
- [ ] The lead's own tree was checked against what the agent said it did
      not do. (§3)
- [ ] Claims added in comments and commit messages are true. (A sentence
      in the code is something the next person relies on.) (§6)
- [ ] Conflicts were enumerated from **what the VCS says is conflicted**,
      not from what the merge output printed. (§7)
- [ ] No conflict marker survived into the commit, and nothing was
      staged that should not be — check what you staged, not what you
      expected to stage. (§7, own)
- [ ] Each merge was made again by the integration verifier, from its
      parents with `git merge-tree`: every path changed on one side only
      equals that side's, and nothing is lost. (§7)
- [ ] Any subagent the parcel spawned is finished, and its result is
      in hand — an outstanding child is an open item, not a footnote. (§3)
- [ ] A seam test exercises this parcel against an already-merged one. (§7)
- [ ] The merge got the full suite: a staging branch per merge, the suite
      on the build host at the staging commit, and main moving on the
      verdict; or, on a round branch, a gate after each merge into it, and
      main moving only to a tip on which the full suite has run and which
      a verifier has passed. (§7)
- [ ] The full suite was run by the lead, on a tree **nothing was merged
      into while it ran**, and the **log was read** — not the exit code.
      (§7)
- [ ] Auditors and verifiers read a committed SHA, or a worktree the lead
      never edits, not the tree the lead is working in. (§7)
- [ ] The gate budget was checked against the merged diff, after each
      merge (or each batch, where §8's trade is made); where main moved on
      a verdict that says FAIL, the reason is written down. (§7)
- [ ] A seam changed mid-round was checked against every open branch at
      once, not at each merge. (§7)
- [ ] A merge prepared while the verifier worked still waited for the
      verdict. (§7)
- [ ] A failure that is not immediately attributable got a timestamp
      check before it got a diagnosis, and was called neither a defect
      nor a false alarm until a clean re-run said which. (§7)
- [ ] Anything the merge taught the lead went **into the ledger**, for
      the parcels still running. (§4, §8)
- [ ] At a wave boundary, the ledger was folded into the next wave's
      briefs. (§2)
- [ ] A send-back resumed the same agent; for an agent that cannot be
      resumed, it was a newly briefed agent, given the verifier's defects,
      the parcel's final report, its ledger file and its worktree. (§8)
- [ ] A probe that caught a defect is in the suite. (§5)

---

## At the end of the round

- [ ] The ledger's durable findings are folded into the project's own
      records, and the ledger is archived from its working copy, with its
      timestamps, beside the case study (or with the round's other
      records), and kept. (§4)
- [ ] The files that state the project's claims — README, published
      docs, support tables — are swept for anything a parcel made stale.
      (Parcels are forbidden to touch these, so every one of them will
      have reported staleness rather than fixed it.) (§7, own)
- [ ] The docs sweep ran in the lead's idle time during the round, for
      every file no parcel touches, so the end of the round is one section
      rather than a sweep. (§7)
- [ ] The lead's own slips are in the round's record, each written in the
      ledger when it was caught. (§7)
- [ ] Before the agents' worktrees were removed, the lead looked for what
      finished agents left running — watches, servers — and stopped it.
      (§7)
- [ ] The verifiers' side notes got a step of their own. (§6)
- [ ] The summary to the owner carries the cost — per agent, measured as
      the tokens processed, read from each agent's transcript and the
      lead's, with the verifiers' share stated, and the wall clock split
      between the build phase and whatever ran unattended after it. (§7)
- [ ] Each parcel's brief errors are written down somewhere the next
      round's briefs will be built from. (own)
