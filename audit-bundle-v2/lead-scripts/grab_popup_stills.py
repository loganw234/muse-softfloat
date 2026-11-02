import subprocess
from pathlib import Path
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = Path("scratch/lead/popup_stills")
OUT.mkdir(parents=True, exist_ok=True)
mp4 = "worktrees/w6-popups/video/segments/gitvisual7.mp4"
for t, name in [(8.5, "parcels.png"), (14.0, "escalations.png"), (31.25, "gates.png")]:
    subprocess.run([FF, "-y", "-ss", str(t), "-i", mp4, "-frames:v", "1",
                    str(OUT / name)], capture_output=True)
    print("grab", name)
