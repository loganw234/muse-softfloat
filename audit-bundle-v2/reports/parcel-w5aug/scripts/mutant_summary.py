import pathlib
import sys

out = pathlib.Path(sys.argv[1])
names = ["control", "te-head", "zero-tail-sign", "swap-pair",
         "jam-window", "p1-opposite", "pack-leak", "corrupt"]
lines = []
bad = 0
for name in names:
    log = out / ("verify-%s.log" % name)
    text = log.read_text(encoding="utf-8", errors="replace").splitlines()
    fails = [l for l in text if l.startswith("FAIL")]
    verdict = [l for l in text if l.startswith("VERDICT")]
    total = [l for l in text if l.startswith("total ")]
    lines.append("%s fail_lines=%d %s %s" % (
        name, len(fails), verdict[0] if verdict else "no-verdict",
        total[0] if total else ""))
    for f in fails[:2]:
        lines.append("  " + f)
    if name == "control":
        if fails or not verdict or verdict[0] != "VERDICT: PASS":
            bad = 1
            lines.append("  CONTROL NOT GREEN")
    else:
        if not fails or not verdict or verdict[0] != "VERDICT: FAIL":
            bad = 1
            lines.append("  NOT REFUSED")
text = "\n".join(lines) + "\n"
(out / "summary2.txt").write_bytes(text.encode())
print(text)
sys.exit(bad)
