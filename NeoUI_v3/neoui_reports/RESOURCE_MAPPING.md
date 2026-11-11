# NeoUI v3 mapping and implementation

Current stage:54 real MCF records (16 media transport,4 HOME/SETUP,26 vehicle/navigation,8 additional media/BT). See VERIFIED_MEDIA_BT_BUILD.json for exact source/new record, pixel and PNG hashes, geometry/alpha, aliases and compiled bindings. MEDIA_BT_RESOURCE_EVIDENCE.json resolves Mbam/related media views plus cover/artwork and state scripts. Earlier VEHICLE_NAV_RESOURCE_EVIDENCE.json and runtime tint evidence remain applicable.

New media resources: BT fallback2217/off2202, generic fallback and dynamic-art border2214/off2199, TYPE090 source-list states1131/1133/1134 and playlist1036. The existing sixteen transport variants are now statically bound by Mbam arrays304/306/308/310. Shared effects and retained renderer-controlled states are documented in MEDIA_BT_BUILD_REPORT.md. Other source-specific cards remain unchanged.

Primary/secondary bitmap layers and identical source day/night pairs remain verified by the preceding runtime trace. HOME ambient composition and scrollbar state tint remain as documented in HOME_SETUP_RUNTIME_TINT.md. No renderer/config/metadata edit is made. Mix/repeat, seekbar and no-bitmap button backgrounds keep original images and runtime colors.

M.I.B. MENU/foundation106 records remain exact;288 non-controlbar navigation records remain exact. Shared skin0 vehicle illustrations, map/road/POI/CFF/route resources, safety graphics, HMI layout, languages and hit zones remain unchanged. No car or SD writes. Installed metadata/current-unit state still requires a separate release precheck.

Preview: neoui_previews/MEDIA_BT_V3_PREVIEW.html. Component compositions and artwork/text samples are not captured head-unit output. Independent new skin slot remains UNKNOWN; this is a reversible offline skin3 replacement candidate, not a car-ready additional skin or full UI release.
