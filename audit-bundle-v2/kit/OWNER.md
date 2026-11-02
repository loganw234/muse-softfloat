# The owner: Logan

What Logan has said for this hackathon, his standing rules from his other projects, the rules his leads added, and
what the lead asks him before it acts. His words are verbatim, with their dates. The kit's readings of them are
marked as the kit's. His first request, which names the work itself, is quoted in PROJECT.md.

## His words for this hackathon (2026-10-23)

Each line gives the question he was answering, in the kit's words, then his answer:

| on | his words |
|---|---|
| the models | "Not yet decided, their most capable for the lead, likely one step down for parcels. Unsure what the TUI they offer has in terms of capabilities, but I will determine that live once the hackathon begins, no need to discern now." |
| the web | "Web access to read third-party code and solutions, the only restriction is staying away from cft" |
| what is off limits | "cft-fp256 only, as thats the only project where code could be copied from" |
| the scope | "Undecided yet" |
| the board | "Yes, a pico will be constantly connected for debugging"; and "Lead controls hardware access" |
| the length | "10 days starting Monday" |
| the planted faults' keys | "The lead holds them for parcels" |
| the standing rules, and a remote | "List all 8, I will discuss which apply with the Meta model, yes to remote, just create a private repo for now." |
| the caps | "Same as above, discussed with the model to determine what it thinks would be best for its harness capabilities." |
| the standard | "It wont be included in the zip as its licensed to me, but I will also be giving the Meta lead the real IEEE 754 pdf for reference, so they will have the material needed in terms of the contract, but not necessarily how to achieve it" |

**So, at kickoff,** the lead and Logan settle:
- which of the standing rules below apply;
- the caps (WORKFLOW.md proposes some);
- the verifiers' tier;
- the project repository and its private remote, and where that remote lives;
- **what rule 7 covers.** The method's briefs have each parcel commit in its own worktree (templates/brief.md), and
  the planted-fault protocol copies a parcel's commit (`tools/plant.py`). Read as written, rule 7 forbids both. So
  the lead asks whether it covers a parcel's commits in its own worktree, or the main branch and pushes only.

## His standing rules

From his other projects, each with its date and source. They were written as eight; the kit's plan verifier found
the ninth, and the kit's build found the tenth. "Which apply" is settled at kickoff.

1. **2026-09-27, send-backs.** "Only a regression or a wrong answer sends work back; anything else merges as a
   recorded known limit, and a sentence that claims more than is true is restated at the merge, not left standing"
   (ParcelRound [METHOD.md](method/parcelround/METHOD.md), lines 1125-1127). His words: "Agreed with the only
   regression or wrong answer being send backs" (method/parcelround/archive/round6-practice-survey.md, line 115).
   On 2026-10-13: "Lead fixes sentence at merge" (cft-fp256's record, line 19166).
2. **2026-09-29, long runs.** "dont have the individual agents all run the full suites, have them hand back large
   runs to you to monitor rather than them, but they should still verify and test as much as they can quickly"
   (METHOD.md, lines 1236-1239).
3. **2026-10-12, tiers.** "For 'simpler' level tasks, you may also utilize Sonnet for the Parcels and Haiku for the
   verifier. But only when its not a 'challenging' task" (cft-fp256's record, line 20101).
4. **2026-10-13, very small fixes.** "Go ahead and handle the two task chips first before we move on, with a Sonnet
   parcel and verifier for each. Unless they are very small fixes, in which case you can handle them and utilize a
   verifier to check" (cft-fp256's record, line 19293).
5. **2026-10-15, models.** "Use Sonnet models for the parcels in this round, as well as for the verifiers. They've
   been proving capable at parcel work. Unsure if that was already the approach used here or if Opus were still
   handling parcels. Difficult parcels still get opus, though most of this work is not "difficult" so to speak"
   (QRO-Crate's docs/VALIDATION.md, lines 1167-1171).
6. **2026-10-15, the loose cap.** "If the last rounds have just been semantic changes and nothing related to code
   directly, round 6 can be the last, with the verifier instructed not to hold it back for prose only issues"
   (QRO-Crate's docs/VALIDATION.md, lines 789-792). QRO-Crate's CLAUDE.md, item 6, states it as a rule: "After three
   NOT READY verdicts whose reasons grow more menial, the next verifier is told that only a defect in what the code
   does blocks. Prose, test gaps where the shipped code is right, and other non-code findings become notes the lead
   takes afterwards. The lead may keep sending back past the cap where the findings are real, and says why in the
   ledger."
7. **Commits and pushes, by his word.** "Nothing is committed or pushed without Logan's word" (QRO-Crate's
   CLAUDE.md, item 5). Here are three of his words that gave it:
   - 2026-10-14: "Go ahead with the first commit once P0 is READY, you can also make a remote repo to push to as
     well" (QRO-Crate's docs/VALIDATION.md, lines 922-924);
   - 2026-10-16: "You are clear to commit and push when ready" (line 2474);
   - for the project repository, 2026-10-23: "yes to remote, just create a private repo for now".
8. **2026-09-30, a pause.** "Go ahead and instruct agents to wrap up for now to take a pause, commit where they are
   and leave a resume note for themselves incase context is lost in the downtime" (cft-fp256's record, line 16510;
   examples/cases/12-pause-and-resume.md shows it handled).
9. **2026-09-25, load.** "Logan, 2026-09-25: no agent loads the machine on purpose" (cft-fp256's record, lines
   15443-15444). These are the record's words, not a quotation of his. It matters if the agents share his desktop.
10. **2026-10-22, the record before a push.** "History is what has been pushed: until then an entry is restated in
    place when a verifier sends its work back, keeping each pass's figures beside the new ones, so the ledger does
    not grow a correction entry for every pass (Logan, 2026-10-22)". That is the header of cft-fp256's record, which
    calls itself a ledger. His words: "Yes, add that sentence to the header, rewriting the current entry is common
    for the verifier send backs, correcting them with new entries would unnecessarily bloat the ledger more"
    (examples/cases/01-owners-words.md, 1b).
    - The kit's reading: this rule is about the project's record. The agents' working ledger of ParcelRound,
      section 4, stays append only.
    - It differs from HonestFramework, whose record is "Append only. Nothing in it is ever edited to agree with a
      later belief" (method/honest/templates/ledger.md; METHOD.md, section 7). The kit's reading: where rule 10
      applies, which is settled at kickoff, Logan's later rule governs his records until a push, and section 7
      governs them after it.

**Reading the tiers.** Rules 3, 4 and 5 name Claude models. The kit reads "Opus" as the most capable tier and
"Sonnet" as one step down, and finds nothing in his words that places "Haiku". That reading is the kit's, for the
kickoff discussion.

## The rules his leads added

These are not his words. Each is a brief rule that came from something that happened, with its source in
cft-fp256's record:
- **A time box and a scope ceiling in every brief** (line 21733). His words on them, 2026-10-20: "If needed it can
  have more time, though how have the time bounds been working so far? I noticed you started giving the agents them,
  good choice" (line 22537).
- **"NEVER change any git configuration"** (line 22676).
- **"wait on one quiet event; do not report a wait"** (line 22681).
- **"delete only what the run created, and stop only processes the run started, by PID"** (line 18990).
- **Scratch in a shared directory "is deleted by the exact path recorded when it was made, never by prefix"**
  (line 21789).
- **"open your own tab and act on it by its id"** (line 21790).

examples/cases/07-conduct.md shows where each came from.

## What the lead asks first, and records the answer

**From the method** (ParcelRound METHOD.md, lines 1372-1377): "a push that deploys, a remote branch deleted, a change
to how results are counted".

**From his words:**
- every commit and push (rule 7);
- models and tiers (rules 3 and 5, and his answer on the models);
- scope ("Undecided yet", and the questions in PROJECT.md);
- how the standard's PDF is held (PROJECT.md).

**The kit's own additions, marked as such:**
- any exception to a standing rule;
- any suspected contact with cft-fp256 (CLEAN-ROOM.md);
- anything that would put his name, his address or his data in front of a third party.

**Not on the list: the board.** He said "Lead controls hardware access", so board time is the lead's to schedule
(BOARD.md).

**Everything else, the lead decides by the standards.** Unattended, it merges, verifies, diagnoses and records within
the rules, and puts his questions in the ledger for him to answer when he reads it (METHOD.md, lines 1364-1370).

**When he answers,** the lead records his words as he gave them, with their date. Its reading goes beside them,
marked as the lead's (METHOD.md, lines 1379-1386; examples/cases/01-owners-words.md).
