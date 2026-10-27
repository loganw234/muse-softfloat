"""Print the exact render stack found on this machine (no installs)."""
from __future__ import annotations

import shutil
import subprocess
import sys


def main() -> None:
    print(f"python: {sys.version.split()[0]}  {sys.executable}")
    for mod in ("PIL", "numpy", "imageio", "imageio_ffmpeg", "matplotlib"):
        try:
            m = __import__(mod)
            print(f"{mod}: {getattr(m, '__version__', '?')}")
        except Exception as e:  # noqa: BLE001 - inventory must not die
            print(f"{mod}: MISSING ({e})")
    print(f"ffmpeg on PATH: {shutil.which('ffmpeg')}")
    print(f"ffprobe on PATH: {shutil.which('ffprobe')}")
    try:
        import imageio_ffmpeg

        exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"bundled ffmpeg: {exe}")
        out = subprocess.run([exe, "-version"], capture_output=True, text=True)
        print("  " + out.stdout.splitlines()[0])
        enc = subprocess.run([exe, "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        print(f"  libx264 encoder present: {'libx264' in enc}")
    except Exception as e:  # noqa: BLE001
        print(f"bundled ffmpeg: MISSING ({e})")
    from pathlib import Path

    for f in ("arialbd.ttf", "segoeuib.ttf", "segoeui.ttf", "consolab.ttf"):
        print(f"font {f}: {(Path(r'C:\Windows\Fonts') / f).exists()}")


if __name__ == "__main__":
    main()
