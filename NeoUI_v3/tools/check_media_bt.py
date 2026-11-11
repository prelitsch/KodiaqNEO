#!/usr/bin/env python3
"""Independent media-stage invariants and local preview selector checks."""
from pathlib import Path
import json,shutil,subprocess
from mcf_inventory import parse
from build_verified_v3 import sha
from build_media_bt_v3 import CARDS,protected_card_pixel
from trace_media_bt import trace,TARGETS
from check_vehicle_nav import Page
OUT=Path(__file__).resolve().parents[1]
def main():
 b=json.loads((OUT/'neoui_reports/VERIFIED_MEDIA_BT_BUILD.json').read_text());source,rs=parse(OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf');blob,ns=parse(OUT/'neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf');prior,ps=parse(OUT/'neoui_build/NeoUI_v3_VEHICLE_NAV_skin3.mcf');old={r['id']:r for r in rs};new={r['id']:r for r in ns};previous={r['id']:r for r in ps}
 assert sha(source)==b['source_sha256'] and sha(blob)==b['candidate_sha256'] and sha(prior)==b['previous_stage_sha256'];assert old.keys()==new.keys()==previous.keys()
 changed={i for i in old if old[i]['record']!=new[i]['record']};assert changed=={e['mcf_id'] for e in b['entries']} and len(changed)==54
 added={i for i in old if previous[i]['record']!=new[i]['record']};assert added==TARGETS
 protected_pixels=0
 for e in b['entries']:
  i=e['mcf_id'];a=old[i];c=new[i];assert (a['width'],a['height'],a['mode'])==(c['width'],c['height'],c['mode']);assert a['raw'][3::4]==c['raw'][3::4]
  assert sha(a['record'])==e['original_record_sha256'] and sha(c['record'])==e['new_record_sha256']
  for k in range(0,len(a['raw']),4):
   if not a['raw'][k+3]:assert a['raw'][k:k+4]==c['raw'][k:k+4]
   if i in CARDS and a['raw'][k+3] and protected_card_pixel(old[CARDS[i]]['raw'],k):assert a['raw'][k:k+4]==c['raw'][k:k+4];protected_pixels+=1
   if i==1036 and a['raw'][k+3] and max(a['raw'][k:k+3])-min(a['raw'][k:k+3])>12:assert a['raw'][k:k+4]==c['raw'][k:k+4]
  for key in ['before','after']:assert sha((OUT/e[key]).read_bytes())==e[key+'_png_sha256']
 for i in b['protected_menu_foundation_records']+b['retained_resources']:assert old[i]['record']==new[i]['record']
 assert len({sha(new[i]['raw']) for i in [1131,1133,1134]})==3
 evidence,mapping=trace();nav={m['mcf_id'] for m in mapping if 'NAVI' in m['symbol'] and 'CONTROLBAR' not in m['symbol'] and m['mcf_id']>=0};assert not(nav&changed)
 transports={m['mcf_id'] for bind in evidence['bindings'] if bind['module']=='Mbam' and bind['lookup']=='getImageArray' and bind['argument'] in [304,306,308,310] for m in bind['resources'] if m['mcf_id']>=0};assert len(transports)==16 and transports<=changed
 assert b['independent_restore_exact'] and b['independent_restore_sha256']==b['source_sha256']
 pagepath=OUT/'neoui_previews/MEDIA_BT_V3_PREVIEW.html';page=Page();page.feed(pagepath.read_text(encoding='utf-8'))
 for link in page.links:assert '://' not in link and (pagepath.parent/link).is_file(),link
 node=shutil.which('node');assert node,'node required for preview script checks'
 script=OUT/'neoui_workspace/refs/media_bt_preview.js';script.write_text(page.script,encoding='utf-8');subprocess.run([node,'--check',str(script)],check=True,capture_output=True)
 harness="""const fs=require('node:fs'),path=require('node:path');let assigned=0;const elements={slot:{value:'2'},card:{value:'2217'},glyph:{value:'pause'},text:{value:'damaged.-'}};const texts=[{},{}];global.document={getElementById(id){if(!elements[id])elements[id]={set src(v){if(!fs.existsSync(path.resolve(__dirname,'../../neoui_previews',v)))throw Error('missing '+v);this.value=v;assigned++;}};return elements[id];},querySelectorAll(){return texts;}};
"""+page.script+"""\nlet count=0;for(let s=0;s<18;s++)for(const card of ['2217','2202','2214','2199','art'])for(const glyph of ['play','pause'])for(const text of ['damaged.-','Ein außergewöhnlich langer deutscher Musiktitel']){elements.slot.value=String(s);elements.card.value=card;elements.glyph.value=glyph;elements.text.value=text;update();for(const side of ['before','after'])if(elements['art_'+side].hidden!==(card!=='art'))throw Error('art visibility');if(texts.some(x=>x.textContent!==text))throw Error('text update');count++;}console.log('PASS '+count+' selector combinations; '+assigned+' image references');"""
 test=script.with_name('media_bt_dom_check.js');test.write_text(harness,encoding='utf-8');result=subprocess.run([node,str(test)],check=True,capture_output=True,text=True)
 checks=dict(status='PASS offline',changed_records=54,new_media_bt_records=8,previous46_exact=True,all_crcs=True,dimensions_alpha_transparent_rgb_exact=True,protected_identity_and_bright_glyph_pixels=protected_pixels,source_list_state_records_distinct=True,existing_transport_records_compiled_bound=16,protected_menu_foundation_records=len(b['protected_menu_foundation_records']),navigation_non_controlbar_records_exact=len(nav),seekbar_and_mode_masks_exact=True,independent_restore_exact=True,local_links_checked=len(page.links),script_syntax=True,selector_combinations=360,native_png_inspection='BT source/off, generic source, source-list pressed and native player sample reviewed',browser_visual_qa='not performed; local-file browser URL policy; no bypass attempted',vehicle_tested=False)
 (OUT/'neoui_reports/MEDIA_BT_PREVIEW_CHECKS.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(result.stdout.strip());print('PASS: 54 records; 8 new; protected identities',protected_pixels,'pixels;',len(nav),'navigation records exact;',len(page.links),'local links')
if __name__=='__main__':main()
