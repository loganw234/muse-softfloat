# audit-bundle/ — frozen method evidence for external auditing

Frozen 2026-10-29 at the SF-2 close (library complete: 849
instantiations). This directory collects the method files that
lived outside the repository during the run, so an external
auditor can re-walk the process without workspace access.
Nothing in here is regenerated: files are byte copies, listed
with SHA-256 in `MANIFEST.sha256` (verify with
`sha256sum -c MANIFEST.sha256` from this directory).
Corrections, if ever needed, arrive as a new bundle version,
never by editing this one.

## Layout

| Path | What |
|---|---|
| `kit/` | The bootstrap kit exactly as delivered (HonestFramework + ParcelRound methods, tools, reference material). It was never patched in place; where its tools lacked a feature (e.g. key-hash pre-commitment), the gap is named in RECORD's Wave 5 close entry. |
| `ledger/` | The append-only working ledger: `briefs/` (every parcel/verifier/study brief), per-agent parcel and verifier ledgers, study and audit ledgers, and `lead.md` (the lead's running log, including incidents). Transient `board.lock` excluded. |
| `plant-keys/` | The planted-copy keys: `key-<copy>.json` (the five planted defects per verification copy, with real tips) and `w5-*-draft.json` drafting files. Grades live in `docs/metrics/plants.jsonl`. |
| `reports/` | Agent reports from scratch, by work dir: parcel/verifier/study READY-NOT READY reports, adherence audits, feasibility studies, and small evidence JSONs (measurements, sync proofs, history). Text evidence only. |
| `lead-scripts/` | The lead's one-off gate/board/assembly scripts (board replays, plant cutting, merges' helpers, video assembly v1–v4). Working tools, kept as run. |

## Deliberate exclusions (and why)

- Build trees, exhaustive-sweep shards, binaries, MP4s other than
  those in `video/`: bulky outputs regenerable from committed vectors
  and scripts; their hashes/counts are in RECORD and the reports.
- Third-party oracle/workload source trees (KissFFT, REBOUND, MPFR
  and similar): executed as oracles in scratch only, never vendored.
  `demo/fetch.py` in the repo pins how to fetch them.
- The IEEE 754-2019 PDF and text extracts derived from it:
  copyrighted; the repo cites clauses only.
- Raw session transcripts: the distilled, checkable form is
  `docs/metrics/*.jsonl` (extracted by `tools/extract_session_metrics.py`,
  whose header is the counting contract) plus the ledgers here.
- Anything under a `cft`-named path: clean-room by construction -
  never opened, never copied.

## How to audit (suggested order)

1. `docs/RECORD.md` (repo) for the claim history, then this bundle's
   ledgers for the brief -> parcel -> verifier -> merge trail behind
   any line of it.
2. `docs/metrics/plants.jsonl` (repo) against `plant-keys/` here:
   every grade re-derives from key + verifier ledger.
3. `kit/WORKFLOW.md` + `kit/method/` for the rules as written,
   `reports/audit-adherence-final/report.md` for the final grade
   (ADHERENT WITH SLIPS) and its evidence.
4. Re-run: `tools/run.sh standard` in the repo; `demo/run_demo.sh`
   for the workloads; `video/assemble.py` for the film.
