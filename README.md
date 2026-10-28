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
is a 3-minute programmatic video; this repository is the library, the video
pipeline and rendered cut, and the record that stands beside them.

## Status

**Tier 1 complete and Tier 2's authorised prefix landed:
822 of 822 instantiations, three workloads bit-identical on
silicon.** [SF-0](docs/studies/SF-0.md),
[SF-1](docs/studies/SF-1.md) and
[SF-2](docs/studies/SF-2.md) are the approved plans of record.
The full Clause 5 surface for binary16/32/64 is implemented
and gated (783/783) — arithmetic, FMA, conversions,
comparisons, totalOrder, and correctly rounded decimal/hex
character conversions (H=20) — plus 39 Tier 2 rows: Clause
9.6 minimum/maximum semantics, the payload accessors, and
correctly rounded `sinPi`/`cosPi`, every family at all three
formats. Each row is gated against Berkeley TestFloat 3e,
MPFR, or an exact reference at the volume its authority
names (171,423 committed vectors; `standard` adds 1,117,504),
and verified wave by wave on planted copies by independent
Spark verifiers (61 of 65 plants caught to date).
Three workloads run bit-identically on the RP2040: REBOUND's
IAS15 integrator over the AEABI compat surface reproduces the
unmodified desktop build's state hashes for 2,000 steps
(2,001/2,001 records); an interval-geometry catalogue streams
host==board bit-for-bit; and KissFFT — BSD-3, scratch-only,
with the one named Fork B change (exact cycle fractions into
`sinpi`/`cospi`) — matches all 12 configuration hashes at the
gated sizes N=256/1024/4096. Per-instantiation status lives in
[docs/COVERAGE.tsv](docs/COVERAGE.tsv); the story, with its
slips attributed, is [docs/RECORD.md](docs/RECORD.md).

The front door is `tools/run.sh <smoke|standard|board|bench>` under
Git Bash: it prints its inventory before any verdict, refuses drift
and each named negative control, and `standard` is the merge gate
(AGENTS.md has the budgets and their measured costs).

Wave 5 (SF-2) is under way: `roundTiesToAway` has landed as
the fifth public rounding attribute across all 255
attribute-carrying rows; `rSqrt`/`hypot`, the `exp2`/`log2`
pairs, and Clause 9.5 augmented arithmetic follow in SF-2's
order. Still deliberately not implemented — deferred or
refused by name in SF-1 §7 and SF-2 §1: the remaining Clause
9.2 functions (`pow`/`powr` refused in any first sequence),
Clause 9.4 reductions, dynamic rounding wrappers, and
public `roundToOdd`. Binary128, decimal formats, and Clause
8 alternate exception handling are out of this project
entirely (SF-0 §2.7). Anything beyond this list needs a new
study and owner approval before it is briefed.

## Demo video

The silent 180-second cut is
[video/out/final.mp4](video/out/final.mp4). Its frame-rendering
pipeline, data loaders, timelines, and source-traced storyboard live in
[video/](video/README.md). Music remains an owner decision; the timeline
is built on a 120 BPM grid so a licensed track can be dropped in later.

## Where things live

| path | what |
|---|---|
| `docs/KICKOFF.md` | the owner's words verbatim, the lead's readings, open questions |
| `docs/HARNESS.md` | how the methods' mechanisms map onto Muse, measured |
| `docs/BOARD.md` | the Pico: protocol and filled details |
| `docs/studies/` | SF-0, SF-1 and SF-2, the approved plans of record |
| `docs/RECORD.md` | dated run entries, the project's record |
| `docs/COVERAGE.tsv` | per-instantiation coverage ledger: status, deciding authority, vector set (generated) |
| `docs/WIDTHS.md` | internal exact-integer widths, with proof notes |
| `tables/` | the format + operation tables everything else is generated from |
| `include/`, `src/` | the library: generated public header, exact-integer core |
| `compat/` | AEABI/toolchain compatibility layer (per-core wrapper state) |
| `tests/` | host runner, exact-reference vector generation, committed vector sets |
| `board/` | RP2040 firmware: CDC replay harness, interposition hello, IAS15 / interval / KissFFT workloads, bench skeleton |
| `tools/` | the front door (`run.sh`), table generator, metrics extractor |
| `video/` | programmatic demo-video pipeline, IAS15 hash captures, storyboard, rendered cuts |
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
