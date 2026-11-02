import ctypes, os, re, subprocess, sys, time
from ctypes import wintypes

wt = r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-sanitize"
with open(os.path.join(wt, "tools", "run.sh"), encoding="utf-8") as f:
    vecs = re.search(r'^VECS="([^"]+)"', f.read(), re.M).group(1).split()

class PMC(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t)]

OpenProcess = ctypes.windll.kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo

def measure(label, exe, args):
    t0 = time.time()
    p = subprocess.Popen([exe] + args, cwd=wt, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, errors="replace")
    h = OpenProcess(0x0400 | 0x0010, False, p.pid)
    out, _ = p.communicate(timeout=3600)
    dt = time.time() - t0
    pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
    ok = GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb) if h else 0
    peakws = pmc.PeakWorkingSetSize / (1024 * 1024) if ok else -1
    peakpf = pmc.PeakPagefileUsage / (1024 * 1024) if ok else -1
    verdict = [ln for ln in out.splitlines() if ln.startswith(("total", "VERDICT", "aug_exhaustive pool", "unit:"))]
    print(f"{label}: rc={p.returncode} wall={dt:.2f}s peakWS={peakws:.1f}MB peakPagefile={peakpf:.1f}MB exeKB={os.path.getsize(exe)//1024} :: {' | '.join(verdict)}", flush=True)
    if h: ctypes.windll.kernel32.CloseHandle(h)
    return p.returncode

runner = os.path.join(wt, r"build\sanitize-trap\msf_runner.exe")
aug = os.path.join(wt, r"build\sanitize-trap\aug_exhaustive.exe")
rc = 0
rc |= measure("trap verify committed", runner, ["verify"] + vecs)
rc |= measure("trap verify extras", runner, ["verify", r"build\sanitize-trap\f16-exhaustive.vec", r"build\sanitize-trap\pack-sweep.vec"])
rc |= measure("trap aug pool", aug, ["pool"])
sys.exit(rc)
