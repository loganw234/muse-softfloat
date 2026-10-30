import collections, hashlib, pathlib, subprocess, sys
cov = pathlib.Path("muse-softfloat/docs/COVERAGE.tsv").read_text().splitlines()
rows = [l.split("\t") for l in cov if l and not l.startswith("#")]
hdr, rows = rows[0], rows[1:]
i = {k: hdr.index(k) for k in ("std_name", "authority", "wave", "status")}
print("rows", len(rows))
print("families", len(set(r[i["std_name"]] for r in rows)))
print("by authority", dict(collections.Counter(r[i["authority"]] for r in rows)))
print("by wave", dict(collections.Counter(r[i["wave"]] for r in rows)))
print("unconfirmed", sum(1 for r in rows if r[i["authority"]] == "unconfirmed"))
expect = {"addition": 27, "fusedMultiplyAdd": 81, "squareRoot": 9,
          "convertFromInt": 24, "convertFormat": 9, "compareQuietEqual": 9,
          "convertToIntegerTiesToEven": 24, "totalOrder": 3, "copy": 3,
          "class": 3, "is754version2019": 4, "lowerFlags": 1,
          "convertFromDecimalCharacter": 3, "scaleB": 3, "logB": 3}
cnt = collections.Counter(r[i["std_name"]] for r in rows)
for k, v in expect.items():
    assert cnt[k] == v, (k, cnt[k], v)
tot_int = sum(v for k, v in cnt.items() if k.startswith("convertToInteger"))
print("to_int total", tot_int); assert tot_int == 240
print("compares total", sum(v for k, v in cnt.items() if k.startswith("compare")))
# byte-stability: regenerate to temp and compare hashes
files = ["include/muse_softfloat.h", "src/msf_formats.h",
         "tests/msf_dispatch.h", "docs/COVERAGE.tsv"]
before = {f: hashlib.sha256(pathlib.Path("muse-softfloat", f).read_bytes()).hexdigest() for f in files}
subprocess.run([sys.executable, "muse-softfloat/tools/gen_tables.py",
                "scratch/lead/gen-check"], check=True, capture_output=True)
for f in files:
    h = hashlib.sha256(pathlib.Path("scratch/lead/gen-check", f).read_bytes()).hexdigest()
    assert h == before[f], f
print("regeneration byte-identical: OK")
# spot signatures
h = pathlib.Path("muse-softfloat/include/muse_softfloat.h").read_text()
for probe in ["msf64_add(msf64_t a, msf64_t b, msf_rounding_t rm, msf_flags_t *flags);",
              "msf32_add_f64_f64(msf64_t a, msf64_t b, msf_rounding_t rm, msf_flags_t *flags);",
              "msf64_fma_f32_f32_f64(msf32_t a, msf32_t b, msf64_t c, msf_rounding_t rm, msf_flags_t *flags);",
              "int64_t msf32_to_i64_ties_to_away(msf32_t a, msf_flags_t *flags);",
              "msf64_t msf16_log_b(msf16_t a, msf_flags_t *flags);",
              "int msf_test_saved_flags(msf_saved_flags_t saved, msf_flags_t group);",
              "msf_class_t msf64_class(msf64_t a);"]:
    assert probe in h, probe
for banned in ["float msf", "double msf", "_from_float"]:
    assert banned not in h, banned
print("signature probes: OK")
print(pathlib.Path("muse-softfloat/src/msf_formats.h").read_text()[:800])
