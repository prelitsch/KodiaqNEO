#!/usr/bin/env python3
"""Offline v3 media graphics build; writes only under NeoUI_v3.
Generated MCF/PNG files contain proprietary source-derived graphics: local only.
"""
import csv,hashlib,json,struct,zlib
from pathlib import Path
from mcf_inventory import parse,write_png
from images_res import resolve
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parents[1]
EXPECTED='641c34e42ed5843c1795bf860fd4cb7bbb913fdb'
def sha(b):return hashlib.sha256(b).hexdigest()
def rebuild(original,rows,replacements):
 n=len(rows);end=52+n*16
 if rows[0]['offset']!=end+4:raise ValueError('unexpected TOC alignment')
 for a,b in zip(rows,rows[1:]):
  if a['offset']+a['record_bytes']!=b['offset']:raise ValueError('noncontiguous records')
 if rows[-1]['offset']+rows[-1]['record_bytes']!=len(original):raise ValueError('unknown suffix')
 prefix=bytearray(original[:end+4]);chunks=[];offset=end+4
 for i,r in enumerate(rows):
  record=replacements.get(r['id'],r['record']);struct.pack_into('<4sIII',prefix,52+i*16,b'IMG ',r['id'],offset,len(record));chunks.append(record);offset+=len(record)
 struct.pack_into('<I',prefix,end,zlib.crc32(prefix[48:end])&0xffffffff)
 return bytes(prefix)+b''.join(chunks)
def record_with_pixels(row,raw):
 old=row['record'];compressed=zlib.compress(raw,9);compressed+=b'\0'*((-len(compressed))%4)
 head=bytearray(old[:36]);struct.pack_into('<I',head,12,len(compressed));struct.pack_into('<I',head,24,zlib.crc32(head[:24])&0xffffffff)
 body=bytes(head[28:])+compressed
 return bytes(head[:28])+body+struct.pack('<I',zlib.crc32(body)&0xffffffff)
def recolor(raw):
 out=bytearray(raw)
 for k in range(0,len(raw),4):
  r,g,b,a=raw[k:k+4]
  if not a:continue
  # Preserve luminance ranking for every source state, shape and alpha pixel.
  lum=(r*54+g*183+b*19)//256
  if g>r*1.18 and g>b*1.12: # source green focus becomes restrained ice cyan
   t=max(r,g,b)/255; rgb=(int(119*t),int(231*t),int(244*t))
  else:
   t=lum/255;rgb=(round(13+226*t),round(19+227*t),round(28+222*t))
  out[k:k+3]=bytes(rgb)
 return bytes(out)
def main():
 source=OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf';data,rows=parse(source)
 if hashlib.sha1(data).hexdigest()!=EXPECTED:raise ValueError('v1 source mismatch')
 if rebuild(data,rows,{})!=data:raise ValueError('no-op rebuild changed bytes')
 with (OUT/'neoui_reports/viewhandler_image_symbols.csv').open(encoding='utf-8') as f:symbols={int(r['id']):r['symbol'] for r in csv.DictReader(f)}
 mapping=resolve(ROOT/'app50_extract/lba0/eso/hmi/lsd/Resources/skin1/images.res',symbols)
 byid={r['id']:r for r in rows};targets=[r for r in mapping if 797<=r['logical_id']<=812 and r['bank']==0]
 expected_ids={1658,1646,1645,1644,1657,1643,1642,1656,1655,1640,1639,1638,1654,1637,1636,1635}
 if {r['mcf_id'] for r in targets}!=expected_ids:raise ValueError('mapping changed')
 replacements={};manifest=[];preview=OUT/'neoui_previews/verified_media';preview.mkdir(parents=True,exist_ok=True)
 for m in targets:
  r=byid[m['mcf_id']]
  if (r['width'],r['height'],r['mode'])!=(120,120,'0x1104'):raise ValueError('geometry/mode changed')
  aliases=[x for x in mapping if x['mcf_id']==r['id']]
  if any(x['logical_id'] not in set(range(797,813))|set(range(1874,1886)) for x in aliases):raise ValueError('unexpected shared usage')
  raw=recolor(r['raw']);assert raw[3::4]==r['raw'][3::4]
  new=record_with_pixels(r,raw);replacements[r['id']]=new
  before=preview/f'{r["id"]}_before.png';after=preview/f'{r["id"]}_after.png'
  write_png(before,120,120,r['raw'],'RGBA');write_png(after,120,120,raw,'RGBA')
  manifest.append(dict(before_png_sha256=sha(before.read_bytes()),after_png_sha256=sha(after.read_bytes()),mcf_id=r['id'],logical_id=m['logical_id'],symbol=m['symbol'],dimensions=[120,120],alpha='byte-identical',confidence='B: images.res reference and glyph visual match to photo 08; on-device result untested',source_state_code=m['symbol'].split('_C_')[-1],scope='skin3 MCF only; all symbolic aliases enumerated',aliases=aliases,original_record_sha256=sha(r['record']),new_record_sha256=sha(new),original_pixel_sha256=sha(r['raw']),new_pixel_sha256=sha(raw),before=str(before.relative_to(OUT)),after=str(after.relative_to(OUT))))
 candidate=rebuild(data,rows,replacements);dest=OUT/'neoui_build/NeoUI_v3_verified_media_skin3.mcf';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(candidate)
 _,candidate_rows=parse(dest);changed=[r['id'] for r in candidate_rows if r['record']!=byid[r['id']]['record']]
 assert set(changed)==expected_ids
 # Local restore simulation uses candidate records plus original changed records only.
 originals={i:byid[i]['record'] for i in changed}
 import zipfile
 with zipfile.ZipFile(OUT/'neoui_build/NeoUI_v3_recovery_records.zip','w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('original_prefix.bin',data[:52+len(rows)*16+4]);z.writestr('metadata.json',json.dumps(dict(source_sha256=sha(data),source_bytes=len(data))))
  for ident,blob in originals.items():z.writestr(f'{ident}.bin',blob)
 restored=rebuild(candidate,candidate_rows,originals)
 assert restored==data
 restoration=OUT/'neoui_build/NeoUI_v3_restore_rehearsal_v1.mcf';restoration.write_bytes(restored);parse(restoration)
 report=dict(status='OFFLINE CANDIDATE ONLY; not vehicle-tested; no installer',firmware='MHI2_ER_SKG13_P4526',mu='MU1440',strategy='existing skin3 replacement; no independent selectable slot',source_sha1=EXPECTED,source_sha256=sha(data),candidate_sha1=hashlib.sha1(candidate).hexdigest(),candidate_sha256=sha(candidate),record_count=len(rows),changed_record_count=len(changed),noop_roundtrip_byte_identical=True,restore_byte_identical=True,all_crcs_verified=True,entries=manifest)
 (OUT/'neoui_reports/VERIFIED_MEDIA_BUILD.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print('PASS:',len(changed),'verified media records; no-op/restore exact; CRCs pass; candidate',report['candidate_sha256'])
if __name__=='__main__':main()
