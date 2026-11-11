# NeoUI v3 current state

Current candidate: neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf. 54 changed records from exact packaged v1: 16 media transports, 4 HOME/SETUP, 26 vehicle/navigation controls and 8 new media/BT graphics. See MEDIA_BT_BUILD_REPORT.md and VERIFIED_MEDIA_BT_BUILD.json.

New graphics: BT/source-off cards2217/2202, generic/source-off2214/2199, TYPE090 source-list states1131/1133/1134 and playlist glyph1036. Mbam (MediaBtAudioMain), its cover-choice script and the common runtime script bind actual image arrays to logical IDs and MCF records. Generic source2214 also supplies the border behind dynamic album artwork. Brand colors, bright glyphs/BT label and source/off distinctions are preserved.

Previous 46 graphics remain exact. 106 protected M.I.B. MENU/foundation records and 288 non-controlbar navigation records remain byte-identical to v1. Shared blue bar, MENU/floor/background, safety/eco/fuel/status graphics, dynamic cover loading, text/layout, hit targets, map/POI/route data and behavior are unchanged. All other records remain exact. TYPE090 states can affect other skin3 lists; playlist1036 aliases playlist/setup. Generic fallback/border applies beyond Bluetooth.

Shuffle/repeat masks, TYPE904 no-bitmap backgrounds, seekbar61/39, indicator917 and compiled color arrays8/40/44 are retained. They use renderer-selected green/dim/white colors; no baked cyan or compiled code patch is applied there. Media spot1889 is fully transparent and remains so. Other source-specific fallback cards remain unmodified.

Independent restore reproduces exact packaged v1. MCF CRCs, dimensions, alpha and transparent RGB pass; all18 transport/source-button slots and360 preview-selector combinations pass. Preview: neoui_previews/MEDIA_BT_V3_PREVIEW.html. It uses actual assets with clearly illustrative placement, sample German text and a preview-only artwork pattern; not a captured or coordinate-verified head-unit screen. Native PNGs inspected; browser visual QA is unavailable under local-file URL policy.

Only NeoUI_v3 receives generated files. Original firmware/backups read-only; no network/SD/vehicle writes, commits or installer. Independent selectable slot remains UNKNOWN; this is a versioned skin3 replacement fallback, not a new skin. PC-validated only. Current-unit hashes/metadata, separate no-write preflight, release review and explicit install authorization remain required.
