"""Build muse-softfloat/audit-bundle-v2/ (frozen external-audit bundle, seal).

Mirrors build_audit_bundle.py (v1) with: destination audit-bundle-v2,
manifest written as raw LF bytes (v1's CRLF broke literal
`sha256sum -c` under Git Bash), evidence scripts beside reports
included, and a generated plant-keys/COPIES.txt pinning every
planted-copy commit. Exclusions are by class and printed.
"""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DST = ROOT / "muse-softfloat" / "audit-bundle-v2"
if DST.exists():
    sys.exit("audit-bundle-v2 exists; remove deliberately first")
DST.mkdir(parents=True)

SKIP_DIR_SUBSTR = ("cft",)  # never opened/listed individually, just skipped
EXCLUDE_DIR_NAMES = {"__pycache__", ".git", "node_modules", "tmp"}
ORACLE_HINTS = ("kissfft", "rebound", "mpfr", "berkeley", "coremath", "core-math")
TEXT_EXTS = {".md", ".txt", ".json", ".jsonl", ".py", ".sh", ".tsv", ".csv",
             ".toml", ".yml", ".yaml"}
stats = {"copied": 0, "bytes": 0, "skipped_oracle": 0, "skipped_binary": 0}

def bad_dir(name: str) -> bool:
    low = name.lower()
    return any(s in low for s in SKIP_DIR_SUBSTR) or name in EXCLUDE_DIR_NAMES

def oracle_dir(path: Path) -> bool:
    low = str(path).lower()
    return any(h in low for h in ORACLE_HINTS)

def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    stats["copied"] += 1
    stats["bytes"] += dst.stat().st_size

def walk_copy(src_root: Path, dst_root: Path, text_only=False, names=None):
    for p in sorted(src_root.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(src_root)
        if any(bad_dir(part) for part in rel.parts):
            continue
        if oracle_dir(p):
            stats["skipped_oracle"] += 1
            continue
        if names is not None and not any(p.match(n) or p.name == n for n in names):
            continue
        if text_only and p.suffix.lower() not in TEXT_EXTS:
            stats["skipped_binary"] += 1
            continue
        copy_file(p, dst_root / rel)

head = subprocess.check_output(
    ["git", "-C", str(ROOT / "muse-softfloat"), "rev-parse", "HEAD"]).decode().strip()

# 1. ledger (full, minus transient lock)
walk_copy(ROOT / "ledger", DST / "ledger")
for lock in (DST / "ledger").glob("*.lock"):
    lock.unlink()

# 2. bootstrap kit, frozen as delivered
walk_copy(ROOT / "softfloat-bootstrap-kit", DST / "kit")

# 3. plant keys + drafts, plus a generated copy-commit pin list
walk_copy(ROOT / "scratch" / "lead" / "keys", DST / "plant-keys")
copies = []
for kf in sorted((DST / "plant-keys").glob("key-*.json")):
    d = json.loads(kf.read_text(encoding="utf-8"))
    copies.append(f"{d.get('copy_commit')}  real_tip {d.get('real_tip')}  {kf.name}")
(DST / "plant-keys" / "COPIES.txt").write_bytes(
    ("# planted-copy commits pinned for external audit (SD-10)\n"
     + "\n".join(copies) + "\n").encode("utf-8"))
stats["copied"] += 1

# 4. scratch text evidence: reports and their small companions (v1 set)
report_names = [
    "report.md", "report-*.md", "*-report.md", "beats*.md",
    "options-facts.md", "measurements*.json", "sync_measurements*.json",
    "history.json", "gate2_numbers.json", "audit*.json", "tokens.json",
    "verify*.json", "owner_msg_lengths.json", "tree_usage.json",
    "copy_inventory.txt", "outro_msg*.txt", "intro_msg*.txt",
]
walk_copy(ROOT / "scratch", DST / "reports", text_only=True, names=report_names)
shutil.rmtree(DST / "reports" / "lead", ignore_errors=True)
# Prune repo-copy trees the name filter swept in (verifier duplicates
# carry a whole tree incl. the v1 bundle): drop anything under an
# audit-bundle* dir, and anything under a repo-copy root (a dir
# holding both tools/run.sh and video/assemble.py).
for p in sorted((DST / "reports").rglob("*"), reverse=True):
    rel = p.relative_to(DST / "reports")
    if any(part.startswith("audit-bundle") for part in rel.parts):
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
copy_roots = []
for marker in (ROOT / "scratch").rglob("tools/run.sh"):
    cand = marker.parent.parent
    if (cand / "video" / "assemble.py").exists() and cand != ROOT / "muse-softfloat":
        copy_roots.append(cand.relative_to(ROOT / "scratch"))
for rel_root in copy_roots:
    shutil.rmtree(DST / "reports" / rel_root, ignore_errors=True)
print("pruned repo-copy roots:", [str(r) for r in copy_roots][:8], "... total", len(copy_roots))

# 4b. evidence scripts sitting beside those reports (v2 addition).
# Deliberately shallow: top level of each evidence dir plus its
# scripts/ or bin/ subdir, .py/.sh only - verifier duplicate repo
# trees live deeper and must never be swept in.
EV_PREFIXES = ("audit-", "verifier-", "parcel-", "study-", "recount-")
for d in sorted((ROOT / "scratch").iterdir()):
    if not d.is_dir() or bad_dir(d.name) or oracle_dir(d):
        continue
    if not d.name.startswith(EV_PREFIXES):
        continue
    cands = [p for p in d.iterdir() if p.is_file()]
    for sub in ("scripts", "bin"):
        sd = d / sub
        if sd.is_dir():
            cands += [p for p in sd.iterdir() if p.is_file()]
    for p in sorted(cands):
        if oracle_dir(p) or p.suffix.lower() not in {".py", ".sh"}:
            continue
        if p.stat().st_size > 200_000:
            continue
        dst = DST / "reports" / p.relative_to(ROOT / "scratch")
        if not dst.exists():
            copy_file(p, dst)

# 5. lead gate scripts (root level of scratch/lead only)
lead_dst = DST / "lead-scripts"
for p in sorted((ROOT / "scratch" / "lead").glob("*")):
    if p.is_file() and p.suffix.lower() in {".sh", ".py"}:
        copy_file(p, lead_dst / p.name)

# 6. README (written before the manifest so it is listed in it)
(DST / "README.md").write_bytes(README := f"""# audit-bundle-v2/ — frozen method evidence for external auditing

Frozen 2026-11-01 at the submission seal, built from main at
`{head}` (this bundle lands in the commit immediately after).
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
""".encode("utf-8"))
stats["copied"] += 1

# 7. manifest (raw LF bytes; excludes itself)
lines = []
for p in sorted(DST.rglob("*")):
    if p.is_file() and p.name != "MANIFEST.sha256":
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{h}  {p.relative_to(DST).as_posix()}")
(DST / "MANIFEST.sha256").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
print(stats)
print(f"manifest: {len(lines)} files; head {head}")
for top in sorted(DST.iterdir()):
    n = sum(1 for _ in top.rglob("*") if _.is_file()) if top.is_dir() else 1
    print(top.name, n)
