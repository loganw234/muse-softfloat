import re
from pathlib import Path
p = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments\intro_outro.py")
s = p.read_text(encoding="utf-8")

def sub(pat, rep, txt, flags=0):
    out, n = re.subn(pat, rep, txt, flags=flags)
    assert n == 1, (pat, n)
    return out

s = sub(r"import json\r?\n", "import contextlib\nimport json\nimport os\n", s)
s = sub(r"PANEL_T = \[3\.5, 4\.0, 4\.5, 5\.0, 5\.5, 6\.0\].*",
        "PANEL_T = [4.5, 5.5, 6.5, 7.5, 8.5, 9.5]  # wave6 dwell: 1.0 s spacing", s)
s = sub(r"INTRO_DUR, OUTRO_DUR = 7\.0, 8\.5", "INTRO_DUR, OUTRO_DUR = 7.0, 12.0", s)

canvas_code = '''
# ---- wave6 supersampling (phone-camera scenes only) ----
# The camera crops (intro dive plate, outro pull-back) are rendered
# on an SSx internal canvas and downscaled to the 2560x1440 output;
# all other frames render native. Chosen SS set from probe stills.
OW, OH = 2560, 1440
SS = int(os.environ.get("MSF_SS", "2"))


def _apply_scale(ss):
    global W, H, K, PHONE_I, PHONE_O, OUTRO_TYPING_TOP, FRAME_C, FRAME_CC
    W, H = OW * ss, OH * ss
    K = W / 1920.0
    PHONE_I = dict(x0=sc(690), x1=sc(1230), y0=sc(70), y1=sc(1010))
    PHONE_O = dict(x0=sc(880), x1=sc(1420), y0=sc(70), y1=sc(1010))
    OUTRO_TYPING_TOP = PHONE_O["y0"] + sc(310)
    FRAME_C = (W / 2 - 0.5, H / 2 - 0.5)
    FRAME_CC = (W / 2, H / 2)


@contextlib.contextmanager
def canvas(ss):
    saved = (W, H, K, dict(PHONE_I), dict(PHONE_O), OUTRO_TYPING_TOP,
             FRAME_C, FRAME_CC)
    _apply_scale(ss)
    try:
        yield
    finally:
        global W, H, K, PHONE_I, PHONE_O, OUTRO_TYPING_TOP, FRAME_C, FRAME_CC
        (W, H, K, PHONE_I, PHONE_O, OUTRO_TYPING_TOP,
         FRAME_C, FRAME_CC) = saved

'''
# fix: global statement must precede use in function; move into top
canvas_code = canvas_code.replace(
    "    saved = (W, H, K,", "    global W, H, K, PHONE_I, PHONE_O, OUTRO_TYPING_TOP, FRAME_C, FRAME_CC\n    saved = (W, H, K,")
canvas_code = canvas_code.replace(
    "        global W, H, K, PHONE_I, PHONE_O, OUTRO_TYPING_TOP, FRAME_C, FRAME_CC\n", "")
s = sub(r"(OUTRO_TYPING_TOP = PHONE_O\[\"y0\"\] \+ sc\(310\)\r?\n)", r"\1" + canvas_code, s)

new_camera = '''def camera(img, center, crop_w, src_w=None, src_h=None, out_w=None, out_h=None):
    src_w = img.width if src_w is None else src_w
    src_h = img.height if src_h is None else src_h
    out_w = OW if out_w is None else out_w
    out_h = OH if out_h is None else out_h
    crop_w = min(float(crop_w), float(src_w))
    crop_h = crop_w * src_h / src_w
    cx = min(max(center[0], crop_w / 2), src_w - crop_w / 2)
    cy = min(max(center[1], crop_h / 2), src_h - crop_h / 2)
    box = (max(0.0, cx - crop_w / 2), max(0.0, cy - crop_h / 2),
           min(float(src_w), cx + crop_w / 2), min(float(src_h), cy + crop_h / 2))
    filt = Image.LANCZOS if crop_w >= out_w else Image.BILINEAR
    return img.resize((out_w, out_h), filt, box=box), (cx, cy), box


def intro_cam(u, target, final_w, src_w=None, src_h=None):
    src_w = W if src_w is None else src_w
    src_h = H if src_h is None else src_h
    ce = smootherstep(u / CENTER_LEAD)
    center = (S.lerp(src_w / 2, target[0], ce),
              S.lerp(src_h / 2, target[1], ce))
    cw = math.exp(S.lerp(math.log(src_w), math.log(final_w), smootherstep(u)))
    return center, cw


def clamp_check(target, final_w, reverse, src_w=None, src_h=None, samples=401):
    src_w = W if src_w is None else src_w
    src_h = H if src_h is None else src_h
    worst = 0.0
    for i in range(samples):
        u = i / (samples - 1)
        cu = 1 - u if reverse else u
        center, cw = intro_cam(cu, target, final_w, src_w, src_h)
        ch = cw * src_h / src_w
        for c, lo, hi in ((center[0], cw / 2, src_w - cw / 2),
                          (center[1], ch / 2, src_h - ch / 2)):
            worst = max(worst, lo - c, c - hi, 0.0)
    return worst

'''
s = sub(r"def camera\(img, center, crop_w\):.*?(?=\r?\ndef encode_start)", new_camera, s, flags=re.S)

s = sub(r"want = 100 \* K", "want = 100 * (plate.width / 1920.0)", s)
s = sub(r"center, cw = intro_cam\(u, target, final_w\)",
        "center, cw = intro_cam(u, target, final_w, plate.width, plate.height)", s)
s = sub(r"img, used_c, _box = camera\(plate, center, cw\)",
        "img, used_c, _box = camera(plate, center, cw, plate.width, plate.height, OW, OH)", s)

new_outro = '''def render_outro(dots_target):
    """12.0 s: dark->dots, reverse pull-back to 2.5, reply1 2.5,
    reply2 typed 3.0-4.0, panel stages 4.5..9.5, hold to 12.0."""
    panels = make_panel_layers()
    n = int(OUTRO_DUR * FPS)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    full2_lines = wrap(tmp, REPLY_2, F("body", 24), sc(380))
    r1_lines = wrap(tmp, REPLY_1, F("body", 27), sc(380))
    assert len(full2_lines) == 1 and len(r1_lines) == 1, (full2_lines, r1_lines)
    full2 = " ".join(full2_lines)
    proc = encode_start(HERE / "outro3.mp4")
    for i in range(n):
        t = i / FPS
        typing = t < 2.5
        r1 = t >= 2.5
        r2 = None
        if t >= 3.0:
            k = min(1.0, (t - 3.0) / 1.0)
            r2 = len(full2) if k >= 1.0 else max(1, int(len(full2) * k))
        if t < 2.5:
            with canvas(SS):
                img_ss, _ = draw_outro_scene(t, typing, r1, r2)
                u = min(1.0, max(0.0, (t - 0.5) / 2.0))
                center, cw = intro_cam(1 - u, dots_target, 200.0 * K, W, H)
                img, _c, _b = camera(img_ss, center, cw, W, H, OW, OH)
            if t < 0.5:
                dark = Image.new("RGB", (OW, OH), NEAR_BLACK)
                img = Image.blend(dark, img, S.ease_out_cubic(t / 0.5))
        else:
            img, _ = draw_outro_scene(t, typing, r1, r2)
            for j, lay in enumerate(panels):
                img = paste_panel(img, lay, panel_p(t, PANEL_T[j]), j < 3)
        proc.stdin.write(img.convert("RGB").tobytes())
        if i % 60 == 0:
            print(f"outro frame {i}/{n}", flush=True)
    encode_end(proc, HERE / "outro3.mp4")
    return dict(reply2_wrapped=full2_lines, reply1_wrapped=r1_lines)

'''
s = sub(r"def render_outro\(dots_target\):.*?(?=\r?\ndef cam_smoothness)", new_outro, s, flags=re.S)

new_main = '''if __name__ == "__main__":
    with canvas(SS):
        period = measure_period()
        plate = period.pop("plate")
        ink = period["ink"]
        final_w = max(1.2, min(ink["w"], ink["h"] * 16 / 9) * 0.55)
        period["final_crop_w"] = round(final_w, 2)
        period.pop("bubble")
        b = period["ink"]["bbox"]
        crop = plate.crop((b[0] - sc(260), b[1] - sc(70), b[2] + sc(60), b[3] + sc(70)))
        big = crop.resize((crop.width * 3, crop.height * 3), Image.NEAREST)
        bd = ImageDraw.Draw(big)
        for pt, col in ((period["raster_centroid"], (255, 60, 60)),
                        (period["v1_formula"], (255, 220, 60))):
            px, py = (pt[0] - (b[0] - sc(260))) * 3, (pt[1] - (b[1] - sc(70))) * 3
            bd.line([px - 26, py, px + 26, py], fill=col, width=3)
            bd.line([px, py - 26, px, py + 26], fill=col, width=3)
        big.save(HERE / "still3_period_bubble.png")
        target = (period["raster_centroid"][0] + 0.5,
                  period["raster_centroid"][1] + 0.5)
        period["target_cont"] = [round(target[0], 2), round(target[1], 2)]
        period["target_output_px"] = [round(target[0] / SS, 2), round(target[1] / SS, 2)]
        period["ss"] = SS
        period["intro_clamp_max_px"] = round(
            clamp_check(target, final_w, False, plate.width, plate.height), 3)
    print(json.dumps(period, indent=1))
    period["plate"] = plate
    proof, cam_log = render_intro(period, final_w)
    period.pop("plate")
    proof_m = analyze_proof(proof)
    print(json.dumps(proof_m, indent=1))
    with canvas(SS):
        dots = measure_dots()
        dots_t = (dots["raster_centroid"][0] + 0.5, dots["raster_centroid"][1] + 0.5)
        dots["target_cont"] = [round(dots_t[0], 2), round(dots_t[1], 2)]
        dots["target_output_px"] = [round(dots_t[0] / SS, 2), round(dots_t[1] / SS, 2)]
        dots["ss"] = SS
        dots["outro_clamp_max_px"] = round(clamp_check(dots_t, 200.0 * K, True, W, H), 3)
    print(json.dumps(dots, indent=1))
    wrapped = render_outro(dots_t)
    smooth = cam_smoothness(cam_log)
    samples = [dict(t=round(t, 2), crop_w=round(cw, 1),
                    center=[round(c[0], 1), round(c[1], 1)])
               for (t, cw, c) in cam_log[::10]]
    meas = dict(resolution=[OW, OH], ss=SS, internal_resolution=[OW * SS, OH * SS],
                scale_K=round(K, 4),
                period=period, proof=proof_m, dots=dots, smooth=smooth,
                cam_samples=samples, wrapped=wrapped,
                reply_chars=dict(r1=len(REPLY_1), r2=len(REPLY_2),
                                 total=len(REPLY_1) + len(REPLY_2)))
    (HERE / "measurements3.json").write_text(json.dumps(meas, indent=1))
    (HERE / "intro_msg3.txt").write_text(INTRO_MSG + "\\n")
    (HERE / "outro_msg3.txt").write_text(REPLY_1 + "\\n\\n" + REPLY_2 + "\\n")
    print("done")
'''
s = sub(r'if __name__ == "__main__":.*\Z', new_main, s, flags=re.S)
p.write_text(s, encoding="utf-8", newline="")
print("patched intro_outro")
