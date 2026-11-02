"""Host/Pico mirror + hygiene checks (scratch only)."""
import re
import sys

ROOT = "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-examples"
host = open(ROOT + "/examples/host/main.c", encoding="utf-8").read()
pico = open(ROOT + "/examples/pico/main.c", encoding="utf-8").read()

def region(text):
    start = text.index("Input operands as interchange")
    end = text.index('printf("EXAMPLE FAIL')
    return text[start:end]

def seq(text, pat):
    return re.findall(pat, text)

rh, rp = region(host), region(pico)
checks = {
    "string literals": seq(rh, r'"[^"\n]*"') == seq(rp, r'"[^"\n]*"'),
    "hex constants": seq(rh, r"0x[0-9a-fA-F]+") == seq(rp, r"0x[0-9a-fA-F]+"),
    "msf identifiers": seq(rh, r"\bmsf[0-9]*_[a-z_0-9]+") == seq(rp, r"\bmsf[0-9]*_[a-z_0-9]+"),
    "MSF_ constants": seq(rh, r"\bMSF_[A-Z_]+") == seq(rp, r"\bMSF_[A-Z_]+"),
}
for k, v in checks.items():
    print(f"mirror {k}: {'MATCH' if v else 'DIFFER'}")
print("host literals:", len(seq(rh, r'"[^"\n]*"')),
      "hex:", len(seq(rh, r"0x[0-9a-fA-F]+")),
      "msf ids:", len(seq(rh, r"\bmsf[0-9]*_[a-z_0-9]+")))

# no hardware arithmetic type words in either example source
for name, text in [("host", host), ("pico", pico)]:
    bad = re.findall(r"\bfloat\b|\bdouble\b", text)
    print(f"type scan {name}: {'clean' if not bad else bad}")

# LF hygiene for every new/edited text file
files = ["examples/host/main.c", "examples/host/build.sh",
         "examples/host/expected.txt", "examples/pico/main.c",
         "examples/pico/CMakeLists.txt", "examples/pico/run_example.sh",
         "examples/README.md", ".github/workflows/ci.yml"]
ok = True
for f in files:
    b = open(ROOT + "/" + f, "rb").read()
    good = b"\r" not in b and b.endswith(b"\n")
    ok = ok and good
    print(f"LF {f}: {'ok' if good else 'BAD'} ({len(b)} bytes)")

# README embedded output must equal expected.txt
exp = open(ROOT + "/examples/host/expected.txt", encoding="utf-8").read()
readme = open(ROOT + "/examples/README.md", encoding="utf-8").read()
print("README embeds expected.txt verbatim:", exp.strip() in readme)

try:
    import yaml
    doc = yaml.safe_load(open(ROOT + "/.github/workflows/ci.yml", encoding="utf-8"))
    print("ci.yml jobs:", sorted(doc["jobs"].keys()))
except ImportError:
    print("ci.yml: pyyaml unavailable in venv (structural check only)")

sys.exit(0 if all(checks.values()) and ok else 1)
