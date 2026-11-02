import pathlib, collections
for f in ("alg-f16.vec", "alg-f32.vec", "alg-f64.vec"):
    path = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w5-alg2\tests\vectors") / f
    groups = collections.defaultdict(dict)
    tags = {}
    for ln in path.read_text().splitlines():
        t = ln.split()
        if len(t) == 8 and "_hypot" in t[0]:
            groups[(t[2], t[3])][t[1]] = (t[5], t[6])
            tags[(t[2], t[3])] = t[7]
    diff = [(k, g) for k, g in groups.items() if g.get("te") != g.get("ta")]
    print(f"{f}: hypot pairs={len(groups)} te!=ta pairs={len(diff)}")
    for k, g in diff[:4]:
        print(f"  {k} tag={tags[k]} te={g['te']} ta={g['ta']} tz={g['tz']} tp={g['tp']}")
