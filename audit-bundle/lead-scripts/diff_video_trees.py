import hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "video"            # workspace (new work)
B = ROOT / "muse-softfloat" / "video"  # repo (tracked old)
def files(base):
    return {str(p.relative_to(base)): p for p in base.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts}
fa, fb = files(A), files(B)
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()[:12]
only_a = sorted(set(fa) - set(fb))
only_b = sorted(set(fb) - set(fa))
diff = [k for k in sorted(set(fa) & set(fb)) if h(fa[k]) != h(fb[k])]
same = [k for k in sorted(set(fa) & set(fb)) if h(fa[k]) == h(fb[k])]
print(f"workspace-only ({len(only_a)}):"); [print("  +", k) for k in only_a]
print(f"repo-only ({len(only_b)}):"); [print("  -", k) for k in only_b]
print(f"differ ({len(diff)}):"); [print("  ~", k) for k in diff]
print(f"identical: {len(same)}")
