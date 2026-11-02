import re, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
FILM = "muse-softfloat/video/out/assembly_v6.mp4"
MP3 = "ES_Sunflower Dance - Helmut Schenker.mp3"
OUT = Path("scratch/lead/music")
OUT.mkdir(parents=True, exist_ok=True)

def dur(path):
    p = subprocess.run([FF, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("FAIL: " + " ".join(cmd) + "\n" + p.stderr[-800:])

fd, td = dur(FILM), dur(MP3)
factor = td / fd
print(f"film {fd:.3f}s  track {td:.3f}s  atempo {factor:.6f} "
      f"(effective BPM {124 * factor:.2f})")

# first onset / tail silence (helps owner shift decisions on the site editor)
p = subprocess.run([FF, "-i", MP3, "-af", "silencedetect=noise=-45dB:d=0.2",
                    "-f", "null", "-"], capture_output=True, text=True)
ends = re.findall(r"silence_end: ([\d.]+)", p.stderr)
starts = re.findall(r"silence_start: ([\d.]+)", p.stderr)
print(f"first sound ends silence at: {ends[0] if ends else 'n/a'}s; "
      f"last silence starts at: {starts[-1] if starts else 'n/a'}s")

A = OUT / "assembly_v6_musicA_stretch.mp4"
run([FF, "-y", "-i", FILM, "-i", MP3, "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-af", f"atempo={factor:.6f}",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
     "-metadata", "title=Muse-Softfloat film + Sunflower Dance (A: stretch to fit)",
     str(A)])
print("A:", A, f"{dur(str(A)):.3f}s", f"{A.stat().st_size} bytes")

B = OUT / "assembly_v6_musicB_native124.mp4"
run([FF, "-y", "-i", FILM, "-i", MP3, "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-af", f"afade=t=out:st={fd - 5.0:.3f}:d=5",
     "-c:a", "aac", "-b:a", "192k", "-t", f"{fd:.3f}",
     "-movflags", "+faststart",
     "-metadata", "title=Muse-Softfloat film + Sunflower Dance (B: native 124, trim+fade)",
     str(B)])
print("B:", B, f"{dur(str(B)):.3f}s", f"{B.stat().st_size} bytes")

for f in (A, B):
    p = subprocess.run([FF, "-i", str(f)], capture_output=True, text=True)
    streams = re.findall(r"Stream #\d+:\d+.*: (Video|Audio):.*", p.stderr)
    print(f.name, "streams:", streams)
