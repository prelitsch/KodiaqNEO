# Logged M.I.B. precheck package

Package: `neoui_build/NeoUI_v3_logged_precheck_sd.zip`

This is a **precheck-only** package. Its M.I.B. launcher creates a new numbered log on SD, verifies that the log can be read, and then captures collector stdout/stderr, exit status, the complete `Resources/skin3/info.txt` contents, firmware identity, MCF hashes/size/attributes, raw free-space and mount output, and stability results. Missing collector or install/restore markers are logged and refused. If SD log creation/readback fails, it exits before reading vehicle paths. It contains no v3 payload and no installation/restore code.

The user's v2 reboot and MENU operation confirmation is recorded in `LIVE_BASELINE_OBSERVATIONS.md`. Selected skin/index remains unknown. Therefore this package cannot install v3. A write-capable installer is still blocked pending release review and QNX write/rollback failure-path validation; an untested vehicle writer cannot be promised fail-safe.

The shell scripts pass Git for Windows Bash syntax checks. QNX execution of the new logger has not been tested. The package was prepared on PC; no SD or vehicle operation was performed here.

SHA-256: `08c11ca7d4c2c05e929ba89ecdbca96dda9a8e5ba9bbbc2760f437adb336f152`
