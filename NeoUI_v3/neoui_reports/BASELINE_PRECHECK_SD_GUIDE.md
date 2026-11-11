# NeoUI v3 logged read-only precheck (precheck only)

This package runs the read-only baseline collector through M.I.B. and saves the complete collector stdout/stderr, full `skin3/info.txt` contents, and exit status to a new numbered log on the SD card. The launcher logs and refuses installation and restore markers. It contains no skin payload or installer. The collector does not write to the vehicle; the launcher writes only its receipt log to SD. The selected skin remains UNKNOWN and must be observed separately in Engineering Menu without changing it.

## Copy to SD

1. Back up the SD card's current `mod/command.sh` to the PC. Do not run an unknown existing command.
2. Copy `mod/command.sh` and `mod/neoui/v3/baseline_precheck.sh` from this package to the same paths on SD. Keep your original launcher backup.
3. Safely eject, insert into the car, then open M.I.B. -> `advanced_settings` -> `run_individual_script`.
4. The launcher verifies it can create and read an SD log before it accesses vehicle files. If that fails, it stops and reports the failure on-screen; no vehicle paths were accessed. Missing collector or marker refusal is also written to the log.
5. On completion, the screen shows `LOG_FILE=...`. The full receipt is saved there, including a failure line and exit code. M.I.B.'s “it is all done!” message is generic; use `PRECHECK_COLLECTOR_EXIT` and `END=` in the log.
6. After the run, safely remove the SD, restore the original `mod/command.sh`, and copy the newest `mod/neoui/v3/logs/precheck_N.log` from SD to the PC. Send that file back.

Do not create `INSTALL_V3_NOW` or `RESTORE_V2`; this package will refuse if either is present. It cannot install. V3 installation remains blocked pending release review and a validated QNX installation/rollback workflow. Do not use this package as an installer.