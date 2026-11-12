# NeoUI v3 current state

The mapped-PNG offline revision pipeline is implemented. Normal `build.ps1` uses `tools/build_visual_revision.py`, the exact v2 pilot MCF, the locked 54-resource catalog and the current editable PNG masters. It no longer invokes the historical reconciliation/report writers during routine builds.

The current masters reproduce the preserved v2-based candidate: 32,797,052 bytes, SHA-1 `2787801d63ae74483b3d005a673a10e1c723e5b1`, SHA-256 `9d7b6601a7d1614b453a4b8428efeeff2daef9684471ff33f54fecb56d1cee09`. All 94 v2 changes, including 74 MENU/foundation changes, are preserved exactly. All 106 protected MENU/foundation records and every unmapped record are checked against v2.

For a later mapped edit: save the local RGBA PNG with unchanged dimensions, alpha mask and transparent RGB bytes, then run `./NeoUI_v3/build.ps1 -Changed 'mapped.semantic.name'`. Declare all edited variants. The tool fails on undeclared/unknown targets, unexpected sources, PNG/MCF corruption, geometry/alpha changes or changed v2 records. It produces immutable input-versioned outputs under `neoui_build/visual_builds/`, including a complete candidate, per-resource before/after gallery, manifests, input snapshots and independent exact predecessor restoration. `latest.json` records the newest successful offline build, never the installed baseline.

See `VISUAL_EDIT_GUIDE.md` for commands, prerequisites, comparison with earlier versions and preview limitations; see `VISUAL_PIPELINE_VALIDATION.md` for the validation evidence. Existing original masters and historical source containers are preserved. Generated MCFs, derived PNGs, snapshots and previews remain local and ignored by Git.

The user-provided live screenshots identify skin3 as the v2 pilot by SHA-1/size and show collector exit 0 and stable bytes. The user confirms matching skin3 info.txt and working v2 startup/MENU after reboot. Selected skin remains unconfirmed, SHA-256 and UTC are unavailable on-device, and QNX mount/install/rollback validation still requires review. These installation gates are separate from a completed PC build. `release-policy.json` remains unchanged; no installer is included and `-Mode Release` refuses.

Historical `DesignRehearsal` and `IconRehearsal` modes remain explicit v1 design demonstrations. They are not the normal PNG-edit build path. Independent extra selectable skin support remains UNKNOWN; current candidate is a skin3 fallback, not a new slot. No SD or vehicle operations are performed by the visual revision pipeline.
