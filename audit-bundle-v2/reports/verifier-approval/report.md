# verifier-approval on 0bfa964 — report (2026-10-26)

Stance: disconfirm only. Nothing in project files changed by this verifier.
Target: `0bfa9642ace34495f085eaa5a4d1b42c5aa81513`
("Recorded SF-0 approval and the MIT licence"), parent `828b8f1`
(pushed, READY-verified SF-0). Scope: `828b8f1..0bfa964` read whole
(5 files, 115+/17-). Clean-room rule observed: nothing with `cft` in
its name opened, searched, or listed. No background work started;
none to stop. `scratch/lead/` and other agents' scratch never read
(only `scratch/approval-audit/report.md`, as briefed).

## Commands run (actual outputs)

1. `git log --oneline -8` in muse-softfloat/:
   `0bfa964 Recorded SF-0 approval and the MIT licence` on top of
   `828b8f1 Drafted SF-0...`, `2bac8e9 ...`, `dfc7a02 ...`.
2. `git show -s --format=%B 0bfa964` — full message captured (see §4).
   Trailer present: `Co-Authored-By: Muse Code (muse-wonder-full-1.0)
   <noreply@meta.ai>`. Author/committer on all 4 commits:
   `Logan <Logan@improperaperture.com>` (consistent).
3. `git diff --stat 828b8f1..0bfa964`: LICENSE 21+, README 24,
   KICKOFF 20+, RECORD 37+, SF-0 30. `git diff` read whole (all hunks,
   §2-§5). `git status --short`: clean. `git diff --name-only`: exactly
   the 5 intended files.
4. `git rev-parse 33c59f9 4f7f870 828b8f1 0bfa964` — all four resolve to
   full SHAs matching the ledger/RECORD claims. `git show-ref`:
   `refs/heads/main = 0bfa964` (local), `refs/remotes/origin/main =
   828b8f1` — parent was pushed before approval; target not yet pushed.
5. `probe_license.py` (scratch/verifier-approval/): worktree LICENSE =
   1065 bytes, CR 0, LF 21, single trailing newline, sha256
   `c28b530f...f2f7ce`; byte-exact equal to canonical MIT text with
   `Copyright (c) 2026 Logan W.` substituted (True, no diff lines).
   `git cat-file -p 0bfa964:LICENSE` == worktree bytes (True; an early
   `od` showing CRLF was PowerShell pipe mangling, disproved by the
   byte-exact subprocess comparison).
6. `probe_files.py`: LICENSE/README/KICKOFF/RECORD/SF-0 all CR 0, zero
   trailing-whitespace lines, all end in newline.
7. Regex sweep over muse-softfloat/ for licence/MIT/GPL/BSD/Copyright
   plus home-path/secret/staleness terms: hits only the expected
   licence statements (§1), pre-existing KICKOFF:103 sandbox-token
   wording (states no valid token — not a secret), BOARD Debug-Probe
   open question, and metrics token-count fields. No `C:/Users` home
   path, no secret, no `Not set yet` / `owner confirmation pending` /
   `(to come)` / `owner's decision` remnant in any touched file.
8. Read in full: ledger/lead.md 13:57:41 entry, ledger/verifier-sf0.md,
   ledger/rechecker-sf0.md, ledger/rechecker2-sf0.md,
   scratch/approval-audit/report.md (whole), KICKOFF appendix + Q1-Q4,
   RECORD new entry, SF-0 status/Section 0 item 8/Q12.8/Section 14,
   README whole, AGENTS.md whole.

## (1) LICENSE and licence-consistency — PASS

- Canonical MIT apart from holder/year line: verified byte-exact (§5).
  Holder exactly `Logan W.`, year 2026, LF endings, at repo root
  (muse-softfloat/LICENSE, the project repo's root). No second
  LICENSE/COPYING file; no other file claims a different library
  licence.
- Q12.8 and SF-0 4.5 keep recommendation/refusal wording as put — this
  is per the audit's own prescription (audit §6: "Section 12 itself
  should not be rewritten; the decision is recorded against Q12.8 via
  the Section 14 entry"), and the new Section 14 entry says so
  explicitly ("Section 12's questions stay as put"). Status line,
  Section 0 item 8, Section 14, KICKOFF appendix, RECORD entry, README
  licence section, and LICENSE all agree on MIT. Disposition is
  unambiguous.
- SF-0 line 805-806 ("remaining open items are the licence/timing
  decision in Q12.8...") is dated Draft-2 pass history, directly
  superseded by the Approval entry below it in the same section — not a
  false sentence standing.
- Note (not a finding): README says "REBOUND is GPL" where SF-0 says
  "GPL-3.0-or-later"; this imprecision predates the diff, and README
  also says "separately-licensed", so the boundary claim holds.

## (2) Approval accounting — PASS

- Owner words verbatim against ledger/lead.md 13:57:41: "Everything
  looks good with the recommendations, go with MIT for the license."
  and "Logan W. works fine" — quoted identically in SF-0 Section 14,
  KICKOFF appendix (blockquotes), RECORD entry, and the commit message
  (punctuation: SF-0 places the second quote's period inside the marks;
  KICKOFF/RECORD keep it outside/absent — substance identical, see note
  N3).
- Stamps/hashes/counts true: ledger stamps 13:16:25 (verifier-sf0 (b) 6,
  15 notes), 13:31:36 (rechecker-sf0 (b) 2, 4 notes), 13:43:09
  (rechecker2-sf0 (b) 0, 1 note), 13:57:41 (approval), 12:06:41 (Wave 0)
  all exist with matching counts; draft SHAs 33c59f9/4f7f870/828b8f1
  all resolve; RECORD chain row reproduces every count and the study
  cap (3 drafts + 2 re-checks); "all muse-spark-1.3" corroborated by
  lead.md dispatch decisions (12:26:47, 13:22:43, 13:35:27, 13:46:21).
- Lead reading marked as the lead's everywhere it extends the words:
  SF-0 ("The lead reads..."), KICKOFF ("Lead reading (marked)"),
  RECORD ("The lead's reading, beside it"), commit message ("The lead
  reading (open to correction)"), ledger 13:57:41 ("Lead reading
  (marked)").
- Open items neither settled nor dropped: kit-zip builder-hash
  confirmation, extra clean-room fencing, Debug Probe presence are named
  as still open in SF-0 Section 14, KICKOFF appendix (mapped to the
  correct Q numbers: Q1 zip+fencing, Q4 probe — verified against
  KICKOFF:124/133-135), RECORD entry, and the commit message. IAS15
  strict-flags definition is claimed approved only as part of the
  whole-study approval, marked as reading — consistent on all surfaces.

## (3) No approved-study substance changed — PASS

- Every SF-0 hunk is approval recording: status line, Section 0 intro
  ("approved by Logan... Section 14 records the approval"), item 8
  (licence MIT + pointer to LICENSE), new Section 14 Approval entry.
  No proposal, number, pin, or gate edited. Earlier Section 14
  pass-history paragraphs untouched.
- README/KICKOFF/RECORD changes say the same thing five ways (MIT,
  holder, nine-question approval reading, three named open items, P0
  may begin) with no mutual contradiction.
- Standing rules honored: detailed commit body (what occurred, lead
  reading, verification, ledger stamps to open first) per 10:38 rule;
  Co-Authored-By trailer names the committing model per 10:49 rule;
  push gated on this verdict per the verifier-before-main-moves gate
  under standing permission (10:48) — correctly not yet pushed.

## (4) Commit message vs reality — PASS

- "READY-verified by rechecker2-sf0 after two send-backs, and pushed
  before approval": true (NOT READY 0,6 → NOT READY 0,2 → READY 0,0;
  origin/main = 828b8f1).
- "Independent read-only approval audit confirmed MIT/no-copy/GPL
  consistency and named the surfaces": true of report content (§1
  surfaces, §3 no-conflict); read-only true (that scratch dir holds
  only report.md; repo files untouched by it). The "(Spark)" model
  tag is uncorroborated in inspectable evidence (report names no model,
  no ledger entry exists) but contradicted by nothing — note N2.
- "Its one certainty gap (the exact holder string) is what Logan just
  closed": true (audit §2 flags exactly this; "Logan W." arrived after
  — consistent with the audit file mtime predating the 13:57:41 ledger
  entry, since the audit ran on the briefed MIT choice without owner
  words, as its §6 admits).
- No hashes miscounted, no verification order mis-stated, no audit
  finding misclaimed.

## (5) Anything else in the diff — PASS

- Home paths: none new. Secrets: none (KICKOFF:103 states the sandbox
  holds no valid token — pre-existing, not a disclosure). Line endings:
  all five files pure LF, no trailing whitespace. Unintended files:
  none (exactly the 5 intended paths; tree clean).

## Findings

- (a) regressions: 0. (b) wrong answers: 0.
- N1 (note): AGENTS.md "The authority — Not named yet" and "SF-0 writes
  this paragraph. Placeholder" now read stale beside approved SF-0, but
  the audit deferred that fill to P0 item 1 — correctly not this
  commit's job.
- N2 (note): commit message's "(Spark)" tag on the approval audit has
  no inspectable provenance (no model self-identification, no ledger
  entry). Uncontradicted; suggest the lead record the audit's model in
  the push/close entry if known.
- N3 (note): SF-0's `"Logan W. works fine."` puts sentence punctuation
  inside the closing quote where the ledger/KICKOFF/RECORD keep the
  owner's string bare. Verbatim substance unaffected; no action needed.

## Verdict: READY — push gate open

Ledger: sandbox has no bash (`bash` spawn Access-denied, probe §8), so
no `ledger.sh` append was made and no ledger file was hand-written. The
ready ledger body is staged at scratch/verifier-approval/ledger-body.md
for the lead to append. Report path:
scratch/verifier-approval/report.md. Probes:
scratch/verifier-approval/probe_license.py,
scratch/verifier-approval/probe_files.py.

Not done: reading any other scratch besides approval-audit (per brief);
running the kit gate or test suites (nothing executable changed);
network/remote checks beyond local refs; touching project files.
