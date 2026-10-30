# verifier-wave0 report — Wave 0 RECORD entry (4805d2e), disconfirm-only

Verifier: verifier-wave0, model muse-spark-1.3. Target: commit
4805d2e5ec8f1ca23ce7a0ced67744672564eb46 in muse-softfloat/ (docs/RECORD.md,
the Wave 0 entry; parent dfc7a02 pushed, this commit not). Method: view formed
from the commit first (`git show 4805d2e`), then checked against reachable
evidence only. No fixes made. No background work started or left running.

## Verdict: NOT READY — (a) 0, (b) 2, notes 6

Both (b)s are small restatements in place before push (rule 10; entry
unpushed, so in-place restatement is allowed): one wrong time-of-day word, and
one provenance head ("by the commands named in the ledger") covering two
figures no reachable ledger file names. Details in findings F1, F2.

## Commands run and actual outputs

1. `git -c safe.directory=... -C muse-softfloat show 4805d2e...` — full diff
   read first. Single-file commit: `docs/RECORD.md | 126 ++++...`, 126
   insertions, no other file touched. Trailer present:
   `Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>`.
2. `git ... show --stat 4805d2e` — confirms: 1 file changed, 126 insertions.
3. `git ... log --format='%H %ad %cd %s' --date=iso 4805d2e -1` — author and
   committer both `2026-10-26 11:02:51 -0700` (morning, not afternoon).
4. `git ... rev-parse 'dfc7a02^{tree}' '31e464e^{tree}'` — both print
   `dacbd5cdf5c249c4947047acdb5e7e847dd910d2`. Tree-identical, as claimed.
5. `git ... show -s --format=%B dfc7a02` vs `31e464e` — messages identical
   except dfc7a02 adds the Co-Authored-By trailer. Message-only amend holds.
6. `git ... ls-tree -r --name-only dfc7a02` — 7 files: .gitattributes,
   .gitignore, AGENTS.md, README.md, docs/BOARD.md, docs/HARNESS.md,
   docs/KICKOFF.md. "7 files at dfc7a02" holds.
7. `git ... grep -n -i -E "42|h264|encode|ffmpeg|ninja" dfc7a02` — hits only
   AGENTS/KICKOFF lines about ninja/ffmpeg installs (venv + system 9.0.2).
   No exit-42, no h264/encode anywhere in the pushed tree.
8. Ledger searches (literal): `h264` in ledger/ → no matches; `encode` in
   ledger/ → no matches; `exit 42` in ledger/lead.md, verifier-phase0.md,
   rechecker-phase0.md, rechecker2-phase0.md, README.md → no matches.
   Control search `picotool` in ledger/lead.md → hit, so the tool was working.
9. `cat ledger/urgent/test-escalation-channel-test.md` — headline
   "Escalation channel test", `For: lead`, `Written: 2026-10-26 10:12:05 -0700`,
   matching ledger/test-escalation.md stamp to the second.
10. Reads (full): ledger/verifier-phase0.md, rechecker-phase0.md,
    rechecker2-phase0.md, test-escalation.md, S1.md, S2.md, S3.md, S4.md,
    lead.md (all entries), ledger/README.md (to line 119), KICKOFF.md (full).
11. Scratch reads: S1/report.md (head + searched sections), S2/report.md
    (headlines + §§1.1–1.4), S3/report.md (§§1.1–1.5, §2.2, §7 checks),
    S4/report.md (§§0–1.3, §3.1, libm table, §§5–7 spot checks).
    Listings: S1..S4 dirs each hold report.md plus probes/scripts;
    reading-scratch holds distill-examples/honest/parcelround-cases/
    qro-round6 (.md x4) and qro/ clone; S4/rebound search hits were
    incidental upstream-notebook text, not surveyor claims.
12. NOT run: no kit gate re-run, no builds, no probes, no network fetches, no
    board reads, no session-transcript reads, no git config changes (sandboxed
    git refused without safe.directory; used `-c safe.directory=` per call).

## Per-item verdicts (RECORD Wave-0 entry, in order)

- Preamble (marks, round_metrics/JSONL, restate-in-place rule): descriptive of
  the record's own conventions. No figure carried. HOLD.
- Owner-quotes paragraph: standing-permission quote matches ledger/lead.md
  10:48:17 verbatim (three sentences; the model-choice sentences are quoted
  separately below, no misquote). Co-Authored quote matches lead.md 10:49:40
  verbatim incl. leading asterisk. KICKOFF summary (public remote, unsandboxed
  installs, IAS15 workload, Wave 1 by tonight, begin-Phase-0) matches KICKOFF
  lines 26–29. 2026-10-23 attribution matches KICKOFF's kit-date line. HOLD.
- Lead-readings paragraph (rule 7 standing, trailer rule, muse-spark-1.3
  verifiers): matches lead.md 10:48:17, 10:49:40, 10:54:45 readings. The
  commit's own trailer names muse-wonder-full-1.0, consistent. HOLD.
- Chain table: verifier-phase0 "0, 3" matches its entry (three (b)s: remote
  spelling, README link, home-paths-in-two-files as one item); rechecker
  "0, 1" matches (one new (b), the README clause); rechecker2 "0, 0
  (scoped)" matches (no (a)/(b) in its 4-check scope). "Sent back twice,
  restated each time" matches lead.md 10:27:25 + 10:36:17. dfc7a02/31e464e
  tree equality + message-only amend verified by command (items 4–5 above).
  "verifier-wave0 ... no (at writing)" is true at writing. HOLD.
- Built paragraph (7 files; ledger/scratch layout; venv package list +
  ninja 1.13.2 beside system Ninja/FFmpeg): matches ls-tree output, KICKOFF
  lines 41/101/117–118, lead.md 10:09:37. HOLD.
- Measured paragraph, item by item:
  - kit gate PASS-via-Bash / REFUSES-from-sandboxed-PowerShell: matches
    lead.md, KICKOFF lines 95–96, and verifier-phase0's independent
    re-confirmation. HOLD.
  - plant.py selftest FAIL at :650 vs make/check PASS on scratch repo:
    matches KICKOFF lines 106–108, lead.md. HOLD.
  - arm + host compiles + host run: compiles match lead.md/KICKOFF/verifier
    probes; the elaboration "(exit 42 by construction)" names a figure with
    no reachable source — see finding F2. FAIL (provenance, not the run).
  - "a 1-second h264 test encode": no reachable source — see F2. FAIL.
  - RP2040 rev B2 answering picotool 2.3.1: matches KICKOFF line 101,
    lead.md. HOLD.
  - escalation file + ledger entry agreeing to the second: matches urgent
    file `Written:` line and ledger stamp 2026-10-26 10:12:05 -0700, lead.md
    10:13:40 read-both verification. HOLD.
  - model probe (no model param on native spawn; Workflow muse-spark-1.3
    child self-ID "Muse Spark" probe-ok; follow-ups tool-less 4 of 4):
    matches lead.md 10:54:45 and 10:12:37. HOLD.
- Survey S1 bullet: FMA required single-rounding (report §1.2 lines 124–126:
  "FMA is required, not optional ... single-rounding"); no required min/max
  (report §1.1 line 115: none required in Clause 5, 9.6 recommended only);
  four binary rounding attributes, ties-to-away attribute decimal-only
  (report lines 239–242) with ties-to-away *operation* required (lines
  94–98); decimal conversions H>=20 for the 16+32+64 combo (report lines
  171–172, marked BELIEVED there — see note N6); binary16 not basic, and as
  arithmetic pulls in all of Clause 5 (report §§0–1, READ 5.1); interchange-
  only binary16 still owes correctly rounded flag-correct conversions
  (report §6 lines 480–482, BELIEVED summary); NaN payload should, canonical
  quiet NaN shall (report lines 344–358); Clause 8 not required of an
  implementation (report §4 lines 370–373). HOLD (N6 noted).
- Survey S2 bullet: 3e frozen 2018-01-20 both packages, BSD-3 (report §§1.1–
  1.2 READ with dates and licence text); archive-pin-by-hash, master drifted
  (report lines 65–75; "never master" slightly stronger than the report's
  "or a named commit" — note N3); default gcc i686 x87 FLT_EVAL_METHOD=2,
  bogus oracle until mingw64-first PATH fix (report headline 2 + §probes);
  MPFR 4.2.2 installed, links+runs (report headline 3); supplements: report
  headline 4 names THREE (IBM Haifa FPgen vectors, exhaustive
  binary16/binary32-unary sweeps, MPFR-directed binary64 randoms) while
  RECORD names only the latter two — note N1 (omission, not falsehood).
  HOLD with N1, N3.
- Survey S3 bullet: --wrap into SDK, partial ROM tail-call (report §§1.1–1.3
  tiers A/B/C); compares + 32-bit int conversions SDK asm (report §1.3 Tier
  B lines 116–140, with the f2uiz/d2uiz-to-ROM nuance faithfully inside the
  report); SCI_EXTRA SDK C with fmaf double-rounding comment
  (float_math.c:334-338) and unfused fma (double_math.c:348) (report lines
  147–157); ROM denormal/NaN treatment + RN-even-only + no traps/flags
  (report §2.2 lines 350–375, datasheet quotes); default build does not
  propagate NaNs (report lines 186–195); "in its fast paths" qualifier is
  not in the source (datasheet states it generally) — note N2; closing
  "reason to exist / yardstick SF-0 prices against" is lead framing of a
  future study, not a measured fact — acceptable as flagged intent, HOLD.
- Survey S4 bullet: REBOUND 262a9cc v5.2.2 GPL-3.0-or-later (report §0 lines
  13–21, MEASURED git log); no pow (report §3.1 lines 354+770–774), no
  trig/exp/log in step path (report lines 210–212); libm surface = sqrt
  (correctly rounded) + fabs/copysign/isnormal (exact) + +-*/ (report lines
  657–659: RECORD's wording tracks this sentence); tables carry far more
  digits than a double holds, pin conversion or carry hex (report lines
  96–101); evaluation order part of numerics (report lines 102–111). The
  bullet omits the sqrt7 Newton helper the ledger headline and report §3
  name (the surface claim stays true — sqrt7 is built from those ops) —
  note N4. HOLD with N4.
- Slips paragraph: five counted (b)s = verifier's 3 (spelling, link, home
  paths in two files) + first-restatement slip (lead.md 10:27:25) +
  second-restatement (b) (rechecker-phase0, lead.md 10:36:17); author-date
  predating verdicts was classed note (not (b)) by both verifiers and is
  listed separately with "(reset)" — matches rechecker2 dates
  10:35:56 vs verdict stamps 10:34:41/10:24:16. "Parcels so far: none" is
  true of the wave state (no parcel verdicts exist). HOLD.
- Time/tokens paragraph: explicitly "not yet measured", no figure carried,
  JSONL/extractor gap named as P0 — a stated limit, honest. First-entry
  stamp 2026-10-26 10:09 -0700 matches lead.md 10:09:37. "this entry the
  same afternoon" is FALSE — see finding F1. FAIL (one word).
- Known-limits paragraph: no single verifier passed 31e464e whole /
  push-readiness rests on chained scoped verdicts — matches rechecker2's
  own stated limits; Monitor watcher unwatched-to-work with PowerShell-form
  arming — matches S1 ledger entry; token accounting absent — matches prior
  paragraph; clean-room no mechanical fence — matches lead.md/KICKOFF
  posture ("owner's fingerprint audit" wording beyond KICKOFF's "owner's
  audit" — note N5); plant.py CRLF limit — matches KICKOFF. HOLD with N5.
- Records paragraph: distill-*.md x4 present; S1..S4 report.md + probes
  present beside them; verifier verdicts in ledger files; qro/ clone
  present; "none of that scratch is in this repository" holds (commit adds
  only docs/RECORD.md). HOLD.

## Findings

F1 — (b) wrong answer. "Ledger stamps bound the wave: first entry
2026-10-26 10:09 -0700, this entry the same afternoon." The Wave 0 entry was
committed 2026-10-26 11:02:51 -0700 (author and committer dates identical,
per `git log --date=iso`). In -0700 that is morning. Fix: "the same morning"
(or "late morning"). One word, restatable in place before push.

F2 — (b) wrong answer (provenance). "Measured, by the commands named in the
ledger: ... arm and host compiles + host run (exit 42 by construction); a
1-second h264 test encode; ..." Reachable ledger files (lead.md,
verifier-phase0.md, rechecker-phase0.md, rechecker2-phase0.md,
test-escalation.md, S1–S4.md, README.md to §Entry-format) name no exit-42
run command and no h264/encode command at all (literal searches for `exit
42`, `h264`, `encode` return nothing; the pushed tree likewise contains
neither). The compiles themselves are multiply attested; the runs may well
have happened in the lead's own scratch, which I am barred from reading —
so this is disconfirmed provenance, not a disconfirmed run. Fix, either: (i)
quote the actual commands into the ledger and keep the figures, or (ii)
reword to mark the two figures lead-measured-with-source-TBD / drop them per
the entry's own "says so rather than carrying a number" rule.

N1 — note (omission, not false). S2 bullet drops the first of the report's
three named supplements (IBM Haifa FPgen IEEE-754R vectors). Suggest adding
it so the headline matches S2 report headline 4 exactly.

N2 — note (un-sourced qualifier). "treats input denormals as zero and NaNs
as infinities in its fast paths": S3 §2.2 quotes the datasheet stating this
generally, with no "fast" scope. Suggest dropping "in its fast paths" (the
deprecated FCMP_FAST slots are a different, unused thing — report lines
120–125).

N3 — note (strength). "never `master`" vs S2 report "Pin the jhauser.us 3e
archive (or a named commit)": the report permits a pinned named commit.
Suggest "never track `master`" to match.

N4 — note (omission, not false). S4 bullet omits the sqrt7 Newton 7th-root
helper named in the S4 ledger headline and report §3. The stated library
surface stays true (sqrt7 is built from those ops), but naming it would
match the survey: the step needs sqrt7-from-+-*/.

N5 — note (unresolved wording). "owner's fingerprint audit": KICKOFF's text
says "owner's audit"; "fingerprint" appears in neither KICKOFF nor the
ledger files I read (likely kit-docs wording, outside my evidence list).
Unresolved, trivial.

N6 — note (tag drop). H>=20 is a BELIEVED consequence in S1 (for the
16+32+64 combo), stated flat in RECORD. Fine as a headline; no action needed
beyond awareness.

## What I did not do (explicit)

- Read nothing with `cft` in its name: never opened, searched, or listed
  any such path, on disk or web. (Incidental: an S4 upstream-notebook blob
  matched a `ffmpeg` search; it is third-party REBOUND text, not a landing.)
- Never read scratch/lead/ or any agent scratch besides S1–S4, my own
  scratch/verifier-wave0/, and the authorized listings.
- Never changed git config (sandboxed git refused without safe.directory;
  used `-c safe.directory=` per invocation, read-only commands only).
- Formed my view from `git show 4805d2e` before opening any ledger file.
- Ran no builds, probes, kit gates, or network fetches; re-ran nothing.
  Dates checked for internal consistency only (commit object vs entry words),
  not against an external clock. Owner-quote wording checked against
  ledger/lead.md and KICKOFF.md only (no session transcripts).
- Spawned nothing; no background work started or left running.
- Did not read kit PROJECT.md/OWNER.md (origin of "fingerprint audit"
  phrasing unresolved — note N5).
