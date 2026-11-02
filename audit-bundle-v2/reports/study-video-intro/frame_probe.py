"""Render single frames from the new modules for layout eyeball."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "study-video-idea"))
sys.path.insert(0, str(HERE.parent / "study-video-why"))
import render_v3 as V3  # noqa: E402
import render_idea2 as ID2  # noqa: E402
import render_why3 as W3  # noqa: E402

OUT = HERE / "frameprobe"
OUT.mkdir(exist_ok=True)
for t in (4.4, 9.4, 14.4, 18.4, 21.4):
    ID2.frame(t).save(OUT / f"idea2_{t}.png")
    print("idea2", t)
for t in (3.4, 7.9, 13.4, 18.4, 23.9, 27.9, 32.4):
    W3.frame(t).save(OUT / f"why3_{t}.png")
    print("why3", t)
img, _ = V3.draw_intro_scene(4.4, len(V3.INTRO_MSG), False)
img.save(OUT / "intro_plate.png")
print("intro plate", img.size)
img, _ = V3.draw_outro_scene(8.4, False, True, 10**6)
panels = V3.make_panel_layers()
for j, lay in enumerate(panels):
    img = V3.paste_panel(img, lay, 1.0, j < 3)
img.convert("RGB").save(OUT / "outro_final.png")
print("outro final done")
per = V3.measure_period()
print("period centroid", per["raster_centroid"], "ink", per["ink"],
      "n", per["n_dot_components"])
print("dots", V3.measure_dots())
