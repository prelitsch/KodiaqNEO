# NeoUI v3 verified media candidate

Scope: a first, partial Graphite & Ice implementation: 16 media transport state variants. This is not the full seven-screen redesign.

- Input: packaged v1 SHA-1 `641c34e42ed5843c1795bf860fd4cb7bbb913fdb`; SHA-256 `dfb37cb771c58fb838d3797c3bf356e8fae9475aa980a236b7e9cba055f5cd58`.
- Output: `neoui_build/NeoUI_v3_verified_media_skin3.mcf`; SHA-1 `33ff91157a9770273aef955d7844192a40f0d106`; SHA-256 `0387eb588d1f7add4853e6a66727a2b0d338a51ee235b8041db1a5c147ce8398`.
- Exact changed records: 1635-1640, 1642-1646, 1654-1658. Logical IDs 797-812 map through the unchanged images.res table. Shared Media Control stage aliases are included in the manifest.
- Every asset remains 120x120, RGBA, with byte-identical alpha and unchanged silhouette. Grey shading is tinted graphite/ice-white; green focus hues become ice cyan. Source state codes C02/C04/C06/C07 stay separate; state names are not guessed.
- Every other MCF record is byte-identical to input v1. Existing v1 changes are inherited, not reworked. The M.I.B. MENU foundation and all skin0/nav resources receive no new edits.
- Verified: file/TOC/IMG CRCs, decompressed lengths, ID order/count, exact change set, distinct state images, native-size visual comparison, no-op rebuild, independent restoration to exact v1 bytes.

The candidate replaces the current M.I.B.-derived skin3; it adds no selectable skin. It is PC-validated and not vehicle-tested. Installed images.res lineage is inferred from the inspected M.I.B. copy script and still requires a fresh no-write hash check before any release. A local record recovery archive supports the PC restoration exercise; it is not a head-unit recovery guarantee. No install package or SD write is prepared.

Open `neoui_previews/VERIFIED_V3_PREVIEW.html`. The eight photographs document scenario coverage; only the media transport component has new implemented assets. HOME tint/bank semantics, vehicle illustration binding, lists and navigation remain separate pending work.
