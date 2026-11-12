# Mapped PNG revision pipeline validation

Validated offline on 2026-11-12. No production PNG master, firmware input, historical candidate, resource catalog or installation policy was changed by the builds/tests. All 54 production master file hashes still match the pre-existing catalog. No SD, vehicle, network or Git publishing operations were performed for this pipeline work.

Normal entry point: `build.ps1` (default `Build`) -> `tools/build_visual_revision.py`. Historical v1 rehearsal and report-reconciliation writers are excluded from this path. Python's standard library is sufficient; this workspace's interpreter is configured in ignored `neoui_workspace/python-path.txt`.

The published unchanged build is `neoui_build/visual_builds/v3-d75db3c48548e5189b8d/`. Its candidate is 32,797,052 bytes, SHA-1 `2787801d63ae74483b3d005a673a10e1c723e5b1`, SHA-256 `9d7b6601a7d1614b453a4b8428efeeff2daef9684471ff33f54fecb56d1cee09`, identical to the preserved v2-based candidate. `latest.json` is an offline convenience pointer, not an installed-baseline decision.

Validation covers:

- Exact v1/v2/design references, the locked 54-record design whitelist and mapped source hashes.
- 2,345 records with correct order, count, bounds, full decompression, dimensions and file/TOC/record CRCs.
- All 94 v2 changes retained exactly, including 74 MENU/foundation changes; all 106 protected MENU/foundation records and every unmapped record match v2.
- Current master format/geometry/alpha and transparent RGB bytes preserved; decoded encoded pixels equal the master snapshot.
- Explicit names required for changes against the previous offline revision; unknown names and extra/missing PNGs are rejected.
- Two successive non-safety icon edits retain the prior edit and alter only the next declared ID; v2 records remain exact.
- Deterministic repeated packing and immutable output collision refusal.
- Independent reconstruction of the exact predecessor from saved prefix/offsets, original changed records and unchanged candidate records. This uses placement at predecessor offsets, not the packing routine.
- Wrong geometry, corrupted PNG, alpha/transparent-RGB changes, source/catalog tampering, unmapped predecessor modifications, damaged recovery records and output collisions fail. Failed builds do not advance the latest pointer.
- PNG metadata-only saves preserve the MCF exactly. The existing decoder fixtures also cover all five standard PNG filters, invalid dimensions and CRC rejection.
- The gallery includes 54 resources and 162 checked image references (v2/previous/new); all build file checksums were checked. Native icon preview was opened successfully.
- Windows published folders inherit the workspace ACL. A private Windows temporary-directory ACL issue was corrected; publication and deterministic/no-edit validation were rerun after the fix.

Evidence: all 10 offline integration tests in `test_visual_revision.py` passed through `build.ps1 -Mode Test`. The no-edit/deterministic/publication test passed again after the staging change, the reference/catalog guard test passed after final metadata gate changes, and a real final build passed all internal validation. Five PNG filter fixtures passed. The PowerShell wrapper's multi-name Audit path and explicit initial predecessor worked; Release mode correctly refused before writing.

Each revision provides its own `manifest.json`, `changeset.json`, `masters/` snapshot, `recovery/`, `restored_predecessor.mcf`, `SHA256SUMS` and standalone `previews/index.html`. All of these generated artifacts live beneath the ignored visual-build directory. Preview panels are decoded firmware resources on checkerboards; they are not full-screen reconstruction or vehicle rendering evidence. Runtime tint and shared consumers remain relevant to visual review.

The completed deliverable is a repeatable PC graphics build pipeline. Installation remains separately blocked; the pipeline contains no vehicle writer and does not claim car-ready or fail-safe installation. `release-policy.json` is unchanged, and every manifest keeps `release_ready=false` and `installed_baseline_activated=false`.
