#!/usr/bin/env python3
# 04_audit.py - wrapper-table audit: every new DEF/wrapper line's format
# indices against the instantiation name. Covers all 126 by reading.
import re
import sys

root = sys.argv[1]
F = {"FMT16": "f16", "MSF_FMT_F16": "f16",
     "FMT32": "f32", "MSF_FMT_F32": "f32",
     "FMT64": "f64", "MSF_FMT_F64": "f64"}


def bits(fmt):
    return {"f16": "msf16_t", "f32": "msf32_t", "f64": "msf64_t"}[fmt]


def audit(path, macros):
    src = open(path, encoding="utf-8").read()
    rows = []
    for m in macros:
        # DEF_X(name, T1, F1, T2, F2, ...) - capture all type/format pairs
        pat = re.compile(r"DEF_%s\(([^)]*)\)" % m)
        for mm in pat.finditer(src):
            toks = [t.strip() for t in mm.group(1).split(",")]
            rows.append((m, toks))
    return rows


prob = []
ok = 0
seen = {}
for path in (root + "/src/msf32.c", root + "/src/msf64.c"):
    fmt_first = "msf64" in path  # msf64 macros take (FMT, type) pairs
    for (m, toks) in audit(path, ["ADD", "SUB", "MUL", "DIV", "FMA", "SQRT",
                                  "CMP_F16"]):
        name = toks[0]
        if m == "CMP_F16":
            if toks[0] in ("PRED", "SUF"):
                continue  # macro definition, not an instantiation
            dest = "32" if "msf32" in path else "64"
            name = "msf%s_compare_%s_f16" % (dest, toks[0])
        elif "_f16" not in name and not name.endswith("_f16"):
            continue
        raw = [(toks[i], toks[i + 1]) for i in range(1, len(toks) - 1, 2)]
        pairs = [(b, a) if fmt_first else (a, b) for (a, b) in raw]
        # expected formats from the name suffix
        if m == "CMP_F16":
            # SIG flag is last token
            sig = toks[-1]
            want_sig = "1" if "signaling" in name else "0"
            if sig != want_sig:
                prob.append("%s: SIG=%s want %s" % (name, sig, want_sig))
            else:
                ok += 1
            seen[name] = True
            continue
        core = name.split("msf32_")[1] if "msf32" in path else name.split("msf64_")[1]
        parts = core.split("_")
        fam = parts[0]
        if fam in ("add", "sub", "mul", "div"):
            exp = [parts[1], parts[2]]
        elif fam == "sqrt":
            exp = [parts[1]]
        elif fam == "fma":
            exp = [parts[1], parts[2], parts[3]]
        else:
            continue
        line_ok = True
        for (ty, fi), ef in zip(pairs, exp):
            af = F.get(fi, fi)
            if af != ef or bits(ef) != ty:
                prob.append("%s: slot type=%s fmt=%s, name wants %s/%s"
                            % (name, ty, af, ef, bits(ef)))
                line_ok = False
        if line_ok:
            ok += 1
        seen[name] = True

# hand-written wrappers: from_f16, sqrt_f16 where no DEF line covers them
for path, dest in ((root + "/src/msf32.c", "f32"), (root + "/src/msf64.c", "f64")):
    src = open(path, encoding="utf-8").read()
    for fn in ("from_f16", "sqrt_f16"):
        full = "msf%s_%s" % ("32" if dest == "f32" else "64", fn)
        if full in seen:
            continue
        m = re.search(r"%s\(.*?\)\s*\{([^}]*)\}" % full, src, re.S)
        body = m.group(1) if m else ""
        tag = "MSF_FMT_F16" if "msf64" in path else "FMT16"
        if tag in body:
            ok += 1
            seen[full] = True
        else:
            prob.append("%s %s: no %s in body: %r" % (path, fn, tag, body[:120]))

print("audited wrapper lines OK: %d, problems: %d, names seen: %d"
      % (ok, len(prob), len(seen)))
for p in prob:
    print("PROBLEM", p)

# cross-check the 126 names: coverage wave=2 msf32_/msf64_ vs seen
rows = [l.rstrip().split("\t") for l in
        open(root + "/docs/COVERAGE.tsv", encoding="utf-8")
        if l.strip() and not l.startswith("#")]
hdr = rows[0]
idx = {h: i for i, h in enumerate(hdr)}
names = set(r[idx["name"]] for r in rows[1:]
            if r[idx["wave"]] == "2" and (r[idx["name"]].startswith("msf32_")
                                          or r[idx["name"]].startswith("msf64_")))
print("coverage xf names:", len(names))
missing = sorted(names - set(seen))
print("names without audited wrapper line:", len(missing))
for m in missing:
    print("  MISSING", m)
