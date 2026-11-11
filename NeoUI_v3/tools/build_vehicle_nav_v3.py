#!/usr/bin/env python3
"""Extend the verified HOME/SETUP candidate using compiled vehicle/nav bindings."""
from pathlib import Path
import hashlib,json,zipfile
from mcf_inventory import parse,write_png
from build_verified_v3 import rebuild,record_with_pixels,EXPECTED,sha
from trace_vehicle_nav import trace,RES,VIEWS
OUT=Path(__file__).resolve().parents[1]
ICONS=set(range(984,994))|{1000,1014,1015,1024}
ARROWS=set(range(1647,1653))
TILES={1707,1714,1716,1717,1719}
TARGETS=ICONS|ARROWS|TILES|{2221}
def transform(ident,row):
 raw=bytearray(row['raw']);changed=0;preserved_chromatic=0
 for k in range(0,len(raw),4):
  if not raw[k+3]:continue
  r,g,b=raw[k:k+3];delta=max(r,g,b)-min(r,g,b)
  if ident in ICONS:
   # Keep yellow media notes, green POI category detail and every colored pixel.
   if delta>12:preserved_chromatic+=1;continue
   v=round((r+g+b)/3);rgb=tuple(round(v*c/255) for c in (220,236,245))
  elif ident in ARROWS or ident in TILES:
   if g>r*1.20 and g>b*1.25:
    # OEM green selection/press graphics -> ice; retain luminance gradients.
    rgb=tuple(round(g*c/255) for c in (119,231,244))
   elif delta<=20:
    v=round((r+g+b)/3);rgb=tuple(round(v*c/255) for c in (220,236,245))
   else:rgb=(r,g,b)
  elif ident==2221:
   # Decorative trip-computer road only, never navigation road rendering.
   rgb=(round(r*.80),round(g*.84),round(b*.90))
  else:raise ValueError('unknown resource')
  if rgb!=(r,g,b):changed+=1
  raw[k:k+3]=bytes(rgb)
 if not changed:raise ValueError('empty transformation')
 return bytes(raw),dict(changed_visible_rgb_pixels=changed,chromatic_icon_pixels_preserved=preserved_chromatic)
def main():
 evidence,mapping=trace()
 if evidence['viewhandler_sha256']!='6f7cad69cdc7077c4aefc747931124e9acdbfb8e3f22295d28ec9304b8452256':raise ValueError('compiled views changed')
 source=OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf';data,rows=parse(source);original={r['id']:r for r in rows}
 if hashlib.sha1(data).hexdigest()!=EXPECTED:raise ValueError('v1 source changed')
 previous=OUT/'neoui_build/NeoUI_v3_HOME_SETUP_skin3.mcf';prior,priorrows=parse(previous)
 if sha(prior)!='e4f850f5cd71e09083ffa3e7650bad03e02e82a2fadc40a19fd2f5347a434be7':raise ValueError('HOME/SETUP candidate changed')
 report=json.loads((OUT/'neoui_reports/VERIFIED_HOME_SETUP_BUILD.json').read_text());entries=list(report['entries'])
 replacements={r['id']:r['record'] for r in priorrows if r['record']!=original[r['id']]['record']}
 protected={m['mcf_id'] for m in mapping if 'MAIN_MENU' in m['symbol'] or m['logical_id'] in [9,13,17,18,19,46,47,48,49,50]}-{-1}
 # Every target must have a constant-bound reference in a reviewed compiled view.
 bound={m['mcf_id'] for b in evidence['bindings'] for m in b['resources']}
 if not TARGETS<=bound or TARGETS&protected:raise ValueError('missing binding or protected alias')
 p=OUT/'neoui_previews/vehicle_nav';p.mkdir(parents=True,exist_ok=True)
 for ident in sorted(TARGETS):
  r=original[ident];dims=(r['width'],r['height']);expected=(78,52) if ident in ICONS else (120,120) if ident in ARROWS else (182,92) if ident in TILES else (1280,170)
  if dims!=expected or r['mode']!='0x1104':raise ValueError('unexpected geometry/format')
  aliases=[m for m in mapping if m['mcf_id']==ident]
  raw,stats=transform(ident,r)
  if raw[3::4]!=r['raw'][3::4]:raise ValueError('alpha changed')
  if any(raw[k:k+4]!=r['raw'][k:k+4] for k in range(0,len(raw),4) if r['raw'][k+3]==0):raise ValueError('transparent RGB changed')
  new=record_with_pixels(r,raw);replacements[ident]=new
  before=p/f'{ident}_before.png';after=p/f'{ident}_after.png';write_png(before,*dims,r['raw'],'RGBA');write_png(after,*dims,raw,'RGBA')
  refs=[dict(module=b['module'],method=b['method'],pc=b['pc'],lookup=b['lookup'],argument=b['argument'],state_logical_ids=b['state_logical_ids']) for b in evidence['bindings'] if any(m['mcf_id']==ident for m in b['resources'])]
  entries.append(dict(mcf_id=ident,logical_ids=sorted({m['logical_id'] for m in aliases}),screen='FAHRZEUG trip road' if ident==2221 else 'FAHRZEUG / shared item paging' if ident in ARROWS else 'NAVIGATION / FAHRZEUG / shared action controls',dimensions=list(dims),alpha='byte-identical',confidence='A: exact compiled-view constant -> image array/direct image -> images.res -> MCF; static, not car-tested',aliases=aliases,compiled_bindings=refs,original_record_sha256=sha(r['record']),new_record_sha256=sha(new),original_pixel_sha256=sha(r['raw']),new_pixel_sha256=sha(raw),before=str(before.relative_to(OUT)),after=str(after.relative_to(OUT)),before_png_sha256=sha(before.read_bytes()),after_png_sha256=sha(after.read_bytes()),**stats))
 candidate=rebuild(data,rows,replacements);dest=OUT/'neoui_build/NeoUI_v3_VEHICLE_NAV_skin3.mcf';dest.write_bytes(candidate);_,newrows=parse(dest);changed={r['id'] for r in newrows if r['record']!=original[r['id']]['record']}
 if changed!=set(replacements) or len(changed)!=20+len(TARGETS):raise ValueError('unexpected changes')
 if not all(r['record']==original[r['id']]['record'] for r in newrows if r['id'] in protected):raise ValueError('MENU/foundation changed')
 with zipfile.ZipFile(OUT/'neoui_build/NeoUI_v3_VEHICLE_NAV_recovery_records.zip','w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('original_prefix.bin',data[:52+len(rows)*16+4]);z.writestr('metadata.json',json.dumps(dict(source_sha256=sha(data),source_bytes=len(data))))
  for i in sorted(changed):z.writestr(f'{i}.bin',original[i]['record'])
 result=dict(status='OFFLINE PARTIAL CANDIDATE; not vehicle-tested; no installer',firmware='MHI2_ER_SKG13_P4526',mu='MU1440',strategy='existing skin3 fallback; selectable new slot UNKNOWN',source_sha1=EXPECTED,source_sha256=sha(data),previous_stage_sha256=sha(prior),images_res_sha256=sha(RES.read_bytes()),viewhandler_sha256=sha(VIEWS.read_bytes()),candidate_sha1=hashlib.sha1(candidate).hexdigest(),candidate_sha256=sha(candidate),record_count=len(rows),changed_record_count=len(changed),new_vehicle_nav_records=sorted(TARGETS),protected_menu_foundation_records=sorted(protected),menu_foundation_exact=True,shared_full_actionbar_strips_exact=True,all_other_records_exact=True,all_crcs_verified=True,shared_scope='Changed action controls can appear in other skin3 application bars; generic 120px paging arrows can appear outside FAHRZEUG. No cross-skin metadata or skin0 modification.',unchanged='Shared vehicle illustrations, eco/fuel/safety graphics, 86px paging arrows, map engine/roads/POIs/routes, viewhandler, images.res, ambience maps and full blue action-bar strip.',entries=entries)
 (OUT/'neoui_reports/VEHICLE_NAV_RESOURCE_EVIDENCE.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8');(OUT/'neoui_reports/VERIFIED_VEHICLE_NAV_BUILD.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print('PASS:',len(TARGETS),'new records;',len(changed),'total;',len(protected),'MENU/foundation records exact; all CRCs verified;',result['candidate_sha256'])
if __name__=='__main__':main()
