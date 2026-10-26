# muse-softfloat

An IEEE 754 softfloat library for the RP2040 — binary16, binary32 and binary64 —
built with Meta's Muse models under two working methods,
[HonestFramework](https://github.com/loganw234/HonestFramework) and ParcelRound
(the owner's methods, carried in the hackathon bootstrap kit, not in this
repository), for the
Meta Global AI Developer Hackathon, 2026-10-26 to 2026-11-04.

The workload that proves it in public: **REBOUND's IAS15 integrator running on a
Raspberry Pi Pico through this library, bit-identical to the unmodified desktop
run** — same integrator source, same bits out, on a chip with no FPU. The demo
is a 3-minute programmatic video; this repository is the library and the record
that stands beside it.

## Status

**Phase 0, 2026-10-26.** No library code yet. This commit is the scaffold:
harness and board maps, the kickoff record, agent notes. The study (SF-0, the
plan of record) comes next, then P0 (the shared seam), then parcel waves.

There is **no front door yet** — no single command answers "does it still hold?"
P0 writes it. Until then, no command's green should be read as a verdict about
this project.

## Where things live

| path | what |
|---|---|
| `docs/KICKOFF.md` | the owner's words verbatim, the lead's readings, open questions |
| `docs/HARNESS.md` | how the methods' mechanisms map onto Muse, measured |
| `docs/BOARD.md` | the Pico: protocol and filled details |
| `docs/studies/` | SF-0, the plan of record (to come) |
| `docs/RECORD.md` | dated run entries, the project's record (to come with SF-0) |
| `AGENTS.md` | notes for agents: the front door (when it exists), the authority, what bites |

The working ledger, briefs and per-agent scratch live outside this repository
(ParcelRound §4) and are archived with timestamps at the round's close.

## Ground rules this repo is built under

- Every claim about correctness is held against a named executable authority
  (SF-0 names it; IEEE 754-2019 is the contract, not the oracle).
- A gate that has not been watched to fail is not a gate; negative controls are
  permanent, named in each brief, and run.
- Work is split into parcels with briefs; a verifier that only disconfirms
  stands between each parcel (and each of the lead's own commits) and the
  push to this public remote — local commits may be restated in place until
  then.
- Nothing is committed or pushed without the owner's word. The words, with
  the lead's reading of what they authorize (owner confirmation pending),
  are in `docs/KICKOFF.md`.
- Developed clean-room from the standard and public third-party sources; each
  source's licence is recorded before anything is copied from it.

## Licence

Not set yet — the owner's decision, recorded in `docs/KICKOFF.md` when made.
Third-party code keeps its own licence; REBOUND is GPL and will appear, if at
all, only as a separately-licensed demo workload, never inside the library.
