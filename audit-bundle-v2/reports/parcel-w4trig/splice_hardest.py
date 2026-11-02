import re

gen = open("worktrees/w4-trig/tests/gen_vectors_trig.py", encoding="utf-8").read()
ext = open("scratch/parcel-w4trig/out/hardest_ext.txt", encoding="utf-8").read()
ext = "\n".join(l for l in ext.splitlines() if not l.startswith("#"))
pat = re.compile(r'HARDEST_EXT = \{.*?\n\}', re.S)
assert pat.search(gen)
gen = pat.sub(ext.rstrip(), gen, count=1)
with open("worktrees/w4-trig/tests/gen_vectors_trig.py", "w", newline="\n", encoding="utf-8") as fh:
    fh.write(gen)
print("spliced; gen bytes", len(gen))
