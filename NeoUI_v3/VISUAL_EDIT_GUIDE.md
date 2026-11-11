# Named visual edits and offline builds

resource-map.json is the54-resource semantic catalog. neoui_reports/RESOURCE_NAME_INDEX.md lets the user identify a screen/key/MCF ID; existing interactive galleries supply source comparisons. Existing research and IDs are reused. Unknown requests, MENU glyphs not in this catalog, fonts/layout, safety symbols, shared skin0 resources and navigation rendering are blocked pending evidence; do not substitute a lookalike.

Example mapped requests: `nav.action.new_destination.c06`, `media.bt.card.source`, `shared.action.media`, `home.panel.primary`. All aliases, shared scope, dimensions, format, state codes, source and modified hashes and evidence links are recorded. Changing a generic source card also changes the dynamic-art border; linked states and shared consumers must be reviewed together.

Editable PNG masters are exported under resources/masters with descriptive paths. They are source-derived proprietary art, local-only and ignored by Git. Do not publish them or imply that the supplied artwork has redistribution rights. Original transformation code remains in the previous stage builders. PNG conversion accepts exact-size non-interlaced RGBA8 (all standard PNG filters); preserves alpha and transparent RGBA; uses the proven zlib/MCF encoder. No font dependency or AI-generated artwork. Python and zlib versions are recorded in rehearsal manifests.

```powershell
# Audit only: preserve existing candidate and masters, run offline checks.
./NeoUI_v3/build.ps1
# Repack editable masters into a separate immutable offline design rehearsal.
./NeoUI_v3/build.ps1 -Mode DesignRehearsal
# Demonstrate one mapped non-safety icon edit in memory; masters stay unchanged.
./NeoUI_v3/build.ps1 -Mode IconRehearsal
```

The last mode alters only MCF988 in a separate design rehearsal, checks deterministic repeated packing, exact one-record diff and independent restoration to the preserved design. Before/after native PNGs are in neoui_previews/rehearsals. This is a tooling demonstration, not proposed install artwork; all original masters, candidates and historical previews remain intact.

For a real visual request, edit only explicitly approved named masters and all appropriate linked variants, then create/review its declarative changeset and previews. The off-car builder validates source hash, mapping uniqueness/whitelist, master format/geometry/alpha, MCF CRC/count/bounds, changed-record diff and output digest. Rehearsal outputs are content-addressed under neoui_build/rehearsals; existing differing bytes are refused. Unchanged records stay exact; TOC offsets/sizes/CRC and altered IMG compressed bytes/CRC can change.

Important current limit: this is a v1-based **design** round trip, not a fresh v2→v3 release. The catalog does not activate a live baseline. A future approved predecessor-based release must preserve all unrelated v2 bytes and restore that predecessor. `-Mode Release` always refuses. No delta or single PNG installation is implied; the head unit uses a complete validated MCF unless another mechanism is proven. Future installed v3 revisions need immutable release versions, exact expected-current hashes, full precheck/installer/restore gates and post-reboot verification each time.
