#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""make_kissfft_tree.py - build the Fork-B-patched KissFFT tree.

Copies the pristine KissFFT 131.2.0 tree fetched by demo/fetch.sh,
applies the Fork B patch at exactly three sites, and verifies the
result against the recorded patched-file sha256s.  Fork B is the
demo workloads' one named change to third-party source (never
described as unmodified KissFFT): twiddle generation hands exact
cycle fractions to correctly rounded sinpi/cospi instead of radian
phases to sin/cos (see docs/BOARD.md, KissFFT section).  Sites:

  kiss_fft.c        alloc phase: -2*pi*i/nfft  ->  -2.0*i/nfft
                    (the sinpi/cospi argument, cycles*2 form)
  kiss_fftr.c       super-twiddle phase: drop the pi factor (the
                    remainder is exactly the sinpi/cospi argument)
  _kiss_fft_guts.h  KISS_FFT_COS/SIN call cospi/sinpi (declared)

Each replacement is an exact-string match that must occur exactly
once, every unpatched file must stay byte-identical to pristine,
and the three patched files must hash to the values below -
recorded in the board-run log of the 2026-10-28 silicon run
(build/kissfft-board/tree-inputs.sha256 in the lead's tree; the
same values hash out of the parcel-w4kissfft scratch tree that
produced the host proof and the board firmware).  Any mismatch is
a hard failure.

Usage: make_kissfft_tree.py <pristine-dir> <out-dir>
Exit status: 0 = patched tree written and verified; 1 = failure;
2 = usage.
"""
import hashlib
import pathlib
import shutil
import sys

PATCHES = [
    ("kiss_fft.c",
     """        for (i=0;i<nfft;++i) {
            const double pi=3.141592653589793238462643383279502884197169399375105820974944;
            double phase = -2*pi*i / nfft;""",
     """        for (i=0;i<nfft;++i) {
            /* MSF Fork B: exact cycle fraction *2 for sinpi/cospi
             * (cos(2*pi*c) = cospi(2c)); exact at power-of-two nfft. */
            double phase = -2.0*i / nfft;"""),
    ("kiss_fftr.c",
     """        double phase =
            -3.14159265358979323846264338327 * ((double) (i+1) / nfft + .5);""",
     """        /* MSF Fork B: exact sinpi/cospi argument (radian phase
         * was pi times this); exact at power-of-two nfft. */
        double phase =
            -((double) (i+1) / nfft + .5);"""),
    ("_kiss_fft_guts.h",
     """#  define KISS_FFT_COS(phase) (kiss_fft_scalar) cos(phase)
#  define KISS_FFT_SIN(phase) (kiss_fft_scalar) sin(phase)""",
     """/* MSF Fork B: phase is an exact cycle-fraction argument for
 * sinpi/cospi (C23 names, declared here). */
double sinpi(double);
double cospi(double);
#  define KISS_FFT_COS(phase) (kiss_fft_scalar) cospi(phase)
#  define KISS_FFT_SIN(phase) (kiss_fft_scalar) sinpi(phase)"""),
]

# Recorded sha256 of the patched files (board-run log provenance
# in the module docstring).
EXPECTED_SHA256 = {
    "kiss_fft.c":
        "8fcc496897ce2844a08a8ca74268b28149bd3a8949fc31e78538151366062305",
    "kiss_fftr.c":
        "b34ff3b21594c61e295f61bbf8a9fd86d6310fcceb459d07389c470ad848744f",
    "_kiss_fft_guts.h":
        "42fd7132fdb19e986d66693a081d90239b19b9a9496f319e86510f5fe7be9402",
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(msg):
    print("make_kissfft_tree: FAIL - %s" % msg)
    return 1


def rel_files(root):
    return sorted(p.relative_to(root).as_posix()
                  for p in root.rglob("*") if p.is_file())


def main(argv):
    if len(argv) != 3:
        print("usage: make_kissfft_tree.py <pristine-dir> <out-dir>")
        return 2
    pristine = pathlib.Path(argv[1])
    out = pathlib.Path(argv[2])
    for fname, _, _ in PATCHES:
        if not (pristine / fname).is_file():
            return fail("no %s under pristine dir %s" % (fname, pristine))
    if (pristine / "kiss_fft.c").read_bytes().decode("utf-8") \
            .count("MSF Fork B"):
        return fail("pristine dir already carries the Fork B marker - "
                    "pass the unpatched fetched tree")

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(pristine, out)

    for fname, old, new in PATCHES:
        p = out / fname
        # Bytes in, bytes out: no newline translation anywhere, so
        # the patched hashes are platform-independent.
        text = p.read_bytes().decode("utf-8")
        n = text.count(old)
        if n != 1:
            return fail("%s: expected patch anchor occurs %d times "
                        "(want exactly 1) - source drift, refusing"
                        % (fname, n))
        p.write_bytes(text.replace(old, new).encode("utf-8"))
        print("patched %s" % fname)

    patched = {fname for fname, _, _ in PATCHES}
    if rel_files(pristine) != rel_files(out):
        return fail("patched tree file set differs from pristine")
    for rel in rel_files(pristine):
        a = sha256_file(pristine / rel)
        b = sha256_file(out / rel)
        if rel in patched:
            if b != EXPECTED_SHA256[rel]:
                return fail("%s: patched sha256 %s, recorded value is %s"
                            % (rel, b, EXPECTED_SHA256[rel]))
            if a == b:
                return fail("%s: patch left the file unchanged" % rel)
        elif a != b:
            return fail("%s: unpatched file changed bytes" % rel)
    print("FORKB-PATCH OK (3 sites; patched sha256 match the recorded values)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
