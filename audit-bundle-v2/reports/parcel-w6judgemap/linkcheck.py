import os, re, sys
readme = sys.argv[1]
base = os.path.dirname(os.path.abspath(readme))
text = open(readme, encoding="utf-8").read()
bad = []
n_rel = 0
for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", text):
    t = m.group(1).strip("<>")
    if t.startswith(("http://", "https://", "mailto:", "#")):
        continue
    n_rel += 1
    path = t.split("#")[0]
    if not path:
        continue
    full = os.path.normpath(os.path.join(base, *path.split("/")))
    if not os.path.exists(full):
        bad.append((t, full))
    else:
        print(f"OK  {t}")
print(f"relative_links={n_rel} bad={len(bad)}")
for t, f in bad:
    print(f"BAD {t} -> {f}")
sys.exit(1 if bad else 0)
