#!/bin/sh
# NeoUI v2 PILOT installer for M.I.B. 3.6.0, exact SKG13 P4526 MU1440 only.
# Default: safe read-only / backup-only PRECHECK. Installation requires INSTALL_V2_NOW marker.
# Does not touch skin0, HOME HMI viewhandler, or navigation map resources.
SD=${NEOUI_SD:-/net/mmx/fs/sda0}
IMG=${NEOUI_IMG:-/net/mmx/mnt/app/eso/hmi/lsd/Resources/skin3/images.mcf}
APP=${NEOUI_APP:-/net/mmx/mnt/app}
SHA=${NEOUI_SHA:-/net/rcc/usr/bin/sha1sum}
TEST=${NEOUI_SIMULATION:-0}
NEO="$SD/mod/neoui"
V2="$NEO/v2"
PAY="$V2/NeoUI_v2_pilot_skin3.mcf"
V1_SHA=641c34e42ed5843c1795bf860fd4cb7bbb913fdb
V2_SHA=28e26e2603497571663a93b303e930a2d4787f50
UPSTREAM_SHA=0a322d581cb320c60bc6be87e2817fcdf20aa2f2
SD_BAK="$V2/backups/skin3_NeoUI_v1_before_v2.mcf"
DEV_BAK="$IMG.neoui-v1-before-v2"
TMP="$IMG.neoui-v2.tmp"
LOG="$V2/NeoUI_v2_result.txt"
LOG_OK=0
say() {
    echo "NeoUI v2: $*"
    if [ "$LOG_OK" = 1 ]; then
        (echo "NeoUI v2: $*" >> "$LOG") 2>/dev/null || echo "NeoUI v2: WARNING: logging failed"
    fi
}
sha() {
    line=$($SHA "$1" 2>/dev/null) || return 1
    set -- $line
    [ -n "$1" ] || return 1
    echo "$1" | tr 'ABCDEF' 'abcdef'
}
fail() { say "FAILED - $*"; return 1; }
app_rw() {
    [ "$TEST" = 1 ] && return 0
    mount -uw "$APP"
}
app_ro() {
    [ "$TEST" = 1 ] && return 0
    mount -ur "$APP"
}
sd_test() {
    [ -d "$V2" ] || { echo "NeoUI v2: FAILED - $V2 missing"; return 1; }
    if [ "$TEST" != 1 ]; then mount -uw "$SD/" >/dev/null 2>&1 || echo "NeoUI v2: SD remount warning, testing access"; fi
    P="$V2/.v2_probe_$$"
    if ! (echo 'NEOUI_V2_RW_OK' > "$P") 2>/dev/null; then
        echo "NeoUI v2: FAILED - SD not writable; no app changes"
        return 1
    fi
    R=$(cat "$P" 2>/dev/null)
    rm -f "$P" 2>/dev/null
    [ "$R" = NEOUI_V2_RW_OK ] || { echo "NeoUI v2: FAILED - SD write readback mismatch"; return 1; }
    if ! (echo 'NeoUI v2: --- session ---' >> "$LOG") 2>/dev/null; then
        echo "NeoUI v2: FAILED - SD log not writable"; return 1
    fi
    LOG_OK=1
    say 'SD write/readback passed'
}
train() {
    if [ "$TEST" = 1 ]; then say 'Simulation firmware check'; return 0; fi
    PC=/net/mmx/mnt/app/eso/bin/apps/pc
    [ -f "$PC" ] || { fail 'Firmware reader missing'; return 1; }
    T=$(on -f mmx "$PC" s:30:1966084 2>/dev/null | sed 's/[^a-zA-Z0-9_-]//g')
    M=$(on -f mmx "$PC" s:30:1966083 2>/dev/null | sed 's/[^a-zA-Z0-9_-]//g')
    say "Firmware: ${T:-UNKNOWN} / MU${M:-UNKNOWN}"
    [ "$T" = MHI2_ER_SKG13_P4526 ] && [ "$M" = 1440 ] || { fail 'Firmware mismatch'; return 1; }
}
verify_payload() {
    [ -f "$PAY" ] || { fail 'Payload missing'; return 1; }
    H=$(sha "$PAY") || H=UNKNOWN
    [ "$H" = "$V2_SHA" ] || { fail "Payload checksum incorrect: $H"; return 1; }
    say 'Payload checksum verified'
}
backup_v1() {
    mkdir -p "$V2/backups" || { fail 'Cannot create SD backup directory'; return 1; }
    if [ -f "$SD_BAK" ]; then
        H=$(sha "$SD_BAK") || H=UNKNOWN
        [ "$H" = "$V1_SHA" ] || { fail 'Existing SD v1 backup invalid'; return 1; }
        say 'SD backup of v1 verified'
        return 0
    fi
    rm -f "$SD_BAK.partial" || { fail 'Cannot remove partial SD backup'; return 1; }
    cp "$IMG" "$SD_BAK.partial" || { fail 'SD v1 backup copy failed'; return 1; }
    H=$(sha "$SD_BAK.partial") || H=UNKNOWN
    [ "$H" = "$V1_SHA" ] || { fail 'SD v1 backup checksum mismatch'; return 1; }
    mv "$SD_BAK.partial" "$SD_BAK" || { fail 'SD backup rename failed'; return 1; }
    sync
    say 'SD backup of v1 saved and verified'
}
precheck() {
    train || return 1
    verify_payload || return 1
    [ -f "$IMG" ] || { fail 'Target skin3 missing'; return 1; }
    H=$(sha "$IMG") || H=UNKNOWN
    say "Current installed skin3 SHA1: $H"
    [ "$H" = "$V1_SHA" ] || { fail 'Installed skin3 is not the expected v1. Refusing upgrade'; return 1; }
    backup_v1 || return 1
    say 'PRECHECK OK - v1 backed up; no app files modified'
}
backup_device() {
    if [ -f "$DEV_BAK" ]; then
        H=$(sha "$DEV_BAK") || H=UNKNOWN
        [ "$H" = "$V1_SHA" ] || { fail 'Existing on-device v1 backup invalid'; return 1; }
        say 'On-device v1 backup verified'
        return 0
    fi
    rm -f "$DEV_BAK.partial" || { fail 'Removing stale device backup failed'; return 1; }
    cp "$IMG" "$DEV_BAK.partial" || { fail 'On-device v1 backup failed'; return 1; }
    H=$(sha "$DEV_BAK.partial") || H=UNKNOWN
    [ "$H" = "$V1_SHA" ] || { fail 'On-device backup checksum invalid'; return 1; }
    mv "$DEV_BAK.partial" "$DEV_BAK" || { fail 'Finalizing device backup failed'; return 1; }
    sync
    say 'On-device v1 backup verified'
}
install() {
    precheck || return 1
    say 'INSTALL explicitly armed; touching app filesystem now'
    app_rw || { fail 'Unable to remount app RW'; return 1; }
    if ! backup_device; then app_ro; return 1; fi
    rm -f "$TMP" || { app_ro; fail 'Cannot remove temporary file'; return 1; }
    if ! cp "$PAY" "$TMP"; then rm -f "$TMP"; app_ro; fail 'Staging payload failed'; return 1; fi
    H=$(sha "$TMP") || H=UNKNOWN
    if [ "$H" != "$V2_SHA" ]; then rm -f "$TMP"; app_ro; fail 'Staged payload SHA1 mismatch'; return 1; fi
    chmod +x "$TMP" || { rm -f "$TMP"; app_ro; fail 'Cannot set file attributes'; return 1; }
    if ! mv "$TMP" "$IMG"; then app_ro; fail 'Replacing skin3 failed'; return 1; fi
    sync
    H=$(sha "$IMG") || H=UNKNOWN
    if [ "$H" != "$V2_SHA" ]; then
        say 'CRITICAL: Post-install checksum failure, trying rollback to v1'
        if cp "$DEV_BAK" "$TMP" && [ "$(sha "$TMP")" = "$V1_SHA" ] && mv "$TMP" "$IMG"; then
            sync
            say 'Rollback file restored; inspect before reboot'
        else
            say 'CRITICAL: automatic rollback failed; do not reboot'
        fi
        app_ro
        fail 'Post-install verification failed'
        return 1
    fi
    if ! app_ro; then fail 'Installed, but app remount RO failed; do not reboot'; return 1; fi
    say 'SUCCESS - Installed NeoUI v2 MENU Pilot graphics. Only skin3/images.mcf changed.'
}
restore_v1() {
    train || return 1
    [ -f "$IMG" ] || { fail 'Target skin3 missing'; return 1; }
    H=$(sha "$IMG") || H=UNKNOWN
    [ "$H" = "$V2_SHA" ] || { fail 'Current skin is not expected v2; no restore'; return 1; }
    if [ -f "$DEV_BAK" ]; then SOURCE="$DEV_BAK"; else SOURCE="$SD_BAK"; fi
    [ -f "$SOURCE" ] || { fail 'No backup of v1'; return 1; }
    H=$(sha "$SOURCE") || H=UNKNOWN
    [ "$H" = "$V1_SHA" ] || { fail 'v1 rollback checksum mismatch'; return 1; }
    app_rw || { fail 'Cannot remount app for restore'; return 1; }
    rm -f "$TMP" || { app_ro; fail 'Cannot clear restore temp'; return 1; }
    if ! cp "$SOURCE" "$TMP"; then app_ro; fail 'Staging restore failed'; return 1; fi
    H=$(sha "$TMP") || H=UNKNOWN
    [ "$H" = "$V1_SHA" ] || { rm -f "$TMP"; app_ro; fail 'Restore checksum mismatch'; return 1; }
    chmod +x "$TMP" || { rm -f "$TMP"; app_ro; fail 'Restore attributes failed'; return 1; }
    mv "$TMP" "$IMG" || { app_ro; fail 'Restore replacement failed'; return 1; }
    sync
    H=$(sha "$IMG") || H=UNKNOWN
    if ! app_ro; then fail 'Restore written but remount RO failed'; return 1; fi
    [ "$H" = "$V1_SHA" ] || { fail 'Final restore checksum mismatch'; return 1; }
    say 'SUCCESS - NeoUI v1 restored. Reboot only after this message.'
}

say 'NeoUI v2 PILOT (MENU and UI controls only; HOME layout and nav unchanged)'
sd_test || exit 1
if [ -f "$V2/INSTALL_V2_NOW" ] && [ -f "$V2/RESTORE_V1" ]; then fail 'Conflicting INSTALL and RESTORE markers'; exit 1; fi
if [ -f "$V2/RESTORE_V1" ]; then
    say 'MODE: RESTORE V1'; restore_v1; STATUS=$?
elif [ -f "$V2/INSTALL_V2_NOW" ]; then
    say 'MODE: INSTALL v2 (armed)'; install; STATUS=$?
else
    say 'MODE: PRECHECK ONLY'; precheck; STATUS=$?
fi
if [ "$STATUS" -eq 0 ]; then say 'END: completed'; else say 'END: FAILED - do not reboot expecting success'; fi
exit "$STATUS"
