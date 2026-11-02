import hashlib
from pathlib import Path
d = Path(__file__).resolve().parents[2] / "muse-softfloat" / "audit-bundle"
lines = []
for p in sorted(d.rglob("*")):
    if p.is_file() and p.name != "MANIFEST.sha256":
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(d).as_posix()}")
(d / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(len(lines), "entries")
