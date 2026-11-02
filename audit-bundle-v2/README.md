# audit-bundle-v2/ — frozen method evidence for external auditing

Frozen 2026-11-01 at the submission seal, built from main at
`2e298ffa46f852db87c7a80750ef864d25c0109c` (this bundle lands in the commit immediately after).
Supersedes `audit-bundle/` (v1, frozen at the SF-2 close and
never edited) with the full Wave 6 + seal record. Files are
byte copies, listed with SHA-256 in `MANIFEST.sha256` (LF line
endings; verify with `sha256sum -c MANIFEST.sha256` from this
directory — v1's manifest was CRLF, which breaks that literal
check under Git Bash while its contents still verify).
Corrections, if ever needed, arrive as a new bundle version,
never by editing this one.

## Layout

| Path | What |
|---|---|
| `kit/` | The bootstrap kit exactly as delivered (HonestFramework + ParcelRound methods, tools, reference material). Never patched in place. |
| `ledger/` | The append-only working ledger at seal: `briefs/` (every parcel/verifier/study/audit brief, including the seal rounds), per-agent parcel/verifier/study/auditor ledgers, and `lead.md`. Transient `board.lock` excluded. |
| `plant-keys/` | The planted-copy keys: `key-<copy>.json` (the five planted defects per verification copy, with real tips), drafting files, and `COPIES.txt` pinning every planted-copy commit. Grades live in `docs/metrics/plants.jsonl`; key hashes were committed to `docs/metrics/plant_keys.sha256` before dispatch from Wave 5 on. |
| `reports/` | Agent reports from scratch, by work dir, with their evidence scripts and small evidence JSONs (measurements, sync proofs, recounts). Text evidence only. |
| `lead-scripts/` | The lead's one-off gate/board/assembly/merge scripts, kept as run (including this bundle's builder). |

## Deliberate exclusions (and why)

- Build trees, exhaustive-sweep shards, binaries, MP4s and other
  renders: bulky outputs regenerable from committed vectors and
  scripts; their hashes/counts are in RECORD and the reports.
  The local music muxes and the raw soundtrack track are excluded
  on licensing grounds as well (see `video/MUSIC.md` in the repo).
- Third-party oracle/workload source trees (KissFFT, REBOUND, MPFR
  and similar): executed as oracles in scratch only, never
  vendored. `demo/fetch.py` in the repo pins how to fetch them.
- The IEEE 754-2019 PDF and text extracts derived from it:
  copyrighted; the repo cites clauses only.
- Raw session transcripts: the distilled, checkable form is
  `docs/metrics/*.jsonl` (extracted by
  `tools/extract_session_metrics.py`, whose header is the counting
  contract) plus the ledgers here.
- Anything under a `cft`-named path: clean-room by construction —
  never opened, never copied.

## How to audit (suggested order)

1. `docs/RECORD.md` (repo) for the claim history, then this
   bundle's ledgers for the brief -> parcel -> verifier -> merge
   trail behind any line of it.
2. `docs/metrics/plants.jsonl` (repo) against `plant-keys/` here:
   every grade re-derives from key + verifier ledger; dispatch
   ordering re-derives from `docs/metrics/plant_keys.sha256`
   commit times vs `docs/metrics/passes.jsonl` session stamps.
3. `kit/WORKFLOW.md` + `kit/method/` for the rules as written,
   `reports/audit-adherence-seal/report.md` for the final grade
   (ADHERENT WITH SLIPS) and its evidence; v1's bundle carries
   the SF-2-close audit.
4. Re-run: `tools/run.sh standard` in the repo;
   `demo/run_demo.sh` for the workloads; `video/assemble.py`
   for the film; `video/captions.py --validate` for captions.
