# Glossary

The words this kit and its examples use, as Logan's records use them. Where two of his projects use a word
differently, both uses are given. Line numbers cite cft-fp256's docs/VALIDATION.md, which is not in this kit;
"QRO-Crate" cites the bundle in reference/.

## The evidence tags

Every claim in a ledger entry, a report or a record entry carries one. They come from that record's own sentence:
"Marks: READ a file, COMPUTED arithmetic on what was read, MEASURED a run of mine, BELIEVED mine and unverified"
(:23536).

- **MEASURED.** Run in this round, with the output in hand. The record often names who ran it, and where: "MEASURED
  by RT at 949e56c" (:18913).
- **READ.** Read, not run: a file and a line, a commit, a report, a page or a search. Examples: "(READ, by VCI)"
  (:20929); "(READ, the project's page)" (:21941); QRO-Crate's "(READ, a search of its tree)".
- **COMPUTED.** Arithmetic on figures that were measured or read. Show the arithmetic, though the record does not
  always: "(COMPUTED)" (:18110). QRO-Crate's documents never use this tag: 0 lines, against 589 for MEASURED, 228 for
  READ and 105 for BELIEVED (MEASURED by the kit's plan verifier, and by v1's).
- **BELIEVED.** An estimate, an inference, or a claim not checked: "BELIEVED where a word was not checked"
  (:18253).

A ledger entry has the same split in two lines: Measured, and Believed (the ledger's README).

## What a verifier finds

- **(a), a regression.** Something that worked and now does not.
- **(b), a wrong answer.** A result that is false, or a sentence that claims more than is true: "(b)2, a sentence
  the merges made false" (:17961).
- **A note.** Anything else: a gap, a wording, a limit.
- **The rule:** "Only a regression "(a)" or a wrong answer "(b)" sends a parcel back. Everything else merges as a
  recorded limit, with its false sentences restated at the merge" (:15854).
- **How a false sentence is handled.** The record handles one both ways: "P1 was sent back a second time for it"
  (:15903), and "no: the lead fixed the wording three times" (:22587). So:
  - when a send-back is going anyway, the author restates the sentence;
  - when nothing else sends the work back, the lead restates it at the merge, as a very small fix past a verifier
    (OWNER.md, rules 1 and 4).
- **How the chain counts one.** Logan's chain tables count a false sentence as a (b), and say in the "sent
  back" column when the lead restated it instead (examples/cases/20-record-skeleton.md, 20a). Round 6's verifiers
  kept "restate" as a class of its own ("two wrong answers, two restates", in
  method/parcelround/archive/round6-ledger.zip). The study picks one, and the record says which.
- **QRO-Crate's split** is the other practice. Its verifiers hold "a defect in what the code does" apart from prose
  (its CLAUDE.md, item 6).

## Verdicts and limits

- **READY and NOT READY.** A verifier's verdict on the work. READY means "a gate, or a stated limit": every property
  of the work is held by a gate, or stated as a limit
  ([ParcelRound METHOD.md](method/parcelround/METHOD.md), section 3).
- **A known limit.** A property the work does not hold. It is stated by the behaviour it concedes, and it gives no
  wrong answer today. A verifier tests it by building a fault that passes every gate, and seeing whether the fault
  lands inside the limit (section 6).
- **A send-back.** The work returns to its author, with the verifier's findings. A re-check after a send-back is
  scoped to the fix, and the fix goes back to the verifier that found the problem, which picks its own faults
  (ParcelRound's CASE-STUDY-4.md, observation 7).
- **To restate.** To rewrite a sentence, or a record entry, so that it claims what is true. Until a push, an entry is
  restated in place, keeping each pass's figures beside the new ones (OWNER.md, rule 10).

## The round

- **A round.** One pass of the whole method, from the plan to the record.
- **A wave.** A group of parcels dispatched together, and merged and closed together.
- **A parcel.** One agent, one brief.
- **P0.** The lead's own first piece of work: what every parcel will share, done first (section 2).
- **A seam.** A place where two parcels' work meets, which belongs to neither. The seam tests are the lead's.
- **A long run.** A run that takes long enough to be the lead's to monitor, not a parcel's (OWNER.md, rule 2).
- **A time box and a scope ceiling.** How long a brief expects a first pass to take, and how large it expects the
  change to be. The record sets each against what happened.
- **The integration verifier.** A verifier on the lead's own work: its merges, its seam and its record. It makes
  each merge again from its parents (section 7).

## The record

- **The ledger.** The round's working channel: one file per author, append only, outside every worktree, archived
  at the round's end with its timestamps (section 4).
- **`urgent/`.** The ledger's directory for messages that mean "stop and read this": one file per message, renamed
  into place.
- **An escalation.** A question or finding that cannot wait for a read moment. It goes to its reader at once, and
  into the ledger first.
- **Three things called a ledger.** In this kit, "the ledger" is ParcelRound's round ledger, above.
  HonestFramework's "validation ledger" (method/honest/templates/ledger.md) is the project's record. And
  cft-fp256's record, quoted in the samples, calls itself a ledger in its header (OWNER.md, rule 10).
- **The record.** The project's own dated entries, in the project repository, of what ran and what it showed. The
  ledger is folded into it.
- **The chain.** A record table with one row for each piece of work: its author, its verifier's passes with (a) and
  (b) per pass, and how often it was sent back (examples/cases/20-record-skeleton.md).
- **Logan's word.** A decision of his, quoted as he gave it, with its date.
- **A standing rule.** One of his decisions that is carried into every round's plan (OWNER.md).

## Gates

- **A gate.** A check that can fail, and has been watched to fail (HonestFramework
  [METHOD.md](method/honest/METHOD.md), section 3).
- **A negative control, or a plant.** A fault put in on purpose, to show that a gate catches it.
- **The front door.** The one command that answers "does it still hold?" (HonestFramework, section 10).
- **The authority.** The one thing that defines a correct answer, and cannot argue (HonestFramework, section 1).
  The study names it.
- **A planted copy, and its key.** A copy of a parcel's work that may hold faults the lead put in, and the file that
  says which. The verifier treats every finding as real (WORKFLOW.md).
