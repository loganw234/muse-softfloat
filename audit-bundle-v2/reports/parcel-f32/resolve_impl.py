import subprocess, pathlib
WT="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32"
def show(stage):
    r=subprocess.run(["git","-C",WT,"show",f":{stage}:tables/implemented.tsv"],capture_output=True,check=True)
    txt=r.stdout.decode("utf-8").replace("\r\n","\n").replace("\r","\n")
    return [l for l in txt.split("\n") if l!=""]
ours=show(2); theirs=show(3); base=show(1)
print("base",len(base),"ours",len(ours),"theirs",len(theirs))
seen=set(); out=[]
for l in theirs+ours:
    if l not in seen:
        seen.add(l); out.append(l)
print("union",len(out))
# assert theirs is base LF-normalised (same rows)
print("theirs==base rows:", theirs==base)
print("extra in ours vs base:", [l for l in ours if l not in set(base)][:3], "count", len([l for l in ours if l not in set(base)]))
p=pathlib.Path(WT)/"tables/implemented.tsv"
p.write_bytes(("\n".join(out)+"\n").encode())
print("wrote",p, "CRLF?", b"\r" in p.read_bytes())
