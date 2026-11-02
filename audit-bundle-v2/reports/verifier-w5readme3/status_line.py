import json
d = json.load(open("scratch/verifier-w5readme3/servesite/data.json"))
def fi(n):
    return format(n, ",d")
status = (
    "Status at %s: %s of %s instantiations implemented and gated \u00b7 "
    "%s committed test vectors \u00b7 planted-copy score %s of %s"
    % (d["base"], fi(d["instantiations"]["implemented"]),
       fi(d["instantiations"]["total"]), fi(d["vectors"]["total"]),
       d["plants"]["caught"], d["plants"]["total"]))
print(status)
print("numbers rows:")
print("  runnable: %s of %s" % (fi(d["sample"]["ops_runnable"]), fi(d["sample"]["ops_total"])))
print("  pair excluded: %s" % fi(d["sample"]["ops_pair_excluded"]))
print("  nonhex excluded: %s" % fi(d["sample"]["ops_nonhex_excluded"]))
print("  822 + pair + nonhex ==", 822 + d["sample"]["ops_pair_excluded"] + d["sample"]["ops_nonhex_excluded"])
print("  sample vectors:", d["sample"]["vectors"], "ops covered:", d["sample"]["ops_covered"])
print("  by_wave:", [(r["wave"], r["caught"], r["total"]) for r in d["plants"]["by_wave"]])
print("  by_wave sums:", sum(r["caught"] for r in d["plants"]["by_wave"]), sum(r["total"] for r in d["plants"]["by_wave"]))
