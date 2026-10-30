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
is a 169-second programmatic video; this repository is the library, the video
pipeline and rendered cut, and the record that stands beside them.

**Live demo:** [loganw234.github.io/muse-softfloat](https://loganw234.github.io/muse-softfloat/) — the actual library compiled to WebAssembly, runnable against the committed test vectors ([site/](site/README.md)).
**Reproduce the workloads:** `bash demo/run_demo.sh host` ([demo/](demo/README.md)) — fetches the pinned REBOUND/KissFFT archives into a gitignored cache and re-proves the workload hashes on your machine (one stale interval expectation is named in step 4 below).

## Start here

Five steps, in order: watch, click, run, reproduce, audit.
Each step stands on its own, so stop whenever you have seen
enough.

1. **Watch the film (about three minutes).**
   [video/out/assembly_v5.mp4](video/out/assembly_v5.mp4)
   runs 169 seconds at 2560x1440 and tells the whole story:
   the library, the orbit integrator running on the Pico,
   and how every answer was checked. It is silent on
   purpose — music is still the owner's decision, so there
   is nothing wrong with your speakers. How it was made:
   [video/README.md](video/README.md).
2. **Try the library in your browser (a minute).** The
   [live site](https://loganw234.github.io/muse-softfloat/)
   runs the actual library, compiled to WebAssembly — not a
   recording. Under "The instrument", press **Deal me a
   committed vector**, then **Run**, and compare the result
   bits and flags with the dealt line; or pick a format and
   operation and type your own operands. 822 of the 849
   operations run there; the page itself names the ones it
   leaves out and why. Then skim "The numbers", "On
   silicon", and "How this was verified". How the page is
   built: [site/README.md](site/README.md).
3. **Run it yourself (set aside five minutes).** From the
   root of a fresh clone (Git Bash on Windows), first:

   ```
   bash examples/host/build.sh
   ```

   That builds the library plus one small example program,
   runs it, and checks every printed line against the
   committed expected output ([examples/](examples/README.md)
   explains what the example shows; a matching Pico version
   lives beside it). Then the fast test gate:

   ```
   bash tools/run.sh smoke
   ```

   It rebuilds everything, runs the unit tests and all
   411,213 committed test vectors, and finishes with checks
   that are designed to be refused — a passing run ends
   `budget smoke: PASS` (27 seconds on the project desktop
   when this map was written; that is a record from that
   machine, not a promise about yours). The same gates run
   on Linux for every push
   ([.github/workflows/ci.yml](.github/workflows/ci.yml),
   four jobs: `smoke`, `standard`, `example-host`, and
   `sanitize`). `standard` is the bigger gate a merge must
   pass, and `example-host` re-runs the example above. The
   full `sanitize` flavour runs only in that CI job; the
   project Windows host runs its lighter trap flavour.
4. **Reproduce the three workload proofs (a few more
   minutes, needs network once).**

   ```
   bash demo/run_demo.sh host
   ```

   This downloads two pinned archives, checks their hashes
   before opening them, and re-runs the three public
   workloads on your machine: the orbit integrator for
   2,000 steps (2,001 step records compared), KissFFT with
   its one named change (12 configurations compared; the
   change is described in [demo/README.md](demo/README.md)
   and [docs/TWIDDLES.md](docs/TWIDDLES.md)), and a 710-row
   interval-geometry catalogue. One known gap, stated
   plainly: the interval leg currently reports FAIL because
   its committed expected file still carries the older
   `ce81d66e…a9aec` hash, while the program now prints
   `ae04caf0…c1422` — the newer recorded value from when
   that workload started using the augmented operations
   (its per-row answers did not change; its counted calls
   did, and the count is part of the hash). The other two
   legs passed when this map was written; the script as a
   whole will keep exiting FAIL until that one expected
   file catches up.
5. **Audit how it was made (as deep as you like).** Start
   with [docs/RECORD.md](docs/RECORD.md), the dated history
   of what was claimed and when — failures stay in it.
   Then follow the reading order under "How to audit" in
   [audit-bundle/README.md](audit-bundle/README.md): the
   record first, then the frozen briefs and ledgers behind
   any line of it, then the planted-defect grades against
   their keys, then the method rules and the final
   adherence report, then re-run the gates from step 3.
   The bundle's manifest lists 576 frozen files with their
   hashes; it was frozen when the library was completed,
   and later work is appended in RECORD and the git
   history. The planted-defect score: before each piece of
   work merged, an independent verifier checked it against
   a copy carrying deliberate hidden defects. Counting the
   rows in [docs/metrics/plants.jsonl](docs/metrics/plants.jsonl)
   in this tree gives 138 caught of 145 (the latest round
   of work: 20 of 20) — recount it yourself; there is one
   line per plant.

## Status

**Tier 1 and Tier 2 complete: 849 of 849 instantiations,
three workloads bit-identical on silicon.**
[SF-0](docs/studies/SF-0.md), [SF-1](docs/studies/SF-1.md)
and [SF-2](docs/studies/SF-2.md) are the approved plans of
record. The full Clause 5 surface for binary16/32/64 is
implemented and gated (783/783) — arithmetic, FMA,
conversions, comparisons, totalOrder, and correctly
rounded decimal/hex character conversions (H=20) — plus
all 66 Tier 2 rows (66/66), every family at all three
formats: Clause 9.6 minimum/maximum semantics, the
Clause 9.7 payload accessors, correctly rounded
`sinPi`/`cosPi`, `rSqrt`/`hypot`, and the
`exp2`/`exp2m1` and `log2`/`log2p1` pairs (Clause 9.2),
and Clause 9.5 augmented addition/subtraction/
multiplication. `roundTiesToAway` is the fifth public
rounding attribute across the 273 attribute-carrying
rows; the augmented operations instead use the
clause-fixed roundTiesTowardZero (no caller attribute),
with pin P1 = R2: an exact tiny residual signals
underflow but raises no flag, and only the
unrepresentable multiplication residual raises
underflow+inexact. Each row is gated against Berkeley
TestFloat 3e, MPFR, or an exact reference at the volume
its authority names (411,213 committed vectors;
`standard` adds 1,117,504 generated checks plus a
5,505,024-check binary16 augmented-pool differential),
and verified wave by wave on planted copies by
independent verifiers (138 of 145 plants caught, as
counted from `docs/metrics/plants.jsonl` in this tree;
the SF-2-close text here pinned 114 of 120 at `bc807e6`).
Recorded one-time evidence beyond the budgets: binary32 exhaustive for each of the `exp2` and
`log2` pairs (42,949,672,960 mode-checks each, zero
mismatches) and binary16 augmented pairs exhaustive
(12,884,901,888 pair checks, zero mismatches) —
[docs/RECORD.md](docs/RECORD.md) carries the shard and
census detail. Three workloads run bit-identically on
the RP2040: REBOUND's IAS15 integrator over the AEABI
compat surface reproduces the unmodified desktop build's
state hashes for 2,000 steps (2,001/2,001 records) on
each of six chips — the genuine Pico and five
RP2040-Zero clones, with the LED-activity firmware build
itself re-verified at 968/968 harness vectors on all
six; an interval-geometry catalogue streams host==board
bit-for-bit; and KissFFT — BSD-3, scratch-only, with the
one named Fork B change (exact cycle fractions into
`sinpi`/`cospi`; derivation in
[docs/TWIDDLES.md](docs/TWIDDLES.md)) — matches all 12
configuration hashes at the gated sizes N=256/1024/4096.
The interval workload's exact stage now consumes the
augmented operations (Wave 6): over the frozen catalogue
its counted library calls measured 616,754 → 396,745
(stage 3 alone 283,314 → 63,305; the SF-2 study model
predicted 394,666 — the difference is three kept negates
per sphere row), with classifications identical on every
row and the new host == board IW1 hash `ae04caf0…c1422`.
These are counted records, not timing claims. Wave 6
also landed the on-ramp in [examples/](examples/README.md)
(the same small program over the public API on host and
Pico, its host output pinned and diff-enforced by
`examples/host/build.sh`; the Pico program printed every
host-expected line on the genuine board at its merge
gate, a RECORD entry), Linux CI, and a `sanitize` gate
budget (both below). The demo script's interval
expectation did not follow the augmented-consumption
hash move above: `demo/expected-interval.txt` still
expects `ce81d66e…a9aec`, so `demo/run_demo.sh host`
fails that one leg while its IAS15 and KissFFT legs pass
(named in step 4 of the map; the board scripts do not
read that file). Per-instantiation status lives in
[docs/COVERAGE.tsv](docs/COVERAGE.tsv); the story, with
its slips attributed, is [docs/RECORD.md](docs/RECORD.md).

The front door is `tools/run.sh <smoke|standard|board|bench|sanitize>` under
Git Bash: it prints its inventory before any verdict, refuses drift
and each named negative control, and `standard` is the merge gate
(AGENTS.md has the budgets and their measured costs). The
fifth budget, `sanitize`, runs the host runners under
sanitizer instrumentation — the trap flavour on this
Windows host, the full ASan+UBSan flavour on Linux —
with deliberate-violation canaries watched first so a
green run proves the instrumentation was live; a flavour
whose runtime is absent skips by name and prints no PASS
verdict. Linux CI
([.github/workflows/ci.yml](.github/workflows/ci.yml))
runs four Ubuntu jobs on every push and pull request —
`smoke`, `standard`, `example-host` (the host example's
output diff enforced there too), and `sanitize` at the
full flavour — and keeps each job's gate logs as
artifacts; `board` and `bench` stay lead-run against the
physical RP2040 and are not part of CI.

The metrics ledgers in [docs/metrics/](docs/metrics/README.md)
split by recency: usage, passes and escalations still end
at the SF-2 close (93 usage rows, 94 pass rows, 20
escalations counted in this tree, all Wave 5 or
earlier); briefs and plants are append-only through
Wave 6, and the plant score above is counted from
`docs/metrics/plants.jsonl` as it stands in this tree.

SF-2 is complete: its four steps (fifth attribute,
`rSqrt`/`hypot`, `exp2`/`log2` pairs, augmented
arithmetic) are all merged, and Wave 6 queue items 1–4
(augmented consumption, Linux CI, the sanitize budget,
the examples on-ramp) have landed since; submission
packaging, including the map above, follows. Still deliberately not
implemented — deferred or refused by name in SF-1 §7
and SF-2 §1: the remaining Clause 9.2 functions
(`pown`/`compound`/`rootn`, the other exp/log bases,
`tanPi` and the inverse-Pi set, radian trig,
hyperbolics; `pow`/`powr` refused in any first
sequence), Clause 9.4 reductions, dynamic rounding
wrappers, and public `roundToOdd`. Binary128, decimal
formats, and Clause 8 alternate exception handling are
out of this project entirely (SF-0 §2.7). Anything
beyond this list needs a new study and owner approval
before it is briefed.

## Demo video

The current silent cut is the 169-second, 2560x1440
[video/out/assembly_v5.mp4](video/out/assembly_v5.mp4) (the earlier
180-second 1080p cut remains at
[video/out/final.mp4](video/out/final.mp4)). Its frame-rendering
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
| `docs/TWIDDLES.md` | the KissFFT Fork B twiddle-provenance derivation, retained in full |
| `tables/` | the format + operation tables everything else is generated from |
| `include/`, `src/` | the library: generated public header, exact-integer core |
| `compat/` | AEABI/toolchain compatibility layer (per-core wrapper state) |
| `tests/` | host runner, exact-reference vector generation, committed vector sets |
| `board/` | RP2040 firmware: CDC replay harness, interposition hello, IAS15 / interval / KissFFT workloads, bench skeleton |
| `examples/` | the on-ramp: the same small public-API program on host (one-command build/run/diff) and on the Pico |
| `demo/` | one-script reproduction of the three workload proofs from a fresh clone |
| `site/` | the live demo page: the library in WebAssembly over the committed vectors |
| `audit-bundle/` | frozen method evidence for external auditing: kit, ledgers, plant keys, reports, with a hash manifest |
| `.github/workflows/` | Linux CI (`ci.yml`: smoke, standard, example-host, sanitize) and the Pages publish workflow |
| `tools/` | the front door (`run.sh`: smoke, standard, board, bench, sanitize), table generator, metrics extractor |
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
  stands between each parcel and the push to this public remote. The lead's
  own wiring/record commits are not planted-verified parcel-style; they are
  gated by `standard` and named as lead work in RECORD (the final adherence
  audit grades the distinction) — local commits may be restated in place
  until pushed.
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
