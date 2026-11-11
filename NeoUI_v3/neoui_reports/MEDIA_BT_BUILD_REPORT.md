> RELEASE HOLD: This is historical v1-based design validation, not an approved v2→v3 payload. Updated AGENTS.md reports v2 installer success; fresh baseline and post-reboot checks remain unconfirmed. See PIPELINE_RECONCILIATION.md.

# MEDIEN / Bluetooth — verified offline graphics

Eight new assets, 54 total. The exact previous46-record stage is retained. This is a versioned skin3 fallback; independently selectable new slot remains UNKNOWN. It is not a complete or car-tested theme release.

## Resource findings

| Component | Exact binding | MCF / geometry |
|---|---|---|
| BT source card | Mbam array344 → logical849 | 2217 / 450×450 |
| BT source-off card | array396 → logical901 | 2202 / 450×450 |
| Generic fallback / dynamic artwork border | array347 → logical852 | 2214 / 450×450 |
| Generic source-off | array399 → logical904 | 2199 / 450×450 |
| Source-list button states | array147 → logical564/569/573; resourceButtonsMediaType341/342 | 1134/1133/1131 / 50×94 |
| Media selection / playlist / playlist setup | array252 → logical732; aliases830/831 | 1036 / 78×52 |
| Existing transport variants, retained | arrays304/306/308/310 → logical797–812 | Existing sixteen 120×120 records |

MEDIA_BT_RESOURCE_EVIDENCE.json records module hashes, methods/ROM offsets, bytecode digests, reviewed lookup PC/literal spans, all state positions, logical IDs, assigned fields and MCF aliases. Sources are exact skin1 metadata and viewhandler lineage used by M.I.B. skin3, plus the exact MU1440 runtime backup. Installed skin3 metadata has not been freshly read from the vehicle; it must be hash-checked before release.

The Mbam cover-choice wrapper passes source/on and source-off arrays to CommonScript. The reviewed output tail assigns selected array[0] to outputs0/1 (default/error) and generic source array[0] to output2 (border). Mbam then calls set_imageDefault, set_imageError and set_borderImage. Dynamic cover ResourceLocator/availability and imageResource assignments remain unchanged. Source-off filenames are resource names, not an asserted disconnected-state enum mapping. MediaBtAudioMain also binds the existing sixteen transport states, upgrading their evidence beyond visual-only matching.

## Actually changed

- Four fallback/border images: darken/cool existing panel pixels. A data-derived mask from the source/on counterpart protects chromatic identity and pixels brighter than145, including Bluetooth symbol, BT source text, music glyph and bright frame. The same identity mask protects the corresponding off image. Original off-state glyph dimming is retained. No new text, logo, geometry, opacity or artwork is introduced.
- Three TYPE090 source-list button state images: cool neutral separators and replace baked decorative green press glow with ice. Preserve all18 state positions, native50×94 alpha and nine-slice insets. No runtime state enum labels are guessed.
- Playlist/selection glyph: neutral pixels receive the existing ice palette; chromatic/yellow music detail is exact.

Shared scope: generic2214 is also the dynamic artwork border across media source views. TYPE090 states can appear in other skin3 lists. Playlist1036 aliases playlist and playlist setup. BT source-off images can be used by other media views. This changes skin3 resources only; it creates no independently selectable option and changes no skin0/1/2 files. Actual cross-screen runtime coverage remains subject to head-unit confirmation.

## Renderer-controlled paths retained

Shuffle/repeat icons956/954/953/952 and play-more-like955 are unchanged. Exact skin COLOR__ARRAY1_8 includes alpha-white4BFFFFFF, white COLOR_16 and greenFF96FF00. TYPE904 array204 has no active bitmap background. These states cannot be given an independent bitmap background merely by painting a guessed image.

Seekbar track61, foreground39 and indicator917 are unchanged; slider arrays40/44 include additional state colors. The existing behavior and visibility scripts remain exact. Retinting these paths would require more renderer analysis and possibly compiled metadata changes, which are outside this asset-only stage. Source-control BT icon1034 remains unchanged. Media spot1889 is fully transparent; it is not treated as an editable visible panel.

The shared MEDIA backdrop aliases MENU2331/2330 and stays exact, as do complete blue action-bar strips. 106 MENU/foundation records and 288 non-controlbar NAVIGATION records remain exact. No safety/status, skin0 vehicle illustration, map engine, POI/CFF, routing, navigation file, viewhandler, image metadata, ambience map, selector or NVRAM change. Other source-specific card graphics (USB/SD/CD/DVD etc.) are retained.

## Validation

- Input v1 SHA1: 641c34e42ed5843c1795bf860fd4cb7bbb913fdb.
- Input v1 SHA256: dfb37cb771c58fb838d3797c3bf356e8fae9475aa980a236b7e9cba055f5cd58.
- Previous stage SHA256: a4d5cddb77ce92583e091b9957f32e6f5b2f40bf95421e223de95cf247e11cf2.
- Candidate SHA256: 86519e2621e63c3183d317fe6a0badca96030e38048db8962903707a74e2fd86.
- Candidate: neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf; 2345 records, exactly54 changed.
- All MCF CRCs, IDs/index/count/bounds and original/new geometry/alpha pass. Transparent RGBA values remain exact. All previous46 records are retained exactly from the previous stage.
- 63476 protected identity/bright-glyph pixels remain exact across the four cards. New button states remain distinct; chromatic playlist detail is preserved.
- Independent recovery uses original-prefix offsets and original changed records plus unchanged candidate records. Restored v1 SHA256: dfb37cb771c58fb838d3797c3bf356e8fae9475aa980a236b7e9cba055f5cd58.
- Preview links and script syntax pass; 360 combinations cover18 slots ×5 card/art choices ×2 transport choices ×2 text choices, checking every generated image path. Native source/candidate PNG compositions inspected. Browser visual QA is not performed because local-file URL access is blocked; no workaround attempted.

## Preview and reproduction

Open neoui_previews/MEDIA_BT_V3_PREVIEW.html. It includes BT/on-off and generic/on-off pairs, generic-border artwork sample, all18 raw transport/source-button slots, unchanged mode-color/seekbar samples, each new native asset pair and all eight original reference scenarios. The source-based player uses illustrative coordinates and sample text; it does not claim exact runtime layout, clipping, nine-slice behavior or tint. The artwork pattern is preview-only and never enters the MCF.

From repository root:

```powershell
python NeoUI_v3/tools/trace_media_bt.py
python NeoUI_v3/tools/build_media_bt_v3.py
python NeoUI_v3/tools/verify_restore.py --media-bt
python NeoUI_v3/tools/preview_media_bt.py
python NeoUI_v3/tools/check_media_bt.py
python NeoUI_v3/tools/refresh_verified_reports.py
```

No installer, install image or SD output is generated. Candidate/recovery/derived resources/previews remain ignored by Git and local-only. Original project code and documentation are reviewable; no commit was requested or made. Offline restoration is not a boot-recovery guarantee. Current firmware/MU/hash/metadata/permissions checks, no-write device preflight, release review and explicit user authorization remain required before installation.
