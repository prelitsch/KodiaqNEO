#!/usr/bin/env python3
"""Keep current entry points from implying that a v1 design is a live-baseline release."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parents[1];R=OUT/'neoui_reports'
BANNER='> RELEASE HOLD: This is historical v1-based design validation, not an approved v2→v3 payload. Updated AGENTS.md reports v2 installer success; fresh baseline and post-reboot checks remain unconfirmed. See PIPELINE_RECONCILIATION.md.\n\n'
def apply():
 if not (R/'PIPELINE_RECONCILIATION.json').exists():return
 for filename in ['VERIFIED_MEDIA_BT_BUILD.json','VERIFIED_VEHICLE_NAV_BUILD.json','VERIFIED_HOME_SETUP_BUILD.json','VERIFIED_MEDIA_BUILD.json']:
  p=R/filename;d=json.loads(p.read_text());d.update(artifact_role='preserved v1-based offline design, not a confirmed installed-baseline release',release_ready=False,expected_current_installed_baseline=None,recovery_scope='exact v1 design reference only; not v2 rollback');p.write_text(json.dumps(d,indent=2),encoding='utf-8')
 (R/'CURRENT_STATE.md').write_text('''# NeoUI v3 current state — baseline reconciliation

RELEASE BLOCKED. The updated AGENTS.md records a successful v2 installer replacement. Older root handoffs claiming "v2 not installed" are stale. Console success does not establish post-reboot behavior or a fresh current installed hash. Current installed baseline and selected skin remain UNKNOWN; release-policy.json deliberately keeps them null.

Preserved design artifact: neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf, SHA256 86519e2621e63c3183d317fe6a0badca96030e38048db8962903707a74e2fd86. It is a v1-based OFFLINE DESIGN REFERENCE with54 changed resources; all existing graphics/previews and research are retained. It is not suitable for direct replacement over assumed v2.

Exact comparison: v2 changes94 records from v1; design changes54; overlap0. Writing the old v1-based container over v2 would revert94 v2 changes, including74 MENU/foundation records, and change148 records total. A future confirmed-v2 build must retain the94 predecessor changes and apply only explicitly reviewed design resources. No rebased deployment payload has been generated.

The existing design validation remains valid relative to its labeled v1 reference: all54 mapped resources, MCF CRCs, fixed dimensions/alpha,106 MENU/foundation records,288 non-controlbar navigation records and exact v1 design restoration. These are not guarantees about the current on-car v2 MENU or recovery. V1 recovery archives are not v2 rollback archives.

New read-only collector: tools/baseline_precheck.sh. Prepared offline only. It reads firmware/MU, target size/hash/attributes, skin3 metadata, raw mounts and QNX free blocks, and checks target stability. Output goes only to stdout/stderr: no SD probe/log/backup, remount, app write, installer or marker arming. Selected skin has no verified automatic getter, SHA256 may be absent, and raw mounts/post-reboot evidence require review. PC review never activates a baseline or authorizes installation.

Maintainability: resource-map.json provides54 stable semantic names; resources/masters holds ignored editable source-derived PNGs; changesets/v3-design-54.json preserves declarative mappings. build.ps1 runs off-car audit/tests or deterministic design/icon rehearsals, never installation. The single named non-safety icon rehearsal changes only MCF988 and independently restores the preserved design. New rehearsal containers are content-addressed and immutable, separate from existing candidates.

Preview: neoui_previews/MEDIA_BT_V3_PREVIEW.html and earlier linked galleries, unchanged source-component comparisons. No new artwork or vehicle tests this reconciliation. See PIPELINE_RECONCILIATION.md, BASELINE_PRECHECK.md, RELEASE_RULES.md and VISUAL_EDIT_GUIDE.md.

All generated work remains in NeoUI_v3. No network, SD or vehicle writes, no commits. Selectable independent skin remains UNKNOWN. Future release requires fresh exact predecessor evidence, installed metadata, permissions/mount review, backups of distinct states, predecessor-based build/diff/restore tests, storage calculation, explicit review/authorization and complete tested installer logic. Mandatory precheck may run immediately before install in the same explicitly armed invocation; a separate SD swap is not required by policy.
''',encoding='utf-8')
 for name in ['MEDIA_BT_BUILD_REPORT.md','RESOURCE_MAPPING.md']:
  p=R/name;s=p.read_text(encoding='utf-8')
  if not s.startswith(BANNER):p.write_text(BANNER+s,encoding='utf-8')
 (R/'V2_SCOPE_AUDIT.md').write_text('''# Corrected v2 scope and installation status

Real images.res mapping resolves the94 v2 records. The prior same-number symbolic-ID interpretation was invalid; the resolved MENU/shared-bar interpretation stands. Updated AGENTS.md now records console-reported v2 installation success, superseding the old "uninstalled" claim. Post-reboot rendering and fresh installed hash are unconfirmed.

Cached v2 payload SHA1 28e26e2603497571663a93b303e930a2d4787f50, SHA256 cfe0aabb1e67e2ea06a07ea365fc24f69e3901e0508a02e87ab8525b92dac103;32,861,680 bytes;2,345 CRC-validated records. It is a local reference, not a fresh device backup.

The54 v3 design records are disjoint from the94 v2 records. Old v1-based v3 replacement would revert all94, including74 protected MENU/foundation records. Preserve the existing graphics as design sources, confirm the actual predecessor read-only, then build a reviewed predecessor-preserving release. See PIPELINE_RECONCILIATION.md.
''',encoding='utf-8')
 p=R/'resource_map.json';m=json.loads(p.read_text());m['release_status']='HOLD: catalog describes preserved v1 design; installed baseline unknown; no v2 deployment approval';p.write_text(json.dumps(m,indent=2),encoding='utf-8')
 p=R/'scenario_resource_matrix.json';m=json.loads(p.read_text());m['artifact_role']='preserved v1-based design previews; not a current-installed-baseline release';p.write_text(json.dumps(m,indent=2),encoding='utf-8')
 print('PASS: current reports retain explicit unknown-live-baseline release hold')
if __name__=='__main__':apply()
