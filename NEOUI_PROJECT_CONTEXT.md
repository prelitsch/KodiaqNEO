# NeoUI Project — full Codex handoff

Date: 2026-11-11. This is a reconstruction from our prior implementation artifacts and user conversation. Validate against actual local files and on-car hashes; don't treat statements about current files as direct filesystem inspection.

## Hardware and desired result
- Vehicle: 2017 Škoda Kodiaq 2.0 TDI, Columbus 9.2-inch MIB2.5. Firmware **MHI2_ER_SKG13_P4526 / MU1440**; update from older P4514/MU1163 reported successful. Hardware ref after update previously reported `565035021E`.
- M.I.B. More Incredible Bash QR Edition 3.6.0 installed; the official **SKG13 Škoda MIB2.5 Image MOD** was installed and selected in the Engineering Menu. Its MENU page is the **one UI element the user already likes**; do not needlessly replace its attractive basic look. Preserve its pleasing floor/perspective/blue-theme characteristics while making them coherent with NeoUI.
- User wants one complete **NeoUI** visual package, preferably as a **new selectable skin** beside the stock/M.I.B. choices, switching using engineering options like before. If impossible/high-risk on this exact firmware, extension/replacement of current M.I.B.-derived skin3 is acceptable, but clearly document tradeoff and preserve full rollback.
- No UX/functionality changes; OEM-like graphical modernization. Tone: understated, premium, graphite, ice/soft cyan, no aggressive neon or fake futuristic dashboards. Dynamic map on HOME left, favorites/phone/media cards right remain as they are.

## User's CURRENT folder on Windows (screenshot, 2026-11-11)
Likely root: `C:\Users\aldin\OneDrive\Desktop\Kodiaq Moding` (confirmed from earlier PowerShell). Items visible:
```
app50_extract/                           # QNXProbe extracted app50 image; inside lba0/
Complete initial SD Card Data/           # backup of original card contents; inspect, preserve
Kodiaq Backup/                          # preserve; inspect metadata, not overwrite
MHI2_ER_SKG13_P4526_MU1440/             # original firmware tree
qnxprobe-main/                           # QNXProbe source
app50_extract.zip                        # ~380 MB extracted QNX archive
Kodiaq Moding.zip                        # ~2.75 GB older project archive, unknown contents
Kodiaq_NeoUI_v1_Car_Install_Kit.zip       # ~29.9 MB
Kodiaq_NeoUI_v2_Car_Pilot_Kit.zip         # ~30.6 MB; not yet installed
M.I.B._More-Incredible-Bash-3.6.0.zip    # ~14.8 MB toolkit
skin3_before_NeoUI.mcf                   # ~29.3 MB pre-v1 M.I.B. backup
READ_ME_FIRST.txt
README.txt
COLLECT_NAV_GRAPHICS.ps1
```
Image screenshot is NOT proof of contents of archives. Supplemental files supplied in THIS handoff ZIP are listed in `README_INSTALL_HANDOFF.md`.

## Timeline and known progress
1. Extracted `MMX2/app/50/default/app.img` (~1.44 GB) via GitHub `abrignoni/qnxprobe`, output `app50_extract.zip` and `app50_extract/lba0`. QNX root dirs: `armle`, `eso`, `gemib.factory`, `hb`, `navigation`, `root`, `speech`, `streetview.factory`, `var`.
2. Firmware resources: `app50_extract/lba0/eso/hmi/lsd/Resources/skin0/images.mcf` (~58 MiB, 1054 images); `skin1/images.mcf` (~28.6 MiB); `skin2/images.mcf` (~28.6 MiB). QNX firmware extraction does NOT automatically reflect on-car post-M.I.B. modifications.
3. Upstream M.I.B. SKG13 Image MOD used `.mcf.delta` on `skin1` to create customized `skin3/images.mcf` containing **2345 images**, upstream resulting SHA1 `0a322d581cb320c60bc6be87e2817fcdf20aa2f2`. It is selected using Engineering Menu. Existing IMAGE MOD skinned only some assets, reportedly 41 changed. M.I.B. colors may follow ambient setting; upstream wiki says the blue background adapts to ambient color.
4. Built NeoUI v1 from 13 redesigned `skin3` PNGs and installed it successfully via custom M.I.B. individual script on 2026-11-10. NeoUI v1 installed output image SHA1 `641c34e42ed5843c1795bf860fd4cb7bbb913fdb`. On-device pre-v1 upstream M.I.B. backup and SD backup verified; head unit still worked after reboot. User observed almost no visible change, indicating design-to-runtime resource mapping was insufficient.
5. Claude delivered v2 Graphite & Ice artwork: **110 skin3 files**, plus six speculative factory skin0 shared proposals (NOT installation-ready), and separate nav icon sketches (NOT mapped). 116 PNGs validated exact dimensions/RGBA. v2 PC builder prepared a 110-asset expanded file and 94-asset MENU-focused pilot (32 tiles + 38 glyphs + 24 bars). `Kodiaq_NeoUI_v2_Car_Pilot_Kit.zip` contains a guarded 94-asset upgrade with backup/restore; payload SHA1 `28e26e2603497571663a93b303e930a2d4787f50`, expected current v1 `641c34...`; offline simulation passed. **User did not install this pilot.** Crucially, it does NOT update the HOME card panels or nav assets.
6. HOME initial resource research: `skin1/images.res`, `ambienceColorMap.res`, `info.txt`, `viewhandler.zip` (JXE compiled Java modules ~1,232) and some animation resource files. Layout/event code is compiled; HOME may use shared skin0/skin1 resources and/or renderer-defined panel backgrounds. The red/blue background on HOME may be ambient/theme-dependent; no confirmed asset mappings. Must avoid changing compiled modules without credible test strategy.
7. Navigation data successfully collected from extracted app50; **actual Škoda path is `navigation/resources/app/sk/eu`**, NOT `/vw/eu` (collector had wrong naming). Input ZIP entries misleadingly use `navigation\resources\app\vw\eu\...` after collector copied; validate each against original Škoda files before use. Resources collected include `images.cff`, `textures.cff`, `roadicon.ri.gz`, `pcconfig/iconsmappings.xml`, `gui/bitmap.skn`, day/night `MapConfigs/*mxf.gz`, 1280×640 variants, map zoom XML. Formats not yet reverse-engineered. No nav changes installed.
8. User sent eight real vehicle photos on 2026-11-11, included in `reference_screens/`. These make scope broader; see `NEOUI_DESIGN_AND_ROADMAP.md`.

## Essential upstream links (verify rather than assume specifics)
- `https://github.com/Mr-MIBonk/M.I.B._More-Incredible-Bash`
- `https://github.com/Mr-MIBonk/M.I.B._More-Incredible-Bash/wiki/SKG13---Skoda-MIB2.5-Image-MOD` — explicitly says install from GEM and select new skin from Engineering Menu; background responds to selected ambient color. This describes upstream mod, not proof additional arbitrary skin slot is supported.
- `https://github.com/abrignoni/qnxprobe` QNX6 filesystem extractor.
- `https://github.com/hgnme/mib2-maps` map style research only; compatibility NOT verified.

## Prior artifacts and how to interpret them
- `Kodiaq_NeoUI_v1_Car_Install_Kit.zip`: v1 reference installer; its `run.sh` operates on `skin3` and hardcodes exact base and output SHA1. Superseded; DO NOT rerun thoughtlessly.
- `Kodiaq_NeoUI_v2_Car_Pilot_Kit.zip`: guarded 94-asset MENU pilot; **PC-tested, NOT car-tested**, does not redesign HOME. Reference/test source, **not current release to install**.
- `Kodiaq_NeoUI_v2_CLAUDE_OUTPUT.zip` supplied in handoff: full original validated source art and notes, including 110 skin3 replacements and proposals. Treat designs as candidates, not verified active IDs.
- `Kodiaq_HOME_View_Research.zip`: resource dump of HOME-related `skin1` files; reference, do not write compiled viewhandler.
- `Kodiaq_NeoUI_Navigation_Research.zip`: map/POI config resources; entries path misleading `/vw/` as explained above.
- `skin3_before_NeoUI.mcf`: current PC's upstream M.I.B. backup; verify SHA1 above.
- OneDrive synchronization caveat: large archive/temp file churn may affect performance. Use temporary worktrees outside sync or separate folders; do not delete/move originals.
