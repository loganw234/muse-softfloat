# Ledger: parcel-w5metrics (Wave 5 close: metrics refresh)

## 2026-10-29 design entry (before any metrics edit): session inventory + annotation plan

**parcel-w5metrics** (brief ledger/briefs/w5-metrics.md). Base 5142594,
worktree worktrees/w5-metrics, branch wave5-metrics (clean at entry).
Owned files only: docs/metrics/{usage,passes,escalations,briefs}.jsonl,
append-only. Nothing with `cft` in its name opened/searched/listed.
Session logs read for counting and role labels only; no owner prose
retained. All runs are script files in scratch/parcel-w5metrics/ under
Git Bash, MSF_PYTHON pinned to the workspace .venv, TMP in scratch,
ulimit ceilings set in the runner.

### Session inventory (MEASURED, inventory0.py + inventory1.py, streaming)

- Store `C:\Users\logan\.local\share\muse\sessions\`: one lead session
  subtree holds the whole project: `2026/10/26/01a17907-.../session.jsonl`
  (139,442,511 bytes at scan, still live) + 247 `subagent/*/session.jsonl`
  (463,672,442 bytes). 30 other top-level session files: 27 are strict
  early snapshots of subagent files under the same session id (smaller,
  different sha256; never counted - the extractor reads the lead subtree
  only), 3 are pre-project stubs with zero provider usage
  (01a177db/01a17900/01a17905, 2026-10-26 09:14-09:24).
- Lead subtree classification (extractor rules replicated streaming):
  248 files = 102 work sessions (main + 101 children) + 146 internal
  reminder-observer sessions (excluded by the extractor, counted here so
  the exclusion is visible). No work session has zero usage.
- All 39 frozen usage/passes sessions are present on disk, including the
  three the tokens study calls missing (8186e494 verifier-w2xf,
  6473dc2e auditor-wave2, 29d5a20a auditor-final - the study's printed
  ids differ from the frozen notes by one hex digit each, and its
  `grand` adds those rows on top of a tree sum that already contains
  them: double count, quantified in the report). No frozen session is
  pruned. Pruned/invisible therefore names no Wave 4-5 session either:
  every ledger/scratch-named Wave 4-5 agent has session files (below).
- 63 unrowed work child sessions: 10 pre-Wave-1 lead-work checks never
  rowed (verifier-extractor, sf0-evidence-auditor, verifier-sf0,
  rechecker-sf0, rechecker2-sf0, approval-audit, verifier-approval,
  verifier-p0, verifier-w1prep, rechecker-nanfix), 16 Wave 4 sessions
  (4 tier2 studies, verifier-sf1 x5 sessions, verifier-w4seam,
  oracle0b, minmax pair, trigspike, interval pair, trig pair, kissfft
  pair - counted as sessions), the Wave 5 set (readme, 4 sf2 studies,
  verifier-sf2, readme2, auditor-adherence-2, attr/alg1/alg2/exp2/log2/
  aug parcel+verifier pairs with exp2 verifier x2 and aug x3 sessions,
  site/demo/twiddledoc pairs + twiddledoc fix session, 2 visual
  studies), and this parcel's own live session (excluded by cutoff).
- Cutoff: extractor `--until 2026-10-29T11:39:55-07:00` (committer time
  of base 5142594, the SF-2-close record commit). Latest in-scope child
  ends 11:36:52 (verifier-w5aug), so no in-scope child is truncated;
  only the live lead main file is cut, and this parcel's session
  (starts 11:51:01) falls outside mechanically.

### Fold rules (extractor output -> appended rows; frozen lead-fold idiom)

1. One extractor run over the lead session dir (placeholder wave;
   `--author-commit lead=dfc7a02...` taken from frozen passes.jsonl:1
   satisfies its only refusal - every Wave 4-5 child is unlabelled or
   surveyor-labelled to the extractor, so no other annotation is
   demanded at run time). The lead pass/usage rows are then dropped:
   the frozen wave0 lead row already rows the lead (cut 11:28:59), the
   brief lists no lead continuation, and re-rowing would double count.
   Unrowed lead-main tokens are quantified in the reconciliation.
2. Recount check: extractor numbers for the 38 frozen child sessions
   must equal the frozen rows per session (tokens/messages/tools/span);
   any difference is reported as a frozen-row error, never edited.
3. Relabel: extractor session-id labels are restated to agent names by
   dispatched role label + brief path + ledger/scratch attribution (the
   frozen fold's method), each mapping listed with its source in the
   fold script's table. Wave = wave of the work per RECORD/brief
   (tier2 studies wave4, sf2 studies wave5, SF-1 verification wave4,
   pre-Wave-1 SF-0/P0 checks wave0, Wave-1-prep checks wave1).
4. Roles/work/commits/verdicts restated from records only: author
   commit = merge second parent (== parcel branch tip, == RECORD's
   named commit); verifier a/b = the verifier report's own class
   counts ("each as its report counts them", kit chain rule) with
   brief-(c) folded into a and dual-tags counted at their first
   letter (disclosed per verifier in the report); PASS/FAIL mapped to
   READY/NOT READY (verifier-sf1, verifier-sf2); sent_back true only
   where git shows the work revised after the verdict (sf0 chain,
   verifier-readme, verifier-sf2, verifier-w5twiddledoc), false for
   planted-copy passes merged unchanged (branch tip predates the
   verifier session in every such case).
5. Multi-session dispatches with no reporting pass of their own (dead
   verifier-w5exp2 attempt 1, stopped verifier-sf1 attempt-1 lenses,
   parcel-w5aug attempts 1/3) fold into the reporting pass: usage sums
   per agent+model (kit sums per agent), pass start/end span the set,
   tool_uses sum, note lists every session. A kit verifier/author pass
   cannot exist without verdict/commit, and none is invented.
   parcel-w5twiddledoc gets pass 1 (author, 0cad043) + pass 2 (fixer,
   a41f026, the unnamed Spark fix child identified by commit body +
   session span; no distinct agent name exists in records).
6. Briefs appended only where base + time box are in the brief/ledger:
   study-tier2-trigspike (b704b4c, 300), parcel-w5exp2 (hypot merge
   4a80126, 900), parcel-w5metrics last (5142594, 480). The four sf2
   studies, two visual studies, and auditor-adherence-2 briefs carry
   no time box (and mostly no base) anywhere in brief or ledger:
   rows would require inventing required fields, so they are reported
   not-reconstructed instead. Verifier briefs have never had rows
   (frozen idiom) and get none.
7. Escalations appended only with a stamped sent time in a ledger
   file: video-final test (wave3, post-freeze), four tier2 study
   tests (wave4), parcel-w5alg1 board wiring and parcel-w5alg2
   VECTORS wording (wave5, answered by lead commits 109b814/53d2265).
   `answered` is omitted where the lead ledger stamps no receipt
   (the five test rows), never estimated. The wave0 channel test
   stays unrowed per the metrics README idiom (rows begin Wave 1).
8. Validation gates before commit: extractor --selftest; kit
   round_metrics.py over the appended files (all waves + wave4 +
   wave5, --repo muse-softfloat) must run clean; append-only proof
   (frozen prefixes byte-identical); reconciliation vs
   scratch/study-tokens-visual/data/tokens.json by span in numbers.

Believed: the 55 appended pass rows / 55 usage rows / 7 escalation
rows / 3 brief rows planned above close every gap the brief names
except the not-reconstructed briefs rows in rule 6. For: lead.

## 2026-10-29 results: metrics current through SF-2 close, READY

Measured: extractor selftest 8/0; full run at
`--until 2026-10-29T11:39:55-07:00` over the lead subtree =
101 work sessions (146 internal excluded). Recount vs frozen:
37/38 frozen child sessions exact; recount-probe off by its final
message (frozen-row error, reported not edited); lead differs by
cutoff as constructed. Fold appended usage +54 (39->93), passes
+55 (39->94), escalations +7 (13->20), briefs +3 (27->30, own row
last); 119 insertions, 0 deletions, frozen prefixes
byte-identical (sha-proven in append_rows.py output). Kit
round_metrics selftest 43/0; tables all-waves + wave0-wave5 on
the appended files all exit 0 with --repo; tools/run.sh smoke
PASS in 23s in the worktree. Tokens reconciliation: streamed
recount at the study's tmax equals its tree to the token (diff 0);
its grand double-counts the 3 "missing" sessions (+38,594,472
in) which are present in the subtree (study ids garbled by one
hex digit each); span bridge to SF-2 close itemised per session
in the report. Not reconstructed (named, never guessed): 7
study/audit briefs rows (no time box anywhere in brief/ledger),
5 test-escalation `answered` stamps (no lead receipt stamp).
Frozen-row errors reported: planted sent_back trues x5,
recount-probe undercount, briefs w1-ff* filename typos, plants
topic wave labels (observation). Full record:
scratch/parcel-w5metrics/report.md (first line READY).
For: lead.
