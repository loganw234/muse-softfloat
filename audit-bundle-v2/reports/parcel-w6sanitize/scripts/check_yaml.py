import sys
sys.path.insert(0, r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6sanitize\pylibs")
import yaml
d = yaml.safe_load(open(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-sanitize\.github\workflows\ci.yml", encoding="utf-8"))
print("jobs:", sorted(d["jobs"]))
s = d["jobs"]["sanitize"]
print("sanitize runs-on:", s["runs-on"], "timeout:", s["timeout-minutes"])
for st in s["steps"]:
    print(" step:", st.get("name"), "|", st.get("uses", st.get("run", "")).split("\n")[0])
# additive check: smoke/standard jobs keep their gate commands
print("smoke run:", d["jobs"]["smoke"]["steps"][3]["run"])
print("standard run:", d["jobs"]["standard"]["steps"][3]["run"])
