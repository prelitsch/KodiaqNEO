#!/bin/sh
# NeoUI v3 baseline precheck launcher for M.I.B. individual-script menu.
# Runs only the stdout-only collector. No install, restore, SD writes or vehicle writes.
SCRIPT=/net/mmx/fs/sda0/mod/neoui/v3/baseline_precheck.sh
if [ ! -f "$SCRIPT" ]; then
    echo 'PRECHECK_LAUNCH_FAILED=collector missing from SD'
    exit 1
fi
echo 'PRECHECK_LAUNCH=starting read-only baseline collector'
sh "$SCRIPT"
STATUS=$?
echo "PRECHECK_COLLECTOR_EXIT=$STATUS"
if [ "$STATUS" -eq 0 ]; then
    echo 'PRECHECK_RESULT=collection completed; this is not install authorization'
else
    echo 'PRECHECK_RESULT=failed; do not install; preserve all output'
fi
exit "$STATUS"