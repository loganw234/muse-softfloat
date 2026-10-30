# SF-0 approval audit — MIT licence choice (2026-10-26)

Scope: read-only audit. No files edited. Commit referenced: 828b8f13e63351ecdce5ca94a0550b4545a35160 (SF-0 pushed to origin/main).
Inspected: `muse-softfloat/docs/studies/SF-0.md` (esp. 0, 4.5, 11, 12, 14), `muse-softfloat/README.md`, `muse-softfloat/docs/KICKOFF.md`, `muse-softfloat/docs/RECORD.md`, `muse-softfloat/AGENTS.md`.
Clean-room rule observed: nothing with `cft` in its name was opened, searched, or listed.

## 1. Every place that says the licence is undecided/recommended and must be restated

1. `muse-softfloat/docs/studies/SF-0.md:3-4` — Status line: "Status: **draft for independent verification, then owner approval. No P0 work starts on this document until Logan approves it.**" Must become an approved status with date (see §4).
2. `muse-softfloat/docs/studies/SF-0.md:34-35` — "The lead's proposals. Each is argued in the section named; Logan approves or corrects them at the end of this study (Section 12)." Spent once approved; Section 14's dated approval note supersedes it.
3. `muse-softfloat/docs/studies/SF-0.md:71-78` (Section 0, item 8) — "The library's own licence is Logan's decision (recommendation in Q12.8)". Must read MIT (owner's 2026-10-26 decision).
4. `muse-softfloat/docs/studies/SF-0.md:736-749` (Section 12, Q12.8) — "8. **Library licence:** choose the library's licence (recommend a permissive licence — MIT or BSD-3-Clause — to keep the library cleanly separable from the GPL workload); and confirm the standing-rule/cap defaults … The kit-zip builder hash … and any clean-room fencing beyond rule+disclosure+audit can be settled in the same reply." Must record the decision: MIT chosen; plus whatever was decided on rules/caps, hash, fencing in the same reply.
5. `muse-softfloat/docs/studies/SF-0.md:781-782` (Section 14) — "until the owner approves; after approval this file is restated only by a new dated section, never silently." Approval must be a new dated Section 14 entry, not a silent edit.
6. `muse-softfloat/docs/studies/SF-0.md:801-806` (Section 14, Draft 2 notes) — "its remaining open items are the licence/timing decision in Q12.8 and the SDK-level benchmark baseline, whose production P0 item 9 now tasks." Licence half is closed by this approval; benchmark baseline stays a P0 production task.
7. `muse-softfloat/README.md:56-60` — "## Licence / Not set yet — the owner's decision, recorded in `docs/KICKOFF.md` when made. Third-party code keeps its own licence; REBOUND is GPL …" Must become the MIT statement (see §2).
8. `muse-softfloat/docs/KICKOFF.md:127-132` (Open question 3) — "…pico-sdk/toolchain pins, the library's licence, copy-vs-read per third-party source; the authority and oracles." Must record the answer (MIT) without editing history — KICKOFF is append-only to past beliefs (KICKOFF.md:5-7, owner rule 10 working default).
9. `muse-softfloat/AGENTS.md` — no licensing mention found (full file read; only licence-adjacent line is AGENTS.md:16, the IEEE PDF custody rule). No restatement needed there, but P0 item 1 (SF-0.md:538-540) requires AGENTS.md's authority/discipline paragraph to be filled from SF-0 Sections 4-5 — that fill-in should carry the decided licence by reference, not invent new wording.

## 2. LICENSE file placement and copyright wording (solo owner, 2026)

- Placement: new file `muse-softfloat/LICENSE` at the repository root (alongside README.md/AGENTS.md). No LICENSE file exists today (verified: repo root holds only `.gitattributes`, `.gitignore`, `AGENTS.md`, `README.md`, `docs/`, `tools/`).
- Content: the standard MIT licence text (Copyright line + permission grant + warranty disclaimer), unmodified apart from the copyright line.
- Recommended copyright line: `Copyright (c) 2026 Logan <surname?>` — **uncertainty flagged**: the owner's legal/full name is not stated in any inspected file (only the GitHub account `loganW234`, the given name Logan, and the identity `gh` is logged in under). Do NOT guess the surname; confirm the exact holder string before writing the file. Year 2026 is certain (project dates throughout).
- Do not use `LICENSE-MIT` or a second COPYING file unless a later GPL workload file needs disambiguation; a single root `LICENSE` keeps tooling (GitHub licence detection) working. Optional: add `SPDX-License-Identifier: MIT` to the generated header later in P0 — SF-0 does not require it, so flag as optional.
- Companion restatement: README.md:56-60 becomes e.g. "Licence: MIT — see LICENSE. Third-party code keeps its own licence; REBOUND remains a separately-licensed GPL-3.0-or-later demo workload, never inside the library." Exact sentence is the lead's; the normative file is LICENSE.

## 3. MIT vs no-copy policy vs GPL REBOUND — no conflict

- The no-copy rule is policy-stronger than licensing: SF-0.md:300-305 — "No third-party softfloat source in the library tree: Berkeley SoftFloat is legally copyable (BSD-3) and is refused anyway as project policy … libgcc soft-fp source is refused on licence; compiler-rt is a read-only design reference at most" — plus SF-0.md:529-530 refusals ("copying third-party softfloat source (Section 4.5)") and SF-0.md:736-738 (Q12.6, recommend yes). MIT does not weaken this: the rule refuses even licence-permitted copying.
- The GPL boundary is structural, not licence-mixing: SF-0.md:474-478 — "REBOUND is GPL-3.0-or-later: the extracted workload is a separate program that links the library through its public/wrapper interface, carries its own licence notices, and no REBOUND code or tables enter the library tree" — with Section 9 detail at SF-0.md:657-676 (pin 5.2.2@262a9cc; hex bit patterns carried, decimal literals converted via MPFR). README.md:59-60 and KICKOFF.md:63-64 say the same ("never inside the library"). Linking a GPL program against an MIT library through its public interface with no GPL code entering the tree is the standard compliant shape; MIT's permissiveness is what keeps the library "cleanly separable from the GPL workload" (SF-0.md:742-744).
- Oracle/fetch hygiene is orthogonal: SF-0.md:466-474 (read/execute allowed, copy into `src/`/`include/` refused; fetched trees live in scratch with hash records). MIT changes nothing there.

## 4. Where the approval itself must be recorded

1. SF-0 status line (SF-0.md:3-4) → approved form with date (2026-10-26) and the nine-question disposition.
2. Section 14 (per SF-0.md:781-782): new dated entry (Draft 4 / approval entry) recording MIT + any Q12 rulings corrected individually; never silent edits to earlier drafts.
3. Section 12 Q12.8 (SF-0.md:742-749): decision recorded (MIT; plus standing-rule/cap confirmation, hash, fencing — whatever the reply settled).
4. KICKOFF.md open question 3 (KICKOFF.md:127-132): answer appended, not edited in place (KICKOFF.md:5-7).
5. RECORD.md: new dated entry (next wave entry) quoting the owner's approval words verbatim beside the lead's readings, per the Wave 0 skeleton (SF-0.md:689-696).
6. Ledger (outside this repo): approval verdict/decision entry with stamps — SF-0.md:702-704 requires commit bodies to name the ledger files and entry stamps to open first.
7. README status (README.md:16-24) + AGENTS.md discipline paragraph (AGENTS.md:74-76): P0 item 1 (SF-0.md:538-540) links the approved SF-0 from README and fills AGENTS.md from Sections 4-5 — the natural moment to propagate the MIT statement.

## 5. What still blocks P0 after the licence choice

Licence no longer blocks anything, but these SF-0/P0 items remain open per the inspected files:

1. The other eight Q12 questions are only approved if the owner approved SF-0 whole or ruled each (Q12.1-7, Q12.9 at SF-0.md:721-759) — licence alone does not approve edition, binary16 posture, Tier 2 order, state model, authority order, copy policy, IAS15 definition, or the Q12.9 package.
2. Standing rules/caps/model tiers (KICKOFF.md:69-91) still read "proposed, not yet settled line by line" — Q12.8 bundles their confirmation with the licence reply; if the reply did not confirm them, they stay defaults, not decisions.
3. Kit-zip hash confirmation (KICKOFF.md:98-99: "owner to confirm … still outstanding") and clean-room fencing beyond rule+disclosure+audit (KICKOFF.md:111-115, 124) — Q12.8 allows settling them "in the same reply"; unsettled = still open.
4. IAS15 strict-flags definition (KICKOFF.md:133-135, Q12.7 SF-0.md:739-741): the meaning of "unmodified" still needs the owner's yes.
5. Board serial channel unproven (SF-0.md:565-574): establishing CDC is itself P0 scope and risk — the top technical P0 risk, unrelated to licensing.
6. SDK-level benchmark baseline production (Section 14 note, SF-0.md:803-805; P0 item 9, SF-0.md:582-585): tasked to P0, not yet produced.
7. Oracle bring-up costing (P0 item 5, SF-0.md:553-561): Berkeley coverage verification and measured vector budgets still to run.

## 6. What this brief got wrong

- It says "SF-0 is at … commit 828b8f13 … pushed to origin/main" — verified only that the file exists in the working tree with the cited content; no git commands were run (per the no-git-writes constraint), so the commit hash and push state are unconfirmed from this audit.
- "chosen MIT for the library licence" is taken on trust from the brief; no owner statement was inspected (ledger and session transcripts are outside the permitted file set), so the decision's provenance is unconfirmed — the record entries in §4 should quote the owner's actual words.
- "Section 14" approval mechanics: Section 14's rule (SF-0.md:781-782) sends approval to a new dated section, but the brief's item (4) also lists "Section 12/14" as recording places — Section 12 itself should not be rewritten; the decision is recorded against Q12.8 via the Section 14 entry.
- Minor: the brief implies AGENTS.md may mention licensing — it does not (full file read).
