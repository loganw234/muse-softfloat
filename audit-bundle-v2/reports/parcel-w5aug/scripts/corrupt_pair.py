import sys

src, dst = sys.argv[1], sys.argv[2]
out = []
done = 0
for line in open(src, encoding="utf-8"):
    tok = line.split()
    if not done and len(tok) == 9 and tok[4] == "->":
        tail = int(tok[6], 16) ^ 1
        tok[6] = "%016x" % tail
        line = " ".join(tok) + "\n"
        done += 1
    out.append(line)
open(dst, "w", encoding="utf-8", newline="\n").writelines(out)
print("corrupted %d pair tail expectation(s) -> %s" % (done, dst))
assert done == 1
