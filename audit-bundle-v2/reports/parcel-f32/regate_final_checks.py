import pathlib
for p in ["worktrees/w1-f32/tests/gen_vectors_f32.py","worktrees/w1-f32/tests/vectors/arith-f32.vec","worktrees/w1-f32/tables/implemented.tsv"]:
    b=pathlib.Path(p).read_bytes()
    print(p, "bytes", len(b), "CR", b.count(b"\r"), "LF", b.count(b"\n"))
# implemented rows
lines=pathlib.Path("worktrees/w1-f32/tables/implemented.tsv").read_text().splitlines()
print("impl lines incl header", len(lines), "msf32 rows", sum(1 for l in lines if l.startswith("msf32_")))
# directed bytes for the 6 parcel files
names=["arith-f32.vec","fma-sqrt-f32.vec","conv-int-f32.vec","toint-f32.vec","rint-misc-f32.vec","compare-f32.vec"]
tot=0
for n in names:
    b=pathlib.Path("worktrees/w1-f32/tests/vectors",n).read_bytes(); tot+=len(b); print(n, len(b), "data-lines", sum(1 for l in b.decode().splitlines() if l and not l.startswith("#")))
print("parcel directed total bytes", tot)
