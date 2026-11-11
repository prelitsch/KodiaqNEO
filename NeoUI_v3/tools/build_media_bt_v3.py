#!/usr/bin/env python3
"""Eight verified media assets added to the exact vehicle/navigation stage."""
from pathlib import Path
import hashlib,json,zipfile
from mcf_inventory import parse,write_png
from build_verified_v3 import rebuild,record_with_pixels,EXPECTED,sha
from trace_media_bt import trace,TARGETS
OUT=Path(__file__).resolve().parents[1]
CARDS={2217:2217,2202:2217,2214:2214,2199:2214}
BUTTONS={1131,1133,1134}
def protected_card_pixel(on,k):
 rgb=on[k:k+3]
 # Data-derived mask: brand colors, bright glyph/BT label and bright frame stay exact.
 return max(rgb)-min(rgb)>24 or max(rgb)>145
def transform(ident,row,source):
 raw=bytearray(row['raw']);n=0;protected=0
 for k in range(0,len(raw),4):
  if not raw[k+3]:continue
  r,g,b=raw[k:k+3]
  if ident in CARDS:
   if protected_card_pixel(source[CARDS[ident]]['raw'],k):protected+=1;continue
   rgb=(round(r*.54),round(g*.60),round(b*.70))
  elif ident in BUTTONS:
   if g>r*1.20 and g>b*1.25:rgb=tuple(round(g*c/255) for c in (119,231,244))
   elif max(r,g,b)-min(r,g,b)<=20:
    v=round((r+g+b)/3);rgb=tuple(round(v*c/255) for c in (220,236,245))
   else:rgb=(r,g,b)
  elif ident==1036:
   if max(r,g,b)-min(r,g,b)>12:protected+=1;continue
   v=round((r+g+b)/3);rgb=tuple(round(v*c/255) for c in (220,236,245))
  else:raise ValueError('unmapped target')
  n+=rgb!=(r,g,b);raw[k:k+3]=bytes(rgb)
 if not n:raise ValueError('no visible change')
 return bytes(raw),dict(changed_visible_rgb_pixels=n,protected_identity_or_chromatic_pixels=protected)
def main():
 evidence,mapping=trace();data,rows=parse(OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf');source={r['id']:r for r in rows}
 if hashlib.sha1(data).hexdigest()!=EXPECTED:raise ValueError('source mismatch')
 prior,prs=parse(OUT/'neoui_build/NeoUI_v3_VEHICLE_NAV_skin3.mcf')
 if sha(prior)!='a4d5cddb77ce92583e091b9957f32e6f5b2f40bf95421e223de95cf247e11cf2':raise ValueError('prior stage mismatch')
 previous=json.loads((OUT/'neoui_reports/VERIFIED_VEHICLE_NAV_BUILD.json').read_text());entries=list(previous['entries']);replacements={r['id']:r['record'] for r in prs if r['record']!=source[r['id']]['record']}
 protected=set(previous['protected_menu_foundation_records']);nav={m['mcf_id'] for m in mapping if 'NAVI' in m['symbol'] and 'CONTROLBAR' not in m['symbol'] and m['mcf_id']>=0}
 if TARGETS&(protected|nav|set(replacements)):raise ValueError('protected/previous resource collision')
 preview=OUT/'neoui_previews/media_bt';preview.mkdir(parents=True,exist_ok=True)
 for ident in sorted(TARGETS):
  r=source[ident];dims=(r['width'],r['height']);expected=(450,450) if ident in CARDS else (50,94) if ident in BUTTONS else (78,52)
  if dims!=expected or r['mode']!='0x1104':raise ValueError('geometry/format mismatch')
  aliases=[m for m in mapping if m['mcf_id']==ident];bindings=[b for b in evidence['bindings'] if any(m['mcf_id']==ident for m in b['resources'])]
  if not bindings:raise ValueError('no compiled binding')
  raw,stats=transform(ident,r,source)
  if raw[3::4]!=r['raw'][3::4]:raise ValueError('alpha changed')
  record=record_with_pixels(r,raw);replacements[ident]=record
  before=preview/f'{ident}_before.png';after=preview/f'{ident}_after.png';write_png(before,*dims,r['raw'],'RGBA');write_png(after,*dims,raw,'RGBA')
  refs=[{k:b[k] for k in ['module','method','method_rom_offset','code_sha256','pc','lookup','argument','state_logical_ids','assigned_field']} for b in bindings]
  entries.append(dict(mcf_id=ident,logical_ids=sorted({m['logical_id'] for m in aliases}),screen='MEDIEN / BT and shared media fallback or artwork border' if ident in CARDS else 'Shared media source-list state' if ident in BUTTONS else 'MEDIEN controlbar / playlist / playlist setup',dimensions=list(dims),alpha='byte-identical',confidence='A: exact static compiled view -> array -> logical image -> MCF; runtime cover/script references reviewed; not car-tested',aliases=aliases,compiled_bindings=refs,original_record_sha256=sha(r['record']),new_record_sha256=sha(record),original_pixel_sha256=sha(r['raw']),new_pixel_sha256=sha(raw),before=str(before.relative_to(OUT)),after=str(after.relative_to(OUT)),before_png_sha256=sha(before.read_bytes()),after_png_sha256=sha(after.read_bytes()),**stats))
 candidate=rebuild(data,rows,replacements);dest=OUT/'neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf';dest.write_bytes(candidate);_,new=parse(dest)
 changed={r['id'] for r in new if r['record']!=source[r['id']]['record']}
 if changed!=set(replacements) or len(changed)!=54:raise ValueError('unexpected diff')
 if any(r['record']!=source[r['id']]['record'] for r in new if r['id'] in protected|nav):raise ValueError('protected resource changed')
 if any(r['record']!=next(x['record'] for x in prs if x['id']==r['id']) for r in new if r['id'] not in TARGETS):raise ValueError('prior stage changed')
 if any(source[i]['raw'][3::4]!=next(r['raw'] for r in new if r['id']==i)[3::4] for i in changed):raise ValueError('alpha changed')
 with zipfile.ZipFile(OUT/'neoui_build/NeoUI_v3_MEDIA_BT_recovery_records.zip','w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('original_prefix.bin',data[:52+len(rows)*16+4]);z.writestr('metadata.json',json.dumps(dict(source_sha256=sha(data),source_bytes=len(data))))
  for i in sorted(changed):z.writestr(f'{i}.bin',source[i]['record'])
 report=dict(status='OFFLINE PARTIAL CANDIDATE; not vehicle-tested; no installer',firmware='MHI2_ER_SKG13_P4526',mu='MU1440',strategy='versioned skin3 fallback; independent new slot UNKNOWN',source_sha1=EXPECTED,source_sha256=sha(data),previous_stage_sha256=sha(prior),candidate_sha1=hashlib.sha1(candidate).hexdigest(),candidate_sha256=sha(candidate),record_count=len(rows),changed_record_count=len(changed),new_media_bt_records=sorted(TARGETS),protected_menu_foundation_records=sorted(protected),menu_foundation_exact=True,navigation_non_controlbar_records_exact=len(nav),all_crcs_verified=True,all_previous_stage_records_retained=True,state_color_arrays_and_seekbar_exact=True,shared_scope='Generic source2214 is the dynamic artwork border and fallback across media views. TYPE0901131/1133/1134 can affect other lists. Playlist1036 aliases playlist/setup. Skin3 only; no other skin tree changes.',retained_resources=[1889,39,61,917,956,955,954,953,952,1034],entries=entries)
 (OUT/'neoui_reports/MEDIA_BT_RESOURCE_EVIDENCE.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8');(OUT/'neoui_reports/VERIFIED_MEDIA_BT_BUILD.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PASS: 8 new / 54 total; prior46 retained; MENU/navigation protected; CRCs pass;',report['candidate_sha256'])
if __name__=='__main__':main()
