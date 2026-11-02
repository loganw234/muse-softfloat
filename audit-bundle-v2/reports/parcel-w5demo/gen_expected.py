#!/usr/bin/env python3
"""Authoring aid (scratch only): build demo/expected-*.txt from the
recorded values, verifying the copies against their sources."""
import hashlib
import pathlib
import re

WS = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat")
DEMO = WS / "worktrees" / "w5-demo" / "demo"

# ---- IAS15: full 2,001 records from the desktop reference run ----
src = WS / "scratch" / "ias15" / "out" / "hashes_native.txt"
blob = src.read_bytes()
digest = hashlib.sha256(blob).hexdigest()
assert digest == "9bedb078b1de37c399312e27a65f971229c2cd8353d5f671ae8ed64a63993ab3", digest
rows = []
for line in blob.decode("utf-8").splitlines():
    if line.strip() and not line.startswith("#"):
        rows.append(line.strip())
assert len(rows) == 2001, len(rows)
assert rows[0].split()[1] == "62bb23b04627c30227a7fb999fee22d0ac9eb4349631d9c41f138c6bde333e01"
assert rows[-1].split()[0] == "2000"
assert rows[-1].split()[1] == "4d4530a668d360897477a63f90dfb0f7c86b33eb3e462f5a464028d083f48abb"
assert rows[-1].split()[2] == "32689328ee80ff8b90685b10087a747cfbba9ac236f2b35c2481ce531c26a4c7"
header = [
    "# expected-ias15.txt - IAS15FH1 state hashes for the demo figure-8 run.",
    "# Provenance: the unmodified desktop REBOUND 5.2.2 run (native SSE2,",
    "# strict flags -O3 -ffp-contract=off) recorded as hashes_native.txt",
    "# (file sha256 9bedb078b1de37c399312e27a65f971229c2cd8353d5f671ae8ed64a63993ab3);",
    "# step 0 and step 2000 H_state/H_full values are quoted in the",
    "# project record.  The same rows were later reproduced bit-for-bit",
    "# by the soft-interposed host build, the generated extract (native",
    "# and soft), and the RP2040 firmware (2,001/2,001 records).",
    "# Row shape: <step> <H_state> <H_full> <t bits> <dt bits> <dt_last_done bits>.",
    "# All 2,001 records are carried (not a prefix) so a divergence names",
    "# its first step; at ~370 KB the file is small next to the committed",
    "# test-vector sets.  Generated data: do not hand-edit.",
]
(DEMO / "expected-ias15.txt").write_bytes(
    ("\n".join(header + rows) + "\n").encode("utf-8"))
print("expected-ias15.txt: %d rows, source sha256 %s" % (len(rows), digest))

# ---- KissFFT: 12 KF rows, cross-checked two ways ----
scratch_kf = [ln.strip() for ln in
              (WS / "scratch" / "parcel-w4kissfft" / "out" / "hashes-main.txt")
              .read_text(encoding="utf-8").splitlines()
              if ln.startswith("KF ")]
ledger = (WS / "ledger" / "parcel-w4kissfft.md").read_text(encoding="utf-8")
ledger_kf = re.findall(r"^KF \d+ (?:complex|real) (?:fwd|inv) [0-9a-f]{64}$",
                       ledger, flags=re.M)
assert len(scratch_kf) == 12, len(scratch_kf)
assert scratch_kf == ledger_kf, (scratch_kf, ledger_kf)
header = [
    "# expected-kissfft.txt - KissFFT Fork B host-proof hashes (12 configurations).",
    "# Provenance: parcel-w4kissfft host proof over the Fork-B-patched",
    "# KissFFT 131.2.0 tree (ledger results entry; identical rows in the",
    "# recorded hashes-main.txt).  The same 12 rows were reproduced",
    "# bit-for-bit on the RP2040 (docs/RECORD.md, Step 2c close).",
    "# Row shape: KF <N> <complex|real> <fwd|inv> <sha256 of output fields>.",
    "# This file doubles as KISSFFT_EXPECT for board/kissfft_run.sh",
    "# (board/kissfft_host.py reads KF rows and ignores other lines).",
]
(DEMO / "expected-kissfft.txt").write_bytes(
    ("\n".join(header + scratch_kf) + "\n").encode("utf-8"))
print("expected-kissfft.txt: %d rows (scratch == ledger)" % len(scratch_kf))

# ---- Interval: full IW1 hash from the parcel ledger ----
iled = (WS / "ledger" / "parcel-w4interval.md").read_text(encoding="utf-8")
m = re.search(r"ce81d66e[0-9a-f]{56}", iled)
assert m, "IW1 hash not found"
iw1 = m.group(0)
assert iw1.endswith("a9aec"), iw1
lines = [
    "# expected-interval.txt - Step 1c interval workload host expectation.",
    "# Provenance: parcel-w4interval results (host IW1 SHA-256 over the",
    "# frozen tests/interval_catalogue.tsv, 710 rows); docs/BOARD.md",
    "# quotes the truncated form ce81d66e...a9aec for the identical",
    "# host and board digests.  demo/run_demo.sh requires the host",
    "# runner to reproduce exactly these two lines' values:",
    "rows=710",
    "HOST_SHA256 %s" % iw1,
]
(DEMO / "expected-interval.txt").write_bytes(
    ("\n".join(lines) + "\n").encode("utf-8"))
print("expected-interval.txt: IW1 %s" % iw1)
print("GEN-EXPECTED DONE")
