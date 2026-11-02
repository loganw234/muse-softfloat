# verifier-extractor report — commit 8770745 (Wave 0 transcript-measured metrics)

Verifier: verifier-extractor, model muse-spark-1.3. Target: commit
877074575a02aefc9dfaada5079931d8ed99381c in muse-softfloat/
(docs/RECORD.md, docs/metrics/passes.jsonl + usage.jsonl,
tools/extract_session_metrics.py). Parent dfc7a02 pushed, this commit not.
Method: view formed from `git show 8770745` / files at HEAD first (HEAD is
8770745, tree clean), then checked against ledger/verifier-wave0.md,
scratch/verifier-wave0/report.md, ledger phase-0 verdict files, ledger/lead.md
11:37:23 entry, AGENTS.md/KICKOFF.md. No fixes, no spawns, no cft paths
touched, no background work left running. TMPDIR pointed into my scratch.

## Verdict: READY — (a) 0, (b) 0, notes 7

No wrong figure and no false sentence found in the commit. All 7 notes are
script-robustness observations or phrasing approximations; none changes a
committed number. Details in N1–N7.

## 1) The script as code (read whole, 434 lines)

Counting rules verified against the implementation:

- Token source: only `payload.event.kind == "model_completed"` records
  contribute usage (lines 160–174). Other records (goal attribution etc.)
  are skipped. HOLDS.
- Dedup: key is `(recorded_at, model, duration_ms)` + all six usage fields
  (line 165); exact duplicate counted once. Selftest's dup check passes and
  the fixture's dup differs in nothing, so the check is real. HOLDS. Note
  N1 (key could merge two genuinely distinct completions sharing
  ts+model+duration+all six usage ints; no instance seen — my three
  independent recounts found 0 dups).
- Tool ids: distinct `call_id or id` from
  `assistant_tool_calls_committed` (lines 156–159). Selftest fixture has
  a,a,b and asserts 2 — real check. HOLDS. Note N2: a call entry that is
  not a dict (or lacks both keys) would raise AttributeError, not Refused;
  a call with neither id is silently skipped. No instance.
- recorded_at math: micros since epoch, `/1_000_000`, `isoformat` (lines
  88–89). Correct. Note N3: `iso_local` uses the runner's local zone
  (`astimezone()`), so start/end strings reproduce only in the same TZ;
  committed rows carry -07:00, matching this host.
- Label precedence: `Role:` in first two started prompts wins, then
  searched head label with prechecker > spark-probe > prechecker-wave0 >
  verifier-wave0 ordering, then deep search of records[:400], then session
  id (lines 181–214). The precedence fix the lead discloses in ledger/lead.md
  11:37:23 (first run mislabelled prechecker-wave0 as verifier-wave0) is
  present at lines 183–184 and the selftest's prechecker fixture really
  quotes verifier-wave0, so the check is real. HOLDS. Note N4: the searched
  fallback keys off quoted names, so live Workflow children whose protocol
  prompts quote other agents get mislabelled — observed: my own session
  8f86c39e classifies as work/verifier-wave0, and post-cutoff reminder
  sessions classify as spark-probe/prechecker-wave0/recount-probe/
  verifier-wave0 (state_check.py output). Harmless at the committed cutoff
  (all such sessions postdate it) but a re-run WITHOUT --until would emit
  duplicate agent rows today.
- Reminder exclusion: `(not is_main) and "reminder observer" in head`,
  head = first two started prompts (line 215). All 10 cutoff-excluded
  sessions match; replication with the tool's own `extract_session` gives
  exactly 19 work + 10 internal + 5 post-cutoff sessions dropped as None.
  HOLDS for this extraction. Note N5: (i) detection reads only the first
  two started prompts; (ii) sessions reduced to nothing by --until return
  None silently and the summary never mentions dropped sessions — 5 exist
  now (4 newer reminder sessions + my own), all legitimately post-cutoff.
- --until: records with `ts > until` are skipped before stamps/usage/tools
  (lines 142–145); sessions left with no stamps or no usage return None
  when until is set (lines 175–177). Cutoff `2026-10-26T11:31:34-07:00`
  parses to 1793039494000000 micros. HOLDS. Note N6: cutoff is 5 s after
  the recount-probe committed end (11:31:29) and ~0.6 s before that file's
  then-max stamp; RECORD's gloss "(the independent recount probe's end
  stamp)" is approximate either way. Figures unaffected: the only records
  in (11:31:29, cutoff] are 4 non-counted probe-file records
  (model_response_created / reasoning deltas, gap3.py), and lead max
  included stamp is exactly 11:28:59 as committed (leadstamps.py).
- Annotations: SHA must be 7–40 hex; verdict must be A,B,READY|NOT
  READY,true|false with READY+sent_back refused; unknown agents refused
  (lines 225–244); unannotated author/verifier passes refused (lines
  284–290). HOLDS. Note N7: a --verdict for a surveyor-role agent (or
  --author-commit for a non-author) would silently attach extra keys;
  no instance — annotations match roles exactly.
- Exit codes: 0 success, 1 Refused with reason, 2 on bad usage
  (`ap.error`). HOLDS. Selftest: 8 checks, 0 failed; each named check
  tests what it claims (dup counted once, distinct ids a,a,b→2, reminder
  excluded with 3 work rows, prechecker precedence, role from Role:,
  both refusals). Coverage is narrower than the hunt list (no --until,
  annotation-validation, unknown-agent, or malformed-JSON case), but
  nothing it claims is faked.

## 2) Ran it

- `--selftest`: `extract_session_metrics selftest: 8 checks, 0 failed`
  (full stdout in rerun.txt capture area; tail lines saved).
- Cutoff re-run to scratch/verifier-extractor/out with the annotations
  from ledger/lead.md 11:37:23 (lead=dfc7a02 full SHA from passes.jsonl;
  verdicts 0,3 / 0,1 / 0,0 / 0,2): exit 0, stdout
  `sessions: 19 work, 10 internal reminder sessions excluded; cutoff
  --until 2026-10-26T11:31:34-07:00`, totals wonder out=374,901
  in=65,119,663, spark out=41,137 in=3,311,541, tool_uses=851.
  Full stdout in scratch/verifier-extractor/rerun.txt.
- Diff vs committed: usage.jsonl byte-identical (19/19 rows). passes.jsonl
  identical modulo transcript-sha256 note prefixes: 18/19 prefixes match;
  only `lead` differs (fe76f464792c → 8bf2b2ffa9fe), expected — the lead
  file is live and grew. Agent sets equal. A second re-run minutes later
  changed only the lead sha prefix again; no figure moved.
- Independent recounts (own scripts, not importing the tool):
  escalation-test (recount_escalation.py): in=292469 out=7908 cached=253600
  msgs=9 tools=10 dups=0 — MATCH on every committed figure including
  start/end. harness-smoke-test: (564,46157,22644,2,1) MATCH.
  verifier-wave0: (30691,2555434,2401199,32,57) MATCH. So the commit
  message's "independent Spark recount of two sampled transcripts agreed
  on every sum" is corroborated for both named transcripts.

## 3) Numbers in prose

- Recomputed from usage.jsonl: wonder 15 agents 374,901 / 65,119,663;
  spark 4 agents 41,137 / 3,311,541; tools 770 / 81. All match RECORD's
  two sum lines exactly. All 19 table cells (out/in/cached per agent)
  match usage.jsonl. Table minutes round correctly from passes.jsonl
  spans (lead 124.3→124 … recount 2.5→2); span sums give ~270.2 and ~8.6,
  matching "about 270" / "about 9". 19 work + 10 internal matches rerun
  stdout. Kit line sha prefixes verified: passes 3e64aac4b119, usage
  554587b40261 (sha256sum). Selftest 8/0 confirmed by running it.
- Chain row: verifier-wave0 (muse-spark-1.3) 0, 2, "once — restated in
  place before push" matches ledger/verifier-wave0.md headline (NOT READY
  on 4805d2e, two (b)s) and scratch/verifier-wave0/report.md (model
  muse-spark-1.3, F1/F2, "restatable in place"). Phase-0 chain cells
  re-confirmed: verifier-phase0 0,3 (three (b) strings in its file),
  rechecker-phase0 0,1 ("one new (b)"), rechecker2-phase0 0,0 scoped
  ("no (a) and no (b) found in that scope").
- Slips paragraph: consistent with verifier-wave0 F1 (wrong time of day)
  + F2 (provenance head) and the phase-0 ledger files; notes N1–N6 from
  that report are all addressed in this commit (FPgen named, "fast paths"
  dropped, "never track master", sqrt7 helper named, "owner's audit",
  H>=20 marked believed).
- Commit-message claims: selftest 8/0 true; recount agreement corroborated
  above; cutoff value exact; "tabled by round_metrics.py" consistent
  (cells match JSONL exactly — round_metrics itself not re-run).

## 4) Diff hygiene

- HEAD is 8770745, tree clean; commit touches exactly the 4 stated files,
  654 insertions, no deletions.
- Line endings: all four files LF, no CR (`.gitattributes` `* -text`
  honored).
- No absolute home paths anywhere in the diff (grep). No private keys,
  tokens, or secret-shaped strings. Emails appear only in the commit
  trailer (owner's own address; coined noreply model address, disclosed
  as coined in RECORD) and RECORD prose about the trailer — no email in
  a committed file beyond that prose.
- Full session UUIDs appear in usage.jsonl/passes.jsonl notes by the
  tool's design (provenance); repo rules (AGENTS.md/KICKOFF.md) state no
  prohibition on session ids, and RECORD's own past slip was home paths,
  not session ids. Noted, not a finding.
- No unintended files; nothing with cft in its name touched.

## What I did not do

- Never read scratch/lead/ or any agent scratch besides the explicitly
  authorized scratch/verifier-wave0/report.md; never opened anything
  with cft in its name.
- Never changed git config (used `-c safe.directory=` per call,
  read-only commands).
- Did not re-run the kit's round_metrics.py or gate; table verified
  cell-by-cell against the JSONL inputs instead.
- Did not verify owner-quote wording against session transcripts.
- Spawned nothing; no background work started or left running (all
  commands completed in-foreground; outputs above).
- Scripts used (all in scratch/verifier-extractor/): recount_escalation.py,
  gap_check.py, gap2.py, gap3.py, state_check.py, leadstamps.py; rerun
  outputs out/, out2/, rerun.txt, rerun2.txt.
