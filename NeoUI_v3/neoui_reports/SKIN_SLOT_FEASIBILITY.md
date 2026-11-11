# Independent skin slot feasibility (NeoUI v3)

**Status: UNKNOWN at firmware-selector level; NO safe, verified additional slot for this release.**

## Evidence inspected

- Target original firmware extraction is `MHI2_ER_SKG13_P4526 / MU1440`; its `eso/hmi/lsd/Resources` tree contains `skin0`, `skin1`, and `skin2`. The original extraction has no `skin3` directory. This is a file inventory result, not a claim about installed on-car state.
- The local M.I.B. 3.6.0 `apps/ImageMod` source has an explicit `SKG13_P4526` branch. It creates backups and patches `skin0/images.mcf`, then copies `Alphabets`, `Fonts`, `i18n`, `view`, `ambienceColorMap.res`, `images.res`, `viewhandler.zip`, and `images.mcf` from `skin1` into `skin3`; it applies `mod/images/SKG13_P4526/skin3/images.mcf.delta`, checks SHA-1 `0a322d581cb320c60bc6be87e2817fcdf20aa2f2`, adds `skin3/info.txt`, and reports the modification installed. The only SKG13 directories in the M.I.B. archive are `skin0` and `skin3`. Its `-b` restore branch restores the skin0 backup and removes skin3.
- The same M.I.B. program contains `skin5` and `skin6` logic only under a separate `VWG13` branch. That is evidence of a different platform path, not evidence those slots are supported by SKG13.
- The official [M.I.B. SKG13 Image MOD page](https://github.com/Mr-MIBonk/M.I.B._More-Incredible-Bash/wiki/SKG13---Skoda-MIB2.5-Image-MOD) says the mod is installed from GEM and a new skin is selected from Engineering Menu. It does not identify the accepted index range or document arbitrary additional slots.
- The extracted stock `skin1` and `skin2` each have `images.mcf`, `images.res`, `info.txt`, `viewhandler.zip`, and `ambienceColorMap.res`, plus subdirectories. M.I.B. builds skin3 as a full copy of skin1 plus a delta; a lone `skin4/images.mcf` would therefore omit dependencies and is not justified.

## Decision

Do not create or package `skin4`; do not patch the selector, viewhandler, root filesystem, or NVRAM. Available evidence proves the known M.I.B. SKG13 selectable mod is skin3, but does not prove the selector rejects other indices. Because accepted selector values and exact runtime discovery behavior are unverified, claiming a firmware-level NO would overstate the evidence. For engineering/release purposes, independent NeoUI beside the current M.I.B. skin is **not established and must be treated as unavailable**.

Current on-car NeoUI v1 is reported as skin3 SHA-1 `641c34e42ed5843c1795bf860fd4cb7bbb913fdb`; that is a reported state, not a fresh read from the head unit. A skin3 fallback would replace that current M.I.B.-derived option. No write to a vehicle or SD card is part of this investigation.

## Dependencies and impact

- `skin0/images.mcf` delta: shared/global impact is possible; actual screens affected must be mapped. Keep unchanged.
- `skin3`: full resource tree cloned from skin1, then M.I.B. delta; NeoUI v1/v2 pilot assets target this slot.
- Selector accepted IDs, whether it scans directories or enumerates them, runtime skin switch semantics, and shared resources used by screens remain unverified.
- View code is compiled in per-skin `viewhandler.zip`; no binary changes are authorized.

## Next proof needed for a YES

Read-only evidence from this exact unit/firmware must establish the selector's accepted IDs and runtime loading requirements, including a complete slot tree and any global dependencies. Then prove switching and restoration without altering selector binaries, compiled view code, shared assets, or NVRAM. Until that is available, continue offline resource mapping and preview work only.


## Additional live-state evidence limits

The local M.I.B. 3.6.0 script documents construction of `skin3`, but the firmware-side selector's accepted index range is not present in the verified evidence. The upstream M.I.B. toolbox says its generic Skin screen supports six skin folders across its supported-unit set; that does not identify which IDs are supported on this exact SKG13/P4526 unit. Therefore a new independent slot remains UNKNOWN, not a proven firmware NO. The release decision remains: do not add `skin4` or alter selector code.
