# The workflow

The round, phase by phase, with what ends each phase and which template it uses. Each step cites the method section
it comes from:
- "PR" is ParcelRound's [METHOD.md](method/parcelround/METHOD.md);
- "HF" is HonestFramework's [METHOD.md](method/honest/METHOD.md).

The phases and their shapes are the method's. What goes in them (the authority, P0's contents, the parcels, the
waves) is the study's to decide, and Logan's to approve.

## Phase 0: day 1

1. Run `python3 -I tools/check_kit.py`, and read START-HERE.md.
2. **With Logan:**
   - settle which standing rules apply, what rule 7 covers, the caps (below) and the verifiers' tier
     (OWNER.md, "So, at kickoff");
   - make the project repository, with its private remote;
   - in it, fill docs/HARNESS.md and docs/BOARD.md from this kit's templates;
   - record his answers verbatim, with their date.
3. **Make the ledger** outside every worktree, with the README from
   [templates/ledger.md](method/parcelround/templates/ledger.md) (PR section 4). Give each agent a scratch directory
   of its own, and keep every secret out of every directory an agent is given (PR section 3). Each brief gives
   the ledger's absolute path (PR section 4: "a fixed absolute path each brief states"). Entries and reports name
   places by roots each dispatch defines, such as `<repos>/` and `<scratch>/`, never by an absolute path: round
   6's practice, proposed as CS6#7 and pending in [ADOPTION.md](method/parcelround/ADOPTION.md).
4. **Arm the escalation channel, and test it.** "A test escalation at dispatch must reach the lead" (PR section 4).
   The channel is either of two means:
   - **The file channel.** A file in `urgent/`, written elsewhere and renamed into place, with a watcher. The
     watcher is the snippet in the ledger's README, armed inline, not from a script file (PR section 4: "Arm the
     watcher from an inline command, not a script file").
   - **Your harness's messages between agents.** The question is written in the sender's own ledger file first.

   Whichever carries it, the three read moments stay the floor.

`tools/ledger.sh` writes a heading stamped from `date`, and an urgent message renamed into place. It does not watch:
the watcher stays inline.

## Phase 1: the survey

Read-only surveyors read the ground and report facts, each with its source and its tag (PR section 1, "Survey the
tree before the plan, read-only"). The ground:
- the standard, Logan's PDF, which only the lead holds unless it shares it;
- the RP2040's datasheet;
- pico-sdk's float support;
- the third-party implementations and test suites;
- the published hard cases.

A surveyor edits nothing, and marks what it measured apart from what it only read.

## Phase 2: the study, the plan of record

The lead writes the study, SF-0, in the project repository. It covers:
- **PROJECT.md's questions,** each with the lead's proposal, put to Logan as a question;
- **the authority and the oracles** (HF section 1). The standard is the contract, and the authority is something
  that can be run;
- **refusals** (HF section 2);
- **the gates, and their negative controls** (HF section 3);
- **P0's contents;**
- **the parcels and the waves,** each parcel with its owned files, its time box and its scope ceiling;
- **how the metrics are captured** (METRICS.md), with docs/HARNESS.md's answers.

**What ends it:** a verifier's re-check finds no (a) or (b), or the draft cap is reached with the open findings
listed; then Logan approves (PR section 7: "The plan of record, and a verifier on it before the owner approves
it"). The template is [templates/checklists.md](method/parcelround/templates/checklists.md), "Before dispatch".

## Phase 3: P0, the lead's

In a new repository, P0 is the seam, not a refactor: what every parcel will share, made once (PR section 2). The kit
proposes, and the study decides:
- the formats' parameters, defined once and generated (HF section 4);
- the runner, the front door, with its budgets (HF section 10; [templates/gate-runner.sh](method/honest/templates/gate-runner.sh));
- the vector format and its replay;
- the board harness;
- the table of refusals.

**What ends it:** a verifier finds it READY, before any parcel that reads it is dispatched.

## Phase 4: the waves

For each wave:
1. **Briefs,** from [templates/brief.md](method/parcelround/templates/brief.md). Each brief carries:
   - its owned and forbidden files, with each forbidden file's owner;
   - its named negative control;
   - its time box and its scope ceiling;
   - what READY means;
   - and its last line: "anything you found that this brief got wrong".

   Check every path and function a brief names before it goes out (PR section 3).
2. **Design first,** where the brief says so. The parcel writes its design in its ledger file and stops, and the
   lead approves or answers it.
3. **Build.** The parcel tests quickly and hands long runs to the lead.
4. **Verify, on a planted copy** (below), from [templates/verifier.md](method/parcelround/templates/verifier.md).
5. **Send back** by OWNER.md rule 1, if it applies: a regression or a wrong answer goes back; a false sentence is
   restated at the merge. A re-check is scoped to the fix, and the fix goes back to the verifier that found the
   problem, which picks its own faults (ParcelRound's CASE-STUDY-4.md, observation 7).
6. **Merge,** serially, with the gate after each merge, and never while a suite runs (PR section 7). Resolve
   conflicts from what git says is conflicted.
7. **The integration verifier** checks the lead's merges, seam and record, and makes each merge again from its
   parents with `git merge-tree`.
8. **The wave's record entry,** in the shape of examples/cases/20-record-skeleton.md, its tables made by
   `tools/round_metrics.py` (METRICS.md). The template is checklists.md, "At each merge".

**At each wave boundary,** read the ledger whole and fold it into the next wave's briefs (PR section 2).

## Phase 5: the board

By docs/BOARD.md. The lead holds it, and a parcel asks for board time.

## Phase 6: the close

- the keys revealed, and the grading recorded;
- the final record entry, with its metrics and the lead's slips;
- the ledger archived with its timestamps;
- what agents left running found and stopped;
- the summary to Logan, with the cost (PR section 7).

The template is checklists.md, "At the end of the round".

## The planted-fault protocol

"The lead holds them for parcels" (Logan, 2026-10-23). It is round 6's practice, which is in
method/parcelround/archive/round6-ledger.zip (its `briefs/_verifier.md`, `keys/` and `lead.md`), with its own
lessons taken in. Steps 4, 5 and 8 below are three of those lessons, which ParcelRound's
[ADOPTION.md](method/parcelround/ADOPTION.md) still holds as pending: CS5#8, CS6#4 and CS6#3. `tools/plant.py` does
the mechanical parts.

1. **Before the verifier is dispatched,** the lead writes a draft of the key, in round 6's format without its
   `copy_commit`: the parcel's `real_tip`, and `plants[]`, each with `file`, `old`, `new` and `shape`. It keeps the
   draft in its own scratch directory, outside every agent's reach.
2. **`plant.py make`** builds the copy in round 6's shape: "a fresh repository detached at 9c306e9 (parent a30aca5),
   with no remote, no refs and no route back to P5's own tip" (round 6's `lead.md`). Its one new commit sits on the
   parcel's base, which the lead gives and the tool prints for the ledger, and holds the parcel's tree with the
   plants applied. The tool then writes the key with its `copy_commit` and prints the key's sha256. Just before
   dispatch, `plant.py check --dispatch` reads the copy as the reveal's check does (step 8), and also what
   `git status` reports of it, untracked and ignored files shown, which must be nothing, and the name of each file
   in its git directory, which must be one `make` writes; it refuses a directory of the copy it cannot read. That is
   the lead's check against a slip, not a defense against a copy built to pass it.
3. **The key's sha256 goes in the ledger before dispatch.** Where Logan lets the lead commit, it also goes into the
   project repository's record in a commit, so that `git log` shows it came first (HF section 9, "Make the blinding
   a property of the record"). Where he does not, the record says the evidence is the ledger's alone.
4. **The parcel's own tip stays out of the ledger until its verifier reports.** The parcel gives it to the lead in
   its final message.
5. **The verifier treats everything it finds as real,** and reads the parcel's ledger file, which holds its design,
   only after it has written its own view. It leaves the copy's git state as it was sent: it builds and runs in a
   clone of the copy under its own scratch directory (`git clone COPY <scratch>/work`), so that the reveal's check
   reads the copy as it was dispatched.
6. **Rulings wait.** A ruling on a finding that touches only the copy describes a plant. It goes in the lead's
   scratch directory, not in the ledger, until the reveal.
7. **The copy goes out of reach** once its verifier has reported: the lead moves it into its own scratch directory.
8. **The reveal** comes when every verifier on a planted copy in the round has reported, later waves' included. Then
   the keys go into the ledger and the record, and `plant.py list` sets each plant beside its report. The lead
   grades each plant caught or missed by reading, and the integration verifier checks the grading, with
   `plant.py check`: the key hashes to what the ledger recorded, the copy's commit is the parcel's tip with the
   plants applied, on the base the ledger names, and the copy's git state meets each condition `plant.py --help`
   lists. At the reveal it does not read the copy's work tree, which the verifier may have changed. If the verifier
   wrote to the copy's git state anyway (an add, a stash, a checkout, a worktree), `check` refuses the copy for it,
   by name; the lead records that refusal beside what the verifier's report says it ran, and the check made at
   dispatch stands for the copy as it was sent.

**Its limits, stated:**
- **What a detection rate measures.** The lead's choice of plants and the verifiers' detection, together. The
  verifiers of the lead's own work get no plants.
- **Shapes the kit already shows.** Round 6's keys, round 4's `verifier-P0-work/plant_*.py`, and QRO-Crate's
  controls/. A verifier that read them knows those shapes, so plant shapes the kit does not show.

## Caps, and a calendar, to propose at kickoff

These are proposals. Logan settles them with the lead, to fit the harness: "discussed with the model to determine
what it thinks would be best for its harness capabilities".

The evidence beside them:
- QRO-Crate's study went twelve drafts, and its P0 six verifier rounds (READ, in its record, reference/QRO-Crate.bundle);
- Logan's rounds ran from about eight hours to a day each (READ, method/parcelround/CASE-STUDY-6.md and CASE-STUDY-2.md).

**The proposed caps:**
- **The study:** at most three drafts and two re-checks, then it goes to Logan with its open findings listed.
- **Verifier passes:** the loose cap (OWNER.md, rule 6), if it applies.
- **Every brief:** a time box and a scope ceiling.

**One round, of several waves.** The kit proposes that the ten days are one round, the method's whole pass
from the plan to the record (GLOSSARY.md). So the keys are revealed once, near the end.

**The proposed calendar:**

| day | date | what |
|---|---|---|
| 1 | Mon 10-26 | setup, and the survey |
| 2 | Tue 10-27 | the study, its verifier, and Logan |
| 3 | Wed 10-28 | P0 |
| 4 | Thu 10-29 | P0's verifier; the first wave dispatched |
| 5 to 8 | Fri 10-30 to Mon 11-02 | two or three waves |
| 9 | Tue 11-03 | integration, and the board's conformance runs |
| 10 | Wed 11-04 | the keys, the record, the metrics, and the summary |

The lead plans around Logan's hours. Decisions wait for him in the ledger (PR section 7, "Unattended, decide what
the standards decide and ask for what is the owner's").
