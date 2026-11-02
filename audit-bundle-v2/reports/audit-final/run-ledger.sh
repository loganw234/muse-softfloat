#!/bin/sh
# auditor-final ledger append (run from workspace root). Appends one entry;
# provenance: child-written file appended by this script, stated here.
LEDGER="ledger/auditor-final.md"
ENTRY="scratch/audit-final/ledger-entry.md"
printf '\n' >> "$LEDGER"
cat "$ENTRY" >> "$LEDGER"
echo "appended $ENTRY -> $LEDGER"
