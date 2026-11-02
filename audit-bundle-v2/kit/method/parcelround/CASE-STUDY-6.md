# A sixth round: the method run on itself, and a gate held to a threat model

Reconstructed after the round from its ledger and from the session's
transcripts. The ledger is archived beside this file as
[archive/round6-ledger.zip](archive/round6-ledger.zip). It
covers one round of one project, ParcelRound itself:
- the lead's P0, which built an adoption record and a gate over the method,
  and went past a verifier six times;
- four parcels, which brought METHOD.md's eight sections to the method as
  practised;
- a fifth, which compiled the templates from the result;
- an integration verifier on the lead's own work.

Every parcel's verifier worked on a copy that might hold planted faults. The
last sections propose what METHOD.md should say differently, which is the
owner's to settle, and record how the round ended.

## The setting

- **The project.** ParcelRound (github.com/loganw234/ParcelRound, MIT): a
  method for running parallel coding agents. It holds METHOD.md's sections 1
  to 8, five case studies of the rounds it was learned from, and four
  templates.
- **The job.** Bring METHOD.md to the method as practised. A fact-gatherer's
  survey, archived as `archive/round6-practice-survey.md`, read which of the
  case studies' proposals later rounds had practised, in cft-fp256's rounds
  and in rounds 4 and 5. The owner decided, through the question tool:
  - adopt everything practised;
  - restore the safeguards the practice had dropped;
  - parcels on Sonnet, verifiers on Opus;
  - an adoption file and a gate.
- **The plan of record** went past a verifier twice before the owner
  approved it: nine material defects on its first draft, ten on its second,
  all accepted (lead.md, 17:07:40).
- **What was new against rounds 1 to 5:**
  - the method gets a gate of its own, `tools/check_method.py`, and an
    adoption record, ADOPTION.md, one row per proposal;
  - the ledger is published, so it holds no absolute path: each dispatch
    message defines two roots, `<repos>` and `<scratch>`, and the ledger
    names places by them;
  - escalation runs over the runtime's messages, entry first, in place of
    `urgent/` and its watchers, and every parcel sends a test escalation at
    dispatch (S1 to S3);
  - every parcel designs first and stops, and builds only on "go" (B13);
  - every parcel's verifier works on a copy that may hold planted faults,
    under the three-commit protocol: the key's hash in the ledger before
    dispatch, the key itself after the report.
- **The models**, read from the transcripts: the lead and every verifier on
  Opus 5.5, the five parcels on Sonnet 5.5.

## Timeline (2026-10-02 into the 3rd, local time, UTC-7; from the ledger's own timestamps, and from the commits' times where a row says so)

| when | what |
|---|---|
| 17:07 | The round opens. P0 is on the round branch at `a5c0494`: case study 5's postscript; ADOPTION.md (113 rows); the gate (712 lines, 10 checks, 11 controls); the practice survey; METHOD.md's preamble. |
| 17:08 | verifier-P0 dispatched. |
| 17:44 | verifier-P0: NOT READY, six defects. Of its 84 faults, 47 caught; of the 37 that passed, 25 lay outside every limit the gate stated. All accepted. |
| 18:19 | P0's first fix, `e9154be`; 26 controls. |
| 18:43 | verifier-P0: NOT READY. The fix had regressed the path pattern; a 29th pattern loganw.dev reads was missing; gaps were stated by their instances. |
| 18:58 | Second fix, `55e8a15`: each limit stated by the behaviour it concedes; 42 controls. |
| 19:25 | verifier-P0: NOT READY, narrowly. Four faults outside every statement, one the last shape of the regression. |
| 19:41 | Third fix, `186e7ab`; 47 controls. |
| 21:05 | The owner: the gate states its threat model, and verifier-P0's fourth pass is its last. |
| 21:11 | verifier-P0: READY on `186e7ab`; NOT READY on the threat-model commit `33fb047`, for one defect inside the model. |
| 21:19 | verifier-P0: READY on `2e34bd1`, a scoped re-check. Wave 1 dispatched, phase 1 only: P1 (sections 1 to 3), P2 (4), P3 (5 and 6), P4 (7 and 8). |
| 21:35-21:40 | All four test escalations arrive as runtime messages. |
| 22:00-22:15 | The four designs reviewed; thirteen brief errors confirmed at their sources. P3 finds a gate control that cannot fail; the lead fixes it at `1dc5ed4`. |
| 22:16 | verifier-P0: READY on `1dc5ed4`, scoped. "Go" to all four. |
| 22:23-22:35 | The four parcels report. The lead audits each and dispatches its verifier on a copy that may hold planted faults. |
| 22:48-23:03 | The four verifiers report. Each catches both of its planted faults: eight of eight. |
| 22:53 | The lead reveals three keys while verifier-P4 is still working. |
| 22:55-23:08 | P1 to P4 merged, each followed by the lead's restates; the lead's integration and gate commits (the commits' times). |
| 23:09 | P5 dispatched on the templates, from `56df604`. |
| 23:16 | ADOPTION.md's sixty wave-1 rows adopted at `fe58489`; verifier-I dispatched on wave 1's integration. |
| 23:47-00:18 | verifier-I: NOT READY three times on the lead's own work. Nine restates (23:47), two of them still open (00:06), then one phrase (00:18); fixed at `5c19906`, `e5ce41e` and `6975994`. |
| 00:06-00:11 | P5's design reviewed and approved; the lead's `a30aca5` before it builds; "go". |
| 00:21 | P5 reports. |
| 00:23 | verifier-P5 dispatched on a copy that may hold planted faults. |
| 00:45 | verifier-P5 reports: both plants caught, ten of ten in the round. |
| 00:47-00:48 | P5 merged, and the lead's restates after it (the commits' times). |

## What the method predicted, and what happened

1. **A verifier loop over a gate did not end by itself, and stating its
   limits by behaviour was not enough to end it.** Case study 4 found that a
   verifier loop over a spelling rule does not end by itself (obs 15), and
   that a limit stated by the faults that found it lets a fault of another
   kind through (obs 21). P0's gate went through four passes in four hours.
   - The first found 30 faults outside every stated limit, 25 in its
     84-fault run and 5 in separate runs (17:44:01). Its
     ruling already asked for limits stated by the behaviour they concede,
     but the docstring still listed what had been found.
   - The second found a regression, and gaps stated by their instances
     (18:43:31).
   - From the second fix on, the limits were written by behaviour, and the
     third pass found four faults outside every statement (19:25:28).

   Each pass found fewer, and each found something. By the lead's
   assessment to the owner, the third pass's findings were mostly shapes no
   honest author writes. Three passes had cost about 1.38 M subagent tokens,
   and the gate had grown from 712 lines to 1,563 (21:05:47).

2. **A threat model ended the loop, and its last pass found a real defect
   inside it.** At the lead's recommendation, the owner had the gate state
   a threat model (21:05:47), in words the lead wrote (`33fb047`): the gate
   guards against drift by honest authors and against accidental
   publication, not against deliberate evasion, nor does it judge content. A fault outside
   the model is out of scope; inside it, the gate must catch it or a limit
   must state it. Judged against that paragraph, the fourth pass found one
   defect inside it: the paragraph said the gate holds line numbers, and
   check 4 read them only in ADOPTION.md (verifier-P0, 21:10:30). It was
   fixed, not scoped down, and a scoped re-check closed it (21:19:10).

3. **The verifiers' real findings in the parcels' own text were
   overreach.** With evasion out of scope, the verifiers' list put content
   first. Besides pointers to other sections that held once every parcel
   had merged, and an older sentence that a new one now contradicted, each
   real finding in a parcel's own text was a sentence wider than its
   source, which the gate does not judge:
   - "the lead decided" in six rounds, cited for three (B13);
   - "the lead judged READY", where the verifiers did (CS4#7);
   - briefs that "say only "append only"", where the cited brief also has
     the stamp rule;
   - a known limit that "concedes no wrong answer", where the source says
     "none gives a wrong answer today";
   - a citation of 20:01 for an event at 19:56;
   - "a gate" at the tip, where the staging branch it relaxes had the full
     suite (S4);
   - "a bare hash", where the source says SHA-256.

   None was a wrong answer of a parcel's own making, so no parcel went
   back; the round's one wrong answer was the lead's (obs 4). The lead restated each at the merge, in a commit of its own after
   it (22:53:58, 23:06:11).

4. **The round's one wrong answer was the lead's own ruling, and a verifier
   found it.** P4 disclosed that "the case study" among the lead's records
   adopted part of CS5#11, which is pending, and the lead ruled "keep it"
   (D1, 22:00:23). verifier-P4 found it under its list's "a pending item
   written as adopted" (23:03:09). A second ruling of the lead's, P3's
   decision 3 at 22:15:07 to keep "it concedes no wrong answer", was one of
   verifier-P3's restates.
   - Neither ruling was on the verifiers' list as an item to check:
     briefs/_verifier.md had them read lead.md, not check it.
   - That is round 3's pattern exactly ([CASE-STUDY-3, §6]): the lead's
     rulings reached the verifiers as reading, and were caught through the
     parcels' text.
   - This round adopted the rule that came of it, that the lead's rulings
     after dispatch are on the verifier's list. This round's own verifier
     brief did not have it (23:16:47). verifier-I's brief and verifier-P5's
     did.

5. **Planted faults: ten of ten caught, from the sources.**
   - **What was planted.** Each wave-1 copy held two faults: a figure
     transcribed wrong, and a rule changed against its source (widened,
     narrowed, made optional, or a pending item written as adopted).
   - **How they were found.** Each wave-1 verifier found both, classed each
     a wrong answer, and recorded both in a view formed before it read the
     parcel's file (verifier-P3 22:43:27, verifier-P2 22:43:52, verifier-P1
     22:47:18, verifier-P4 22:54:53).
   - **The reference copy.** Each then noticed that its two were the only
     places where the copy differed from the parcel's design, which design
     first leaves in the parcel's ledger file. So the faults were found by
     checking sources, and the design only confirmed them. A verifier that
     read the design first could have found every plant by comparison
     alone.
   - **Wave 2.** verifier-P5's copy held a template line tagged with a
     section that exists but does not hold its rule (the trap P5's brief
     names, which check 5 cannot see), and the escalation order reversed.
     It found both (00:45:48).

6. **The lead revealed keys while a verifier still worked.**
   - The 22:53:58 entry revealed three keys, with their plants' shapes,
     while verifier-P4 was still working on a copy built the same way.
   - verifier-P4's file shows that it saw the entry appear, that it had
     formed its two findings from the sources before it read the entry,
     and that it listed the keys by name only and opened none (22:54:53).
     The entry that records the findings is itself stamped after the
     reveal. Its grade rests on that record
     (23:06:11).
   - The shapes reached wave 2 as well, and not through the keys. The
     lead's entries that graded wave 1 described each plant in prose, and
     verifier-P5's brief has it read lead.md first.
   - Its dispatch told it so, and asked it to record whether it read them
     before forming its view (00:24:40). It had read them, and said so
     before any view (00:25:17).

7. **Every parcel corrected its brief.**
   - **Wave 1.** Thirteen brief errors from four parcels, each confirmed by
     the lead at its source between 22:00:23 and 22:15:07: four of P4's, one
     of P2's, three of P1's, five of P3's.
     - Most were the lead's own transcriptions: a line number, a count of
       rounds, a word no source holds.
     - One was wider than its case: "unrelated parcels need not wait",
       which the case supports only as "need not wait for its fixes".
   - **P5** listed eleven items under what its brief got wrong (00:06:17),
     eight of them errors in its brief and the shared text; the lead
     accepted them (00:11:29). One was the lead's
     own measurement: the finding that the templates' placeholders render as
     nothing on GitHub (21:21:12) had been measured on a shortened text. P5
     measured the files: 11 of brief.md's 44 placeholders vanished, and 9
     of verifier.md's 27.
   - Round 1 had twelve, from five parcels ([CASE-STUDY.md](CASE-STUDY.md)).

8. **A parcel found a gate control that could not fail.** P3 ran the
   gate's controls on its draft and got 47 of 48 (22:05:39). The control
   for a declared foreign pin that nothing names removed the pin from
   ADOPTION.md only. Once a parcel cited a cft-fp256 line beside the pin,
   as every parcel would, the pin was named and the control could not fail.
   The lead fixed the control before "go", and verifier-P0 confirmed it live
   both ways (22:16:02).

9. **The runtime's messages carried the escalations.** All five test
   escalations arrived, with no watch armed: wave 1's four within five
   minutes (21:35:40-21:40:37), and P5's at 23:21:14. P3's gate finding came
   as a message after its entry was written, entry first (22:05:39,
   22:06:22).

10. **A limit stated by its instances came back in the lead's own gate.**
    - All four wave-1 verifiers found that a citation whose observation
      number or section mark names a real but wrong item passes, while the
      docstring stated that concession only for minutes and phrases.
    - verifier-P3 found that a HonestFramework passage copied without its
      bold passed check 9. That is inside the threat model, and was neither
      caught nor stated. The lead's gate commit `6c83960` catches it, with a
      control the old gate fails.
    - verifier-P4 found that a link's text and its URL are never compared,
      so a URL naming another line passes. The lead stated it.
    - verifier-I then found the lead's new statement of the passage limit
      stated by its instance again, emphasis, and the new count reading less
      than check 9 says it reads. `5c19906` restated the limit, and
      `e5ce41e` widened the count's reach and added a 50th control.

11. **The published ledger held no absolute path, and the lead typed six
    values.** The ledger's README, every brief and every entry named places
    by `<repos>` and `<scratch>`. The gate's privacy scan of the ledger
    found no address, path or token (verifier-P0, 21:18:33). Three times the
    lead wrote into the ledger a value it had not read:
    - a time, "18:2x", corrected at 18:27:26 by two clock readings that
      bound it;
    - a commit, "8f-merge", left unfilled in the entry that listed the
      merges, corrected at 23:09:17;
    - an entry's time, "23:54" for 23:53:44, corrected at 00:11:37.

    Each correction is an appended entry, as the ledger's rule asks. Three
    more were typed elsewhere:
    - in a message to verifier-I, and in this file's draft, an entry named
      by a time no entry has, which verifier-I found (00:18:34);
    - in this file's draft, "00:24:05" for the stamp 00:24:40, replaced
      within minutes and recorded later;
    - also in this file's draft, "00:49:21" for 00:46:54, which a script
      checking every cited time against the ledger caught before the
      commit (00:53:23).

12. **The integration verifier found more restates in the lead's own work
    than in any parcel's.** verifier-I remade the four merges exactly and
    found no wrong answer or regression. But nine of the lead's own
    sentences claimed more than their sources (23:47:23, 23:48:06):
    - the restated preamble was still false of two rules;
    - one restate added a phrase, "measured-or-believed", that the lead had
      read in an unpublished brief and no record held;
    - a commit message misread case study 3;
    - two counts were off by one;
    - ADOPTION.md credited every row to one of the owner's answers;
    - a gate limit the lead had just written was again stated by its
      instance;
    - a fix to section 4 was half done.

    The lead's restates, written to correct the parcels' overreach,
    overreached the same way. They were fixed at `5c19906`, and the ledger
    was corrected by an appended entry. The scoped re-check found two of
    the nine still open (00:06:24):
    - the restated preamble said "every" rule rests on a break or a catch,
      then admitted nine that rest on practice;
    - ADOPTION.md still credited four rows to the wrong one of the owner's
      answers.

    `e5ce41e` put the exceptions inside the preamble's sentence. A third
    pass found one phrase still claiming more than the plan records
    (00:18:34), fixed at `6975994`.

13. **Wave 2's parcel said its templates carry only what ADOPTION.md
    assigns them, and they carry more.** P5 compiled the four templates
    from METHOD.md, each rule tagged with the section it comes from. Its own
    checks found every tag's sentence in its section, and every pair
    ADOPTION.md sends to a template carried. Its entry added that "none is
    carried that ADOPTION.md does not send there", and the lead's entry
    repeated it as "and none it doesn't" (00:23:24). verifier-P5 found
    the templates carry more: correct rules, each with its section, that
    ADOPTION.md's template column does not send them (00:45:48). The column
    was narrower than the templates, and the claim wider than what was
    measured.

## Cost of the round (measured from the transcripts)

Each agent's usage is summed from its own transcript, once per message.
"Output" is what it generated. "Read" is its input and cache reads and
writes, mostly the cache re-read on every turn. The two agents that prepared
the plan ran before the round opened. The rest is counted from the opening,
17:07, to 00:49, before this file was committed. Each parcel and verifier
row covers both of its phases, and verifier-I's covers its first phase
and both re-checks.

| agent | model | messages | output tokens | tokens read |
|---|---|---:|---:|---:|
| the practice survey, before the round | Opus 5.5 | 122 | 77,215 | 38,506,487 |
| the plan's verifier, before the round | Opus 5.5 | 107 | 114,138 | 31,608,573 |
| verifier-P0 | Opus 5.5 | 256 | 129,015 | 117,705,649 |
| P1: sections 1 to 3 | Sonnet 5.5 | 195 | 269,491 | 89,180,987 |
| P2: section 4 | Sonnet 5.5 | 170 | 259,368 | 82,782,527 |
| P3: sections 5 and 6 | Sonnet 5.5 | 162 | 240,676 | 75,267,763 |
| P4: sections 7 and 8 | Sonnet 5.5 | 158 | 235,500 | 73,309,286 |
| verifier-P1 | Opus 5.5 | 78 | 44,727 | 17,746,448 |
| verifier-P2 | Opus 5.5 | 74 | 68,067 | 16,595,826 |
| verifier-P3 | Opus 5.5 | 78 | 67,340 | 18,754,450 |
| verifier-P4 | Opus 5.5 | 85 | 55,203 | 22,201,709 |
| P5: the templates | Sonnet 5.5 | 199 | 182,235 | 112,682,745 |
| verifier-P5 | Opus 5.5 | 83 | 54,897 | 22,551,795 |
| verifier-I, wave 1 | Opus 5.5 | 149 | 117,223 | 64,501,622 |
| the lead, from the round's opening | Opus 5.5 | 553 | 823,019 | 262,720,554 |
| **total** | | | **2,738,114** | **1,046,116,421** |

- **The verifiers' share** of output tokens, verifier-P0's and the plan's
  verifier's included, is 650,610 of 2,738,114, about 24%. The parcels' is
  1,187,270, about 43%. The lead's is 823,019, about 30%.
- **The wall clock:** 17:07, the round's opening entry, to 00:48, the last
  commit before this file, for the work above: 7 hours 41
  minutes. P0's gate took 4 hours 12 minutes of it, to wave 1's dispatch at
  21:19.

## What METHOD.md should say differently (proposed; the owner's to settle)

Each item says whether it is **new**, a **reinforcement** of a rule the
method already has, or an **extension** of one. The bracket names the
observations each rests on.

**§5, gates.**
- **A gate states its threat model before its first verifier pass**: what
  it guards against, and what it leaves to verifiers. A fault outside the
  model is out of scope; inside it, the gate catches the fault or a limit
  states it by behaviour (extension of case study 4's READY standard).
  [1, 2]
- **A citation that writes one fact twice, as a link's text and its URL,
  is held equal by the gate, or written once** (new). [10]

**§6, the verifier.**
- **A round's planted-fault keys, and any description of their plants,
  stay out of the ledger until every verifier on a planted copy in the
  round has reported, later waves' included** (new). [6]
- **A verifier on a planted copy forms its view before it reads the
  parcel's file**, because design first leaves the parcel's design there as
  a reference copy of the work (reinforcement of R2). [5]
- **A wrong answer that the lead's own ruling caused is the lead's to fix,
  past a verifier**; the parcel that followed the ruling is not sent back
  (extension of the send-back rule). [4]
- **A restate at the merge only narrows a sentence to its source; it adds
  nothing the record does not hold** (extension of the send-back rule).
  [12]

**§4, the ledger.**
- **A published ledger names places by roots that each dispatch defines,
  never by an absolute path** (new; section 4's "a fixed absolute path"
  predates it). [11]
- **A value in the lead's entry is read from the command that measured it,
  like a stamp, not typed** (extension of the stamp rule, which case
  study 3 carried into every brief). [11]

## The round's end

- **Known limits, recorded for the owner and a later round:**
  - README step 4 says to run the full suite after each merge. HonestFramework
    quotes those words verbatim, so changing them is the owner's call.
    METHOD.md's staging branch keeps the full suite after each merge; its
    round branch runs a gate after each merge and the full suite at the tip
    before main moves (23:53:44).
  - CS5#11 stays pending. This round practised its second half, the case
    study read against the ledger by someone other than the lead before it
    is pushed. verifier-I reads this file in its second phase.
  - brief.md has no slot for section 3's cost model, and verifier.md's
    item 5 carries only the "re-run" half of section 6's rule on negative
    controls (00:46:54).
- **verifier-I's second phase** read this file against the ledger, and
  judged it READY after a scoped re-check (01:17:56).
- **The archive.** The ledger was archived from its working copy as
  `archive/round6-ledger.zip`: 27 files, each checked byte for byte
  against its file, with its modification time kept. The gate pins the
  archive's SHA-256. It does not excuse personal paths in it: only the
  earlier archives are excused, so this one is held to the privacy check
  like any file. Its last entry is the lead's, at 01:18:19.
- **Still to come, before main moves:** a scoped check of this commit,
  then main moved to it. Neither can be recorded in this file or the
  archive.
