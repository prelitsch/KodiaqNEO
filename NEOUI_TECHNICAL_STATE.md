# Engineering inventory, slot feasibility, and installation boundary

## Exact baseline identifiers and state
| Item | Verified/reported value | Meaning |
|---|---|---|
| Firmware | `MHI2_ER_SKG13_P4526` | exact supported train |
| MU | `1440` | exact supported version |
| Image MOD skin3 SHA1 | `0a322d581cb320c60bc6be87e2817fcdf20aa2f2` | upstream M.I.B. skin BEFORE NeoUI v1 |
| NeoUI v1 skin3 SHA1 | `641c34e42ed5843c1795bf860fd4cb7bbb913fdb` | v1 successful installer payload, presumed on-car until read-only verification |
| NeoUI v2 MENU pilot skin3 SHA1 | `28e26e2603497571663a93b303e930a2d4787f50` | OFFLINE-validated v2 payload, NOT installed |
| `skin3` MCF count | 2345 | known reconstruction and existing v1/v2 payloads |
| Original `skin0` MCF count | 1054 | ORIGINAL FW, not installed skin0 baseline |

## Firmware paths in extracted app50
```
MHI2_ER_SKG13_P4526_MU1440/MMX2/app/50/default/app.img
app50_extract/lba0/eso/hmi/lsd/Resources/skin0/images.mcf
app50_extract/lba0/eso/hmi/lsd/Resources/skin1/images.mcf
app50_extract/lba0/eso/hmi/lsd/Resources/skin2/images.mcf
app50_extract/lba0/navigation/resources/app/sk/eu/
```
Prior scripts operated against these **on-device** paths:
```
/net/mmx/mnt/app/eso/hmi/lsd/Resources/skin3/images.mcf
/net/mmx/fs/sda0/mod/command.sh
/net/mmx/fs/sda0/mod/neoui/run.sh
```
`M.I.B. -> advanced_settings -> run_individual_script` invokes `mod/command.sh` on the SD; existing command launcher calls NeoUI script. Confirm actual launcher before changing. QNX SD1 FAT32 mount `/net/mmx/fs/sda0`; installed app volume under `/net/mmx/mnt/app`; `mount -uw` / `mount -ur` used by prior scripts. Changing permissions, remount behavior, file capacity, fs locking etc. require actual verification on this firmware.

## Crucial distinction: selectable skin vs in-place patch
Existing active M.I.B. image mod's selection is real (official SKG13 Image MOD wiki documents selection via Engineering Menu). But user wants **one additional selectable NeoUI option**, not replacement of upstream M.I.B. slot. Our previous NeoUI did not add a slot — it modified skin3 in place.

Investigate in this priority order:
1. Inspect `app50_extract/lba0/eso/hmi/lsd/Resources/skin{0,1,2}` each `info.txt`, `images.res`, `images.mcf`, `viewhandler.zip`, animation/ambient resources, missing files and directory size. Inspect upstream M.I.B. SKG13 Image MOD script in local `M.I.B._More-Incredible-Bash-3.6.0.zip`, especially what files are copied to `skin3`, any `skinN` references, switch configuration, selection IDs, state persistence, which program chooses skin.
2. Determine slot capacity from actual selection implementation. Maybe finite 0..3; **never assume skin4 is supported or that it suffices to copy skin3 to skin4.** Determine if a skin needs a complete directory of resources (viewhandler, images.res, config, animations), not merely a single MCF. Any new slot may require selector binary changes and is disallowed without a recovery/test plan.
3. Determine if all UI surfaces share `skin0`, and if a change would be global no matter what skin is selected. Shared nav region assets may not be skin-selectable. Keep an architectural table: `asset -> screen -> provenance -> slot/global -> safe/unknown`.
4. If the new slot can be done by copying valid complete skin and selecting an already-supported slot ID, with no patch to core code, prototype **offline only**. Require a read-only inspection step on actual car to confirm target slot free and version matches before install.
5. If new selectable skin needs binary patching or writes outside resources, mark **NO / NOT YET PRACTICAL**. Fallback is a versioned reversible update to existing `skin3`, accepting M.I.B. visual features as a base. Offer PC-switchable images while car selected skin remains one slot only, and label it clearly.

## Existing v2 pilot installation mechanics — READ ONLY reference
The user's v2 pilot `README_START_HERE.md` describes two-stage marker gates:
- first GEM execution backup/precheck, checks SHA1 currently installed equals v1 and copies current image to SD;
- second explicit `INSTALL_V2_NOW` enables `skin3` change (no other files). `RESTORE_V1` permits restore if GEM stays functional.
This script was **tested in local simulation only**, never on head unit. Don't reuse unchanged if building an independent skin or multi-file release. Verify actual runtime state; do not assume car has current SHA without read-only check. Backup original upstream M.I.B. and current NeoUI v1 separately.

## On-car behavior and prior gotchas
- Old attempt failed because `printf` not an available external executable; use QNX-portable shell commands only after test.
- SD mounted read-only initially. `mount -uw /net/mmx/fs/sda0/` permitted write and read-back during diagnosis. Avoid modifying SD from car except an authorized backup/log.
- User success output (`NeoUI: SUCCESS - Installed NeoUI v1 image`) demonstrates file replacement and validation, not evidence correct graphics rendered on HOME.
- Power/boot risks: a corrupt graphics resource may prevent infotainment UI or GEM loading. SD rollback may become unusable. Use proper 12V regulated support and consider independent recovery path, not just shell script.
- A vehicle-powered run may have special live mounting/write restrictions; do not schedule or instruct driving with diagnostics running.

## Navigation package details
Actual `navigation/resources/app/sk/eu`, not Volkswagen `vw/eu`. The archive `Kodiaq_NeoUI_Navigation_Research.zip` contains **27 entries** and has archive paths normalized under `.../vw/eu` due to earlier collector implementation; contents are from the Škoda `sk/eu` source. Contents include:
- `images.cff`, `textures/textures.cff`, `gui/bitmap.skn`
- `gui/road_name_marker.png`, `Street_Pin_Shadow2D.png`, `Street_Pin_Shadow3D.png`
- `pcconfig/iconsmappings.xml`
- `poi/petrol_stations.pc.gz`, `roadicon/roadicon.ri.gz`
- `MapConfigs/mapconfig_default_0_DTM.mxf.gz` and `_1_DTM.mxf.gz`, vehicle/kombi/traffic variants, 1280x640 versions, fontconfig and zoom/resource config files.
No nav edits were installed. Start by inspecting directly PNG markers (maybe safe if truly active), XML icon mappings and CFF container format. A file merely present is not evidence of run-time use. Editing road-map configs is a later, distinct release.

## Non-negotiable release proof
- Document input filenames + SHA256; exact on-car checksums verified in a no-write pass.
- Preserve all original byte-for-byte backups on PC and SD; hash-verification; complete restoration simulation of all files to be touched.
- Record explicit path, origin, slot/global behavior, ID, image geometry/alpha, visual mapping evidence for EACH changed resource.
- Validate MCF directory, offsets, lengths, indices, PNG parse, count, per-entry diffs, bounds, no unexpected file changes. Test archive packaging.
- Provide a full PREVIEW gallery, changed-assets manifest, checksums, installer scripts with safe gates, STOP/FAIL instructions, rollback + limitation statement.
- Before first car install, obtain explicit user review/approval and use a dedicated precheck. Only then discuss a write.
