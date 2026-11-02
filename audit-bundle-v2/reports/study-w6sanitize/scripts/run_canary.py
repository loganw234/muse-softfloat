import subprocess, sys, os
# Run each argv[1:] command, report true Windows return code + output.
for spec in sys.argv[1:]:
    parts = spec.split("|")
    try:
        p = subprocess.run(parts, capture_output=True, text=True, timeout=30)
        out = (p.stdout + p.stderr).strip().replace("\n", " ")[:240]
        print(f"RC={p.returncode} CMD={' '.join(parts)} :: {out}", flush=True)
    except subprocess.TimeoutExpired:
        print(f"RC=TIMEOUT CMD={' '.join(parts)}", flush=True)
    except OSError as e:
        print(f"RC=OSERROR CMD={' '.join(parts)} :: {e}", flush=True)
