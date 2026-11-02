#!/usr/bin/env bash
# pdfx: extract printed-page text for 754-2019 sections 5.3.3 and 5.10 (read-only,
# working notes only; no standard text is copied into any report or vector file).
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
"$PY" -c "
from pypdf import PdfReader
r = PdfReader('754-2019.pdf')
print('pages:', len(r.pages))
full = []
for i, p in enumerate(r.pages):
    t = p.extract_text() or ''
    full.append(t)
all_t = chr(10).join(full)
import re
for tag in ['5.10', '5.3.3']:
    idxs = [m.start() for m in re.finditer(r'(?m)^5\.10[ \t]|(?m)^5\.3\.3[ \t]', all_t)]
    print(tag, 'heading-hits:', len(idxs))
" 2>&1 | head -n 20
