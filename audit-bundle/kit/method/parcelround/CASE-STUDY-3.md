# A third round, reconstructed after it ran unattended

The first case study ([CASE-STUDY.md](CASE-STUDY.md)) was written after
a round that produced the method; the second
([CASE-STUDY-2.md](CASE-STUDY-2.md)) was written while its round ran.
This one was written the morning after, from the record the round left:
the lead's transcript, every agent's own transcript and the workflow
journals, the two ledgers, and git. Four agents reconstructed the
timeline, the cost, the sweep and a rule-by-rule check against
[METHOD.md](METHOD.md). The lead wrote a draft from their results, and
four more agents, who had not written it, checked every figure and claim
in it against the primary sources. They confirmed 100 statements and
found 22 wrong, 44 misleading and 3 unsupported - attributions and
counts, and about as many overstated scope words and characterisations,
several carried over from the fact-gatherers' summaries rather than the
records. Two more agents then re-checked the corrections: 51 of the 69
were sound, 17 had brought in a new error of their own, one had not yet
been made, and they raised 29 issues in all. A third pass on the 39
passages that changed confirmed 34 of 40 checks and found 6 minor
imprecisions. This version carries all three passes' corrections; the
loop stopped at 69, 29, 6. Where the lead's account at the time
disagrees with the record, the record wins and the disagreement is
stated.

Three things are new here. The method was applied first to an **audit**:
a documentation sweep, where the parcels were read-only auditors and the
lead owned every edit; the four follow-ups that took most of the day were
ordinary parcels writing code and documents in worktrees. Every agent was
dispatched by a **workflow script** rather than one at a time, which
turned out to change two of the method's assumptions. And for the last
13 h 41 min the owner **sent nothing at all**. Round 2 also ran mostly
unmonitored, but with touches along the way; this one had none.

## The setting

cft-fp256, the same project as round 2: a deterministic floating-point
coprocessor for an Alveo U50, with a Python golden model that is the
authority, a C library with software, XRT and remote backends, bindings
in nine languages, and a verification runner of forty stages. Fifty-odd
tracked documents describe it, and they had drifted.

The ask, at 08:32 on 2026-09-24: bring every document up to date; use
ParcelRound for the agents and the HonestFramework repository for what
counts as a verified claim; report a plan first. The build box
(amd-arc-box, the one with the card) was busy with a clock sweep, so the
round was to keep mostly read-only there, small verification runs
allowed; the desktop was contended - "accuracy should never differ due to
speed". The owner's decisions on the plan, at 09:00: commit straight to
main; widen the docs gate; no planted faults on the auditors ("a
comprehensive sweep of whats there, not new sourced data"); state the
clock as 175 MHz, assumed. At 09:50, mid-round: "Let the verifiers finish
before you apply anything."

The sweep landed at 11:57 and left 179 out-of-scope notes from its
auditors and verifiers, mostly stale code comments. Three of the four
follow-ups came from that list: the comments themselves, the published
wasm pages' prose with the pages regenerated, and two capability-word
inconsistencies. The fourth - the runner's verdict saying "nothing
skipped" over a check that skipped inside a passing stage - came from the
lead's own gate run at 10:26. At 12:20 the owner said "Go ahead and
tackle the 4 left open (this PC is free for work if needed)", and at
12:21 "You may start docker here". The next message came at 04:00 the
following morning.

Lead: one Claude session, claude-opus-5-5 at xhigh effort. Agents: the
same model, all 145 of them spawned by ten Workflow calls (one of which
crashed at launch); the Agent tool was never used. One environmental fact
mattered more than expected, and the lead learned it late: **the main
checkout was shared with a second live session** - the U50 clock sweep -
which committed and pushed 3b15d52 to main at 12:52, in the middle of
this round.

**How the round was run.** 17 h 30 min from the request to the final
report. The owner sent seven messages during the work, all before 12:22;
the follow-up phase then ran 13 h 42 min, 13 h 41 min of it after the
last message. In that stretch something was running in the background
for 796 of 822 minutes - agents for 573, the lead's own gate runs for
240, the follow-ups' CI runs for 280, overlapping - and the lead was
inside a turn for 64 minutes in 48 turns. The follow-ups did not need a
human to keep their standards. The sweep did, once: at 09:50 the owner's
message stopped the lead applying findings before the verifiers had
finished - its applier still pointed at the main checkout the verifiers
were reading, though the lead had created a worktree for the edits six
seconds earlier. And some calls took effect before the owner
could see them; they are listed under §7 below.

## The shape of the round

**Phase 1, the sweep (09:06-11:57, 117 agents in four workflows).**

    P0 (lead)   a derived facts sheet: the counts and bits several
                documents state, each with the command that derives it;
                a ledger with urgent/
    round 1     15 read-only auditors, one per document group; their
                findings in chunks of up to 8 to 47 verifiers told to
                refute; one coverage critic                       63 agents
                303 findings: 193 confirmed, 89 amended, 14 to the lead,
                7 refuted; 291 applied by the lead into a worktree
    review      12 reviewers of the lead's own applied diff (11) and of
                the widened docs gate (1)                         12 agents
                85 document fixes, 17 gate issues
    round 2     15 triage auditors on the verifiers' 314 side notes and
                the critic's findings, 15 verifiers              30 agents
                324 items: 51 findings, 49 applied
    round 3     6 checks and 6 verifiers on round 2's side notes 12 agents
                6 of 6 real; the loop ran dry
    landed      080fe30, 5541aa8, 2ca3754, f6cf3bc, 0aede0f on main:
                432 corrections; the docs gate widened, with 32 planted
                controls and a mutation test (29 of 29)

**Phase 2, the four follow-ups (12:29-00:22, 28 agents in five
workflows).** Eight parcel agents under seven names (P1's comment work was
split by directory into P1-rtl and P1-host), each in its own worktree,
each followed by a verifier; a send-back became a fresh fixer and a
re-check scoped to the verifier's defects. Merges were serial, in
batches, on a staging branch in its own worktree; main moved once, at the
end.

| wave | parcel | job | verdict |
|---|---|---|---|
| 1 | P1-rtl | comments in rtl, hw, formal, tb, python (13 files) | MERGE |
| 1 | P1-host | comments across host/ (29 of 44 notes) | SEND-BACK 2 -> MERGE |
| 1 | P3 | the software handle's capability word | SEND-BACK 1 -> MERGE |
| 1 | P4 | the runner counts a skip inside a passing stage | SEND-BACK 2 -> MERGE |
| - | lead | the documents that quoted what wave 1 changed (cf8f00f) | gates and CI |
| 2 | P1b | comments in the three files P3 changed; two generators write LF | MERGE |
| 2 | P6 | CFT_NO_PROGRAM and CFT_TINY compile again, and every profile is compiled | SEND-BACK 2 -> MERGE |
| 2 | P2 | the Node module and both published pages rebuilt in the pinned container | SEND-BACK 2 -> MERGE |
| 2 | P7 | the skip lines the runner could not see | SEND-BACK 2 -> MERGE |
| - | lead | four claims no parcel owned, a silent drop made loud, two skip lines (1ab44ad) | gates and CI |

Six send-backs and eleven defects. All six re-checks returned MERGE -
including P7's, which passed a small overclaim in its own fix's comment
and commit message and noted two gaps outside its diff, one of which the
lead's seam closed. The overclaim and the other gap are still open on
main, with at least seven other notes the verifiers left (§6 below). Two
of the eleven defects came from the lead's own mid-round grant and
ruling.

## Timeline (local time, PDT; 2026-09-24 unless marked)

Times are from the transcripts' own stamps, git author dates, file
mtimes and `gh run list`. A verifier's verdict time is the last line of
its own transcript, because the workflow journal carries no times.

| when | what |
|---|---|
| 08:32 | The request. By 08:36 a plan with four questions for the owner; 24 minutes waiting for the answer. |
| 09:00 | The owner's decisions: straight to main, widen the gate, no planted faults, the clock as 175 MHz assumed. |
| 09:04 | The facts sheet written (P0) and the sweep's ledger created. |
| 09:06 | **Round 1 dispatched**: 63 agents in one workflow. |
| 09:10-09:19 | The lead widens the docs checker **in the main checkout the auditors are reading**. An auditor runs it and posts at 09:14 that the docs stage "FAILS at HEAD" - the lead's uncommitted edit. The lead's urgent note at 09:18; the ledger watcher armed at 09:18, twelve minutes after dispatch. |
| 09:19 | The lead tells the owner it "disabled each check in turn and watched its controls go red". It had disabled its three new ones; nine checks had no control at all (found by the gate reviewer, below). |
| 09:21-09:30 | Three auditors correct the facts sheet through the ledger: the CAPS2 row (09:21), the make targets (09:22), the host tools (09:29). Each is fixed in the sheet within two minutes. |
| 09:50 | The owner: "Let the verifiers finish before you apply anything." 113 of 303 verdicts were in. The applier was written and still aimed at the main checkout the verifiers were reading; the lead had created a worktree 6 s before the message and repointed the applier to it 8 s after. Nothing was applied until the workflow ended. |
| 10:12 | The owner asks how the method is working; the lead names four of its own mistakes and proposes seven changes. |
| 10:19 | **Round 1 ends**: 303 findings - 193 confirmed, 89 amended, 14 to the lead, 7 refuted - and 314 side notes. |
| 10:22-10:26 | 291 edits applied in a worktree; the runner prints "PASS, nothing skipped" over a stage whose log skipped a check - the seed of follow-up 4. |
| 10:27-11:07 | **The review workflow** on the lead's own work: 85 fixes to the applied diff - 42 filed as contradictions with a neighbouring sentence, most of them sentences a correct edit had left stale; among the others, 13 more half-applied amendments (14 in all), 3 broken code blocks, damaged lists and 2 bad overrides - and 17 gate issues, headed by nine checks with no planted control. |
| 11:18, 11:23 | 080fe30 (376 corrections) and 5541aa8 (the gate: 32 planted controls, 29 of 29 mutations killed). |
| 11:24 | Round 2 crashes 21 ms after launch: its work list was passed as the string `__FROM_FILE__`. Relaunched 33 s later. |
| 11:45 | Round 2 ends: 324 items, 51 findings, 49 applied (2ca3754, 11:46). |
| 11:47-11:52 | Round 3: 6 candidates, 6 real. f6cf3bc at 11:53. |
| 11:55-11:57 | 0aede0f (the VALIDATION entry), main pushed, records copied, the four follow-ups offered, the report. |
| 12:20, 12:21 | "Go ahead and tackle the 4 left open"; "You may start docker here". **The last human message for 15 h 39 min.** |
| 12:26 | The 179 notes split into work-lists by owner; the lead's comment-only checker written (14 self-test cases). |
| 12:29 | **Wave 1 dispatched**: P1-rtl, P1-host, P3, P4, each followed by a verifier. The lead's watcher armed 8 s later. |
| 12:30-12:53 | **Six messages through urgent/** - four corrections of the brief and two reassignments - each within 10 to 68 s of the parcel's entry reaching the lead: the build line lacked `TMP`/`TEMP` (12:31); the test targets need `.exe` (12:33); `host/tests` was given to two parcels (12:39); the comment checker cannot read SystemVerilog (12:41); IMUL's dead capability branch goes to P3 (12:50); the replay's own skip lines go to P4 (12:53). |
| 12:52 | The clock-sweep session commits 3b15d52 to main in the shared checkout and pushes; per-ref concurrency cancels the sweep's own CI run at 12:53. The lead notices at 13:30. The sweep's commits were only ever CI-tested inside 3b15d52's run, green at 14:37. |
| 13:00 | P3 finds that `-DCFT_NO_PROGRAM`, and so the tiny profile, has not compiled under gcc 14 or later since 2026-09-14. It becomes P6. |
| 13:01, 13:07 | P1-rtl MERGE; P1-host SEND-BACK (a comment it wrote was false since 7b3c10c; a refusal it described holds only on XRT). |
| 13:29 | The lead's watcher expires. It is not re-armed until 17:23. |
| 13:30 | The lead reads P1-host's SEND-BACK from the journal and reports it to the owner, then waits for the whole wave before sending it back. |
| 14:52 | P3 SEND-BACK: it wrote that the committed module reports 0x671f; the verifier measured 0x271f. |
| 15:08 | P4 SEND-BACK: with `FORCE_COLOR=1` pytest paints `SKIPPED` and the new scan counted nothing - seven real skips passed `--require-all`. Wave 1 ends after 159 minutes, because the slowest verifier took 111. |
| 15:09 | **The lead tries to send the three parcels back through SendMessage, as METHOD §8 says. All three fail: "could not be resumed: No transcript found for agent ID".** |
| 15:11 | The comment checker's third version: 32 self-test cases, on which the second was wrong 10 times. |
| 15:12 | The send-back workflow: three fresh fixers, each followed by a scoped re-check. P4's fixer, which also carried two items the lead added, takes 106 minutes. |
| 17:16 | All three MERGE. |
| 17:17 | The lead creates the staging branch in the shared checkout, realises from the fetch that the other session commits in that same checkout, switches back and deletes the branch 12 s later, and makes it in a worktree. Four merges within two seconds (P3 squashed); 0 conflict markers. |
| 17:21-17:22 | cf8f00f, the lead's seam; staging pushed; the gate budget and CI started. |
| 17:23 | **Wave 2 dispatched**: P1b, P2, P6, P7, each followed by a verifier. Its brief carries wave 1's corrections. |
| 17:36-18:16 | Ten urgent messages - eight from the lead, two parcels' escalations. P2 reported that its named negative control could not fail, because `verify.mjs` never read the sample the control corrupts; it proposed its own replay as a disclosed stand-in, and the lead granted a real gate 55 s later (17:40-17:41). P7 found `cpp-api-test` passing a malformed vector set as "no vector sets" (18:16, granted 30 s later). Among the lead's own: the grant for P6's refusal (17:44) and a ruling on P7's skip summary (17:46). |
| 17:59 | P2 finds that the WebSocket replay has been silently dropping every published case whose op name the client could not send - every imul case in its sample. |
| 18:23-18:26 | The lead runs P6's profile check under gcc 13 in a container (the compiler CI uses). |
| 18:46, 18:49 | P1b MERGE; P6 SEND-BACK - **the lead's own grant** keyed the new refusal on the format ceiling and so refused a working build. |
| 18:57 | The watcher expires again; it is not re-armed for the rest of the round. |
| 18:58 | P6's send-back launched as its own workflow while wave 2 still runs. |
| 19:00-19:10 | CI green on cf8f00f; the local gate 34 of 35, the failure (`lang-rust`) shown identical at the base commit, golden's three desktop skips named on the VERDICT line. |
| 19:44 | P6 MERGE. |
| 19:56, 20:01 | P7 SEND-BACK - **the lead's own skip rule** let one device-test run count the same missing capability both ways; P2 SEND-BACK - a false history of the old module's LANE_MASK bit. Wave 2 ends after 158 minutes. |
| 20:01-20:02 | The lead rules the skip accounting; the P2 and P7 send-back workflow launched with the full defect lists; P1b and P6 merged. |
| 20:02-20:04 | **The lead's context is compacted automatically**: 968,139 tokens to 20,900. It carries on from the summary with the seam checks. |
| 20:08 | The seam makes P2's silent drop a named failure: the new check is watched failing on the pre-P2 tree - "not sent: imul (66 cases)". |
| 20:22, 22:13 | P2 MERGE; P7 MERGE (its fixer 88 minutes, its re-check 44). |
| 22:14-22:18 | P7 and P2 merged; 1ab44ad, the lead's second seam; staging pushed; the gate chain and CI started. |
| 23:40 | CI green: the host job's 22 stages under `--require-all`, 0 inner skips. The local gate 34 of 35 again, as at 19:09. |
| 00:20 (09-25) | `node` and `wasm`, which the gate budget leaves out, PASS. |
| 00:22 | 987ee41 (the VALIDATION entry); main fast-forwarded and pushed; the push deploys the public Pages site; the live pages checked byte for byte against the committed ones at 00:24. |
| 02:02 | Main's CI green; **the final report**. |
| 04:00 | The owner returns. |

## What the system caught

**In the sweep, mostly the lead.** The verifiers on the auditors did the
work the method expects - 89 amendments to proposed text, refutations
that fell on the auditors' least confident findings (5 of 33 low, 2 of
133 medium, 0 of 137 high). But the most consequential catches were of
the lead:

- **The facts sheet**, the round's P0, went out unverified and was wrong
  three times; auditors corrected it through the ledger within 23 minutes
  of dispatch.
- **Six brief premises** were wrong, among them that `docs/BITSTREAM.md`
  does not exist (it does, in the sibling repository cft-rebound), that a
  generated file was generated end to end, and where eight keywords live.
- **The lead's applier** replaced only the original quote where a
  verifier had widened the span in prose (14 half-applied sentences),
  re-filled paragraphs into three code blocks - two of them build commands
  that would then have built at the build script's 10 MHz default, the
  project's first documented trap - and damaged lists.
- **Two lead overrides** (E-18, E-19) put back the construction their
  verifier had removed: an assumed clock written as measured, which the
  lead's own facts sheet forbade.
- **Seven applied edits** each left a neighbouring sentence contradicted
  that the finding's own verifier had pointed to - two verifiers had said
  the edit could not stand alone, two that its neighbours had to move with
  it, one left it to the lead, two called it a separate fix.

The applier's damage, the overrides and the contradictions were found by
the review workflow: twelve agents who read the lead's applied diff and
gate against the verifiers' findings, the facts sheet and HEAD. The
lead's own structure check had caught the re-fill starting lines with a
dash - seven stray list items in six files - and it had fixed the
re-filler and re-applied every edit before them; they found the rest. It
was the highest-yield step of the day.

**In the follow-ups, eleven defects in six send-backs.** Eight were false
sentences - in a comment, a document or a commit message - and four of
those were in published documents the parcels had written about their
own change; one was a number transcribed instead of measured (0x671f;
the module said 0x271f). By origin, the other three were a gate that
could not fail and the lead's own grant and rule - a grant that refused a
working build, and a rule that counted one capability two ways - though
both of those also reached documents the parcels wrote (EMBEDDED.md's
row, verify/README.md's list).

**Five gates that could not fail, and were fixed**, each in a script
that existed to say "nothing was missed":

1. the new inner-skip scan read a coloured log, so `FORCE_COLOR=1` passed
   seven real skips under `--require-all` (P4's verifier);
2. the published page's negative control: `verify.mjs` never read the
   embedded sample the control corrupts, so the broken page passed steps
   1 to 4 (P2, reported through urgent/ with a disclosed stand-in; the
   lead granted a real gate);
3. `cpp-api-test` passed a malformed vector set as "no vector sets" and
   exited 0 (P7);
4. `device-test` said "agree on every case" over a leg it had skipped
   (P7);
5. the WebSocket replay dropped every case it could not name (found by
   P2 and flagged again by P7; the lead's seam made it a named failure,
   watched failing before P2's change and passing after).

Others were found. Some were fixed in the parcels' own work: the cpp and
remote replays printed no report, so a set skipped there reached no log
(P4 at 13:15, fixed in P7's 1420e54). Some were left open: the
generators' `--check` compares newlines loosely and passed a CRLF header
(P1b), and two of the re-check notes in §6 below (the stray-line check's
overclaim and `remote_test.c`'s silent skip). The lead's comment-only
checker, the instrument three parcels were certified by, was wrong twice
before it was right: its first version read a SystemVerilog tick as a
quote (P1-rtl found it), and its second dropped statement-leading
strings in Python, missed a Makefile comment's continuation and stripped
pragma comments like prose (the P1 verifiers found those).

**Two real defects in code no parcel was asked about.** The tiny and
no-sequencer profiles had not compiled under gcc 14 or later since
2026-09-14, because no runner stage or CI job built them - the documented
`make embedded` gate that does has no recorded run since 2026-09-09
(found by P3 at 13:00, fixed by P6). And P6's scratch compile of each build
switch on its own found a stack overwrite the first time it was run: a
narrowed bignum with the transcendentals on copies 34-limb constants into
it. The lead's grant made the library stage's profile check compile every
switch and assert the refusal; it is refused by name now.

**The brief-errors field returned 57 items from 14 reports**; the build
line and the `.exe` names were each reported by all four wave-1 parcels.
The ones that mattered most: the lead's premise that CI skipped a check
(stages run in file order; it did not), the fix a brief placed in the
wrong function, and the negative control that could not fail.

## Observations against the method

**§8, contradicted: a send-back could not resume the parcel, so it needed
a re-brief.** METHOD says a send-back needs no re-brief because the
harness resumes the agent. Round 2's parcels were spawned one at a time
and could be resumed; this round's were spawned by workflow scripts, and
SendMessage to all three wave-1 parcels failed with "No transcript found
for agent ID". Every send-back became a fresh fixer, briefed by the lead
with the verifier's defects, the parcel's ledger file and its worktree,
followed by a scoped re-check - three fixer scripts the method had said
would not be needed. The time was in line with the method's estimate of
half an hour of parcel and half an hour of verifier: fixer plus re-check
averaged 57.6 minutes a send-back (medians 21.9 and 11.5), and the two
long fixers (106 and 88 minutes) carried scope the lead added - P4's an
audit of the CI stages, P7's the new skip rule across device-test. The
fixers were not given the parcel's final report, which the lead had in
the journal; its ledger file and its commits were their only memory of
it.

**§8, a workflow reports when its slowest agent finishes.** A ready
verdict waits for its siblings: P2's re-check said MERGE at 20:22 and was
reported at 22:13, together with P7's, while the lead sat idle and
unwatched. P1-host's case looks the same and is not: its SEND-BACK was
final at 13:07 and its fixer started at 15:12, but the lead had read the
verdict from the journal at 13:30 and chose to wait for the wave. Five
completion notifications were also truncated, and the lead read the
journal directly four times instead. Scripting the whole loop per parcel -
parcel, verifier, fixer, re-check - would remove the structural wait,
and also the lead's chance to add a ruling between verdict and fix; the
P4, P6 and P7 fixers each carried one. It would do nothing for truncation;
the journal is the reliable read.

**§4, the lead's watcher: what it bought, what it cost, and when it was
down.** A watch in this harness lasts at most thirty minutes. All eight
parcels armed one within half a minute of starting (P4 with a background
shell loop), and their watchers re-armed on expiry within seconds to
nine minutes, except at the very end of two parcels' runs. The lead's
lapsed twice without being re-armed, and its watch covered 26 percent of
the follow-ups' agent-active minutes. Eleven of the 49 follow-up entries
were never delivered to it - eight of them the fixers', which were all
written while it was down. Nothing was lost, because the report schemas
required the same substance - brief errors, findings for the lead - and
it came back with the verdicts. Six of the eight parcels never used
urgent/; all eight asked the lead questions in their own files, and each
was answered while the watch happened to be up. What the watch bought
was latency: every correction in the timeline went out within 10 to 68
seconds of the parcel's entry reaching the lead (in wave 1, 27 to 74
seconds from the entry being written), and in the sweep it turned three
facts-sheet corrections around within two minutes. What it cost is that
each notification wakes the lead and re-reads its whole context, which
reached 957,455 tokens before the compaction. Over the lead's work,
turns started by watcher events were 33 percent of its cache reads for
10 percent of its output; turns started by expiries add 13 percent, but
they include real work - one began applying round 1, another launched
P6's send-back. In the sweep's first thirty minutes of watching, 36
calls read 11.4 million cached tokens: twenty single-call
acknowledgements - twelve of them "nothing needed from me" - were over
half of that, the three facts-sheet corrections about a quarter, and a
check of an auditor's claims about CLAUDE.md the rest.

**§4, stamps.** Where a brief said to take the time from `date`, 5 of 38
watched parcel entries still carried typed stamps; all five were
corrected by their authors, and two were off by more than a minute (18
minutes ahead, 4 behind). None of the three send-back scripts stated the
rule, and 5 of the fixers' 6 stamps were typed. The rule - substitute,
never type - is what held. But round 2's supporting evidence, that every
guessed stamp ran ahead of the clock, does not: most did here; two ran
behind, both by about four minutes. The sweep's ledger README had stated the
rule; the follow-ups' README, a verbatim copy of `templates/ledger.md`,
does not, because the template does not.

**§4, the ledger's end.** The lead kept no file of its own in the
follow-ups: its rulings live in fourteen urgent messages and the
transcript. The copy of the sweep's ledger kept in the project reset every
mtime to the copy's time; the working copy survived long enough to be
archived with its times, so the loss was a near miss. In the follow-ups,
the lead's replies are timed by the urgent/ files' mtimes and the
parcels' entries by the watcher's notifications in the transcript, since
a per-author file's mtime is only its last append.

**§5 and §7, the lead's work through a verifier.** The method says the
lead's code goes through the same gates as a parcel's and, where it is
more than a line, through a verifier. The sweep did that for its applied
diff and its gate, and the review workflow found 102 issues. It did not
do it for its records, and the follow-ups did it for nothing of the
lead's: cf8f00f, 1ab44ad (nine files, code among them) and both
VALIDATION entries went through gates and CI only. The lead's own
re-reading caught one wrong line in each VALIDATION entry. The sweep's
entry and commit messages still disagree with the records in places no
agent checked: two counts (the critic's "12" findings routed to round 2
were 10; "all 53 tracked files in full" was 52 documents and a data file,
six of them read in part by scope, and the append-only record itself not
audited), an unearned "each verified" (85 reviewer fixes were applied
without a second check), one brief error recorded of six, and in the
commit messages "326 items" for 324. The follow-ups' entry and the final
report disagree with the record too: they say nothing built the tiny
profiles (`make embedded` does, when run), and they credit the library
stage's profile check with finding the stack overwrite that P6's scratch
per-switch compile found.

**§6, a verifier per parcel paid again - and its side notes had nowhere
to go.** Eight verifiers, six send-backs, eleven defects, no verdict
that was a false alarm, and no MERGE since found wrong. Two defects came
from grants and rulings the lead posted to urgent/ mid-round. Those
reached the verifiers as required reading, but no item on their list
asked for them to be checked; METHOD's list names "the seam paragraph,
the plan's premise", not decisions made after dispatch, and both were
caught through the parcels' diffs. The verifiers' and re-checks' notes
beside their verdicts were read by the lead selectively, and at least
nine are still open at 987ee41. P7's re-check passed a small overclaim
in its own fix - the stray-line check's comment and commit message claim
more forms than its pattern catches - and noted that `remote_test.c`
skips, without a word, any segmented-reduction opcode the server does
not serve. P6's re-check noted that EMBEDDED.md says every switch is
compiled on its own, which is not quite what the target does. Five of
P1-rtl's verifier's notes are still stale comments: a Dockerfile's
pointer to a BRINGUP gate, a Makefile's claim about packaging, an opcode
labelled unassigned in a formal testbench, and two formal files that
describe a proof the formal run never completes and a differential it no
longer cites. And P7's verifier noted that the Node and page replays
print their report only on failure, so a set skipped inside a passing
replay reaches no log. The sweep had solved exactly this with a round
for side notes; the follow-ups had none.

**§7, published documents written by parcels.** METHOD keeps published
docs as the lead's. This round let parcels write the rows describing
their own change, and six of the eleven defects were false text in
exactly those rows - four by origin, two carrying the lead's grant and
rule. All six were caught: four by wave-2 verifiers whose list said
"check every claim in a comment, doc or commit message" (P2's caught two,
P6's and P7's one each), and two by wave-1 verifiers whose list said
comments and commit messages only - one widened its own list, the other
found it under "anything else".

**§7, freeze what is audited.** "Never merge while a suite is running"
is about suites. The sweep's version was an edit to the tree that
read-only agents were reading: it produced a false "fails at HEAD", and
ten auditors noted the uncommitted edit in their reports (three more
recorded running the lead's in-progress checker). Rounds 2 and 3 read
committed SHAs, and the follow-ups used a worktree per agent and a
staging worktree; it did not recur.

**§7, the merge discipline held, in batches.** One staging branch per
round rather than per merge; merges in batches of four, two and two; the
gate budget and CI after the first and last batches, the middle one
getting only the library and generator stages; main moved once. Two
things to say plainly. Both local gate runs ended `VERDICT: FAIL (1
stage)` on `lang-rust`; main moved on the strength of the same failure
reproduced at the base commit and CI's pass, and the VALIDATION entry says
so. And the gate budget is a subset: it leaves out `node` and `wasm`. The
lead chained them after the last batch, where P2 had changed them, but
not after the first, where P3 had changed `bindings/node` too and only
CI's host job ran them.

**§7, unattended decisions.** Within the standards, and deferred to the
owner where they were the owner's (the open questions at the end of the
VALIDATION entry). But some calls took effect before the owner could see
them: the rule for which skips count; crossings granted outside parcels'
files; the shared checkout fast-forwarded; and two effects beyond the
local checkout - the remote staging branch deleted, and the push to main
redeploying the public Pages site. The lead checked the live pages byte
for byte; it had not asked beforehand whether a deploy was wanted.

**The shared checkout.** Two sessions committed to one repository at
once, and nobody had told the lead. It inferred at 08:35 that another
session commits to the repository, and only at 17:17 - after switching
the shared checkout to a new branch - that the other session committed
in that same checkout; before then, the sweep's checker edits and its
11:56 push were made there. The collision cost little: the branch was
created and deleted within twelve seconds, and every parcel was already
in a worktree. The harness made each wave-2 worktree from the session
checkout's HEAD - 3b15d52, the other session's commit - so the wave-2
brief had every parcel fast-forward to the staging branch and check the
SHA (P2's first git output: "Updating 3b15d52..cf8f00f"). The less
obvious hazard was CI: with per-ref concurrency, the other session's
push cancelled the sweep's own run, and "cancelled" reads like nothing
happened; the lead noticed 37 minutes later.

**Compaction mid-round.** At 20:02 the lead's context was compacted
automatically, from 968,139 tokens to 20,900. The round did not lose its
place, for two reasons: the send-backs had already been launched with
their full defect lists before the compaction began, and the summary
carried the state. The lead went straight back to its seam checks,
consulted the journals when writing the VALIDATION entry, and did not
re-read the ledger. The one item the summary had truncated had already
been acted on.

**Where the wall clock went.** The follow-up phase was 13 h 42 min; the
lead was inside a turn for about an hour of it. The rest was agents and
gates, and much of the agents' time was the same long stages run again by
the parcel, its verifier, the fixer and the re-check on nearly the same
tree (inferred: the longest agents were a verifier at 111 minutes, a
fixer at 106, two parcels at 104 and 101; the runner's `node` stage
alone takes 22 to 38 minutes). The runner has no cache - a fresh
invocation reruns everything - so each role paid it in full. The same
waiting shows in the token record: agents' prompt caches last five
minutes, and 76 percent of the parcels' and fixers' cache writes came
after a pause of five minutes or more; the lead's last an hour, and 66
percent of its cache writes followed a gap of an hour or more.

## What the lead got wrong

Recorded because most of the proposals below come from these, and
because the method's claim is that it makes the lead's errors visible.

1. **Dispatched a P0 nobody had verified.** The facts sheet every auditor
   checked against was wrong three times.
2. **Edited the tree under audit** while 63 agents read it, and wrote its
   applier against that tree; it created a worktree for the edits seconds
   before the owner's message stopped it applying before the verifiers
   had finished.
3. **Overclaimed to the owner**: "disabled each check in turn" when it had
   disabled three, with nine uncontrolled.
4. **Wrote an applier that could not apply what the verifiers wrote**:
   half-applied amendments, re-fills into code blocks and across list
   items.
5. **Overrode one verifier's two amendments** (E-18, E-19) with the
   construction it had removed, and applied seven edits that left a
   neighbour contradicted which the findings' verifiers had pointed to.
6. **Launched a workflow with its work list as a placeholder string.**
7. **Wrote a Windows build line without `TMP`/`TEMP`**, three minutes
   after reading the runner function that passes them; the test targets
   without `.exe`; `host/tests` into two parcels' ownership.
8. **Certified parcels with a checker that was wrong twice.**
9. **Put wrong premises in most of its briefs** (57 brief-error items from
   14 reports). The three that mattered most: that CI skipped a check,
   where a swallowed report was dropped, and a negative control that
   nothing read.
10. **Issued a grant and a rule that were each wrong**, caught only because
    they surfaced in parcels' diffs.
11. **Did not know the checkout was shared**, and created a branch in it.
12. **Let its watcher lapse** from 13:29 to 17:23 (3 h 54 min) - from the
    middle of wave 1's verification through its send-backs - and for the
    rest of the round from 18:57.
13. **Waited an hour and forty minutes on a send-back it had already
    read** (P1-host), for the wave to finish.
14. **Wrote records that disagree with its own data** (in the sweep's
    entry: two wrong counts, an unearned "each verified", one brief error
    of six; in the follow-ups' entry and final report: that nothing built
    the tiny profiles, and that the profile check found the overwrite),
    and put none of its follow-up records past another agent.
15. **Left the verifiers' side notes without a step to act on them**; at
    least nine are still open on main.
16. **Reported no cost** in the final report, and when asked, reported the
    harness's per-agent figure ("26.4M tokens") as tokens used. It is the
    sum of each agent's final context size; what was processed is in the
    table below.

## Cost of the round (measured from the transcripts)

Two measures, because they answer different questions. The **harness
figure** is what each Workflow call reports as its tokens: it is the sum,
over the run's agents, of each agent's context size at its final request.
It reconciles exactly with every run's state file, and it is the
comparable figure if round 2's agent cards showed the same field (which
cannot be determined from these sources). The **processed** figures are
summed from every API response in the transcripts, de-duplicated by
message id (taking the largest output count among a message's lines):
output generated, and the prompt tokens written to and read from cache.

| run | agents | wall | harness figure | output | cache read | tool uses |
|---|---|---|---|---|---|---|
| sweep round 1 (audit, verify, critic) | 63 | 72.6 min | 11,005,330 | 2,823,051 | 506.5M | 3,356 |
| sweep review | 12 | 40.2 min | 2,604,860 | 660,113 | 84.2M | 607 |
| sweep round 2 (failed launch) | 0 | 21 ms | 0 | 0 | 0 | 0 |
| sweep round 2 | 30 | 20.1 min | 4,159,386 | 908,320 | 115.5M | 1,096 |
| sweep round 3 | 12 | 5.3 min | 865,461 | 71,879 | 6.7M | 114 |
| follow-ups wave 1 | 8 | 159.1 min | 2,534,155 | 857,679 | 252.5M | 1,280 |
| wave 1 send-backs | 6 | 124.7 min | 936,852 | 250,089 | 45.5M | 374 |
| follow-ups wave 2 | 8 | 157.8 min | 2,964,499 | 1,020,817 | 391.5M | 1,625 |
| P6 send-back | 2 | 46.2 min | 399,986 | 127,077 | 21.2M | 149 |
| P2 and P7 send-backs | 4 | 131.7 min | 950,522 | 293,292 | 82.5M | 434 |
| **145 agents** | | **2,087 agent-min (34.8 h)** | **26,421,051** | **7,012,317** | **1,506M** | **9,035** |
| the lead (the work, 464 API calls) | | | | 491,119 | 227.6M | 468 tool calls |

The agents also wrote 41.0M tokens to cache and the lead 3.2M; uncached
input was negligible (16,922 and 1,078). The agents produced 93.5 percent
of the round's output. Everything ran on claude-opus-5-5. The automatic
compaction's own request is not in these sums: no transcript line carries
its usage.

The follow-ups, per agent (wall from each agent's own first and last
stamp; output tokens; tool uses):

| agent | wall | output | tools | | agent | wall | output | tools |
|---|---|---|---|---|---|---|---|---|
| P1-rtl | 20.4 min | 89.8k | 149 | | P1b | 63.6 min | 136.6k | 255 |
| P1-host | 25.8 min | 123.2k | 247 | | P2 | 100.7 min | 180.8k | 307 |
| P3 | 88.0 min | 177.1k | 261 | | P6 | 60.7 min | 170.4k | 244 |
| P4 | 48.1 min | 158.3k | 218 | | P7 | 103.5 min | 190.6k | 335 |
| verify P1-rtl | 12.1 min | 62.2k | 72 | | verify P1b | 19.1 min | 76.7k | 118 |
| verify P1-host | 13.0 min | 64.8k | 91 | | verify P2 | 57.1 min | 76.4k | 130 |
| verify P3 | 55.6 min | 85.9k | 116 | | verify P6 | 25.1 min | 96.8k | 108 |
| verify P4 | 111.0 min | 96.4k | 126 | | verify P7 | 49.7 min | 92.6k | 128 |
| fix P1-host | 6.3 min | 32.0k | 51 | | fix P6 | 32.4 min | 95.0k | 98 |
| fix P3 | 5.4 min | 23.3k | 42 | | fix P2 | 11.4 min | 41.6k | 81 |
| fix P4 | 105.8 min | 104.1k | 129 | | fix P7 | 88.1 min | 165.1k | 211 |
| re-check P1-host | 5.4 min | 27.1k | 38 | | re-check P6 | 13.8 min | 32.1k | 51 |
| re-check P3 | 5.5 min | 21.0k | 34 | | re-check P2 | 9.2 min | 28.0k | 44 |
| re-check P4 | 18.8 min | 42.6k | 80 | | re-check P7 | 43.5 min | 58.5k | 98 |

**The checking share.** Verifiers and re-checks were 82 of the 145
agents: 41.4 percent of the harness figure and 36.9 percent of the
output. In the follow-ups alone, the same shape as round 2's, they were
38.3 percent of the harness figure - round 2 reported 38 percent - and
33.8 percent of the output. Counting every checking role - the sweep's
reviewers and critic too - checking was 52.5 percent of the harness
figure and 47.4 percent of the output. It produced every send-back, the
review's catches of the lead's applier and gate, and the catches of the
lead's grant and rule; auditors and parcels caught the lead's other
errors (the facts sheet, the tree under audit, the brief premises, the
comment checker's first version); the P1 verifiers caught its second. No
verdict was a false alarm; of the verifiers' 314 side notes, round-2
triage found 72 not to be defects.

**The wall.** 17 h 30 min from the request to the final report: the sweep
3 h 26 min (its workflows 138 minutes; 24 minutes waiting for the owner's
decisions), the follow-ups 13 h 42 min. Agent time was 2.0 times the
session's wall. At most ten agents ran at once; in the sweep's first
round auditors queued for up to 19.6 minutes for a slot and verifiers up
to 17.6. From the last verdict (22:13) to main moving (00:22) took
2 h 09 min of merging, seam work and gates; from main moving to the final
report, 1 h 40 min, nearly all of it main's CI.

**Other costs.** 139 dropped connections in the lead's session before the
final report, each retried (six minutes of backoff in all). One automatic
compaction. The owner's own time is not in these sources. Writing this
record took eleven more agents - four to gather, four to verify, three
to re-check - for 5,430,458 by the harness figure, 1,101 tool uses and
117 minutes of wall.

## What METHOD.md should say differently (proposed; the owner's to settle)

Each item says whether it is **new**, a **reinforcement** of a rule the
method already has (which this round broke or found under-specified), an
**extension** or **relaxation** of one, or a **reversal**; the evidence
is the section above it names.

**§3-§4, the brief and the ledger.**

- **Brief a send-back as a new agent when the dispatch cannot resume
  one** (reversal, for workflow-spawned agents, of §8's "a send-back needs
  no re-brief"). Give the fixer the parcel's final report as well as its
  ledger file and worktree; the lead has the report and this round's
  fixers did not get it. [§8 observations]
- **The stamp rule goes in `templates/ledger.md` and in every brief,
  fixers' included** (reinforcement of §4's "stamps are substituted, not
  typed", moved into the template). The verbatim template lacks it, the
  three fixer scripts lacked it, and 5 of the fixers' 6 stamps were
  typed. And correct the supporting claim: a typed stamp errs in both
  directions. [§4 stamps]
- **A parcel's question for the lead goes in urgent/** (reinforcement:
  `templates/ledger.md` already says escalating through urgent/ is what
  the channel is for). Put it in the brief as well: six of eight parcels
  never used urgent/, and all eight asked questions in their own files
  that were answered only because the lead's watcher happened to be up.
  [§4 watcher]
- **Archive the ledger from the working copy, with its timestamps**
  (extends §4's end-of-round rule). The project's copy of the sweep's
  ledger had reset every mtime; only the surviving working copy kept
  them. [§4 the ledger's end]

**§4, the lead's watcher.**

- **In a harness where every watch expires, the expiry notice is the
  moment to re-arm and do a full read** (reinforcement of §4's "re-arms
  and does a full read"). The lead did not, twice, and was down for the
  whole send-back phase. [§4 watcher]
- **The lead watches urgent/ continuously and reads the rest at set
  points** (reversal of §4's "Watch the whole directory, not just
  `urgent/`"), provided parcels put their questions in urgent/ as above.
  Each notification re-reads the lead's whole context; event-started
  turns were a third of the lead's cache reads, and the report schemas
  carried everything the lapsed watch missed. The lead still reads every
  author file at each wave boundary and before each merge, which keeps
  the cross-parcel view §4 wants. [§4 watcher; Cost]

**§5-§7, the lead's own work.**

- **The lead's seam commits go through a verifier before main moves**
  (reinforcement of §5's "the lead's code goes through the same gates as
  a parcel's, and ... through a verifier"), **and so do its records** -
  the VALIDATION entry and the commit messages (new). The sweep's review
  of the applied diff was the highest-yield step of the day; its records,
  which no agent checked, disagree with the data in at least five places.
  [§5 and §7]
- **The verifier's list includes the lead's grants and rulings issued
  after dispatch** (new, extending §6's list of the lead's artefacts). Two
  of eleven defects were in them; they were required reading but no item
  asked for them to be checked. [§6]
- **"Check every claim in a comment, doc or commit message" is on every
  verifier's list when parcels write docs** (extends §6's "a false claim
  in a comment is a finding"). Six of eleven defects were false text in
  parcel-written docs; the wave-1 verifiers, whose list lacked the item,
  caught theirs by widening it or under "anything else". [§7 published
  documents]
- **Give side notes a step of their own in every round** (new). The sweep
  triaged its verifiers' side notes and the critic's findings in a round
  and found 51 findings, 41 of them drawing on the side notes; the
  follow-ups had no such step, and at least nine notes are still open.
  [§6]
- **Freeze what is audited** (new): read-only agents read a committed SHA
  or a worktree the lead never edits. [§7 freeze]
- **Check a gate budget against the merged diff before trusting it**,
  after every batch, and when main moves on a verdict line that says FAIL,
  the record says why (relaxes §7's "the full suite after each one" for
  batched merges, and extends its "a merge with no RTL in its diff gets no
  RTL suite, and the ledger says so"). [§7 merge discipline]
- **The cost summary gives processed tokens beside the harness's figure,
  and says which is which** (new; the harness figure is final context
  size), and it is in the final report (reinforcement of §7's "the
  summary to the owner, with the cost"). [Cost; the lead's errors, 16]
- **Settle at kickoff what the owner may want to see first** (extends
  §7's "unattended, decide what the standards decide and ask for what is
  the owner's"): effects beyond the local checkout - pushes that deploy,
  deleting remote branches - and changes to how results are counted.
  Unattended, the lead cannot ask in time. [§7 unattended decisions]

**§8, sequencing.**

- **Decide, per round, whether the lead sits between verdict and fix**
  (new). Scripting parcel, verifier, fixer and re-check as one pipeline
  per parcel removes the structural wait for the slowest sibling; keeping
  the lead in between lets it add rulings, as it did for three fixers. And
  read verdicts from the journal, not the completion notice, which is
  truncated. [§8 observations]
- **Let a verifier reuse a run whose inputs are identical** (relaxes §6's
  "re-run the gate itself, from a clean build"): a run log keyed by the
  tree's hash, with the verifier re-running from clean what it doubts.
  With four roles per sent-back parcel each re-running the same long
  stages, the saving is estimated in hours, not measured. [Where the wall
  clock went]
- **A worktree the harness creates branches from the session checkout's
  HEAD** (reinforcement of §3's "the base commit, and an instruction to
  verify it"): when the round's base is a staging branch, the brief says
  `git merge --ff-only <base>` and checks the SHA, as wave 2's did. And
  when another session shares the repository, never switch its branch,
  and watch CI for "cancelled". [The shared checkout]

**A sweep is a round** (extends, and for a standalone sweep replaces,
§7's "the docs sweep, in the lead's idle time during the round").
Auditors are read-only parcels, one per document group; a verifier per
chunk of findings told to refute; the lead's applier verified by a
review workflow before anything is committed; the verifiers' side notes
collected in a schema field and triaged in a round of their own; repeat
until a round comes back nearly empty (here 303, 51, 6). Freeze the
tree, verify the facts sheet before dispatch, and give the applier's
replacement the exact span the verifier approved. [The shape of the
round; What the system caught]

## The round's end (2026-09-25)

**What was delivered.** Every tracked document except the append-only
VALIDATION.md (and the parts of ROUND2.md and the studies kept as
written) swept against the tree - 432 corrections in three rounds - and
a docs gate that holds every document's links, every live document's
quoted paths (the records exempt), the counts the four front-door files
state, and the index's totals, with a planted fault for every check.
Then the four follow-ups: the software handle's capability word made
true, and `cft_supports` answering for IMUL; the runner counting a skip
inside a passing stage, naming it on the VERDICT line and failing it
under `--require-all`, with one rule for what counts; the Node module
and both published pages rebuilt in the pinned container, byte-identical
across two clean builds, their embedded sample now gated, and the live
site serving them; every reduced build profile, and each switch on its
own, compiled in the library stage; and the stale comments made true -
each comment edit in P1-rtl's, P1-host's and P1b's files proved
comment-only (P1b's two generator changes and the vendored manifest
proved separately), and P2's, in files that also carried granted code or
that the checker cannot read, checked by its verifier by inspection.
Main at 987ee41, CI green, the Pages site checked byte for byte.

**What carries forward.** The owner's questions at the end of
cft-fp256's VALIDATION entry for the follow-ups: an empty last-error
string on the tiny profile; capability bits the Node module publishes
that no export reaches; the narrowed bignum's safe width; the embedded
replays and the skip-accounting test that no stage runs; a partial
vector directory that still passes silently; the generators' loose
`--check`, a missing `mpmath` dependency and refusal messages citing the
old program model; the desktop's own failures (golden's three skips,
`lang-rust`, the `/tmp` mount); and the layout catalogue still building
the single tile at 135 MHz. Two more: the sweep's own open note that
NOVEL.md entry 4's rule does not fit the fp32 column, which the
follow-ups' entry did not carry forward, and at least nine verifiers'
and re-checks' notes still open on main (§6). And the proposals above,
which are the owner's to adopt or not, as round 2's were.

**The ledgers** are archived at
archive/round3-ledger.zip (not in this kit): the sweep's
(twenty-six auditor entries, eleven triage entries, two urgent messages)
and the follow-ups' (forty-nine entries in twelve author files, sixteen
urgent messages), each with its original timestamps. The working copies
are deleted, as the method says.

## Postscript (2026-09-25, 07:58)

The owner read this and asked for the corrections and the nine notes the
same morning, and for the lead to make them alone, without agents, as a
small job. In cft-fp256, 0ae1c5e makes the notes of §6 true: each was
checked against the source before it was changed, and each code change
was watched to fire - a segmented reduction forced absent prints its
NOT COMPARED line and is counted by nothing, and the three skip-line
shapes the replay writes reach the log from a passing set and are
counted. 7d7285d appends a dated VALIDATION entry that corrects the two
entries this study found wrong, without editing them. The runner's
docs, formal, remote, node and wasm stages passed on the fixes with
nothing skipped. Where the text above says a note is "still open on
main", it describes 987ee41.
