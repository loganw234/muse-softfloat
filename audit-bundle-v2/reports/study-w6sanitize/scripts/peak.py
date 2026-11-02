import ctypes, os, re, subprocess, sys, time
from ctypes import wintypes

tree = r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\study-w6sanitize\tree"
with open(os.path.join(tree, "tools", "run.sh"), encoding="utf-8") as f:
    vecs = re.search(r'^VECS="([^"]+)"', f.read(), re.M).group(1).split()

env = dict(os.environ)
env["PATH"] = (r"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64;"
               + env.get("PATH", ""))

class PMC(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t)]

OpenProcess = ctypes.windll.kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

for label, rel in [("base", r"build-san\msf_runner_base.exe"),
                   ("trap", r"build-san\msf_runner_trap.exe"),
                   ("asan", r"build-san\msvc\msf_runner_asan.exe")]:
    exe = os.path.join(tree, rel)
    t0 = time.time()
    p = subprocess.Popen([exe, "verify"] + vecs, cwd=tree,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, errors="replace", env=env)
    h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, p.pid)
    out, _ = p.communicate(timeout=3600)
    dt = time.time() - t0
    pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
    ok = GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb) if h else 0
    peakws = pmc.PeakWorkingSetSize / (1024 * 1024) if ok else -1
    peakpf = pmc.PeakPagefileUsage / (1024 * 1024) if ok else -1
    verdict = [ln for ln in out.splitlines() if ln.startswith(("total", "VERDICT"))]
    print(f"{label}: rc={p.returncode} wall={dt:.2f}s peakWS={peakws:.1f}MB "
          f"peakPagefile={peakpf:.1f}MB exeKB={os.path.getsize(exe)//1024} :: {' '.join(verdict)}",
          flush=True)
    if h:
        ctypes.windll.kernel32.CloseHandle(h)
