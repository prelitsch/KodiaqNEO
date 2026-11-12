#!/usr/bin/env python3
"""Named editable PNG -> deterministic off-car design rehearsal. Never a release."""
from pathlib import Path
import argparse,hashlib,json,struct,sys,zlib
from mcf_inventory import parse,write_png
from build_verified_v3 import rebuild,record_with_pixels
OUT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def read_png(path,w,h):
 return read_png_bytes(path.read_bytes(),w,h)
def read_png_bytes(b,w,h):
 if b[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('PNG signature')
 off=8;compressed=bytearray();header=False;ended=False
 while off<len(b):
  if off+12>len(b):raise ValueError('truncated PNG')
  n=struct.unpack_from('>I',b,off)[0];tag=b[off+4:off+8];end=off+12+n
  if end>len(b) or zlib.crc32(b[off+4:off+8+n])&0xffffffff!=struct.unpack_from('>I',b,off+8+n)[0]:raise ValueError('PNG bounds/CRC')
  data=b[off+8:off+8+n]
  if tag==b'IHDR':
   if header or data!=struct.pack('>IIBBBBB',w,h,8,6,0,0,0):raise ValueError('require exact dimensions, non-interlaced RGBA8')
   header=True
  elif tag==b'IDAT':
   if not header:raise ValueError('PNG IDAT before header')
   compressed.extend(data)
  elif tag==b'IEND':
   if n or end!=len(b):raise ValueError('PNG suffix/end')
   ended=True
  elif tag[:1].isupper():raise ValueError('unsupported critical PNG chunk')
  off=end
 if not header or not ended:raise ValueError('incomplete PNG')
 dec=zlib.decompressobj();scan=dec.decompress(compressed,(w*4+1)*h+1)
 if len(scan)!=(w*4+1)*h or not dec.eof or dec.unused_data:raise ValueError('PNG decoded length/stream')
 out=bytearray(w*h*4);stride=w*4
 for y in range(h):
  filt=scan[y*(stride+1)];line=scan[y*(stride+1)+1:(y+1)*(stride+1)]
  if filt>4:raise ValueError('PNG filter')
  if filt==0:out[y*stride:(y+1)*stride]=line;continue
  for x,v in enumerate(line):
   a=out[y*stride+x-4] if x>=4 else 0;c=out[(y-1)*stride+x-4] if y and x>=4 else 0;u=out[(y-1)*stride+x] if y else 0
   p=a+u-c;dist=[abs(p-a),abs(p-u),abs(p-c)];paeth=[a,u,c][dist.index(min(dist))]
   pred=[0,a,u,(a+u)//2,paeth][filt];out[y*stride+x]=(v+pred)&255
 return bytes(out)
def immutable(path,blob):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  if path.read_bytes()!=blob:raise ValueError('immutable output collision')
 else:path.write_bytes(blob)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--rehearse-icon',action='store_true');a=ap.parse_args();cat=json.loads((OUT/'resource-map.json').read_text())['resources'];change=json.loads((OUT/'changesets/v3-design-54.json').read_text());policy=json.loads((OUT/'release-policy.json').read_text())
 data,rows=parse(OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf');baseline,brs=parse(OUT/'neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf');old={r['id']:r for r in rows};design={r['id']:r for r in brs}
 if sha(data)!=change['source']['sha256'] or sha(baseline)!=change['target']['sha256'] or rebuild(data,rows,{})!=data:raise ValueError('exact source/design/no-op guard')
 if len(cat)!=54 or len({v['mcf_id'] for v in cat.values()})!=54:raise ValueError('mapping uniqueness')
 if {n:v['mcf_id'] for n,v in cat.items()}!={v['name']:v['mcf_id'] for v in change['changes']}:raise ValueError('semantic name/ID whitelist differs from explicit design changeset')
 replacements={};edits=[];demo_id=cat['nav.action.new_destination.c06']['mcf_id'];raw_before=design[demo_id]['raw'];demo_raw=None
 for name,item in cat.items():
  i=item['mcf_id'];r=old[i];master=(OUT/item['master']).resolve()
  if not master.is_relative_to((OUT/'resources/masters').resolve()) or sha(r['record'])!=item['original_record_sha256']:raise ValueError('master/source guard')
  raw=read_png(master,*item['dimensions'])
  if a.rehearse_icon and i==demo_id:
   raw=bytearray(raw)
   for k in range(0,len(raw),4):
    if raw[k+3] and min(raw[k:k+3])>40 and max(raw[k:k+3])-min(raw[k:k+3])<32:raw[k]=max(0,raw[k]-24)
   raw=bytes(raw);demo_raw=raw
  if raw[3::4]!=r['raw'][3::4]:raise ValueError('alpha change forbidden: '+name)
  for k in range(0,len(raw),4):
   if not r['raw'][k+3] and raw[k:k+4]!=r['raw'][k:k+4]:raise ValueError('transparent RGBA change: '+name)
  record=record_with_pixels(r,raw);replacements[i]=record;edits.append(dict(name=name,mcf_id=i,master_sha256=sha(master.read_bytes()),record_sha256=sha(record)))
 result=rebuild(data,rows,replacements);ident=sha(result);path=OUT/'neoui_build/rehearsals'/(ident+'.mcf');immutable(path,result);_,new=parse(path);diff=[r['id'] for r in new if r['record']!=design[r['id']]['record']]
 if a.rehearse_icon:
  if diff!=[demo_id]:raise ValueError('icon rehearsal changed other resources or masters differ from preserved design')
  # Independent original-offset restoration against the preserved design container.
  prefix=baseline[:52+len(brs)*16+4];restored=bytearray(len(baseline));restored[:len(prefix)]=prefix;nr={r['id']:r for r in new}
  for r in brs:restored[r['offset']:r['offset']+r['record_bytes']]=r['record'] if r['id']==demo_id else nr[r['id']]['record']
  if bytes(restored)!=baseline:raise ValueError('independent design restore failed')
  preview=OUT/'neoui_previews/rehearsals';preview.mkdir(parents=True,exist_ok=True);write_png(preview/'named_icon_before.png',78,52,raw_before,'RGBA');write_png(preview/'named_icon_after.png',78,52,demo_raw,'RGBA')
  contact=b''.join(raw_before[y*78*4:(y+1)*78*4]+demo_raw[y*78*4:(y+1)*78*4] for y in range(52));write_png(preview/'named_icon_pair.png',156,52,contact,'RGBA')
 elif not diff and result!=baseline:raise ValueError('same records but unexpected container changes')
 # Second independent encode from the same data checks deterministic output.
 if rebuild(data,rows,replacements)!=result:raise ValueError('nondeterministic encode')
 report=dict(status='OFFLINE DESIGN REHEARSAL ONLY; NOT AN INSTALLABLE RELEASE',source_sha256=sha(data),preserved_design_sha256=sha(baseline),output_sha256=ident,output_path=str(path.relative_to(OUT)),changed_ids_against_preserved_design=diff,changed_ids_against_v1=sorted(replacements),container_changes='TOC offsets/sizes/CRC and affected IMG compressed bytes/CRC; unchanged record bytes exact',deterministic=True,independent_restore_exact=bool(a.rehearse_icon),installed_baseline=policy['installed_baseline'],release_ready=False,dependencies=dict(python=sys.version,zlib=zlib.ZLIB_VERSION,fonts='none; existing raster masters only'),edits=edits)
 immutable(path.with_suffix('.json'),json.dumps(report,indent=2).encode());(OUT/'neoui_reports'/('VISUAL_EDIT_REHEARSAL.json' if a.rehearse_icon else 'DESIGN_BUILD_REHEARSAL.json')).write_text(json.dumps(report,indent=2),encoding='utf-8');print('PASS:',('single named icon988; restore exact' if a.rehearse_icon else str(len(diff))+' differences from preserved design')+'; deterministic, all CRCs; RELEASE BLOCKED; '+ident)
if __name__=='__main__':main()
