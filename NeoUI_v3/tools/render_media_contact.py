#!/usr/bin/env python3
from pathlib import Path
import json
from mcf_inventory import parse
from mcf_contact_sheets import png,FONT
OUT=Path(__file__).resolve().parents[1]
def main():
 b=json.loads((OUT/'neoui_reports/VERIFIED_MEDIA_BUILD.json').read_text());_,old=parse(OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf');_,new=parse(OUT/'neoui_build/NeoUI_v3_verified_media_skin3.mcf');old={r['id']:r for r in old};new={r['id']:r for r in new};W,H=1040,608;rgb=bytearray([13,19,28])*(W*H)
 for index,m in enumerate(b['entries']):
  ox=(index%4)*260;oy=(index//4)*152
  for charnum,c in enumerate(str(m['mcf_id'])):
   for y,row in enumerate(FONT[c]):
    for x,v in enumerate(row):
     if v=='1':
      for yy in range(2):
       for xx in range(2):k=((oy+8+y*2+yy)*W+ox+8+charnum*8+x*2+xx)*3;rgb[k:k+3]=bytes([119,231,244])
  for col,r in enumerate([old[m['mcf_id']],new[m['mcf_id']]]):
   raw=r['raw']
   for y in range(120):
    for x in range(120):
     k=(y*120+x)*4;rr,gg,bb,a=raw[k:k+4];j=((oy+25+y)*W+ox+col*128+x)*3;rgb[j:j+3]=bytes(((rr*a+13*(255-a))//255,(gg*a+19*(255-a))//255,(bb*a+28*(255-a))//255))
 png(OUT/'neoui_previews/CONTROL_COMPARISON.png',W,H,rgb)
 assert len({new[m['mcf_id']]['raw'] for m in b['entries']})==16,'state variants collapsed'
 print('16 states remain distinct; rendered native-size source/candidate comparison')
if __name__=='__main__':main()
