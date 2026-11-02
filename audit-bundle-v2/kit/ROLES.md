# Roles

Four roles. In this hackathon:
- **Logan is the owner.**
- **The models are not yet decided.** Logan, 2026-10-23: "Not yet decided, their most capable for the lead,
  likely one step down for parcels. Unsure what the TUI they offer has in terms of capabilities, but I will determine
  that live once the hackathon begins, no need to discern now." The kit's reading: the models are settled at kickoff,
  with the rest of OWNER.md's list.
- **The verifiers' tier** is settled at kickoff (OWNER.md, rules 3 and 5).

The roles are ParcelRound's [METHOD.md](method/parcelround/METHOD.md)'s. A line cites the method by its section,
Logan's own words by his name and their date, a rule he or his leads added by OWNER.md or the kit page that carries
it, and its details by the kit page or template that holds them. A line that cites nothing is the kit's summary of
the role, in the method's words.

## The owner: Logan

- **He decides:** scope; models and tiers; which standing rules apply (OWNER.md); the caps; anything that leaves the
  project repository: a push, a deploy, a deleted remote branch, a change to how results are counted.
- **He approves:** the plan of record, after its verifier; each push; any exception to a standing rule.
- **He gives:** the IEEE 754 PDF, the board, and his answers at kickoff.
- **His words are kept as he gave them, with their dates.** The lead's reading goes beside them, marked as the
  lead's (section 7, Habits).

## The lead

**What it owns** (section 7, "What the lead keeps"):
- **the plan of record:** the study SF-0, past a verifier before Logan approves it;
- **P0, the shared seam:** past a verifier before any parcel that reads it is dispatched (section 2);
- **the seam tests,** which belong to no parcel, and which are why the method exists (section 1);
- **every brief** ([templates/brief.md](method/parcelround/templates/brief.md)) and every verifier's brief
  ([templates/verifier.md](method/parcelround/templates/verifier.md));
- **every merge:** serially, with the gate after each one, and the full suite on the tip before the main branch
  moves;
- **the long runs and the board:** "Lead controls hardware access" (Logan; BOARD.md);
- **the planted faults and their keys** (WORKFLOW.md);
- **the record:** its entries and their tables (METRICS.md), Logan's words verbatim, and the lead's own slips;
- **the files that state the project's claims:** its README, and its published documents;
- **the ledger's own file,** its README ("the ledger directory's own `README.md`", templates/ledger.md), and
  folding the ledger into the record at the round's end;
- **the cleanup** of what finished agents left running;
- **the summary to Logan,** with the cost.

**Its own work goes past a verifier like a parcel's:** seam commits, fixes, merges and record entries, from the first
commit of the round to the last (section 7).

**What it decides, and what it asks first:** OWNER.md, "What the lead asks first". Unattended, it decides what the
standards decide, and leaves Logan's questions in the ledger for him to answer when he reads it.

**What it never does** (section 7, Habits):
- merge on the strength of a report;
- merge while a suite is running;
- act on an escalation it has not checked;
- resolve a conflict from what the merge output printed, rather than from what git says is conflicted;
- let an auditor read a tree it is still editing.

## A parcel

One agent with one brief (section 3). It owns the files its brief names, by path, and by function where a file is
shared.

**What it must do:**
- check that it is on its base commit, or after it, in the right repository, and say what it found in the ledger;
- read the ledger at three moments: before it starts; before it designs anything that touches a file its brief
  calls shared or forbidden; and before it writes its report (section 4);
- propose a design first where its brief says so, and stop until the lead answers;
- build its brief's named negative control, run it, see it fail, and report both results (section 5);
- test as much as it can quickly, and hand long runs to the lead (OWNER.md, rule 2, if it applies);
- disclose any boundary it crossed, and why. A crossing is expected; a silent one is not (section 3);
- end its report with what the brief got wrong and what it did not do, and stop its own background work before it
  reports.

**What it never does:**
- push, merge, rebase, or commit to the main branch;
- weaken an assertion to make something pass;
- fix anything outside its scope (it reports it instead);
- change any git configuration (OWNER.md, the leads' rules);
- delete what it did not create (OWNER.md, the leads' rules);
- read another agent's scratch directory.

## A verifier

**Its job is to disconfirm one piece of work, and to report** (section 6). "Found nothing" is an acceptable answer,
and is not held against it.

**What it must do:**
- re-run the gate from a clean build, rather than trust pasted output: on a planted copy, in a clone of it
  (WORKFLOW.md, step 5);
- re-run the negative control, or build one if there is none;
- diff the change against the ownership list;
- check every claim in a comment, a document or a commit message;
- state what it ran, command by command;
- form its own view before it reads the parcel's file. On a planted copy, that is before it reads the parcel's
  design (WORKFLOW.md).

**What it never does:**
- fix anything;
- read another agent's scratch directory. The lead's is the one that holds the keys.

**How it classes what it finds:** (a), a regression; (b), a wrong answer; or a note (GLOSSARY.md). Only (a) and (b)
send work back (OWNER.md, rule 1, if it applies). READY means that every property of the work is held by a gate, or stated as a
limit (section 3, "What READY means").
