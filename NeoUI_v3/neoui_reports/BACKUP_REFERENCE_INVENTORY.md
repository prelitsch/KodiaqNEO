# Labeled reference and recovery inventory

These references are distinct and hash-verified on PC. Only the pre-NeoUI file is labeled a historical PC backup. Cached install payloads are not fresh independent backups of the installed unit. No file was copied to/from an SD card or vehicle. No backup was overwritten.

| State label | PC provenance | Bytes | SHA256 |
|---|---|---:|---|
| mib_pre_neoui | skin3_before_NeoUI.mcf | 30758884 | 0cd5623541b32eb865716eadd86f978c018797f2b2be83d00289c3f1090886e4 |
| neoui_v1 | NeoUI_v3\neoui_workspace\asset_dump\skin3_neoui_v1_payload.mcf | 32173128 | dfb37cb771c58fb838d3797c3bf356e8fae9475aa980a236b7e9cba055f5cd58 |
| neoui_v2_pilot | NeoUI_v3\neoui_workspace\asset_dump\skin3_neoui_v2_pilot.mcf | 32861680 | cfe0aabb1e67e2ea06a07ea365fc24f69e3901e0508a02e87ab8525b92dac103 |
| v3_design | NeoUI_v3\neoui_build\NeoUI_v3_MEDIA_BT_skin3.mcf | 32108500 | 86519e2621e63c3183d317fe6a0badca96030e38048db8962903707a74e2fd86 |

Current installed predecessor, selected skin, owner/mode and mount state remain UNKNOWN. Historical v1 mode777/root:root is not a v3 instruction. Existing v1 design recovery archives restore v1 only. A confirmed-v2 release requires separately labeled, independently verified exact-v2 predecessor backups and original-state recovery copies; do not rename a v1 payload/backup to v2.
