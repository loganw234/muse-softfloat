import pathlib
cov = pathlib.Path("muse-softfloat/docs/COVERAGE.tsv").read_text(encoding="utf-8").splitlines()
rows = [l.split("\t") for l in cov if l and not l.startswith("#")]
hdr, rows = rows[0], rows[1:]
ni, wi, si = hdr.index("name"), hdr.index("wave"), hdr.index("status")
impl = [(r[ni], r[wi]) for r in rows if r[si] == "implemented"]
assert len(impl) == 63, len(impl)
out = ["# implemented.tsv - per-instantiation implementation status.",
       "# One row per instantiation the core provides today (name, claiming",
       "# wave). tools/gen_tables.py reads ONLY this file for status: an",
       "# instantiation not listed is planned (declared, dispatch NULL,",
       "# runner reports it not-implemented by name). A parcel appends its",
       "# own rows as its operations land; the lead merges serially.",
       "# Claiming conformance additionally needs the wave gate to close.",
       "name\twave"]
out += ["%s\t%s" % t for t in impl]
pathlib.Path("muse-softfloat/tables/implemented.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")
print("seeded", len(impl))

ops = pathlib.Path("muse-softfloat/tables/operations.tsv").read_text(encoding="utf-8").split("\n")
out = []
for ln in ops:
    if ln.startswith("#   status"):
        out.append("#   (status lives in tables/implemented.tsv, per instantiation)")
        continue
    if "\t" in ln and not ln.startswith("#"):
        cells = ln.split("\t")
        assert len(cells) == 11, ln
        del cells[7]  # status column
        ln = "\t".join(cells)
    out.append(ln)
pathlib.Path("muse-softfloat/tables/operations.tsv").write_text("\n".join(out), encoding="utf-8")
print("dropped status column")
