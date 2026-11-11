# Discovery instructions for Codex: do the engineering, don't guess

## Task 0 — input discovery
- Work from actual `C:\Users\aldin\OneDrive\Desktop\Kodiaq Moding` project root. Locate handoff files there after user extracts ZIP.
- Check `app50_extract/lba0` and M.I.B zip. Use targeted listing, not full recursive hashing of 2.75 GB archive at every run.
- Reconcile source archives names and expected hashes; create `neoui_reports/INPUT_INVENTORY.csv` and `CURRENT_STATE.md`.

## Task 1 — selectable slot proof (PRIORITY 1)
- Read official SKG13 M.I.B. wiki (linked in project context) and inspect the installed local M.I.B. zip scripts concerning Image MOD. Find what creates skin3 and the exact skin selector setting/variable and acceptable IDs. There may be a hard-coded list, multiple image banks or config dependencies; identify by evidence rather than supposition.
- Inspect original `skin0/skin1/skin2`, determine differences in required files and if `skin3` clones one with image patch. Investigate whether the HMI dynamically scans skin dirs, reads skin selection from engineering menu, or selects enumerated versions.
- Output `SKIN_SLOT_FEASIBILITY.md` (YES/NO/UNKNOWN) with *what can be selected in car*, technical proof, any changes beyond `images.mcf`, recovery exposure, and selected approach.
- Do NOT attempt to add a skin slot by modifying app executables or compiled viewhandlers in this release.

## Task 2 — resource mapping (PRIORITY 2)
- Build Python command-line tools that can list and extract MCF records deterministically, reconstruct PNGs, compare skin0/1/2/3, produce indexed contact sheets and diff manifests. Reuse prior scripts from M.I.B / v2 pilot / archived project if correct, rather than reinventing with unvalidated format guesses.
- Inventory `images.res`, `info.txt`, `viewhandler.zip` module filenames, `ambienceColorMap.res`, nav icon maps. Decompilation/disassembly only for read-only mapping as needed. Do not modify compiled binaries.
- Check unusual current HOME backgrounds from image screenshots. M.I.B official background blue depends on ambient color, suggesting UI may be runtime-colorized. Test hypothesis with actual config references rather than only source PNG color.
- Setup list and Fahrzeug may share skin0 assets; verify stock/current skin0 discrepancy before redesign. Propose either per-skin adjustments (preferred) or shared global adjustments with user consent. Do not overwrite factory based on old factory PNG.
- Create machine-readable `resource_map.json` with fields: id, path, source_sha256, original_dimensions, screen, state, evidence, confidence, slot_scope, proposed_change, dependencies, side_effects.

## Task 3 — navigation feasibility (OPTIONAL LOW RISK)
- Inspect `navigation/resources/app/sk/eu` raw assets and the provided nav archive. `gui/road_name_marker.png` and pin shadows are standalone files, but that does NOT prove they are used on the user's live nav. Determine which renderer loads which.
- Analyze mapping XML. For `images.cff`, `textures.cff`, `roadicon.ri.gz` use existing documented formats if available; otherwise show that parser/editing remains unproven. Avoid binary search-and-replace hacks.
- Limit this release to proven graphical changes, if any; no day/night mapconfig edits, routes, road widths or map palettes unless separately scoped after user approval.

## Task 4 — graphics build and QA
- Re-use Claude v2 source artwork where applicable, but do not replace good-looking M.I.B. MENU with less desirable experiments just to maximize modified IDs. Show before/after and ask targeted visual feedback only after integrated preview.
- Create an offline preview for all 8 photo scenarios (original photo may be cropped/rectified as visual reference; screen artwork should be rendered from actual assets when possible). Keep conceptual overlays clearly labeled.
- Include dark/night visibility, normal/selected/disabled states, dynamic text overlays, language-length stress tests (German), album artwork placeholders, and no rendering of inaccurate fake live map data.
- Validate MCF entry count/order/index, offsets, image data lengths, alpha/PNG integrity, and exact list of changed bytes; no changes to unexpected resources.

## Task 5 — release gating
- A new independent selectable skin must have a proven supported index, complete copied dependency tree, and risk report. If not, produce **fallback existing `skin3`** with checksum-aware installer and rollback to NeoUI v1. Do not package files for unsupported `skin4` and imply safe selection.
- Create `PRECHECK_ONLY` mode; capture current firmware and expected source hashes and storage available. No writable mount during read-only precheck except when explicitly necessary for log writing on SD; permit log output to removable SD only.
- Ensure multi-file install is transactional or has documented partial-failure recovery; no blind swap. Compare SHA1 for QNX environment, SHA256 on PC, and full back-up restore rehearsal.
- Deliver build reports, signed-off scope list, installer source, explicit apply/rollback instructions and known brick/recovery risks. Flag any release as NOT vehicle-tested until the user executes it and reports verified results.

## Definition of done
Done is **not** a nice design concept. Done is: evidenced real resource mapping for requested UI changes, reproducible artifact, exact compatible slot/fallback proof, validated package and rollback, visual screen review, and explicit user authorization before on-car operation. If a screen cannot be modified without compiled code, document an honest partial completion and offer choice — don't quietly omit HOME while labeling the build 'full'.
