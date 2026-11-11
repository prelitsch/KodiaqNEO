#!/bin/sh
# READ-ONLY BASELINE COLLECTOR. No installer, log file, backup, SD probe or remount.
# Prepared offline; not executed or empirically verified on the vehicle.
# Only stdout/stderr output. Never source an installer or interpret an install marker.
MODE=DEVICE_READ_ONLY
PREFIX=
if [ "$#" -ne 0 ]; then
    if [ "$#" -eq 2 ] && [ "$1" = --offline-fixture ]; then
        MODE=OFFLINE_SIMULATION
        PREFIX=$2
        case "$PREFIX" in /*) ;; *) echo 'FAILED=fixture must be an absolute POSIX path'; exit 1 ;; esac
    else
        echo 'FAILED=only --offline-fixture PATH is accepted; no install or restore mode'
        exit 1
    fi
fi
APP="$PREFIX/net/mmx/mnt/app"
IMG="$APP/eso/hmi/lsd/Resources/skin3/images.mcf"
PC="$APP/eso/bin/apps/pc"
SHA="$PREFIX/net/rcc/usr/bin/sha1sum"
V3="$PREFIX/net/mmx/fs/sda0/mod/neoui/v3"
echo 'NEOUI_BASELINE_RECEIPT=1'
echo "MODE=$MODE"
echo 'WRITE_POLICY=STDOUT_ONLY'
echo 'RELEASE_READY=false'
fail() { echo "FAILED=$*"; echo 'END=FAILED'; exit 1; }
utc_now() {
    if command -v date >/dev/null 2>&1; then
        NOW=$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null) || NOW=
        [ -n "$NOW" ] && { echo "$NOW"; return 0; }
    fi
    echo UNKNOWN
}
for cmd in on awk wc ls df mount; do
    command -v "$cmd" >/dev/null 2>&1 || fail "missing dependency: $cmd"
done
for marker in INSTALL_V3_NOW RESTORE_V2 DIAGNOSTIC_ONLY; do
    [ ! -e "$V3/$marker" ] || fail "marker $marker present; this collector cannot install/restore"
done
[ -x "$PC" ] && [ -x "$SHA" ] || fail 'firmware reader or SHA1 executable missing'
[ -f "$IMG" ] && [ ! -L "$IMG" ] || fail 'target absent, not regular or symbolic link'
START=$(utc_now)
echo "START_UTC=$START"
# Preserve subprocess status before parsing; never strip arbitrary garbage into a match.
T=$(on -f mmx "$PC" s:30:1966084) || fail 'firmware train read failed'
M=$(on -f mmx "$PC" s:30:1966083) || fail 'MU read failed'
T=$(echo "$T" | awk 'NF {if(NF!=1 || ++n!=1) exit 1; v=$1} END {if(n!=1) exit 1; print v}') || fail 'ambiguous train output'
M=$(echo "$M" | awk 'NF {if(NF!=1 || ++n!=1) exit 1; v=$1} END {if(n!=1) exit 1; print v}') || fail 'ambiguous MU output'
echo "FIRMWARE=$T"
echo "MU=$M"
[ "$T" = MHI2_ER_SKG13_P4526 ] && [ "$M" = 1440 ] || fail 'unsupported firmware/MU'
echo 'TARGET=/net/mmx/mnt/app/eso/hmi/lsd/Resources/skin3/images.mcf'
echo 'SELECTED_SKIN=UNKNOWN'
echo 'SELECTED_SKIN_METHOD=no verified read-only selector query; record Engineering Menu observation separately'
hash_file() {
    LINE=$("$SHA" "$1") || return 1
    H=$(echo "$LINE" | awk 'NR==1 && length($1)==40 && $1 !~ /[^0-9a-f]/ {v=$1; ok=1} END {if(NR!=1 || !ok) exit 1; print v}') || return 1
    echo "$H"
}
H1=$(hash_file "$IMG") || fail 'installed hash unavailable/UNKNOWN; no retry or bypass'
BYTES=$(wc -c < "$IMG") || fail 'target size unavailable'
BYTES=$(echo "$BYTES" | awk 'NF==1 && $1 ~ /^[0-9]+$/ {print $1; ok=1} END {if(!ok) exit 1}') || fail 'invalid byte length'
ATTR=$(ls -ldn "$IMG") || fail 'target attributes unavailable'
echo "CURRENT_SHA1=$H1"
echo "CURRENT_BYTES=$BYTES"
echo "ATTRIBUTES=$ATTR"
case "$H1" in
    0a322d581cb320c60bc6be87e2817fcdf20aa2f2) STATE=mib_pre_neoui ;;
    641c34e42ed5843c1795bf860fd4cb7bbb913fdb) STATE=neoui_v1 ;;
    28e26e2603497571663a93b303e930a2d4787f50) STATE=neoui_v2_pilot ;;
    *) fail 'unrecognized installed state; retain evidence and investigate' ;;
esac
echo "REFERENCE_MATCH=$STATE"
SHA256=$(command -v sha256sum) || SHA256=
if [ -n "$SHA256" ]; then
    L256=$("$SHA256" "$IMG") || fail 'SHA256 utility failed'
    H256=$(echo "$L256" | awk 'NR==1 && length($1)==64 && $1 !~ /[^0-9a-f]/ {v=$1; ok=1} END {if(NR!=1 || !ok) exit 1; print v}') || fail 'invalid SHA256 result'
    echo "CURRENT_SHA256=$H256"
else
    echo 'CURRENT_SHA256=UNKNOWN'
fi
for NAME in images.res viewhandler.zip info.txt ambienceColorMap.res; do
    F="$APP/eso/hmi/lsd/Resources/skin3/$NAME"
    [ -f "$F" ] && [ ! -L "$F" ] || fail "missing/linked metadata $NAME"
    META=$(hash_file "$F") || fail "metadata hash failed: $NAME"
    echo "METADATA_${NAME}=$META"
done
DF_TEXT=$(df -k "$APP") || fail 'df command failed'
echo 'DF_RAW_BEGIN'
echo "$DF_TEXT"
echo 'DF_RAW_END'
# Firmware-observed pattern, strengthened: exactly one /dev row and one percent field.
FREE=$(echo "$DF_TEXT" | awk '
    $1 ~ /^\/dev\// {
        rows++; pct=0
        point=$NF; sub(/\/$/, "", point)
        if(point!="/mnt/app" && point!="/net/mmx/mnt/app") bad=1
        for(i=1;i<=NF;i++) if($i ~ /^[0-9]+%$/) {
            pct++; if(i<2 || $(i-1) !~ /^[0-9]+$/) bad=1; else free=$(i-1)
            percent=$i; sub(/%$/, "", percent); if(percent+0>100) bad=1
        }
        if(pct!=1) bad=1
    }
    END {if(rows!=1 || bad) exit 1; print free}
') || fail 'ambiguous/invalid QNX df row; do not use Linux column positions'
case "$FREE" in ''|*[!0-9]*) fail 'invalid free-block count' ;; esac
echo "APP_FREE_KIB=$FREE"
MOUNTS=$(mount) || fail 'mount-state listing failed'
echo 'MOUNTS_RAW_BEGIN'
echo "$MOUNTS"
echo 'MOUNTS_RAW_END'
echo 'APP_MOUNT_STATE=UNINTERPRETED_RAW_OUTPUT_REQUIRES_REVIEW'
# No payload-size assumption or fixed 100MiB success claim at discovery time.
echo 'STORAGE_RELEASE_BUDGET=NOT_CALCULATED_UNTIL_FINAL_PAYLOAD_AND_STRATEGY'
H2=$(hash_file "$IMG") || fail 'final stability hash failed'
B2=$(wc -c < "$IMG") || fail 'final stability size failed'
B2=$(echo "$B2" | awk '{if(NF!=1 || $1 !~ /^[0-9]+$/) exit 1; print $1}') || fail 'invalid final size'
A2=$(ls -ldn "$IMG") || fail 'final attributes failed'
[ "$H1" = "$H2" ] && [ "$BYTES" = "$B2" ] && [ "$ATTR" = "$A2" ] || fail 'target changed during collection'
echo 'STABLE_DURING_COLLECTION=true'
echo 'POST_REBOOT_VERIFICATION=UNKNOWN'
END_TIME=$(utc_now)
echo "END_UTC=$END_TIME"
echo 'END=COLLECTED_NOT_RELEASE_AUTHORIZATION'
exit 0
