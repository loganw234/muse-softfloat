import json

rows = [
    dict(plant=1, shape="guard no longer trips on inexact augmented pairs",
         note="F2: mask omits INEXACT vs design entry + .c comment; inert today (msf_aug co-raises), isolated by reading + GUARD=0 mutant"),
    dict(plant=2, shape="product head replaced by its tail in aug_prod",
         note="F1: {tail,tail} expansions; 426 decided-wrong vs independent Fraction discriminant oracle"),
    dict(plant=3, shape="product head and tail swapped at the call site",
         note="F1: aug_prod called with &e,&p; isolated by reading + 426-row full-stream differential"),
    dict(plant=4, shape="msf_aug.c dropped from the interval host build list",
         note="F4: exact-spelled interval_run.sh gcc exits 1, undefined augmented_add/mul; ARM -c clean"),
    dict(plant=5, shape="header states the opposite of the P1=R2 guard semantics",
         note="F3: header 'trips the guard' vs msf_aug.c P1=R2 exact-tiny-no-flag and the design entry"),
]
key = "fb244b52150ebedabbfc641324f47c587ba794ce97670bdda05aaf76d6b84b51"
path = "muse-softfloat/docs/metrics/plants.jsonl"
before = open(path, "rb").read()
assert b"verifier-w6augint" not in before
with open(path, "ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    for r in rows:
        r.update(wave="wave6", verifier="verifier-w6augint",
                 work="Wave 6: interval stage 3 consumes augmented pairs",
                 key_sha256=key, grade="caught", graded_by="lead",
                 checked_by="lead-merge")
        ordered = {k: r[k] for k in ("wave", "verifier", "work", "key_sha256",
                                      "plant", "shape", "grade", "graded_by",
                                      "checked_by", "note")}
        out.write((json.dumps(ordered) + "\n").encode("utf-8"))
after = open(path, "rb").read()
assert after[:len(before)] == before
allrows = [json.loads(x) for x in after.decode("utf-8").splitlines() if x.strip()]
print("plants total=%d caught=%d" % (
    len(allrows), sum(1 for r in allrows if r["grade"] == "caught")))
