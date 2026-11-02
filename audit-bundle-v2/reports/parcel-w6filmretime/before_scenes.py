import sys
from pathlib import Path
SEG = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments")
sys.path.insert(0, str(SEG))
import idea, why
for name, mod in (("idea", idea), ("why", why)):
    print(name, "DUR", mod.DUR)
    seen = []
    for s, a, b, lines in mod.BLOCKS:
        if s not in seen:
            seen.append(s)
    print(" scenes:", seen)
    for row in mod.BLOCKS:
        print(" ", row)
