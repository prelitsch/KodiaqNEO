#!/usr/bin/env python3
"""Read-only MCF inventory and conservative PNG export helper.

MCF records observed on this target have a 52-byte file header, 16-byte index
records and IMG record payloads with a 36-byte record header followed by zlib
bytes. This tool validates bounds, zlib decode length and unique IDs. Pixel
channel semantics are not claimed; PNG export is for offline visual inspection.
"""
from __future__ import annotations
import argparse, csv, hashlib, struct, zlib
from pathlib import Path

FILE_HEADER=52
INDEX_REC=16
IMG_HEADER=36
MODE_RGBA=0x1104
MODE_INDEXED=0x1000

def parse(path: Path):
    data=path.read_bytes()
    if len(data)<FILE_HEADER or data[:4]!=b'\x89MCF':
        raise ValueError('unrecognized MCF signature/header')
    count=struct.unpack_from('<I',data,48)[0]
    index_end=FILE_HEADER+count*INDEX_REC
    if index_end>len(data): raise ValueError('index exceeds file size')
    if zlib.crc32(data[:16])&0xffffffff != struct.unpack_from('<I',data,16)[0]: raise ValueError('file header CRC')
    if zlib.crc32(data[20:44])&0xffffffff != struct.unpack_from('<I',data,44)[0]: raise ValueError('TOC header CRC')
    if zlib.crc32(data[48:index_end])&0xffffffff != struct.unpack_from('<I',data,index_end)[0]: raise ValueError('TOC data CRC')
    seen=set(); rows=[]
    for n in range(count):
        tag,ident,off,size=struct.unpack_from('<4sIII',data,FILE_HEADER+n*INDEX_REC)
        if ident in seen: raise ValueError(f'duplicate image ID {ident}')
        seen.add(ident)
        if tag!=b'IMG ' or off<index_end or size<IMG_HEADER or off+size>len(data):
            raise ValueError(f'invalid index entry #{n}: id={ident}, off={off}, size={size}')
        r=data[off:off+size]
        typ,rid,flags,zsize,pixels,unknown,checksum,w,h,mode,tail=struct.unpack_from('<4sIIIIIIhhhh',r)
        if typ!=b'IMG ' or rid!=ident or w<=0 or h<=0 or IMG_HEADER+zsize>size:
            raise ValueError(f'invalid image record id={ident}')
        if zlib.crc32(r[:24])&0xffffffff != checksum: raise ValueError(f'image header CRC id={ident}')
        if zlib.crc32(r[28:-4])&0xffffffff != struct.unpack_from('<I',r,len(r)-4)[0]: raise ValueError(f'image data CRC id={ident}')
        raw=zlib.decompress(r[IMG_HEADER:IMG_HEADER+zsize])
        expected=w*h*(4 if mode==MODE_RGBA else 1 if mode==MODE_INDEXED else 0)
        if not expected or len(raw)!=expected:
            raise ValueError(f'unknown mode or decoded length mismatch id={ident} mode={mode:#x} {len(raw)} != {expected}')
        rows.append(dict(id=ident,index=n,offset=off,record_bytes=size,width=w,height=h,mode=f'0x{mode:04x}',decoded_bytes=len(raw),flags=flags,zlib_bytes=zsize,stored_checksum=f'0x{checksum:08x}',record= r,raw=raw))
    return data,rows

def write_png(path: Path,w:int,h:int,raw:bytes,order:str):
    if order=='BGRA':
        raw=b''.join(raw[i:i+4][2:3]+raw[i:i+4][1:2]+raw[i:i+4][0:1]+raw[i:i+4][3:4] for i in range(0,len(raw),4))
    elif order=='ARGB':
        raw=b''.join(raw[i:i+4][1:4]+raw[i:i+4][0:1] for i in range(0,len(raw),4))
    elif order!='RGBA': raise ValueError(order)
    def chunk(tag,payload):
        body=tag+payload
        return struct.pack('>I',len(payload))+body+struct.pack('>I',zlib.crc32(body)&0xffffffff)
    scan=b''.join(b'\0'+raw[y*w*4:(y+1)*w*4] for y in range(h))
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(scan,6))+chunk(b'IEND',b'')
    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(png)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('mcf',type=Path); ap.add_argument('--csv',type=Path); ap.add_argument('--export',type=Path,help='export selected image IDs for visual inspection'); ap.add_argument('--ids',nargs='*',type=int,default=[]); ap.add_argument('--channel-order',choices=['RGBA','BGRA','ARGB'],default='RGBA')
    a=ap.parse_args(); data,rows=parse(a.mcf); sha=hashlib.sha256(data).hexdigest()
    print(f'PASS structural decode: {a.mcf} bytes={len(data)} sha256={sha} images={len(rows)}')
    if a.csv:
        a.csv.parent.mkdir(parents=True,exist_ok=True)
        with a.csv.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=['id','index','offset','record_bytes','width','height','mode','decoded_bytes','flags','zlib_bytes','stored_checksum','source_sha256']); w.writeheader()
            for r in rows:w.writerow({k:r[k] for k in w.fieldnames if k in r}|{'source_sha256':sha})
    if a.export:
        wanted=set(a.ids); selected=[r for r in rows if r['id'] in wanted]
        if wanted-set(r['id'] for r in selected): raise ValueError(f'missing ids: {sorted(wanted-set(r["id"] for r in selected))}')
        for r in selected:
            if r['mode']!=f'0x{MODE_RGBA:04x}': print(f'SKIP id={r["id"]}: indexed/unknown palette not mapped'); continue
            write_png(a.export/f"{r['id']:04d}_{a.channel_order}.png",r['width'],r['height'],r['raw'],a.channel_order)
            print(f"EXPORTED visual-inspection candidate id={r['id']} {r['width']}x{r['height']} order={a.channel_order}")
    dims={}
    for r in rows:dims[(r['width'],r['height'],r['mode'])]=dims.get((r['width'],r['height'],r['mode']),0)+1
    print('dimensions/modes:')
    for (w,h,m),n in sorted(dims.items(),key=lambda x:(-x[0][0]*x[0][1],x[0][0],x[0][1])):print(f' {w}x{h} {m}: {n}')
if __name__=='__main__': main()
