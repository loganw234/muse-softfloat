"""Independent recount: expand instantiation counts per sig class by hand."""
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
    return rows

FMT = ["f16", "f32", "f64"]
INTS = ["i8", "u8", "i16", "u16", "i32", "u32", "i64", "u64"]
ops = read_tsv(ROOT / "tables" / "operations.tsv")

def count_sig(sig):
    n = 0
    if sig in ("rint_named", "rint_exact", "next", "sign_un", "classify",
               "class_op", "radix_op"):
        n = 3
    elif sig in ("remainder", "sign_bin", "totalorder"):
        n = 3
    elif sig == "scaleb":
        n = 3
    elif sig == "logb":
        n = 3
    elif sig == "arith_bin":
        n = 27
    elif sig == "arith_un":
        n = 9
    elif sig == "fma":
        n = 81
    elif sig == "from_int":
        n = 24
    elif sig == "to_int":
        n = 24
    elif sig == "conv_fmt":
        n = 9
    elif sig == "char_from":
        n = 3
    elif sig in ("char_to_dec", "char_to_hex"):
        n = 3
    elif sig == "compare":
        n = 9
    elif sig == "version_op":
        n = 4
    elif sig == "flag_op":
        n = 1
    else:
        raise SystemExit("unknown " + sig)
    return n

from collections import Counter
tot = 0
per = Counter()
impl = 0
impl_names = []
for r in ops:
    c = count_sig(r["sig"])
    tot += c
    per[r["sig"]] += c
    if r["status"] == "implemented":
        impl += c
        impl_names.append(r["op"])
print("families:", len(ops))
print("instantiations:", tot)
print("per-sig:", dict(per))
print("implemented instantiations:", impl, "from families:", impl_names)

# unconfirmed authority check from COVERAGE.tsv
cov = read_tsv(ROOT / "docs" / "COVERAGE.tsv")
unc = [l for l in cov if l.get("authority", "").strip() == "unconfirmed"]
print("coverage rows:", len(cov), "unconfirmed:", len(unc))
import collections
print("authority values:", collections.Counter(l.get("authority", "") for l in cov))
print("status values:", collections.Counter(l.get("status", "") for l in cov))
