#!/usr/bin/env python3
"""Create local indexed thumbnail sheets from a structurally parsed MCF."""
import argparse, struct, zlib
from pathlib import Path
from mcf_inventory import parse
FONT={'0':['111','101','101','101','111'],'1':['010','110','010','010','111'],'2':['111','001','111','100','111'],'3':['111','001','111','001','111'],'4':['101','101','111','001','001'],'5':['111','100','111','001','111'],'6':['111','100','111','101','111'],'7':['111','001','010','010','010'],'8':['111','101','111','101','111'],'9':['111','101','111','001','111']}
def png(path,w,h,rgb):
 def ch(t,b):
  q=t+b; return struct.pack('>I',len(b))+q+struct.pack('>I',zlib.crc32(q)&0xffffffff)
 scan=b''.join(b'\0'+rgb[y*w*3:(y+1)*w*3] for y in range(h))
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(scan,5))+ch(b'IEND',b''))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('mcf',type=Path); ap.add_argument('output',type=Path); ap.add_argument('--per-page',type=int,default=100); ap.add_argument('--cols',type=int,default=10); ap.add_argument('--tile',type=int,default=56); a=ap.parse_args()
 _,rows=parse(a.mcf); rows=[r for r in rows if r['mode']=='0x1104']; cols=a.cols; per=a.per_page; tile=a.tile; label_h=10; rows_page=(per+cols-1)//cols; a.output.mkdir(parents=True,exist_ok=True)
 for start in range(0,len(rows),per):
  group=rows[start:start+per]; W=cols*tile; H=rows_page*(tile+label_h); canvas=bytearray([25,34,45])*(W*H)
  for j,r in enumerate(group):
   x0=(j%cols)*tile; y0=(j//cols)*(tile+label_h); w,h=r['width'],r['height']; scale=min((tile-4)/w,(tile-4)/h); dw=max(1,int(w*scale)); dh=max(1,int(h*scale)); ox=x0+(tile-dw)//2; oy=y0+(tile-dh)//2; raw=r['raw']
   for yy in range(dh):
    sy=min(h-1,int(yy*h/dh))
    for xx in range(dw):
     sx=min(w-1,int(xx*w/dw)); k=(sy*w+sx)*4; rr,gg,bb,aa=raw[k:k+4]; q=((oy+yy)*W+ox+xx)*3
     canvas[q:q+3]=bytes(((rr*aa+25*(255-aa))//255,(gg*aa+34*(255-aa))//255,(bb*aa+45*(255-aa))//255))
   text=str(r['id']); tx=x0+2; ty=y0+tile+1
   for digit in text:
    for gy,line in enumerate(FONT[digit]):
     for gx,v in enumerate(line):
      if v=='1':
       q=((ty+gy)*W+tx+gx)*3; canvas[q:q+3]=b'\xd8\xe8\xf2'
    tx+=4
  first=group[0]['id']; last=group[-1]['id']; png(a.output/f'contact_{first:04d}_{last:04d}.png',W,H,canvas); print(f'{first}-{last}: {len(group)} images')
if __name__=='__main__':main()
