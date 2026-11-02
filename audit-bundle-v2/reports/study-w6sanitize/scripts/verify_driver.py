import os, re, subprocess, sys, threading, time

# Usage: verify_driver.py <tree_dir_win> <exe_win> <label> <log_path>
# Runs `exe unit` once, then `exe verify <file>` for every vector file
# named in tools/run.sh VECS, then one all-files verify invocation.
# One process, one log stream (host append-corruption avoidance).

tree, exe, label, logpath = sys.argv[1:5]
peak = {"rss": 0, "method": "none"}
try:
    import psutil
    peak["method"] = "psutil-poll-50ms"
except Exception:
    psutil = None

def run(args, timeout_s):
    t0 = time.time()
    p = subprocess.Popen(args, cwd=tree, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, errors="replace")
    stop = threading.Event()
    def poll():
        if psutil is None:
            return
        try:
            pr = psutil.Process(p.pid)
            while not stop.is_set():
                try:
                    rss = pr.memory_info().rss
                    if rss > peak["rss"]:
                        peak["rss"] = rss
                except Exception:
                    break
                time.sleep(0.05)
        except Exception:
            pass
    th = threading.Thread(target=poll, daemon=True)
    th.start()
    try:
        out, _ = p.communicate(timeout=timeout_s)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
        rc = "TIMEOUT"
    stop.set()
    return rc, time.time() - t0, out

with open(os.path.join(tree, "tools", "run.sh"), encoding="utf-8") as f:
    runsh = f.read()
m = re.search(r'^VECS="([^"]+)"', runsh, re.M)
vecs = m.group(1).split()

log = open(logpath, "w", encoding="utf-8", newline="\n")
def say(s):
    log.write(s + "\n"); log.flush(); print(s, flush=True)

say(f"label={label} exe={exe}")
say(f"vector files from run.sh VECS: {len(vecs)}")
rc, dt, out = run([exe, "unit"], 600)
tail = " | ".join([ln for ln in out.strip().splitlines() if ln.strip()][-6:])
say(f"UNIT rc={rc} t={dt:.2f}s :: {tail[:400]}")

bad = 0
total_lines = 0
t_all = time.time()
for i, v in enumerate(vecs, 1):
    rc, dt, out = run([exe, "verify", v], 1800)
    tot = ""
    for ln in out.splitlines():
        if ln.startswith("total:") or ln.startswith("VERDICT"):
            tot += ln.strip() + " "
        mm = re.match(r"total: (\d+)", ln)
        if mm:
            total_lines += int(mm.group(1))
    if rc != 0:
        bad += 1
        say(f"[{i}/{len(vecs)}] rc={rc} t={dt:.2f}s {v} :: {tot} :: TAIL: " +
            " | ".join(out.strip().splitlines()[-4:])[:500])
    else:
        say(f"[{i}/{len(vecs)}] rc=0 t={dt:.2f}s {v} :: {tot.strip()}")
say(f"per-file verify: {len(vecs)-bad}/{len(vecs)} files rc=0, total-count-lines={total_lines}, wall={time.time()-t_all:.1f}s")

if bad == 0:
    rc, dt, out = run([exe, "verify"] + vecs, 3600)
    tot = " ".join(ln.strip() for ln in out.splitlines()
                   if ln.startswith("total:") or ln.startswith("VERDICT"))
    say(f"ALL-FILES single invocation rc={rc} t={dt:.2f}s :: {tot[:300]}")
    if rc != 0:
        say("ALL-FILES TAIL: " + " | ".join(out.strip().splitlines()[-6:])[:800])
else:
    say("ALL-FILES single invocation SKIPPED (per-file failures above)")

say(f"peak child RSS: {peak['rss']/(1024*1024):.1f} MiB (method={peak['method']})")
say(f"DRIVER-DONE label={label} bad_files={bad}")
log.close()
