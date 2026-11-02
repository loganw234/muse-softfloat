import ctypes, json, sys, time, tracemalloc
from pathlib import Path
SEG = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments")
OUT = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6filmretime")
sys.path.insert(0, str(SEG))
import intro_outro as io
from PIL import Image

class PMC(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

def peak_mb():
    pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
    ctypes.windll.psapi.GetProcessMemoryInfo(
        ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
    return round(pmc.PeakWorkingSetSize / 1e6, 1), round(pmc.WorkingSetSize / 1e6, 1)

def find_u(target, final_w, plate, want_native):
    want = want_native * (plate.width / io.OW)
    best = (1e18, 0.0)
    for i in range(1001):
        u = i / 1000.0
        _c, cw = io.intro_cam(u, target, final_w, plate.width, plate.height)
        if abs(cw - want) < best[0]:
            best = (abs(cw - want), u)
    return best[1]

rows = []
for ss in (1, 2, 3):
    tracemalloc.start()
    t0 = time.time()
    with io.canvas(ss):
        period = io.measure_period()
        plate = period.pop("plate")
        ink = period["ink"]
        final_w = max(1.2, min(ink["w"], ink["h"] * 16 / 9) * 0.55)
        target = (period["raster_centroid"][0] + 0.5, period["raster_centroid"][1] + 0.5)
        clamp = io.clamp_check(target, final_w, False, plate.width, plate.height)
        t_plate = time.time() - t0
        stills = {}
        for want_native in (800, 400):
            u = find_u(target, final_w, plate, want_native)
            center, cw = io.intro_cam(u, target, final_w, plate.width, plate.height)
            img, used, box = io.camera(plate, center, cw, plate.width, plate.height, io.OW, io.OH)
            fn = OUT / f"ss{ss}_mid{want_native}.png"
            img.save(fn)
            # centre crop for text inspection (bubble sits near target)
            img.crop((640, 360, 1920, 1080)).save(OUT / f"ss{ss}_mid{want_native}_crop.png")
            stills[str(want_native)] = dict(u=round(u,3), crop_w_ss=round(cw,1),
                                            eff_upscale=round(io.OW / cw, 3), file=fn.name)
        # one outro pull-back scene at this SS (75 such frames in render)
        t1 = time.time()
        img_ss, _dots = io.draw_outro_scene(1.5, True, False, None)
        t_outro1 = time.time() - t1
        solid_w = Image.new("RGB", (io.W, io.H), io.WHITE)
        down_w, _c, _b = io.camera(solid_w, (io.W/2, io.H/2), io.W, io.W, io.H, io.OW, io.OH)
        solid_b = Image.new("RGB", (io.W, io.H), io.NEAR_BLACK)
        down_b, _c, _b = io.camera(solid_b, (io.W/2, io.H/2), io.W, io.W, io.H, io.OW, io.OH)
    cur, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    pk, ws = peak_mb()
    row = dict(ss=ss, internal=[io.OW*ss, io.OH*ss],
               raster_centroid=period["raster_centroid"],
               centroid_output_px=[round(period["raster_centroid"][0]/ss,2),
                                   round(period["raster_centroid"][1]/ss,2)],
               ink=period["ink"], final_crop_w=round(final_w,2),
               clamp_max_px_ss=round(clamp,3), clamp_max_px_out=round(clamp/ss,3),
               wall_plate_measure_s=round(t_plate,2), wall_outro_scene1_s=round(t_outro1,2),
               est_outro_pullback_75f_s=round(t_outro1*75,1),
               tracemalloc_peak_mb=round(peak/1e6,1),
               process_peak_ws_mb_cum=pk, process_ws_mb=ws,
               solid_white_down=list(down_w.getpixel((100,100))),
               solid_nearblack_down=list(down_b.getpixel((100,100))),
               stills=stills)
    rows.append(row); print(json.dumps(row), flush=True)
(OUT / "ss_probe.json").write_text(json.dumps(rows, indent=1))
print("done")
