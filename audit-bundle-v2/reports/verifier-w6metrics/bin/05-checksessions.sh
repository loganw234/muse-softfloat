#!/bin/bash
# Verify child session dirs exist under the lead session store.
set -u
LEAD="C:/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971"
ls "$LEAD" 2>&1
echo "=== subagent count ==="
ls "$LEAD/subagent" 2>&1 | wc -l
for s in 10cd2f59-c609-7290-8082-8ba117d5e688 76db86d8-0507-76af-8538-ec8742014c07 ecdd2639-b5e1-749a-8856-d9fbd60b8eb2 adcb269a-91cc-7545-8516-cd94fbbaa08d e7eab46e-c640-7bef-87b3-7aeba9104c37 aea58a8b-5978-7113-8f5d-87b02f0378ab 294ada8c-2d1c-7568-8b3d-f708f46139b0; do
  if [ -f "$LEAD/subagent/$s/session.jsonl" ]; then echo "FOUND $s"; else echo "MISSING $s"; fi
done
