# FAHRZEUG and navigation action controls — offline build

26 new graphics, 46 total. Real source assets and compiled bindings; no guessed MCF IDs. This is an existing skin3 fallback. A separately selectable new skin remains UNKNOWN; see SKIN_SLOT_FEASIBILITY.md.

## Verified mapping

| Component | Binding | MCF records |
|---|---|---|
| Trip-computer decorative road | Cmc.initWidgets direct logical 2592 | 2221 (1280×170) |
| Next / previous paging | Cmc image arrays 712 / 715, all 18 positions | 1652/1651/1650 and 1649/1648/1647 (120×120) |
| New destination | Nmg/Nmn array 904 → logical 1937/1938 | 989/988 |
| My destinations | array 903 → 1935/1936 | 991/990 |
| POIs action icon | array 905 → 1939 | 987 (not map POI images.cff) |
| View | array 902 → 1933/1934 | 993/992 |
| Media / tuner / TV dynamic branches | arrays 456/457/907 → 994/995/1941 | 1015/1014/985 |
| Announcements / switch map | arrays 908/906 → 1942/1940 | 984/986 |
| Setup / vehicle view | arrays 831/450 → 1752/984 | 1000/1024 |
| Shared button tiles | arrays 114/115/116/118/119/120/123 | 1707/1714/1716/1717/1719 |

The icon records are 78×52, tile records 182×92. VEHICLE_NAV_RESOURCE_EVIDENCE.json stores exact module, method, ROM offset, method digest, invocation PC, literal ID, all state positions and resolved aliases. getImageArray is an indirection: array2 (start,length) addresses logical references in array3. Equal numeric image/MCF IDs are never assumed. Both navigation modes resolve the same control families. State-slot indices stay verbatim; C04/C06/C07 and named tile variants are recorded without inventing renderer state labels.

## Actual changes and shared effects

Neutral icon pixels receive a restrained ice palette; every chromatic icon pixel is preserved, including green POI detail and yellow media notes. Icon silhouettes, alpha, transparent RGB, dimensions, insets and state bindings remain exact. Decorative green paging and button selected/pressed pixels receive ice while retaining their gradients. Normal separator pixels receive the same cool neutral palette. The trip-road decoration is darkened/cooled without changing lane geometry or alpha.

The five shared button-state records and shared setup/media/tuner/TV/vehicle-view glyphs can appear in other skin3 application bars. The six paging glyphs can appear in other screens. This is not isolated to NAVIGATION/FAHRZEUG, and does not affect other skin directories unless an unverified installation aliases them; no installation is provided. 86px paging variants and unmapped button variants remain unchanged.

106 protected MENU/foundation records remain byte-identical to v1: all MAIN_MENU aliases, shared car/background foundation and complete blue action-bar layers. This deliberately replaces the previous stage’s broad 208-record guard with a precise MENU/foundation guard and explicitly authorized controlbar targets. M.I.B. MENU tile graphics, perspective/floor and behavior are retained. All records outside the 46-item manifest are exact.

The vehicle picture uses shared skin0/imageidmap.res: tagged UTF-16 path strings followed by a matching integer ID array, not path ordinals. Twelve encoded Car/Bordcomputer/Car.png paths resolve; the actual vehicle prefix is unverified. All skin0 pictures and metadata are untouched. Eco leaf, fuel station, safety/status graphics are retained. No navigation road/map/POI/CFF/routing files, viewhandler, selector, ambience maps, NVRAM or filesystem images are modified.

## Validation and preview

- Source SHA1: 641c34e42ed5843c1795bf860fd4cb7bbb913fdb.
- Source SHA256: dfb37cb771c58fb838d3797c3bf356e8fae9475aa980a236b7e9cba055f5cd58.
- Candidate SHA256: a4d5cddb77ce92583e091b9957f32e6f5b2f40bf95421e223de95cf247e11cf2.
- Candidate: neoui_build/NeoUI_v3_VEHICLE_NAV_skin3.mcf; 2345 records; all CRCs pass.
- Exactly 26 new / 46 total changed records; dimensions, alpha and transparent pixels exact; chromatic icon pixels preserved.
- Independent recovery reconstructs original offsets using saved original records plus unchanged candidate records. Complete restored v1 SHA256 equals dfb37cb771c58fb838d3797c3bf356e8fae9475aa980a236b7e9cba055f5cd58.
- Reproduce: python tools/build_vehicle_nav_v3.py; python tools/verify_restore.py --vehicle-nav; python tools/preview_vehicle_nav.py; python tools/check_vehicle_nav.py; python tools/update_vehicle_nav_reports.py (from NeoUI_v3).

VEHICLE_NAV_V3_PREVIEW.html has all 18 navigation state positions, dynamic media branch notes, native trip-road/paging/button comparisons, all 26 before/after pairs and eight reference photographs. The navigation row is a source-asset arrangement with illustrative text placement; it does not claim exact head-unit coordinates or runtime tints. Full-strip blue is a shader sample. Browser visual QA is unavailable due local-file URL policy; native PNGs are inspected and local links/script syntax checked separately.

## Release limitations

PC-validated only, no on-car test or installer. The source is the exact packaged installed-v1 reference, not a fresh read of the current unit. Installed skin3 metadata must match the traced skin1-derived lineage before release. Off-car restore success is not a boot-recovery guarantee. Current-unit state, permissions, firmware/MU and hash preflight, release review and explicit installation authorization remain required. Original sources are read-only, no SD/vehicle/network operations, all generated derivatives/binaries/previews excluded from Git.
