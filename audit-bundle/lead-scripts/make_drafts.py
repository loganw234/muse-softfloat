import json, pathlib, subprocess
def tip(wt):
    return subprocess.run(["git", "-C", wt, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
f32 = {
  "real_tip": tip("worktrees/w1-f32"),
  "plants": [
    {"file": "src/msf32.c",
     "old": "    if (b.cls == MSF_VC_ZERO) {\n        *flags |= MSF_FLAG_DIVISION_BY_ZERO;\n        return INF32(sign);",
     "new": "    if (b.cls == MSF_VC_ZERO) {\n        return INF32(sign);",
     "shape": "a mandatory exception flag dropped on one path"},
    {"file": "src/msf32.c",
     "old": "    if (b.cls == MSF_VC_INFINITY) {\n        return INF32(effb);",
     "new": "    if (b.cls == MSF_VC_INFINITY) {\n        return INF32(b.sign);",
     "shape": "the effective (negated) sign ignored on an infinity fast path"},
    {"file": "src/msf32.c",
     "old": "a.exp - b.exp + (la - lb) - 63",
     "new": "a.exp - b.exp + (la - lb) - 62",
     "shape": "exponent bookkeeping off by one"},
    {"file": "tests/vectors/arith-f32.vec",
     "old": "msf32_add te 0 80000001 -> 80000001 00",
     "new": "msf32_add te 0 80000001 -> 80000000 00",
     "shape": "a committed vector expectation corrupted"},
    {"file": "tests/gen_vectors_f32.py",
     "old": "-(1 << 24), (1 << 31) - 1, -(1 << 31), (1 << 32) - 1,",
     "new": "-(1 << 24), (1 << 31) - 2, -(1 << 31), (1 << 32) - 1,",
     "shape": "a boundary value quietly weakened in the generator pool"},
  ],
}
f64 = {
  "real_tip": tip("worktrees/w1-f64"),
  "plants": [
    {"file": "src/msf64.c",
     "old": "    if (b.cls == MSF_VC_ZERO) {\n        *flags |= MSF_FLAG_DIVISION_BY_ZERO;\n        return inf_bits(sign);",
     "new": "    if (b.cls == MSF_VC_ZERO) {\n        return inf_bits(sign);",
     "shape": "a mandatory exception flag dropped on one path"},
    {"file": "src/msf64.c",
     "old": "int s = (s1 == s2) ? s1 : (rm == MSF_IROUND_TOWARD_NEGATIVE);",
     "new": "int s = (s1 == s2) ? s1 : (rm == MSF_IROUND_TOWARD_POSITIVE);",
     "shape": "the signed-zero rule inverted"},
    {"file": "src/msf64.c",
     "old": "|| (prod_inf && c.cls == MSF_VC_INFINITY && c.sign != psign);",
     "new": "|| (prod_inf && c.cls == MSF_VC_INFINITY && c.sign == psign);",
     "shape": "an opposite-infinities invalid test inverted"},
    {"file": "tests/vectors/arith-f64.vec",
     "old": "msf64_div_f32_f32 te 0 80000000 -> 7ff8000000000000 01",
     "new": "msf64_div_f32_f32 te 0 80000000 -> 7ff8000000000000 00",
     "shape": "a committed vector flag expectation corrupted"},
    {"file": "tests/gen_vectors_f64.py",
     "old": "F_UNF = 0x08",
     "new": "F_UNF = 0x04",
     "shape": "a flag-bit constant wrong in the reference generator"},
  ],
}
k = pathlib.Path("scratch/lead/keys")
k.mkdir(parents=True, exist_ok=True)
for name, d in (("w1-f32-draft.json", f32), ("w1-f64-draft.json", f64)):
    (k / name).write_bytes((json.dumps(d, indent=2) + "\n").encode())
    print(name, d["real_tip"])
