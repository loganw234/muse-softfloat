ADHERENT WITH SLIPS — the load-bearing mechanisms (planted-copy verification, owned-file parcels, oracle clean room, append-only record) demonstrably ran on every wave, but verifier-before-main was inverted once and never fully applied to lead commits, plants were graded per wave against the approved once-at-end reveal, and the metrics inputs froze at Wave 3 while Waves 4-5 ran unrowed.

# Methods audit, Phase 0 through Wave 5 SF-2 Step 1 (auditor-adherence-2)

Freeze point: `muse-softfloat` main = origin/main = `7c3819c`
(2026-10-28 06:17:43 -0700), tree clean. Note: at dispatch main was
`889ec2e`; the SF-2 Step 1 merge chain (`6e0f2f2`, `5e5591d`,
`7c3819c`) landed in the audit's first minutes, pre-announced in
`ledger/lead.md` 2026-10-28 05:24:40. Counts below are at `7c3819c`
(82 commits reachable from main, 58 first-parent, 14 merges).
Counting scripts + raw outputs: `scratch/audit-adherence-2/{git_audit,
metrics_ledger_audit,claims_tree_audit,brief_scratch_audit,chronology,
extra,final_counts}.{py,out.txt}`, run via `run_all.sh` and siblings
(Git Bash, `MSF_PYTHON` = workspace `.venv`, TMP in scratch).
Keys: sha256 only, contents never opened (`scratch/lead/` entered for
key hashes + file names only, per auditor-wave1 precedent — disclosed).
Nothing with `cft` in its name was opened, searched, or listed.
Governing texts read: kit top level (START-HERE, WORKFLOW, ROLES,
OWNER, PROJECT, CLEAN-ROOM, METRICS, BOARD, HARNESS, AGENTS seed),
both METHOD.md whole (HonestFramework 873 lines, ParcelRound 1,448),
templates (brief/verifier/ledger/checklists heads and rule lines),
tool contracts (plant.py, check_kit.py, round_metrics.py, ledger.sh,
check_claims.py, gate-runner.sh, check_generated.py docstrings),
`muse-softfloat/AGENTS.md`, `docs/HARNESS.md`, `docs/KICKOFF.md`,
`ledger/lead.md` headings all (101 entries) + sampled bodies,
`docs/metrics/*.jsonl` all, `scratch/audit-wave1|audit-wave2|
audit-final/report.md` whole, SF-2 whole, SF-0 sampled sections,
README/BOARD whole. Sampling boundaries: Not audited, below.

## Per-mechanism grades

### 1. Verifier before main moves — held-with-named-slips

Parcel side ran: 13 planted-copy verifications (plants.jsonl: 13
verifiers x 5 plants), disconfirm-only briefs with copy fences
(`ledger/briefs/verify-w4trig.md`: never the branch, other worktrees,
keys, `scratch/lead/`, `ledger/lead.md`), and from Wave 2 merges
follow verdicts in time (W2 merges `a05412f` 08:12:45 / `71fbd53`
08:14:27 after reports 08:08/08:10 and grading 08:11:57; W3 merge
`1357863` 10:28:56 after report 10:26:52; W4/W5 merge bodies name
grades + copy hashes). Lead's own P0/study/seam/README/SF-2 went past
verifiers or planted copies, stronger than the kit's stated limit
("verifiers of the lead's own work get no plants").

Slips, counted:
- Wave 1 sequence inverted: merges `2843792` (05:17:07) and `06fdec8`
  (05:18:44) preceded the planted verdicts (05:44:48 / 05:50:22,
  passes.jsonl). Self-recorded (`ledger/lead.md` 05:58:36, 06:27:24)
  and push held until graded, but local main moved first — exactly
  PR section 7's "before main moves", and auditor-wave1 SEV-1 stands.
- One parcel merged with no verifier at all: `d9718cf` ias15-pico
  (host gates + lead-run silicon substituted, disclosed in the body;
  auditor-final section 1.1 confirms no planted verification existed).
- Lead direct commits: of 44 first-parent non-merge commits, only
  ~12 carry a named verifier/re-checker (phase0 chain, sf0 chain,
  extractor, wave0, approval, p0, w1prep, nanfix, tininess, sf1,
  w4seam, readme/sf2 branches). ~30 (wiring `704cf0c`/`8d8219c`/
  `6720f9a`/`e905868`/`6a5f95c`, runner fixes `f3c48b8`/`83622cf`,
  board firmware `72c30b7`, serial targeting `5e712cb`, and most
  RECORD commits) reached main and were pushed with no verifier
  before the push; wave auditors checked W1-W3 of these after the
  fact. `README.md:98-101` ("a verifier ... stands between each
  parcel (and each of the lead's own commits) and the push") is
  therefore a false universal sentence in the claim file itself.
- Verdicts honoured in substance after Wave 1 (no merge stands with
  a non-plant (a)/(b)), but passes.jsonl records all 8 planted
  NOT READYs as `sent_back: true` when nothing was sent back —
  the chain table round_metrics builds from those rows misstates
  the loop that actually ran.

### 2. Planted-copy hygiene — held-with-named-slips

Held: keys only in `scratch/lead/keys/` (13 `key-*.json` + drafts);
the 13 key-file sha256s equal plants.jsonl's 13 distinct
`key_sha256` exactly (extra.py set equality); key hashes ledgered
before dispatch (`ledger/lead.md` 2026-10-27 05:23:02, 2026-10-28
02:51:41 with dispatch PASS); copies in round-6 shape — sampled 4/13
(`verify-f32`, `verify2-f16`, `verify4-trig`, `verify5-attr`):
detached HEAD, one parent = parcel base, zero refs, zero remotes,
clean status; grades in metrics 61 caught / 4 missed, misses graded
missed with honest notes (w1f32 generator plant; verifier-readme
elision; verifier-sf2 plants 1 and 5), never edited to caught.

Slips:
- Reveal runs per wave, not once: SF-0 5.2 as approved says
  "revealed once near the end" (`docs/studies/SF-0.md:518-520`),
  and METRICS.md reserves the plants table for the reveal. Grading
  landed same-step every wave (12 plants.jsonl commits). No recorded
  owner decision changes this (searched `ledger/lead.md` for
  `reveal`: only check lines). Cost is concrete: graded `shape`
  texts sit in `docs/metrics/plants.jsonl` inside later verifiers'
  own copies, and no verifier brief sampled forbids reading it
  (`verify-w4trig.md` fences keys/scratch/lead.md, not plants.jsonl).
  Auditor-wave1 called this "early but contained"; I disagree —
  six waves in, the shapes are in the corpus a verifier is handed.
- Key hashes were never committed before dispatch; they first enter
  git with the grades. WORKFLOW step 3 asks for the hash in a commit
  where the owner lets the lead commit (standing permission,
  `ledger/lead.md` 2026-10-26 10:48:17), so blinding-before-dispatch
  rests on the ledger alone — HF section 9's named weakness.
- Copies were not "moved out of reach" at report (WORKFLOW step 7):
  all 13 still sit at `worktrees/verify*/` at freeze.
- All 65 plants rows claim `checked_by: integration`, but no
  integration-verifier agent or ledger file exists in any wave
  (see mechanism 8 / sharpest slip 4).

### 3. Parcels — held-with-named-slips

Brief-before-work is the norm: 38 brief files; W1 briefs are
full-template (8.9 KB, owned/forbidden, named control, 300-min box,
3,000-line ceiling, READY, brief-got-wrong — brief_scratch_audit:
`w1-f32.md`/`w1-f64.md` miss only the not-done marker). Design
entries precede code where required (parcel-f32/f64 design rulings
`ledger/lead.md` 21:55:48/21:56:25 before checkpoints 22:19/22:28;
`ledger/parcel-w4trig.md:2` design entry "written before any kernel
code"). Owned-file discipline held by escalation instead of edit
(tininess/ingest, runner bugs `f3c48b8`/`83622cf`). No parcel merged
or pushed: all 14 merges are lead first-parent commits; remote has
only `origin/main`. READY/NOT READY honoured per mechanism 1.

Slips:
- Brief shape thins every wave. `ledger/briefs/w5-attr.md` (3.6 KB)
  has time box, owned files, design-first, named controls — but no
  scope ceiling (`briefs.jsonl` row: `ceiling_lines: 0`, written by
  the parcel itself per the brief), no brief-got-wrong line, no
  READY definition, no test escalation. Same pattern across W4/W5
  parcel, study, verifier, and this audit's own brief (no time box
  or ceiling at all). Brief corrections counted in corrections.jsonl
  stop at Wave 3 (16 rows), so the dropped line shows in the data.
- Two build passes ran unbriefed (ias15-port, video-tools, Wave 2;
  auditor-wave2 area 8). The owner's 2026-10-27 strict-leaning
  risk tiers (`docs/KICKOFF.md:166-198`) settle the policy — under
  the brief's rule that is adherence for the policy question — but
  those two builds predated it and produced artifacts later relied
  on; healed only in part by the ias15-pico brief and auditor-final.
- One time box cannot bind: parcel-w4trig 2,880 min (briefs.jsonl).
- Git author is uniformly "Logan" (82/82): parcel/lead attribution
  rests on branch names, trailers naming the model, and the ledger,
  not on git — one METRICS.md cross-check (commits by agent) is
  softer than the kit assumes.

### 4. Records — held-with-named-slips (severe end)

Held: ledger outside every worktree, one file per author;
RECORD is pure-append since first push (15 commits touching
`docs/RECORD.md`, 0 deletions in every numstat row — extra.py);
the Wave 2 false "same-step" sentence was corrected by appended
erratum `4ceffa9`, not edited (owner rule 1 done right); slips are
attributed in RECORD entries sampled; owner words verbatim + lead
readings marked (`docs/KICKOFF.md`, appended, never rewritten to
agree).

Slips:
- The same-step ledger pledge (BACKFILL `ledger/lead.md` 2026-10-27
  06:27:24, after the 7.1-hour Wave 1 gap) decayed again: Wave 2
  batched entries (auditor-wave2 SEV-1), then in W4/W5 twelve ledger
  files carry no `ledger.sh` stamped heading at all
  (parcel-w4interval, parcel-w4kissfft, verifier-w3str,
  verifier-w4seam/interval/kissfft/trig, verifier-w5attr,
  verifier-readme, verifier-sf2, study-sf2-attribute,
  auditor-final — chronology.py), several without
  Measured/Believed/For. `docs/HARNESS.md:23` ("the kit's
  `tools/ledger.sh` ... is the only ledger writer briefs use") is
  no longer true. The 2026-10-28 05:24:40 lead entry batches SF-2
  approval + this audit's dispatch + w5attr READY + grading + merge
  + board into one "same step" entry written for events spanning
  ~50 minutes. Two lead entries are also out of order
  (06:42:00 before 06:38:00, 2026-10-27).
- Metrics same-step broke for Waves 4-5: passes.jsonl and
  usage.jsonl stop at 39 rows (last commit `f458f26`, 2026-10-27
  11:18); escalations.jsonl (13 rows) and corrections.jsonl (16)
  stop at Wave 3. Roughly 23 ledger-named W4/W5/readme/SF-2 agents
  have no pass/usage rows; four `ledger/urgent/` tier2 test files
  have no escalations rows; the four `sf2-*` studies have no
  briefs.jsonl rows (20 rows vs 38 brief files). RECORD's W4/W5
  paragraphs therefore carry no token/minute figures where W1-W3
  entries do (e.g. `docs/RECORD.md:570-572`).
- One post-push in-place restatement of pushed metrics rows:
  `25d6b82` rewrote 19 Wave 0 passes rows (pushed in `2bac8e9`)
  while extending them — disclosed in `ledger/lead.md` 06:38:00
  ("roles restated"), but rule 10's restate window had closed.
- RECORD "one append-only entry per wave" (SF-0 10) became
  "appended paragraphs" for Steps 1c/2c and Wave 5 Step 1 (RECORD
  tail) — append-only held, per-wave skeleton (chain tables, slips
  sections) did not survive into W4/W5.

### 5. Honest claims — held-with-named-slips

Held: claim surface is a closed set mechanically checked —
`docs/COVERAGE.tsv` at freeze: 822 rows, `status` = implemented
x822, `claim` in {required: 783, C-754: 39}, `tier` in {1,2}, zero
`unconfirmed` cells (claims_tree_audit + extra.py). Deferred-by-name
surfaces exist and stay named: SF-1 section 7, `docs/studies/SF-2.md:30-39`
(incl. `pow`/`powr` refused, 9.4 NO-GO "nowhere in the library").
Qualified sentences where it matters: KissFFT is "never unmodified"
(merge `32bbd93`, `docs/BOARD.md:120-124`); relabeled ties-to-away
vectors are provenance-tagged, never presented as decided
(`6e0f2f2` body); board string-`ta` limitation recorded, not hidden
(RECORD tail). Timings are never performance claims: perf-word scan
of README/RECORD/BOARD/AGENTS finds only negations and apparatus
(`docs/RECORD.md:231,290,369`; step rate at `docs/RECORD.md:561-564`
is a named measurement — 1.58 steps/s, 1,000-step block, 125 MHz,
UF2 named — framed as time-lapse, "never a real-time claim";
`docs/BOARD.md:91-92` compute_us "not a rate claim").

Slips:
- README, the first-read claim file, is false at freeze the day
  Step 1 landed: `roundTiesToAway` still listed deferred
  (`README.md:54`), SF-2 absent from the plans sentence
  (`README.md:20-21,75`), plants "49 of 50" (`README.md:32`)
  against 61/65 cumulative. It was planted-verified true at
  `3a12b71` and not restated at the `6e0f2f2` merge — owner rule 1
  ("restated at the merge, not left standing") missed this once.
- `README.md:98-101` verifier-between-every-lead-commit-and-push
  (mechanism 1) and `docs/HARNESS.md:23` ledger.sh-only writer
  (mechanism 4) are standing false sentences in governing docs.
- verifier-sf2 missed the planted 822+27=855 arithmetic by
  repeating it (plants.jsonl wave5 row 1) — recorded honestly as
  missed; the shipped SF-2 says 849. Included here because it
  shows the claim-check failing once and the record saying so.

### 6. Clean room — held

Fetches: 5/5 rows carry name, URL, version, archive sha256,
licence, licence sha256, date, fetcher (Berkeley SoftFloat/TestFloat
3e BSD-3, REBOUND 5.2.2 GPL-3, CORE-MATH MIT, KissFFT 131.2.0 BSD-3;
`docs/metrics/fetches.jsonl`). No vendored third-party source in the
tracked tree: 165 tracked files; marker scan over tracked
`src/`+`include/`+`compat/` finds no Berkeley/SoftFloat/TestFloat/
CORE-MATH/REBOUND/copyright text (one prose `KissFFT` word in
`compat/msf_aeabi.h`); oracles live executed-only in
`scratch/oracles/` (archives + builds), KissFFT patched in scratch
with the repo taking only wrappers/guarded targets, REBOUND
extraction scratch-only with `board/ias15_tables.h` bit-pattern data
(auditor-final re-derived this). Defective-oracle handling is
fenced by name wherever found: `cr_cospif` directed modes excluded
(Step 0b, `ledger/lead.md` line 483-484), F1 `cr_expm1`/`log1p`
directed wrong on this host (`docs/studies/SF-2.md:98,178-179`,
origin openly unresolved), raw MPFR `RNDNA` prohibited (SF-2 2;
`ledger/briefs/w5-attr.md:45-48`), MPFR `rSqrt(-0)` sign fenced
against the clause (SF-2 3), mingw `sqrt` not correctly rounded
(`muse-softfloat/AGENTS.md:64-68`), host FPU confined to SF-0 4.2's
fenced envelope with the x87 path refused by a named control.
IEEE PDF stays outside every repository (workspace root; cited by
clause). One caveat, not a slip: the owner's fingerprint audit was
waived by the owner 2026-10-27 for unfinished tooling
(`docs/KICKOFF.md:196-198`) and the record keeps saying waived
(`docs/RECORD.md:596`) — adherence by recorded owner decision,
with the control's absence stated. Blinding limits (shared
filesystem, instruction-only fences) are stated in `docs/HARNESS.md:18,22`,
not papered over.

### 7. Commit discipline — held-with-named-slips

Held: Co-Authored-By trailers 82/82 commits reachable from main
(git_audit.py); detailed bodies the norm (median 634 chars, parcel
merge bodies carry counts, hashes, ledger stamps: `75309d4`,
`20bc16b`, `da46f51`, `6e0f2f2`); merges serial, 14/14 on the lead's
first-parent chain; conflicts resolved visibly (two merge bodies
retain git's `# Conflicts:` block — honest residue, better than
silent). Slips: 15/58 first-parent bodies contain no "ledger"
reference against the owner's 2026-10-26 rule (`ledger/lead.md`
11:38:59; SF-0 10) — concentrated in the newest commits
(`7c3819c`, `5e5591d`, `6e0f2f2`, `889ec2e`, `3a12b71`, `32bbd93`);
10 bodies are under 200 chars ex-trailer, the SF-2 plan-of-record
merge `889ec2e` thinnest at 47 ("Planted-verified draft with
findings folded in."); `dfc7a02` has no body text beyond the
trailer. Auditor-wave1 graded this area ADHERED on its sample; the
full-history count says held-with-slips.

### 8. Automation honesty — held-with-named-slips

Held: gates are script files, not inline one-offs — the front door
`tools/run.sh` (268 lines) prints inventory before verdicts,
refuses drift, and carries permanent named negative controls run in
every budget (`tools/run.sh:160-222`, invoked :240): corrupted-bit,
wrong-NaN, wrong-rounding-mode (incl. the new te/ta control :183),
wrong-flag, stale-manifest, count-mismatch, wrong-tininess-polarity,
x87-refusal (loud SKIP-BY-NAME when the hostile compiler is absent,
:205), and the tier-inventory trio that replaced retired control 9.
Lead work left ~200 script files in `scratch/lead/` (names only
inspected), incl. per-wave `check_plants_*.sh`, `mergetree_check.sh`,
extract/fold scripts. Board discipline eventually structural:
board.lock cited in ledger entries for every board run; serial
targeting (`MSF_BOARD_SERIAL`, uppercase) + port pinning after the
env-hop incident (mechanism 10), clones recorded untouched.

Slips:
- The integration verifier of WORKFLOW Phase 4 step 7 never existed
  as an agent. Merge-tree re-makes were lead-run
  (`ledger/lead.md` 2026-10-27 10:36:44; "merge-tree standard PASS"
  claims at 16:35:06, 17:41:34, and in W4/W5 entries), with
  auditor-final independently re-running 6 of 14 merges. For the 8
  W4/W5 merges the re-make evidence is the merger's own. Yet all 65
  plants rows say `checked_by: integration` and merge bodies say
  "merge-tree" without an agent behind the noun. I disagree with
  auditor-final's "W2-3 CLOSED": mechanically re-run for W1-W3,
  yes; the method's independent role, no.
- Merge-time gate logs are still not cited by path in merge bodies
  (auditor-wave1 finding 7, wave2 finding 4, final F6 — third-wave
  repeat); `build/standard/` overwrites by design, disclosed.
- Multi-board flashing by bus/address preceded serial targeting by
  ~12 hours: the owner-requested clone sweep flashed both clones
  untargeted (`ledger/lead.md` 2026-10-27 14:16:23) before
  `5e712cb` landed targeting; lead itself records "should have
  landed with the multi-board test" (2026-10-28 02:24:00). Failed
  safe later only because picotool refuses ambiguous BOOTSEL sets.

### 9. Owner gates — held-with-named-slips

Held: studies approved before waves with verifiers first where it
counts most — SF-0: verifier + two re-checks to READY, then owner
approval + MIT (`ledger/lead.md` 13:46:21 -> 13:57:41); SF-1:
format-parity rule stopped a stale verification mid-flight
(14:43:57), re-verified PASS 14:53:41, owner approved 15:48:22.
Scope changes are recorded in the owner's words with the lead's
readings marked (`docs/KICKOFF.md` appended sections: SF-0/MIT,
closing decisions incl. fingerprint waiver and risk tiers; SF-2
section 9). Standing permissions were used inside their text:
pushes only by the lead under the 2026-10-26 standing word, push
confirmations by ls-remote in ledger entries; model tiers settled
in approved SF-0 10 (parcels Wonder, verifiers Spark — usage.jsonl
W0-W3 conforms: Spark rows are verifier/rechecker/auditor rows).
Adherence-by-owner-decision, said explicitly: fingerprint waiver,
strict-leaning risk-tier brief policy, public remote over the kit's
private one, accelerated calendar.

Slips / open owner items:
- SF-2: the owner approved the prefix at 05:19:07 before
  verifier-sf2 reported (05:22:45) — approval of scope from the
  studies, with the plan text verified and folded before merge
  (`889ec2e` 05:24:09), but the kit's order (verifier, then owner)
  was inverted for this plan, and the lead's approval prompt
  inverted the P1 gloss ("underflow raised" vs study R2 "no
  underflow raised"). Recorded honestly (`ledger/lead.md`
  05:19:07, 05:24:40; SF-2 5) and pinned to a second read at the
  Step 4 brief, but re-confirmation by the owner is still owed —
  the one live owner-decision risk in the project.
- Kit-zip sha256 confirmation against the builder's record is
  still outstanding from Phase 0 (`docs/KICKOFF.md:98-99`;
  `ledger/lead.md` line 118 lists it open; nothing later closes it).
- Standing rules were never confirmed line-by-line; they ride on
  the lead's marked reading of the SF-0 approval
  (`docs/KICKOFF.md:69-91,156-163`). Workable, recorded, and one
  owner pass away from settled.

### 10. Incident handling — held

Each named failure was recorded at the event with a corrective rule
that then binds later work:
- Tininess: parcel escalation 22:11:37 -> lead ruling re-derived
  by hand 22:14:34 (`ledger/lead.md` line 165, "the kernel is
  defective against the study"), fix `53acb1a` + Spark re-check
  READY (05:00:39), parcels re-gated; permanent wrong-tininess-
  polarity control in `tools/run.sh`; RECORD attributes the slip
  to the lead twice over (kernel + reference).
- Env-drop flash trap: found, root-caused by two-level probe, and
  fixed structurally in the same run (`ledger/lead.md` 2026-10-28
  02:30:28; `tools/run.sh` delegates through `"$BASH"`, flash logs
  its target unconditionally) — recorded with artifact hashes and
  the admission targeting should have landed earlier.
- Oracle defects: fenced by name with the decider moved, never
  averaged (mechanism 6: cospif, F1, RNDNA, MPFR rSqrt sign, mingw
  sqrt, Berkeley eq-ingest asymmetry ruled as ingest defect).
- Runaway script: owner-reported, lead entry same step
  (`ledger/lead.md` 2026-10-28 05:00:04), closed 05:12:22 with PID
  56188, 43.4 GB working set, twice-verified command line, RAM
  freed and verified, corrective rule (bounded intermediates +
  memory ceilings in sweep briefs). Two shape blemishes only: the
  05:00 entry carries no Measured/Believed lines, and the process
  was stopped by a sibling study agent, not its owner — both
  visible in the entries themselves.
- Smaller honesties of the same kind: the lead's false-start
  merge-tree "pass" disclosure, the Wave 2 RECORD erratum, the
  plant.py draft refused for pre-existing new text and re-anchored
  (`ledger/lead.md` 2026-10-28 02:51:41).

## Five sharpest slips, with costs

1. **Verifier-before-main inverted in Wave 1 and never universal for
   lead commits** (merges `2843792`/`06fdec8` 27 min before the
   verdicts; ~30/44 lead first-parent commits unverified before
   push; one parcel, ias15-pico `d9718cf`, with no verifier).
   Cost: the send-back loop had to run on merged trees, and
   `README.md:98-101` now states as a ground rule a gate that a
   reader can disprove from `git log` — the exact claim class the
   project exists to not make.
2. **Per-wave plant reveal against the approved once-at-end rule**
   (SF-0 5.2; 12 grading commits; key hashes uncommitted pre-dispatch).
   Cost: graded plant shapes are readable inside later verifiers'
   own copies, so the headline detection rate (61/65) cannot be
   read as shape-blind; the blinding rests on ledger + instruction,
   HF section 9's named failure shape.
3. **Metrics inputs froze at Wave 3** (passes/usage 39 rows, last
   `f458f26`; escalations/corrections likewise; ~23 W4/W5 agents
   unrowed). Cost: the hackathon's measured half cannot produce
   chain/time/token tables for its hardest waves from its own
   inputs, and RECORD's W4/W5 entries quietly dropped the figures
   W1-W3 carried.
4. **`checked_by: integration` without an integration verifier**
   (65/65 rows; merge-tree re-makes lead-run, independently re-run
   for only 6/14 merges). Cost: the one cross-check METRICS.md names
   for the plants table is the grader grading itself, under a role
   name that asserts otherwise.
5. **Claim surface left standing false at the Step 1 merge**
   (README: roundTiesToAway "deferred" the day it shipped, SF-2
   absent, 49/50 plants; SF-2 approved in scope before its
   verifier, on a prompt whose P1 gloss was inverted). Cost: the
   public first-read file contradicts the shipped tree it describes,
   and one owner approval may rest on the inverted reading until
   the Step 4 second read forces the question.

## Five fixes worth adopting before Wave 5 ends

1. **Restate README + HARNESS at the next merge, then gate them.**
   Fix the Step 1 status, SF-2, plants cumulative, the
   verifier-before-push sentence (state the real rule: parcels and
   named lead work planted-verified; wiring/record commits gated by
   `standard` + wave auditors), and `docs/HARNESS.md:23`. Add a
   claim-surface checklist line to the lead's merge script files:
   README/BOARD/RECORD diffed against the merge's own claims.
2. **Dispatch a real integration verifier once, for Waves 4-5.**
   Scope: merge-tree re-make of the 8 W4/W5 merges, `plant.py check`
   over all 13 keys reading hashes from the ledger, re-grade a
   sample of plants per wave. Until it reports, append a RECORD
   erratum restating `checked_by: integration` as lead-run checks;
   do not edit the pushed rows.
3. **Backfill the metrics before the Step 2 brief goes out.**
   One extractor pass with an explicit cutoff for all W4/W5
   agents into passes/usage (rows marked backfill in notes, as
   Wave 1's close-out did), briefs rows for the four `sf2-*`
   studies, escalations rows for the retained tier2 urgent tests,
   corrections rows from W4/W5 reports. Then `round_metrics.py
   --wave wave4` must run clean before Step 2 dispatch.
4. **Restore end-of-round reveal for the remaining Wave 5 steps.**
   Commit each key's sha256 (hash only) before dispatch; keep
   grades in lead scratch until the close; add one line to verifier
   briefs: `docs/metrics/plants.jsonl` is off-limits reading.
   Publish the full plants table once, at the close, per METRICS.md.
5. **Repair ledger + brief shape mechanically.**
   Children stage bodies in scratch; only `tools/ledger.sh append`
   writes the ledger, with one provenance line per staged entry.
   Add a stamped provenance entry to each of the 12 unstamped files
   (recording their mtimes — no forged stamps). Diff every W5 brief
   against `ledger/briefs/w1-f32.md` for the dropped items:
   scope ceiling, brief-got-wrong line, READY definition, test
   escalation. Ask the owner two one-line questions in the same
   step: confirm SF-2 pin P1 as R2 (no underflow raised), and
   confirm the kit-zip sha256 — both already written down as owed.

## Not audited (sampling boundaries)

- Kit depth: case studies (honest CASE-STUDY, parcelround
  CASE-STUDY-1..6), examples/cases 01-20, ADOPTING/ADOPTION/
  FAILURE-MODES bodies, archived round ledgers, and the QRO-Crate
  bundle were read only through the kit's own citations, not whole;
  template files beyond their rule-bearing heads likewise. Grades
  rest on the two METHOD.md texts, the kit top level, templates'
  stated contents, and tool-contract docstrings as listed above.
- Numerical correctness: no gate was re-run (read-only brief).
  Verifier/parcel counts are taken as reported evidence; the only
  re-derivations are the counts in the audit scripts (git history,
  JSONL sets, coverage columns, key-hash set equality, copy shape
  on 4/13 copies, numstat append-only proof).
- `plant.py check` was not executed by this audit (it would need
  key contents); dispatch/reveal PASS claims rest on lead ledger
  entries + `scratch/lead/check_plants_*.sh` script names, and
  auditor-final's merge-tree re-runs were not repeated.
- Transcripts/session logs were not opened; usage extraction was
  not re-derived (rows' internal consistency only). Board hardware
  was not run; board claims rest on ledger/RECORD/log citations.
- SF-1 was sampled (headings, deferred/claim counts), not read
  whole; SF-0 sections sampled as cited. Scratch report bodies:
  full reads for the three prior audits; first-line/verdict
  inventory for the remaining ~55 report trees, with spot reads
  (verifier-w4trig ledger, parcel-w4trig design entry).
- Push history beyond `origin/main` == local main at freeze was
  not independently queried from the remote host; per-push timing
  rests on ls-remote lines inside ledger entries.
- Waves are graded as one round to Wave 5 Step 1; anything landing
  after `7c3819c` (2026-10-28 06:17:43 -0700) is outside this audit.

