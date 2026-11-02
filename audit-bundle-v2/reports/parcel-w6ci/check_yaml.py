import pathlib
import sys

root = pathlib.Path(__file__).resolve().parents[2]
paths = [
    root / "worktrees/w6-ci/.github/workflows/ci.yml",
    root / "worktrees/w6-ci/tools/run.sh",
    root / "scratch/parcel-w6ci/run-gate.sh",
]
for p in paths:
    data = p.read_bytes()
    print(p.name, "bytes", len(data), "CRLF", data.count(b"\r\n"), "LF", data.count(b"\n"))

try:
    import yaml
except ImportError:
    print("PyYAML: NOT INSTALLED")
    sys.exit(3)
print("PyYAML:", yaml.__version__)
doc = yaml.safe_load(paths[0].read_text(encoding="utf-8"))
print("top-level keys:", sorted(str(k) for k in doc))
on = doc.get("on", doc.get(True))  # YAML 1.1 reads bare `on` as True
print("triggers:", sorted(on))
for job, spec in doc["jobs"].items():
    runs = [s["run"] for s in spec["steps"] if "run" in s]
    uses = [s["uses"] for s in spec["steps"] if "uses" in s]
    print("job", job, "runs-on", spec["runs-on"], "timeout", spec["timeout-minutes"])
    print("  uses:", uses)
    for r in runs:
        print("  run:", " // ".join(r.strip().splitlines()))
print("YAML parse: OK")
