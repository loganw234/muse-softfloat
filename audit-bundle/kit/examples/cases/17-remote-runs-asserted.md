# A run elsewhere, its SHA and content asserted apart

HonestFramework METHOD.md section 6: assert the SHA and the content separately. Two more instances sit in other samples: 7a's bullet on an empty clone, and 11a's clone asserted before the run.

## 17a. A clone asserted before a run on the card

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "cft_last_error() belongs to the call that just returned", line 23296. Not in this kit.
- **What it shows** (the kit's reading): A run on another machine, from a clone whose SHA and content were asserted apart before it built.
- **Cut:** nothing.

> - **On the card: the lead's run, 2026-10-22 08:41 to 08:42, MEASURED** (records in `Data/runs/2026-10-12-math-round/box/p2bcard/`: the driver script, its summary, the N1 patch and six logs, two builds and four device-test runs, nine files, with the box's SHA256SUMS and its check). On amd-arc-box, from a clone of this branch at 8513fc1d (the SHA and the content asserted apart: HEAD equal and 0 changed files, `CFT_XRT_UPLOAD` found 6 times in backend_xrt.cpp and 12 in device_test.c, the patch's sha256 starting 679968c5e4e504c1), built `XRT=1` (rc 0, 0 warnings, `ldd` names XRT, the build id reads commit=8513fc1d tracked=clean) and run through `hw/run-device-test.sh <image> -b -n 96` on the U50, XRT 2.19.194, kernel clock 135 MHz, on the rev8q quad image (sha256 4f9921a25af6..., 4 tiles) and the rev8a single image (sha256 0639248e9c66..., 1 tile):

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
