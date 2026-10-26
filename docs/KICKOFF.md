# Kickoff — Phase 0, 2026-10-26

The owner's words verbatim with dates, the lead's readings marked as the
lead's, what was settled, what was only proposed, and what Phase 0 measured.
Later owner words are appended here or in the record entry that quotes them;
nothing below is edited to agree with a later belief (owner rule 10 governs
restating before a push — see "Standing rules" status).

## The owner's words

From the bootstrap kit (2026-10-23, quoted in the kit's PROJECT.md / OWNER.md):

> I plan to take part in a hackathon hosted by Meta AI, the goal is to develop an IEEE-754 compliant softfloat for RP2040, for binary16/32/64. The math library is only one portion of the project, the other portion is testing how Meta models handle the methods and systems I use, along with heavy metrics tracking (cfts most recent work has been tracked the most I believe)

Also 2026-10-23, per the kit: web access with cft-fp256 off limits; a Pico
"constantly connected for debugging" and "Lead controls hardware access";
the IEEE 754 PDF is his, licensed, given to the lead outside any repository;
models = most capable for the lead, one step down likely for parcels, settled
live; scope "Undecided yet"; a remote, "just create a private repo for now"
(superseded 2026-10-26, below).

At kickoff, 2026-10-26 (owner, in session with the lead):

> The bootstrap kit doesnt mention it much, but we will also make a programmatic video for the demo video (3 minutes) of the project, showcasing the process and methods. The timeline listed in the kit is not strict, and will likely be accelerated highly.

> Logged in, we will use a public remote for the project (the bootstrap repo was to be kept private, minor confusion there), here you go https://github.com/loganw234/muse-softfloat.git
> Go ahead and run the installs unsandboxed as needed. If unable, let me know what you need and Ill get it.

> One addition is to address the 'impact' segment of the judging criteria, my idea is to port REBOUND IAS15 to run on the Pico, proving byte identical to the unmodified desktop run in order to utilize that as both a visual demonstration and workload for the library showing actual usecases rather than just a functional library. The demo video will have to carry a significant portion of the weight of the submission, with the math library standing beside it and its product. I'd also like to advance the timeline by getting to wave 1 by tonight. Go ahead and begin with Phase 0 after you have done a thorough readthrough of the various supporting docs and details which matter (how commits are laid out, how the ledgers work and where each goes, etc.)

## Settled by those words

- **Deliverables, in parallel:** (1) the softfloat library; (2) the tracked
  metrics record of the work; (3) a REBOUND IAS15 port to the Pico as the
  demonstration workload, with byte-identity against the unmodified desktop
  run as its proof claim; (4) a 3-minute programmatic demo video carrying a
  significant portion of the submission's weight.
- **The project remote is public:** the muse-softfloat repository under the
  owner's account, at the URL quoted above; the *bootstrap* repository stays
  private, this one does not.
- **Installs may run unsandboxed** with his approval path (done: ninja,
  ffmpeg, project `.venv`; see AGENTS.md).
- **Timeline accelerated:** kit calendar is not strict; target: Wave 1
  dispatched the evening of 2026-10-26.
- **Phase 0 begins now**, after the lead's readthrough (both METHODs whole,
  all four templates, kit top-level docs; case studies / failure modes /
  examples / QRO-Crate distilled by read-only agents — READ tags in the
  ledger say which is which).

## The lead's readings (marked; owner corrects what is wrong)

1. **Rule 7 (commits/pushes).** "Begin Phase 0" + the remote above are the
   owner's word for the Phase-0 commit(s) and pushing them to this remote,
   and afterwards for parcel commits inside their own worktrees only. Every
   later push of `main` is asked for again unless he gives a standing word.
2. **Byte-identical IAS15.** Read strictly: same REBOUND source, unmodified,
   on both sides; desktop built from that source, Pico built from that source
   over this library; outputs compared bit for bit over a stated integration.
   Compiler flags that change FP semantics (contraction, fast-math) are part
   of "unmodified" to define in SF-0 — BELIEVED the two hard points are
   step-control `pow` and any non-IEEE desktop libm result; the survey
   measures both before the study promises anything.
3. **REBOUND is GPL** (to be re-read in the survey): the port lives as a
   demo workload with its own licence boundary, never inside the library.
4. **PDF custody:** the standard stays at the workspace root, outside every
   repo and worktree; the lead reads it, surveyors the lead names may read
   it; the record cites it by clause only.

## Standing rules — proposed, not yet settled line by line

The kit lists ten standing rules for the owner to confirm. He has not gone
through them yet. Working defaults until he corrects them — every parcel
brief applies these and says they are defaults:

| # | rule (short) | default here |
|---|---|---|
| 1 | only (a) regression / (b) wrong answer sends back; false sentences restated at merge | apply |
| 2 | parcels test quickly; long runs go to the lead to monitor | apply |
| 3/5 | model tiers per task difficulty | lead = muse-wonder-full-1.0; parcels/verifiers = harness default (same model) until the owner sets tiers — **open** |
| 4 | very small fixes by the lead + a verifier | apply |
| 6 | loose cap after three shrinking NOT-READYs | apply |
| 7 | no commit/push without the owner's word | apply, per reading 1 above — **confirm** |
| 8 | pause = commit where you are + resume note | apply |
| 9 | no agent loads the machine on purpose | apply |
| 10 | record restated in place until pushed; append-only after | apply, kit's reading (working ledger stays append-only always) |

**Caps (kit proposals, adopted as defaults):** study ≤ 3 drafts + 2
re-checks, then to the owner with open findings listed; verifier passes
under the loose cap; every brief carries a time box and a scope ceiling.
**One round, several waves** (kit proposal): planted-fault keys revealed
once, near the end. Verifier tier: open with 3/5.

## What Phase 0 measured (2026-10-26)

- Kit gate `VERDICT: PASS, all five checks hold` — via Git Bash only; from
  sandboxed PowerShell it REFUSES (a `\\?\` path git cannot open). Standing
  route in AGENTS.md. Kit untouched; re-verified PASS after all probes.
- Zip sha256 `d530b3ce…d33d8f01` (Get-FileHash and sha256sum agree) —
  **owner to confirm against the builder's record; still outstanding.**
- Tools: arm-none-eabi-gcc 14.2.1 and host gcc 16.1 compile+run; cmake
  4.4.4; pico-sdk 2.3.1; picotool 2.3.1 sees an **RP2040 rev B2**; git
  2.45.2; `gh` logged in under the owner's identity (repo scope; the sandbox
  identity holds no valid token, so pushes run escalated as the owner);
  remote exists, was empty.
- Kit tools: `round_metrics` selftest 43/43, `ledger.sh` 49/49 (Temp
  redirected), `plant.py make`+`check --dispatch` PASS on a scratch repo;
  `plant.py selftest` FAILS on Windows-Python CRLF (its regex at :650) —
  known limit, kit frozen, recorded not patched.
- Harness: subagent smoke parcel returned correct facts *and* a brief
  correction; subagent results auto-deliver (docs/HARNESS.md).
- **Clean-room disclosure:** clones with `cft` in their names sit beside the
  workspace under `source\repos` (directory *names* only were listed;
  nothing inside was opened, searched, or read). No mechanical fence exists;
  rule + briefs + disclosure + owner's audit carry it. Owner's fencing
  decision is an open question below.
- rmtree damage found: winget alias deleted (invoked by package path),
  ghost Ninja registration, several dead PATH entries; installs done
  (Ninja, FFmpeg 9.0.2 system; `.venv` ninja 1.13.2 + libs for the sandbox).

## Open questions for the owner

Phase 0 does not block on these; SF-0 returns with a proposal beside each.

1. Zip sha256 confirmation (above) and clean-room fencing (above).
2. Standing rules + rule-7 scope + caps + model tiers: confirm/correct the
   defaults table.
3. The study's nine (kit PROJECT.md): edition; which formats are arithmetic
   and whether clause-9 functions are in; roundTiesToAway; exception state
   on two cores + clause 8; tininess + NaN policy; interface (pico-sdk
   drop-in and/or own API, binary16 storage); speed/size targets and their
   yardstick, flash/RAM, language; pico-sdk/toolchain pins, the library's
   licence, copy-vs-read per third-party source; the authority and oracles.
4. IAS15: is a Debug Probe on the board, and may the desktop side be built
   with strict FP flags (`-ffp-contract=off` etc.) and still count as
   "unmodified"? (Survey returns facts; the definition is the owner's.)

## Accelerated calendar (target, not a claim)

2026-10-26: Phase 0 (this) → survey → SF-0 + its verifier → owner →
P0 + its verifier → **Wave 1 dispatch, evening**. Each gate still gates: if a
verifier or the owner sends something back, the date moves and the record
says so. Waves 2–3, integration + board conformance, IAS15 proof runs, video
production, close (keys, metrics tables, summary with cost) follow inside
the hackathon window (ends 2026-11-04).
