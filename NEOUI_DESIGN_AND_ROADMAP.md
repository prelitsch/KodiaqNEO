# Graphite & Ice — UI redesign specification

## The single most important user preference
**The MENU after the official M.I.B. SKG13 Image MOD is the only screen the user explicitly LIKES.** It has a blue/perspective/floor quality worth keeping as inspiration, even if the icon family is refined. Do not replace it with an unrelated flat dashboard. User wants the *rest* of the car firmware modernized to the MENU's level, with a cohesive high-end appearance. Treat visual coherence as paramount.

### Visual tokens (previous Claude v1 design)
- Deep graphite: `#0D131C`
- Panel graphite: `#17202C`
- Slate: `#6C8095`
- Soft ice-cyan focus: `#77E7F4`
- Ice-white text/icon: `#EFF6FA`
- Prefer restrained luminous elements and gradients, legibility at night, measured contrast and subtle selected states. Preserve functional colors for alerts/status (not all green/red/amber should become cyan!).
- No Apple/brand logos invented, no text baked into graphics that is actually rendered by HMI, no resized geometry or shifted interaction targets.

## Real on-car photos provided (2026-11-11)
Files in `reference_screens/` are original images, annotated by filenames. All are of the same 2017 Kodiaq/Columbus unit. The 8 photos cover:

1. `01_HOME_disconnected.jpg`: HOME map large left; right upper area says phone not connected; right lower shows inactive media device; blue-gray panel and top status.
2. `02_HOME_connected_empty.jpg`: HOME map; right upper two favorites placeholders (beveled frames); lower device inactive; blue gradient background.
3. `03_MENU_MIB_style.jpg`: classic M.I.B. modified MENU 4×2 tiles, the only visual element user LIKES. Reflect this in NeoUI and retain it as reference.
4. `04_NAV_bottom_action_bar.jpg`: map with bottom tabs (new destination, favorites, POI, view, media, announcements, setup) and old blue beveled nav bar. User dislikes tab shapes and all action tiles.
5. `05_FAHRZEUG_vehicle_stats.jpg`: car silhouette on road, trip figures, big left/right arrow, bottom vehicle strip, perspective floor; user wants a more modern car/status presentation.
6. `06_SETUP_list_view.jpg`: generic Settings list screen, bright list dividers, green/yellow scrollbar/accent, perspective floor; must modernize shared list styling (if asset-backed), preserve controls and text.
7. `07_HOME_connected_media_playing.jpg`: HOME right panel, phone favorites top and media artwork/text bottom. Different state from pictures 1 and 2, must handle all cases, keep data-driven rendering.
8. `08_MEDIEN_Bluetooth_player.jpg`: full BT Media playing view, old album-card/Bluetooth logo and playback buttons, bottom bar; must modernize consistent with other screens.

Keep status bar/time and safety indicators legible and preserve navigation/map screen geography. Future work may include full Radio/Telefon/Traffic screenshots but these are not blocking for current evidence map.

## Required UI groups and probable complexity
| Group | Exact user's goal | Implementation evidence required |
|---|---|---|
| MENU | polish the existing-liked M.I.B. 4×2 launcher, modern icons/state | 32 tiles + 38 glyphs + 24 bars from Claude v2; verify they truly show on car |
| HOME | dark right-side cards for disconnected, favorites, media; better outlines, separator, cyan accents | find actual backgrounds/selected state in `skin*`/compiled renderer; photo reference + resource mapping; no invented separate tile dimensions |
| NAVIGATION | refine bottom nav action strip + accessible overlays; subtle POI style update | map to actual `images.mcf` or `images.cff`, bottom bar shared with HMI? Confirm runtime, integrity |
| FAHRZEUG | vehicle screens, progress and trip statistics, arrows, lower strip | identify images/config; keep numeric data, VW car assets and UI hitboxes intact |
| SETUP/LISTS | remove dated bright separators / ugly scrollbar and highlight colors, dark premium list backgrounds | identify shared list rows, line/highlight assets and color renderer; preserve accessibility and focus states |
| MEDIEN | modern Bluetooth cover/device card, playback transport controls, bottom icons | map resources, ensure play/pause/skip visibility and same state geometry |
| RADIO and other common screens | inherit compatible changes, no surprises | identify shared resource effects and test all screens |

## Specific v2 existing art, but NOT yet on car
Full `Kodiaq_NeoUI_v2_CLAUDE_OUTPUT.zip`: `design_output/replacements/skin3/` contains 110 replacement PNGs; `design_output/proposals_only/skin0_shared/` six factory-baseline proposals; `design_output/proposals_only/navigation_concepts/` ten POI types ×48/128px sketches. Claude says all 116 delivered PNGs have matching source dimensions and RGBA and generated 8-bit PNGs. Check exact folder and metadata rather than blindly relying on this brief.

Only **94 skin3** of those were integrated into last v2 MENU-focused pilot. Other **16 backgrounds** were deliberately excluded as active HOME mapping unknown. More radical HOME render examples, UI mockups and simulated 4x2 layouts from old zip files are **not actual extracted asset mappings**.

## Implementation approach for every UI element
1. From photographed area describe its pixel role (background, frame, icon, line, live label, map, button, animation).
2. Find plausible original imagery using metadata search, MCF contact sheets, alpha/size heuristics, code references and resource mappings. Evidence ranking: (A) proven runtime code/reference + visual match, (B) resource name/reference + visual match, (C) visual-only candidate, (D) conceptual.
3. Only A/B can be considered for a deployable asset. For C/D create previews/research and mark not deployable. Avoid false certainty.
4. Generate exact-size replacement preserving alpha/selection geometry, compare at screen-relevant scale, and inspect full states (HOME connected/disconnected, MEDIA playing/paused, list selected/unselected, night/day).
5. Document intended effect and side effects: shared file and multi-skin scope.

## Realistic deliverable order
1. Inventory + separate-skin feasibility. Decide architecture before editing shared assets.
2. UI map and contact sheet for 8 photos, especially HOME and shared list styles.
3. First complete static interactive preview with clear source vs design vs confidence labels; include fallback if some components prove renderer-defined.
4. Implement all proven changes and unit/regression tests in a reproducible build tool.
5. Optional mini nav polish only if backed by parsed resource format and reversible delivery; otherwise omit and report why.
6. Final PC release candidate: one installable NeoUI theme with **explicitly documented selected skin strategy**; precheck, restore, back-out; user approves before writing to car.
