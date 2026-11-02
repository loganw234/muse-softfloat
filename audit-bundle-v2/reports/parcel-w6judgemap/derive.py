#!/usr/bin/env python3
"""Re-derive every README number from the w6-judgemap tree. Read-only."""
import collections, csv, hashlib, json, os, re, struct, sys

ROOT = sys.argv[1]
def p(*a): return os.path.join(ROOT, *a)
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
def count_lines(path):
    with open(path, "rb") as f:
        return sum(1 for _ in f)

out = []
# COVERAGE
rows = []
with open(p("docs", "COVERAGE.tsv"), newline="", encoding="utf-8") as f:
    lines = [ln for ln in f if not ln.startswith("#")]
rdr = csv.DictReader(lines, delimiter="\t")
for r in rdr:
    rows.append(r)
out.append(f"COVERAGE header={rdr.fieldnames}")
out.append(f"COVERAGE rows={len(rows)}")
for key in rdr.fieldnames or []:
    c = collections.Counter((r.get(key) or "") for r in rows)
    if len(c) <= 12:
        out.append(f"COVERAGE {key}={dict(sorted(c.items()))}")
# vectors
vdir = p("tests", "vectors")
vfiles = sorted(f for f in os.listdir(vdir) if f.endswith(".vec"))
vtotal = sum(count_lines(os.path.join(vdir, f)) for f in vfiles)
out.append(f"VECTORS files={len(vfiles)} total_lines={vtotal}")
# dispatch ops count (site runnable derivation: count distinct op rows in dispatch header lightly)
disp = open(p("tests", "msf_dispatch.h"), encoding="utf-8", errors="replace").read()
out.append(f"DISPATCH bytes={len(disp)}")
# plants
plants = [json.loads(ln) for ln in open(p("docs", "metrics", "plants.jsonl"), encoding="utf-8") if ln.strip()]
grades = collections.Counter(r.get("grade") for r in plants)
bywave = {}
for r in plants:
    w = r.get("wave"); bywave.setdefault(w, [0, 0]); bywave[w][1] += 1
    if r.get("grade") == "caught": bywave[w][0] += 1
out.append(f"PLANTS total={len(plants)} grades={dict(grades)} caught={grades.get('caught',0)}")
out.append(f"PLANTS by_wave={bywave}")
# metrics row counts
for name in ["usage.jsonl", "passes.jsonl", "briefs.jsonl", "corrections.jsonl", "escalations.jsonl", "plants.jsonl", "fetches.jsonl"]:
    path = p("docs", "metrics", name)
    rows_j = [json.loads(ln) for ln in open(path, encoding="utf-8") if ln.strip()]
    waves = collections.Counter(r.get("wave") for r in rows_j)
    out.append(f"METRICS {name} rows={len(rows_j)} waves={dict(sorted((str(k),v) for k,v in waves.items()))}")
# fetches detail
for r in [json.loads(ln) for ln in open(p("docs","metrics","fetches.jsonl"), encoding="utf-8") if ln.strip()]:
    out.append(f"FETCH {r.get('name')} {r.get('version')} sha={str(r.get('archive_sha256'))[:16]}...")
# expected files
ias = [ln for ln in open(p("demo","expected-ias15.txt"), encoding="utf-8") if ln.strip() and not ln.startswith("#")]
out.append(f"IAS15 expected_records={len(ias)} first_step={ias[0].split()[0]} last_step={ias[-1].split()[0]} sha256={sha256_file(p('demo','expected-ias15.txt'))}")
kf = [ln for ln in open(p("demo","expected-kissfft.txt"), encoding="utf-8") if ln.startswith("KF ")]
out.append(f"KISSFFT expected_rows={len(kf)} configs={sorted(set((ln.split()[1],ln.split()[2],ln.split()[3]) for ln in kf))} sha256={sha256_file(p('demo','expected-kissfft.txt'))}")
iv = open(p("demo","expected-interval.txt"), encoding="utf-8").read()
out.append(f"INTERVAL expected_file={iv.strip().splitlines()[-2:]} sha256={sha256_file(p('demo','expected-interval.txt'))}")
cat = [ln for ln in open(p("tests","interval_catalogue.tsv"), encoding="utf-8") if ln.strip()]
out.append(f"INTERVAL catalogue_lines={len(cat)} head={cat[0].strip()[:80]}")
# CI jobs
ci = open(p(".github","workflows","ci.yml"), encoding="utf-8").read()
jobs = re.findall(r"^  ([a-z0-9_-]+):\s*$", ci, re.M)
out.append(f"CI jobs={jobs}")
for m in re.findall(r"run:\s*(.+run\.sh.+|.+build\.sh.+)", ci):
    out.append(f"CI run: {m.strip()}")
pages = open(p(".github","workflows","pages.yml"), encoding="utf-8").read()
out.append(f"PAGES has_upload={'upload-pages-artifact' in pages or 'pages' in pages.lower()}")
# site data
data = json.load(open(p("site","data.json"), encoding="utf-8"))
out.append(f"SITE data.json base={data.get('base')} inst={data['instantiations']} vectors={data['vectors']['total']} plants={data['plants']['caught']}/{data['plants']['total']} sample={data['sample']}")
ops = json.load(open(p("site","ops.json"), encoding="utf-8"))
out.append(f"SITE ops.json type={type(ops).__name__} len={len(ops) if hasattr(ops,'__len__') else '?'}")
try:
    vs = json.load(open(p("site","vectors-sample.json"), encoding="utf-8"))
    out.append(f"SITE vectors-sample type={type(vs).__name__} len={len(vs) if hasattr(vs,'__len__') else '?'}")
except Exception as e:
    out.append(f"SITE vectors-sample lines={count_lines(p('site','vectors-sample.json'))} err={e}")
out.append(f"SITE replay-log={open(p('site','replay-log.txt'), encoding='utf-8').read().strip()[-300:]}")
out.append(f"SITE wasm sha256={sha256_file(p('site','msf.wasm'))} bytes={os.path.getsize(p('site','msf.wasm'))}")
# site index buttons/labels for "what to click"
idx = open(p("site","index.html"), encoding="utf-8").read()
labels = re.findall(r"<button[^>]*>(.*?)</button>", idx, re.S)
labels = [re.sub(r"<[^>]+>"," ",x).strip() for x in labels]
heads = re.findall(r"<h[12][^>]*>(.*?)</h[12]>", idx, re.S)
heads = [re.sub(r"<[^>]+>"," ",x).strip() for x in heads]
out.append(f"SITE buttons={labels}")
out.append(f"SITE headings={heads}")
# examples expected
exp = open(p("examples","host","expected.txt"), encoding="utf-8").read().strip().splitlines()
out.append(f"EXAMPLE expected_lines={len(exp)} last={exp[-1]} sha256={sha256_file(p('examples','host','expected.txt'))}")
# audit bundle manifest count
man = [ln for ln in open(p("audit-bundle","MANIFEST.sha256"), encoding="utf-8") if ln.strip()]
out.append(f"AUDIT manifest_entries={len(man)} sha256={sha256_file(p('audit-bundle','MANIFEST.sha256'))}")
# header declarations count (rough: msf_ fns) - not used as instantiation count, cross-check only
hdr = open(p("include","muse_softfloat.h"), encoding="utf-8").read()
out.append(f"HEADER msf16/32/64 decl hits={len(re.findall(r'msf_(?:f16|f32|f64)_', hdr))}")

# MP4 probe: mvhd duration + tkhd width/height + audio track presence (soun handler)
def probe_mp4(path):
    data = open(path, "rb").read()
    res = {"bytes": len(data), "sha256": sha256_file(path)}
    i = data.find(b"mvhd")
    if i >= 0:
        ver = data[i+4]
        if ver == 1:
            timescale, duration = struct.unpack(">IQ", data[i+4+20:i+4+32])
        else:
            timescale, duration = struct.unpack(">II", data[i+4+12:i+4+20])
        res["timescale"] = timescale; res["duration_units"] = duration
        res["duration_s"] = duration / timescale if timescale else None
    res["has_soun"] = b"soun" in data
    res["has_mp4a"] = b"mp4a" in data
    # tkhd width/height: last 8 bytes of tkhd box (fixed 16.16)
    dims = []
    start = 0
    while True:
        j = data.find(b"tkhd", start)
        if j < 0: break
        size = struct.unpack(">I", data[j-4:j])[0]
        if 0 < size < 10000:
            w, h = struct.unpack(">II", data[j-4+size-8:j-4+size])
            dims.append((w >> 16, h >> 16))
        start = j + 4
    res["tkhd_dims"] = dims
    return res
for name in ["assembly_v5.mp4", "final.mp4"]:
    out.append(f"VIDEO {name} {probe_mp4(p('video','out',name))}")
print("\n".join(out))
