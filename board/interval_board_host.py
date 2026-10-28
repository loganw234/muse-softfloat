#!/usr/bin/env python3
"""Host side of the Step 1c interval board run (SF-1).

Streams a frozen interval catalogue TSV to the msf_interval
firmware over USB CDC, waits for each row ack, and compares the
board's IW1 SHA-256 against the host runner's digest for the
same file (--expect-sha256, from board/interval_host.c output).
Selects the board by USB serial (default: the genuine board in
docs/BOARD.md) so clone boards sharing the bus are never
addressed by accident.

    interval_board_host.py CATALOGUE.tsv --expect-sha256 HEX
        [--port COMx] [--serial HEXID] [--timeout SECS]
"""
import argparse
import sys
import time

import serial
import serial.tools.list_ports

PICO_VID = 0x2E8A
GENUINE_SERIAL = "E66440A2CB6F5C2B"


def find_port(serial_want):
    for p in serial.tools.list_ports.comports():
        if p.vid == PICO_VID and (p.serial_number or "").upper() == serial_want:
            return p.device
    return None


def read_line(ser, timeout=30.0):
    ser.timeout = timeout
    line = ser.readline()
    if not line:
        raise SystemExit("board: timeout waiting for a line")
    return line.decode("utf-8", "replace").strip()


def read_until(ser, prefix, timeout=30.0, keep=None):
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = read_line(ser, max(1.0, deadline - time.time()))
        if keep is not None:
            keep.append(line)
        if line.startswith(prefix):
            return line
        if line.startswith("E "):
            raise SystemExit("board: error line %r" % line)
    raise SystemExit("board: timeout waiting for %r" % prefix)


def row_command(fields):
    kind = fields[2]
    rid = fields[0]
    o = fields[4:7]
    d = fields[7:10]
    g = fields[10:16]
    if kind == "sphere":
        return "S %s %s %s %s" % (rid, " ".join(o), " ".join(d),
                                  " ".join(g[0:4]))
    if kind == "box":
        return "X %s %s %s %s" % (rid, " ".join(o), " ".join(d),
                                  " ".join(g))
    if kind == "torus":
        return "T %s %s %s" % (rid, " ".join(o), " ".join(d))
    raise SystemExit("catalogue: unknown kind %r" % kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("catalogue")
    ap.add_argument("--port")
    ap.add_argument("--serial", default=GENUINE_SERIAL)
    ap.add_argument("--expect-sha256", required=True)
    ap.add_argument("--timeout", type=float, default=180.0,
                    help="per-reply inactivity timeout in seconds")
    args = ap.parse_args()
    serial_want = args.serial.upper()

    rows = []
    for raw in open(args.catalogue, encoding="utf-8"):
        s = raw.rstrip("\r\n")
        if s and not s.startswith("#"):
            fields = s.split("\t")
            if len(fields) != 19:
                print("catalogue: bad row (%d fields): %s"
                      % (len(fields), s[:80]))
                return 2
            rows.append(fields)
    print("streaming %d catalogue rows from %s" % (len(rows), args.catalogue))

    port = args.port
    deadline = time.time() + 30
    while not port and time.time() < deadline:
        port = find_port(serial_want)
        if not port:
            time.sleep(0.5)
    if not port:
        print("board: no Pico with serial %s within 30s" % serial_want)
        print("ports seen:", [(p.device, hex(p.vid or 0), p.serial_number)
                              for p in serial.tools.list_ports.comports()])
        return 2
    print("board port: %s (serial %s)" % (port, serial_want))
    ser = serial.Serial(port, 115200, timeout=5)
    try:
        time.sleep(0.3)
        ser.reset_input_buffer()
        ser.write(b"I\n")
        banner = read_until(ser, "MSF-INTERVAL", 30.0)
        print("board: %s" % banner)
        if serial_want.lower() not in banner.lower():
            print("board: banner ID does not name serial %s" % serial_want)
            return 1
        ser.write(b"B\n")
        read_until(ser, "OK begin", 30.0)

        t_start = time.time()
        for i, fields in enumerate(rows, 1):
            ser.write((row_command(fields) + "\n").encode())
            want = "R %s" % fields[0]
            got = read_line(ser, args.timeout)
            if got != want:
                print("row %s: board replied %r, want %r"
                      % (fields[0], got, want))
                return 1
            if i % 100 == 0:
                print("  %d/%d rows acked (%.1fs)"
                      % (i, len(rows), time.time() - t_start))
        print("all %d rows acked in %.1fs wall (streaming included)"
              % (len(rows), time.time() - t_start))

        ser.write(b"E\n")
        kept = []
        summary = read_until(ser, "SUMMARY", 60.0, kept)
        sha_line = read_until(ser, "BOARD_SHA256", 60.0, kept)
        done = read_until(ser, "INTERVAL-DONE", 60.0, kept)
        print("board: %s" % summary)
        print("board: %s" % sha_line)
        print("board: %s" % done)
        got_sha = sha_line.split()[1].lower()
        if got_sha != args.expect_sha256.lower():
            print("board interval: IW1 hash mismatch\n  board %s\n  host  %s"
                  % (got_sha, args.expect_sha256.lower()))
            return 1
        print("board interval: IW1 hash matches host")
        print("board interval: PASS (%d rows)" % len(rows))
        return 0
    finally:
        ser.close()


if __name__ == "__main__":
    sys.exit(main())
