#!/usr/bin/env python3
"""Render primary/secondary HOME composites using the local MU1440 shader equation."""
from pathlib import Path
import json,html
from mcf_inventory import parse,write_png
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
TINTS={'white':(255,255,255),'blue':(0,102,255),'ice':(119,231,244),'red':(242,0,40)}
def compose(primary,secondary,tint):
 if len(primary)!=len(secondary):raise ValueError('layer geometry mismatch')
 out=bytearray(len(primary))
 for i in range(0,len(primary),4):
  pa=primary[i+3]/255;sa=secondary[i+3]/255;a=sa+pa*(1-sa)
  for c in range(3):
   fg=secondary[i+c]*tint[c]/255
   out[i+c]=round((fg*sa+primary[i+c]*pa*(1-sa))/a) if a else 0
  out[i+3]=round(a*255)
 return bytes(out)
def main():
 _,old=parse(OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf');_,new=parse(OUT/'neoui_build/NeoUI_v3_HOME_SETUP_skin3.mcf');old={r['id']:r for r in old};new={r['id']:r for r in new};dest=OUT/'neoui_previews/home_setup';dest.mkdir(parents=True,exist_ok=True)
 for key,tint in TINTS.items():
  for state,data in [('before',old),('after',new)]:write_png(dest/f'home_{key}_{state}.png',407,300,compose(data[2127]['raw'],data[2126]['raw'],tint),'RGBA')
 # Single-layer white scrollbar mask is tinted at runtime and is unchanged.
 for key,tint in TINTS.items():
  r=old[83];raw=bytearray(r['raw'])
  for i in range(0,len(raw),4):
   for c in range(3):raw[i+c]=round(raw[i+c]*tint[c]/255)
  write_png(dest/f'thumb_{key}.png',25,51,bytes(raw),'RGBA')
 rows=['Bildschirm','Zeit und Datum','Sprache/Language','Zusätzliche Tastatursprachen','Einheiten','Datenübertragung mobile Geräte']
 lists=[]
 for state in ['before','after']:
  items=''.join(f"<div class='row'>{html.escape(t)}<img class='divider' src='home_setup/19_{state}.png'></div>" for t in rows)
  lists.append(f"<div><h3>{'v1 source' if state=='before' else 'v3 candidate'}</h3><div class='list'><h3>Einstellungen System</h3>{items}<div class='track'><img src='home_setup/84_{state}.png'><img class='thumb' src='home_setup/thumb_blue.png'></div></div></div>")
 cards=[]
 scenarios=json.loads((OUT/'neoui_reports/scenario_resource_matrix.json').read_text())['scenarios']
 for s in scenarios:
  name=s['photo'];scope='HOME tile layers 2127 / 2126 updated; live text and connection behavior remain HMI-rendered' if name[:2] in ['01','02','07'] else 'Separator 19 and track 84 updated; thumb tint/state behavior retained' if name.startswith('06') else 'Existing 16-variant media palette stage retained' if name.startswith('08') else 'No new screen-specific artwork; MENU/controlbar protected records match v1 exactly'
  cards.append(f"<article><h3>{html.escape(name)}</h3><img class='photo' src='../../reference_screens/{name}'><p>{scope}</p></article>")
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NeoUI v3 HOME and SETUP</title><style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;padding:28px;background:#0d131c;color:#eff6fa;font:15px/1.5 Segoe UI,sans-serif}h1{color:#77e7f4}h2{margin-top:32px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:20px}article,.box{background:#17202c;border:1px solid #344454;border-radius:12px;padding:16px;overflow:hidden}.panel{position:relative;max-width:407px}.panel img{display:block;width:100%}.sample{position:absolute;inset:0;display:grid;place-content:center;text-align:center;color:#eff6fa;font-size:20px;text-shadow:0 1px 2px #000;padding:15px;white-space:pre-line}.photo{width:100%;height:310px;object-fit:contain;background:#080d13}select,button{font:inherit;padding:9px;background:#243b4a;color:#eff6fa;border:1px solid #77e7f4;margin:5px}p{max-width:1150px}.list{position:relative;background:#0d131c;padding:14px 42px 10px 16px}.list h3{margin:0 0 14px}.row{font-size:20px;position:relative;padding:12px 0 14px}.divider{position:absolute;bottom:0;left:0;width:100%;height:3px}.track{position:absolute;right:10px;top:60px;bottom:20px;width:25px}.track>img:first-child{width:25px;height:100%;position:absolute}.track .thumb{width:25px;height:110px;position:absolute;top:0}.note{border-left:3px solid #77e7f4;padding:10px 16px;background:#17202c}.native img{image-rendering:auto}a{color:#77e7f4}</style><h1>NeoUI v3 · HOME / SETUP candidate</h1><p>Four new real MCF graphics: HOME base and ambient overlay, list divider, scrollbar track. The previous sixteen media variants are retained. The 208 protected MENU/controlbar records are byte-identical to v1.</p><div class="note">These are source-based component previews, not captured head-unit screens. HOME composition follows the extracted MU1440 shader. SETUP text/layout is a legibility sample copied from the reference photo; it does not change HMI text, layout or hit targets. Ice is a sample tint, not a newly enabled vehicle ambient option.</div><h2>HOME · two layers, day and night</h2><p>Both day/night entries use the same layer records on this firmware. Changing the tint below illustrates runtime ambient multiplication. Sample content tests contrast only.</p><label>Sample tint <select id="tint" onchange="update()"><option value="blue">Mapped display blue (#0066FF)</option><option value="white">White</option><option value="ice">Ice sample</option><option value="red">Red sample</option></select></label><label>Content <select id="content" onchange="update()"><option value="Telefon nicht verbunden">Disconnected</option><option value="Favoriten">Connected, empty favorites</option><option value="damaged.-&#10;LIVE now">Media playing</option></select></label><div class="grid"><div class="box"><h3>v1 source</h3><div class="panel"><img id="homeBefore" src="home_setup/home_blue_before.png"><div class="sample">Telefon nicht verbunden</div></div></div><div class="box"><h3>v3 candidate</h3><div class="panel"><img id="homeAfter" src="home_setup/home_blue_after.png"><div class="sample">Telefon nicht verbunden</div></div></div></div><h2>SETUP · divider and track</h2><p>Thumb record 83 and the runtime state/color bindings stay byte-identical. The tint control demonstrates that the white thumb mask retains color selection; the candidate does not force cyan into it.</p><div class="grid">'''+''.join(lists)+'''</div><h2>Four exact asset changes</h2><div class="grid">'''
 for ident in [2127,2126,19,84]:page+=f"<article class='native'><h3>MCF {ident}</h3><p>v1 source / v3 candidate · same dimensions and alpha</p><img style='max-width:47%' src='home_setup/{ident}_before.png'> <img style='max-width:47%' src='home_setup/{ident}_after.png'></article>"
 page+="</div><h2>Eight scenario references and scope</h2><div class='grid'>"+''.join(cards)+"</div><p><a href='VERIFIED_V3_PREVIEW.html'>Previous media-state comparison</a></p><script>function update(){const t=document.getElementById('tint').value;document.getElementById('homeBefore').src='home_setup/home_'+t+'_before.png';document.getElementById('homeAfter').src='home_setup/home_'+t+'_after.png';document.querySelectorAll('.thumb').forEach(e=>e.src='home_setup/thumb_'+t+'.png');document.querySelectorAll('.sample').forEach(e=>e.textContent=document.getElementById('content').value);}</script></html>"
 (OUT/'neoui_previews/HOME_SETUP_V3_PREVIEW.html').write_text(page,encoding='utf-8');print('wrote shader-composed HOME tint previews and SETUP/eight-scenario gallery')
if __name__=='__main__':main()
