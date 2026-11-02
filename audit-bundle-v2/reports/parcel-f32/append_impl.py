import csv, pathlib
root=pathlib.Path("worktrees/w1-f32")
lines=[l for l in open(root/"docs/COVERAGE.tsv", encoding='utf-8').read().splitlines() if not l.startswith('#')]
rows=list(csv.DictReader(lines, delimiter='\t'))
mine=[r['name'] for r in rows if r['wave']=='1' and r['name'].startswith('msf32_')]
assert len(mine)==173, len(mine)
p=root/"tables/implemented.tsv"
data=p.read_bytes()
print("ends with LF:", data.endswith(b"\n"), "CR present:", b"\r" in data, "len", len(data))
existing=data.decode().splitlines()
names=[l.split("\t")[0] for l in existing if l and not l.startswith("#") and l!="name\twave"]
assert not set(mine)&set(names), set(mine)&set(names)
add="".join("%s\t1\n"%n for n in mine).encode()
assert data.endswith(b"\n")
p.write_bytes(data+add)
print("appended", len(mine), "new len", len(data+add))
