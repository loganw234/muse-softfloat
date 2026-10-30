# Start here

This kit is for the lead and the agents of a ten-day hackathon, Monday 2026-10-26 to Wednesday 2026-11-04. The
work is an IEEE 754 softfloat for the RP2040, in binary16, binary32 and binary64 (PROJECT.md). The way of working
is two methods of Logan's, which this kit carries whole:
- **HonestFramework** ([method/honest/](method/honest/README.md)): no claim about the work rests on an agent's
  judgement. Every "is this true?" is answered by something that cannot hold an opinion: a reference, a gate
  watched to fail, a hash, a record with dates on it.
- **ParcelRound** ([method/parcelround/](method/parcelround/README.md)): one lead splits the work into parcels,
  each agent with a brief, a ledger between them, a verifier between each parcel and the merge, and serial merges.

The work's own repository, made at kickoff, is called **the project repository** in this kit.

Logan is the owner. He is also measuring how you handle these methods, so the record you keep is half of what this
hackathon makes (METRICS.md).

## First, before anything else

1. **Run the kit's gate**, from this directory: `python3 -I tools/check_kit.py`. It must end
   `VERDICT: PASS, all five checks hold`. If it does not, stop, and tell Logan what it printed.
   `python3 -I tools/check_kit.py --control` shows that each of its checks can fail. A PASS shows that the kit
   matches its own MANIFEST.txt, which a changed kit could carry changed with it. What shows that it is the kit
   that was built is the zip's sha256: confirm it with Logan, who has it from the builder's record.
   The kit's commands call Python 3 `python3`; on Windows it may be `python` or `py -3`. The gate and the tools
   need git as well.
2. **Read [CLEAN-ROOM.md](CLEAN-ROOM.md).** One repository of Logan's is off limits, and the file says why, what
   counts, and what to do if a search lands there.

## Five things that bind from the first minute

1. **The clean room** ([CLEAN-ROOM.md](CLEAN-ROOM.md)).
2. **The ledger.** One file per author, append only, outside every worktree, each heading stamped from `date`,
   never from memory ([WORKFLOW.md](WORKFLOW.md); [the ledger's README](method/parcelround/templates/ledger.md)).
3. **Escalation.** What cannot wait for a read moment goes to its reader at once, and is written in the ledger
   first.
4. **Nothing is committed or pushed without Logan's word** ([OWNER.md](OWNER.md), rule 7), until he says otherwise
   at kickoff.
5. **The kit is frozen.** Nothing you fill in lives inside it. [HARNESS.md](HARNESS.md) and [BOARD.md](BOARD.md)
   are templates, and their filled copies go in the project repository. A changed file fails the gate's check 1.

## What to read, by role

Read in this order. A parcel's and a verifier's own brief comes first for them, and the lead writes it.

<!-- reading:begin -->
| who | order | file | bytes |
|---|---:|---|---:|
| everyone, first | 1 | [CLEAN-ROOM.md](CLEAN-ROOM.md) | 4,436 |
|  | 2 | [ROLES.md](ROLES.md) | 5,794 |
|  | 3 | [GLOSSARY.md](GLOSSARY.md) | 6,676 |
| the lead, before the first dispatch | 1 | [OWNER.md](OWNER.md) | 9,434 |
|  | 2 | [WORKFLOW.md](WORKFLOW.md) | 12,075 |
|  | 3 | [PROJECT.md](PROJECT.md) | 3,903 |
|  | 4 | [METRICS.md](METRICS.md) | 4,192 |
|  | 5 | [HARNESS.md](HARNESS.md) | 2,929 |
|  | 6 | [BOARD.md](BOARD.md) | 1,892 |
|  | 7 | [method/honest/README.md](method/honest/README.md) | 6,827 |
|  | 8 | [method/honest/METHOD.md](method/honest/METHOD.md) | 45,122 |
|  | 9 | [method/honest/FAILURE-MODES.md](method/honest/FAILURE-MODES.md) | 17,567 |
|  | 10 | [method/parcelround/README.md](method/parcelround/README.md) | 5,987 |
|  | 11 | [method/parcelround/METHOD.md](method/parcelround/METHOD.md) | 78,224 |
|  | 12 | [method/parcelround/templates/brief.md](method/parcelround/templates/brief.md) | 9,121 |
|  | 13 | [method/parcelround/templates/verifier.md](method/parcelround/templates/verifier.md) | 9,277 |
|  | 14 | [method/parcelround/templates/ledger.md](method/parcelround/templates/ledger.md) | 9,750 |
|  | 15 | [method/parcelround/templates/checklists.md](method/parcelround/templates/checklists.md) | 13,444 |
|  | 16 | [examples/README.md](examples/README.md) | 5,889 |
| a parcel, with its brief | 1 | [method/honest/METHOD.md](method/honest/METHOD.md) | 45,122 |
|  | 2 | [method/parcelround/templates/ledger.md](method/parcelround/templates/ledger.md) | 9,750 |
|  | 3 | [AGENTS.md](AGENTS.md) | 2,943 |
| a verifier, with its brief | 1 | [method/parcelround/METHOD.md](method/parcelround/METHOD.md) | 78,224 |
|  | 2 | [method/honest/METHOD.md](method/honest/METHOD.md) | 45,122 |
| when it is needed | 1 | [method/honest/ADOPTING.md](method/honest/ADOPTING.md) | 8,167 |
|  | 2 | [method/honest/WITH-PARCELROUND.md](method/honest/WITH-PARCELROUND.md) | 6,998 |
|  | 3 | [method/honest/CASE-STUDY.md](method/honest/CASE-STUDY.md) | 11,839 |
|  | 4 | [method/honest/templates/README.md](method/honest/templates/README.md) | 3,656 |
|  | 5 | [method/parcelround/ADOPTION.md](method/parcelround/ADOPTION.md) | 30,936 |
|  | 6 | [method/parcelround/CASE-STUDY.md](method/parcelround/CASE-STUDY.md) | 14,156 |
|  | 7 | [method/parcelround/CASE-STUDY-6.md](method/parcelround/CASE-STUDY-6.md) | 23,135 |
|  | 8 | [method/parcelround/archive/round6-practice-survey.md](method/parcelround/archive/round6-practice-survey.md) | 23,833 |
<!-- reading:end -->

Sizes are bytes. For a 200K-vocabulary tokenizer, count about four bytes a token on these texts: tiktoken's
`o200k_base` gives 3.98 on the kit's copy of ParcelRound's METHOD.md, and 3.82 across all the kit's Markdown
(MEASURED at v1). Other tokenizers count differently: on that METHOD.md, Claude Code's Read tool counted about 2.9
bytes a token (MEASURED by the kit's cold reader).

## What is in the kit

| path | what it is |
|---|---|
| [START-HERE.md](START-HERE.md) | this file |
| [CLEAN-ROOM.md](CLEAN-ROOM.md) | what is off limits, and why |
| [ROLES.md](ROLES.md) | the owner, the lead, a parcel, a verifier: what each decides, asks and never does |
| [WORKFLOW.md](WORKFLOW.md) | the round, phase by phase, with what ends each; the planted-fault protocol; caps and a calendar to propose |
| [OWNER.md](OWNER.md) | Logan's words for the hackathon; his standing rules, verbatim with dates; what the lead asks him first |
| [PROJECT.md](PROJECT.md) | the softfloat charter: what is fixed, the standard's place, and the questions the study puts to Logan |
| [GLOSSARY.md](GLOSSARY.md) | the evidence tags, the finding classes, and the words of the methods |
| [METRICS.md](METRICS.md) | what is recorded, from which source, and the tables the record carries |
| [HARNESS.md](HARNESS.md) | a template: each mechanism the methods assume, mapped to your harness on day 1 |
| [BOARD.md](BOARD.md) | the Pico: who holds it, and how a board run is recorded; a template for its details |
| [AGENTS.md](AGENTS.md) | seed agent notes for the project repository |
| [NOTICE.md](NOTICE.md) | what the kit carries, and under which licence |
| [method/honest/](method/honest/README.md) | HonestFramework at `65447fd`, changed only by the rules below |
| [method/parcelround/](method/parcelround/README.md) | ParcelRound at `f42242e`, its case studies and four of its archived round ledgers, changed only by the rules below |
| [examples/](examples/README.md) | where to find prior briefs, ledgers and reviews, and samples of how things were handled |
| `reference/QRO-Crate.bundle` | QRO-Crate, a real project run with both methods, as a git bundle of `main` at `8afeede`: `git clone -b main reference/QRO-Crate.bundle QRO-Crate` |
| [tools/](tools/check_kit.py) | `check_kit.py`, the gate; `ledger.sh`, the ledger's two writes; `plant.py`, the planted copies and their keys; `round_metrics.py`, the record's tables. Each tool's first lines say how to run it, and each has a self-test (`bash tools/ledger.sh selftest`, `python3 -I tools/plant.py selftest`, `python3 -I tools/round_metrics.py --selftest`), as the gate has `--control` |
| `MANIFEST.txt` | the kit's version, its sources' commits, the rules' counts, and every file's sha256 |

## How the method texts were changed

Only by these rules. MANIFEST.txt carries each rule's count, and the builder fails if a count moves:
- **R1:** a link into cft-fp256 keeps its text and loses its target.
- **R2:** a link to ParcelRound's repository points at [method/parcelround/README.md](method/parcelround/README.md).
- **R3:** a link to a file this kit leaves out keeps its text and says "(not in this kit)".
- **R4:** inside an archived ledger, a URL into cft-fp256 stops being one.
- **R5:** inside an archived ledger, Logan's user name in a home path becomes `<user>`, an address at one of his
  personal domains becomes `<address>`, and two fragments of his identifiers, his email domain's name and an account
  id's prefix, become `<domain>` and `<id-prefix>`.
- **R6:** a URL to Logan's site becomes plain text.

Every archived ledger keeps each member's name, order and timestamp. A member no rule changed keeps its bytes.

## The kit's limits

- **Descriptions of what is not here.** ParcelRound's METHOD.md:22-24 and ADOPTION.md:11 describe
  `tools/check_method.py`, which the kit leaves out: it pins all six archives by sha256 (READ, ParcelRound's
  tools/check_method.py), and the kit carries four, repacked (MANIFEST.txt lists them).
- **Absent archives.** METHOD.md's citation forms point at ledgers archived beside the case studies. Rounds 2 and 3's
  are absent, because they record cft-fp256's own work.
- **Citations that dangle.** ParcelRound's texts and QRO-Crate cite cft-fp256 by file and line, and those citations
  dangle by design. Do not try to resolve them.
- **"Byte for byte."** CASE-STUDY-6.md:383-388 and CASE-STUDY-4.md:126 say their archives are "checked byte for
  byte". That is not true of this kit's repacked copies, only of each member no rule changed.
- **Round 4's ledgers** name cft-fp256's tree paths and API facts, but carry no code.
- **The archives were written in another harness,** and some lines name its tools (SendMessage, ToolSearch,
  Monitor, worktrees by `isolation`). Read them as that harness's. [HARNESS.md](HARNESS.md) maps each mechanism
  to yours.
- **Run the tools as commands.** Importing one from a Python of your own writes `tools/__pycache__/`, which the
  gate refuses: check 1 as files MANIFEST.txt does not list, and check 4 for what the compiled code holds. Delete that
  directory by its exact path.
- **The gate's arithmetic list is a stated limit, not a guarantee.** The docstring of
  [tools/check_kit.py](tools/check_kit.py) says why, and what backs it.
