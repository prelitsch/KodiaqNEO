# Edit a mapped PNG and build a v3 revision

The normal build now starts from the exact v2 pilot MCF and applies the current 54 mapped masters. Every v2 MENU change and every record outside that whitelist stays byte-identical to v2. The original v1-based design and earlier candidates remain available as references.

Keep the labeled local references: `neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf`, `neoui_workspace/asset_dump/skin3_neoui_v2_pilot.mcf`, `neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf` and `neoui_build/NeoUI_v3_v2_based_candidate.mcf`. Their exact hashes are enforced. A fresh Git clone must be supplied with these private inputs and `resources/masters/` from the local project backup; Git deliberately excludes firmware and derived artwork. Missing or different inputs stop the build rather than triggering new extraction or guesses.

1. Find the semantic name, PNG path, geometry, linked variants and shared consumers in `resource-map.json` or `neoui_reports/RESOURCE_NAME_INDEX.md`.
2. Edit its PNG under `resources/masters/`. Save exact-size, non-interlaced RGBA8. Preserve the alpha mask and RGB bytes of fully transparent pixels. Recoloring is supported; an outline/alpha change requires a separately reviewed pipeline change. Editors that discard invisible RGB data can cause validation to fail.
3. Tell Codex the mapped names/files you changed, or run the command below. Declare every modified variant. The build refuses pixel changes outside the declared names and refuses PNG files that are missing or outside the catalog. Do not manually update catalog hashes or old manifests.
4. Open the generated preview and review all relevant states and shared consumers before considering installation.

Example: edit `resources/masters/nav/action/new_destination/c06.png` (78 x 52), mapped to `nav.action.new_destination.c06`, ID 988. Then run from the repository root:

```powershell
# Normal offline revision; automatically compares with the latest successful offline build.
./NeoUI_v3/build.ps1 -Changed 'nav.action.new_destination.c06'

# More than one edited mapped asset:
./NeoUI_v3/build.ps1 -Changed 'nav.action.new_destination.c06','shared.action.media'

# First/no-edit build; reproduces the preserved v2-based candidate.
./NeoUI_v3/build.ps1

# Check inputs and edit declarations without publishing a revision:
./NeoUI_v3/build.ps1 -Mode Audit -Changed 'nav.action.new_destination.c06'

# Isolated pipeline regression checks; production masters are never edited by these tests.
./NeoUI_v3/build.ps1 -Mode Test
```

Python 3.10+ is required (standard library only). If it is not on PATH, set `$env:NEOUI_PYTHON` to its executable, pass `-PythonPath 'C:\path\to\python.exe'`, or store its executable path as the single line in ignored `neoui_workspace/python-path.txt`. This workspace has that local interpreter configuration prepared. An explicit parameter/environment variable takes precedence. If a bundled interpreter is updated or removed, point the configuration at an available Python 3.10+ executable. The script works regardless of the shell's working directory; `-PreviousBuild` paths are relative to `NeoUI_v3`.

Each validated revision is published under `neoui_build/visual_builds/v3-<input-digest>/`:

| File | Purpose |
|---|---|
| `candidate.mcf` | Complete v2-based MCF with the current mapped PNG edits |
| `previews/index.html` | Offline gallery: v2 / previous offline build / new, native PNGs on checkerboards, aliases and shared scope; toggle unchanged assets |
| `manifest.json` | Inputs, output hashes, dimensions/alpha, all 54 resources, preservation and validation results |
| `changeset.json` | Exact changed resources against the preceding offline revision |
| `masters/` | Snapshot of all 54 PNG inputs, so later edits do not change the historical revision |
| `recovery/` | Saved predecessor prefix, offsets and original changed records |
| `restored_predecessor.mcf` | Independently reconstructed, byte-identical previous offline MCF |
| `SHA256SUMS` | Checksums of the complete build contents |

The builder verifies known v1/v2/design hashes, mapped source-record hashes, 2,345 IDs/order/bounds/CRCs, full decompression, dimensions, alpha, decoded output pixels, exact changed-ID whitelist and deterministic packing. It checks all 94 v2 changes, including 74 MENU/foundation changes, and every unmapped record against v2. It restores the preceding offline version independently using saved offsets rather than the packing routine. Existing differing build contents are refused, and `latest.json` advances only after validation succeeds. Failed builds never replace the previous revision or its pointer.

The gallery contains exact decoded resource previews, not a claim of full-screen or on-car rendering. Runtime tint, text, map behavior and shared usage still come from the existing firmware. Review aliases and linked states together; unmapped MENU glyphs, safety icons, fonts/layout, skin0 resources and map rendering require separate evidence.

By default, the first comparison is the preserved v2-based candidate (`9d7b6601...`), and later comparisons use `neoui_build/visual_builds/latest.json`. This pointer records a successful **offline build**, not the installed vehicle version. To compare with a specific earlier build, pass `-PreviousBuild 'neoui_build/visual_builds/v3-...'`; use `-PreviousBuild initial` to compare with the original v2-based candidate. All earlier edits remain in the editable masters and are included when rebuilding from v2.

All generated revisions, snapshots, MCFs and previews are proprietary/source-derived local artifacts, ignored by Git. Publish only original code/docs or assets with established redistribution rights. `DesignRehearsal` and `IconRehearsal` are retained as historical v1 demonstrations; the normal `Build`/`Audit` modes do not run them or rewrite the catalog/research reports. `Release` still refuses: installation remains a separate reviewed process with exact installed-baseline precheck, SD logging and explicit authorization.
