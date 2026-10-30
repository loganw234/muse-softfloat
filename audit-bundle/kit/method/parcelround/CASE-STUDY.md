# One round, measured

The numbers behind [METHOD.md](METHOD.md). A method doc that cannot say
what it caught is an opinion.

## The setting

A ~15,000-line C project: a numerical integrator re-implemented so that
every floating-point operation goes through a software library, letting
the same code run at 64-, 128- and 256-bit precision. At 64-bit it must
reproduce the original **bit for bit** — every gate asserts that, and
"close enough" is never an acceptable answer anywhere in the suite.

That exactness matters to the case study in one direction only: it makes
failures unambiguous. It does not make the method precision-specific.
Any project with a suite you trust gets the same shape of result.

An earlier round on the same codebase had produced the canonical
failure — four parcels, four green gates, a feature that did not work,
because the seam between two of them belonged to nobody. This round was
designed against that.

## The shape of the round

One **P0** by the lead, then five **parcels** in parallel worktrees, two
**verifiers**, and one follow-up parcel spawned from a verifier's
findings. The lead merged serially and ran the full suite after each
merge.

P0 was two refactors: a capability list that was stated in four places
became one table both callers walk, and a 718-line single-`main()` test
file became a file per topic plus a header saying how to add one. After
it, unlocking a capability was deleting one row, and a parcel's only
shared-file edits were four one-line additions.

## What the system caught

**Twelve brief errors, from all five parcels.** Every single parcel
corrected its brief. The most consequential: the lead had described a
callback mechanism as an *addition* of an exactly-representable value,
so the total would be "wide arithmetic plus an exact addend, correctly
rounded". It is a **replacement** — the callback returns only the
narrow total and there is no addend to recover. The parcel worked that
out, proved the alternative was not bit-exact with a two-line
counterexample, and shipped replacement narrowed by a bit comparison.
The feature's cost at wide precision is materially different from what
the brief said, and nothing else would have surfaced that.

Others included: a setting the lead thought reached one function
reaching two; a flag the lead thought was live being overwritten by the
caller on every step, so refusing it had been refusing something
*correct*; and a piece of state the lead had catalogued as dead turning
out to be read before it was written.

**Seven gates that could not fail** — the first four found by the parcel
that wrote the code each gate was meant to hold down, unprompted:

1. A control that disabled a newly written branch left **every case
   passing**. The parcel swept for a configuration that discriminates,
   found one, added it, and the control then failed on exactly the
   affected mode.
2. A case exercising a re-read of stale data triggered on **step 1**,
   when the data being re-read was still all zeros.
3. A control was observed through a *rounded view* of a wider state. The
   underlying difference was real but re-converged below the view's last
   bit, so the control matched at two of three precisions and **could
   not fail**. Fixed by hashing the wide bytes into every dump.
4. With massless particles, the feature under test was **bit-inert** —
   every removed term contributed exactly zero and ordering was
   preserved, so the obvious test case would have passed with **nothing
   implemented**. Every divergence control was moved onto massive
   particles.

**A fifth, found by a verifier:** a `memcmp` that decides whether a
value keeps its wide precision can be swapped for `!=` and **pass the
entire suite** while silently breaking signed zero.

**A sixth, in shared scaffolding:** the helper every refusal case in the
project used asserted "the integration stopped and the clock did not
move" — and a defect could satisfy that while leaving the particles at
intermediate values, because the code under test had just set the clock
itself.

**And a seventh, in a worked example:** it printed what the library
answered instead of asserting what it should answer, so after a
capability landed it shipped the line `-> NOT REFUSED, which is a bug`
about behaviour that was correct. The project's own published output
accused its library of a defect, and the build exited 0.

**Two verifiers, both productive.** Each confirmed every item on the
list it was given, and each found things that were not on it:

- the first found that a callback writing any field other than the one
  the port read back was **silently discarded** where the original would
  have used it — through three separate channels, 15 of 21 values
  differing in each — plus four places where correct code had nothing
  holding it down;
- the second disproved a claim written in the code (*"byte for byte what
  we wrote before"*: measured 10,590 → 10,783 bytes), confirmed an
  upstream defect in the dependency and found a **new consequence** of
  it — that mixing builds across one commit inside one archive produces
  an unloadable file in one direction — and caught a hash seed
  mislabelled as a standard one **and hand-copied into a second file,
  three hours after the project wrote down its rule against
  transcribed constants**.

**Two previously unrecorded defects**, one of them upstream in a
third-party dependency, reproduced minimally rather than inferred.

## The worked example: a defect that lived in the gap between two parcels

The clearest thing this round produced is one defect traced end to end,
because it exercises every claim the method makes.

**Two parcels, both correct.** One added user-supplied forces, called at
every substage of the integrator. Another implemented two additional
step-size criteria. Each shipped gated, each passed the full suite, and
a verifier went over the first one and confirmed it.

**The warning existed and arrived too late.** The forces parcel ended
its report with a paragraph headed *"for P3"*: the upstream step
controller reads a velocity array that, when a velocity-dependent force
is registered, holds *predicted* values rather than the step's starting
ones. That is exactly what the criteria parcel needed to know. It
arrived hours after that parcel had started — and is the specific
incident the ledger was invented for.

**The gates could not see it.** The forces file pinned the criterion to
the default. The criteria file registered no force. Neither brief
mentioned the other. **The combination was untested by construction**,
and no amount of care inside either parcel would have changed that.

**An audit found the mechanism and honestly under-called it.** A
documentation auditor traced the divergence precisely — the port kept
the predicted velocities in one buffer and the controller read another
— then did the work to bound the severity: the value feeds only a skip
predicate, `|v²·dt²/x²| < 1e-16`, never the error estimate. It scanned
**260 configurations tuned to sit on that threshold** and found no flip,
and reported the divergence as *latent rather than demonstrated*. That
was the honest call on the evidence it had.

**The seam test found the instance.** Written by the lead, because it
belonged to no parcel, crossing all four criteria with a
velocity-dependent force on three problems. Two-body: identical at every
criterion. Five-body: identical. **Three-body close encounter under the
GLOBAL criterion: 21 of 21 values differing at ~1e-4 relative** — not a
last-bit difference but a trajectory divergence, meaning one flipped
boolean on one step sent the two runs down different step sequences and
they never rejoined. The audit's tuned two-body scan could not reach
that state; a close encounter reaches it immediately.

**The fix was three lines**, because the port already had the right
numbers in a buffer and was reading the wrong one.

### What each part of the method contributed

| | |
|---|---|
| Parcel briefs with owned files | kept two parallel changes from colliding — and, by drawing the boundary, created the gap |
| *"Tell me what the brief got wrong"* | produced the warning at all |
| The ledger | would have delivered it in minutes instead of hours; it did not exist yet |
| A verifier | confirmed the forces parcel and did not look at the crossing, because it was not in that parcel either |
| An independent audit | found the mechanism, and was right to call it latent |
| **The seam test** | found the instance |
| Named negative controls | proved the seam test was exercising the combination rather than comparing two runs that did not differ |

**The generalisable claim.** Splitting work creates a gap exactly where
the split is, and the gap is invisible to everyone working inside it.
Every participant here did careful work; the defect was in the one place
none of them owned. That is not a failure of the parcels — it is the
structural cost of parcelling, and the only defence is for someone to
own the intersections deliberately and test them on purpose.

A seam test is cheap. This one is a hundred lines and runs in seconds.
It found a real bit-identity failure that five parcels, two verifiers, a
follow-up parcel and 211 assertions had all passed over.

## The channel's first live use, which ran backwards

The ledger was added at the end of the round and its push channel a
little after that, both designed around the lead correcting a brief
after dispatch. The first message through it went the other way.

A parcel was dispatched to audit a **second repository**, and its
worktree was created from the session's repository instead — because
that is what the tooling does, and the lead had not thought about it.
The agent got a checkout of the wrong project and a brief full of paths
that did not exist in it. Worse, the brief told it to stay out of a
repository its own worktree was inside of, where a sibling was working.

What it did is the shape to want:

- **measured the mismatch four independent ways** before claiming it —
  the `.git` pointer, the remote URL, the commit at the tip against the
  one the brief named, and the presence-or-absence of every path the
  brief listed, in both candidate repositories;
- **escalated to `urgent/` rather than to its final report**, which
  would have arrived two hours later;
- **worked out which half of the brief was wrong** — the assignment was
  clearly the second repository, the checkout was broken — and picked
  the reading that keeps the work useful;
- **made no edits anywhere**, in particular declining to write into the
  target repository's live main checkout, which was not its to touch;
- **converted everything it was licensed to fix into reported
  corrections**, so the audit still happens and comes back as a patch
  list;
- and **flagged that a re-dispatch should not assume the commit** the
  brief named without checking.

The lead verified all of it in one command before acting, which is the
same habit as not merging on the strength of a report: an escalation is
a report too.

Two things went into the method from this. The lead needs its own
watcher, over the whole directory rather than just `urgent/` — and
needs it *more* than the agents do, because agents have three read
moments built into their workflow and the lead has none. And a
dispatch checklist needs a line about the worktree being a checkout of
the right repository, which is not a typo class of error but a
structural one: if the tooling branches from the session's repo, a
parcel aimed elsewhere cannot use that mechanism at all.

Without the push channel this would have surfaced in a final report,
after the audit had either wasted its time or quietly audited the wrong
project. The pull-only ledger would not have surfaced it either, because
the person who needed to read it was the one with no reason to look.

## What the lead got wrong

Worth recording, because four of the doc's rules came from these.

1. **Committed a merge with an unresolved conflict in it**, plus eight
   agent worktrees as embedded repositories — by resolving the two files
   the merge message named, then staging everything without checking
   what the VCS still considered conflicted.
2. **Merged while a suite was running**, reasoning that the suite's
   binaries were already built so source edits could not reach it. True
   of the compiled gates, false of the scripted ones: the run read a
   newly merged script off disk and drove it against the old binary,
   producing three failures that were entirely self-inflicted. Diagnosed
   by comparing the binary's build time against the script's mtime.
3. **Carried a forbidden-files list across from a sibling repository**
   without checking. Four of the six files named "never edit" did not
   exist in the repository being worked on.
4. **Dispatched a parcel into a worktree of the wrong repository**, and
   wrote it a brief that told it to stay out of the tree it was
   standing in. See above.

## What it cost

- **Every merge conflicted**, in the same four places every time, and
  every one was trivial — a P0 outcome, not luck.
- **Suite time dominated.** ~25 minutes per run, serial. Four merges is
  most of a working day of waiting, and it is the thing nobody budgets.
- **Three parcels independently solved the same setup problem**, because
  there was no channel between them. That is what the ledger is for, and
  it was added at the end of this round rather than the start.

## What the numbers say

The parcels were fine. Agents given a clear boundary and a named control
did careful work, found their own vacuous gates, and disclosed every
boundary crossing unprompted.

What the system surfaced, repeatedly and fast, is that **the lead's
model of the code was wrong** — twelve times, and in three of five
places where the lead drew a seam by function. That is the return on the
method: not that it makes agents trustworthy, but that it makes the
plan's wrongness visible in hours instead of at integration.

The single cheapest line in the whole system asks for exactly that.
