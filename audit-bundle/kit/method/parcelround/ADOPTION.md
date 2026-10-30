# Adoption

What METHOD.md has taken in from the case studies, when, and on what
evidence, and what is still pending. There is one row per proposal in a case
study's list "What METHOD.md should say differently", and one per practice
the owner adopted without a proposal.

**This file is the current adoption state.** A case study's heading records the
state when the case study was written, and is not updated afterwards. For
example, case study 3's says "the owner's to settle".
`python tools/check_method.py` holds this file's ids against the case studies'
lists and the other ids it declares, every adopted row's headings against
METHOD.md, and every line number to the commit it is counted at.

**Statuses.**

- **adopted at `<commit>`**: in METHOD.md since that commit, under the
  heading or headings named. A rule split across two sections names both,
  separated by ` ; `.
  Round 6's rows (2026-10-02) name the commit of the parcel that wrote
  them, or of both parcels where two did. The lead's restates and
  corrections after each merge are in the round's ledger and its case
  study. Each row was adopted at the owner's word, in the answers round
  6's plan of record records: the proposals and B rows practised in a
  later round at "Everything practised (Recommended)"; the R rows, and
  S1, S4, S5 and S6, under "Restore safeguards (Recommended)", which
  named R1, R2 and those four (R3 to R5 are in the plan's table of
  safeguards, approved with it); B9, S2 and S3 by name, as their rows say.
- **adopted in part at `<commit>`**: the same, for only the part the
  status names: the part that was practised, or the part a ruling kept.
- **pending**, or **not adopted**: not in METHOD.md. The reason is given. A
  pending proposal is the owner's to settle.

**Ids.**

- `CSn#k` is the k-th proposal in case study n's list.
- `B` rows are practices from cft-fp256's later rounds that nobody proposed
  (the survey's Table B).
- `R` rows are safeguards that practice had dropped, restored.
- `S` rows are adaptations allowed with their conditions.

**Templates.** The template column names the templates a row's rule is
compiled into, as round 6 assigned them. The templates carry some rules in
more places than the column names. Each rule in a template is tagged, in
parentheses, with the METHOD.md section it comes from, or "own" for the
templates' own guidance, as each template's legend says; the tag, not this
column, says where a line comes from. For round 2's rows, the column gives the templates P5 put
each in, or "none" with the reason.

**Evidence.** The survey of 2026-10-02,
[archive/round6-practice-survey.md](archive/round6-practice-survey.md), gives
each row's evidence of practice, file and line. Much of the cft-fp256 evidence
is in that project's gitignored `Data/runs/` and is not public. Its
`docs/VALIDATION.md` and `docs/ROADMAP.md` are public, and pinned at
`4190a47`. That is a stated limit of this file's evidence. A line number
names the commit it is counted at, since lines move.

| id | proposal | type | status | evidence | METHOD heading | template | parcel |
|---|---|---|---|---|---|---|---|
| CS2#1 | Read the requester's code, not its ask list | untyped | adopted at `9b18e35` | CS2:358; METHOD.md:66; both at `49a9266` | Read the requester's code, not its ask list | checklists | P5 |
| CS2#2 | A seam's refusal belongs in every backend | untyped | adopted at `9b18e35` | CS2:362; METHOD.md:131; both at `49a9266` | Four more things a seam settles | checklists | P5 |
| CS2#3 | A value statement names the measurement that would falsify it | untyped | adopted at `9b18e35` | CS2:365; METHOD.md:137; both at `49a9266` | Four more things a seam settles | brief, checklists | P5 |
| CS2#4 | A wave boundary is the one moment a brief can be updated | untyped | adopted at `9b18e35` | CS2:371; METHOD.md:144; both at `49a9266` | Four more things a seam settles | checklists | P5 |
| CS2#5 | Name a base commit "at or after" | untyped | adopted at `9b18e35` | CS2:375; METHOD.md:149; both at `49a9266` | Four more things a seam settles | brief, checklists | P5 |
| CS2#6 | Derive the ownership list from the seam's own comments | untyped | adopted at `9b18e35` | CS2:381; METHOD.md:172; both at `49a9266` | 3. The brief | checklists | P5 |
| CS2#7 | A brief's cost model names the divisor it assumes | untyped | adopted at `9b18e35` | CS2:385; METHOD.md:177; both at `49a9266` | 3. The brief | checklists | P5 |
| CS2#8 | Name the trap, and name what will be measured at verification | untyped | adopted at `9b18e35` | CS2:388; METHOD.md:183; both at `49a9266` | 3. The brief | brief, checklists | P5 |
| CS2#9 | Verify the functions you name | untyped | adopted at `9b18e35` | CS2:392; METHOD.md:239; both at `49a9266` | Verify the constraints you write down | checklists | P5 |
| CS2#10 | A prohibition is written as the command to use | untyped | adopted at `9b18e35` | CS2:396; METHOD.md:216; both at `49a9266` | 3. The brief | brief, checklists | P5 |
| CS2#11 | Environment facts belong in the brief, not in the parcel's first hour | untyped | adopted at `9b18e35` | CS2:399; METHOD.md:210; both at `49a9266` | 3. The brief | brief, checklists | P5 |
| CS2#12 | Stamps are substituted, not typed | untyped | adopted at `9b18e35` | CS2:407; METHOD.md:349; both at `49a9266` | 4. The ledger | brief, checklists, ledger | P5 |
| CS2#13 | The lead's watcher skips the lead's own file | untyped | adopted at `9b18e35` | CS2:412; METHOD.md:500; both at `49a9266` | The lead watches too, and watches more | checklists, ledger | P5 |
| CS2#14 | A correction is linked from the entry it corrects | untyped | adopted at `9b18e35` | CS2:414; METHOD.md:355; both at `49a9266` | 4. The ledger | ledger | P5 |
| CS2#15 | A background job that writes to the ledger stamps at write and says what it describes | untyped | adopted at `9b18e35` | CS2:420; METHOD.md:361; both at `49a9266` | 4. The ledger | ledger | P5 |
| CS2#16 | A single target's exit code is not a verdict | untyped | adopted at `9b18e35` | CS2:427; METHOD.md:541; both at `49a9266` | 5. Gates and negative controls | brief | P5 |
| CS2#17 | The lead's code goes through the same gates as a parcel's | untyped | adopted at `9b18e35` | CS2:430; METHOD.md:550; both at `49a9266` | 5. Gates and negative controls | checklists, verifier | P5 |
| CS2#18 | Print the build time of every binary a gate runs | untyped | adopted at `9b18e35` | CS2:435; METHOD.md:545; both at `49a9266` | 5. Gates and negative controls | checklists (its first half; "name the test executables to the build" is build-system specific) | P5 |
| CS2#19 | When a mechanism is enforced in two places, a gate that reads the cheapest observable cannot see a defect in the other | untyped | adopted at `9b18e35` | CS2:438; METHOD.md:555; both at `49a9266` | 5. Gates and negative controls | verifier | P5 |
| CS2#20 | A crash can be a gate's faithful signal | untyped | adopted at `9b18e35` | CS2:443; METHOD.md:560; both at `49a9266` | 5. Gates and negative controls | none: an observation, not an instruction | P5 |
| CS2#21 | A probe that has caught a defect goes into the suite | untyped | adopted at `9b18e35` | CS2:446; METHOD.md:562; both at `49a9266` | 5. Gates and negative controls | checklists | P5 |
| CS2#22 | A verifier per parcel pays | untyped | adopted at `9b18e35` | CS2:453; METHOD.md:645; both at `49a9266` | What verifiers actually returned | none: the case for a decision already made when a verifier's brief is written | P5 |
| CS2#23 | A verifier's report is due when its LIST is exhausted, not when its first pass is | untyped | adopted at `9b18e35` | CS2:460; METHOD.md:653; both at `49a9266` | What verifiers actually returned | verifier | P5 |
| CS2#24 | A verifier's default list carries the instruments the parcel lacks | untyped | adopted at `9b18e35` | CS2:464; METHOD.md:658; both at `49a9266` | What verifiers actually returned | verifier | P5 |
| CS2#25 | The scoped re-check after a fix is the default | untyped | adopted at `9b18e35` | CS2:469; METHOD.md:664; both at `49a9266` | What verifiers actually returned | verifier | P5 |
| CS2#26 | A verifier's report distinguishes "the shipped code is right" from "the gate would catch it if it weren't" | untyped | adopted at `868f95e`, before round 2 | CS2:472; METHOD.md:634; both at `49a9266` | What verifiers actually returned | verifier | P5 |
| CS2#27 | A staging branch per merge, the suite on the box at the staging commit, and main moves on the verdict | untyped | adopted at `9b18e35` | CS2:478; METHOD.md:694; both at `49a9266` | 7. What the lead keeps | checklists | P5 |
| CS2#28 | A merge conflict is not two piles of text | untyped | adopted at `9b18e35` | CS2:483; METHOD.md:731; both at `49a9266` | Habits | checklists | P5 |
| CS2#29 | The docs sweep happens in the lead's idle time during the round | untyped | adopted at `9b18e35` | CS2:487; METHOD.md:701; both at `49a9266` | 7. What the lead keeps | checklists | P5 |
| CS2#30 | A merge with no RTL in its diff gets no RTL suite, and the ledger says so | untyped | adopted at `9b18e35` | CS2:490; METHOD.md:736; both at `49a9266` | Habits | none: specific to RTL | P5 |
| CS2#31 | The lead's summary to the owner carries the cost | untyped | adopted at `9b18e35` | CS2:493; METHOD.md:704; both at `49a9266` | 7. What the lead keeps | checklists | P5 |
| CS2#32 | Dispatch on the fast simulator; the slow one confirms in the background | untyped | adopted at `9b18e35` | CS2:498; METHOD.md:783; both at `49a9266` | 8. Sequencing | none: specific to the fast simulator | P5 |
| CS2#33 | A send-back needs no re-brief | untyped | adopted at `9b18e35` | CS2:501; METHOD.md:786; both at `49a9266` | 8. Sequencing | checklists | P5 |
| CS2#34 | A stop line in a brief fires for value, not only for size | untyped | adopted at `9b18e35` | CS2:506; METHOD.md:791; both at `49a9266` | 8. Sequencing | brief | P5 |
| CS2#35 | The round's build phase is done when every parcel is merged and box-verified; the image and the card day are the lead's and the owner's, after | untyped | adopted at `9b18e35` | CS2:509; METHOD.md:794; both at `49a9266` | 8. Sequencing | none: specific to the card day | P5 |
| CS3#1 | Brief a send-back as a new agent when the dispatch cannot resume one | reversal | adopted at `d38fea1` | archive/round6-practice-survey.md, CS3#1 | 8. Sequencing | checklists | P4 |
| CS3#2 | The stamp rule goes in `templates/ledger.md` and in every brief, fixers' included | reinforcement | adopted at `3676786` | archive/round6-practice-survey.md, CS3#2 | 4. The ledger | ledger, brief, checklists | P2 |
| CS3#3 | A parcel's question for the lead goes in urgent/ | reinforcement | adopted at `3676786` | archive/round6-practice-survey.md, CS3#3 | Escalation: one rule, whatever carries it | ledger, brief, checklists | P2 |
| CS3#4 | Archive the ledger from the working copy, with its timestamps | extension | adopted at `3676786` | archive/round6-practice-survey.md, CS3#4 | 4. The ledger | ledger, brief, checklists | P2 |
| CS3#5 | In a harness where every watch expires, the expiry notice is the moment to re-arm and do a full read | reinforcement | adopted at `3676786` | archive/round6-practice-survey.md, CS3#5 | 4. The ledger | ledger, brief, checklists | P2 |
| CS3#6 | The lead watches urgent/ continuously and reads the rest at set points | reversal | adopted in part at `3676786`: the lead watches the escalation channel continuously; reading the rest at set points is R4 | archive/round6-practice-survey.md, CS3#6 | 4. The ledger | ledger, checklists | P2 |
| CS3#7 | The lead's seam commits go through a verifier before main moves | reinforcement + new | adopted at `4ff28ca` and `d38fea1` | archive/round6-practice-survey.md, CS3#7 | 5. Gates and negative controls ; 7. What the lead keeps | checklists, verifier | P3 (code); P4 (records) |
| CS3#8 | The verifier's list includes the lead's grants and rulings issued after dispatch | new | adopted in part at `4ff28ca`: the lead's grants and rulings made after dispatch are on the verifier's list | archive/round6-practice-survey.md, CS3#8 | 6. The verifier | verifier | P3 |
| CS3#9 | "Check every claim in a comment, doc or commit message" is on every verifier's list when parcels write docs | extension | adopted at `4ff28ca` | archive/round6-practice-survey.md, CS3#9 | 6. The verifier | verifier | P3 |
| CS3#10 | Give side notes a step of their own in every round | new | adopted at `4ff28ca` | archive/round6-practice-survey.md, CS3#10 | 6. The verifier | checklists | P3 |
| CS3#11 | Freeze what is audited | new | adopted at `d38fea1` | archive/round6-practice-survey.md, CS3#11 | 7. What the lead keeps | checklists | P4 |
| CS3#12 | Check a gate budget against the merged diff before trusting it | relaxation + extension | adopted in part at `d38fea1`: the budget checked against the merged diff, and the record of why main moved on FAIL; ruling D4 left out the relaxation for batched merges | archive/round6-practice-survey.md, CS3#12 | 7. What the lead keeps | checklists | P4 |
| CS3#13 | The cost summary gives processed tokens beside the harness's figure, and says which is which | new + reinforcement | adopted in part at `d38fea1`: the round's cost reported as processed tokens, read from transcripts (with R3) | archive/round6-practice-survey.md, CS3#13 | 7. What the lead keeps | checklists | P4 |
| CS3#14 | Settle at kickoff what the owner may want to see first | extension | adopted in part at `d38fea1`: what the owner wants to see first, asked and recorded | archive/round6-practice-survey.md, CS3#14 | 7. What the lead keeps | checklists | P4 |
| CS3#15 | Decide, per round, whether the lead sits between verdict and fix | new | pending: no practice found | archive/round6-practice-survey.md, CS3#15 | — | — | — |
| CS3#16 | Let a verifier reuse a run whose inputs are identical | relaxation | adopted in part at `4ff28ca`: reuse of a run under S6's conditions | archive/round6-practice-survey.md, CS3#16 | 6. The verifier | verifier | P3 |
| CS3#17 | A worktree the harness creates branches from the session checkout's HEAD | reinforcement | adopted in part at `03561a7`: fast-forward to the base and check its SHA, never switch another session's branch; the CI clause was not practised | archive/round6-practice-survey.md, CS3#17 | 3. The brief | brief | P1 |
| CS3#18 | A sweep is a round | extension / replacement | pending: its practised parts are adopted as B17 and CS3#11 | archive/round6-practice-survey.md, CS3#18 | — | — | — |
| CS4#1 | The lead's P0 goes past a verifier before any parcel that reads it is dispatched | extension (+ relaxation) | adopted at `03561a7` | archive/round6-practice-survey.md, CS4#1 | 2. P0: make the shared thing shared, before you split | checklists | P1 |
| CS4#2 | A trap one round measures goes into the next round's seam as a refusal, not into its briefs as a rule | extension | adopted at `03561a7` | archive/round6-practice-survey.md, CS4#2 | Put what a round measures into the tree | checklists | P1 |
| CS4#3 | A tool's check that no stage runs is flagged, as a test file that no stage runs is | extension | adopted at `03561a7` | archive/round6-practice-survey.md, CS4#3 | 2. P0: make the shared thing shared, before you split | checklists | P1 |
| CS4#4 | A spike states the cases it measured, and a figure the docs quote has a script in the tree, or the docs say it has none | new | adopted in part at `03561a7`: a figure the documents quote has a script in the tree | archive/round6-practice-survey.md, CS4#4 | Put what a round measures into the tree | brief | P1 |
| CS4#5 | Name a control by the property that makes it bite, or run it before the brief goes out | extension | adopted at `03561a7` | archive/round6-practice-survey.md, CS4#5 | 3. The brief | brief, verifier | P1 |
| CS4#6 | Name each agent's scratch directory, and keep secrets outside every directory an agent is given | new | adopted at `03561a7` | archive/round6-practice-survey.md, CS4#6 | 3. The brief | brief, verifier | P1 |
| CS4#7 | State the READY standard, "a gate, or a stated limit", in the brief before the first pass | new | adopted at `03561a7` | archive/round6-practice-survey.md, CS4#7 | 3. The brief | brief, verifier | P1 |
| CS4#8 | An agent's "what I did not do" is a claim: the lead checks its own tree after every agent | extension | adopted at `03561a7` | archive/round6-practice-survey.md, CS4#8 | 3. The brief | brief, verifier | P1 |
| CS4#9 | The lead arms its watch with its first dispatch | reinforcement | adopted at `3676786` | archive/round6-practice-survey.md, CS4#9 | 4. The ledger | ledger, checklists | P2 |
| CS4#10 | Re-arm a watch when it expires, keep its snapshot across re-arms, and run one watch at a time, on files of its own | extension | adopted at `3676786` | archive/round6-practice-survey.md, CS4#10 | 4. The ledger | ledger, brief, checklists | P2 |
| CS4#11 | When a pause is announced, each agent records where it is | new | adopted at `3676786` | archive/round6-practice-survey.md, CS4#11 | 4. The ledger | ledger, brief, checklists | P2 |
| CS4#12 | The lead's decisions go in the ledger first, then in the message | reinforcement | adopted at `3676786` | archive/round6-practice-survey.md, CS4#12 | 4. The ledger | ledger, brief, checklists | P2 |
| CS4#13 | A gate that reads source text is a stated limit, not a guarantee | extension | adopted at `4ff28ca` | archive/round6-practice-survey.md, CS4#13 | What a gate cannot see, and who finds it | verifier | P3 |
| CS4#14 | A limit is stated by the behaviour it concedes, not by the plants that found it | new | adopted at `4ff28ca` | archive/round6-practice-survey.md, CS4#14 | What a gate cannot see, and who finds it | verifier | P3 |
| CS4#15 | The lead's fixes to a verifier's findings go back to that verifier, which picks its own faults | extension | adopted at `4ff28ca` | archive/round6-practice-survey.md, CS4#15 | What a gate cannot see, and who finds it | verifier | P3 |
| CS4#16 | A stated limit is tested: the verifier builds a fault that passes every gate, and READY needs it to land inside the limit | new | adopted at `4ff28ca` | archive/round6-practice-survey.md, CS4#16 | What READY needs, and what sends work back | verifier | P3 |
| CS4#17 | The verifier reads a claim's domain and quantifier as claims, beside its numbers | extension | adopted at `4ff28ca` | archive/round6-practice-survey.md, CS4#17 | 6. The verifier | verifier | P3 |
| CS4#18 | A figure that crosses into the docs from any report, a verifier's included, carries its definition or is re-measured | new | adopted at `4ff28ca` | archive/round6-practice-survey.md, CS4#18 | 6. The verifier | verifier | P3 |
| CS4#19 | Work added after the verifier's cut is stated as unverified, in the ledger and in the records, and held to the records by a gate where it can be | new | pending: practised only in the round that proposed it | archive/round6-practice-survey.md, CS4#19 | — | — | — |
| CS4#20 | A seam changed mid-round is checked against every open branch at once | new | adopted at `d38fea1` | archive/round6-practice-survey.md, CS4#20 | 7. What the lead keeps | checklists | P4 |
| CS4#21 | The lead may prepare a merge while the verifier works; the verdict still gates main | new | adopted at `d38fea1` | archive/round6-practice-survey.md, CS4#21 | 7. What the lead keeps | checklists | P4 |
| CS4#22 | A claim stated in two places is corrected in one, so a docstring points to the document | reinforcement | pending: no practice found | archive/round6-practice-survey.md, CS4#22 | — | — | — |
| CS4#23 | A lead-only round is a shape of its own | new | pending: its practised part (the lead's small fixes past a verifier) is adopted as CS3#7 and CS5#1 | archive/round6-practice-survey.md, CS4#23 | — | — | — |
| CS5#1 | The lead's seam commits and records go past a verifier before main moves, all round, not only P0 | reinforcement | adopted at `4ff28ca` and `d38fea1` | archive/round6-practice-survey.md, CS5#1 | 5. Gates and negative controls ; 7. What the lead keeps | checklists, verifier | P3 (code); P4 (records) |
| CS5#2 | When a seam changes mid-round, the lead checks its own controls for assumptions the change breaks | new | pending: practised only in the round that proposed it | archive/round6-practice-survey.md, CS5#2 | — | — | — |
| CS5#3 | No brief holds the owner's personal data | new | pending: practised only in the round that proposed it | archive/round6-practice-survey.md, CS5#3 | — | — | — |
| CS5#4 | A rule the brief states and no gate reads goes on the verifier's checklist by name | new | pending: practised only in the round that proposed it | archive/round6-practice-survey.md, CS5#4 | — | — | — |
| CS5#5 | Where a gate reads text another program renders, hold the input to a subset both read alike, | extension | pending: practised only in the round that proposed it | archive/round6-practice-survey.md, CS5#5 | — | — | — |
| CS5#6 | Pin the parser's version in one file that the desktop and CI both read | new | pending: practised only in the round that proposed it | archive/round6-practice-survey.md, CS5#6 | — | — | — |
| CS5#7 | A control names the rule it exercises, and restores the bytes it planted over exactly | new | adopted at `4ff28ca` | archive/round6-practice-survey.md, CS5#7 | 5. Gates and negative controls | verifier | P3 |
| CS5#8 | A planted control's parcel tip stays out of the ledger until its verifier reports | extension | pending: not practised | archive/round6-practice-survey.md, CS5#8 | — | — | — |
| CS5#9 | A record names the level at which each shape was measured, the full gate or a unit-level call | new | pending: practised only in round 5 (and the same session's front-page change that evening) | archive/round6-practice-survey.md, CS5#9 | — | — | — |
| CS5#10 | An agent stops its own background work, its watches and servers, before it reports, and the lead checks for leftovers at cleanup | new | adopted at `03561a7` and `d38fea1` | archive/round6-practice-survey.md, CS5#10 | 3. The brief ; 7. What the lead keeps | brief, checklists | P1 (the agent); P4 (the lead's check) |
| CS5#11 | The case study is written from the ledger, not from the lead's memory, and read against it by someone other than the lead before it is pushed | extension | pending: practised only in the round that proposed it | archive/round6-practice-survey.md, CS5#11 | — | — | — |
| CS5#12 | Parcels, and their verifiers, can run on a smaller model when the work is sentences rather than code | observation | pending: practised only in the round that proposed it | archive/round6-practice-survey.md, CS5#12 | — | — | — |
| CS5#13 | Take each agent's model from its transcript, not from its dispatch | new | pending: practised only in the round that proposed it | archive/round6-practice-survey.md, CS5#13 | — | — | — |
| CS6#1 | A gate states its threat model before its first verifier pass; a fault outside it is out of scope, and one inside it is caught or stated by behaviour | extension | pending: proposed by round 6 | CASE-STUDY-6.md, obs 1 and 2 | — | — | — |
| CS6#2 | A citation that writes one fact twice, as a link's text and its URL, is held equal by the gate, or written once | new | pending: proposed by round 6 | CASE-STUDY-6.md, obs 10 | — | — | — |
| CS6#3 | Planted-fault keys, and any description of their plants, stay out of the ledger until every verifier on a planted copy in the round has reported | new | pending: proposed by round 6 | CASE-STUDY-6.md, obs 6 | — | — | — |
| CS6#4 | A verifier on a planted copy forms its view before it reads the parcel's file, which holds the parcel's design | reinforcement | pending: proposed by round 6 | CASE-STUDY-6.md, obs 5 | — | — | — |
| CS6#5 | A wrong answer the lead's own ruling caused is the lead's to fix, past a verifier; the parcel that followed it is not sent back | extension | pending: proposed by round 6 | CASE-STUDY-6.md, obs 4 | — | — | — |
| CS6#6 | A restate at the merge only narrows a sentence to its source; it adds nothing the record does not hold | extension | pending: proposed by round 6 | CASE-STUDY-6.md, obs 12 | — | — | — |
| CS6#7 | A published ledger names places by roots each dispatch defines, never by an absolute path | new | pending: proposed by round 6 | CASE-STUDY-6.md, obs 11 | — | — | — |
| CS6#8 | A value in the lead's entry is read from the command that measured it, not typed | extension | pending: proposed by round 6 | CASE-STUDY-6.md, obs 11 | — | — | — |
| B1 | A verifier on the plan of record, before the owner approves it | practice | adopted at `d38fea1` | archive/round6-practice-survey.md, Table B | 7. What the lead keeps | checklists | P4 |
| B3 | The send-back rule: only a regression or a wrong answer sends work back; anything else merges as a recorded known limit, and a sentence that claims too much is restated at the merge | practice; the owner's rule, 2026-09-27 | adopted at `4ff28ca` | archive/round6-practice-survey.md, Table B | What READY needs, and what sends work back | verifier | P3 |
| B4 | Agents test quickly and hand long runs back to the lead | practice; the owner's rule, 2026-09-29 | adopted at `d38fea1` | archive/round6-practice-survey.md, Table B | 7. What the lead keeps | brief, checklists | P4 |
| B8 | The owner's decisions recorded verbatim, with their dates | practice | adopted at `d38fea1` | archive/round6-practice-survey.md, Table B | 7. What the lead keeps | checklists | P4 |
| B9 | The owner's standing rules carried from round to round | practice | adopted at `d38fea1` (beyond the four answers; approved by Logan by name, 2026-10-02) | archive/round6-practice-survey.md, Table B | 7. What the lead keeps | checklists | P4 |
| B10 | Each merge re-made by the integration verifier, to expose hand resolutions | practice | adopted at `d38fea1` | archive/round6-practice-survey.md, Table B | 7. What the lead keeps | checklists, verifier | P4 |
| B11 | The plan restated by the lead before its verifier | practice | not adopted: practised once | archive/round6-practice-survey.md, Table B | — | — | — |
| B12 | The plan of record's sections | practice | not adopted: a project convention, and a template candidate | archive/round6-practice-survey.md, Table B | — | — | — |
| B13 | Design first: a parcel proposes, and the lead approves before it builds | practice | adopted at `03561a7` | archive/round6-practice-survey.md, Table B | 3. The brief | brief | P1 |
| B14 | The lead's own slips, in every round's record | practice | adopted at `d38fea1` | archive/round6-practice-survey.md, Table B | 7. What the lead keeps | checklists | P4 |
| B15 | The ledger kept as the round's record and archived, never deleted | practice | adopted at `3676786` | archive/round6-practice-survey.md, Table B | 4. The ledger | ledger, checklists | P2 |
| B16 | No intentional load on the machine; one run at a time, niced | practice | not adopted: project-level | archive/round6-practice-survey.md, Table B | — | — | — |
| B17 | Read-only surveyors before a plan | practice | adopted at `03561a7` | archive/round6-practice-survey.md, Table B | Survey the tree before the plan, read-only | — | P1 |
| R1 | Restore: every parcel brief asks for anything the brief got wrong; verifier briefs keep their own open question, 'anything else' | restoration | adopted at `03561a7` | archive/round6-practice-survey.md, the departures table | 3. The brief | brief, checklists | P1 |
| R2 | Restore: a verifier forms its own view before reading a parcel's self-report | restoration | adopted at `3676786` and `4ff28ca` | archive/round6-practice-survey.md, the departures table | 4. The ledger ; 6. The verifier | verifier | P2 (the rule, kept as written); P3 (a cross-reference) |
| R3 | Restore: the summary to the owner carries the cost, read from transcripts | restoration | adopted at `d38fea1` | archive/round6-practice-survey.md, the departures table | 7. What the lead keeps | checklists | P4 |
| R4 | Restore: the lead reads every author's file before each merge and at each wave boundary, so the cross-parcel view survives | restoration | adopted at `3676786` | archive/round6-practice-survey.md, the departures table | 4. The ledger | ledger, checklists | P2 |
| R5 | Restore: the three read moments stay the floor, whatever carries the push | restoration | adopted at `3676786` | archive/round6-practice-survey.md, the departures table | 4. The ledger | brief, ledger | P2 |
| S1 | Allowed: the runtime's messages in place of urgent/, the ledger entry first; the brief says how to escalate without finishing; verifiers get only the lead's messages | allowed shape | adopted at `3676786` | archive/round6-practice-survey.md, the departures table | Escalation: one rule, whatever carries it ; The lead watches too, and watches more | ledger, brief | P2 |
| S2 | Allowed: the ledger's rules carried in every brief, the three read moments (R5) included, in place of a README | allowed shape | adopted at `3676786` (beyond the four answers; approved by Logan by name, 2026-10-02) | archive/round6-practice-survey.md, the departures table | 4. The ledger | ledger, brief | P2 |
| S3 | Allowed: the lead told of escalations by the runtime, in place of a watch; the channel watched to work (a test escalation at dispatch reaches the lead) | allowed shape | adopted at `3676786` (beyond the four answers; approved by Logan by name, 2026-10-02) | archive/round6-practice-survey.md, the departures table | Escalation: one rule, whatever carries it ; The lead watches too, and watches more | ledger, checklists | P2 |
| S4 | Allowed: one round branch; P0 lands on it before any parcel; a gate after each merge; each merge re-made; main moves only to a verified tip | allowed shape | adopted at `03561a7` and `d38fea1` | archive/round6-practice-survey.md, the departures table | 2. P0: make the shared thing shared, before you split ; 7. What the lead keeps | checklists | P1 (§2); P4 (§7) |
| S5 | Allowed: parcels own the documents that describe their code; the claims documents stay the lead's; every claim in a parcel-written document is on its verifier's list | allowed shape | adopted at `03561a7` and `d38fea1` | archive/round6-practice-survey.md, the departures table | 3. The brief ; 7. What the lead keeps | brief, verifier | P1 (the brief); P4 (the lead's) |
| S6 | Allowed: reuse of a run made by someone other than the author of the work verified, with identical inputs and binary hashes; the verifier re-runs from clean what it doubts; the full suite at the round branch's tip before main moves never reuses | allowed shape | adopted at `4ff28ca` | archive/round6-practice-survey.md, the departures table | 6. The verifier | verifier | P3 |
