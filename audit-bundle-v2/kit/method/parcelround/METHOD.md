# The method

Every rule here is here because something broke without it, or because
its practice caught a defect before it shipped, or, where the rule says
so, because it rests on practice that held, on a cost, or on the owner's
word.
Where a rule cites an incident, that is evidence rather than colour; the
incidents are written up in [CASE-STUDY.md](CASE-STUDY.md) (round 1)
and [CASE-STUDY-2.md](CASE-STUDY-2.md) (round 2, whose timestamps the
citations below use).

**Citations.** Rounds 3 to 6 are cited by name:
- `[CASE-STUDY-3, 15:09]` is a time in that case study, or in its round's
  ledger archived beside it;
- `[CASE-STUDY-4, obs 10]` is a numbered observation;
- `[CASE-STUDY-3, §5]` is a section mark.

A bare time is round 2's. An incident recorded outside the case studies is
cited by a link to its record.

**Adoption.** What this file has adopted from each case study, and when, is in
[ADOPTION.md](ADOPTION.md). `python tools/check_method.py` checks the citations
here, in these forms, and the adoption record; its docstring states what it
cannot see, and `--control` shows that each of its checks can fail.

**This file is the canonical copy.** It was extracted from a working
copy that still lives in the project it was developed on, as that
round's own documentation. Two copies of one document is precisely
what section 1 tells you not to have; the honest position is that the
duplication is known, this one wins, and the other is scheduled to
become a pointer once this repository has somewhere to point at.

Vocabulary: the **lead** is you, the session that plans, briefs, merges
and verifies. A **parcel** is one agent with one brief. A **verifier**
is an agent whose only job is to disconfirm a parcel's work. A **round**
is one pass of all of it.

---

## 1. The one failure mode

Not "an agent does bad work". Agents mostly do the work in front of
them. The failure is that **the work between the parcels belongs to
nobody**, and it is invisible because every parcel's own gate is green.

The canonical instance: four parcels built one feature, every gate
passed, and the feature did not work. The tests for one half drove a
stand-in for the other half — a stub whose own header said to re-point
the tests once the real thing landed. It landed. Nobody did. So the
whole path had never once been executed, and the load routine happily
reported "restored exactly" for a restore that had not happened, because
it validated the *file* rather than what reached memory.

Nobody was wrong. The seam belonged to no parcel.

### Two rules that prevent most of it

**Exactly one file owns each shared fact; everyone else includes it.**
When the same fact is stated twice, the copies drift — not might, do. In
the instance above a single count was written by hand in four places and
a name list in a fifth; growing the list broke all six in different
ways, including a gate that passed while printing "only 50 of 48".

**Derive counts and name lists; never transcribe them.** There are two
grades of this and it is worth being precise, because a brief that
conflates them is wrong about the thing it is protecting.

- **Derived**: the consumer reads the definition, so there is one value
  and no way to disagree — a test that greps the header for a `#define`.
- **Declared once and checked**: the count is still a literal, but it
  sits beside the list it counts and a selftest asserts it against the
  list, so a disagreement surfaces on the next run.

Ask for the first where it is possible and the second where it is not,
and do not call the second the first.

The payoff is immediate and visible. When a constant moved from one
header to another, the test that *reads* it stopped with `no #define
CFT_MAX_BODIES in src/ias15_cft.c`, naming the file it could not find it
in. A transcribed copy would have gone on silently testing a stale
number. **A test that breaks when you move a definition is working.**

### Read the requester's code, not its ask list

A round that exists because another project asked for something starts
by reading that project's *code*, not its list of asks. Round 2's plan
took its three largest corrections from there before a single parcel
was dispatched: one ask had already been delivered and nobody had told
the requester; two asks were one mechanism wearing two names; a third
ask's ceiling was two percent of the requester's wall, measured from
its own timing table. Every one of those would otherwise have been a
parcel. [CASE-STUDY-2, 02:00-03:30]

### Survey the tree before the plan, read-only

**Before the plan is written, send read-only surveyors to the tree.**
They edit nothing, and they read one named commit. Each reports the
facts it finds with the file and line behind them, marks which it
measured and which it only read, as §4 has a ledger entry mark what it
measured, and names the gaps and the places where the documents and the
code disagree. The lead writes the plan from their reports. The cert,
language and step-6 rounds of cft-fp256 each began with read-only agents
surveying the tree at a fixed commit (one agent, in the cert round),
before the plan of record
([round 6's survey, B17](archive/round6-practice-survey.md)). In the
language round three surveyors cited each fact to a file and line
(docs/VALIDATION.md:16682, at `4190a47`, cft-fp256's record, not in this
kit),
and a parcel then fixed the defects the survey found
(docs/VALIDATION.md:16764, at `4190a47`, cft-fp256's record, not in this
kit).
That is the evidence: no case study records a break from the lack of it.

---

## 2. P0: make the shared thing shared, before you split

Before dispatching anything, list every file each parcel would touch.
**Anything appearing in three or more columns is not a conflict to
manage — it is the first parcel, and it is the lead's.**

The diagnostic is mechanical. In the measured round, five parcels each
removed one entry from a list that was stated in four places: two
functions, a test, and a table in the README. Five agents editing four
files each is twenty edits and a guaranteed drift. P0 turned the list
into one table that both callers walk, and **unlocking a capability
became deleting one row.**

**Aim for a glob, not a list.** Even after that P0, every parcel still
had to add its file to a build variable, a declaration to a header, and
a call to a `main()` — four one-line edits in shared files, so every
merge conflicted in the same four places. Trivial is a P0 win over what
it would otherwise have been, but *zero* was available: had the build
globbed a directory and the entry points been discovered rather than
declared, the parcels would have shared no file at all. When you design
the refactor, ask what would make the seam **disappear**, not what would
make it small.

Two conditions:

- **It must preserve behaviour**, proven by running the full suite
  before and after. A P0 that also fixes things is a P0 whose green
  suite means nothing.
- **It must land and be pushed before any parcel starts**, so every
  worktree branches from it. A P0 landing mid-round is worse than none.
  When the round runs on a round branch (§7), P0 lands on that branch
  before any parcel starts, and every worktree is cut from the branch
  after it. That is what the push was for, so the branch itself need not
  be pushed: the language and step-6 rounds cut their parcels' worktrees
  from an unpushed one, and no case study records a break from that.
  [round 6's survey, the departures table](archive/round6-practice-survey.md)

**P0 goes past a verifier before any parcel that reads it is
dispatched.** The lead's code goes through the same gates as a parcel's
(§5), and P0 is the code every parcel stands on. In round 4 the
verifier's report on P0 found a run credited to the wrong law, two gates
that could not fail, and a runner that could report PASSED over a
failure; the first would have sent a parcel to reuse a scorer written
for another law, and to improve on a baseline that never existed. The
gate is per parcel, on the seams that parcel reads, so a parcel that
reads none of P0's seams need not wait for its fixes: the one working in
another repository, which read only the lead's library build, was
dispatched after that report and ahead of the fixes, because none of the
findings touched its inputs. [CASE-STUDY-4, obs 1; obs 5; 13:49; 13:53]

### Make the registry self-enforcing

When P0 turns scattered statements into a table, make the test **walk
that table and fail by name, in both directions**:

- a row no test exercised → fail, naming the row;
- a test naming a row that no longer exists → fail, naming the test.

The first stops a capability being added untested. The second catches a
test left behind when a capability is *removed*, which is the one a
round of deletions will actually hit.

This earned its place on the first run: four rows had never been
exercised by anything. The table did not create that gap, it revealed
it.

Then prove the check can fail — add a dummy row, confirm the failure
names it, remove the row.

**A tool's check that no stage runs is flagged, as a test file that no
stage runs is.** Round 4's registry failed any test file no stage ran,
and a tool's own check is the same gap in another place: in its second
round a Sattolo shuffle in place of Fisher-Yates passed every stage,
while the print tool's `--check` would have caught it in three seconds
and nothing ran that check. It became a gate five minutes after the
verifier named it. [CASE-STUDY-4, obs 27; 06:23; 06:28]

### Four more things a seam settles

**A seam's refusal belongs in every backend**, never only in the one
function the first parcel will edit. Round 2's P0 put the refusal of the
not-yet-built feature exactly where P1 would remove it, so the moment
P1 landed, the remote route accepted the feature it could not run.
[CASE-STUDY-2, 08:2x]

**A value statement names the measurement that would falsify it.**
"The mask removes idle lanes' compute and bytes" read as a fact in the
plan until the parcel measured that the sequencer issues per beat: the
compute half was never there. A brief's stop line says what to measure
before stopping; the measurement made the report decidable in one
reading. [12:37]

**A wave boundary is the one moment a brief can be updated.** Fold the
ledger into the next wave's briefs there and then; otherwise the next
wave starts from the plan as it was written the night before. The
ledger's `For:` lines are what made twenty minutes enough. [11:41]

**Name a base commit "at or after"**, and put the exact tip in the
dispatch message, where it can be right. A brief that names its base
exactly is wrong the moment the brief itself is committed. [11:41]

### Put what a round measures into the tree

**A trap one round measures goes into the next round's seam as a
refusal, not into its briefs as a rule.** A trap in a brief is a rule
each parcel has to remember; in the seam it is refused by name. Round 4
measured that an editable install of the owner's checkout made any test
run from outside a clone's root import the owner's code, and put that in
a parcel's brief as a rule with an assertion. Its second round put it in
the seam as a refusal, and the first thing the refusal stopped was the
lead's own smoke test. [CASE-STUDY-4, obs 25; 13:06; 05:01]

**A figure the documents quote has a script in the tree.** In round 4 a
spike's figures came from scratch work that nothing in the tree
reproduced, and the verifier's corrections rested on scripts of the same
kind, which were found only while the ledger was archived.
[CASE-STUDY-4, obs 24; obs 28]

---

## 3. The brief

Sections, each here because leaving it out cost something. The
template is [templates/brief.md](templates/brief.md).

**Start here** — what to read, in what order, with paths. An agent that
has read the post-mortem does not repeat it.

**Your job** — one paragraph. If it needs three, the parcel is two
parcels.

**Design first: a parcel proposes, and the lead approves before it
builds.** The brief can make the parcel's first phase a design: say
"Before you build anything, write your design in your ledger, make it
your report, and stop. The lead approves it, or answers it, before you
build." The brief lists what the design must cover. In each of the rev7,
audit, fixes, steps-5-and-6, language and step-6 rounds of cft-fp256, at
least one parcel's brief had it propose before it built, and the audit,
steps-5-and-6 and language rounds' ledgers record the lead deciding
([round 6's survey, B13](archive/round6-practice-survey.md));
the language round's record has one parcel's design, of ten decisions,
approved
(docs/VALIDATION.md:16851, at `4190a47`, cft-fp256's record, not in this
kit).
That is the evidence: no case study records a break from the lack of it.

**Files you own** — by path, and by *function* where a file is shared.
"`choose_timestep()` in `src/engine.c`, and nothing else in that file"
is a workable boundary; "the step control" is not.

**Files you must NOT touch, and who owns each.** Naming the owner
matters: a boundary with a reason behind it gets respected, an arbitrary
one gets litigated in the report. **Derive the ownership list from the
seam's own comments**, or diff the two before dispatch: round 2's first
escalation, two minutes after dispatch, was an edit the brief required
and the ownership list forbade. [CASE-STUDY-2, 06:32]

**A parcel may own the documents that describe its own code**, named by
section where a document is shared, and listed with its files. The
documents that state the project's claims stay the lead's (§7), and the
brief names them among the files the parcel must not touch. Every claim
in a document a parcel writes goes on its verifier's list: round 3 let
parcels write the rows that describe their own change, and six of its
eleven defects were false text in exactly those rows. [CASE-STUDY-3, §7]
In cft-fp256's later rounds parcels wrote their own documents, and the
lead kept only its record, its plan and its standing instructions.
[round 6's survey, the departures table](archive/round6-practice-survey.md)

**The cost model, with the divisor it assumes.** "A gathered element
costs about one beat" assumed a read side that pipelines; the tile keeps
one burst in flight, and the number was a round trip. A cost model that
names its assumption is checked by the parcel's first measurement; one
that does not is believed until a verifier prices it. [08:2x]

**The trap, and what will be measured at verification** - cycles,
cells, a mux count, a poisoned pointer - so the parcel measures it
first. The named trap got solved; the column nobody named got a
send-back. [12:49; 14:56]

**What READY means, stated before the first pass.** READY is "a gate, or
a stated limit": every property of the work is held by a gate, or stated
as a limit (§5 says how a limit is stated, §6 how it is tested). Put it
in the parcel's brief and in its verifier's, before the first verifier
pass. Without it a verifier loop over a spelling rule does not end by
itself: in round 4 two parcels each went three rounds, every pass
finding new spellings, until the lead scoped the next round to converge
and the verifiers judged READY by the standard they had offered
themselves.
[CASE-STUDY-4, obs 15; 22:39]

**The small edits outside your files that ARE expected**, enumerated.
Without this an agent either avoids a necessary edit and delivers
something that does not build, or reads the absence of a rule as
permission and sprawls. Say "one declaration here, one line in the build
file, one call in `main()`" and that is what you get.

**How to make the tree buildable**, if that takes a step. Three parcels
in one round each discovered independently that a directory their brief
told them to read did not exist in a fresh worktree, and each solved it
from scratch. One line in the brief.

**The base commit, and an instruction to verify it.** A worktree does
not necessarily branch from where you think: one parcel found itself a
merge behind the SHA its brief named, noticed, and reset. Say the SHA
and say "check you are on it".

Say what to do when it is not: "run `git merge --ff-only <sha>`, check
the SHA again, and if the merge refuses, stop and tell the lead." A
harness that cuts the worktree from the session's checkout hands the
parcel whatever that checkout's HEAD is. In round 3 it was the commit
another session had made in the shared repository, so the wave-2 brief
had every parcel fast-forward to the staging branch and check the SHA.
When another session works in the same repository, the brief says so,
and says never to switch that checkout's branch: round 3's lead did,
before it knew the other session committed there, and the branch was
gone within twelve seconds. [CASE-STUDY-3, The shared checkout]

**Host build traps, as verbatim commands.** Not "build it" — the exact
invocation, including whatever is non-obvious on this machine. An agent
will rediscover these in forty minutes; you can spend three lines.

**Each agent's own scratch directory, named in its brief**, and no
secret in any directory an agent is given. Say: "Your scratch directory
is `<dir>/<your-name>/`; put everything you make outside your worktree
there, and nowhere else." In round 4 the agents shared the lead's
session scratchpad, which held the platform key the round used, and a
parcel that wrote a script at its root overwrote a file of the lead's.
[CASE-STUDY-4, obs 9; 16:13]

**Working rules learned the hard way** — the two or three
environment-specific traps that have actually cost hours. Keep the list
short and true; a long one gets skimmed. **Environment facts belong in
the brief, not in the parcel's first hour**: which interpreter runs the
gates, the heredoc and line-ending traps, the pipeline that deadlocks
at zero CPU, the generated files a fresh worktree lacks. Round 2 learned
every one of these twice. [CASE-STUDY-2, the parcels' ledger files]

**A prohibition is written as the command to use.** "Never kill by
image name" was broken under pressure; "`docker ps --no-trunc`, then one
container ID whose command line is yours" was not. A rule that names
the safe action is followed when the unsafe one is closer to hand.
[08:14]

**The negative control, named specifically.** See §5. Name it by the
property that makes it bite, or run it before the brief goes out: a
control the brief names is a claim, like a path or a function. In round
4 the lead's brief asked for a target "about 1e-14" from a boundary
without measuring the error there; plain binary64 decides such a target
identically, so the control could not fail, and the parcel planted
inside binary64's own error instead. The lesson came back later: a check
held what a function traced, not what it returned, so a fault that
traced honestly and answered otherwise passed every gate. A control
bites only where the fault bites. [CASE-STUDY-4, obs 8; obs 16; 16:17]

**Do not** — push, merge, rebase, or commit to the main branch; weaken
an assertion to make something pass; fix anything outside scope.

**Report format**, always including *"anything you found that the brief
got wrong."* This is the highest-yield sentence in the whole system.
Round 1 measured it: all five parcels corrected their briefs, twelve
corrections in all ([CASE-STUDY.md](CASE-STUDY.md)). **Write it into
every parcel brief.** Method and template both carry it, and none of the
parcel briefs cft-fp256 has written since 2026-09-25 (37, as counted on
2026-10-02) does; rounds 4 and 5 kept it. The survey records the
absence, not what it cost.
[round 6's survey, the departures table](archive/round6-practice-survey.md)
A verifier's brief keeps its own open question, what else is there (§6),
and does not carry this one.

### Verify the constraints you write down

A forbidden-files list carried from another project is noise at best.
Four of the six files named "never edit" in one round's briefs **did not
exist in that repository** — they belonged to a sibling repo and the
list came across unchecked. Harmless as a prohibition; the same
carelessness in an *owned*-files list sends an agent to edit the wrong
thing.

Check that every path in a brief exists before you send it. **And
verify the functions you name.** Two of round 2's briefs named
functions that did not exist and one carried a premise about a loader
that was wrong as a mechanism; each cost a parcel its first half hour,
and each was a grep away. [CASE-STUDY-2, 11:53; 15:30]

**Check the worktree is of the right repository.** If your tooling
creates an agent's worktree from *the session's* repository, a parcel
aimed at a different repository cannot use that mechanism at all — it
will get a checkout of the wrong project, with a brief full of paths
that do not exist in it. That happened, and the brief compounded it by
telling the agent to stay out of a repository its worktree was inside
of. One `git log --oneline -1` and one `git remote -v` at the top of the
brief catches it; better, check before dispatching.

### A parcel's own subagents are invisible to you

A parcel may spawn agents of its own, and nothing tells the lead. They
are in no brief, they appear in no report until one mentions them, and
**a parcel that finishes without waiting silently drops their work**.

Observed: an audit parcel dispatched a sweep, finished fifteen minutes
before the sweep did, and wrote in its final report that it would "fold
its result in if the session continues" — a promise it could no longer
keep, because it had already stopped. The sweep returned eleven
findings, eight of them wrong assertions in shipped comments, including
one stale encoding window repeated in four languages across six files.
Those survived only because this harness notified the *top-level
session* rather than the parent that spawned it. A harness that routed
the result to the parent would have dropped it.

Two lines in the brief close it:

- **if you spawn a subagent, say so in the ledger when you dispatch
  it** — that is the only way the lead learns it exists;
- **do not finish while one is running.** If you must, say in your
  report that its result is outstanding and that you cannot collect it,
  rather than promising to fold it in.

And one for the lead: when a report mentions an outstanding child,
**that is an open item, not a footnote**. Track it the way you track a
parcel.

What a parcel starts that is not an agent outlives it the same way.
**Stop your own background work before you report**: the watches and
servers you started. In round 5, finished agents' watch loops and two
local web servers that parcels had started outlived them; they held the
worktree folders open, so the cleanup could not delete them, and one
server, started with no bind address, listened on every interface.
Stopping the loops woke a finished verifier, which re-armed its watch on
a closed round. [CASE-STUDY-5, obs 12]

### Expect boundary violations, and judge them on disclosure

A seam drawn by function is a hypothesis like any other, and one round
falsified three of five. A parcel told to own the step control found
that the setting it was implementing also changes a *different*
function; another needed one call in a function its brief never
mentioned; a third put its plumbing in an existing file rather than the
new one the brief named, because a new object would have meant a larger
edit to the build than the code was to the file.

All three were right, and all three said so unprompted. That is the
standard: **judge a crossing on whether it was disclosed and reasoned,
not on whether it happened.** A parcel that silently stays inside a
wrong boundary ships something half-implemented; a parcel that crosses
one quietly is the thing the ownership list exists to prevent. Ask for
the disclosure explicitly and you get it.

**Disclosure is a claim, and the lead checks it.** Say "end your report
with what you did not do", and after every agent check the lead's own
tree against that list. In round 4 a verifier's clone sat inside the
lead's tree and its report did not list it; only the lead's `git status`
found it. [CASE-STUDY-4, obs 4; 13:51]

---

## 4. The ledger

A brief is written once, at dispatch, and cannot be updated. Everything
learned while the parcels are running otherwise reaches them **never** —
it arrives in a final report, after the sibling who needed it has
finished.

Three things from one round:

- three parcels independently hit the same setup problem and each solved
  it from scratch;
- one parcel ended its report with a paragraph headed "for P3" — which
  reached P3 hours after P3 had made the same discovery itself;
- the lead learned at the second merge that a refusal was refusing
  something correct, with three agents still running and no channel to
  tell them.

So: **an append-only ledger the agents read and write while they work.**
Drop-in text at [templates/ledger.md](templates/ledger.md).

**Its rules reach every agent in one of two ways**: as a README in the
ledger's directory (the drop-in text above), or as the same rules in every
brief. Either is allowed, and the second only if every brief carries them,
the three read moments included, verifiers' and fixers' briefs as much as
parcels'. A rule its carrier lacks does not reach the agents who rely on that
carrier, as the stamp rule below shows. A later cft-fp256 parcel brief, which
carries the rules in place of a README, has "append only" and the stamp rule,
and none of the three read moments [round 6's survey, B7, CS3#2 and the
departures table](archive/round6-practice-survey.md).

**Where it lives matters.** Agents in worktrees cannot see each other's
files — that is what a worktree is. The ledger sits outside every
worktree, at a fixed absolute path each brief states, and is **ignored
by version control** so it never conflicts and never lands in history.
(That is the working copy; its archive, at the round's end, is the one
deliberate exception.)

**One file per author, append only.** Not one shared file: concurrent
appends lose writes, and per-author files make locking unnecessary by
construction. Everyone reads the directory; everyone writes only their
own, and corrects an earlier entry by appending beneath it. (A verifier
reads the lead's file first, and a parcel's only once it has formed its own
view: see "Verifiers watch the lead's channel only", below.)

**Read at three moments**, stated as moments because "periodically"
means never: before starting; before designing anything that touches a
file the brief called shared or forbidden; before writing the report.
These are the floor, not the mechanism — see the push channel below.
They stay the floor whatever carries the push, and whatever carries the
ledger's rules.

**Write when it clears the bar** — *would this have changed another
parcel's work, or the lead's?* Three things do: environment and setup
facts; a brief that turned out wrong (the moment you find it, not in
your report); a finding about shared code. Progress and plans do not. A
ledger full of status is one nobody reads.

**Mark what you measured.** Every entry says which claims were measured
and which believed. Agents build on each other's entries and an
unverified claim propagates faster than a verified one.

**When a pause is announced, each agent records where it is** before it
stops: what is committed, what is half done, what it was about to do. A
pause is the exception to "progress and plans do not" above, because the
entry is a resume note for its writer as much as for the lead. On resuming,
do a full read, check your tree before you trust your memory of what you
had done, re-arm your watch, and say where you were interrupted. Round 4's
lead wrote that rule into the ledger when a usage limit was announced; three
agents then stopped mid-task and each resumed from its own entries and its
tree, none repeating or losing recorded work, and one had written its state
down before the pause, unasked [CASE-STUDY-4, obs 12; 16:25]. The owner's
own words for a pause, in cft-fp256's steps-5-and-6 round, were to "commit
where they are and leave a resume note for themselves incase context is lost
in the downtime", and that round's first-session agents did not survive the
pause: each was dispatched again from its brief and its own ledger's resume
note (docs/VALIDATION.md:16507, at `4190a47`, cft-fp256's record, not in this
kit).
It rests on practice and on the owner's word.

**The lead writes to it too**, and this is half the value: it is the
only channel for correcting a brief after dispatch. **The lead's decisions go
in the ledger first, then in the message.** Round 4's lead resumed a parcel by
message and wrote its answer to the ledger ten minutes later, and the
verifier that watched the ledger found no answer there [CASE-STUDY-4,
obs 17; 23:25-23:35]. A message may carry a correction as well (below), but
only once its entry is written, and that is the sense in which the ledger is
the only channel: it is the channel of record, so that what a later reader
finds in it is every correction there was, in order.

**Stamps are substituted, not typed.** Every author in round 2 - the
lead three times, four parcels, a verifier - typed a guessed time at
least once, and every guess ran ahead of the clock by three to ninety
minutes. The fix that held was mechanical: write the entry with a
placeholder and let the append substitute the clock. [CASE-STUDY-2, §4]

**The stamp rule goes in the ledger's template and in every brief, fixers'
included**, as an instruction an entry can follow word for word: write each
heading's time from `date`, never from memory. Round 3 shows why, and
corrects what round 2 was taken to show: a typed stamp errs in both
directions. Most guesses there ran ahead of the clock too, but two ran behind,
both by about four minutes. Where the brief said to take the time from
`date`, 5 of 38 watched parcel entries still carried typed stamps, all
corrected by their authors; the three send-back scripts did not state the
rule, and 5 of the fixers' 6 stamps were typed; and the follow-ups' README,
a verbatim copy of the template, lacked it because the template did.
[CASE-STUDY-3, §4]

**A correction is linked from the entry it corrects** - an appended "see
HH:MM" line beneath the old entry is an append, not an edit - and a
number a sibling might reuse is restated in the form the sibling would
search for. A retracted count sat in the file for fifteen minutes, in
order, headlined CORRECTION, and was used once anyway. [13:34]

**A background job that writes to the ledger stamps at write and says
what it describes.** A launch wrapper appended its entry an hour after
the state it described had been superseded. [12:45]

### Escalation: one rule, whatever carries it

**What cannot wait for a read moment goes to its reader at once, and is
written in the ledger.** That is the lead's correction of a brief after
dispatch, and a parcel's question or finding that only the lead can act on.
A parcel's question goes this way, not into its own file to wait for the
lead's next read: in round 3 all eight parcels asked the lead questions in
their own files, six never used `urgent/`, and each was answered while the
lead's watch happened to be up [CASE-STUDY-3, §4]. So the brief says that a
question goes by the escalation channel, and says how to escalate without
finishing: send it and wait for the answer, rather than holding it for the
final report.

Two means carry it, and either is allowed: the file channel, a file in
`urgent/` and a watch on it, described in the next subsection; or the
runtime's own messages between agents, with the question written in the
sender's own file first. cft-fp256 used no `urgent/` from its audit round on,
and messaged in both directions
[round 6's survey, B6](archive/round6-practice-survey.md). On either means:

- **The ledger entry comes first**, then the message: the lead's decisions
  (above), an agent's question in its own file. The file channel meets this by
  being a file in the ledger.
- **A verifier is sent only the lead's messages**, as it watches only the
  lead's channel (below).
- **The three read moments stay the floor**, whatever carries the push (item 1
  below).
- **Where the lead learns of escalations from the runtime instead of from a
  watch, the channel is watched to work.** cft-fp256's cert round's lead kept
  no watch [round 6's survey, the departures
  table](archive/round6-practice-survey.md). A test escalation at dispatch
  must reach the lead, and the lead's record says how it learned of each
  escalation, the test included. A channel nobody has checked is believed to
  work: round 4's lead dispatched a verifier without arming its watch, and the
  round's first urgent message sat unread for five minutes [CASE-STUDY-4,
  obs 2]. The test shows that the channel worked at dispatch, and in one
  direction; the three read moments, and the lead's own reads below, cover the
  rest.

### Reading it is a polling schedule; add a push channel

Three read moments are a schedule, and a schedule's latency is its
interval. An agent that reads at the start, designs for an hour, then
reads again before touching a shared file will sit on a correction
posted ten minutes in for the other fifty. That is the difference
between a note that saves an hour and a note that arrives after the hour
is spent.

So **watch the ledger as well as reading it**, with a file watcher that
turns a new entry into a notification. Where the agent runtime offers a
monitor primitive — a background command whose every stdout line becomes
a notification — one poll loop over a directory is all it takes. This
subsection is the file channel, one of the two means of the rule above.

Three things make this work rather than backfire.

**1. Push PLUS pull, never instead.** A watcher that has died — timed
out, been killed, been auto-stopped for volume — looks exactly like a
ledger with nothing new in it. Silence is not success. The three read
moments stay as the floor and the watcher is latency reduction on top;
if an agent notices its watch is gone while it is still working, it
re-arms *and* does a full read. This holds whatever carries the push: the file watch, the runtime's
messages, or neither. And where every watch expires, as in a harness that
caps one at thirty minutes, the expiry notice is the moment for an agent
still working to re-arm it and do a full read, not a later noticing: round 3's lead's watch expired at 13:29
and was not re-armed until 17:23, and expired again at 18:57 and was not
re-armed for the rest of the round [CASE-STUDY-3, 13:29; 17:23; 18:57].

**2. Split the channel by urgency, not by author.** Most entries matter
to one parcel in four. Watching everything means every agent pays a
notification for every entry, most of them irrelevant — and a runtime
that throttles or stops a noisy watch will turn the push channel off
without saying so. So:

- `ledger/urgent/` — **watched.** One file per message, and the bar is
  "stop what you are doing and read this". Mostly the lead: a brief that
  turned out wrong, a merge that invalidated an assumption, a parcel
  told to delete something that turned out to be load bearing.
- `ledger/<author>.md` — **polled** at the three moments. Everything
  else.

This is what turns the ledger from a noticeboard into a channel the lead
can actually *send* on, which is the half a brief has never had.

**3. Emit the routing line, not the entry.** The watcher should print
the headline and the `For:` line, nothing more, so an agent decides in
one glance whether to go and read. A notification that dumps a paragraph
costs the same attention as the interruption it was meant to save.

**Arm the watcher from an inline command, not a script file.** Where
agents in a round share a scratch directory (§3 gives each its own), the
watcher is the single script *every* participant writes — so it is the single
filename every participant collides on. Both agents in one round
reached for the same obvious name; the second write won, and the first
agent's process survived only because the shell had already read the
file. It noticed, re-armed under a distinct name, and put it in the
ledger. An inline command has no file to clobber and nothing to be
edited out from under a running process. If you must use a file, put
your own name in it.

**Re-arm from the snapshot, and run one watch at a time, on files of its
own.** A re-armed watch that kept the last one's snapshot reported on its
first pass the entry that arrived while it was down, so the gap cost latency
and not information [CASE-STUDY-4, obs 3; 15:25]. The shape below takes its
snapshot when it starts, so it does not announce what arrived while no watch
ran; the full read in item 1 is what finds that. And two watches running
together on one snapshot's temporary files each moved the other's copy, and
the lead's script reported the ledger rewritten when it was not; the lead
checked every file by hand [CASE-STUDY-4, obs 17; 21:28-21:31].

**One file per urgent message, written atomically** — compose it
elsewhere and rename it into place. A new file is an unambiguous event,
and rename-into-place means a watcher can never catch a half-written
one. Appending to a shared `urgent.md` reintroduces both problems.

A shape that works, polling every twenty seconds and emitting one line
per new message:

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

**Verifiers watch the lead's channel only.** A verifier is paid for
independence, and a stream of "the parcel says this is fine" is exactly
the input that erodes it. Environment facts and lead corrections should
reach it; parcel self-reports should not, until it has formed its own
view.

### The lead watches too, and watches more

The channel above was designed as lead-to-agents: a way to correct a
brief after dispatch. Its first live use was the other direction — a
parcel escalating that it had been dispatched into a worktree of the
wrong repository — and the lead had no watcher at all, because the
design had the lead as sender.

**Arm one.** The lead is the *worse* poller of the two: agents have
three read moments built into their workflow and the lead has none, just
an interleave of merges, suite runs and conversation with no beat where
checking naturally lands. And the lead is the only node that can act on
an escalation. A channel whose one actor is not listening is half a
channel.

**Arm it with the first dispatch, and keep it armed.** The lead's channel is
live from the first thing it dispatches, not from the first time it
remembers: round 4's lead dispatched a verifier without arming its watch, and
the round's first urgent message sat unread until the owner noticed, five
minutes later [CASE-STUDY-4, obs 2; 13:43]. The next morning the same lead
armed it with the dispatch only because its memory carried the lesson, and
METHOD.md did not yet say it [CASE-STUDY-4, obs 32]. The lead watches the
escalation channel continuously, and re-arms on expiry as item 1 above has it.
Where the runtime tells the lead of escalations instead of a watch, the same
moment is the test escalation, as the rule above has it.

Two things are different about the lead's watch.

**Watch the whole directory, not just `urgent/`.** Agents are shielded
from sibling chatter deliberately — it is noise to them and it is what
throttles a watch. The lead wants all of it, because **only the lead
can see a pattern across parcels**: three agents hitting the same setup
problem is invisible to each of them and obvious to the one reading all
three files. Emit the headline and `For:` line only, as agents do, and
the volume stays manageable. **Whatever replaces that watch, the lead reads
every author's file before each merge and at each wave boundary** - where
section 2 has it fold the ledger into the next wave's briefs. These are the
lead's own read moments, the floor under its view across parcels as the
agents' three are under theirs: a watch on `urgent/` alone, or the runtime's
messages, shows the lead what is sent to it, not what the parcels wrote beside
it. In round 3, with the lead's watch down, 11 of the follow-ups' 49 entries
never reached it; nothing was lost, because the report schemas required the
same substance and it came back with the verdicts [CASE-STUDY-3, §4]. That was
a property of the schemas, which the reads do not rely on.

**The posture is observer, not actor.** An entry is information, not a
task, and most need nothing. The failure mode is a lead who treats every
notification as an interrupt and thrashes the merge queue. A short
decision procedure on each:

- does it invalidate a brief that is in flight? → write to `urgent/`, or
  write the entry and then message the agent (the rule above);
- does it change the merge order, or what the next parcel should be? →
  adjust, and say so in the ledger;
- does it need the lead to verify something? → verify it;
- otherwise → note it and carry on.

**Verify an escalation like any other report.** The parcel that
escalated the wrong-worktree dispatch measured it four independent ways
and was right; the lead still checked it, in one command, before acting.
An escalation is a report, and *never act on the strength of a report*
does not stop applying because the report is urgent.

**And make escalating safe.** An agent that escalates something which
turns out to be its own misreading must not be penalised for it, or
agents learn to sit on problems until the final report — which is
exactly the latency the channel exists to remove. Same rule as the
verifier's "found nothing".

At the end of the round, fold anything durable into the repository's own
records, and then **archive the ledger from its working copy, with its
timestamps, beside the case study (or with the round's other records, where
there is none), and keep it**: it is the round's record, and neither the
archive nor the working copy is deleted at the round's end. A copy can lose
the times: round 3's project copy of the sweep's ledger had reset every file's
modification time to the copy's own, and only the working copy, still there,
held them [CASE-STUDY-3, §4]. Rounds 3 and 5 archived from the working copy,
each file with its time [CASE-STUDY-3, The ledgers] [CASE-STUDY-5, The ledger].
That it is kept, not deleted, rests on practice: no case study records a break
from deleting a ledger, and cft-fp256 kept the ledgers of several of its rounds
in place as the record, citing them from its documents
[round 6's survey, B15](archive/round6-practice-survey.md). An archive is for
the reader of the case study, not a channel.

**The lead's watcher skips the lead's own file.** Every entry the lead
wrote in round 2 came back as a notification. [CASE-STUDY-2, §4]

---

## 5. Gates and negative controls

**A gate that cannot fail is not a gate**, and the ways one dies are
specific enough to check for. All four of these were found in a single
round, and each was found by the parcel that wrote the code the gate was
meant to hold down:

- **Passing against itself.** A mode the implementation silently ignored
  would have left every case comparing the default against the default.
- **Proving nothing.** A case exercising a re-read triggered on step 1,
  when the thing being re-read was still all zeros. Re-read zeros, got
  zeros, passed.
- **Vacuous through the observable.** A control was checked through a
  rounded *view* of a wider state; the underlying difference existed and
  re-converged below the view's last bit, so the control matched and
  could not fail. Fixed by hashing the wide bytes.
- **Inert by construction.** A configuration where the physics made the
  difference *exactly zero* — so the obvious test would have passed with
  nothing implemented at all.

- **No expectation at all.** A case that *prints* what the code answers
  rather than asserting what it should answer will go on printing
  whatever it answers, forever, and look fine. A worked example did
  exactly this: it listed what it assumed was refused, printed
  `-> NOT REFUSED, which is a bug` for anything accepted, and after a
  capability landed it shipped that line about **correct** behaviour —
  accusing the library of a defect in the project's own published
  output, with the build exiting 0. Every case states the answer it
  expects, or it is documentation rather than a gate.

And one more, found by a verifier rather than a parcel: a **bit
comparison** that could be swapped for a **value comparison** and still
pass the entire suite, while silently breaking signed zero.

Round 2 added six, three of them about the gate's own plumbing:

- **A single target's exit code is not a verdict** where the harness
  cannot set one; the brief says which command is. A parcel found the
  test framework's makefile checked only that a results file existed;
  main fixed it the same morning. [CASE-STUDY-2, 07:30]
- **Print the build time of every binary a gate runs.** The tell for a
  stale binary was a count that did not move; the line that would have
  said "05:13" costs nothing. And name the test executables to the
  build: `make all` does not build them, twice in one round. [11:50;
  the card day]
- **The lead's code goes through the same gates as a parcel's**, and
  through a verifier: every seam commit and every fix, all round, not
  only P0, before main moves (§7 has its merges and records). Twice the
  lead's own change was wrong on its first run - a stale test binary
  standing in for a gate, a bound computed from the wrong example - and
  both times a gate caught it, not a person. [11:50; 17:39] Round 3's
  two seam commits, one of nine files with code among them, went past
  gates and CI alone [CASE-STUDY-3, §5]. Round 4's P0 verifier found
  four new defects when it re-checked the lead's fixes to its 21
  findings, three of them in the gates written to answer them
  [CASE-STUDY-4, 15:59]. Round 5's plan had the rule with no exemption
  in it, and its lead still put eight commits of its own on main with no
  verifier, among them an email gate, one list of edges and the site's
  ledger as a source. The verifier found gate-kind defects in three, the
  email gate's among them: it read raw bytes, so an encoded address
  passed. The lead's own gate was no substitute for someone else's.
  [CASE-STUDY-5, obs 2]
- **When a mechanism is enforced in two places, a gate that reads the
  cheapest observable cannot see a defect in the other.** A mask was
  enforced at the active set and again at the drain strobes; the
  strobes hid a revived lane from every byte-level case, and only a flag
  could tell. [14:56; 16:04]
- **A crash can be a gate's faithful signal** when the property is "no
  read happened": a regression cannot pass it silently. [13:59]
- **A probe that has caught a defect goes into the suite.** A probe that
  sat outside the suite caught two real defects from there; it is in
  the suite now. [10:24; 12:18]

And two from the card day, where the suite was green and the silicon
was not:

- **A device gate needs a device with its own memory.** The simulator's
  memory model started every test empty and the software executor wrote
  the caller's buffer in place, so no host in the suite ever held a
  device copy with a previous run in it - and the first masked run after
  an unmasked one on the card returned the previous run's bytes. The
  seam test is the one the device test already had: the masked leg
  after the unmasked one, on the same window. [the card day, 21:44]
- **Test the largest shape a capacity claims, and one past it.** A
  capacity kept at page granularity behind a per-beat contract passed
  every shape the suite had and failed at 64 lanes, the first shape
  that crossed a page. [the card day, 22:0x]

So: **name each parcel's negative control in its brief.** Not "test it
properly" — the specific control. "A do-nothing routine must leave the
run bit-identical to no routine at all, *and* the active case must
differ from the inactive one." Require the parcel to build it, run it,
confirm it fails, delete the artifact, and **report both results**. A
control described but not run is worth nothing, so ask for its output.

**A control names the rule it exercises, and restores the bytes it
planted over exactly.** A control that fails for some other reason
than the one it was written for tests nothing, and nothing shows it.
In round 5 two email controls were caught by raw text that still held
the whole address, so their joining rule was never exercised; and on
Windows 22 of the lead's control writes wrote CRLF line endings, and
the carriage returns left in a restored MANIFEST satisfied five new
controls that named no file. Neither showed as a failure.
[CASE-STUDY-5, obs 9]

### What a gate cannot see, and who finds it

**A gate that reads source text is a stated limit, not a guarantee.**
In round 4 each gate written as a list of forbidden spellings fell to
a spelling it did not list, and so did the three allowlists that
came after. What held checked what the code does: an audit hook that
sees a process, a socket or a file write however it is spelled, and
exact checks on tight inputs inside each step. So put the guarantee in
a check of behaviour, and state what that check cannot see.
[CASE-STUDY-4, obs 10; obs 14]

**A limit is stated by the behaviour it concedes, not by the plants
that found it.** Round 4's second parcel stated its limits as the
faults it had met, rebindings below the names and a rebinding between
checks. A trace hook installed at import was neither, and it passed
every gate: a limit stated by its instances is walked past, as a rule
stated by its instances is. The fix stated the class, with the trace
hook as its plant. A limit stated that way holds against a new
spelling of the same behaviour. Section 6 tests each stated limit that
way, and a known limit recorded at a merge is one. [CASE-STUDY-4,
obs 21]

**The lead's fixes to a verifier's findings go back to that verifier,
which picks its own faults.** Each gate written to answer a finding
had been watched to fail, but on faults its author chose: the premise
gate's author planted only faults that scale with precision, and the
gate was blind to the one kind that does not. The P0 verifier's first
three passes found 21, then 4, then 5 defects, a third of them in
fixes to the pass before. [CASE-STUDY-4, obs 7; obs 13]

---

## 6. The verifier

For anything hard to check by reading, put a second agent between the
parcel and the merge whose job is to *disconfirm*. Template at
[templates/verifier.md](templates/verifier.md).

**Inputs:** the brief, the diff, and the parcel's claimed results. When
it reads the last of these is §4's: "Verifiers watch the lead's channel
only".

**It must:**

- **re-run the gate itself**, from a clean build, rather than trust
  pasted output;
- **re-run the negative control**, or build one if the parcel did not;
- **diff the changes against the ownership list** — anything outside is
  a finding, even if it looks correct;
- look for the specific cheat shapes: an assertion loosened, a tolerance
  where exactness was required, a skipped case, a constant transcribed,
  a `TODO` where work was claimed;
- **verify the "nothing else regressed" claim by running the rest**, not
  by reading it.

**A verifier may reuse a run instead of re-running it, but only when
all three hold:**

- someone other than the author of the work under verification made
  the run;
- the inputs are identical, the hashes of the binaries the run used
  included;
- the verifier re-runs from clean anything it doubts.

So a parcel's verifier may reuse a long run the lead made for that
parcel (§7), but the verifier of the lead's own work may not reuse the
lead's run, and the full suite at the tip of the branch main will move
to is always run afresh before main moves. The allowance rests on a
cost, not on a break: round 3's runner had no cache, so the parcel, its
verifier, the fixer and the re-check each paid in full for the same long
stages, which the case study infers were much of the agents' time, and
the saving from reuse is an estimate, in hours, not a measurement
[CASE-STUDY-3, Where the wall clock went]. The conditions keep what the
first duty above is for. A run the author made is the pasted output that
duty exists not to trust: the lead's own gate passed commits whose
gate-kind defects only a verifier found [CASE-STUDY-5, obs 2]. A run on
a stale binary says nothing about the work: the lead's script ran a
binary from 05:13 on two merge gates [11:50]. And whatever the verifier
doubts it still re-runs from clean.

**It must NOT fix anything.** A verifier that edits is a second author
with none of the first one's context, and you lose the independence you
paid for. It reports; the parcel or the lead acts.

**When it is worth the extra agent:** the gate is slow, so there is a
real chance it was not run; the change touches a numerical invariant, a
hot path, or anything where "looks right" and "is right" come apart; the
report claims green without pasting output; or the parcel is the long
pole, where a late problem is most expensive.

**Its own failure mode is rubber-stamping.** Require it to state what it
actually ran, command by command, and make **"found nothing" an
acceptable, unpenalised answer**. A verifier under pressure to produce
findings invents them, which is worse than none.

### What verifiers actually returned

**Give it a numbered list to attack, and expect its best work to be
outside the list.** One run confirmed all eight items it was handed and
found two genuine divergences nobody had thought to ask about. Eight
confirmations were worth the run; the two findings were worth more. Name
what you suspect, then ask explicitly what *else* is there.

**Distinguish "the shipped code is right" from "the gate would catch it
if it weren't."** Four of one run's findings were the second kind.
Those are worth as much as defects, because they are the defects of the
next change, and a verifier is the only role positioned to notice them.

**A false claim in a comment is a finding.** One verifier disproved a
statement in the code — "this file is byte for byte what we wrote
before" — by writing the file at both commits and comparing. The
behaviour was fine; the sentence was not, and a sentence in the code is
something the next person will rely on.

**Put "check every claim in a comment, doc or commit message" on every
verifier's list when parcels write documents.** It extends the rule
above. Six of round 3's eleven defects were false text in the rows
parcels wrote about their own change, and all six were caught: four by
wave-2 verifiers whose list said that, two by wave-1 verifiers whose
list said comments and commit messages only, one of which widened its
list and one of which found it under "anything else". [CASE-STUDY-3,
§7]

**The verifier reads a claim's domain and quantifier as claims, beside
its numbers.** Both defects round 4's second-round verifier found lay
in the words around a measured figure, not in the figure: a table's
columns, 16 to 64, read as a band out to 90, and "for ANY law" on the
evidence of one law. The same slip was made twice more where no
verifier was looking, and the lead caught both before they were
committed: a draft saying every piece of the work had been checked by
an independent agent, and an account saying every number in the paper
is held, when its check holds the ones it lists. So ask of each claim
how far it reaches, and what was measured to reach that far.
[CASE-STUDY-4, obs 23]

**A figure that crosses into the documents from any report carries its
definition, or is re-measured**, a verifier's report included. Two
figures reached round 4's docs with the parcel's label and not its
definition: "units of u", where u was the uniform a target is drawn
from and not the unit roundoff, and "(relative)" on distances that
were absolute. Every figure traced to the ledger, so a check that
traced figures passed both. [CASE-STUDY-4, obs 20] A verifier's "2
independent modes" became "two modes" in the lead's correction, a word
dropped and the error kept, and four more of its figures went into the
docs unmeasured by the lead. [CASE-STUDY-4, obs 28]

**A verifier per parcel pays.** Round 2's four verifiers were 38
percent of the agents' tokens and produced four send-backs, none for a
wrong bit: each found a property the parcel had no instrument for - a
cost class, a flag arm reading stale lanes, a read before a bounds
check, a gate hole beside an unpriced area column. The parcel measures
what its brief names; the verifier measures what the brief did not know
to name. [CASE-STUDY-2, §6]

**A verifier's report is due when its LIST is exhausted, not when its
first pass is.** "No defect" was posted before the one target outside
the list had run, and the lead had the parcel staged within minutes of
it. [10:07; 10:24]

**A verifier's default list carries the instruments the parcel lacks**:
synthesis cell and mux counts for RTL, a poisoned pointer for anything
that reads a caller's buffer, "derive the increment" for any count a
report quotes, and the lead's own artefacts - the seam paragraph, the
plan's premise - beside the parcel's. [09:29; 10:49; 13:34; 14:56]

**The lead's grants and rulings made after dispatch are on the
verifier's list**, as items to check and not only as reading. Two of
round 3's eleven defects came from them: a grant that keyed a new
refusal on the format ceiling and so refused a working build, and a
skip rule that let one run count the same missing capability both
ways. Both reached the verifiers as required reading, no item on their
lists asked for them to be checked, and both were caught through the
parcels' diffs. [CASE-STUDY-3, §6; 18:49; 19:56]

**The scoped re-check after a fix is the default** - eleven to
twenty-three minutes each in round 2 - not a re-run of the whole list.
[10:38; 12:09; 13:59; 17:31]

**Side notes get a step of their own, in every round.** Round 3's
sweep triaged its verifiers' 314 side notes, with the critic's
findings, in a round of their own: 324 items, 51 findings, 49 applied.
The follow-ups had no such step, and at least nine of their verifiers'
and re-checks' notes were still open on main when the round ended.
[CASE-STUDY-3, The shape of the round; §6]

**One technique worth copying.** To prove a change did not touch a build
it was not supposed to, diff the **preprocessed translation unit** at
both commits, not the source. In one case the same file compiled two
ways and only one was in scope; the preprocessed output was 3610 lines
each and differed by one line. That settles the question in a way
reading a diff cannot. Comparing the compiled object's hash is the same
idea, cheaper.

### What READY needs, and what sends work back

**A stated limit is tested.** A verifier judges READY by the standard
the brief states (§3), a gate or a stated limit for every property, and
a limit is a claim it can test: it reads each limit the work states,
builds a fault that passes every gate, and sees whether the fault lands
inside the limit or outside it. Inside, the property is stated.
Outside, the limit claims less than the work concedes, which is a
sentence that claims more than is true (below), and READY waits for it
to be restated. In round 4 the verifier of P1's new check built a fault
to evade it, and the fault passed every gate and lay inside the limit
P1 had stated: it certifies wrong sites only on inputs the end-to-end
check never reaches. [CASE-STUDY-4, obs 18] It rests on practice.

**Only a regression or a wrong answer sends work back; anything else
merges as a recorded known limit, and a sentence that claims more than
is true is restated at the merge, not left standing.** This is the
owner's rule of 2026-09-27, recorded in cft-fp256's docs
(docs/VALIDATION.md:15274, at `4190a47`, cft-fp256's record, not in this
kit)
and carried over there with its restate clause
(docs/VALIDATION.md:16164, at `4190a47`, cft-fp256's record, not in this
kit);
the owner's own words of agreement are in
[round 6's survey, B3](archive/round6-practice-survey.md). It rests on
the owner's word and on practice: no break that led to it is recorded in
a public source.

"Known limit" is a place where a wrong answer could be relabelled and
hidden, so a known limit is held to what §5 and the test above ask of
any limit:

- it gives no wrong answer today. The first entry to apply the rule in
  that file, dated 2026-09-28, fixed five wrong answers a verifier
  found in the shipped tree, none introduced by the commit it checked,
  and made its other notes true in the docs or listed them as known
  limits (docs/VALIDATION.md:15260-15283, at `4190a47`, cft-fp256's record, not in this
kit),
  of which it says none gives a wrong answer today
  (docs/VALIDATION.md:15492-15494, at `4190a47`, cft-fp256's record, not in this
kit);
- it is stated by the behaviour it concedes, not by the instance a
  verifier found (§5);
- it is tested: a fault built to pass every gate must land inside it,
  and a limit such a fault walks past is a sentence that claims more
  than is true, so it is restated at the merge as the class it
  concedes.

---

## 7. What the lead keeps

**The lead's seam commits and fixes (§5), its merges and its records go
past a verifier before main moves, from the first commit of the round to
the last.** Its records are the project's record entries and its commit
messages. Not only P0 (§2), and the plan goes past one too, before the
owner approves it (below). The lead is the one
author in a round that nobody disconfirms by default
[CASE-STUDY-2, §5], and in each of rounds 2 to 5 the record shows its
own work going in without a verifier:

- **Round 2:** a patch of the lead's was wrong on its first run, and its
  gate was the only check it had had. [CASE-STUDY-2, 17:39]
- **Round 3:** the follow-ups' seam commits and both record entries went
  through gates and CI only, and each entry still disagreed with the
  data after the lead had re-read it. [CASE-STUDY-3, §5]
- **Round 4:** three of the lead's commits were on main before any
  verifier had read them, and the verifier's fourth pass over them found
  that the import allowlist among them did not hold.
  [CASE-STUDY-4, 20:56-20:58; 21:12]
- **Round 5:** the plan had the rule, and the lead pushed eight commits
  of its own with only its own gate; the verifier it then added found
  gate-kind defects in three. [CASE-STUDY-5, obs 2]

What else the lead keeps:

- **The plan of record, and a verifier on it before the owner approves
  it.** The verifier reads the draft against the tree, the lead answers
  its findings in a new draft, the verifier re-checks that, and the
  owner is asked after. In cft-fp256's certificate round the first draft
  drew twenty findings and the second six more gaps, and the plan
  changed before any code; one change was a salt committed by HMAC,
  since a bare SHA-256 of a key longer than 64 bytes would publish the key
  (docs/VALIDATION.md:15649, at `4190a47`, cft-fp256's record, not in this
kit).
  Its language and step 6 plans went the same way, step 6's reaching the
  owner only after three checks
  ([round 6's survey, B1](archive/round6-practice-survey.md)).
- **P0.**
- **The seam tests.** They belong to no parcel, which is exactly why
  they get skipped. Each merge should get a test exercising *two*
  parcels together. The test that would have caught the canonical
  failure is nine lines and runs in under a second.

The payoff is concrete rather than theoretical: the worked example in
[CASE-STUDY.md](CASE-STUDY.md) is a bit-identity defect that five
parcels, two verifiers and 211 assertions all passed over, because it
lived in a combination that two parcels' gates each excluded by
construction. A hundred-line seam test found it in seconds.
- **Files that are the lead's alone** — the README, published docs, CI
  config. Not because agents cannot write prose, but because those files
  state the project's claims and the claims must be one voice.
  A parcel may own the documents that describe its own code; what stays
  the lead's is the documents that state the project's claims, and every
  claim in a document a parcel writes is on its verifier's list. §3 has
  the rule and its incident.
- **Every merge, and the full suite after each one** - as a staging
  branch per merge, the suite on the build host at the staging commit,
  and main moving on the verdict. A merge is a push, not a staging. Keep
  a second, third and fourth checkout on the build host so a send-back
  never queues behind a sibling's hour. [CASE-STUDY-2, 11:06; 11:47;
  12:57]
  A round branch is an allowed shape beside this one: every worktree is
  cut from one branch (§2), the merges go onto it, and main moves to its
  tip at the round's end or at a milestone, not at each merge. Three
  conditions keep what the staging branch is for: a gate runs after each
  merge into it; each merge is made again by the integration verifier
  (below); and main moves only to a tip on which the full suite has run
  and which a verifier has passed. The shape rests on practice, and no
  case study records a break from it: round 3 ran one staging branch for
  the round and moved main once [CASE-STUDY-3, 17:17; 00:22; §7], and
  cft-fp256's later rounds ran a round branch
  ([round 6's survey, the departures table](archive/round6-practice-survey.md)).
- **The long runs.** Agents test as much as they can quickly, and hand
  large runs back to the lead to monitor. That is the owner's rule of
  2026-09-29, in the owner's words: "dont have the individual agents all
  run the full suites, have them hand back large runs to you to monitor
  rather than them, but they should still verify and test as much as
  they can quickly"
  (docs/VALIDATION.md:16165, at `4190a47`, cft-fp256's record, not in this
kit;
  [round 6's survey, B4](archive/round6-practice-survey.md)).
  It rests on the rule and on practice; no case study records a break
  without it.
- **The ledger's own file**, and folding it into the record at the end.
- **The lead's own slips, in every round's record.** Each is written in
  the ledger when it is caught, and listed in the round's record. No
  case study records a break from lacking the list; they record what the
  lists produced. Round 1's four gave four of this document's rules
  [CASE-STUDY, What the lead got wrong], and round 3's sixteen gave most
  of that round's proposals [CASE-STUDY-3, What the lead got wrong].
  cft-fp256's record entries carry the list in each of their nine
  entries from 2026-09-28 to 2026-10-02
  ([round 6's survey, B14](archive/round6-practice-survey.md)).
- **The cleanup: what the agents left behind.** Before the agents'
  worktrees are removed, the lead looks for what finished agents left
  running, and stops it. Round 5's watch loops and two local web servers
  outlived the agents that started them, one server listened on every
  interface, and they held the worktree folders open, so the cleanup
  could not delete them. [CASE-STUDY-5, obs 12] The agent's half,
  stopping its own background work before it reports, is in §3.
- **The docs sweep, in the lead's idle time during the round**, for
  every file no parcel touches, so the end of the round is one section
  rather than a sweep. [15:03]
- **The summary to the owner, with the cost** - per agent, measured as
  below, with the verifiers' share stated, and the wall clock split
  between the build phase and whatever ran unattended after it.
  [Cost of the round]
  Measure the cost as the tokens processed, read from each agent's
  transcript and the lead's: every message counted once, as the output
  generated and the prompt tokens read from cache and written to it.
  Round 3's lead reported no cost in its final report and, asked, gave
  the harness's per-agent figure as tokens used, which is the sum of
  each agent's final context size and not what it processed
  [CASE-STUDY-3, What the lead got wrong; Cost of the round]; rounds 4
  and 5 measured it from the transcripts
  [CASE-STUDY-4, Cost of the rounds] [CASE-STUDY-5, Cost of the round].

### Habits

**Never merge on the strength of a report.** Run the suite yourself.
Agents report in good faith and are sometimes wrong about what their own
change did.

**Resolve conflicts from what the VCS says is conflicted**, never from
what the merge output happened to print, and assert that no marker
survives before you stage. One lead resolved the two files the merge
message named, staged everything, and committed a third file still
holding its conflict — along with eight agent worktrees as embedded
repositories.

**Never merge while a suite is running.** This looks safe — the suite
built its binaries at the start, so a source edit cannot reach it — and
it is wrong for any part of the suite that is *interpreted*. One lead
merged mid-run on exactly that reasoning; the run reached a scripted
checker, read the merged parcel's **new** script off disk, and drove it
against the **old** compiled binary, producing three failures that were
entirely self-inflicted. A suite is only as prebuilt as its
least-compiled component, and scripts are never prebuilt.

**Freeze what is audited.** Auditors and verifiers read a committed SHA,
or a worktree the lead never edits, not the tree the lead is working
in. Round 3's lead widened its docs checker in the checkout the
auditors were reading; one of them posted at 09:14 that the docs stage
failed at HEAD, which was the lead's uncommitted edit, and ten noted the
edit in their reports. [CASE-STUDY-3, 09:10-09:19; §7]

**A merge conflict is not two piles of text.** The VCS hoists a shared
ending out of the conflict block; a resolver that has not read the lines
after the block has not read the conflict, and the compiler is the gate
that says so twenty seconds later. [CASE-STUDY-2, 14:12]

**The integration verifier makes each merge again.** From the merge's
parents, with `git merge-tree`, it rebuilds what the merge should hold
and compares: every path changed on one side only must equal that
side's, and nothing may be lost. A merge resolved by hand is the lead's
own work, and hand resolutions have gone wrong: round 1's lead
committed one with its conflict still in it
[CASE-STUDY, What the lead got wrong], and round 2's committed one
unresolved, on a `;` where `&&` belonged [CASE-STUDY-2, 14:12]. No
case study records the re-make itself, so it rests on practice:
cft-fp256's fixes round had its integration verifier do this for each
merge (docs/VALIDATION.md:16437, at `4190a47`, cft-fp256's record, not in this
kit;
[round 6's survey, B10](archive/round6-practice-survey.md)).

**A merge with no RTL in its diff gets no RTL suite, and the ledger says
so**, rather than the lead pretending it ran one; the build host's run
at the next merge with RTL covers the combined tree. [14:09]

**A gate budget is a subset of the suite, so check it against the merged
diff before you trust it**, after each merge (or each batch, where §8's
trade is made), and when main moves on a verdict that says FAIL, write
down why. Round 3's budget left out the `node` and `wasm` stages. The
lead ran them after the last batch, where one parcel had changed them,
but not after the first, where another had changed `bindings/node` and
only CI's host job ran them. Both local runs ended
`VERDICT: FAIL (1 stage)` on `lang-rust`, and main moved on the same
failure shown at the base commit and on CI's pass, which the record
entry says. [CASE-STUDY-3, 19:00-19:10; 00:20; §7]

**A seam changed mid-round is checked against every open branch at
once**, not at each merge. Round 4's lead turned its guards gate into an
allowlist while two parcel branches were open, ran it against both
before either merged, and found it would have refused their pure
constructors; it was widened to pure modules before the parcels arrived.
[CASE-STUDY-4, obs 11; 17:49-17:52]

**The lead may prepare a merge while the verifier works; the verdict
still gates main.** Round 4's lead made the merge in a worktree of its
own and ran the whole suite before the verdict arrived, so that the
verdict made the merge a fast-forward; writing the integration against
the ledger, not the parcel's report, also caught a figure the parcel had
handed over wrongly. [CASE-STUDY-4, obs 19; 23:40-23:50]

**One instrument per hypothesis, cheapest first, before touching the
design.** When the card disagreed with the bench, three instruments in
an hour - a fingerprint of the wrong bytes, a flag that only the lanes
could raise, a pattern in a pad that only the strobes could preserve -
told the host from the tile without a rebuild, and the defect was the
host's. The rebuild would have taken two hours and proved nothing.
[the card day, 21:2x-21:44]

**Unattended, decide what the standards decide and ask for what is the
owner's.** Round 2 ran for most of its length with no human watching;
the lead merged, verified, diagnosed and recorded within the project's
own rules, and put the owner's questions - the card, a clock, a push to
another repository - in the ledger to be answered when read. That is
the posture: the standards are the brief the owner already wrote.
[The setting]

**Ask what the owner wants to see first, and record the answer.**
Unattended, the lead cannot ask in time, so the question comes before
the effect: a push that deploys, a remote branch deleted, a change to
how results are counted. Round 3's lead did all three before the owner
could see them, and had not asked beforehand whether a deploy was
wanted. [CASE-STUDY-3, 00:22; §7]

**The owner's decisions are kept as the owner gave them, with their
dates.** The lead's reading goes beside them, marked as the lead's. No
case study records a break without it; it rests on practice. Round 4's
owner cleared a push "when ready", the lead recorded its own reading of
"ready", and the push went nine hours later, under the owner's word of
15:35 [CASE-STUDY-4, 15:35; 00:39]. cft-fp256's record entries of
2026-09-29 to 2026-10-02 quote the owner's decisions in the owner's
words ([round 6's survey, B8](archive/round6-practice-survey.md)).

**The owner's standing rules are carried from round to round**, into the
part of each plan that says how the round is held. No case study records
a break without it; it rests on practice. cft-fp256's plans carry the
send-back rule of 2026-09-27 and the long-run rule of 2026-09-29 that
way, and its record entries mark a rule "carried over" with its date
(docs/VALIDATION.md:16164, at `4190a47`, cft-fp256's record, not in this
kit;
[round 6's survey, B9](archive/round6-practice-survey.md)).

**Read the log, not the exit code.** A background wrapper once reported
exit 0 for a run whose log said `Error 1`, because a trailing `echo`
succeeded. And when a failure is not immediately attributable, check
timestamps before diagnosing — comparing a binary's build time against a
script's mtime settled the case above in one command. Never call such a
failure a defect *or* a false alarm until a clean re-run says which.

---

## 8. Sequencing

- **Dispatch the long pole first.** It sets the merge order and it is
  where a late problem hurts most.
- **Hold any parcel that shares a file intimately with another** until
  the first lands. A VCS will merge two disjoint functions in one file
  without complaint; what it cannot merge is one parcel reshaping the
  thing another is hooking into.
- **Parcels finishing early is fine.** Merging is serial, and the
  constraint is not the merge but the **suite run after it**. Budget it
  explicitly: at twenty-five minutes a run, five parcels is two hours of
  waiting nobody plans for. Where two parcels share no file, merging
  both and running one suite is a defensible trade *if you say you made
  it* — a failure then costs a bisection over two candidates, cheap when
  each arrived green on its own.
- **Re-brief from what comes back.** The first report usually corrects
  the plan. Fold it into the remaining briefs, and into the ledger for
  the ones already running.
- **Dispatch on the fast simulator; the slow one confirms in the
  background.** The owner said so in round 2, and the confirmation
  changed nothing all day. [CASE-STUDY-2, 06:3x]
- **A send-back needs no re-brief.** The harness resumes the agent with
  its whole context, so a fix costs half an hour of parcel and half an
  hour of verifier, and the hour is the build host. The method assumed
  a parcel could not be re-entered; it can, and the loop is cheap enough
  to run three times on one parcel. [§6 of the case study]
  **The exception is an agent that cannot be resumed.** Round 3's
  parcels were started by workflow scripts, and the lead's attempt to
  resume all three failed: "could not be resumed: No transcript found
  for agent ID". A send-back to such an agent is a newly briefed agent.
  Brief it with the verifier's defects, and give it the parcel's final
  report, its ledger file and its worktree: round 3's fixers had the
  ledger file and the commits, their only memory of the parcel, and not
  the report the lead held. Resuming the same agent stays the default.
  [CASE-STUDY-3, 15:09; 15:12; §8]
- **A stop line fires for value, not only for size.** The parcel priced
  smallest stopped at its line because the value was not there, and the
  plan was corrected with its table. [12:37]
- **The build phase is done when every parcel is merged and verified on
  the build host; the image and the card day are the lead's and the
  owner's, after**, and that phase can be the longer half of the round
  in wall clock: round 2 was 24 hours, of which the last ten were tile
  builds and the runs against them. [17:49; the card day]
