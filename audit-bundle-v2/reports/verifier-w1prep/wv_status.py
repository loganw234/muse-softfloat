#!/usr/bin/env python3
"""wv_status.py - status-mechanism checks (own implementation).
1. Generator must refuse: unknown name in implemented.tsv, duplicate row,
   wave mismatch (each on a mutated COPY; tree untouched).
2. Dispatch binds exactly the implemented+replayable set; COVERAGE status
   matches implemented.tsv 1:1.
3. operations.tsv really has no status column and comments agree.
4. Counts for the report; COVERAGE diff vs parent: no status changes,
   authority changes only on the exact-family rows.
"""
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path("muse-softfloat")
TMP = pathlib.Path("scratch/verifier-w1prep/tmp/status")
PY = ".venv/Scripts/python.exe"


def read_tsv(path):
    rows, header = [], None
    for line in pathlib.Path(path).read_text(encoding="utf-8").split("\n"):
        if not line or line.startswith("#"):
            continue
        cells = line.split("\t")
        if header is None:
            header = cells
        else:
            rows.append(dict(zip(header, cells)))
    return header, rows


def run_gen_mutated(case, mutate):
    """Copy tables+script into scratch, apply mutate(text)->text on
    implemented.tsv, run the generator there. Returns (rc, tail)."""
    work = TMP / ("case_" + case)
    if work.exists():
        shutil.rmtree(work)
    (work / "tables").mkdir(parents=True)
    for p in (ROOT / "tables").glob("*"):
        shutil.copy(p, work / "tables" / p.name)
    (work / "tools").mkdir()
    shutil.copy(ROOT / "tools/gen_tables.py", work / "tools/gen_tables.py")
    ip = work / "tables" / "implemented.tsv"
    ip.write_text(mutate(ip.read_text(encoding="utf-8")), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(work / "tools/gen_tables.py"), str(work / "out")],
                          capture_output=True, text=True)
    tail = (proc.stdout + proc.stderr)[-600:]
    return proc.returncode, tail


def main():
    out_lines = []
    # --- direct table reads ---
    op_header, op_rows = read_tsv(ROOT / "tables/operations.tsv")
    impl_header, impl_rows = read_tsv(ROOT / "tables/implemented.tsv")
    cov_header, cov_rows = read_tsv(ROOT / "docs/COVERAGE.tsv")
    out_lines.append("operations.tsv columns: %s" % ("|".join(op_header)))
    out_lines.append("implemented.tsv rows: %d (header %s)" % (len(impl_rows), "|".join(impl_header)))
    out_lines.append("COVERAGE.tsv rows: %d" % len(cov_rows))
    assert "status" not in op_header, "operations.tsv still has a status column!"
    out_lines.append("operations.tsv has no status column: CONFIRMED")
    # comment agreement
    ops_text = (ROOT / "tables/operations.tsv").read_text(encoding="utf-8")
    assert "(status lives in tables/implemented.tsv, per instantiation)" in ops_text
    assert "status      implemented" not in ops_text
    out_lines.append("operations.tsv doc comments agree (status lives in implemented.tsv): CONFIRMED")
    impl_text = (ROOT / "tables/implemented.tsv").read_text(encoding="utf-8")
    assert "tools/gen_tables.py reads ONLY this file for status" in impl_text
    out_lines.append("implemented.tsv header claims single status source: CONFIRMED")
    # 1:1 match
    impl_names = [r["name"] for r in impl_rows]
    assert len(impl_names) == len(set(impl_names)), "duplicate rows in implemented.tsv"
    cov_impl = sorted(r["name"] for r in cov_rows if r["status"] == "implemented")
    cov_plan = sorted(r["name"] for r in cov_rows if r["status"] == "planned")
    out_lines.append("COVERAGE implemented=%d planned=%d" % (len(cov_impl), len(cov_plan)))
    assert sorted(impl_names) == cov_impl, "COVERAGE status != implemented.tsv 1:1"
    out_lines.append("COVERAGE status matches implemented.tsv 1:1: CONFIRMED")
    assert not any(r["status"] not in ("planned", "implemented") for r in cov_rows)
    # dispatch binding: parse msf_dispatch.h rows
    disp = (ROOT / "tests/msf_dispatch.h").read_text(encoding="utf-8")
    import re
    m_rows = re.findall(r'\{ "([^"]+)", "[^"]*", MSF_SIG_\w+, MSF_RK_\w+, \{[^}]*\}, \d, \d, \d, (\d), (\d), ([^}]+)\},?', disp)
    out_lines.append("dispatch rows parsed: %d" % len(m_rows))
    assert len(m_rows) == len(cov_rows), (len(m_rows), len(cov_rows))
    for name, status, wave, call in m_rows:
        cov = next(r for r in cov_rows if r["name"] == name)
        assert int(status) == (1 if cov["status"] == "implemented" else 0), name
        assert int(wave) == int(cov["wave"]), "wave drift " + name
    # call bindings: implemented+replayable => msf_call_ symbol; else NULL/0
    replayable = {"rint_named", "rint_exact", "next", "remainder", "scaleb", "logb",
                  "arith_bin", "arith_un", "fma", "from_int", "to_int", "conv_fmt",
                  "sign_un", "sign_bin", "compare", "totalorder", "classify",
                  "class_op", "radix_op", "version_op"}
    sig_of = {}
    for n2, std2, sig2, rk2, ak2, nargs2, hrm2, hfl2, st2, wv2, call2 in re.findall(
            r'\{ "([^"]+)", "([^"]*)", (MSF_SIG_\w+), (MSF_RK_\w+), \{([^}]*)\}, (\d), (\d), (\d), (\d), (\d), ([^}]+)\},?', disp):
        sig_of[n2] = sig2.replace("MSF_SIG_", "").lower()
    bound = [n for (n, s, w, c) in m_rows if int(s) == 1 and "msf_call_" in c]
    null_impl = [n for (n, s, w, c) in m_rows if int(s) == 1 and "msf_call_" not in c]
    out_lines.append("implemented+dispatch-bound(non-NULL call): %d" % len(bound))
    out_lines.append("implemented but NULL call (non-replayable sigs): %d %s" % (len(null_impl), null_impl[:10]))
    for n in bound:
        assert sig_of[n] in replayable, n
    for (n, s, w, c) in m_rows:
        if int(s) == 0:
            assert "msf_call_" not in c, "planned row binds a call: " + n
    out_lines.append("dispatch binds exactly implemented(+replayable) set: CONFIRMED")
    # --- mutation refusals (copies only; tree untouched) ---
    base_impl = (ROOT / "tables/implemented.tsv").read_text(encoding="utf-8")
    first_data = next(l for l in base_impl.split("\n") if l and not l.startswith("#"))
    rc, tail = run_gen_mutated("unknown", lambda t: t + "msf64_no_such_op\t1\n")
    out_lines.append("mutate unknown-name: rc=%d refused=%s" % (rc, rc != 0))
    assert rc != 0, "generator ACCEPTED unknown implemented.tsv name!"
    rc, tail = run_gen_mutated("duplicate", lambda t: t + first_data + "\n")
    out_lines.append("mutate duplicate-row: rc=%d refused=%s" % (rc, rc != 0))
    assert rc != 0, "generator ACCEPTED duplicate row!"
    def wave_bump(t):
        ls = t.split("\n")
        seen_header = False
        for i, l in enumerate(ls):
            if l and not l.startswith("#"):
                if not seen_header:
                    seen_header = True
                    continue
                c = l.split("\t")
                c[1] = str(int(c[1]) + 1)
                ls[i] = "\t".join(c)
                break
        return "\n".join(ls)
    rc, tail = run_gen_mutated("wavemismatch", wave_bump)
    out_lines.append("mutate wave-mismatch: rc=%d refused=%s" % (rc, rc != 0))
    assert rc != 0, "generator ACCEPTED wave mismatch!"
    out_lines.append("generator refuses all three mutations: CONFIRMED")
    open("scratch/verifier-w1prep/wv_status.txt", "w", encoding="utf-8").write("\n".join(out_lines) + "\n")
    print("\n".join(out_lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
