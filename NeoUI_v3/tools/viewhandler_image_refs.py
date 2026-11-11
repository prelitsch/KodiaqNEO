#!/usr/bin/env python3
"""Extract symbolic IMAGE_<id> names from read-only JXE resources in a ZIP."""
import argparse,csv,re,zipfile
from pathlib import Path
RX=re.compile(rb'IMAGE_(\d+)_([A-Z0-9_]+)')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('zip',type=Path);ap.add_argument('--csv',type=Path,required=True);a=ap.parse_args();rows=[]
 with zipfile.ZipFile(a.zip) as z:
  for name in z.namelist():
   if name.endswith('/'):continue
   data=z.read(name)
   for m in RX.finditer(data): rows.append((int(m.group(1)),name,m.group(2).decode('ascii','replace')))
 a.csv.parent.mkdir(parents=True,exist_ok=True)
 with a.csv.open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(['id','module','symbol']);w.writerows(sorted(set(rows)))
 print(f'{len(set(rows))} symbolic references across {len(set(r[0] for r in rows))} image IDs -> {a.csv}')
if __name__=='__main__':main()
