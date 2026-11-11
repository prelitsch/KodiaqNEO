#!/usr/bin/env python3
from pathlib import Path
import json,csv,hashlib
from mcf_inventory import parse
from images_res import resolve
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent;R=OUT/'neoui_reports'
def main():
 b=json.loads((R/'VERIFIED_HOME_SETUP_BUILD.json').read_text());changed={x['mcf_id'] for x in b['entries']};proof=json.loads((R/'RUNTIME_TINT_EVIDENCE.json').read_text())
 with (R/'viewhandler_image_symbols.csv').open(encoding='utf-8') as f:symbols={int(x['id']):x['symbol'] for x in csv.DictReader(f)}
 refs=resolve(ROOT/'app50_extract/lba0/eso/hmi/lsd/Resources/skin1/images.res',symbols);_,rs=parse(OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf');dims={r['id']:[r['width'],r['height']] for r in rs}
 old=json.loads((R/'resource_map.json').read_text())['entries'];groups={r['symbol_id']:r.get('screen','shared') for r in old}
 for r in refs:
  if r['mcf_id'] in changed and r['logical_id'] not in groups:groups[r['logical_id']]='MEDIEN / Media Control'
 entries=[]
 for logical,screen in groups.items():
  rr=[r for r in refs if r['logical_id']==logical]
  entries.append(dict(symbol_id=logical,symbol=symbols.get(logical,''),screen=screen,resolved=[dict(layer=r['layer'],mcf_id=r['mcf_id'],day_night_same=r['day_night_same'],dimensions=dims.get(r['mcf_id']),scale_mode=r['scale_mode'],inset_index=r['inset_index']) for r in rr],id_translation='verified from exact images.res + MU1440 runtime',screen_confidence='B: reviewed source/name/shape/runtime path' if any(r['mcf_id'] in changed for r in rr) else 'C: resource link verified; per-view usage requires review',implemented=any(r['mcf_id'] in changed for r in rr),scope='skin3; shared aliases enumerated; no skin0 changes'))
 (R/'resource_map.json').write_text(json.dumps(dict(schema_version=4,status='primary/secondary and day/night semantics resolved; 20 records implemented offline',entries=entries),indent=2),encoding='utf-8')
 with (R/'RESOLVED_RESOURCE_MAP.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['logical_id','symbol','layer','day_night_same','mcf_id','dimensions','scale_mode','inset_index','implemented'])
  for r in refs:w.writerow([r['logical_id'],r['symbol'],r['layer'],r['day_night_same'],r['mcf_id'],dims.get(r['mcf_id']),r['scale_mode'],r['inset_index'],r['mcf_id'] in changed])
 for p in R.glob('*_RESOLVED.md'):
  s=p.read_text(encoding='utf-8').replace('bank 0','primary').replace('bank 1','secondary').replace('aliases (bank)','aliases (layer)');p.write_text(s,encoding='utf-8')
 runtime='''# Runtime HOME / SETUP tint trace

Source: the user's existing MU1440-lsd.jxe backup, SHA-256 a55d9cfb69c5756f8202b7f7aa4079d4d5b637ae4c2fd0fe723f1d6816cbeea8. The firmware startup script loads /ifs/lsd.jxe. Inspection is static; no firmware class is executed or modified. RUNTIME_TINT_EVIDENCE.json records exact class/method offsets, code hashes, reference sites and two original shader hashes. The targeted J9 reader validates UTF-8/self-relative pointers and declared method counts; it is not a general decompiler.

## Resource selection

SkinImagePoolImpl.createImage(logical) creates two ScaleImage entries at logical*2 and logical*2+1. Image's constructor stores these as dayImage and nightImage. Image.getCurrentImage selects day for mode 0 and night for mode 1. The six ints per logical image are two triples for those day/night ScaleImages.

The second half of scaleImageData is a SECOND BITMAP layer, not a separate day/night bank. createScaleImage reads the primary bitmap ID at scaleIndex*3 and, when supportsSecondScaleImageBitmap is true, the second bitmap ID at arrayLength/2 + scaleIndex*3. Insets and scale mode are preserved. Both day/night triples match on the exact P4526 input, including HOME and SETUP assets. Earlier bank 0/1 labels in reports refer to primary/secondary layers and should not be read as day/night modes.

## Ambient selection and renderer

SkinInformationServiceImpl.readAmbienceColorMap loads the selected skin's ambienceColorMap.res and vehicle-matched color mappings. setIntLightAmbientLightColor updates mapped display colors and notifies receivers. ViewCompositorImpl.SkinInformationHandler checks isAmbientColorEnabled and feeds getAmbientColor (with opaque alpha) into Color.setGlobalDynamicColor, or null when ambient color is disabled. Color.getCurrentColor selects day/night data; its dynamic path calls Color.mix, which multiplies channel values and divides by 255. Current skin mode notifications call the day/night mode setter.

AbstractWidgetUI.updateScaleImageDrawable loads primary into image slot 0 and optional secondary into slot 1. StaticImageUI supplies the current widget color. The shipped ImageComposition.glslf samples the primary, multiplies secondary RGB by vertex/widget color, then alpha-composites secondary over primary. Default image blending is 0, whose shader selector chooses Modulate. For opaque primary P and secondary S with alpha a, the default component composition is (S.rgb * tint.rgb) * a + P.rgb * (1-a). Global alpha and other effects remain runtime controlled.

The local map's BAP blue 0x006EFE maps to display blue 0x0066FF. Preview colors are explicit sample widget tints; a particular view may also multiply its own day/night color. The offline preview does not assert a captured head-unit pixel match or alter the ambient palette.

## Verified graphics scope

HOME symbols 193/194 share primary 2127 and secondary 2126, both 407x300. The source primary is opaque black; the secondary is a grayscale mask with alpha 15..204. The candidate sets primary to graphite #0D131C and scales visible secondary luminance to 45%, preserving every alpha byte. This retains OEM tint response with a restrained overlay.

SETUP/shared list symbol 111 maps only to divider 19 (88x3); its visible luminance is reduced to 45%. Symbol 274 maps only to scrollbar track 84 (25x51), changed to graphite slate #303A46. Scrollbar.updateScrollbarImage selects an image and color by state, assigning WHITE if no state color is present. Foreground/thumb 83 (symbol 275) remains byte-identical because its white mask receives runtime color. The candidate does not force cyan into that binding or restyle focus/disabled states.

The generic list divider/track changes can affect other skin3 list screens. All 208 MAIN_MENU, controlbar and shared foundation protected records match input v1 byte-for-byte. No skin0, viewhandler, selector, ambience map, navigation map, coordinates or touch target is changed. HOME component usage has resource-name/geometry/photo evidence (B), while live unit behavior remains untested.
'''
 (R/'HOME_SETUP_RUNTIME_TINT.md').write_text(runtime,encoding='utf-8')
 report=f'''# NeoUI v3 HOME / SETUP offline candidate

This partial candidate adds four HOME/SETUP graphics to the verified sixteen media variants. It is a replacement of existing skin3, not an additional selectable skin.

- New records: 2127 (HOME graphite base), 2126 (HOME ambient overlay), 19 (list divider), 84 (scrollbar track).
- Existing media variants: 16 retained exactly from the prior media stage.
- Alpha and dimensions: unchanged for every graphic. All aliases and source/new record, pixel and PNG hashes are in VERIFIED_HOME_SETUP_BUILD.json.
- Preserved: all {len(b['menu_and_controlbar_protected_records'])} protected MENU/controlbar/shared foundation records; runtime-colored scrollbar thumb 83; compiled code, resource metadata and ambient palette.
- Input v1 SHA-1: {b['source_sha1']}.
- Candidate SHA-1: {b['candidate_sha1']}.
- Candidate SHA-256: {b['candidate_sha256']}.

Validated: all file/TOC/image CRCs; exact 20-record change set; unchanged ID order/count/geometry/alpha; fixed baseline and metadata hashes; MENU protection; independent recovery archive restoration to the complete original v1 SHA-256 {b['source_sha256']}.

Preview: neoui_previews/HOME_SETUP_V3_PREVIEW.html. HOME uses the original shader's primary/secondary composition with explicit tint samples. SETUP is a component/legibility composition, with wording copied from photo 06. All eight original scenarios are included with scope notes. These are not runtime head-unit captures, and other screen components are not redesigned by this stage.

This is PC-validated and not vehicle-tested. No installer or SD operations are prepared. Installed skin3 metadata and live renderer behavior still require the later user-authorized precheck/review gates. A script/record restore on PC is not a recovery guarantee if the car UI cannot boot.
'''
 (R/'HOME_SETUP_BUILD_REPORT.md').write_text(report,encoding='utf-8')
 (R/'CURRENT_STATE.md').write_text('''# NeoUI v3 current state

Current candidate: neoui_build/NeoUI_v3_HOME_SETUP_skin3.mcf. It changes 20 records from exact packaged v1: 16 media transport states plus 4 HOME/SETUP assets. See HOME_SETUP_BUILD_REPORT.md and HOME_SETUP_RUNTIME_TINT.md.

Runtime primary/secondary bitmap layering, day/night selection and ambient color chain are traced statically from the existing exact-hash MU1440 lsd.jxe backup. Full-table numeric mapping is resolved. The source pairs use identical day/night image IDs. The earlier term bank means bitmap layer, not day/night bank.

HOME now has a graphite base and restrained grayscale ambient mask. Shared lists get a subdued divider and track. The scrollbar foreground retains runtime state tint. 208 protected M.I.B. MENU/controlbar/foundation records are byte-identical to v1. Independent restoration reproduces complete v1 bytes.

Preview: neoui_previews/HOME_SETUP_V3_PREVIEW.html. All eight source photos have scope notes; component previews are not captured head-unit output. Vehicle illustration, map/POI resources, full screen layouts and many remaining widget states are not yet redesigned.

Original firmware and backups remain read-only. All generated work stays in NeoUI_v3. No commits, vehicle writes, SD writes or installer. Independent selectable slot remains UNKNOWN on exact firmware; current candidate is a versioned skin3 fallback. Future release requires current-unit hashes and explicit install authorization.
''',encoding='utf-8')
 scenario_path=R/'scenario_resource_matrix.json'
 scenario=json.loads(scenario_path.read_text())
 scenario['status']='20-record candidate: 16 media + HOME base/overlay + SETUP divider/track; source-based component previews'
 for q in scenario['scenarios']:
  prefix=q['photo'][:2]
  q['v3_scope']='HOME tile layers 2126/2127 updated; dynamic phone/media content remains runtime-rendered' if prefix in ['01','02','07'] else 'List divider 19 and scrollbar track 84 updated; runtime thumb 83 unchanged' if prefix=='06' else '16 media transport variants implemented' if prefix=='08' else 'No new screen-specific graphic; MENU/controlbar foundation protected'
  q['mapping_confidence']='B for implemented components from source/name/shape/runtime evidence; remaining component bindings may be C'
 scenario_path.write_text(json.dumps(scenario,indent=2),encoding='utf-8')
 print('updated runtime trace, current map/state and 20-record build report')
if __name__=='__main__':main()
