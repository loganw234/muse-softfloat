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

## 2026-10-26 - SF-0 verified, approved, and licensed MIT; P0 gate open

**What the owner asked**, verbatim: "Go ahead with SF-0"; then "Looks
good, go ahead. The only slight change is more IEEE 754 compliance if time
allows it"; after the study was pushed for approval, "Everything looks
good with the recommendations, go with MIT for the license."; asked only
for the copyright holder, "Logan W. works fine".

**The lead's reading, beside it:** the approval covers all nine SF-0
Section 12 recommendations, including Q12.8's standing-rule/cap defaults
as amended and Q12.9's settled-in-body package. It does not confirm the
kit-zip builder hash, choose extra clean-room fencing, or state whether a
Debug Probe is attached; all three stay open by name and none blocks P0.

**The chain** (READ, ledger verdict entries; (a), (b) per pass):

| work | author | verifier's passes | sent back |
|---|---|---|---|
| SF-0 study (draft 1 `33c59f9`; draft 2 `4f7f870`; draft 3 pushed `828b8f1`) | the lead | verifier-sf0 0, 6 - 15 notes; rechecker-sf0 0, 2 - 4 notes; rechecker2-sf0 0, 0 - 1 note (all muse-spark-1.3) | twice — restated in place before push; READY at the study cap (3 drafts + 2 re-checks) |
| this approval-recording change (LICENSE, approval entries, status lines) | the lead | Spark verifier named in its commit message | no (at writing) |

**Measured:** the approved study is `docs/studies/SF-0.md` at
`828b8f1`, confirmed on `origin/main` by the remote's own answer before
approval. The independent SF-0 evidence audit's open holes that draft 1
had not yet dispositioned (decimal authority design, per-instantiation
coverage, oracle bring-up, board sample scope, Tier 2 entry criteria)
were dispositioned in draft 2 and checked in both re-checks. Approval and
licence are recorded here, in SF-0 Section 14, in the KICKOFF appendix,
and in the ledger at 2026-10-26 13:57:41 -0700; the licence file itself
is `LICENSE` (MIT, Copyright (c) 2026 Logan W.).

**Known limits:** SF-0's approval approves a plan, not an implementation:
no library code, runner, oracle build, or board proof exists yet, and the
unproven board serial channel remains P0's top named risk. Metrics for
agents after the Wave 0 cutoff (SF-0's verifiers included) are counted in
the next entry, not restated into Wave 0's snapshot.

## 2026-10-26 - P0: the shared seam, gated on host and on silicon

**What the owner asked**, verbatim: "Go ahead and proceed. Good work so
far"; during the run, "*Other work is also in progress on this machine,
as such your runs may face slow downs from resource contention. No need
to adjust for it, simply notifying you".

**The lead's reading, beside it:** proceed means P0 exactly as SF-0
Section 6 enumerates it, lead-authored, Spark-verified before push.
Timings measured today were made under load and are recorded as such,
never as performance evidence.

**The chain** (READ, ledger verdict entries; (a), (b) per pass):

| work | author | verifier's passes | sent back |
|---|---|---|---|
| approval-recording change pushed at `0bfa964` | the lead | verifier-approval 0, 0 - 3 notes (muse-spark-1.3) | no |
| P0 shared seam (this commit) | the lead | Spark verifier named in its commit message (P0 acceptance, SF-0 §6) | no (at writing) |

**Measured** (host x86_64-w64-mingw32 gcc 16.1.0, `FLT_EVAL_METHOD=0`
probed; Arm GNU Toolchain 14.2.1 for target objects; all under load):

- Tables and generation: `tables/` expands to **783 instantiations**
  across S1's 81 families (comparison names re-measured), 63
  implemented, 0 with unconfirmed authority; the four generated files
  regenerate byte-identically (drift check in every budget).
- Gates: `smoke` PASS with 17,662 committed vectors; `standard` PASS
  adding 917,504 exhaustive-binary16 and 200,000 seeded pack64-sweep
  vectors against the independent exact-rational reference (37,821
  sticky-non-invariant sweep cases dropped by construction, counted).
  Flag operations are gated by a 32x32 exhaustive state machine in the
  runner's unit mode. Target symbol scan clean (undefined: only
  `__aeabi_lmul`, a switch helper, and the library's own symbols).
  Eight negative controls each refused: corrupted expected bit, wrong
  NaN expectation, wrong rounding mode, wrong flag bit, stale
  manifest, count mismatch, wrong-tininess-polarity build, x87
  compiler path. Remaining §5.2 controls arm with their surfaces
  (bootrom cases and wrong-board-identity with board budgets in later
  waves; decimal-oracle range in Wave 3; the wrapper-state leak is
  exercised as contract-observed sharing in the hello below).
- Oracle bring-up: Berkeley SoftFloat 3e + TestFloat 3e fetched from
  jhauser.us (SHA-256s and licence hashes in
  `docs/metrics/fetches.jsonl`), built in scratch (8086-SSE,
  tininess after rounding read in its `specialize.h` and echoed by
  `testsoftfloat`), self-check clean on 10 sampled functions.
  Header-measured coverage matches the authority map in
  `docs/COVERAGE.tsv` (no nextUp/scaleB/logB/totalOrder/class/decimal;
  integer conversions 32/64-bit only). Berkeley's invalid integer
  deliveries are the indefinite patterns (signed-min/unsigned-all-ones),
  differing from the project saturation rule in the header — hence the
  `exact-invalid-project-rule` comparison on those rows. Its flag bit
  order differs from ours; translation at ingest is specified in
  `tests/VECTORS.md`. Vector pricing per rounding slice, seed 1:
  binary ops level 1 = 46,464 cases, level 2 = 40,284,288 (81-97 s to
  generate); mulAdd level 1 = 6,133,248; unary/conversion slices
  408-768. A first cross-check agrees: our `is_signaling` vs Berkeley
  `isSignalingNaN`, 65,728 encodings, 0 disagreements. MPFR 4.2.2
  re-measured live through the pinned path.
- Board (RP2040 rev B2, unique ID `e66440a2cb6f5c2b`, COM8, under
  `board.lock`): 968 board-smoke vectors replayed over USB CDC,
  whole-run SHA-256 `4573ac098f2f8a5bf8c6b09fb9746ee206e24a3870c19b4b07f3dd3fee5f28a7`
  identical on host and board; harness UF2 `987bb37b...`, ELF
  `020de7f9...` (per-build hashes, printed each run). Interposition
  hello PASS (12/12): `--wrap=copysignf/copysign` over the core,
  cross-core state isolation, same-core IRQ sharing observed as the
  §3.4 contract states (flags `0x12` after IRQ), save/restore
  round-trip. Reflash cycles are hands-free via `picotool load -f -x`.
  Bench skeleton runs under both SDK flavours with placement/clock
  labels and identical sinks; per §6 item 9 no number from it is
  quoted as a performance claim.
- Metrics: transcript extraction at cutoff 2026-10-26T17:31:58-07:00
  (scratch output; committed `usage.jsonl`/`passes.jsonl` still end at
  the Wave 0 cutoff by design): 26 work sessions, 848,844 output /
  143,025,602 input tokens (Wonder 646,782 / 122,367,746; Spark
  202,062 / 20,657,856), 1,568 tool uses, 28 internal reminder
  sessions excluded and counted. New shapes `briefs/corrections/
  escalations/plants/fetches` JSONL exist beside them; rows begin
  with Wave 1 (plants at their reveal).

**Slips, attributed:** the lead's own wide-integer spot-check had two
wrong expectations (code was right; test fixed); the first board
budget printed PASS over a failed second flash because `run.sh` did
not propagate the sub-script's exit (fixed in the same commit, and
the failure itself — picotool needing `-f` — is now BOARD.md/AGENTS
text); an oracle pricing probe wrote 3.4 GB of vector files before
being stopped and replaced by streaming counts (SF-0's rule); a
per-file `>>` manifest loop hit a measured offset-0 append quirk,
fixed by single-stream writes.

**Known limits:** no arithmetic operation is implemented or claimed;
the 63 gated operations are the P0 set of SF-0 §6 item 4 only, and
the round-and-pack exemplar is gated as an internal operation
against the project-exact reference, not yet through a public
operation. Berkeley vectors are priced but not yet wired into the
runner (Wave 1 owns the ingest + flag translation). Board evidence
covers the 968-vector smoke sample, not full-volume replay. Metrics
tables extend at the next record close; the extractor still needs
its wave-split and label updates for that, named here so it is not
discovered then.

## 2026-10-27 - Wave 1: binary32 and binary64 arithmetic, verified under plants

Two format parcels (ParcelRound, 300-minute boxes, 3,000 hand-written
line ceilings, `ledger/briefs/w1-f32.md` / `w1-f64.md`) implemented the
full homogeneous Clause 5 core for binary32 and binary64: 173
instantiations each, taking the project to 409 of 783 implemented
(63 P0 + 173 + 173), with 0 instantiations at `authority=unconfirmed`.
Parcels owned only `src/msf32.c` / `src/msf64.c`, their vector
generators and sets, and status-row appends; the shared kernels
(`msf_pack_generic`, `msf_decode.h`) stayed lead-owned, and anything
inadequate there was an escalation, not an edit. That fence is what
caught the wave's largest defect (below).

- Checkpoints `6c1bc01` (f32) and `5153324` (f64) stopped correctly
  on lead-owned defects: the P0 pack kernel implemented tininess on
  the delivered value, not Clause 7.5's unbounded-exponent rounding,
  and the Python reference implemented the same wrong reading, so
  every self-consistent gate passed. Berkeley disagreed; parcel-f32
  escalated with a repro and was upheld. Both parcels independently
  found the ingest tool mapping Berkeley's quiet `eq` to signaling
  (f64 with a 46,464-case proof). Lead fixes `53acb1a` (kernel +
  reference + vector regeneration; the corrected reference failed
  the old kernel first) and `b37fb12` (smoke control 9 named a
  now-implemented op; LF normalisation) were Spark-rechecked READY
  (rechecker-tininess, oracle differential 2400/2400) and pushed.
  Fresh regater agents then closed both parcels READY (`26c76aa`,
  `cb10ee2`); combined post-fix Berkeley evidence exceeds 37M cases.
- Verification: planted copies (kit `plant.py`, first use) at
  `1779df0` (f32) / `d1e9442` (f64), five plants each spanning code
  semantics, flags, committed vectors, and generator constants; key
  SHA-256s `71ef8ff1...` / `e6bbc65c...` were ledgered before the
  verifiers ran and never disclosed to them. Both Spark verifiers
  returned NOT READY on the copies, as constructed. Graded against
  the keys: **9 of 10 plants caught** (f64 5/5; f32 4/5). The one
  miss is the instructive one: a weakened boundary value in the f32
  generator pool was observed as 16-line regeneration drift but
  filed benign because expectations were arithmetically correct on
  both sides - detection without the project's byte-identity norm.
  No non-plant defect stands: the f32 verifier's (a) findings
  (shared-file changes vs base; parcel vectors unwired from `run.sh`
  in the copy) are copy artifacts - the shared files carry the lead
  fixes the parcel branch merged, and the wiring landed on main in
  `704cf0c` / `8d8219c`. Grades in `docs/metrics/plants.jsonl`.
- Merged serially onto main (`2843792` f32, `06fdec8` f64;
  `implemented.tsv` union to 409 rows, tables regenerated).
  `tools/run.sh standard` PASS after each merge; final state: smoke
  52,168 committed vectors and 9/9 negative controls refused,
  standard adds 1,117,504 (timings under known machine load, never
  performance claims). Board: 2,767 sampled committed binary32/64
  vectors replayed on the RP2040 (ID `e66440a2cb6f5c2b`, under
  `board.lock`), whole-run SHA-256
  `4d7c2a28581a36381d4ccf5084f3e909b68e186a763d45341c48ced427b329af`
  identical on host and board; harness UF2 `3c7f66a1...`, ELF
  `5de04aab...` (per-build hashes).
- Metrics (`round_metrics.py --wave wave1`, kit tool, repo counted):
  Wonder parcels+regaters 272,858 output / 77,372,569 input tokens,
  503 tool uses, ~129 minutes; Spark verifiers+rechecker+auditor
  371,597 output / 93,246,932 input, 568 tool uses, ~61 minutes.
  Parcels used 48 and 56 of 300 boxed minutes; regaters 12 and 13
  of 120. Escalations: 3 real (median 2 minutes to ruling, longest
  41) plus 2 first-minutes tests answered in ~20 seconds. Brief
  corrections: 7 offered, 7 accepted. Note `round_metrics` counts
  all changed lines including generated vectors (14,219 / 14,301)
  against a ceiling the briefs define as hand-written lines
  (1,788 / 1,814 of 3,000); `ceiling_text` in `briefs.jsonl` says
  which is which. The lead's own session is cumulative across waves
  and is not delta-extracted; that remains owed tooling.

**Deviations, named:** the local merges onto main preceded the
planted verifiers' reports, against the kit's verify-then-merge
sequence; nothing was pushed between, and the push gate held until
grading left no genuine send-back. The lead ledger was silent from
22:14 to 05:23 across checkpoints, fixes, regates, and merges; the
gap was caught by the owner and backfilled as a marked backfill,
and from here every commit or merge gets a ledger entry in the
same step. Verifier tasking lived in Workflow prompts rather than
brief files; briefs become files from Wave 2. A mid-project
adherence audit (auditor-wave1, Spark, disconfirm-only) confirmed
the above independently and added the re-check list this entry's
close-out worked through; such an audit now runs at the end of
each significant wave, by owner request.

**Slips, attributed:** the tininess defect was the lead's, twice
over (kernel and reference agreeing wrongly); the parcels' fence,
not the lead's gates, caught it. The ingest `eq` mis-mapping was
the lead's. Parcels initially ended at checkpoints rather than
closing, because finished agents return tool-less on follow-up;
fresh regaters are now the standing pattern for send-backs.

**Known limits:** binary16 and the remaining cross-format rows are
Wave 2; decimal/hex is Wave 3 and still the largest design risk.
Berkeley level-2 slices were largely take-capped for wall-clock
under load; the integration verifier's merge-tree re-make remains
owed at final wave. Metrics: Spark Workflow sessions arrive
labelled by session UUID and were relabelled by content/stamp
attribution in the fold (noted per row); the extractor's role
inference needed lead restatement for parcel/regater/verifier
rows (also noted per row). Board evidence is a 2,767-vector
sample, not full-volume replay.
