# NeoUI v3 read-only baseline precheck kit

This kit gathers the current MIB2.5 baseline and prints the receipt to the M.I.B. individual-script screen. It does not install, restore, change permissions, remount filesystems, create a log, back up files, or write to the head unit. Keep v3 installation blocked after collection.

If the firmware environment has no `date` command, collection continues and prints `START_UTC=UNKNOWN` and `END_UTC=UNKNOWN`. The PC reviewer will mark freshness incomplete; do not substitute a guessed timestamp.

## Kit contents

- `mod/command.sh`: temporary M.I.B. launcher. It invokes the collector and prints its exit status. M.I.B.'s own menu script prints “it is all done!” regardless of the child's exit status, so use `PRECHECK_COLLECTOR_EXIT` and the collector's `END=` line to determine the result.
- `mod/neoui/v3/baseline_precheck.sh`: the stdout-only collector.

## Prepare the SD card on the PC

1. Back up the SD card's current `mod/command.sh` to the PC. Do not run the existing command blindly; it may invoke an older installer or other commands.
2. Copy the kit's `mod/neoui/v3/baseline_precheck.sh` to the same path on the SD card, creating `mod/neoui/v3` if needed.
3. Temporarily replace SD `mod/command.sh` with the kit's `mod/command.sh`. Keep the original PC backup so you can restore it after collection.
4. Safely eject the SD card.

The SD card writes above are only kit placement. This precheck's vehicle-side execution is read-only. Do not add any install/restore marker files. Do not run any v2/v3 installer.

## Run through M.I.B.

1. Insert the SD card and open M.I.B.
2. Choose `advanced_settings` -> `run_individual_script`.
3. Let the output finish. Do not interrupt the script or remove the SD card while it is running.
4. Capture the complete output from `NEOUI_BASELINE_RECEIPT=1` through the final `END=` line. Photograph each screen if the interface does not allow copying text. Include any M.I.B. lines immediately before and after the collector output.
5. A usable successful collection ends with `END=COLLECTED_NOT_RELEASE_AUTHORIZATION` and `PRECHECK_COLLECTOR_EXIT=0`. Any `FAILED=` line or nonzero exit means stop and send the complete output; do not retry with edits or bypasses. An `UNKNOWN` timestamp can still provide baseline identity, but freshness remains incomplete.
6. Turn the unit off normally, remove the SD when safe, and restore the original `mod/command.sh` from the PC backup. The collector itself creates no SD log, so capture the screen output before leaving the menu.

## Send back

Send the entire captured output, not only the hash. Also report the Engineering Menu's currently selected skin/index as observed without changing it, whether the head unit starts normally after its most recent normal reboot, and whether the v2 MENU appears functional. These observations are separate from the script receipt.

This output is evidence for offline review only. It does not authorize an installation. Unknown hash, skin selection, metadata, mount state, reboot behavior and recovery checks can keep release blocked.