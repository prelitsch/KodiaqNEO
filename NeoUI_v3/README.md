# NeoUI v3 offline workspace

The normal build pipeline reads the 54 mapped editable PNGs, builds a complete MCF from the exact v2 pilot, and preserves all 94 v2 changes (including 74 MENU/foundation changes). It generates versioned local artifacts, previews, a declarative changeset, validation and independent restoration. The user's M.I.B. screenshots identify the installed skin3 MCF as v2 by SHA-1 and size; normal startup and MENU after reboot are user-confirmed. Installation remains blocked by the separate release gates.

All graphics, previews and mapping research are preserved. Start with [pipeline reconciliation](neoui_reports/PIPELINE_RECONCILIATION.md), [current state](neoui_reports/CURRENT_STATE.md), [read-only baseline precheck](neoui_reports/BASELINE_PRECHECK.md) and [release rules](neoui_reports/RELEASE_RULES.md). Older media/HOME/vehicle reports remain historical design validation relative to v1.

```powershell
./NeoUI_v3/build.ps1                        # current PNGs -> validated v2-based offline revision
./NeoUI_v3/build.ps1 -Changed 'nav.action.new_destination.c06'  # after editing its master PNG
./NeoUI_v3/build.ps1 -Mode Audit            # input audit, no published build
./NeoUI_v3/build.ps1 -Mode Test             # isolated pipeline regression checks
```

These commands write only inside NeoUI_v3; no SD or vehicle access. Python 3.10+ standard library is sufficient; pass `-PythonPath` or set `NEOUI_PYTHON` if Python is not on PATH. Open `neoui_build/visual_builds/latest.json` to locate the newest successful build and its `previews/index.html`. The pointer does not activate an installed baseline. Release mode refuses installation.

The user ran `tools/baseline_precheck.sh` on the vehicle and supplied screenshots. The logged precheck wrapper stores future receipts and full skin3/info.txt contents on SD; it cannot install. Selected skin, QNX mount semantics, device SHA-256/clock availability and installation/rollback validation remain release concerns. See `neoui_reports/LIVE_BASELINE_OBSERVATIONS.md`.

[VISUAL_EDIT_GUIDE.md](VISUAL_EDIT_GUIDE.md) explains editing, declared names, build commands, all outputs, preview limitations and comparison with earlier offline revisions. Historical builders retain their v1 design-source guards; normal visual revision builds use the verified v2 reference and preserve unrelated records.

Open neoui_previews/MEDIA_BT_V3_PREVIEW.html for existing source-component comparisons and earlier galleries. Previews are not captured vehicle output. Derived firmware/master art, MCFs, recovery archives and previews are local-only and ignored by Git. Only original code/docs and rights-cleared assets may be committed; no commit or installation is part of this work. Independent selectable skin remains UNKNOWN.
