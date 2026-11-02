import sys
try:
    import yaml
except ImportError:
    print("NOYAML")
    sys.exit(3)
doc = yaml.safe_load(open("C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-examples/.github/workflows/ci.yml", encoding="utf-8"))
print("jobs:", sorted(doc["jobs"].keys()))
job = doc["jobs"]["example-host"]
print("runs-on:", job["runs-on"])
print("steps:", [s.get("name", "?") for s in job["steps"]])
