import pathlib
W = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w3-str")
p = W / "tables" / "implemented.tsv"
data = p.read_bytes()
# measured: the committed file is CRLF throughout (779/779 lines);
# the brief says append my rows LF, so my 12 rows are LF regardless.
assert data.endswith(b"\n")
rows = []
for f in (16, 32, 64):
    for op in ("from_decimal", "to_decimal", "from_hex", "to_hex"):
        rows.append(f"msf{f}_{op}\t3\n")
add = "".join(rows).encode()
for r in rows:
    name = r.split("\t")[0].encode()
    assert name not in data, name
p.write_bytes(data + add)
print("appended", len(rows), "rows; total lines", (data + add).count(b"\n"))
for f in ["src/msf_string.c", "tests/gen_vectors_str.py"]:
    b = (W / f).read_bytes()
    print(f, "CR bytes:", b.count(b"\r"), "LF:", b.count(b"\n"), "size:", len(b))
