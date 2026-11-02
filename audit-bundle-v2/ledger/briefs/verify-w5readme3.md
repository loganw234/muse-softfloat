**Role:** verifier-w5readme3 (ParcelRound verifier, README+site refresh)

**Stance:** disconfirm only. Findings: a public number
or claim the tree contradicts, a site artefact that
does not reproduce, a WASM answer that disagrees.

**Copy:** `worktrees/verify5-readme3` (detached HEAD,
parent `e9c57fb`). Never consult the parcel
branch/worktree, other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5readme3/`, or `ledger/lead.md`.
Authorities: this brief, `ledger/parcel-w5readme3.md`,
the copy's tree itself (COVERAGE, metrics jsonl,
RECORD, tables, runners), `scratch/parcel-w5site/`
(build recipe) if needed. Nothing with `cft` in its
name. Never modify the copy (serve/inspect outside it).

**Required probes:**
1. Every README number re-derived by your own
   commands: instantiations (COVERAGE + gate
   inventory), committed vectors (runner total),
   standard extras split, plants (plants.jsonl
   recount, incl. by-wave), metrics row counts,
   workloads' figures vs RECORD hashes.
2. Claim discipline: timings never framed as
   performance claims; KissFFT never "unmodified";
   the augmented op-count benefit labelled study
   model (interval not consuming it yet); P1=R2 and
   fixed-rounding statements vs the kernel/tables;
   the fifth attribute's scope vs COVERAGE attr rows.
3. Site data: `site/data.json`/`ops.json` regenerated
   by the copy's build_data.py must match committed;
   ops runnable count vs dispatch; the 9 augmented
   pairs' exclusion printed wherever the total is
   claimed (index.html, numbers, site/README).
4. WASM: rebuild `site/msf.wasm` from the recipe -
   byte-identity claimed; replay the committed
   sample (`site/replay.mjs` shape) headless - every
   sample line must match the committed vector files
   AND the wasm answers (0 mismatches), include
   explog known-answers (exp2(0)=1 class cells).
5. Serve check: static serve of site/ outside the
   copy, status line numbers == data.json == your
   recounts; no 404 assets.
6. Claim surface = README.md + site/ + one briefs row
   vs the parent; briefs row base is the real base.

**Outputs:** `scratch/verifier-w5readme3/report.md`
(READY/NOT READY; per-number table: claimed vs
re-derived; findings; not-done) + `ledger/
verifier-w5readme3.md`. Structured
complete/evidence/unresolved - mandatory. Script files
(Git Bash, MSF_PYTHON pinned; WASM tooling scratch
only). ~300 min.
