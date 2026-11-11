# Read-only baseline precheck â€” prepared offline

tools/baseline_precheck.sh is a read-only vehicle collector. The user ran it through M.I.B. and supplied screenshots showing a completed collection (exit 0). A new logged precheck wrapper stores stdout/stderr, the full skin3/info.txt contents, and status in a numbered SD log. The wrapper writes only that log to SD; it has no installer or vehicle-write path. The separate build.ps1 remains off-car only.

The collector uses the observed firmware reader `/net/mmx/mnt/app/eso/bin/apps/pc` through `on -f mmx` with the two verified train/MU read identifiers, and `/net/rcc/usr/bin/sha1sum`. It checks available dependencies (date is optional), exact firmware/MU, regular non-symlink target, byte length, SHA1, optional SHA256, numeric-owner/mode listing, images.res/viewhandler/info/ambience-map hashes, raw `df -k` and mount listing, and repeat target hash/size/attributes. Command failure, UNKNOWN hash, unsupported firmware, missing file, ambiguous storage rows, target instability or v3/diagnostic marker presence aborts. It never retries a failing hash or interprets a marker as permission.

The collector itself emits only stdout/stderr and performs no SD write/readback, log, backup, mount option, staging or attribute change. The logged wrapper creates and verifies the SD log before reading vehicle paths. The no-argument `mount` command lists state only. No-marker execution only collects evidence. The explicit `--offline-fixture` option prefixes every device path for the test harness and labels the receipt OFFLINE_SIMULATION; it can never establish live evidence.

Unknowns remain visible: selected skin has no verified automatic read method; record an Engineering Menu observation separately without changing selection. SHA256 may not exist on QNX; UNKNOWN is retained and PC review remains incomplete. Raw mounts need QNX-specific review. The three shared metadata hashes match the traced skin1-derived lineage. The user confirms the installed skin3 info.txt matches the local skin3 copy. When `date` is absent, the collector emits UNKNOWN timestamps; PC review then marks freshness incomplete. Device clock freshness, post-reboot behavior and independently verified backups still require evidence. The collector does not copy a full current MCF to the PC and cannot validate its internal resource directory on-device. Matching both hashes and size to a PC-validated reference establishes identity only, not rendering or recovery.

Future, separately authorized receipt review on PC:

```powershell
python NeoUI_v3/tools/review_baseline.py --capture NeoUI_v3/neoui_workspace/baseline_receipts/capture.txt
```

Place an independently collected raw stdout receipt there only when one exists. Do not synthesize one from historical console notes. The reviewer rejects duplicate/malformed fields, failed/simulation/stale receipts, firmware/hash/size or metadata mismatches. It writes an ignored local PC review report. It never changes release-policy.json, activates a baseline, arms markers or authorizes installation. Even complete identity evidence leaves selected-skin, mounts, post-reboot, backup, final-build, storage and authorization gates pending.

Run the offline tests only:

```powershell
python NeoUI_v3/tools/test_baseline_precheck.py
```

Existing Git for Windows sh is used, not WSL. Every device command is mocked with isolated fixture paths under NeoUI_v3. Tests cover27 collector cases and8 receipt checks; fixture file hashes are unchanged. Shell syntax and read-only command/redirection audits pass. ShellCheck is unavailable and QNX utility behavior is not empirically tested by these mocks. Full install/copy/move/remount/interruption recovery tests remain future release requirements; this collector contains none of those write operations.

Free space is recorded in1024-byte blocks without claiming the historical100MiB v2 threshold is sufficient. Final release budget must include actual predecessor backup, payload staging, rollback staging and reserve, rounded upward. Reject ambiguous units/filesystems and recompute with actual final sizes; no old free-space measurement is accepted as live.
