#!/usr/bin/env python3
"""Known two-row PNG filter fixtures and rejection checks for editable-master input."""
from pathlib import Path
import json,struct,zlib
from visual_build import read_png
OUT=Path(__file__).resolve().parents[1]
def main():
 p=OUT/'neoui_workspace/refs/png_decoder_tests';p.mkdir(exist_ok=True)
 raw=bytes([10,20,30,255,40,50,60,128])*2
 fixtures=[bytes([0,10,20,30,255,40,50,60,128])*2,bytes([1,10,20,30,255,30,30,30,129])*2,bytes([2,10,20,30,255,40,50,60,128,2,0,0,0,0,0,0,0,0]),bytes([3,10,20,30,255,35,40,45,1,3,5,10,15,128,15,15,15,193]),bytes([4,10,20,30,255,30,30,30,129,4,0,0,0,0,0,0,0,0])]
 def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
 for n,scan in enumerate(fixtures):
  blob=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',2,2,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b'');f=p/f'filter{n}.png';f.write_bytes(blob);assert read_png(f,2,2)==raw
 f=p/'bad_crc.png';f.write_bytes(blob[:-1]+bytes([blob[-1]^1]))
 for path,w,h in [(f,2,2),(p/'filter0.png',3,2)]:
  try:read_png(path,w,h)
  except ValueError:pass
  else:raise AssertionError('invalid PNG accepted')
 r=dict(status='PASS',standard_png_filters=list(range(5)),known_rgba_bytes_match=True,wrong_dimensions_rejected=True,corrupt_crc_rejected=True)
 (OUT/'neoui_reports/EDITABLE_PNG_TESTS.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print('PASS: five PNG filter fixtures; bad dimensions/CRC rejected')
if __name__=='__main__':main()
