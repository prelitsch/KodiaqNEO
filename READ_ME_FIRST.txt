Kodiaq NeoUI - SD v1.2 compatibility fix
=======================================

Your screen confirmed that the previous SD remount returned status 0, but both
write tests failed because `printf` is not available on this Columbus. These
scripts use shell `echo` instead. This is a script compatibility problem; the
previous test did not prove the SD card was read-only.

STEP 1 - DIAGNOSTIC ONLY (do this FIRST)
1. Keep a backup of E:\mod\neoui\run.sh on the PC.
2. Copy 1_DIAGNOSTIC\run.sh -> E:\mod\neoui\run.sh (overwrite there).
3. Do not touch E:\mod\command.sh or E:\mod\neoui\NeoUI_v1_skin3_images.mcf.
4. Confirm that E:\mod\neoui\INSTALL_NOW does NOT exist.
5. Safely eject, insert SD1, open GEM > M.I.B. > Advanced Settings > Run individual script.
6. Wait for both:
   NeoUI: SD ROOT WRITE AND READ-BACK OK
   NeoUI: NEOUI FOLDER WRITE AND READ-BACK OK
   and final: NeoUI: DIAGNOSTIC PASS - SD is writable
7. Take a photo and send it back BEFORE proceeding.

STEP 2 - PRECHECK / BACKUP (only after confirming STEP 1)
1. Return the card to the laptop.
2. Copy 2_INSTALLER_AFTER_SUCCESS\run.sh -> E:\mod\neoui\run.sh.
3. Ensure INSTALL marker exists and INSTALL_NOW does NOT exist. Do not create RESTORE.
4. Run Individual Script again. This should test checksums, save a verified
   backup to the SD, and report PRECHECK OK without replacing the installed skin.
5. Verify SD backup checksum on Windows and only then consider arming installation.

WARNING: The experimental actual skin installation is NOT the first step.
Do not create INSTALL_NOW or flash anything before the precheck and backup have
been checked. A valid MCF checksum doesn't prove it will display correctly in
Columbus. This fix does not change app/firmware files during the diagnostic.
