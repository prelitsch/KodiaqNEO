# NeoUI v3 offline workspace

Current stage: 54 changed graphics from exact NeoUI v1: sixteen media transport variants, four HOME/SETUP assets, 26 vehicle/navigation graphics and eight additional MEDIEN/BT graphics. Start with neoui_reports/MEDIA_BT_BUILD_REPORT.md and CURRENT_STATE.md. Prior tint evidence remains in HOME_SETUP_RUNTIME_TINT.md.

106 M.I.B. MENU/foundation records and the complete blue action-bar strips remain byte-identical. Verified shared action buttons/icons and generic 120px paging arrows now change and can appear in other skin3 screens. Shared vehicle illustrations, eco/fuel/safety graphics, map engine/roads/POIs/routes and layout remain untouched. This candidate replaces existing skin3; an additional selectable skin is still unverified. No installer or SD writes.

The new stage changes BT/generic fallback pairs, shared media source-list states and playlist glyph. Generic fallback2214 is also the border behind dynamic artwork. Bluetooth identity and off-state distinctions are preserved; artwork loading and renderer-colored shuffle/repeat/seekbar states remain unchanged. TYPE090 state images and playlist aliases can affect other skin3 lists/media views.

From the repository root (Python 3 standard library):

```powershell
python NeoUI_v3/tools/images_res.py app50_extract/lba0/eso/hmi/lsd/Resources/skin1/images.res NeoUI_v3/neoui_reports/viewhandler_image_symbols.csv NeoUI_v3/neoui_reports/resolved_images_res.json
python NeoUI_v3/tools/trace_runtime_tint.py
python NeoUI_v3/tools/build_verified_v3.py
python NeoUI_v3/tools/build_home_setup_v3.py
python NeoUI_v3/tools/verify_restore.py --home-setup
python NeoUI_v3/tools/preview_home_setup.py
python NeoUI_v3/tools/trace_vehicle_nav.py
python NeoUI_v3/tools/build_vehicle_nav_v3.py
python NeoUI_v3/tools/verify_restore.py --vehicle-nav
python NeoUI_v3/tools/preview_vehicle_nav.py
python NeoUI_v3/tools/check_vehicle_nav.py
python NeoUI_v3/tools/trace_media_bt.py
python NeoUI_v3/tools/build_media_bt_v3.py
python NeoUI_v3/tools/verify_restore.py --media-bt
python NeoUI_v3/tools/preview_media_bt.py
python NeoUI_v3/tools/check_media_bt.py
python NeoUI_v3/tools/refresh_verified_reports.py
```

Inputs remain in the user's read-only firmware/archive/backup trees. The local v1 reference is neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf, extracted from the v1 install-kit ZIP; exact SHA-1 641c34e42ed5843c1795bf860fd4cb7bbb913fdb. Runtime backup SHA-256 and images.res SHA-256 are pinned. Only NeoUI_v3 receives generated files.

Open neoui_previews/MEDIA_BT_V3_PREVIEW.html for BT/generic/artwork component comparisons,18 source-state slots, new before/after assets and eight references; it links earlier stage galleries. These are source-component comparisons, not captured head-unit output or verified screen-coordinate reconstruction. Generated MCF/PNG/recovery archives and decoded tables contain source-derived proprietary resources: local-only, excluded from Git. Original tools and project documentation can be reviewed for publication; no commit was requested or made. PC validation is not on-device validation.
