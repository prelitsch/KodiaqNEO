#!/usr/bin/env python3
"""Read-only compiled-view -> image array -> logical image -> MCF evidence."""
from pathlib import Path
import csv,hashlib,io,json,re,struct,zipfile
from images_res import arrays,resolve
from j9_inspect import Rom
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'NeoUI_v3'
RES=ROOT/'app50_extract/lba0/eso/hmi/lsd/Resources/skin1/images.res'
VIEWS=RES.parent/'viewhandler.zip'
EXPECTED_RES='8d491108101560fcb0f1eca3eff7b46c023a30b0b970c37ba2d4cd831d71e0d1'
def sha(b):return hashlib.sha256(b).hexdigest()
def literal(code,p):
 # Reviewed J9 invocation pattern: sipush/bipush/iconst immediately before invokevirtual.
 if code[p-3:p-2]==b'\x11':return int.from_bytes(code[p-2:p],'little',signed=True)
 if code[p-2:p-1]==b'\x10':return int.from_bytes(code[p-1:p],'little',signed=True)
 if 3<=code[p-1]<=8:return code[p-1]-3
 return None
def trace():
 if sha(RES.read_bytes())!=EXPECTED_RES:raise ValueError('images.res changed')
 a=arrays(RES)
 with (OUT/'neoui_reports/viewhandler_image_symbols.csv').open(encoding='utf-8') as f:symbols={int(r['id']):r['symbol'] for r in csv.DictReader(f)}
 mapping=resolve(RES,symbols);bindings=[];sources={};array_symbols={}
 with zipfile.ZipFile(VIEWS) as z:
  with zipfile.ZipFile(io.BytesIO(z.read('CommonClasses.jxe'))) as j:b=j.read('rom.classes')
  array_symbols={int(i):n.decode() for i,n in re.findall(rb'IMAGEARRAY_(\d+)_([A-Z0-9_]+?PNG)',b)}
  for module,namespace in [('Cmc','car'),('Nmg','nav'),('Nmn','nav')]:
   raw=z.read(module+'.jxe');sources[module]=sha(raw)
   with zipfile.ZipFile(io.BytesIO(raw)) as j:rom=Rom(j.read('rom.classes'))
   cls='generated/de/vw/mib/'+namespace+'/view/internal/'+module
   for m in rom.methods(rom.find(cls)):
    code=bytes.fromhex(m['code_hex'])
    for site in m['candidate_cp_sites']:
     is_array=site['target'].startswith('getImageArray(')
     if not (is_array or site['target'].startswith('getImage(')):continue
     p=site['pc'];n=literal(code,p)
     if n is None:continue
     if is_array:
      start,length=a[2][n*2:n*2+2];refs=list(a[3][start:start+length])
     else:refs=[n]
     # Publish only reviewed target families, not a disassembly of firmware.
     if not (set(refs)&{9,2592,500,501,502,504,506,508,510,512,514,984,994,995,1752,1933,1934,1935,1936,1937,1938,1939,1940,1941,1942,1457,1458,1459,1462,1463,1464}):continue
     if code[p]!=0xb6:raise ValueError('unexpected invocation opcode')
     bindings.append(dict(module=module,method=m['name'],method_rom_offset=m['offset'],pc=p,argument=n,lookup='getImageArray' if is_array else 'getImage',array_symbol=array_symbols.get(n,'') if is_array else None,state_logical_ids=refs,method_code_sha256=sha(code),literal_and_call_hex=code[max(0,p-3):p+3].hex(),resources=[r for r in mapping if r['logical_id'] in set(refs)]))
 # Decode a different container: string paths are mapped by the following int array.
 p=RES.parent.parent/'skin0/imageidmap.res';b=p.read_bytes();o=20
 tag,n=struct.unpack_from('<II',b,o);o+=8
 if (tag,n)!=(1,1970):raise ValueError('unsupported imageidmap')
 paths=[]
 for _ in range(n):
  tag,k=struct.unpack_from('<II',b,o);o+=8
  if tag!=0:raise ValueError('unsupported string')
  paths.append(b[o:o+k*2].decode('utf-16le'));o+=k*2
 tag,k=struct.unpack_from('<II',b,o);o+=8
 if tag!=5 or k!=n or o+k*4!=len(b):raise ValueError('invalid path/id table')
 ids=struct.unpack_from('<'+str(k)+'i',b,o)
 cars=[dict(path=path,mcf_id=i,skin='shared skin0; unchanged') for path,i in zip(paths,ids) if path.endswith('Car/Bordcomputer/Car.png')]
 if not cars:raise ValueError('vehicle paths missing')
 evidence=dict(status='static exact-input resource binding; no head-unit execution',images_res_sha256=sha(RES.read_bytes()),viewhandler_sha256=sha(VIEWS.read_bytes()),module_sha256=sources,image_arrays='array2 pairs (start,length) index array3; preserve all state positions; primary/secondary and day/night resolved by runtime trace',bindings=bindings,shared_vehicle_illustration=dict(imageidmap_sha256=sha(b),paths=cars,selection='Car/Bordcomputer/Car.png with encoded vehicle prefix; actual unit prefix unverified, all variants unchanged'))
 return evidence,mapping
def main():
 evidence,_=trace();p=OUT/'neoui_reports/VEHICLE_NAV_RESOURCE_EVIDENCE.json';p.write_text(json.dumps(evidence,indent=2),encoding='utf-8')
 print('PASS:',len(evidence['bindings']),'compiled view bindings;',len(evidence['shared_vehicle_illustration']['paths']),'shared vehicle paths preserved')
if __name__=='__main__':main()
