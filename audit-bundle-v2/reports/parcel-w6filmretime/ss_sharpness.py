import numpy as np
from PIL import Image
from pathlib import Path
OUT = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6filmretime")
for want in (800, 400):
    ref = np.asarray(Image.open(OUT / f"ss3_mid{want}.png").convert("L")).astype(np.float64)
    for ss in (1, 2, 3):
        a = np.asarray(Image.open(OUT / f"ss{ss}_mid{want}.png").convert("L")).astype(np.float64)
        gx = np.diff(a, axis=1); gy = np.diff(a, axis=0)
        sharp = float((gx*gx).mean() + (gy*gy).mean())
        rmse = float(np.sqrt(((a-ref)**2).mean()))
        # text-edge zone only: high-gradient pixels of reference
        rgx = np.abs(np.diff(ref, axis=1, append=ref[:, -1:]))
        mask = rgx > 40
        rmse_edge = float(np.sqrt(((a-ref)[mask]**2).mean())) if mask.any() else 0.0
        print(f"mid{want} ss{ss}: grad_energy={sharp:.1f} rmse_vs_ss3={rmse:.2f} rmse_edge={rmse_edge:.2f} edge_px={int(mask.sum())}")
