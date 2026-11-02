import csv, pathlib
root = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w2-xf")
def read_tsv(p):
    lines=[l for l in open(p, encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))
cov=read_tsv(root/"docs/COVERAGE.tsv")
w2=[r["name"] for r in cov if r["wave"]=="2" and (r["name"].startswith("msf32_") or r["name"].startswith("msf64_"))]
hdr_lines=(root/"include/muse_softfloat.h").read_text(encoding="utf-8").splitlines()
for n in w2:
    hits=[l.strip() for l in hdr_lines if (n+"(") in l]
    print(n, "=>", hits[0] if hits else "NOT FOUND")
print("\n--- dispatch snippets ---")
disp_lines=(root/"tests/msf_dispatch.h").read_text(encoding="utf-8").splitlines()
for n in ["msf32_add_f16_f64","msf64_fma_f16_f32_f64","msf32_compare_quiet_equal_f16","msf64_compare_quiet_equal_f16","msf32_from_f16","msf64_sqrt_f16","msf32_add_f64_f64"]:
    for i,l in enumerate(disp_lines):
        if n in l:
            print(f"-- {n} at line {i+1}")
            for j in range(max(0,i-2), min(len(disp_lines), i+3)):
                print("   ", disp_lines[j])
            break
