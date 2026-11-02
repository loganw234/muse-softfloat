#!/usr/bin/env python3
"""Six-board enumeration + LED-firmware harness replay (lead-run).

Flashes msf_board_harness (LED build) onto every attached RP2040:
BOOTSEL boards via UF2 drive copy (one at a time, so the new CDC
port attributes the board ID), running boards via targeted
picotool load --ser. Then replays board-smoke.vec on all boards
in parallel and compares each whole-run hash to the host's.
Holds ledger/board.lock for the whole run.
"""
import concurrent.futures
import datetime as dt
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import serial
import serial.tools.list_ports

WS = Path(__file__).resolve().parents[2]
REPO = WS / "muse-softfloat"
PICOTOOL = Path(r"C:\Users\logan\pico\picotool\picotool.exe")
PY = WS / ".venv" / "Scripts" / "python.exe"
UF2 = REPO / "build" / "board-fw" / "fw" / "msf_board_harness.uf2"
VEC = REPO / "build" / "board-fw" / "board-smoke.vec"
EXPECT = "4573ac098f2f8a5bf8c6b09fb9746ee206e24a3870c19b4b07f3dd3fee5f28a7"
LOCK = WS / "ledger" / "board.lock"
OUT = WS / "scratch" / "lead" / "sixboard-harness.json"


def cdc_ports():
    """serial_number (upper) -> device, for VID 2E8A ports."""
    out = {}
    for p in serial.tools.list_ports.comports():
        if p.vid == 0x2E8A:
            out[(p.serial_number or "").upper()] = p.device
    return out


def bootsel_drives():
    return [Path(f"{c}:\\") for c in "DEFGHIJKLMNOPQRSTUVWXYZ"
            if (Path(f"{c}:\\") / "INFO_UF2.TXT").exists()]


def wait_new_port(before, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        now = cdc_ports()
        new = {s: d for s, d in now.items() if s not in before}
        if new:
            return new
        time.sleep(1)
    return {}


def wait_serial(ser, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        now = cdc_ports()
        if ser in now:
            return now[ser]
        time.sleep(1)
    return None


def banner_id(port):
    ser = serial.Serial(port, 115200, timeout=5)
    time.sleep(0.3)
    ser.reset_input_buffer()
    ser.write(b"I\n")
    line = ser.readline().decode("utf-8", "replace").strip()
    ser.close()
    return line


def replay(port):
    p = subprocess.run(
        [str(PY), str(REPO / "board" / "host_replay.py"), str(VEC),
         "--port", port, "--expect-sha256", EXPECT],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=900)
    return port, p.returncode, p.stdout


def main():
    if LOCK.exists():
        print("board.lock held:", LOCK.read_text())
        return 1
    LOCK.write_text("lead (Muse Code)\nsix-board enumeration + LED harness replay\n%s\n"
                    % dt.datetime.now(dt.timezone.utc).isoformat())
    boards = {}  # serial -> dict
    try:
        drives = bootsel_drives()
        running = cdc_ports()
        print("BOOTSEL drives:", [str(d) for d in drives])
        print("running CDC:", running)

        for d in drives:
            before = cdc_ports()
            print(f"copying harness UF2 to {d} ...", flush=True)
            shutil.copyfile(UF2, d / UF2.name)
            new = wait_new_port(before)
            if not new:
                print(f"FAIL: no new CDC port after flashing {d}")
                boards[f"bootsel-{d.drive}"] = {"error": "no port after flash"}
                continue
            for ser_id, port in new.items():
                boards[ser_id] = {"port": port, "via": f"BOOTSEL {d.drive}"}
                print(f"  {d.drive} -> serial {ser_id} on {port}")

        for ser_id in list(running):
            print(f"picotool load --ser {ser_id} ...", flush=True)
            p = subprocess.run(
                [str(PICOTOOL), "load", "--ser", ser_id, "-f", "-x", str(UF2)],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                timeout=180)
            print(p.stdout[-500:])
            if p.returncode != 0:
                boards[ser_id] = {"error": "picotool load rc=%d" % p.returncode}
                continue
            port = wait_serial(ser_id)
            if not port:
                boards[ser_id] = {"error": "port did not return"}
                continue
            boards[ser_id] = {"port": port, "via": "picotool --ser"}

        time.sleep(2)
        for ser_id, b in boards.items():
            if "port" in b:
                try:
                    b["banner"] = banner_id(b["port"])
                except Exception as e:  # noqa: BLE001
                    b["banner"] = f"ERROR {e}"
                print(ser_id, b["port"], b["banner"], flush=True)

        todo = {s: b["port"] for s, b in boards.items() if "port" in b}
        print(f"replaying on {len(todo)} boards in parallel...", flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(todo) or 1) as ex:
            futs = {ex.submit(replay, port): s for s, port in todo.items()}
            for fut in concurrent.futures.as_completed(futs):
                s = futs[fut]
                port, rc, out = fut.result()
                boards[s]["replay_rc"] = rc
                boards[s]["replay_tail"] = "\n".join(out.strip().splitlines()[-3:])
                print(f"== {s} ({port}) rc={rc}\n{boards[s]['replay_tail']}", flush=True)
    finally:
        LOCK.unlink(missing_ok=True)
    OUT.write_text(json.dumps(boards, indent=2))
    ok = sum(1 for b in boards.values() if b.get("replay_rc") == 0)
    print(f"SUMMARY boards={len(boards)} replay_pass={ok}")
    print(json.dumps(boards, indent=2))
    return 0 if ok == len(boards) and boards else 1


if __name__ == "__main__":
    sys.exit(main())
