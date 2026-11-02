import csv, pathlib
root = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w2-xf")
outdir = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\snippets")
outdir.mkdir(exist_ok=True)
def read_tsv(p):
    lines=[l for l in open(p, encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))
cov=read_tsv(root/"docs/COVERAGE.tsv")
w2=[r for r in cov if r["wave"]=="2" and (r["name"].startswith("msf32_") or r["name"].startswith("msf64_"))]
TYPE={"f16":"msf16_t","f32":"msf32_t","f64":"msf64_t"}
F32F={"f16":"FMT16","f32":"FMT32","f64":"FMT64"}
F64F={"f16":"MSF_FMT_F16","f32":"MSF_FMT_F32","f64":"MSF_FMT_F64"}
snips={}
def add(key,line): snips.setdefault(key,[]).append(line)
for r in w2:
    name,dest,srcs=r["name"],r["dest"],r["sources"].split(",")
    std=r["std_name"]
    if std in ("addition","subtraction","multiplication","division"):
        macro={"addition":"DEF_ADD","subtraction":"DEF_SUB","multiplication":"DEF_MUL","division":"DEF_DIV"}[std]
        if dest=="f32":
            add("msf32_arith", f"{macro}({name}, {TYPE[srcs[0]]}, {F32F[srcs[0]]}, {TYPE[srcs[1]]}, {F32F[srcs[1]]})")
        else:
            add("msf64_arith", f"{macro}({name}, {F64F[srcs[0]]}, {TYPE[srcs[0]]}, {F64F[srcs[1]]}, {TYPE[srcs[1]]})")
    elif std=="fusedMultiplyAdd":
        if dest=="f32":
            add("msf32_fma", f"DEF_FMA({name}, {TYPE[srcs[0]]}, {F32F[srcs[0]]}, {TYPE[srcs[1]]}, {F32F[srcs[1]]}, {TYPE[srcs[2]]}, {F32F[srcs[2]]})")
        else:
            add("msf64_fma", f"DEF_FMA({name}, {F64F[srcs[0]]}, {TYPE[srcs[0]]}, {F64F[srcs[1]]}, {TYPE[srcs[1]]}, {F64F[srcs[2]]}, {TYPE[srcs[2]]})")
    elif std in ("squareRoot","convertFormat"):
        add("misc", name)
    else:
        add("cmp_"+dest, name)
for k,v in snips.items():
    (outdir/(k+".txt")).write_text("\n".join(v)+"\n", encoding="utf-8")
    print(k, len(v))
# comparison predicate table check against msf32 existing lines
print("\n".join(snips.get("cmp_f32",[])))
print("misc:", snips.get("misc"))
