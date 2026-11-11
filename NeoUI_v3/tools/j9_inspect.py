#!/usr/bin/env python3
"""Read-only targeted J9 ROM metadata inspector for the local MU1440 backup."""
import struct,zipfile,hashlib,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parents[1]
class Rom:
 def __init__(self,data):
  if len(data)<112 or data[:4]!=b'J99J':raise ValueError('unsupported ROM header')
  self.b=data
 def u32(self,o):return struct.unpack_from('<I',self.b,o)[0]
 def sp(self,o):return o+struct.unpack_from('<i',self.b,o)[0]
 def utf(self,p):
  if not 0<=p<len(self.b)-2:return ''
  n=struct.unpack_from('<H',self.b,p)[0]
  if not 0<n<2000 or p+2+n>len(self.b):return ''
  s=self.b[p+2:p+2+n]
  return s.decode('ascii') if all(32<=x<127 for x in s) else ''
 def name(self,o):
  try:return self.utf(self.sp(o))
  except (struct.error,IndexError):return ''
 def find(self,name):
  token=name.encode();pos=self.b.find(struct.pack('<H',len(token))+token)
  if pos<0:raise ValueError(name)
  for o in range(0,min(400000,len(self.b)-8),4):
   if self.sp(o)!=pos:continue
   c=self.sp(o+4)
   if 0<c<len(self.b)-112 and self.name(c+8)==name and 112<=self.u32(c)<10000000:return c
  raise ValueError('class header not found: '+name)
 def cp(self,c,index):
  q=c+112+(index-1)*8
  if not 1<=index<=self.u32(c+52):return '?'
  s=self.name(q)
  if s:return s
  p=self.sp(q+4)
  if 0<p<len(self.b)-8:
   a=self.name(p);d=self.name(p+4)
   if a and d:return a+d
  return str(struct.unpack_from('<II',self.b,q))
 def methods(self,c):
  start=self.sp(c+32);end=c+self.u32(c);out=[]
  for o in range(start,end-20,4):
   name=self.name(o);sig=self.name(o+4)
   if not name or not sig.startswith('('):continue
   mod,stack,words,high,args,temps=struct.unpack_from('<IHHBBH',self.b,o+8)
   size=(words+(high<<16))*4
   if size>100000 or o+20+size>end:continue
   code=self.b[o+20:o+20+size];refs=[]
   # Operand annotations are candidate sites until instruction boundaries are reviewed.
   for j in range(len(code)-2):
    if code[j] in [0xb2,0xb3,0xb4,0xb5,0xb6,0xb7,0xb8,0xb9,0xbb,0xbd,0xc0,0xc1]:
     idx=int.from_bytes(code[j+1:j+3],'little');label=self.cp(c,idx)
     if label!='?':refs.append(dict(pc=j,opcode=hex(code[j]),cp_index=idx,target=label))
   out.append(dict(offset=o,name=name,descriptor=sig,modifiers=hex(mod),max_stack=stack,args=args,temps=temps,code_hex=code.hex(' '),candidate_cp_sites=refs))
  if len(out)!=self.u32(c+28):raise ValueError(f'method count mismatch {len(out)} != {self.u32(c+28)}')
  return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('classes',nargs='+');a=ap.parse_args();p=next((ROOT/'Kodiaq Backup').rglob('*lsd.jxe'))
 with zipfile.ZipFile(p) as z:rom=Rom(z.read('rom.classes'))
 out={}
 for n in a.classes:
  c=rom.find(n);out[n]=dict(class_offset=c,rom_size=rom.u32(c),methods=rom.methods(c));print(n,c)
  for m in out[n]['methods']:print(m['name'],m['descriptor'],'code',m['code_hex'],'REFS',[(x['pc'],x['target']) for x in m['candidate_cp_sites']])
 dest=OUT/'neoui_workspace/refs/j9_inspection.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),classes=out),indent=2),encoding='utf-8')
if __name__=='__main__':main()
