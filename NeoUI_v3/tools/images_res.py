#!/usr/bin/env python3
"""Decode the observed P4526 images.res integer arrays (read-only)."""
import struct,csv,json,hashlib,argparse
from pathlib import Path

def arrays(path):
 b=path.read_bytes()
 if b[:12]!=struct.pack('<III',5,5,2) or b[12:18]!=b'SkrX51':raise ValueError('unsupported images.res header')
 o=20;out=[]
 while o<len(b):
  tag,n=struct.unpack_from('<II',b,o)
  if tag!=5 or o+8+n*4>len(b):raise ValueError('invalid integer array')
  out.append(struct.unpack_from('<'+str(n)+'i',b,o+8));o+=8+n*4
 if len(out)!=4 or len(out[0])%4 or len(out[1])%12:raise ValueError('unexpected array layout')
 if max(out[3])+1!=len(out[1])//12:raise ValueError("logical-count mismatch")
 return out

def resolve(path,symbols):
 a=arrays(path);N=len(a[1])//12; rows=[]
 for bank in range(2):
  for logical in range(N):
   q=a[1][(bank*N+logical)*6:(bank*N+logical+1)*6]
   if q[:3]!=q[3:]:raise ValueError('unverified pair variant')
   rec,inset,flags=q[:3]
   if not 0<=inset<len(a[0])//4:raise ValueError('inset out of bounds')
   rows.append(dict(layer='primary' if bank==0 else 'secondary',day_night_same=(q[:3]==q[3:]),logical_id=logical,symbol=symbols.get(logical,''),bank=bank,mcf_id=rec,inset_index=inset,insets=list(a[0][inset*4:inset*4+4]),scale_mode=flags,flags=flags))
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('res',type=Path);ap.add_argument('symbols',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
 with a.symbols.open(encoding='utf-8') as f:s={int(r['id']):r['symbol'] for r in csv.DictReader(f)}
 rows=resolve(a.res,s);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'source_sha256':hashlib.sha256(a.res.read_bytes()).hexdigest(),'bank_semantics':'0=primary bitmap; 1=secondary bitmap layer; each contains day/night triples, identical on this input; verified from MU1440 runtime','rows':rows},indent=2),encoding='utf-8');print(len(rows),'resolved bank entries')
if __name__=='__main__':main()
