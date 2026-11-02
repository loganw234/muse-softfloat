"""parcel-xf negative controls (build/w2/controls/).

1. flip-result-bit: first arith-xf.vec expectation bit flipped.
2. trap-flip: first exact-py-xf:trap-convert-first line with its
   expectation replaced by the convert-sources-first answer
   (recomputed here); the implementation must FAIL this file,
   proving the trap discriminates exact vs convert-first.
Writes the two control files and prints what it changed.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
WT = ROOT / "worktrees" / "w2-xf"
OUT = WT / "build" / "w2" / "controls"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location(
    "gen_vectors_xf", WT / "tests" / "gen_vectors_xf.py")
gx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gx)

# 1. flipped result bit
lines = (WT / "tests" / "vectors" / "arith-xf.vec").read_text().splitlines()
done = False
for i, l in enumerate(lines):
    if l and not l.startswith("#") and " -> " in l:
        tok = l.split()
        k = tok.index("->")
        tok[k + 1] = "%x" % (int(tok[k + 1], 16) ^ 1)
        print("control1 flipped line %d: %s" % (i + 1, l))
        print("control1          -> %s" % " ".join(tok))
        lines[i] = " ".join(tok)
        done = True
        break
assert done
(OUT / "flip-result-bit.vec").write_bytes(("\n".join(lines) + "\n").encode())

# 2. trap expectation flipped to the convert-first answer
traps = (WT / "tests" / "vectors" / "traps-xf.vec").read_text().splitlines()
binfn = dict(gx.BINOPS)
done = False
for l in traps:
    if not l or l.startswith("#"):
        continue
    tok = l.split()
    if tok[-1] != "exact-py-xf:trap-convert-first":
        continue
    name, rm = tok[0], tok[1]
    k = tok.index("->")
    argbits = [int(x, 16) for x in tok[2:k]]
    exact_bits, exact_flags = int(tok[k + 1], 16), tok[k + 2]
    parts = name.split("_")
    # msf32_<op>_<afmt>_<bfmt> or msf32_fma_<a>_<b>_<c>
    if parts[1] == "fma":
        af, bf, cf = parts[2], parts[3], parts[4]
        wb, wf = gx._wf_convert_first_fma(af, argbits[0], bf, argbits[1],
                                          cf, argbits[2], rm)
    else:
        op, af, bf = parts[1], parts[2], parts[3]
        wb, wf = gx._wf_convert_first_bin(binfn[op], af, argbits[0],
                                          bf, argbits[1], rm)
    assert wb != exact_bits, (l, wb)
    newline = "%s %s %s -> %x %02x control-xf:trap-flipped-to-convert-first" % (
        name, rm, " ".join("%x" % a for a in argbits), wb, wf)
    print("control2 exact line:        %s" % l)
    print("control2 convert-first line: %s" % newline)
    (OUT / "trap-flip.vec").write_bytes(
        ("# control: expectation is the WRONG convert-first answer\n"
         + newline + "\n").encode())
    done = True
    break
assert done
print("controls written to", OUT)
