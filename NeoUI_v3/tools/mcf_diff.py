#!/usr/bin/env python3
"""Compare MCF records by ID without modifying either input."""
import argparse,csv,hashlib
from pathlib import Path
from mcf_inventory import parse
def main():
 ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('other',type=Path);ap.add_argument('--csv',type=Path,required=True);a=ap.parse_args()
 _,aa=parse(a.base);_,bb=parse(a.other); left={r['id']:r for r in aa};right={r['id']:r for r in bb}; ids=sorted(set(left)|set(right)); changes=[]
 for ident in ids:
  x=left.get(ident);y=right.get(ident); status='added' if x is None else 'removed' if y is None else 'same' if x['record']==y['record'] else 'changed'
  if status!='same':
   q=y or x;changes.append(dict(id=ident,status=status,width=q['width'],height=q['height'],mode=q['mode'],base_record_sha256=hashlib.sha256(x['record']).hexdigest() if x else '',other_record_sha256=hashlib.sha256(y['record']).hexdigest() if y else ''))
 a.csv.parent.mkdir(parents=True,exist_ok=True)
 with a.csv.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['id','status','width','height','mode','base_record_sha256','other_record_sha256']);w.writeheader();w.writerows(changes)
 print(f'{a.base} -> {a.other}: {len(changes)} added/changed/removed images; unchanged ids {len(ids)-len(changes)}')
 for q in changes:print(f"{q['id']}: {q['status']} {q['width']}x{q['height']} {q['mode']}")
if __name__=='__main__':main()
