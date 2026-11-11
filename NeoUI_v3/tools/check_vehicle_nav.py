#!/usr/bin/env python3
"""Independent pixel/record, local preview-link and script checks; no vehicle I/O."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,shutil,subprocess
from mcf_inventory import parse
from trace_vehicle_nav import trace
OUT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
class Page(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.script='';self.in_script=False
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='script':self.in_script=True
  for key in ['src','href']:
   if key in d:self.links.append(d[key])
 def handle_endtag(self,tag):
  if tag=='script':self.in_script=False
 def handle_data(self,s):
  if self.in_script:self.script+=s
def main():
 report=OUT/'neoui_reports/VERIFIED_VEHICLE_NAV_BUILD.json';b=json.loads(report.read_text());_,old=parse(OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf');data,new=parse(OUT/'neoui_build/NeoUI_v3_VEHICLE_NAV_skin3.mcf');old={r['id']:r for r in old};new={r['id']:r for r in new}
 assert sha(data)==b['candidate_sha256'] and old.keys()==new.keys()
 changed={i for i in old if old[i]['record']!=new[i]['record']};assert changed=={e['mcf_id'] for e in b['entries']} and len(changed)==46
 assert len(b['entries'])==46 and len(b['new_vehicle_nav_records'])==26
 warm=0
 for e in b['entries']:
  i=e['mcf_id'];r=old[i];n=new[i];assert (r['width'],r['height'],r['mode'])==(n['width'],n['height'],n['mode'])
  assert r['raw'][3::4]==n['raw'][3::4] and sha(n['record'])==e['new_record_sha256'] and sha(r['record'])==e['original_record_sha256']
  for k in range(0,len(r['raw']),4):
   if not r['raw'][k+3]:assert r['raw'][k:k+4]==n['raw'][k:k+4]
  if i in set(range(984,994))|{1000,1014,1015,1024}:
   for k in range(0,len(r['raw']),4):
    rgb=r['raw'][k:k+3]
    if r['raw'][k+3] and max(rgb)-min(rgb)>12:assert rgb==n['raw'][k:k+3];warm+=1
 for i in b['protected_menu_foundation_records']:assert old[i]['record']==new[i]['record']
 evidence,mapping=trace();nav={m['mcf_id'] for m in mapping if 'NAVI' in m['symbol'] and 'CONTROLBAR' not in m['symbol'] and m['mcf_id']>=0};assert not(nav&changed)
 assert b.get('independent_restore_exact') and b['independent_restore_sha256']==b['source_sha256']
 htmlpath=OUT/'neoui_previews/VEHICLE_NAV_V3_PREVIEW.html';p=Page();p.feed(htmlpath.read_text(encoding='utf-8'))
 for link in p.links:
  assert '://' not in link and (htmlpath.parent/link).is_file(),link
 for slot in range(18):
  for state in ['before','after']:assert (htmlpath.parent/f'vehicle_nav/nav_slot{slot}_{state}.png').is_file()
 script=OUT/'neoui_workspace/refs/vehicle_nav_preview.js';script.write_text(p.script,encoding='utf-8');node=shutil.which('node')
 if not node:raise RuntimeError('node required for local preview script syntax check')
 subprocess.run([node,'--check',str(script)],check=True,capture_output=True)
 # Exercise all state-selector mappings in a minimal DOM without a browser/network.
 harness="""const elements={slot:{value:'2'},before:{},after:{},ids:{replaceChildren(...rows){this.rows=rows;}}};global.document={getElementById(id){return elements[id];},createElement(tag){return {tag,children:[],append(v){this.children.push(v);}};}};
"""+p.script+"""\nfor(let s=0;s<18;s++){elements.slot.value=String(s);update();if(elements.ids.rows.length!==7||elements.after.src!=='vehicle_nav/nav_slot'+s+'_after.png')throw Error('state update failed');for(const r of elements.ids.rows)if(r.children.length!==3)throw Error('missing id cells');}console.log('PASS all 18 selector states');"""
 test=script.with_name('vehicle_nav_dom_check.js');test.write_text(harness,encoding='utf-8');run=subprocess.run([node,str(test)],check=True,capture_output=True,text=True)
 checks=dict(status='PASS offline',changed_records=46,new_records=26,all_crcs=True,unchanged_records_exact=True,dimensions_alpha_transparent_rgb_exact=True,chromatic_icon_pixels_preserved=warm,protected_menu_foundation_records=len(b['protected_menu_foundation_records']),navigation_non_controlbar_records_exact=len(nav),independent_restore_exact=True,local_links_checked=len(p.links),state_slot_images_checked=36,script_syntax=True,state_selector_18_slots=True,native_png_inspection='normal and pressed navigation, paging arrows, button states and decorative road inspected',browser_visual_qa='not performed; local-file URL policy blocks browser access; no bypass attempted',vehicle_tested=False)
 (OUT/'neoui_reports/VEHICLE_NAV_PREVIEW_CHECKS.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(run.stdout.strip());print('PASS:',len(changed),'records;',warm,'chromatic icon pixels preserved;',len(nav),'non-controlbar navigation records exact;',len(p.links),'local links valid')
if __name__=='__main__':main()
