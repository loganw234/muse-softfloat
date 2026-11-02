"""Assert first/last sampled stills are pure white (white-plane bookends)."""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
for name in ("still_000.2s.png", "still_015.9s.png"):
    im = Image.open(HERE / "stills" / name).convert("RGB")
    px = im.getdata()
    nonwhite = sum(1 for p in px if p != (255, 255, 255))
    print(name, im.size, "nonwhite_px =", nonwhite, "of", len(px))
