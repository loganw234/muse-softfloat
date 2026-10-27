"""Render a timeline to MP4: Pillow frames -> rawvideo pipe -> ffmpeg libx264.

Usage (from the video/ dir, with a Python environment that has this
project's video dependencies installed):
    python render.py                 # proof -> out/proof.mp4
    python render.py --timeline mycut.json --out out/mycut.mp4
    python render.py --export-timeline proof.json
    python render.py --still 7.2 --out frame.png
    python render.py --fps 30 --crf 18 --preset veryfast
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import imageio_ffmpeg

import scenes
import style as S
import timeline as TL

HERE = Path(__file__).resolve().parent


def ffmpeg_exe() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def scene_at(timeline: list[dict], t: float) -> dict:
    for sc in timeline:
        if sc["t0"] <= t < sc["t1"]:
            return sc
    return timeline[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", help="JSON timeline (default: timeline.PROOF)")
    ap.add_argument("--which", choices=["proof", "final"], default="proof",
                    help="built-in timeline to render/export (ignored with --timeline)")
    ap.add_argument("--export-timeline", help="write the built-in (--which) timeline as JSON and exit")
    ap.add_argument("--out", default=str(HERE / "out" / "proof.mp4"))
    ap.add_argument("--fps", type=int, default=S.FPS)
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--still", type=float, help="render a single frame at this time (s) to --out PNG")
    ap.add_argument("--max-seconds", type=float, help="truncate (fast smoke renders)")
    args = ap.parse_args()

    builtin = TL.FINAL if args.which == "final" else TL.PROOF
    if args.export_timeline:
        Path(args.export_timeline).write_text(json.dumps(builtin, indent=2), encoding="utf-8")
        print(f"wrote {args.export_timeline}")
        return 0

    if args.timeline:
        timeline = json.loads(Path(args.timeline).read_text(encoding="utf-8"))
    else:
        timeline = builtin
    TL.validate(timeline)
    total = timeline[-1]["t1"]
    if args.max_seconds:
        total = min(total, args.max_seconds)

    t_start = time.time()
    print("loading real project data (metrics jsonl + git log)...", flush=True)
    ctx = scenes.build_ctx()
    print(f"  plants {ctx['data']['plants']}, agents {len(ctx['data']['tool_uses_by_agent'])}, "
          f"commits {len(ctx['data']['git_subjects'])}", flush=True)

    if args.still is not None:
        sc = scene_at(timeline, args.still)
        img = scenes.render_scene(sc, args.still, ctx, total)
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        img.save(args.out)
        print(f"still t={args.still}s ({sc['kind']}) -> {args.out}  [{time.time() - t_start:.1f}s]")
        return 0

    n_frames = int(total * args.fps)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{S.W}x{S.H}",
        "-r", str(args.fps), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(out),
    ]
    print(f"rendering {n_frames} frames ({total:.1f}s @ {args.fps}fps) -> {out}", flush=True)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(n_frames):
            t = i / args.fps
            sc = scene_at(timeline, t)
            img = scenes.render_scene(sc, t, ctx, total)
            proc.stdin.write(img.tobytes())
            if i % 90 == 0:
                print(f"  frame {i}/{n_frames}  t={t:.1f}s  {sc['kind']}  "
                      f"[{time.time() - t_start:.0f}s elapsed]", flush=True)
    finally:
        proc.stdin.close()
    rc = proc.wait()
    wall = time.time() - t_start
    if rc != 0:
        print(f"ffmpeg failed rc={rc}", file=sys.stderr)
        return rc
    print(f"DONE {out}  {out.stat().st_size / 1e6:.1f} MB  wall {wall:.1f}s "
          f"({n_frames} frames, machine under load - not a rate claim)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
