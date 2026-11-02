"""One still per new popup card at mid-dwell (card fully up, alpha=1)."""
import sys
from pathlib import Path

sys.path.insert(0, "video/segments")
import gitvisual as g

g.assign_lanes()
g.all_lane_pts()
OUT = Path("C:/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6popups/stills")
OUT.mkdir(parents=True, exist_ok=True)
for i, (title, _lines) in enumerate(g.POPUP5):
    t = g.ARRIVALS[i] + g.POPUP_DWELL[i] / 2.0
    p = OUT / ("card%d_%s_t%.2f.png" % (i, title, t))
    g.frame_at(t).save(p)
    print("still t=%.2fs -> %s" % (t, p))
