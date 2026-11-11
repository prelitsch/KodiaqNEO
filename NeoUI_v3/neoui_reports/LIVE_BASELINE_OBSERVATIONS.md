# Live baseline observations from M.I.B. screenshots

## Evidence and scope

The user supplied screenshots of the M.I.B. `advanced_settings/run_individual_script/Console` output. The photos show receipt fields from firmware identity through raw `df` and scrollable mount output, stability result and wrapper status. They do not provide a plain-text capture, and the initial header fields are not all visible. Values below are transcribed from the photos and the user's accompanying observation summary; no receipt text was saved on the SD card.

The collector completed successfully with `PRECHECK_COLLECTOR_EXIT=0`, `STABLE_DURING_COLLECTION=true`, and `END=COLLECTED_NOT_RELEASE_AUTHORIZATION`. That means the read-only collection ran to completion. The end marker explicitly does not authorize installation.

## Observed values

| Field | Screenshot value |
|---|---|
| Firmware | `MHI2_ER_SKG13_P4526` |
| MU | `1440` |
| Target | `/net/mmx/mnt/app/eso/hmi/lsd/Resources/skin3/images.mcf` |
| Current bytes | `32861680` |
| Current SHA-1 | `28e26e2603497571663a93b303e930a2d4787f50` |
| Reference match | `neoui_v2_pilot` |
| Current SHA-256 | `UNKNOWN` (device has no usable `sha256sum`) |
| Attributes | `-rwxrwxrwx`, owner/group shown as `0 0`; stable across the collector's two observations |
| Selected skin | `UNKNOWN`; collector has no verified read-only selector query |
| Start/end UTC | both `UNKNOWN` because `date` is unavailable |
| Write policy | `STDOUT_ONLY` |
| Release ready | `false` |
| Free app space | `326097 KiB`; raw `df` reports `1404880 1078783 326097 77% /mnt/app` |
| Storage budget | `NOT_CALCULATED_UNTIL_FINAL_PAYLOAD_AND_STRATEGY` |
| Post-reboot verification | User confirms normal startup and v2 MENU worked after reboot |
| Collector end | `COLLECTED_NOT_RELEASE_AUTHORIZATION` |
| Wrapper exit | `PRECHECK_COLLECTOR_EXIT=0` |

The reported byte count is about `31.34 MiB`; free app space is about `318.45 MiB`. This is an observation, not a release storage calculation. Applying the current policy formula preliminarily gives 198,613 KiB required (32,092 KiB current-state copy + 32,029 KiB candidate + 32,092 KiB rollback staging + 102,400 KiB reserve), leaving 127,484 KiB against the screenshot free-space value. This estimate still needs confirmation against the final installer and actual QNX copy/rename strategy.

## Reference comparisons

The SHA-1 and byte count match the known v2 pilot MCF reference (`28e26e2603497571663a93b303e930a2d4787f50`, `32861680` bytes). The local extracted reference MCF also has that SHA-1. This identifies the observed `skin3/images.mcf` as the v2 pilot payload by the collector's reference check; a device SHA-256 is unavailable.

The screenshot metadata hashes were compared read-only with the local extracted skin1 lineage:

| Metadata | Device screenshot SHA-1 | Local reference SHA-1 | Result |
|---|---|---|---|
| `images.res` | `66dbe279caba75ad1fd4c0cccd5e636756da2de8` | `66dbe279caba75ad1fd4c0cccd5e636756da2de8` | Match |
| `viewhandler.zip` | `844c4127775432fdeb63ee6f020578e7ad015846` | `844c4127775432fdeb63ee6f020578e7ad015846` | Match |
| `ambienceColorMap.res` | `2b32d5611856cb74f9c57ed596bd83dd98c82b71` | `2b32d5611856cb74f9c57ed596bd83dd98c82b71` | Match |
| `Resources/skin3/info.txt` | Screenshot hash is visually ambiguous | Local skin3 copy SHA-1: `f1a2ac9acacffa5576cc58203d7c8f5e876e7f5b` | User confirms the installed skin3 `info.txt` matches the local copy; accepted as user-reported evidence |

The photos show `MOUNTS_RAW_BEGIN`, a scrollable sequence of mount entries, and `MOUNTS_RAW_END`. Visible entries include `/mnt/app` on `qnx6`, `/mnt/ota`, `/mnt/media`, `/mnt/navdb`, `/mnt/ols`, `/mnt/gecache`, `/mnt/adb`, `/mnt/icab`, `/mnt/mmebackup`, `/mnt/gracenotedb`, `/mnt/speech`, `/mnt/boardbook`, `/mnt/gemodels`, `/logosdisk`, `/ramdisk`, and mounted navigation/speech media. The collector labels app mount state `UNINTERPRETED_RAW_OUTPUT_REQUIRES_REVIEW`; the photos do not change that assessment.

## Assessment and release state

The collector completed and confirms the expected firmware/MU, a stable `skin3/images.mcf` matching the v2 pilot by SHA-1 and size, and matching `images.res`, `viewhandler.zip`, and `ambienceColorMap.res` hashes against the local reference lineage. This is sufficient to use v2 as the working predecessor for **offline** reconciliation, with the screenshot evidence recorded.

Release remains blocked. The selected skin is unknown; SHA-256 and UTC timestamps are unavailable; `info.txt` lineage, QNX mount semantics, post-reboot v2 behavior, recovery inventory, storage budget for the final candidate, final v2-based build/diff, and restore rehearsal remain unresolved. `release-policy.json` remains unchanged (`installed_baseline: null`, `release_ready: false`). No installation or vehicle write is authorized by these screenshots.
