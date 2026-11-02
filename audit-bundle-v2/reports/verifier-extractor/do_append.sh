cd /c/Users/logan/source/repos/Muse-Softfloat || exit 99
export TMPDIR="$PWD/scratch/verifier-extractor"
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-extractor"
export TEMP="$TMP"
softfloat-bootstrap-kit/tools/ledger.sh append ledger verifier-extractor "verdict READY on 8770745: Wave 0 metrics extraction holds, 7 notes" < /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-extractor/ledger_body.txt
echo "rc=$?"
