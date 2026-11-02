from pathlib import Path
src = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\study-video-gitvisual-v6\measure_sync7.py")
dst = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6filmretime\measure_sync_w6.py")
s = src.read_text(encoding="utf-8")
s = s.replace('sys.path.insert(0, str(HERE))\nimport gitvisual7 as R',
              'SEG = Path(r"C:\\Users\\logan\\source\\repos\\Muse-Softfloat\\worktrees\\w6-filmretime\\video\\segments")\n'
              'sys.path.insert(0, str(SEG))\nimport gitvisual as R')
assert "import gitvisual as R" in s
s = s.replace("_cam = R.master_cam(98.3)", "_cam = R.master_cam(R.T_BOX + 7.8)")
s = s.replace('for t in (50.0, 65.0, 80.0)}', 'for t in (55.0, 75.0, 90.0)}')
s = s.replace('"sync_measurements7.json"', '"sync_measurements_w6.json"')
s = s.replace("-> sync_measurements7.json", "-> sync_measurements_w6.json")
dst.write_text(s, encoding="utf-8", newline="")
print("wrote", dst)
