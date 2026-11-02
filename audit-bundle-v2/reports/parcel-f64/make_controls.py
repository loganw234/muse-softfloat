import pathlib, sys
sys.stdout.reconfigure(encoding="utf-8")
root=pathlib.Path(__file__).resolve().parents[2]/"worktrees/w1-f64"
out=root/"build/w1/controls"
out.mkdir(parents=True, exist_ok=True)

def load(p):
    return p.read_text().splitlines()

def first_data(lines):
    for i,l in enumerate(lines):
        if l and not l.startswith("#"):
            return i
    raise SystemExit("no data")

def flip_result(src, dst):
    lines=load(src); i=first_data(lines); tok=lines[i].split()
    a=tok.index("->"); tok[a+1]="%x" % (int(tok[a+1],16) ^ 1)
    lines[i]=" ".join(tok)
    dst.write_text("\n".join(lines)+"\n")
    print(dst, "flipped result line", i+1, lines[i])

def flip_flag(src, dst):
    lines=load(src); i=first_data(lines); tok=lines[i].split()
    a=tok.index("->"); tok[a+2]="%02x" % (int(tok[a+2],16) ^ 0x10)
    lines[i]=" ".join(tok)
    dst.write_text("\n".join(lines)+"\n")
    print(dst, "flipped flag line", i+1, lines[i])

def nan_payload(src, dst, compare):
    lines=load(src)
    # set compare directive after header
    lines = [l for l in lines if "compare=" not in l]
    lines.insert(1, "# compare=%s" % compare)
    for i,l in enumerate(lines):
        if not l or l.startswith("#"): continue
        tok=l.split(); a=tok.index("->")
        res=int(tok[a+1],16)
        # quiet nan f64: exp all ones and quiet bit
        if (res>>52)&0x7ff == 0x7ff and (res>>51)&1 and (res & ((1<<52)-1)):
            tok[a+1]="%x" % (res ^ 0x10)  # payload bit, stays quiet nan
            lines[i]=" ".join(tok)
            print(dst, "payload line", i+1, lines[i])
            break
    else:
        raise SystemExit("no qnan result found")
    dst.write_text("\n".join(lines)+"\n")

berk = root/"build/w1/quick-add.vec"
if not berk.exists():
    raise SystemExit("quick-add missing; rerun quick ingest")
flip_result(berk, out/"berkeley-flip-result.vec")
flip_flag(berk, out/"berkeley-flip-flag.vec")
nan_src = root/"build/w1/directed-check/nan-f64.vec"
nan_payload(nan_src, out/"nan-payload-nanclass.vec", "nan-class")
nan_payload(nan_src, out/"nan-payload-exact.vec", "exact")
print("controls written to", out)
