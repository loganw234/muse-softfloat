import hashlib, json
from collections import Counter
from pathlib import Path

MAIN = Path("muse-softfloat/docs/metrics")
WT = Path("worktrees/w6-metrics/docs/metrics")

def rows(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

for name in ("usage.jsonl", "passes.jsonl", "escalations.jsonl", "briefs.jsonl"):
    old = (MAIN / name).read_bytes()
    new = (WT / name).read_bytes()
    ro, rn = rows(MAIN / name), rows(WT / name)
    print(f"{name}: rows {len(ro)}->{len(rn)} prefix={new[:len(old)] == old} "
          f"new waves={Counter(r.get('wave') for r in rn[len(ro):])}")

u_old, u_new = rows(MAIN / "usage.jsonl"), rows(WT / "usage.jsonl")
def billed(rs):
    return (sum(r.get("input_tokens", 0) for r in rs),
            sum(r.get("output_tokens", 0) for r in rs))
oi, oo = billed(u_old); ni, no = billed(u_new); ai, ao = billed(u_new[len(u_old):])
print(f"usage frozen in+out={oi}+{oo}={oi+oo}")
print(f"usage appended in+out={ai}+{ao}={ai+ao}")
print(f"usage refreshed in+out={ni}+{no}={ni+no}")
agents = [r.get("agent") for r in u_new[len(u_old):]]
print("appended usage agents dup:", [a for a, c in Counter(agents).items() if c > 1])
p_new = rows(WT / "passes.jsonl"); p_old = rows(MAIN / "passes.jsonl")
print("appended passes agents:", [r.get("agent") for r in p_new[len(p_old):]])
b_new = rows(WT / "briefs.jsonl"); b_old = rows(MAIN / "briefs.jsonl")
for r in b_new[len(b_old):]:
    print("brief+", r.get("author"), "base", str(r.get("base"))[:12])
print("usage sha frozen prefix:", hashlib.sha256((MAIN / 'usage.jsonl').read_bytes()).hexdigest()[:16])
