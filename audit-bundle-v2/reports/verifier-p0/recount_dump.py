"""Independent recount from tables/ (no gen_tables.py logic reused)."""
import pathlib

ROOT = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\muse-softfloat")

def read_tsv(path):
    rows, header = [], None
    for line in path.read_text(encoding="utf-8").split("\n"):
        if not line or line.startswith("#"):
            continue
        cells = line.split("\t")
        if header is None:
            header = cells
        else:
            assert len(cells) == len(header), (path, line)
            rows.append(dict(zip(header, cells)))
    return rows, header

fmts, fh = read_tsv(ROOT / "tables" / "formats.tsv")
ops, oh = read_tsv(ROOT / "tables" / "operations.tsv")
print("formats header:", fh)
print("formats rows:", [(f["name"], f.get("p"), f.get("w"), f.get("emax")) for f in fmts])
print("ops header:", oh)
print("families:", len(ops))
for r in ops:
    print(" | ".join(str(r.get(k, "")) for k in oh))
