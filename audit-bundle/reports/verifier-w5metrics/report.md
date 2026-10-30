NOT READY

Verifier: verifier-w5metrics. Copy: `worktrees/verify5-metrics` (detached
HEAD `091c890`, parent `5142594`; read-only, unmodified — `git status`
clean at end of run). Authorities read: this brief
(`ledger/briefs/verify-w5metrics.md`), `ledger/parcel-w5metrics.md`, the
copy's `tools/extract_session_metrics.py`, the session stores under
`C:\Users\logan\.local\share\muse\sessions\`, the copy's git history,
`docs/RECORD.md` (in the copy), `scratch/study-tokens-visual/data/tokens.json`,
`softfloat-bootstrap-kit` (kit rule + `round_metrics.py`). Never consulted:
the parcel branch/worktree, any other worktree, key files, `scratch/lead/`,
`scratch/parcel-w5metrics/`, `ledger/lead.md`; nothing with `cft` in its
name opened/searched/listed. Session logs read for counting and role labels
only; no owner prose quoted. All runs are script files in this directory
(Git Bash, `MSF_PYTHON` pinned to the workspace `.venv`
Python 3.12.15, `ulimit` ceilings, large logs streamed/file-by-file).

## Probe 1 — append-only: PASS

Parent-blob hash vs file head (Git Bash `sha256sum`), all four files
byte-identical prefixes, 119 insertions, 0 deletions
(`scratch/verifier-w5metrics/00_append_only.sh`):

- `usage.jsonl`: parent rows 39, head rows 93, prefix IDENTICAL
  (`11463ad2...`), appended 54.
- `passes.jsonl`: parent 39, head 94, IDENTICAL (`d96ea499...`), appended 55.
- `escalations.jsonl`: parent 13, head 20, IDENTICAL (`baed1144...`), appended 7.
- `briefs.jsonl`: parent 27, head 30, IDENTICAL (`6854b096...`), appended 3.

## Probe 2 — extractor re-run: 7/8 agents exact; 2 row/note errors (F1, F5)

- Selftest from the copy: `extract_session_metrics selftest: 8 checks,
  0 failed` (`01_selftest.sh`).
- Resample (`02_resample.py/.sh`, same extractor code, `--until
  2026-10-29T11:39:55-07:00`): wave0 verifier-sf0, wave4
  study-tier2-trigspike + verifier-sf1 (5 sessions folded), wave5
  parcel-w5exp2 / verifier-w5twiddledoc / study-tokens-visual /
  parcel-w5aug (3 sessions folded) — every token/message/tool-use number,
  model string, pass start/end/tool_uses, and note sha prefixes MATCH.
- verifier-w5exp2: all four usage numbers + messages + pass tools/span/shas
  MATCH, but the row's model (`muse-wonder-full-1.0`) is wrong — both
  session files contain only `muse-spark-1.3` completions (217 + 102 msgs;
  out 192,336 + 67,691 = 260,027; in 49,775,540 + 15,352,760 = 65,128,300).
  FINDING F1. Its pass row spans/sums BOTH sessions (tools 232 + 145 = 377,
  start 17:31:50), contradicting its note ("pass is the second attempt's
  span set"). Note inaccuracy FINDING F5.
- Model attribution: extractor saw exactly the row's model for the other 7
  agents (relabelling accepted per the fold's role-label + ledger mapping;
  first-prompt heads are workflow protocol text, labels deeper/attributed).

## Probe 3 — annotations

Authors (`03a_authors.py`, ALL TRACE): all 14 author/fixer commits exist,
are ancestors of HEAD, are the landing merges' second parents (13/13;
twiddledoc pass 1 is the pre-fix mainline commit named explicitly by parcel
rule 5), and are cited in RECORD and/or a parcel ledger (kissfft via RECORD
line 748 citing merge `32bbd93` whose message names tip `d322d07`).

Verifiers: every appended verdict matches its ledger report + full report
(`03b_tallies.sh`, `03c_findings.sh`, per-section reads). a/b totals match
in all 26 rows — explicit tags where the report/ledger gives them (sf0
0,6; rechecker-sf0 0,2; sf1 0,0 PASS→READY; w4seam 3,2 with (b1)/(b2) named;
w4minmax 0,5; w4interval 2,3; w4trig 3,3 tagged; w4kissfft 4,1 tagged;
w5attr 3,2 first-line; w5alg1 1,3 "3 wrong-answer + 1 seam-regression";
w5alg2 2,3 tagged; w5log2 1,4 with F3 (b/c)→(b) at first letter;
w5exp2 3,2 with F1 (b) explicit; w5aug 5,1 see F6). Untagged splits follow
the kit rule ((a) = regression vs the in-copy record, (b) = wrong answer):
readme 5,1 (F6 no-authority as the (b)); readme2 5,0; w5site 4,1 (F1
behavior swap as the (b)); w5demo 1,4 (gate-hole finding as the (a));
w5log2 F5 wrong-vector as (b); w5exp2 F2/F3/F5 (a), F4 (b); sf2 F5-minor as
the (b); twiddledoc F1–F7 all (a) (the one "(b)" hit in its report is a
"Site-(b)" label, not a finding).

sent_back: true sourced for sf0 chain (draft-3 `828b8f1` 13:35 after both
verdicts), verifier-readme (fix `d87c87c` 05:15 after 03:55 pass end),
verifier-sf2 (fold `f3eea91` 05:24:09 after 05:22:51 pass end),
verifier-w5twiddledoc (fix `a41f026` 18:06:16 after 18:03:55 + merge
`97d1cbe`). verifier-w5aug true has NO post-verdict revision: tip
`3741453` (09:53) predates the session (11:11–11:36); merge `4a0b0d4`
(11:37:16) lands identical content (empty second-parent diff) —
structurally identical to verifier-w5exp2 (merge 3 min after a NOT READY
verdict, unchanged content) which is marked false. FINDING F4 (breaks the
brief's "planted-copy NOT READY is NOT a send-back" rule). All falses
consistent: branch tips predate verifier sessions; landing merges carry no
new content (exp2/alg1/log2 checked); w4seam's "send back" verdict text is
a recommendation, and no dedicated revision round occurred.

## Probe 4 — escalations: sent/answered sourced; 1 unverifiable stamp (U1)

All 7 sent stamps sourced: video-final + 4 tier2 from `ledger/urgent/*`
Written stamps (10:37:11; 13:55:26/13:56:00/13:56:08/13:56:19, the last
with the channel test named in the study-architecture ledger entry);
alg1/alg2 from parcel results entries (06:36:21, 07:51:02). Answered:
alg1 = `109b814` committer date 06:59:35 ✓ (message confirms the Step 2a
escalation fix); alg2 = `53d2265` 08:55:26 ✓ (message confirms the wording
fix); 4 tier2 rows omit answered ✓ (no lead receipt). video-final answered
= sent stamp with no inspectable receipt (only `ledger/video-final.md:2`
carries 10:37:11; the receipt would live in the off-limits `ledger/lead.md`)
→ UNRESOLVED U1, not a fabrication finding (frozen idiom rows carry
answered test receipts as routine; design/results entries are
self-consistent reading "five" as the 4 tier2 rows + the unrowed wave0
channel test).

## Probe 5 — briefs: 2/3 sourced; 1 corrupt base (F3)

- study-tier2-trigspike: base `b704b4c9b805...` exists ("Recorded SF-1
  Step 1 landing"); brief + study ledger name it; time box 300 ✓.
- parcel-w5metrics: base `5142594` ✓ (the cut commit); time box 480 per the
  parcel brief ("~480 min") ✓.
- parcel-w5exp2: time box 900 ✓ ("base = the hypot merge commit"); but the
  row's base `5a8012636d5b2c5785935dc64bc137a39d4556d6` does NOT exist —
  one-hex-digit corruption of `4a80126...` (the hypot merge; design rule 6
  names it; brief intent matches). FINDING F3. The kit table independently
  records it: "git diff failed: fatal: bad object 5a80126...".

## Probe 6 — reconciliation: exact three-way accounting

Streamed file-by-file recount at cutoff (`06_reconcile.py/.sh`,
`06b_peragent.py`): 101 work + 145 internal-with-usage sessions (plus the
cancelled zero-usage `01a17f18` = the study's "1 zero" file, and 2
post-cutoff sessions correctly excluded by `--until`, one being this
verification session). 89/93 usage agents re-derive exactly; the 4 deltas
are lead (frozen cut, expected), recount-probe (known frozen-row error,
confined to a frozen row), and F1/F2. Fold-vs-recount delta (out
+901,455 / in +371,630,203 / msgs +1,453) decomposes EXACTLY: unrowed
lead-main continuation (out +950,418 / in +371,587,130 / msgs +1,452) +
recount-probe error (out +1,037 / in +43,073 / msgs +1) − extractor slip
(out −50,000).

- Study bridge: study tree (tmax 2026-10-28T20:07:54) = work-only recount +
  internal recount at tmax, EXACTLY (out 6,444,124 / in 1,469,302,586 /
  cached 1,424,594,514 / msgs 8,709). So the study summed provider usage on
  ALL files including the 145 internal reminder sessions
  (out 235,121 / in 13,560,774 / cached 8,642,189 / msgs 145); the
  extractor excludes them from rows. Parcel "diff 0" holds only for
  work+internal combined — semantic qualifier F8 (minor).
- Span bridge (tmax → SF-2 close): 8 sessions, out 380,917 / in
  106,378,696 / msgs 645, itemised: lead-main continuation (28,954 /
  11,265,354 / 50), study-tokens-visual tail (24,604 / 4,247,152 / 36),
  parcel-w5log2 `a5304343` (18,272 / 11,289,699 / 39), verifier-w5log2
  `c9338017` (93,103 / 24,033,925 / 165), aug attempts `90de2274`
  (8,148 / 1,164,023 / 26), `dded10c5` (91,544 / 20,137,930 / 120),
  `7cc459bf` (4,049 / 902,128 / 21), verifier-w5aug `f1f11a35` (112,243 /
  33,338,485 / 188). Check: tmax→cutoff recount deltas match to the token.
- Double-count: the 3 "missing" sessions exist under near-ids and their
  frozen numbers sum EXACTLY to the study's missing block (in 38,594,472 =
  31,686,147 + 1,996,410 + 4,911,915; out 158,002; msgs 242) — grand adds
  them onto a tree that already contains them. CONFIRMED. ID-garbling note:
  digits differ by 4/1/2, not "one hex digit each" (F7, minor).

## Probe 7 — kit + smoke: PASS

- Kit `round_metrics.py` selftest 43/0; tables `all`, `wave4`, `wave5`
  over the copy's files with `--repo` all exit 0 (`07a_kit.sh`,
  outputs in `kit-tables/`).
- `tools/run.sh smoke` PASS in 26s, exit 0, in an isolated scratch copy
  (`07b_smoke.sh`, log `07b_smoke.log`): code tree byte-identical to the
  copy (src/include/tables/tests/tools/run.sh all diff-clean; docs
  identical outside metrics), drift check clean, 411,213/411,213 vectors,
  unit/type/symbol/controls clean. Run outside the copy; the copy never
  modified. (The main checkout's tracked files are not visible from this
  session, and every other worktree is fenced off, so the isolated
  byte-identical tree is the closest faithful runner.)

## Findings (row/annotation errors)

- F1: appended `usage` row verifier-w5exp2 model `muse-wonder-full-1.0`
  vs transcripts' `muse-spark-1.3` (numbers exact).
- F2: appended `usage` row verifier-extractor `output_tokens` 84,350 vs
  transcript 34,350 (+50,000; every other field exact). The parcel's own
  results-entry total (3,574,759) matches the corrected sum, not the
  committed rows' sum (3,624,759).
- F3: appended `briefs` row parcel-w5exp2 `base` 5a80126… nonexistent;
  intended 4a80126… (hypot merge). Kit table echoes the bad object.
- F4: appended `passes` row verifier-w5aug `sent_back=true` with no
  post-verdict revision (merge lands identical pre-verdict tip 24 s after
  the verdict); the identical exp2 shape is marked false.
- F5 (minor): verifier-w5exp2 pass note ("second attempt's span set")
  contradicts the row, which spans/sums both sessions.
- F6 (minor): verifier-w5aug row totals 6 (5,1) vs the verifier's own "5
  findings" + ledger tags (= 4,1 at first-letter rule); the 5th (a) has no
  explicit tag (plausibly the disproved pool-zero-mismatch claim, class
  undisclosed).
- F7 (minor): study-id garbling is 4/1/2 digits, not "one hex digit each".
- F8 (minor): study-tree "diff 0" needs the work+internal qualifier above.

## Not done / unresolved

- U1: video-final escalation `answered` stamp source (presumed lead receipt
  in off-limits `ledger/lead.md`) — unverifiable and unfalsified here.
- a/b splits for reports without explicit class tags are reconstructed
  from the kit rule ((a) = regression vs the in-copy record, (b) = wrong
  answer); totals and verdicts are verified, the per-finding class mapping
  for readme/readme2/w5site/w5demo/w5log2-F5/w5exp2-F2–F5/sf2-F1–F4/
  twiddledoc-F1–F7 is the natural reading, stated per row above.
- Full per-agent resample covered 8 of 54 appended usage agents (waves
  0/4/5 + verifiers + studies + multi-session folds); all 93 agents were
  additionally re-derived per-session from the row notes (`06b`), with
  only the lead cut, the known recount-probe frozen error, F1, and F2 as
  deltas.
- The copy was never modified; no commits made by this verifier.
