#!/usr/bin/env python3
"""Lead-run multi-board IAS15 cross-chip check.

Flashes each enumerated RP2040 board one at a time using picotool
device selection, captures its printed unique ID, then (optionally in
parallel) runs the same figure-8 hash/rate commands on every board.
Never uses untargeted flashing when more than one board is present.
"""
import argparse
import concurrent.futures
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import serial.tools.list_ports

WS = Path(__file__).resolve().parents[2]
REPO = WS / "muse-softfloat"
PICOTOOL = Path(r"C:\Users\logan\pico\picotool\picotool.exe")
PY = WS / ".venv" / "Scripts" / "python.exe"
FW_DIR = REPO / "build" / "board-fw" / "ias15fw"
SELFTEST_UF2 = FW_DIR / "msf_aeabi_selftest.uf2"
IAS15_UF2 = FW_DIR / "msf_ias15.uf2"
HOST = REPO / "board" / "ias15_host.py"
REF = WS / "scratch" / "ias15" / "out" / "hashes_native.txt"
COMPARE = WS / "scratch" / "ias15" / "work" / "compare_hashes.py"
LOCK = WS / "ledger" / "board.lock"
GENUINE_ID = "e66440a2cb6f5c2b"
ID_RE = re.compile(r"(?:MSF-AEABI-SELFTEST|MSF-IAS15) 1 ID ([0-9a-fA-F]{16})")


def run(cmd, log_path=None, check=True, timeout=None):
    print("+", " ".join(str(x) for x in cmd), flush=True)
    p = subprocess.run([str(x) for x in cmd], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=timeout)
    if log_path:
        Path(log_path).write_text(p.stdout, encoding="utf-8", newline="\n")
    print(p.stdout, end="" if p.stdout.endswith("\n") or not p.stdout else "\n")
    if check and p.returncode != 0:
        raise RuntimeError("command failed rc=%d: %s" % (p.returncode, cmd[0]))
    return p


def ports():
    out = []
    for p in serial.tools.list_ports.comports():
        if p.vid == 0x2E8A:
            out.append({
                "device": p.device,
                "serial": (p.serial_number or "").upper(),
                "location": getattr(p, "location", None),
                "hwid": p.hwid,
                "description": p.description,
            })
    return sorted(out, key=lambda x: x["device"])


def bootsel_devices():
    p = run([PICOTOOL, "info", "-a"], check=False)
    return [(int(a), int(b)) for a, b in
            re.findall(r"(?m)^RP2040 device at bus (\d+), address (\d+):", p.stdout)]


def wait_for_new_port(before, timeout=35):
    before_keys = {(x["device"], x["serial"], x["location"]) for x in before}
    deadline = time.time() + timeout
    while time.time() < deadline:
        now = ports()
        new = [x for x in now
               if (x["device"], x["serial"], x["location"]) not in before_keys]
        if len(new) == 1:
            return new[0]
        if len(new) > 1:
            raise RuntimeError("multiple new CDC ports appeared: %r" % new)
        time.sleep(0.5)
    raise RuntimeError("no new CDC port appeared; ports=%r" % ports())


def wait_for_serial(serial_want, timeout=35):
    deadline = time.time() + timeout
    while time.time() < deadline:
        matches = [x for x in ports() if x["serial"] == serial_want.upper()]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise RuntimeError("duplicate CDC serial %s: %r" % (serial_want, matches))
        time.sleep(0.5)
    raise RuntimeError("CDC serial %s did not enumerate; ports=%r" %
                       (serial_want, ports()))


def capture(port, until, out_log, cmd=None, hashes=None, idle=1500):
    c = [PY, HOST, "--port", port, "--until", until,
         "--idle-timeout", str(idle)]
    if cmd:
        c += ["--cmd", cmd]
    if hashes:
        c += ["--hashes", str(hashes)]
    return run(c, out_log, check=True)


def board_id_from_log(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    m = ID_RE.search(text)
    return m.group(1).lower() if m else None


def flash_running(uf2, serial, log_path):
    matches = [x for x in ports() if x["serial"] == serial.upper()]
    if len(matches) != 1:
        raise RuntimeError("serial %s is not unique among running boards: %r" %
                           (serial, matches))
    # picotool's parser accepts device-selection options before the file;
    # putting --ser after the file is rejected by this build.
    return run([PICOTOOL, "load", "--ser", serial, "-f", "-x", str(uf2)],
               log_path, check=True)


def flash_bootsel(uf2, bus, addr, log_path):
    return run([PICOTOOL, "load", "--bus", str(bus),
                "--address", str(addr), "-x", str(uf2)],
               log_path, check=True)


def prepare_board(kind, label, port_info, out):
    """Flash selftest then IAS15 to one board; return identity dict."""
    board_dir = out / label
    board_dir.mkdir(parents=True, exist_ok=True)
    if kind == "bootsel":
        before = ports()
        flash_bootsel(SELFTEST_UF2, port_info[0], port_info[1],
                      board_dir / "flash-selftest.log")
        p = wait_for_new_port(before)
    else:
        p = port_info
        flash_running(SELFTEST_UF2, p["serial"], board_dir / "flash-selftest.log")
        p = wait_for_serial(p["serial"])
    capture(p["device"], "AEABI-RESULT", board_dir / "selftest.log")
    text = (board_dir / "selftest.log").read_text(encoding="utf-8", errors="replace")
    if "AEABI-RESULT PASS" not in text:
        raise RuntimeError("%s selftest did not PASS" % label)
    bid = board_id_from_log(board_dir / "selftest.log")
    if not bid:
        raise RuntimeError("%s did not print a board ID" % label)
    serial = p["serial"] or bid.upper()
    flash_running(IAS15_UF2, serial, board_dir / "flash-ias15.log")
    p = wait_for_serial(serial)
    capture(p["device"], "IAS15-READY", board_dir / "ready.log", cmd="I")
    return {"label": label, "board_id": bid, "serial": serial,
            "port": p["device"], "location": p.get("location"),
            "dir": str(board_dir)}


def truncated_ref(steps, out):
    rows = []
    for ln in REF.read_text(encoding="utf-8").splitlines():
        if ln.startswith("#"):
            rows.append(ln)
        elif ln.strip():
            if int(ln.split()[0]) <= steps:
                rows.append(ln)
    path = out / ("ref_first_%d.txt" % steps)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    return path


def run_board(board, steps, ref_path, out):
    d = Path(board["dir"])
    hashes = d / "hashes_board.txt"
    capture(board["port"], "IAS15-DONE", d / "run.log",
            cmd="R %d 1" % steps, hashes=hashes, idle=1500)
    cmp_log = d / "compare.log"
    try:
        run([PY, COMPARE, ref_path, hashes], cmp_log, check=True)
        board["compare"] = "PASS"
    except Exception as e:
        board["compare"] = "FAIL: %s" % e
    try:
        capture(board["port"], "IAS15-DONE", d / "rate.log",
                cmd="T %d" % steps, idle=1500)
        rates = []
        total_steps = 0
        total_us = 0
        for ln in (d / "rate.log").read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.search(r"RATE block_steps=(\d+) elapsed_us=(\d+) clk_sys_hz=(\d+)", ln)
            if m:
                rates.append({"steps": int(m.group(1)),
                              "elapsed_us": int(m.group(2)),
                              "clk_sys_hz": int(m.group(3)),
                              "steps_per_s": int(m.group(1)) * 1e6 / int(m.group(2))})
                total_steps += int(m.group(1))
                total_us += int(m.group(2))
        board["rates"] = rates
        board["rate_steps_per_s"] = (total_steps * 1e6 / total_us) if total_us else None
    except Exception as e:
        board["rate_error"] = str(e)
    return board


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--parallel-run", action="store_true",
                    help="run R/T captures concurrently after sequential flashing")
    ap.add_argument("--skip-genuine", action="store_true")
    ap.add_argument("--max-clones", type=int, default=99)
    args = ap.parse_args()

    out = REPO / "build" / "multiboard-ias15"
    out.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        print("board.lock exists (held):", LOCK.read_text(encoding="utf-8"))
        return 1
    token = "lead (Muse Code)\nIAS15 multi-board cross-chip run\n%s\n" % dt.datetime.now().astimezone().isoformat()
    LOCK.write_text(token, encoding="utf-8", newline="\n")
    boards = []
    failures = []
    try:
        print("initial CDC ports:", json.dumps(ports(), indent=2))
        boots = bootsel_devices()
        print("BOOTSEL devices:", boots)
        for i, (bus, addr) in enumerate(boots[:args.max_clones], 1):
            try:
                boards.append(prepare_board(
                    "bootsel", "clone-bootsel-%d-%d-%d" % (i, bus, addr),
                    (bus, addr), out))
            except Exception as e:
                failures.append({"target": "bootsel %d/%d" % (bus, addr),
                                 "phase": "prepare", "error": repr(e)})
                print("FAIL prepare bootsel", bus, addr, repr(e), flush=True)
        prepared_serials = {b["serial"] for b in boards}
        running = [x for x in ports() if x["serial"] not in prepared_serials]
        for p in running:
            is_genuine = p["serial"].lower() == GENUINE_ID
            if is_genuine and args.skip_genuine:
                continue
            label = "genuine" if is_genuine else "clone-running-%s" % p["serial"].lower()
            try:
                boards.append(prepare_board("running", label, p, out))
            except Exception as e:
                failures.append({"target": label, "phase": "prepare",
                                 "error": repr(e)})
                print("FAIL prepare running", label, repr(e), flush=True)
        ref = truncated_ref(args.steps, out) if args.steps < 2000 else REF
        if args.parallel_run and len(boards) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(boards)) as ex:
                done = list(ex.map(lambda b: run_board(b, args.steps, ref, out), boards))
            boards = done
        else:
            boards = [run_board(b, args.steps, ref, out) for b in boards]
    finally:
        result = {"steps": args.steps, "boards": boards, "failures": failures,
                  "finished": dt.datetime.now().astimezone().isoformat()}
        (out / "manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        try:
            if LOCK.read_text(encoding="utf-8") == token:
                LOCK.unlink()
                print("board lock released")
        except FileNotFoundError:
            pass
    bad = failures or any(b.get("compare") != "PASS" for b in boards)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
