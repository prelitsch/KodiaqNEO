#!/usr/bin/env python3
"""Offline HOME/SETUP stage: four verified records added to the media candidate."""
from pathlib import Path
import csv,json,hashlib,zipfile
from mcf_inventory import parse,write_png
from images_res import resolve
from build_verified_v3 import rebuild,record_with_pixels,EXPECTED,sha
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parents[1]
def transform(ident,r):
 raw=bytearray(r['raw'])
 for k in range(0,len(raw),4):
  if not raw[k+3]:continue
  if ident==2127:raw[k:k+3]=bytes((13,19,28))
  elif ident==2126:
   if not raw[k]==raw[k+1]==raw[k+2]:raise ValueError('HOME secondary no longer grayscale')
   v=round(raw[k]*0.45);raw[k:k+3]=bytes((v,v,v))
  elif ident==19:
   v=round(raw[k]*0.45);raw[k:k+3]=bytes((v,v,v))
  elif ident==84:raw[k:k+3]=bytes((48,58,70))
  else:raise ValueError('unknown change')
 return bytes(raw)
def main():
 src=OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf';data,rows=parse(src);original={r['id']:r for r in rows}
 if hashlib.sha1(data).hexdigest()!=EXPECTED:raise ValueError('baseline mismatch')
 media_data,media_rows=parse(OUT/'neoui_build/NeoUI_v3_verified_media_skin3.mcf');media=json.loads((OUT/'neoui_reports/VERIFIED_MEDIA_BUILD.json').read_text())
 if sha(media_data)!=media['candidate_sha256']:raise ValueError('media stage mismatch')
 with (OUT/'neoui_reports/viewhandler_image_symbols.csv').open(encoding='utf-8') as f:symbols={int(r['id']):r['symbol'] for r in csv.DictReader(f)}
 res=ROOT/'app50_extract/lba0/eso/hmi/lsd/Resources/skin1/images.res'
 if sha(res.read_bytes())!='8d491108101560fcb0f1eca3eff7b46c023a30b0b970c37ba2d4cd831d71e0d1':raise ValueError('images.res hash changed')
 evidence=json.loads((OUT/'neoui_reports/RUNTIME_TINT_EVIDENCE.json').read_text())
 if evidence['source_sha256']!='a55d9cfb69c5756f8202b7f7aa4079d4d5b637ae4c2fd0fe723f1d6816cbeea8':raise ValueError('runtime evidence mismatch')
 if sha(media_data)!='0387eb588d1f7add4853e6a66727a2b0d338a51ee235b8041db1a5c147ce8398':raise ValueError('media candidate hash changed')
 mapping=resolve(res,symbols)
 protected={m['mcf_id'] for m in mapping if 'MAIN_MENU' in m['symbol'] or 'CONTROLBAR' in m['symbol'] or m['logical_id'] in [13,17,18,19]}-{ -1 }
 targets={2127:({193,194},(407,300)),2126:({193,194},(407,300)),19:({111},(88,3)),84:({274},(25,51))}
 assert not set(targets)&protected
 replacements={r['id']:r['record'] for r in media_rows if r['record']!=original[r['id']]['record']};entries=list(media['entries']);preview=OUT/'neoui_previews/home_setup';preview.mkdir(parents=True,exist_ok=True)
 for ident,(expected_aliases,dims) in targets.items():
  r=original[ident];aliases=[m for m in mapping if m['mcf_id']==ident]
  if {m['logical_id'] for m in aliases}!=expected_aliases or (r['width'],r['height'])!=dims or r['mode']!='0x1104':raise ValueError('source mapping/geometry mismatch')
  raw=transform(ident,r);assert raw[3::4]==r['raw'][3::4];new=record_with_pixels(r,raw);replacements[ident]=new
  before=preview/f'{ident}_before.png';after=preview/f'{ident}_after.png';write_png(before,*dims,r['raw'],'RGBA');write_png(after,*dims,raw,'RGBA')
  entries.append(dict(mcf_id=ident,logical_ids=sorted(expected_aliases),screen='HOME' if ident>2000 else 'SETUP / shared skin3 lists',dimensions=list(dims),alpha='byte-identical',confidence='B: exact resource link, shape/photo match and runtime layer/color path traced',aliases=aliases,original_record_sha256=sha(r['record']),new_record_sha256=sha(new),original_pixel_sha256=sha(r['raw']),new_pixel_sha256=sha(raw),before=str(before.relative_to(OUT)),after=str(after.relative_to(OUT)),before_png_sha256=sha(before.read_bytes()),after_png_sha256=sha(after.read_bytes())))
 candidate=rebuild(data,rows,replacements);dest=OUT/'neoui_build/NeoUI_v3_HOME_SETUP_skin3.mcf';dest.write_bytes(candidate);_,newrows=parse(dest);changed={r['id'] for r in newrows if r['record']!=original[r['id']]['record']}
 assert changed==set(replacements) and len(changed)==20
 assert all(r['record']==original[r['id']]['record'] for r in newrows if r['id'] in protected)
 assert next(r for r in newrows if r['id']==83)['record']==original[83]['record']
 with zipfile.ZipFile(OUT/'neoui_build/NeoUI_v3_HOME_SETUP_recovery_records.zip','w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('original_prefix.bin',data[:52+len(rows)*16+4]);z.writestr('metadata.json',json.dumps(dict(source_sha256=sha(data),source_bytes=len(data))))
  for i in changed:z.writestr(f'{i}.bin',original[i]['record'])
 report=dict(status='OFFLINE PARTIAL CANDIDATE; not vehicle-tested; no installer',firmware='MHI2_ER_SKG13_P4526',mu='MU1440',strategy='existing skin3 fallback',source_sha1=EXPECTED,source_sha256=sha(data),images_res_sha256=sha(res.read_bytes()),candidate_sha1=hashlib.sha1(candidate).hexdigest(),candidate_sha256=sha(candidate),record_count=len(rows),changed_record_count=20,new_home_setup_records=sorted(targets),menu_and_controlbar_protected_records=sorted(protected),menu_and_controlbar_exact=True,scrollbar_foreground_83_exact=True,all_crcs_verified=True,entries=entries)
 (OUT/'neoui_reports/VERIFIED_HOME_SETUP_BUILD.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PASS: 20 changed records (16 media + 4 HOME/SETUP);',len(protected),'MENU/controlbar records exact; CRCs pass',report['candidate_sha256'])
if __name__=='__main__':main()
