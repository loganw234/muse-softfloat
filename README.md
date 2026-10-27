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

**P0 (the shared seam) landed, 2026-10-26; Wave 1 next.** [SF-0](docs/studies/SF-0.md)
is the approved plan of record. The seam is in: the generated API over
783 operation instantiations (63 implemented and gated — classification,
sign-bit, flag and version operations for all three formats, plus the
binary64 round-and-pack exemplar), the host runner, Berkeley/MPFR
oracle bring-up, and the RP2040 board harness with on-silicon replay.
No arithmetic operation is claimed yet; per-instantiation status lives
in [docs/COVERAGE.tsv](docs/COVERAGE.tsv).

The front door is `tools/run.sh <smoke|standard|board|bench>` under
Git Bash: it prints its inventory before any verdict, refuses drift
and each named negative control, and `standard` is the merge gate
(AGENTS.md has the budgets and their measured costs).

## Where things live

| path | what |
|---|---|
| `docs/KICKOFF.md` | the owner's words verbatim, the lead's readings, open questions |
| `docs/HARNESS.md` | how the methods' mechanisms map onto Muse, measured |
| `docs/BOARD.md` | the Pico: protocol and filled details |
| `docs/studies/` | SF-0, the approved plan of record |
| `docs/RECORD.md` | dated run entries, the project's record |
| `docs/COVERAGE.tsv` | per-instantiation coverage ledger: status, deciding authority, vector set (generated) |
| `docs/WIDTHS.md` | internal exact-integer widths, with proof notes |
| `tables/` | the format + operation tables everything else is generated from |
| `include/`, `src/` | the library: generated public header, exact-integer core |
| `compat/` | AEABI/toolchain compatibility layer (per-core wrapper state) |
| `tests/` | host runner, exact-reference vector generation, committed vector sets |
| `board/` | RP2040 firmware: CDC replay harness, interposition hello, bench skeleton |
| `tools/` | the front door (`run.sh`), table generator, metrics extractor |
| `docs/metrics/` | the metrics inputs (usage, passes, briefs, fetches, …) |
| `AGENTS.md` | notes for agents: the front door, the authority, what bites |

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
- Git operations run under the owner's standing permission (2026-10-26);
  his words and the lead's readings are in `docs/KICKOFF.md`. Commits carry
  detailed bodies with verification and ledger references, and AI-authored
  commits carry the committing model's Co-Authored-By trailer.
- Developed clean-room from the standard: no third-party softfloat source is
  copied into the library, even where licences allow (SF-0 §4.5). Oracles are
  fetched by recorded hash and only executed.

## Licence

MIT — see [LICENSE](LICENSE) (Copyright (c) 2026 Logan W.). Third-party
code keeps its own licence; REBOUND is GPL and will appear, if at all, only
as a separately-licensed demo workload, never inside the library.
