#!/usr/bin/env python3
"""Independent restoration check: fill original offsets from saved records/candidate."""
from pathlib import Path
import struct,zipfile,json,hashlib,argparse
from mcf_inventory import parse
OUT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--home-setup',action='store_true');g.add_argument('--vehicle-nav',action='store_true');g.add_argument('--media-bt',action='store_true');a=ap.parse_args()
 candidate=OUT/('neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf' if a.media_bt else 'neoui_build/NeoUI_v3_VEHICLE_NAV_skin3.mcf' if a.vehicle_nav else 'neoui_build/NeoUI_v3_HOME_SETUP_skin3.mcf' if a.home_setup else 'neoui_build/NeoUI_v3_verified_media_skin3.mcf')
 _,rows=parse(candidate);available={r['id']:r['record'] for r in rows}
 recovery=OUT/('neoui_build/NeoUI_v3_MEDIA_BT_recovery_records.zip' if a.media_bt else 'neoui_build/NeoUI_v3_VEHICLE_NAV_recovery_records.zip' if a.vehicle_nav else 'neoui_build/NeoUI_v3_HOME_SETUP_recovery_records.zip' if a.home_setup else 'neoui_build/NeoUI_v3_recovery_records.zip')
 with zipfile.ZipFile(recovery) as z:
  prefix=z.read('original_prefix.bin');meta=json.loads(z.read('metadata.json'));n=struct.unpack_from('<I',prefix,48)[0];result=bytearray(meta['source_bytes']);result[:len(prefix)]=prefix
  for i in range(n):
   _,ident,off,size=struct.unpack_from('<4sIII',prefix,52+i*16)
   blob=z.read(f'{ident}.bin') if f'{ident}.bin' in z.namelist() else available[ident]
   if len(blob)!=size:raise ValueError('restoration size mismatch')
   result[off:off+size]=blob
 if hashlib.sha256(result).hexdigest()!=meta['source_sha256']:raise ValueError('restoration digest mismatch')
 dest=OUT/('neoui_build/NeoUI_v3_MEDIA_BT_independent_restore_v1.mcf' if a.media_bt else 'neoui_build/NeoUI_v3_VEHICLE_NAV_independent_restore_v1.mcf' if a.vehicle_nav else 'neoui_build/NeoUI_v3_HOME_SETUP_independent_restore_v1.mcf' if a.home_setup else 'neoui_build/NeoUI_v3_independent_restore_v1.mcf');dest.write_bytes(result);parse(dest)
 if a.home_setup or a.vehicle_nav or a.media_bt:
  report=OUT/('neoui_reports/VERIFIED_MEDIA_BT_BUILD.json' if a.media_bt else 'neoui_reports/VERIFIED_VEHICLE_NAV_BUILD.json' if a.vehicle_nav else 'neoui_reports/VERIFIED_HOME_SETUP_BUILD.json');d=json.loads(report.read_text());d['independent_restore_sha256']=meta['source_sha256'];d['independent_restore_exact']=True;report.write_text(json.dumps(d,indent=2),encoding='utf-8')
 print('PASS independent restore:',meta['source_sha256'])
if __name__=='__main__':main()
