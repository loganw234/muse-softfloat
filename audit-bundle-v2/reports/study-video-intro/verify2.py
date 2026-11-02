import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

H = Path("scratch/study-video-intro")


def stats(p):
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.int32)
    flat = a.reshape(-1, 3)
    dom = Counter(map(tuple, flat[::37].tolist())).most_common(1)[0]
    return dict(file=p.name, min=int(a.min()), max=int(a.max()),
                mean=[round(float(a[:, :, c].mean()), 2) for c in range(3)],
                dominant_sampled=dom,
                all_white=bool((a == 255).all()),
                frac_white=round(float((a.min(axis=2) == 255).mean()), 4),
                frac_min_ge_250=round(float((a.min(axis=2) >= 250).mean()), 4))


for p in [H / "stills2/intro/still_004.8s.png",
          H / "stills2/intro/still_004.5s.png",
          H / "stills2/intro/still_004.3s.png",
          H / "stills2/outro/still_000.0s.png"]:
    print(json.dumps(stats(p)))

v1 = (H / "outro_msg.txt").read_text()
v2 = (H / "outro_msg2.txt").read_text()
print("v1_msg_chars", len(v1.strip()), "v2_msg_chars", len(v2.strip()),
      "ratio", round(len(v2.strip()) / len(v1.strip()), 3))
print(json.dumps(json.loads((H / "measurements2.json").read_text())["smooth"]))
print(json.dumps(json.loads((H / "measurements2.json").read_text())["cam_samples"]))

# 2-suffix renames for the grabbed stills
for d in (H / "stills2/intro", H / "stills2/outro"):
    for p in sorted(d.glob("still_*.png")):
        q = p.with_name(p.name.replace("still_", "still2_"))
        if not q.exists():
            p.rename(q)
print("renamed stills to still2_*")
