# NeoUI v3 offline workspace

**Release hold:** updated AGENTS.md records v2 installer success; the fresh baseline and post-reboot behavior remain unconfirmed. The existing54-record v3 container is a preserved **v1-based design reference**, not an approved v2 upgrade. Applying it directly over v2 would revert94 v2 records, including74 MENU/foundation records. No rebased deployment payload has been produced.

All graphics, previews and mapping research are preserved. Start with [pipeline reconciliation](neoui_reports/PIPELINE_RECONCILIATION.md), [current state](neoui_reports/CURRENT_STATE.md), [read-only baseline precheck](neoui_reports/BASELINE_PRECHECK.md) and [release rules](neoui_reports/RELEASE_RULES.md). Older media/HOME/vehicle reports remain historical design validation relative to v1.

```powershell
./NeoUI_v3/build.ps1                        # off-car audit/checks only
./NeoUI_v3/build.ps1 -Mode DesignRehearsal   # reproduce named editable masters separately
./NeoUI_v3/build.ps1 -Mode IconRehearsal     # one named icon/diff/restore demonstration
```

These commands write only inside NeoUI_v3; no SD or vehicle access. Release mode always refuses while baseline/release gates remain unresolved. Existing Git for Windows sh runs isolated mocked precheck tests; WSL is not required. Python standard library and existing Node checks validate the offline pipeline.

The read-only tools/baseline_precheck.sh is prepared, not run on hardware. It emits stdout/stderr receipts only: no SD probe/log/backup, remount, app write or install mode. tools/review_baseline.py reviews a future independently collected receipt on PC without activating a baseline or authorizing installation. Selected-skin, mounts, SHA256 availability and post-reboot evidence can remain explicitly unresolved.

[VISUAL_EDIT_GUIDE.md](VISUAL_EDIT_GUIDE.md) explains54 semantic resource keys, local editable masters, declarative changesets and deterministic immutable design rehearsals. Historical builders retain their v1 design-source guards; those are not current-installed-hash guards. A future predecessor-based release must retain unrelated current-state records and restore that exact predecessor.

Open neoui_previews/MEDIA_BT_V3_PREVIEW.html for existing source-component comparisons and earlier galleries. Previews are not captured vehicle output. Derived firmware/master art, MCFs, recovery archives and previews are local-only and ignored by Git. Only original code/docs and rights-cleared assets may be committed; no commit or installation is part of this work. Independent selectable skin remains UNKNOWN.
