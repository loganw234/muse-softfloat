import subprocess, pathlib
wt = pathlib.Path("worktrees/w1-f64")
def show(stage):
    return subprocess.check_output(["git","-C",str(wt),"show",f":{stage}:tables/implemented.tsv"])
base = show(1).replace(b"\r\n",b"\n").splitlines()
ours = show(2).replace(b"\r\n",b"\n").splitlines()
theirs = show(3).replace(b"\r\n",b"\n").splitlines()
print(f"base={len(base)} ours={len(ours)} theirs={len(theirs)}")
# Union preserving ours order, then any theirs-only lines in theirs order (none expected beyond normalisation)
seen=set()
out=[]
for line in ours:
    if line not in seen:
        seen.add(line); out.append(line)
extra=[l for l in theirs if l not in seen]
print(f"theirs-only lines to append: {len(extra)}")
for l in extra:
    out.append(l)
p = wt/"tables/implemented.tsv"
data = b"\n".join(out) + b"\n"
p.write_bytes(data)
print(f"wrote {len(out)} lines, {len(data)} bytes, CR count={data.count(bytes([13]))}")
