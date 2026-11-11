#!/bin/sh
# Logged, precheck-only M.I.B. individual-script launcher.
SD=/net/mmx/fs/sda0
V3="$SD/mod/neoui/v3"
LOGDIR="$V3/logs"
SCRIPT="$V3/baseline_precheck.sh"
if ! mkdir -p "$LOGDIR"; then
    echo 'PRECHECK_LOG_FAILED=cannot create SD log directory; no vehicle files were accessed'
    exit 1
fi
N=1
while [ -f "$LOGDIR/precheck_$N.log" ]; do N=$((N+1)); done
LOG="$LOGDIR/precheck_$N.log"
if ! (echo 'NEOUI_LOG_WRAPPER=1' > "$LOG") 2>/dev/null; then
    echo 'PRECHECK_LOG_FAILED=cannot create SD log; no vehicle files were accessed'
    exit 1
fi
CHECK=$(cat "$LOG" 2>/dev/null)
if [ "$CHECK" != 'NEOUI_LOG_WRAPPER=1' ]; then
    echo 'PRECHECK_LOG_FAILED=SD log readback mismatch; no vehicle files were accessed'
    exit 1
fi
sync
{
    echo "LOG_FILE=$LOG"
    echo 'PRECHECK_RUN=BEGIN'
    if [ -f "$V3/INSTALL_V3_NOW" ] || [ -f "$V3/RESTORE_V2" ]; then
        echo 'INSTALL_BLOCKED=this package is precheck-only; remove install/restore markers; no vehicle files accessed'
        STATUS=1
    elif [ ! -f "$SCRIPT" ]; then
        echo 'PRECHECK_LAUNCH_FAILED=collector missing from SD; no vehicle files accessed'
        STATUS=1
    else
        sh "$SCRIPT"
        STATUS=$?
    fi
    echo "PRECHECK_COLLECTOR_EXIT=$STATUS"
    if [ "$STATUS" -eq 0 ]; then
        echo 'PRECHECK_RESULT=collection completed; not install authorization'
    else
        echo 'PRECHECK_RESULT=failed or blocked; preserve this log; do not install'
    fi
    echo 'PRECHECK_RUN=END'
} >> "$LOG" 2>&1
RUN_STATUS=$STATUS
sync
cat "$LOG"
exit "$RUN_STATUS"