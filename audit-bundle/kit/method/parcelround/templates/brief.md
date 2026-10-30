# Parcel brief template

Copy, fill the `<...>`, delete the parenthesised notes. Every section is
here because leaving it out cost something — [METHOD.md](../METHOD.md)
§3 says what.

Each rule ends with the METHOD.md section it comes from, as `(§3)`.
`(own)` marks this template's own guidance, which METHOD.md does not
state, and `(§3, own)` a rule that is both. A tag covers what stands since
the previous tag. Delete the tags with the other parenthesised notes.

Keep it dense. A brief that reads like a contract gets skimmed; one that
reads like a colleague handing over gets followed. (own)

---

You are parcel **`<P2>`** in `<repo>` (a git worktree of
`<absolute path>`, branched from `<branch>` at or after commit `<sha>`;
the dispatch message names the exact commit). (§2) **Check you are on that
commit or after it, in the right repository** — `git log --oneline -1`
and `git remote -v`. If you are not, run `git merge --ff-only <sha>`,
check the SHA again, and if the merge refuses, stop and tell the lead.
(§2, §3) Say what you found in the ledger. (own)

`<If another session works in this repository, say so here, and say never
to switch that checkout's branch.>` (§3)

`<One paragraph on what the project is and what its central invariant is.
The thing that, if broken, makes everything else pointless. Say it in
the terms the tests use.>` (own)

## Start here

1. `<the plan / the round's brief document>`, all of it, then its
   **`<P2>`** section.
2. `<the method or post-mortem doc>` — `<what it will save them>`.
3. `<the header or registry P0 produced>` — `<how a capability is
   unlocked now>`.
4. `<the two or three source locations they will actually be editing,
   and the upstream they are reproducing>`. (§3, own)

## The ledger

`<absolute path outside every worktree>`. Read **every** file there
before you start, again before you design anything touching a file this
brief calls shared or forbidden, and again before you write your report.
Append to `<your-name>.md` only. Its README says what clears the bar.
The ledger is the round's record: it is archived with its timestamps at
the end of the round, and kept. (§4)

`<If the ledger has no README, put its rules in this brief instead, the
three read moments included.>` (§4)

Write each heading's time from `date`, never from memory. (§4)

**When a pause is announced, record where you are** before you stop: what
is committed, what is half done, what you were about to do. On resuming,
do a full read, check your tree before you trust your memory of what you
had done, re-arm your watch, and say where you were interrupted. (§4)

**What cannot wait for a read moment goes to its reader at once, and is
written in the ledger.** A question for me goes by the escalation
channel, not into your own file to wait for my next read: to escalate
without finishing, send it and wait for the answer, rather than holding
it for your final report. (§4)

(Two means carry it, and either is allowed: keep the one this round uses,
and delete the other.) (§4)

- **The file channel.** **Before you start anything else, arm a
  persistent watcher on `<path>/urgent/`** — the README has the loop.
  That directory is for messages that mean "stop and read this", mostly
  from me, and it is how a brief gets corrected after it has been sent.
  The three read moments above are the floor; the watch is what stops you
  spending an hour on a path I already know is wrong. If you notice your
  watch has died while you are still working, re-arm it **and do a full
  read** — a dead watcher and a quiet directory look identical. Where every
  watch expires, the expiry notice is the moment for an agent still working
  to re-arm it and do a full read, not a later noticing. Re-arm from the
  snapshot you kept, and run one watch at a time, on files of its own.
  (§4, own)
- **The runtime's messages.** Write the question in your own file first,
  then message `<the lead>` and wait for the answer. My decisions are in
  the ledger before any message, so a later read of the ledger finds every
  correction, in order. The three read moments above are the floor. A test
  escalation at dispatch must reach me: send `<the test message>` when
  you start. (§4)

## Your job

`<One paragraph. If it needs three, this is two parcels.>` (§3)

## Design first

`<If this parcel's first phase is a design, keep this section; if not,
delete it.>` (§3)

Before you build anything, write your design in your ledger, make it your
report, and stop. The lead approves it, or answers it, before you build.
(§3) Your design must cover `<what the design must cover>`. (§3)

## What reading `<the upstream>` already turned up — verify it, do not trust it

`<Anything you found while writing the brief. Hand over the facts and the
line numbers; it saves an hour each time. Then say explicitly:>` (own)

**A finding you should confirm before relying on it.** `<the claim.>` If
that holds, `<what follows>`. Check it against the source; if I am wrong,
say so in your report and design from what is actually there. (§3, own)

**The trap that would be a silent wrong answer.** `<the thing that
becomes live the moment their change lands, and that nothing currently
handles. There is usually one. Finding it is most of the value of
writing the brief.>` (§3, own) `<Name what will be measured at
verification, so the parcel measures it first.>` (§3)

## Files you own

- `<path>`, **only** `<function>` — `<and why the boundary is there>`.
  (§3)
- A new `<path>`. (§3)
- `<A document that describes this parcel's own code, by section where a
  document is shared.>` (§3)

## Files you must NOT touch

- `<path or function>` — **`<who>` is editing it right now.** (§3)
- `<path>` — `<owner>`. (§3)
- **Integrator-only:** `<the files that state the project's claims>`. If
  one needs a change, say so in your report. (§3, §7, own)
- Anything outside this worktree — in particular `<other live repos>`.
  (own)

Expected small edits outside your files, and **only** these: `<registry
row>`, `<one declaration>`, `<one line in the build file>`, `<one call
in main()>`. (§3)

## Building and testing on this host

`<The tree may need a step before it builds — say it. Then the exact
invocation, not "build it":>` (§3)

```bash
<verbatim, including every non-obvious variable>
```

`<Which gate to run, how long it takes, and "background long runs rather
than polling". Then: "Build only inside your own worktree.">` (own)

`<Say which command is the verdict, where a single target's exit code is
not one.>` (§5)

Test as much as you can quickly, and hand large runs back to me to
monitor. (§7)

Your scratch directory is `<dir>/<your-name>/`; put everything you make
outside your worktree there, and nowhere else. (§3)

## Working rules this repository learned the hard way

- `<the two or three environment traps that have actually cost hours.
  Keep it short and true; a long list gets skimmed.>` (§3)
- **A gate that cannot fail is not a gate.** `<Then the specific control,
  named — not "test it properly". For example: "a do-nothing routine
  must leave the run bit-identical to no routine at all, *and* the
  active case must differ from the inactive one.">` Build it, run it,
  confirm it fails, delete the artifact, and **report both results**. (§5)
  `<Name the control by the property that makes it bite, or run it before
  this brief goes out.>` (§3)
- **If you spawn a subagent, say so in the ledger when you dispatch it.**
  **Do not finish while one is running**; if you must, say in your report
  that its result is outstanding and that you cannot collect it, rather
  than promising to fold it in. (§3)

## What READY means

READY is "a gate, or a stated limit": every property of your work is held
by a gate, or stated as a limit (§5 says how a limit is stated, §6 how it
is tested). (§3)

## Do not

- push, merge, rebase, or commit to `<main>`. (§3) Commit inside your
  worktree only; the integrator merges. (own)
- weaken an assertion to make something pass. (§3)
- `<the specific regression this parcel is most likely to cause>`. (own)
- "fix" anything outside your scope — report it instead. (§3, own)
- `<Write each prohibition as the command to use.>` (§3)

## Report

What you changed file by file, the gate output (**actual lines**), the
controls with their measured numbers, and **anything you found that this
brief got wrong**. (§3, §5, own) If you hit something that makes the
approach unworkable, stop and report that rather than inventing a
different design. (own) If you had to cross a boundary this brief drew,
say so and say why — that is expected and fine; doing it silently is not.
(§3)

End your report with what you did not do. (§3) **Stop your own background
work before you report**: the watches and servers you started. (§3)
`<The stop line: say what to measure before stopping, and that it fires
for value, not only for size.>` (§2, §8) `<If this parcel produces
figures the documents will quote: a figure the documents quote has a
script in the tree.>` (§2)
