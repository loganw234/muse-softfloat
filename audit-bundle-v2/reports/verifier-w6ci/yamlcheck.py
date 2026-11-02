import sys
try:
    import yaml
except ImportError:
    print("NO-PYYAML")
    sys.exit(2)
d = yaml.safe_load(open("/mnt/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify6-ci/.github/workflows/ci.yml"))
print("YAML-OK")
for name, job in d["jobs"].items():
    print("JOB", name, "runs-on=", job.get("runs-on"), "timeout=", job.get("timeout-minutes"))
    for s in job["steps"]:
        r = s.get("run", "")
        print("  STEP", s.get("name"), "|", r.replace("\n", " / ")[:150])
print("TRIGGERS", list(d.get("on", {}).keys()) if isinstance(d.get("on"), dict) else d.get("on"))
