# AGENTS.md — NeoUI for 2017 Škoda Kodiaq Columbus MIB2.5

> This file is the standing instruction set for Codex when opened at the **Kodiaq Moding** project root. Read `NEOUI_PROJECT_CONTEXT.md`, `NEOUI_TECHNICAL_STATE.md`, `NEOUI_DESIGN_AND_ROADMAP.md`, and `NEOUI_RESEARCH_TASKS.md` before changing anything.

## Mission
Build **NeoUI**: a coherent, modern, OEM-credible **Graphite & Ice** visual skin for a 2017 Kodiaq Columbus MIB2.5 (MHI2_ER_SKG13_P4526, MU1440). User wants real firmware graphics, not image-generation mockups. They like the **currently active M.I.B. Image MOD MENU** and want to retain its best elements while modernizing the entire UI. Target views: HOME (split map + phone/favorites/media widgets, with different connection states), MENU, NAVIGATION action strip/POI markers, FAHRZEUG, SETTINGS/list screens, MEDIEN/BT and shared states. Preserve layout/behavior, language, safety indications, legibility and touchscreen hit zones.

## Highest-priority architectural choice
**Preferred:** a NEW, independently selectable NeoUI skin/slot alongside the existing M.I.B. skin, preserving the stock and current M.I.B. options. The user's prior NeoUI v1 modified `/net/mmx/mnt/app/eso/hmi/lsd/Resources/skin3/images.mcf` **in place**; this is NOT independent. Investigate actual resource directories, installed `info.txt`/configuration and selection references, upstream SKG13 Image MOD installation scripts, compiled view-handler dependencies and live switch behavior. Do not assume `skin4` or any other index is supported. Creating a directory or copying an MCF there alone is NOT proof of a selectable skin. Do not overwrite stock/M.I.B. to fake independence.

Only when independent-slot support is **documented and verified for this exact firmware**, implement it. Record which resources are shared and whether nav modifications apply globally across skins. If uncertain, DO NOT patch selector code, root filesystem, viewhandler, nor NVRAM parameters. **Fallback:** generate a reversible versioned skin3 upgrade built from the **verified currently installed** state (v2 once confirmed after reboot), with a way to restore exact previous bytes; do not assume the on-car state is still v1. Report honestly that fallback replaces the current M.I.B.-derived `skin3` rather than adding a selectable third skin.

## NON-NEGOTIABLE safety/release rules
1. **No automatic operations on the vehicle.** Work off-car, read-only source discovery, dry-runs, previews and validation by default. User explicitly authorizes any actual installation after inspecting a release report. Never touch vehicle-connected hardware from the dev PC or perform a flash unattended.
2. **Do not modify live hardware on assumptions.** Need proof of source, target, checksum, file permissions, scripts and rollback compatibility; identify boot-recovery limitations.
3. Support **only** `MHI2_ER_SKG13_P4526` / `MU1440` until evidence for others. Check these at installation time. Reject unknown firmware and unexpected hashes. Provide a safe PRECHECK-only mode; after offline validation and explicit user approval, a marker-armed installer MAY run the identical mandatory precheck followed by install in the **same invocation**, aborting before application writes on any failure. See the v2 field-tested release workflow below.
4. Original files, M.I.B. active skin, NeoUI v1, and NeoUI v2 need distinct labeled backups and SHA-1/SHA-256 entries; original M.I.B. skin3 SHA1 `0a322d581cb320c60bc6be87e2817fcdf20aa2f2`, installed NeoUI v1 payload SHA1 `641c34e42ed5843c1795bf860fd4cb7bbb913fdb`, and v2 pilot payload SHA1 `28e26e2603497571663a93b303e930a2d4787f50`. Backup naming must make source state obvious. A working skin3 upgrade may be unsafe if GUI no longer loads; script rollback is not a recovery guarantee.
5. NEVER silently modify `skin0`, `skin1`, `skin2`, user-selectable skin index, `viewhandler.zip`, `ambienceColorMap.res`, `ifs-root`, nav rendering files, or binaries. Require separate evidence/release gate for each. Changes to shared resources could affect ALL skins, defeating selectable isolation.
6. No edits to navigation road colors, map engine, routes, or POI `images.cff` until format and runtime usage are proven. The map is mission-critical; a PNG concept is not a mapped source asset.
7. Preserve icon semantics and contrast. Safety/warning/status icons (seat belt, airbag, hazard, speed, assist alerts, tire pressure etc.) MUST NOT be restyled ambiguously or hidden. Keep touch targets and coordinates fixed; visual assets are not a layout redesign.
8. Scripts: POSIX / QNX-compatible shell subset. Avoid `printf` as external utility (failed in earlier on-car diagnostics). Test available commands empirically; prefer simple `echo`, `cp`, `mv`, `sha1sum`, `sync`, `mount` in verified context. Take SD FAT32 limitations, QNX remount behavior, atomicity, rollback, and interrupted writes seriously.
9. Never mass-apply unreviewed PNGs by guessed IDs. For each changed resource record ID, source, exact dimensions, alpha channel, screen usage evidence, selection states, original and new hashes, affected skins, and visual before/after. An ID in MCF is not evidence that UI actually displays it.
10. Do not claim any build is **car-ready** until exact input state, offline validation, independent restoration exercise and a documented on-device preflight (either standalone or part of a user-authorized, marker-armed install run) have passed. Distinguish PC-validated, on-device installed, and visually/functionally verified after reboot. Do not claim HOME changed merely because concept art exists.
11. Prioritize working code, data-driven extraction, contact sheets, screenshots and realistic rendered previews over another abstract design explanation. Do not delegate artwork to Claude unless the user requests it. Codex owns integration and may use programmatic Pillow/SVG design techniques.
12. Preserve original files; work in `neoui_workspace/`, `neoui_build/`, `neoui_reports/` and `neoui_previews/`. Don't move/delete 2.75 GB original archive, raw firmware, backup folder or SD card data. Never write generated files into firmware source trees.


## Field-tested v2 installation findings (2026-11-11): REQUIRED FOR v3
This section records observed behavior from actual Kodiaq M.I.B. console screenshots and the v1/v2 artifacts. Treat these as firmware-specific observations, **not** general guarantees for other QNX units or future releases.

### Verified device and file layout
- Console: M.I.B. 3.6.0 via **Advanced Settings → Run individual script** (GEM 4.12st screen).
- Device firmware observed by script: `MHI2_ER_SKG13_P4526` / `MU1440`; hard-fail on unknown/mismatched firmware.
- SD card mounted at `/net/mmx/fs/sda0` in tested script; do not hard-code the Windows drive letter (`E:` was only its observed PC letter).
- Application filesystem: `/net/mmx/mnt/app`; installed graphics target: `/net/mmx/mnt/app/eso/hmi/lsd/Resources/skin3/images.mcf`.
- SHA utility used: `/net/rcc/usr/bin/sha1sum`; firmware reader: `/net/mmx/mnt/app/eso/bin/apps/pc`, invoked via `on -f mmx ... s:30:1966084` (train) and `s:30:1966083` (MU). Verify these dependencies at runtime.
- Measured on-device `df -k` at diagnostic: `1404880` 1K blocks total, `1015019` used, **`389861` available**, `73%` usage for `/mnt/app/` (observed then, not a permanent guarantee).
- Existing v1 skin3 was 32,173,128 bytes, `root:root`, mode `-rwxrwxrwx` (777). v2 pilot payload is 32,861,680 bytes. Read and preserve actual mode/owner for v3 rather than assuming 777 everywhere.
- Observed checksums: original pre-NeoUI M.I.B.-derived skin3 `0a322d581cb320c60bc6be87e2817fcdf20aa2f2`; NeoUI v1 `641c34e42ed5843c1795bf860fd4cb7bbb913fdb`; NeoUI v2 pilot `28e26e2603497571663a93b303e930a2d4787f50`.
- The v2 installer console showed **`SUCCESS - Installed NeoUI v2 MENU Pilot graphics. Only skin3/images.mcf replaced.`** followed by **`END: completed`**. This establishes a successful scripted replacement and verification as reported by the installer; **post-reboot rendering and all functional behavior have not been independently established by that console output**. For v3, determine actual installed v2 SHA from a fresh on-device read, not from project assumptions.

### Actual failures and their fixes
1. **Transient payload hashing failure:** one early PRECHECK emitted `Payload checksum incorrect: UNKNOWN`; a subsequent run emitted `Payload checksum verified`. Preserve failure logs and exit before touching app files; never bypass hash verification or replace `UNKNOWN` with a guessed value. Investigate SD read reliability and executable availability if repeated.
2. **Incorrect Linux-shaped `df` parser:** the initial storage guard used `df -k "$APP" | awk 'NR==2 {print $4}'`, which failed on this QNX output with `FAILED - Cannot determine available application storage` even though the independent diagnostic showed free space. The installation correctly aborted **after precheck and before app writes**.
3. **Working QNX parser:** parse the available blocks as the numeric field immediately before the percentage column on the `/dev/...` filesystem row; this successfully logged `Storage check passed: 389861 KB available` on the device:

```sh
FREE_KB=$(df -k "$APP" | awk '
    $1 ~ /^\/dev\// {
        for (i = 1; i <= NF; i++) {
            if ($i ~ /%$/ && i > 1) {
                print $(i-1)
                exit
            }
        }
    }
')
case "$FREE_KB" in
    ''|*[!0-9]*) fail 'Cannot determine available application storage'; return 1 ;;
esac
if [ "$FREE_KB" -lt 102400 ]; then
    fail "Insufficient application storage: ${FREE_KB} KB free"
    return 1
fi
say "Storage check passed: ${FREE_KB} KB available"
```

This snippet is an **observed working pattern, not a universal parser**. Validate it against the actual v3 `df` output; ensure exactly one correct filesystem row and verify exit statuses/units. At least 100 MiB free was the v2 guard, not necessarily enough for larger v3 archives: calculate worst-case on-device backup + staging + rollback reserve, round upward, and fail closed.
4. The diagnostic-only branch (`DIAGNOSTIC_ONLY`) ran `df -k "$APP"`, `ls -l "$IMG"`, and `ls -ld "$APP"` before installation logic. It was explicitly removed before the installation attempt. Never let a leftover diagnostic marker silently override a v3 install marker.
5. Full v2 installation after corrected parser: firmware hash/payload check, existing v1 SHA, SD backup, free-space check, and on-device backup all passed; only then was `skin3/images.mcf` replaced; install completed. Preserve this sequencing.

### Mandatory v3 build and release workflow
1. **Discover live baseline:** record firmware/MU, current selected skin, path, byte length, SHA-1 and SHA-256, owner/mode, mount state, and free blocks before preparing any delta. For a v2→v3 upgrade, expected current SHA-1 may be `28e26e2603497571663a93b303e930a2d4787f50` **only if a fresh read confirms it**. Never reuse v1 as the expected current installed hash merely because earlier scripts used it.
2. **Build exact, versioned artifacts:** e.g. `NeoUI_v3_skin3.mcf`, a release manifest with source/target hashes and sizes, reproducible builder inputs, and `run.sh`. Hash the actual final bytes copied to SD. Do not trust an archive just because its checksum matches a manifest; also validate MCF header, resource count/IDs, offsets/bounds, decompression, pixel dimensions, and expected differences against the known-good baseline. v2 comparison indicated 2,345 entries; verify count again for v3 rather than assuming it is invariant.
3. **Independent off-car validation:** POSIX shell syntax (`sh -n`), static audit (ShellCheck where available), simulation using temporary filesystem paths, PRECHECK-only, successful install, successful restore, hash mismatch, missing SD/payload, insufficient storage, existing/invalid backups, conflicting markers, copy/move/hash failures, remount failure, and interrupted/partial-file recovery. A syntax pass or happy-path simulation does **not** guarantee on-car recovery. Do not require WSL on Windows merely to run checks; use an appropriate existing POSIX shell or a contained test runner.
4. **Precheck is always mandatory, but a separate visit is optional.** Support (a) default PRECHECK-only mode with no application changes, and (b) an **explicitly user-authorized, marker-armed single-run PRECHECK → INSTALL** mode. In (b), `install()` calls `precheck()` first and returns immediately on failure; there is NO second SD swap merely to perform the same tests. User must review the release and consent to the risk before arming. Do not silently auto-arm after any standalone precheck.
5. **Explicit mutually exclusive markers:** v2 names were `INSTALL_V2_NOW` and `RESTORE_V1`; for v3 prefer unambiguous versioned names such as `INSTALL_V3_NOW` and `RESTORE_V2` (choose once and document consistently). If both exist, fail before any app write. Default with no markers is PRECHECK-only. After successful install, instruct user to remove the install marker on PC so rerunning the script cannot accidentally attempt another installation. Versioning markers does not replace a current-installed-hash guard.
6. **Safe file sequencing:** verify SD writable (temporary write/readback) and append to a persistent log; firmware; payload SHA; target existence and installed SHA; independently verified SD backup; calculated free-space guard; on-device backup if feasible; remount app read-write; stage payload next to target; verify staged hash; preserve target attributes; replace via same-filesystem rename; `sync`; verify final installed hash; restore app read-only; log final result. Backups should precede replace and must never be overwritten without verified content/expected hashes. Be mindful that extra on-device backup+staging can consume ~two payload sizes.
7. **Failure handling is part of the release:** every error must stop further modification, emit a clear `FAILED`/`CRITICAL` log, preserve working backups, and attempt best-effort cleanup. If failure occurs after replacement, do not ambiguously report "nothing changed". Distinguish pre-write abort, installed-but-remount-failed, post-write hash mismatch, rollback completed, and rollback failed. Rollback itself must verify final bytes and restore mount state; do not imply it guarantees boot recovery. Avoid deleting the only backup or replacing original bytes until the replacement is fully staged and verified.
8. **Persistent append-only log:** v2 wrote to `mod/neoui/v2/NeoUI_v2_result.txt` on the SD card, with `--- session ---`, `MODE`, firmware, payload SHA check, installed SHA, backup verification, storage, result, and `END: completed` or `END: FAILED`. V3 should log to a versioned equivalent such as `mod/neoui/v3/NeoUI_v3_result.txt`. Continue logging after a failed precheck; on SD unwritable/log initialization failure, fail safely and display console message (a log cannot be guaranteed). Do not mislabel a normal installer message as proof of GUI compatibility.
9. **Safe user instructions:** safely eject SD; use stable external power where practical; execute only via the verified M.I.B. UI path; do not interrupt during a write; read the result before reboot; do not repeatedly rerun on any `FAILED` or `CRITICAL`; collect console photo and SD log on PC for diagnosis. A successful flash/write permits only a carefully controlled reboot and **post-reboot** visual/functional tests (MENU, HOME, navigation, media, phone/CarPlay, settings, safety indicators) before declaring v3 usable.
10. **Final v3 release package:** include `RELEASE_MANIFEST.md` (firmware/target/hash/size/permissions and changed ID inventory), `PRECHECK_AND_INSTALL.md` (one-run and precheck-only options), `ROLLBACK.md` (including recovery limitations), backup inventory and checksum file, versioned scripts/payloads, SD directory tree, test report with simulated vs actual-car evidence, and exact Windows PowerShell copy/marker/log commands. Explicitly identify the prior-version backup and original pre-NeoUI backup separately.

### v2 sample reference paths (do NOT confuse these with v3 filenames)
```text
SD: /net/mmx/fs/sda0
mod/neoui/run.sh
mod/neoui/v2/NeoUI_v2_pilot_skin3.mcf
mod/neoui/v2/NeoUI_v2_result.txt
mod/neoui/v2/backups/skin3_NeoUI_v1_before_v2.mcf
mod/neoui/v2/INSTALL_V2_NOW   (explicitly armed install)
mod/neoui/v2/RESTORE_V1       (mutually exclusive rollback)
mod/neoui/backups/skin3_before_NeoUI.mcf  (older original-state backup)
Device: /net/mmx/mnt/app/eso/hmi/lsd/Resources/skin3/images.mcf
```

**Never silently copy v2 names, hardcoded hashes, or backup expectations into v3.** Adapt the entire dependency chain and include a release-specific manifest. Preserve both the known-working predecessor and an independently verified original-state recovery copy off-device.

## v3 maintainability requirement: rapid, repeatable visual-only revisions

**Goal:** After v3 has been installed and verified, the user must be able to request changes such as "replace the Navigation icon", "make Media blue", or "change this background" without repeating the original firmware research, manually locating MCF resource IDs, or rebuilding installer logic from scratch. Treat maintainability as a first-class v3 deliverable, not a future optional enhancement. This applies only to graphics for which resource mapping, encoding and runtime effects have been verified. Never promise that arbitrary UI layout, fonts, compiled behavior, safety symbols or navigation rendering can be changed as easily as a bitmap.

### Required source architecture and assets
1. Maintain a **machine-readable resource catalog**, e.g. `neoui_workspace/resource-map.json`, keyed by stable descriptive names (such as `menu.navigation.default`), with exact MCF container path, numeric resource ID, source firmware/baseline, dimensions, format/codec, alpha/transparency, palette if relevant, compression, variants (pressed/selected/disabled/day/night), display location, affected skins/shared scope, confidence level, and evidence (screenshot/extraction/test). Record original and modified hashes. Clearly flag unmapped or shared resources; never infer a match from an icon's appearance alone.
2. Keep **editable master artwork** separate from generated assets, using descriptive filenames (`resources/icons/`, `resources/backgrounds/`, `resources/buttons/` etc.). Preserve originals and source formats (SVG, PNG, layered formats where applicable); conversions into firmware resources are reproducible. Do not confuse proposed folders with on-device filesystem paths. Record font/licensing dependencies where relevant.
3. Create a **deterministic, version-controlled build pipeline**, e.g. `build.ps1` plus scripts/tools as needed: editable source -> validated firmware-compatible asset -> replacement of exact mapped resource(s) -> rebuilt MCF/container -> integrity verification -> release manifest. Use the existing proven encoder/repacker where available; if reliable round-trip packing is not proven, mark this pipeline blocked instead of inventing it. Do not write into original firmware trees.
4. Make each visual edit **declarative**: an explicit change set with semantic names, old/new image and hashes, resource IDs, variants, containers, and affected skin scope. Default to the smallest feasible source change. Generate a binary/container diff report proving only the intended resources changed; explain any unavoidable container metadata or offset differences.
5. Provide **visual comparison output** before packaging: contact sheet of changed assets and relevant states, labeled before/after screen previews, actual resolution and alpha-checkerboard previews where useful. Identify which previews are render approximations versus validated device screenshots. Keep known-good v3 baseline screenshots for regression comparison.

### Codex workflow for a later visual request (v3.1, v3.2, etc.)
1. Translate user's plain-language request into named catalog entries. If mapping is incomplete or the requested look changes layout/behavior, investigate and report scope before changing anything. For ambiguous names, show a labeled contact sheet rather than guessing.
2. Modify only the approved editable masters and the corresponding mapped firmware resources. Keep all linked states consistent; preserve dimensions, alignment, transparency, hit areas, semantics, warning visibility and day/night contrast.
3. Run automated validation: mapping uniqueness, old baseline hash, source and encoded dimensions, allowed resource IDs, container consistency (header, offsets/bounds, entry count, decompressability), output hash, and a whitelist/diff of changed resources. Fail closed on unknown formats or shared-asset impacts.
4. Produce a preview and short `VISUAL_CHANGELOG.md` listing changes, untouched areas, test evidence, and risks. User reviews the appearance before a car-installable package is considered.
5. Build a **new immutable, versioned release** (never silently overwrite v3) with exact expected-current installed hash, final payload hash, firmware gate, storage calculation, backup and restore instructions, persistent SD logging and the already established marker-armed mandatory PRECHECK -> INSTALL flow. A visual-only revision is **not** exempt from full installer safety checks.
6. **Do not assume a single-icon update can be installed as a single file.** If the device needs a full `skin3/images.mcf` replacement, package the full validated container. Use smaller deltas only after proving on this firmware that they are supported, atomic, recoverable, and safe. Never alter live firmware via speculative direct writes.
7. After installation, verify user-selected target screens and relevant adjacent states in the car, including reboot/persistence. Record the on-device installed hash as the next release's baseline; keep exact prior payload and recovery backups.

### Required v3 handover deliverables
- `resource-map.json` (or equivalent) with documented schema and evidence/confidence fields.
- An inventory/contact sheet and an index that lets the user point Codex to an icon by screen/name/ID.
- Editable master assets, conversion/repack scripts, pinned tool versions/dependencies and repeatable build instructions.
- `build.ps1`/equivalent one-command **off-car** visual build, validation report and preview generation; do **not** equate build with vehicle installation.
- `VISUAL_EDIT_GUIDE.md` with examples like "change `menu.navigation.default`" and known blocked/unsafe resource classes.
- A demonstrated rehearsal replacing one **non-safety-critical mapped** icon, reproducing the container deterministically and validating its binary diff, without touching the vehicle.

**Acceptance condition:** A mapped cosmetic icon edit should require no new firmware archaeology or manual MCF hex editing, and Codex should be able to regenerate previews and an offline-validated package in one routine command. Actual duration depends on asset complexity, encoder support, review and installation; never promise minutes as a guarantee. If this cannot be achieved, document exact limitations and keep v3's known-good installation independent of the experimental tooling.

## First session actions
- Inventory user folder and archive contents without extracting huge archives redundantly; log filenames, sizes and SHA256s of key MCF and ZIP inputs.
- Identify upstream installed M.I.B. image mod's slot creation/selection logic using firmware/M.I.B. files and official documentation. Write `neoui_reports/SKIN_SLOT_FEASIBILITY.md` with a proven YES/NO/UNKNOWN, exact dependencies, impact, and recommendation.
- Build a reproducible resource inventory (all existing `skin*` directories, `images.mcf`, `images.res`, `info.txt`, animations, UI config, view code, nav resource tree). Distinguish original firmware vs on-car installed state; don't assume extracted firmware includes the currently installed M.I.B. skin3.
- Map each pictured UI component to a source graphics ID/config/renderer using evidence. Focus HOME right-side favorites/phone/media panel, MENU icons/background, bottom navigation bar, Setup list highlighting/separators, Fahrzeug background/arrow/road illustration, Medien box/buttons. Use side-by-side contact sheets and explicit confidence levels.
- Produce an **offline interactive/side-by-side preview** for ALL eight screenshot scenarios, then validated off-car build. If a component requires compiled view code and cannot be safely customized, list it as blocked instead of guessing.
- Proposed release workflow: DISCOVER -> MAP -> DESIGN -> BUILD -> VALIDATE -> REVIEW -> USER-AUTHORIZED PRECHECK + EXPLICIT INSTALL (precheck may be in same armed invocation). Stop before vehicle operations.

## User preference
User is a .NET developer (Windows/PowerShell/Python available), wants decisive technical execution and concise status. Ask only blocking questions. In progress reports distinguish ACTUALLY changed graphics from mockup or speculative mapping.
