#!/usr/bin/env python3
import csv,json,hashlib,html
from pathlib import Path
from mcf_inventory import parse
OUT=Path(__file__).resolve().parents[1];R=OUT/'neoui_reports';P=OUT/'neoui_previews'
def readcsv(n):
 with (R/n).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def main():
 if (R/'VERIFIED_MEDIA_BT_BUILD.json').exists():
  from update_media_bt_reports import main as current_reports
  current_reports();return
 if (R/'VERIFIED_VEHICLE_NAV_BUILD.json').exists():
  from update_vehicle_nav_reports import main as current_reports
  current_reports();return
 if (R/'VERIFIED_HOME_SETUP_BUILD.json').exists():
  from update_home_setup_reports import main as current_reports
  current_reports();return
 mapping=json.loads((R/'resolved_images_res.json').read_text())['rows'];_,source=parse(OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf');src={r['id']:r for r in source};build=json.loads((R/'VERIFIED_MEDIA_BUILD.json').read_text());changed={r['mcf_id'] for r in build['entries']};inverse={}
 for m in mapping:
  if m['mcf_id']>0:inverse.setdefault(m['mcf_id'],[]).append(m)
 with (R/'RESOLVED_RESOURCE_MAP.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(['logical_id','symbol','bank','mcf_id','width','height','flags','inset_index','implemented'])
  for m in mapping:
   image=src.get(m['mcf_id'],{});w.writerow([m['logical_id'],m['symbol'],m['bank'],m['mcf_id'],image.get('width',''),image.get('height',''),m['flags'],m['inset_index'],m['mcf_id'] in changed])
 old=json.loads((R/'resource_map.json').read_text())['entries'];entries=[]
 for oldrow in old:
  logical=oldrow.get('symbol_id',oldrow.get('logical_id'));refs=[x for x in mapping if x['logical_id']==logical]
  entries.append(dict(symbol_id=logical,symbol=oldrow['symbol'],screen=oldrow['screen'],resolved=[dict(bank=m['bank'],mcf_id=m['mcf_id'],dimensions=[src[m['mcf_id']]['width'],src[m['mcf_id']]['height']] if m['mcf_id'] in src else None,flags=m['flags'],inset_index=m['inset_index']) for m in refs],id_translation='verified on exact local images.res and MCF',screen_confidence='B: media glyph visual match' if any(m['mcf_id'] in changed for m in refs) else 'C: exact runtime screen/state still to be confirmed',implemented=any(m['mcf_id'] in changed for m in refs),scope='skin3 resource tree cloned from stock skin1; installed metadata requires future read-only precheck'))
 (R/'resource_map.json').write_text(json.dumps(dict(schema_version=3,status='real ID translation resolved; 16 media records implemented offline',entries=entries),indent=2),encoding='utf-8')
 for filename in ['skin1_vs_mib_skin3_diff.csv','mib_skin3_vs_neoui_v1_diff.csv','neoui_v1_vs_v2_pilot_diff.csv']:
  report=['# Resolved record audit: '+filename,'','Actual MCF IDs resolved through images.res; same-number CommonClasses names are not used.','', '| MCF record | Geometry | Logical aliases (bank) |','|---|---|---|']
  for d in readcsv(filename):
   i=int(d['id']);aliases='; '.join(f"{m['logical_id']} (bank {m['bank']}): {m['symbol']}" for m in inverse.get(i,[]));report.append(f"| {i} | {d['width']}x{d['height']} | {aliases or 'no main-table alias'} |")
  (R/(Path(filename).stem+'_RESOLVED.md')).write_text('\n'.join(report),encoding='utf-8')
 (R/'V2_SCOPE_AUDIT.md').write_text('''# Corrected v2 scope audit

The prior same-number symbolic-ID interpretation was invalid. The real images.res table now resolves the old v2 records. Its MENU tile and shared bar descriptions are supported by those actual aliases; the earlier claim that these records represented status/nav direction symbols is withdrawn. See neoui_v1_vs_v2_pilot_diff_RESOLVED.md for all 94 records and actual aliases. The v2 pilot remains uninstalled and is not the v3 baseline.
''',encoding='utf-8')
 (R/'IMAGE_ID_TRANSLATION.md').write_text('''# images.res translation resolved

The exact skin1 P4526 file has a 20-byte header, then four tagged signed-int32 arrays. Each array has tag 5 and a count. Counts: 320, 34572, 2732, 25037; their bounds consume the file exactly. The first array is 80 groups of four inset values. The second is two banks of 2881 logical entries, with six ints per entry. Each entry has two identical triples (MCF ID, inset index, flags) on this input. The last array's maximum index plus one independently agrees with 2881 logical entries.

All active MCF references exist; inset indices are bounded. Bank meaning and the final arrays' runtime dispatch semantics remain unverified. No metadata/selector array is changed. Symbol 797 (pause C02) resolves to record 1658 (120x120 pause glyph); symbols 193/194 resolve to HOME panel records 2127/2126 (407x300). Main MENU/media backgrounds alias 2331/2330. This explains the former same-number mismatch.

images_res.py reproduces the mapping. RESOLVED_RESOURCE_MAP.csv includes every bank/ID/geometry, while resolved_images_res.json retains insets and flags. Installed skin3 metadata has not been freshly read from the car; local M.I.B. script lineage says it copies skin1 metadata. A future release must verify that metadata hash during a read-only device precheck.

MCF checksums are also resolved: file header CRC covers bytes 0-15; TOC header CRC covers its first 24 bytes; TOC data CRC covers image count plus directory. Each IMG header CRC covers its first 24 bytes, and final CRC covers width/height/mode plus compressed/padded data. All stock/MIB/v1/v2 inputs pass.
''',encoding='utf-8')
 (R/'RESOURCE_MAPPING.md').write_text('''# NeoUI v3 mapping and implementation

Numeric translation is resolved for all 2881 logical images in two resource banks. Every active MCF reference is valid. RESOLVED_RESOURCE_MAP.csv and resource_map.json replace prior numeric hypotheses. Screen usage still needs review by component; a correct resource lookup does not prove every photo uses that code path.

The offline v3 candidate implements 16 play/pause/skip state graphics, mapped from logical IDs 797-812 to MCF records 1635-1640, 1642-1646 and 1654-1658. Source glyphs visually match photo 08. Media Control stage aliases share some records and receive the same palette change. Shapes, dimensions, alpha and source state contrast are preserved. Source state codes are retained without guessing their renderer labels.

HOME tile backgrounds are now mapped to 2126/2127, list separator to 19, scrollbar foreground/background to 83/84, and MENU/shared bars have resolved aliases. These have no v3 replacements yet: HOME and scrollbar colorization/runtime bank selection remain unverified; the MENU foundation is retained. Vehicle illustration and navigation map assets remain unchanged.

No-op rebuild and local restore exercises return the exact v1 bytes. Every candidate record CRC passes and exactly 16 records differ. The candidate is a skin3 fallback, not a separate selectable skin. It is not vehicle-tested and has no installer.
''',encoding='utf-8')
 scenario=json.loads((R/'scenario_resource_matrix.json').read_text())['scenarios'];cards=[]
 for q in scenario:
  logicals=q.get('candidate_symbol_ids',[]);actual=sorted({m['mcf_id'] for m in mapping if m['logical_id'] in logicals and m['mcf_id']>0});q['resolved_mcf_records']=actual;q['mapping_confidence']='ID translation verified; exact runtime view binding varies by component';q['v3_scope']='16 transport glyph variants updated in the media player' if q['photo'].startswith('08') else 'No screen-specific v3 change in this candidate'
  cards.append(f"<article><h2>{html.escape(q['photo'])}</h2><img class='photo' src='../../reference_screens/{q['photo']}'><p>{q['v3_scope']}</p><details><summary>Resolved source candidates</summary><p>{', '.join(map(str,actual))}</p><p>Translation is verified; this does not establish every candidate's exact runtime view binding.</p></details></article>")
 (R/'scenario_resource_matrix.json').write_text(json.dumps(dict(status='real IDs resolved; only verified media transport changes implemented',scenarios=scenario),indent=2),encoding='utf-8')
 pairs=[]
 for a in build['entries']:
  pairs.append(f"<article><h3>MCF {a['mcf_id']} / logical {a['logical_id']}</h3><p>{html.escape(a['symbol'])}</p><div class='pair'><figure><img src='verified_media/{a['mcf_id']}_before.png'><figcaption>Installed-v1 source</figcaption></figure><figure><img src='verified_media/{a['mcf_id']}_after.png'><figcaption>NeoUI v3 candidate</figcaption></figure></div></article>")
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NeoUI v3 verified media preview</title><style>body{background:#0d131c;color:#eff6fa;font:15px/1.5 Segoe UI,sans-serif;margin:0;padding:28px}h1{color:#77e7f4}h2{font-size:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px}article{background:#17202c;border:1px solid #344454;padding:18px;border-radius:12px;overflow-wrap:anywhere}.photo{width:100%;height:300px;object-fit:contain;background:#070c12}.pair{display:flex;justify-content:center;gap:20px;background:#0b1017}.pair img{width:120px;height:120px}figure{margin:10px}figcaption{font-size:12px;color:#b8cad8}button{padding:12px;background:#243b4a;color:#eff6fa;border:1px solid #77e7f4;cursor:pointer}section{margin-top:28px}</style><h1>NeoUI v3 / Verified media palette</h1><p>Actual firmware graphics with exact ID translation and byte-verified v1 restoration. This is a local asset review, not a head-unit runtime screenshot. Sixteen transport variants are changed; the other photographed scenarios retain their current graphics in this candidate.</p><button onclick="document.querySelectorAll('.pair').forEach(e=>e.style.background=e.style.background==='rgb(216, 226, 234)'?'#0b1017':'#d8e2ea')">Toggle comparison background</button><section><h2>Source/candidate at native 120x120 pixels</h2><div class='grid'>'''+''.join(pairs)+"</div></section><section><h2>Eight vehicle scenarios and candidate impact</h2><div class='grid'>"+''.join(cards)+"</div></section></html>"
 (P/'VERIFIED_V3_PREVIEW.html').write_text(page,encoding='utf-8')
 print('refreshed real-ID maps, corrected audits and 8-scenario/16-variant preview')
if __name__=='__main__':main()
