import pathlib
p = pathlib.Path("muse-softfloat/tables/operations.tsv")
lines = p.read_text(encoding="utf-8").split("\n")
out = []
for ln in lines:
    if "\tflag_op\t" in ln:
        ln = ln.replace("\tnone\tno\t0\t", "\tnone\tstate\t0\t")
    if ln.startswith("to_<int>_"):
        ln = ln.replace("exact-int-sweep\texact", "exact-int-sweep\texact-invalid-project-rule")
    out.append(ln)
p.write_text("\n".join(out), encoding="utf-8", newline="\n")
print("flag_op state rows:", sum(1 for l in out if "\tstate\t" in l))
print("to_int rows:", sum(1 for l in out if "exact-invalid-project-rule" in l))
