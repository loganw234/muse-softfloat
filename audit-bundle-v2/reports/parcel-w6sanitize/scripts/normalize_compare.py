import re, sys
# Normalized verdict comparison (acceptance b): drop the date line,
# canonicalize the elapsed-seconds in the final budget line. Every
# other byte (LF endings, verdicts, totals, inventory, build ids)
# must be identical.
def norm(path):
    data = open(path, "rb").read()
    lines = data.split(b"\n")
    out = []
    for ln in lines:
        if ln.startswith(b"date: "):
            continue
        ln = re.sub(rb"budget (\w+): PASS in \d+s", rb"budget \1: PASS in Ns", ln)
        out.append(ln)
    return b"\n".join(out)
a, b = norm(sys.argv[1]), norm(sys.argv[2])
open(sys.argv[3], "wb").write(a)
open(sys.argv[4], "wb").write(b)
print(f"before bytes={len(a)} after bytes={len(b)} identical={a == b}")
if a != b:
    al, bl = a.split(b"\n"), b.split(b"\n")
    for i, (x, y) in enumerate(zip(al, bl)):
        if x != y:
            print(f"first diff line {i+1}:\n  before: {x!r}\n  after:  {y!r}")
            break
    print(f"lines before={len(al)} after={len(bl)}")
    sys.exit(1)
