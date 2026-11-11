# Current release rules

Current authorization is offline only. No SD or vehicle writes. Baseline discovery outputs stdout only; the future installer logging/backup/write rules below do not grant permission to execute them now.

States must remain distinct: PC design/MCF validation; console-reported installed; post-reboot visual/functionally verified. Current v3 is only the first. V2 has console-reported install success, with fresh state and reboot behavior unconfirmed.

Never substitute v1 design source for expected-current installed baseline. Classify a fresh exact state, selected skin, metadata, owner/mode, mount state and capacity; reject unknown hashes. Preserve pre-NeoUI M.I.B., v1, v2 and future predecessor backups with distinct labels and SHA1/SHA256. Restore exact predecessor bytes and attributes, not an older reference merely because its recovery script exists.

Future authorized modes: no marker means PRECHECK-only; INSTALL_V3_NOW means identical mandatory precheck then install in the same invocation; RESTORE_V2 is mutually exclusive and applies only to confirmed v2 predecessor. Conflicts fail before writes. DIAGNOSTIC_ONLY never silently wins. No auto-arming. A separate precheck visit/SD swap is optional, not mandatory. Explicit approval must follow review of a concrete release report.

Future write sequence: verified SD probe/log setup; firmware/payload/current-state gates; independently verified SD backup; calculated capacity; feasible on-device predecessor backup; app writable mount; verified adjacent staging; preserve actual attributes; same-filesystem rename; sync/final hash; original read-only mount restoration; explicit result and marker-removal instructions. Do not assume chmod+x preserves owner/mode or old777 applies. Fail safely if logging cannot initialize; never overwrite unverified backups.

Future outcomes must distinguish pre-write abort, replaced-but-remount-failed, post-write mismatch, rollback verified and rollback failed. Preserve error evidence and viable backups. No claim that script rollback guarantees boot/GEM recovery. Installer tests must cover both success paths and all dependency/hash/marker/storage/backup/copy/move/remount/interruption failures. A syntax or happy-path test is insufficient.

Future package: immutable version, full validated MCF if required, exact source/target hashes and sizes, changed-ID whitelist, firmware/permissions/storage manifest, backup checksum inventory, PRECHECK_AND_INSTALL and ROLLBACK docs, append-only versioned SD log contract, shell sources, complete simulation report and carefully scoped PC marker/copy/log instructions. No such deployable package is produced by the current collector or design rehearsals.

No changes to skin0/1/2, selectors, compiled view code, ambient maps, nav rendering/roads/POIs/routes or safety/status icons without their separate evidence/release gates. Independent slot remains UNKNOWN. Derived firmware/master art stays local-only; only original code/docs and rights-cleared assets may be committed.
