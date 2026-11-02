"""Build muse-softfloat/audit-bundle/ (frozen external-audit bundle).

Copies the method evidence that lived outside the repo:
ledger/, plant keys, the bootstrap kit, scratch text reports,
and lead gate scripts. Exclusions are by class and printed.
"""
import hashlib, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DST = ROOT / "muse-softfloat" / "audit-bundle"
if DST.exists():
    sys.exit("audit-bundle exists; remove deliberately first")
DST.mkdir(parents=True)

SKIP_DIR_SUBSTR = ("cft",)  # never opened/listed individually, just skipped
EXCLUDE_DIR_NAMES = {
    "__pycache__", ".git", "node_modules", "tmp",
}
# third-party oracle/workload source trees never enter the bundle
ORACLE_HINTS = ("kissfft", "rebound", "mpfr", "berkeley", "coremath", "core-math")
TEXT_EXTS = {".md", ".txt", ".json", ".jsonl", ".py", ".sh", ".tsv", ".csv", ".toml", ".yml", ".yaml"}
stats = {"copied": 0, "bytes": 0, "skipped_oracle": 0, "skipped_binary": 0}


def bad_dir(name: str) -> bool:
    low = name.lower()
    if any(s in low for s in SKIP_DIR_SUBSTR):
        return True
    if name in EXCLUDE_DIR_NAMES:
        return True
    return False


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


# 1. ledger (full, minus transient lock)
walk_copy(ROOT / "ledger", DST / "ledger")
for lock in (DST / "ledger").glob("*.lock"):
    lock.unlink()

# 2. bootstrap kit, frozen as delivered
walk_copy(ROOT / "softfloat-bootstrap-kit", DST / "kit")

# 3. plant keys + drafts
walk_copy(ROOT / "scratch" / "lead" / "keys", DST / "plant-keys")

# 4. scratch text evidence: reports and their small companions
report_names = [
    "report.md", "report-*.md", "*-report.md", "beats*.md",
    "options-facts.md", "measurements*.json", "sync_measurements*.json",
    "history.json", "gate2_numbers.json", "audit*.json", "tokens.json",
    "verify*.json", "owner_msg_lengths.json", "tree_usage.json",
    "copy_inventory.txt", "outro_msg*.txt", "intro_msg*.txt",
]
walk_copy(ROOT / "scratch", DST / "reports", text_only=True, names=report_names)
# drop the lead/ subtree of reports (scripts land separately below)
shutil.rmtree(DST / "reports" / "lead", ignore_errors=True)

# 5. lead gate scripts (root level of scratch/lead only)
lead_dst = DST / "lead-scripts"
for p in sorted((ROOT / "scratch" / "lead").glob("*")):
    if p.is_file() and p.suffix.lower() in {".sh", ".py"}:
        copy_file(p, lead_dst / p.name)

# 6. manifest
lines = []
for p in sorted(DST.rglob("*")):
    if p.is_file():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{h}  {p.relative_to(DST).as_posix()}")
(DST / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(stats)
print(f"manifest: {len(lines)} files")
for top in sorted(DST.iterdir()):
    n = sum(1 for _ in top.rglob("*") if _.is_file()) if top.is_dir() else 1
    print(top.name, n)
