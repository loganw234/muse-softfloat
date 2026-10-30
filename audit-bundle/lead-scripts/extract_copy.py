import ast, sys
sys.stdout = open(r"scratch\lead\assembly\copy_inventory.txt", "w", encoding="utf-8")
files = {
 "intro/outro v2": r"scratch\study-video-intro\render_v2.py",
 "idea": r"scratch\study-video-idea\render_idea.py",
 "why2": r"scratch\study-video-why\render_why2.py",
 "git v4": r"scratch\study-video-gitvisual\render_gitvisual4.py",
}
for label, path in files.items():
    tree = ast.parse(open(path, encoding="utf-8").read())
    seen = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value.strip()
            if len(s) >= 8 and any(c.isalpha() for c in s) and " " in s:
                if s not in seen:
                    seen.append(s)
    print(f"===== {label} ({path}) {len(seen)} strings")
    for s in seen:
        w = len(s.split())
        print(f"[{w:3d}w] {s!r}")
    print()
