# v3 pipeline reconciliation with v2 field findings

## Baseline from M.I.B. screenshots

The user supplied read-only collector screenshots showing `MHI2_ER_SKG13_P4526` / `MU1440`, the skin3 MCF SHA-1 `28e26e2603497571663a93b303e930a2d4787f50`, 32,861,680 bytes, and `REFERENCE_MATCH=neoui_v2_pilot`. The collector ended `COLLECTED_NOT_RELEASE_AUTHORIZATION`, was stable during collection, and wrapper exit was 0. Three shared metadata hashes match the local skin1-derived reference. See [LIVE_BASELINE_OBSERVATIONS.md](LIVE_BASELINE_OBSERVATIONS.md).

SHA256 and UTC time were unavailable on the unit, the selected skin is unknown, and metadata/mount/post-reboot/recovery checks remain incomplete. The live screenshots support v2 as the **working offline predecessor**; they do not clear a release gate or activate `release-policy.json`.

## Rebased offline candidate

`tools/rebase_v3_onto_v2.ps1` verifies the v1, v2 and v3 design containers by their local SHA-1/SHA-256 references, verifies every one of the 54 design source and target record hashes, and requires each v2 target record to still equal its reviewed v1 source. It then starts from the exact v2 MCF and replaces only the 54 explicit design records.

The resulting [v2-based build report](V2_BASED_BUILD.json) records:

- Candidate: `neoui_build/NeoUI_v3_v2_based_candidate.mcf`, 32,797,052 bytes, SHA-1 `2787801d63ae74483b3d005a673a10e1c723e5b1`, SHA-256 `9d7b6601a7d1614b453a4b8428efeeff2daef9684471ff33f54fecb56d1cee09`.
- Exactly 54 changed records against v2.
- All 94 v2 changes retained byte-for-byte, including the protected MENU/foundation records; there is no overlap with the 54 design IDs.
- MCF offsets and CRCs validated. A restoration rehearsal reconstructs the v2 pilot byte-for-byte (SHA-1 `28e26e2603497571663a93b303e930a2d4787f50`).

The original v1-based design candidate remains preserved. Candidate and restoration MCFs are local-only generated/proprietary artifacts, ignored by Git.

## Install build status

No installation package is being labeled complete or fail-safe yet. On-device QNX installation and rollback paths have not been failure-tested; interrupted writes can leave the GUI unusable, and rollback is not guaranteed to recover a boot failure. The selected skin is unknown, UTC/SHA-256 are unavailable, raw QNX mount behavior and `info.txt` lineage need review, post-reboot v2 function is unconfirmed, and final payload/backup/storage calculations have not been approved.

`release-policy.json` remains `installed_baseline: null`, `selected_skin: null`, and `release_ready: false`. Do not copy or run an installer. The next release work is to close the listed evidence gaps, finish a same-filesystem installer and restore failure-path simulation, obtain explicit release review/authorization, and only then prepare a marker-armed SD package. No SD or vehicle writes were performed by this offline reconciliation.
