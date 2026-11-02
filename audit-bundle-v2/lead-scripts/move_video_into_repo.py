import shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
src = ROOT / "video"
dst = ROOT / "muse-softfloat" / "video"
assert src.exists() and not dst.exists()
shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
n = sum(1 for _ in dst.rglob("*") if _.is_file())
sz = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file())
print(f"copied {n} files, {sz/1e6:.1f} MB -> {dst}")
