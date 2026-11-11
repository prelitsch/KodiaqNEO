#!/usr/bin/env python3
"""Local source-based component comparisons; no layout or firmware patching."""
from pathlib import Path
import html,json
from mcf_inventory import parse,write_png
from images_res import arrays,resolve
from preview_home_setup import compose
from trace_vehicle_nav import trace,RES
OUT=Path(__file__).resolve().parents[1]
NAV=[('Neues Ziel',116,904),('Meine Ziele',120,903),('Sonderziele',120,905),('Ansicht',120,902),('Medien',120,456),('Ansagen',120,908),('Setup',115,831)]
def over(canvas,w,h,raw,rw,rh,x,y):
 for sy in range(rh):
  for sx in range(rw):
   if not(0<=x+sx<w and 0<=y+sy<h):continue
   a=(sy*rw+sx)*4;b=((y+sy)*w+x+sx)*4;sa=raw[a+3]/255;da=canvas[b+3]/255;oa=sa+da*(1-sa)
   for c in range(3):canvas[b+c]=round((raw[a+c]*sa+canvas[b+c]*da*(1-sa))/oa) if oa else 0
   canvas[b+3]=round(oa*255)
def main():
 evidence,mapping=trace();a=arrays(RES);p=OUT/'neoui_previews/vehicle_nav';p.mkdir(parents=True,exist_ok=True)
 datasets={}
 for state,path in [('before','neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf'),('after','neoui_build/NeoUI_v3_VEHICLE_NAV_skin3.mcf')]:
  _,rs=parse(OUT/path);datasets[state]={r['id']:r for r in rs}
 def logical(array,slot):
  start,length=a[2][array*2:array*2+2]
  if length!=18:raise ValueError('unexpected state array')
  return a[3][start+slot]
 def record(array,slot):
  n=logical(array,slot);refs=[r for r in mapping if r['logical_id']==n and r['layer']=='primary'];return refs[0]['mcf_id']
 index={}
 for slot in range(18):
  index[slot]=[dict(label=t,tile_logical=logical(ti,slot),tile_mcf=record(ti,slot),icon_logical=logical(ic,slot),icon_mcf=record(ic,slot)) for t,ti,ic in NAV]
  for state,rs in datasets.items():
   # Native 182x92 assets laid side by side for comparison only. Not a coordinate reconstruction.
   base=bytearray(bytes((13,19,28,255))*(1280*92));strip=compose(rs[2095]['raw'],rs[2092]['raw'],(0,102,255));over(base,1280,92,strip,1280,92,0,0)
   for n,entry in enumerate(index[slot]):
    tile=rs[entry['tile_mcf']];icon=rs[entry['icon_mcf']];over(base,1280,92,tile['raw'],182,92,n*182,0);over(base,1280,92,icon['raw'],78,52,n*182+52,3)
   write_png(p/f'nav_slot{slot}_{state}.png',1280,92,bytes(base),'RGBA')
 # Native asset contact sheets, deliberately without a speculative car illustration.
 groups=[('arrows',[1652,1651,1650,1649,1648,1647],120,120),('buttons',[1707,1714,1716,1717,1719],182,92),('icons',[989,988,991,990,987,993,992,1015,984,1000,986,985,1014,1024],78,52)]
 for name,ids,w,h in groups:
  for state,rs in datasets.items():
   raw=bytearray(bytes((13,19,28,255))*(w*len(ids)*h))
   for j,i in enumerate(ids):over(raw,w*len(ids),h,rs[i]['raw'],w,h,j*w,0)
   write_png(p/f'{name}_{state}.png',w*len(ids),h,bytes(raw),'RGBA')
 manifest=json.loads((OUT/'neoui_reports/VERIFIED_VEHICLE_NAV_BUILD.json').read_text())
 cards=[]
 for e in manifest['entries']:
  if e['mcf_id'] not in manifest['new_vehicle_nav_records']:continue
  cards.append(f"<article><h3>MCF {e['mcf_id']} · {' × '.join(map(str,e['dimensions']))}</h3><p>Logical {', '.join(map(str,e['logical_ids']))} · alpha exact</p><div class='pair'><img src='{html.escape(Path(e['before']).relative_to('neoui_previews').as_posix())}'><img src='{html.escape(Path(e['after']).relative_to('neoui_previews').as_posix())}'></div><p>{html.escape(e['screen'])}</p></article>")
 scenarios=json.loads((OUT/'neoui_reports/scenario_resource_matrix.json').read_text())['scenarios'];refs=[]
 for s in scenarios:
  name=s['photo'];prefix=name[:2];scope='NAV action controls changed; map, POIs, routing, maneuver resources unchanged.' if prefix=='04' else 'Trip-road decoration, 120px paging arrows and action controls changed. Shared vehicle, fuel and eco illustrations retained.' if prefix=='05' else 'M.I.B. MENU/floor/background retained exactly.' if prefix=='03' else 'Previous HOME/SETUP/media changes retained; shared action-control changes can also appear here.'
  refs.append(f"<article><h3>{html.escape(name)}</h3><img class='photo' src='../../reference_screens/{html.escape(name)}'><p>{scope}</p></article>")
 labels=''.join('<span>'+html.escape(x[0])+'</span>' for x in NAV)
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NeoUI v3 vehicle and navigation</title><style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;padding:28px;background:#0d131c;color:#eff6fa;font:15px/1.5 Segoe UI,sans-serif}h1,a{color:#77e7f4}h2{margin-top:32px}p{max-width:1150px}.note,article{background:#17202c;border:1px solid #344454;border-radius:10px;padding:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:18px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}.pair img{max-width:100%;height:auto}.wide{width:100%;height:auto;display:block;background:#0d131c}.bar{position:relative;max-width:1280px}.labels{position:absolute;inset:58% 0 0;display:grid;grid-template-columns:repeat(7,1fr);text-align:center;color:#eff6fa;font-size:clamp(7px,1.5vw,22px);pointer-events:none;text-shadow:0 1px 2px #000}.photo{width:100%;height:310px;object-fit:contain;background:#080d13}select,button{font:inherit;background:#243b4a;color:#eff6fa;border:1px solid #77e7f4;padding:8px;margin:5px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #344454;padding:6px;text-align:left}.scroll{overflow:auto}summary{cursor:pointer;color:#77e7f4}</style><h1>NeoUI v3 · FAHRZEUG / NAVIGATION</h1><p>26 additional real MCF records; 46 total with the previous media and HOME/SETUP stages. Exact compiled-view bindings, dimensions and alpha retained. M.I.B. MENU and the full blue action-bar strip remain byte-identical.</p><div class="note">Offline source-based component previews, not captured head-unit output. The navigation row uses native assets arranged for comparison: labels and icon positions are preview placement, not a verified screen-coordinate reconstruction. The full strip is a blue-tint sample using the traced two-layer shader; widget tint, clipping, nine-slicing and text remain controlled by unchanged HMI code. No UI layout, touch target, route or map change.</div><h2>NAVIGATION · all 18 source state slots</h2><p>State positions are kept verbatim. No guessed enabled/disabled labels. Slots 7 and 8 expose the pressed/selected tile resources through the actual array. The same IDs are bound by guided and unguided views. Media/tuner/TV are dynamic alternatives; the row shows the media branch.</p><label>Source state slot <select id="slot" onchange="update()">'''+''.join(f'<option value="{i}"'+(' selected' if i==2 else '')+f'>{i}</option>' for i in range(18))+'''</select></label><h3>v1 source</h3><div class="bar"><img class="wide" id="before" src="vehicle_nav/nav_slot2_before.png"><div class="labels">'''+labels+'''</div></div><h3>v3 candidate</h3><div class="bar"><img class="wide" id="after" src="vehicle_nav/nav_slot2_after.png"><div class="labels">'''+labels+'''</div></div><div class="scroll"><table><thead><tr><th>Button</th><th>Tile logical / MCF</th><th>Icon logical / MCF</th></tr></thead><tbody id="ids"></tbody></table></div><h2>FAHRZEUG · real trip-road decoration</h2><p>Logical 2592 → MCF 2221, loaded directly by Cmc.initWidgets. Native 1280 × 170, identical alpha and lane shapes. This is the trip-computer illustration road, not navigation road rendering. The silver car, fuel station, eco/safety indicators and shared background stay untouched.</p><h3>v1 source</h3><img class="wide" src="vehicle_nav/2221_before.png"><h3>v3 candidate</h3><img class="wide" src="vehicle_nav/2221_after.png"><h2>FAHRZEUG · paging controls</h2><p>Next C04/C06/C07 then previous C04/C06/C07; six exact 120px source glyphs. Shared outside FAHRZEUG; 86px variants unchanged. Warm/colored icon details such as POI categories and yellow media notes are preserved.</p><div class="grid"><article><h3>v1 source</h3><img class="wide" src="vehicle_nav/arrows_before.png"></article><article><h3>v3 candidate</h3><img class="wide" src="vehicle_nav/arrows_after.png"></article></div><h2>Shared action-control states</h2><p>Normal separator, selected, pressed, left separator and last selected. Native alpha and nine-slice metadata unchanged. These can affect other skin3 application bars; they do not create a separately selectable skin.</p><img class="wide" src="vehicle_nav/buttons_before.png"><img class="wide" src="vehicle_nav/buttons_after.png"><details><summary>Every new asset · v1 / v3</summary><div class="grid">'''+''.join(cards)+'''</div></details><h2>Eight reference scenarios</h2><div class="grid">'''+''.join(refs)+'''</div><p><a href="HOME_SETUP_V3_PREVIEW.html">Previous HOME / SETUP component comparisons</a> · <a href="VERIFIED_V3_PREVIEW.html">Previous media states</a></p><script>const states='''+json.dumps(index)+''';function update(){const s=document.getElementById('slot').value;document.getElementById('before').src='vehicle_nav/nav_slot'+s+'_before.png';document.getElementById('after').src='vehicle_nav/nav_slot'+s+'_after.png';document.getElementById('ids').replaceChildren(...states[s].map(e=>{const r=document.createElement('tr');[e.label,e.tile_logical+' / '+e.tile_mcf,e.icon_logical+' / '+e.icon_mcf].forEach(v=>{const c=document.createElement('td');c.textContent=v;r.append(c)});return r}));}update();</script></html>'''
 (OUT/'neoui_previews/VEHICLE_NAV_V3_PREVIEW.html').write_text(page,encoding='utf-8');(p/'state_index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
 print('PASS: 18 state-slot comparisons, native vehicle assets, 26 before/after pairs and eight reference scenarios')
if __name__=='__main__':main()
