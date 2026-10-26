# The record

Chronological, dated entries of runs and verdicts. A figure is a fact about
its run and is never updated to agree with a later belief; failures stay in.
Marks: READ a file, COMPUTED arithmetic on what was read, MEASURED a run,
BELIEVED unverified. Before a push an entry may be restated in place keeping
each pass's figures beside the new ones (owner rule 10, working default);
after a push it is append-only. The working ledger outside this repo is the
channel; this file is what it folds into. Metric tables are made by the
kit's `round_metrics.py` from JSONL inputs, and name their sources; where a
source does not exist yet, the entry says so rather than carrying a number.

## 2026-10-26 - Wave 0: readthrough, Phase 0 scaffold pushed, survey S1-S4 landed

**What the owner asked**, verbatim with dates: the project and methods test
(2026-10-23, quoted in docs/KICKOFF.md); the public remote and unsandboxed
installs, the IAS15 impact workload, Wave 1 by tonight, and begin-Phase-0
words (2026-10-26, same file); then, during this wave: "You have standing
permission to manage pushing to main as well as merges or any other related
git commands. The remaining questions can be handled conversationally as we
reach it. Once the surveyor target finishes we can record this as Wave 0
for the metrics tracking." and "*Ensure you also append a "Co-Authored"
line as the other projects commits carry indicating your model"

**The lead's readings, beside them:** standing permission satisfies rule 7
for this repo (method gates unchanged); every AI-authored commit carries a
`Co-Authored-By:` trailer naming the committing model by exact id (lead's:
Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>, address coined by
analogy, owner to correct); verifiers run on muse-spark-1.3 where the
harness admits model choice (measured below).

**The chain** (READ, ledger verdict entries; (a), (b) per pass):

| work | author | verifier's passes | sent back |
|---|---|---|---|
| Phase 0 scaffold (aec2295; e6dd094; 31e464e; pushed message-only amend dfc7a02, tree dacbd5c identical to 31e464e) | the lead | verifier-phase0 0, 3; rechecker-phase0 0, 1; rechecker2-phase0 0, 0 (scoped) | twice — the lead restated its own prose each time |
| this Wave 0 entry | the lead | verifier-wave0 (muse-spark-1.3) 0, 2 | once — restated in place before push |

**What was built:** the public repo scaffold (7 files at dfc7a02, docs/
KICKOFF.md has the inventory); the ledger with README, urgent channel and
briefs dir outside the worktree; per-agent scratch and worktree layout
(docs/HARNESS.md); project `.venv` (numpy, mpmath, pypdf, Pillow,
matplotlib, imageio-ffmpeg, ninja 1.13.2) beside system Ninja/FFmpeg.

**Measured:** kit gate
`VERDICT: PASS, all five checks hold` via Git Bash (refuses from sandboxed
PowerShell on its `\\?\` cwd — re-confirmed independently by
verifier-phase0); kit tools' selftests as recorded in KICKOFF.md, incl.
`plant.py` selftest FAILING on Windows-Python CRLF at kit plant.py:650 while
`plant.py make`/`check --dispatch` pass on a scratch repo; arm and host
compiles, a host run and an h264 test encode (those two runs were lead-run
before the ledger existed; their commands live in the session transcript,
not in any ledger file, so no figure from them is carried here);
RP2040 rev B2 answering picotool 2.3.1; escalation test file + ledger entry
agreeing to the second (2026-10-26 10:12:05 -0700), verified by the lead
reading both; model probe: native spawns expose no model choice (inherit
the lead's), a Workflow child pinned to muse-spark-1.3 self-identified
"Muse Spark", probe-ok; followed-up finished agents arrive tool-less
(4 of 4) — send-backs are newly briefed agents.

**The survey (S1-S4, read-only; full reports in each surveyor's scratch and
ledger file, headline facts only here):**

- Standard (S1): FMA is required, single-rounding; no required min/max in
  754-2019 (Clause 9.6 recommended); four binary rounding attributes (the
  ties-to-away *operations* remain required); decimal character conversions
  required for arithmetic formats with correctly rounded digits to H >= 20
  (S1's believed consequence for the 16/32/64 combination);
  binary16 is not a basic format and as arithmetic pulls in all of Clause 5;
  interchange-only binary16 still owes flag-correct conversions; NaN payload
  propagation is `should`, canonical quiet NaN is the required result;
  Clause 8 alternate handling is not required of an implementation.
- Oracles (S2): SoftFloat/TestFloat 3e are BSD-3 and frozen at 2018-01-20
  (pin the jhauser archive by hash, or a named commit — never track
  `master`, which has drifted);
  MPFR 4.2.2 is already installed and links/runs; this host's default `gcc`
  is the 32-bit x87 build (FLT_EVAL_METHOD=2) and is a bogus SSE2 oracle
  until the mingw64 toolchain is pinned first in PATH; TestFloat's declared
  blind spots are supplemented by the IBM Haifa FPgen vectors, exhaustive
  binary16/binary32-unary sweeps, and MPFR-directed binary64 randoms.
- Target (S3): pico-sdk wraps via GNU-ld `--wrap` into SDK code, only part
  of which tail-calls the bootrom; compares and 32-bit conversions are SDK
  assembler, SCI_EXTRA libm is SDK C (`fma` unfused, `fmaf` double-rounding,
  recorded in its own comments); bootrom arithmetic flushes output
  denormals to zero, treats input denormals as zero and NaNs as infinities,
  and has no exception flags at all; the default SDK
  build does not propagate NaNs. That delta is this library's reason to
  exist, and the yardstick SF-0 prices against.
- IAS15 (S4): REBOUND 5.2.2 at 262a9cc is GPL-3.0-or-later; the step needs
  no `pow` and no transcendentals — correctly rounded + - * / sqrt plus
  exact fabs/copysign/isnormal-class helpers (its sqrt7 timestep helper is
  built from those same operations); coefficient tables are decimal
  literals with far more digits than a double holds, so literal conversion
  must be pinned (or the tables carried as hex bit patterns); expression
  evaluation order in the predictor/final series is part of the numerics.

**The lead's slips, each recorded in the ledger when caught:** a misspelled
owner account in the sentence correcting the remote; an HonestFramework
link to the bare profile; absolute home paths published in two files; a
first restatement that explained the misspelling while leaving it standing;
a second restatement that added "`main` here has passed one" — a claim of
its own verdict in advance; an author date left predating the verdicts it
answered (reset). Every (b) so far was the lead's own sentence, the last two in this entry's
first form (a wrong time of day, a provenance head the ledger did not
support), caught by verifier-wave0; the parcels' so far: none. Also process: local root commit + two amends
were made under the lead's Phase-0 reading of rule 7 before the owner's
standing word above; nothing left this machine until dfc7a02 under that
word, and the remote's own answer (ls-remote) is recorded in the ledger.

**Time and tokens (MEASURED from transcripts; one pass per session):**
`tools/extract_session_metrics.py` (this commit) counts provider usage from
`model_completed` records only, distinct tool-call ids, and first/last
`recorded_at` per session; author commits and verifier verdicts are explicit
annotations from the ledger, never inferred. Snapshot cutoff
`2026-10-26T11:31:34-07:00` (the independent recount probe's end stamp), so
the figures stay reproducible while this session continues; 19 work
sessions counted, 10 internal reminder sessions excluded. The extractor's
own selftest is 8 checks, 0 failed, and an independent Spark recount of two
sampled transcripts (harness-smoke-test and verifier-wave0) agreed on every
sum before this entry carried a number. Inputs in `docs/metrics/`
(`usage.jsonl`, `passes.jsonl`); the table below was made by the kit's
`round_metrics.py` from those inputs, unedited except this paragraph.
Minutes are per-session spans, so parallel agents' minutes overlap; the
lead's single pass spans the whole wave. Ledger stamps bound the wave:
first entry 2026-10-26 10:09 -0700.

**Time and tokens** (MEASURED from the usage and the transcripts, rows marked transcribed READ from a harness's counters; minutes from each pass's start to its end):

_kit softfloat-bootstrap-kit v1 (MANIFEST.txt sha256 37d2139240af); read passes.jsonl sha256 3e64aac4b119, usage.jsonl sha256 554587b40261._

| agent | model | passes | minutes, first pass; all | tool uses | output tokens | input tokens | cached |
|---|---|---|---|---|---|---|---|
| lead | muse-wonder-full-1.0 | 1 | 124 | 231 | 116,106 | 29,136,439 | 27,798,900 |
| harness-smoke-test | muse-wonder-full-1.0 | 1 | 0 | 1 | 564 | 46,157 | 22,644 |
| reader-parcelround-cases | muse-wonder-full-1.0 | 1 | 12 | 29 | 30,233 | 1,496,621 | 1,290,780 |
| reader-honest-cases | muse-wonder-full-1.0 | 1 | 9 | 13 | 9,853 | 263,192 | 113,756 |
| reader-examples-cases | muse-wonder-full-1.0 | 1 | 9 | 25 | 17,616 | 498,847 | 387,336 |
| reader-qro-round6 | muse-wonder-full-1.0 | 1 | 9 | 32 | 17,350 | 1,963,068 | 1,784,972 |
| escalation-test | muse-wonder-full-1.0 | 1 | 2 | 10 | 7,908 | 292,469 | 253,600 |
| verifier-phase0 | muse-wonder-full-1.0 | 1 | 12 | 38 | 25,505 | 1,554,187 | 1,472,572 |
| surveyor-standard | muse-wonder-full-1.0 | 1 | 12 | 97 | 23,960 | 3,410,168 | 3,279,728 |
| surveyor-oracles | muse-wonder-full-1.0 | 1 | 14 | 56 | 28,485 | 2,160,730 | 2,047,452 |
| surveyor-target | muse-wonder-full-1.0 | 1 | 38 | 108 | 37,813 | 16,221,610 | 15,442,132 |
| surveyor-ias15 | muse-wonder-full-1.0 | 1 | 17 | 76 | 30,529 | 5,773,632 | 5,606,276 |
| rechecker-phase0 | muse-wonder-full-1.0 | 1 | 8 | 33 | 16,665 | 1,696,109 | 1,611,556 |
| main-check | muse-wonder-full-1.0 | 1 | 1 | 2 | 1,926 | 71,325 | 46,568 |
| rechecker2-phase0 | muse-wonder-full-1.0 | 1 | 4 | 19 | 10,388 | 535,109 | 487,512 |
| verifier-wave0 | muse-spark-1.3 | 1 | 6 | 57 | 30,691 | 2,555,434 | 2,401,199 |
| prechecker-wave0 | muse-spark-1.3 | 1 | 0 | 4 | 2,187 | 109,761 | 78,419 |
| spark-probe | muse-spark-1.3 | 1 | 0 | 1 | 649 | 21,851 | 0 |
| recount-probe | muse-spark-1.3 | 1 | 2 | 19 | 7,610 | 624,495 | 580,481 |

- **Sums for muse-wonder-full-1.0** (COMPUTED from the rows): 15 agents, 374,901 output tokens, 65,119,663 input tokens, 770 tool uses, about 270 minutes.
- **Sums for muse-spark-1.3** (COMPUTED from the rows): 4 agents, 41,137 output tokens, 3,311,541 input tokens, 81 tool uses, about 9 minutes.

_Not made: time boxes and scope ceilings needs briefs.jsonl, absent from metrics._

_Not made: plants needs plants.jsonl, absent from metrics._

_Not made: brief corrections needs corrections.jsonl, absent from metrics._

_Not made: escalations needs escalations.jsonl, absent from metrics._

**Known limits (owner rule: they merge):** no single verifier passed
31e464e whole — push-readiness rests on the chained scoped verdicts stated
above; the Monitor watcher wake path is unwatched-to-work until Wave 1
dispatch test escalations (S1 measured that the ledger README's bash watch
snippet dies under this harness's Monitor shell and a PowerShell form arms —
briefs must carry the PowerShell form); token figures are a cutoff snapshot
(above) — agents after it, this entry's verifier included, are counted in a
later entry, and brief-corrections/escalations/plants tables are not yet
made;
clean room has no mechanical fence (rule, briefs, disclosure, owner's
audit — KICKOFF.md); `plant.py` selftest cannot pass on this
host's Python (CRLF; the tool itself measured working).

**Records:** full method distillations in `reading-scratch/distill-*.md`
(recovered from the readers' session transcripts when their follow-up
sessions arrived tool-less); survey reports in `scratch/S1..S4/report.md`
with probes beside them; verifier verdicts in their ledger files; the QRO
reference clone in `reading-scratch/qro`. None of that scratch is in this
repository.
