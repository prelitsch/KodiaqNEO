#!/usr/bin/env python3
"""Review a stdout receipt on PC. Never arms, installs, or activates a baseline."""
from pathlib import Path
import argparse,datetime,hashlib,json,re
OUT=Path(__file__).resolve().parents[1]
def parse_receipt(text):
 fields={};blocks={};block=None
 for line in text.splitlines():
  if block:
   if line==block+'_RAW_END':block=None
   else:blocks[block].append(line)
   continue
  if line in ['DF_RAW_BEGIN','MOUNTS_RAW_BEGIN']:
   block=line[:-10]
   if block in blocks:raise ValueError('duplicate raw block')
   blocks[block]=[];continue
  if '=' not in line:raise ValueError('unexpected receipt line')
  k,v=line.split('=',1)
  if not re.fullmatch(r'[A-Za-z0-9_.]+',k) or k in fields:raise ValueError('invalid/duplicate receipt field')
  fields[k]=v
 if block:raise ValueError('unterminated raw block')
 return fields,blocks
def review(text,now=None):
 f,blocks=parse_receipt(text);policy=json.loads((OUT/'release-policy.json').read_text());issues=[]
 if f.get('NEOUI_BASELINE_RECEIPT')!='1' or f.get('MODE')!='DEVICE_READ_ONLY':issues.append('not a genuine device-mode receipt; offline simulations cannot confirm a baseline')
 if f.get('END')!='COLLECTED_NOT_RELEASE_AUTHORIZATION' or 'FAILED' in f:issues.append('collection did not complete')
 if f.get('FIRMWARE')!=policy['firmware'] or f.get('MU')!=policy['mu']:issues.append('firmware/MU mismatch')
 if f.get('TARGET')!=policy['device_target']:issues.append('target mismatch')
 if f.get('STABLE_DURING_COLLECTION')!='true':issues.append('target stability not established')
 now=now or datetime.datetime.now(datetime.timezone.utc)
 try:
  start=datetime.datetime.strptime(f['START_UTC'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc);end=datetime.datetime.strptime(f['END_UTC'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
  if not start<=end<=now+datetime.timedelta(minutes=5) or now-start>datetime.timedelta(hours=24):issues.append('receipt timestamp stale, inconsistent or in future; device clock needs review')
 except (KeyError,ValueError):issues.append('missing/invalid UTC timestamps')
 matches=[name for name,r in policy['known_reference_states'].items() if f.get('CURRENT_SHA1')==r['sha1'] and f.get('CURRENT_SHA256')==r['sha256'] and f.get('CURRENT_BYTES')==str(r['bytes'])]
 if len(matches)!=1:issues.append('full SHA1/SHA256/length identity missing or unknown; UNKNOWN never passes')
 if not f.get('ATTRIBUTES','').startswith('-'):issues.append('regular file numeric owner/mode observation missing')
 if not f.get('APP_FREE_KIB','').isdigit():issues.append('free 1024-byte blocks missing')
 if not blocks.get('DF') or not blocks.get('MOUNTS'):issues.append('raw df/mount evidence missing')
 metadata={}
 base=OUT.parent/'app50_extract/lba0/eso/hmi/lsd/Resources/skin1'
 for name in ['images.res','viewhandler.zip','ambienceColorMap.res']:
  expected=hashlib.sha1((base/name).read_bytes()).hexdigest();actual=f.get('METADATA_'+name);metadata[name]=dict(expected_lineage_sha1=expected,observed_sha1=actual)
  if actual!=expected:issues.append('installed metadata lineage mismatch/missing: '+name)
 if not re.fullmatch('[0-9a-f]{40}',f.get('METADATA_info.txt','')):issues.append('skin info hash missing')
 gates=['selected skin requires separately recorded Engineering Menu observation; no verified automatic getter','mount state raw output requires QNX-specific review','post-reboot v2 visual/functional verification unconfirmed','independent predecessor and original-state backups/hash inventory still required','final predecessor-based build, diff, restore rehearsal and storage budget not approved','release review, explicit installation authorization and marker-armed precheck/install implementation not present']
 return dict(status='IDENTITY_REVIEW_ONLY' if not issues else 'INCOMPLETE_OR_REJECTED',receipt_sha256=hashlib.sha256(text.encode()).hexdigest(),reference_identity=matches[0] if len(matches)==1 else None,reference_identity_and_receipt_checks_pass=not issues,collection_issues=issues,metadata=metadata,release_gates=gates,installed_baseline_activated=False,release_ready=False,no_writes_to_sd_or_vehicle=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--capture',type=Path,required=True);a=ap.parse_args()
 try:r=review(a.capture.read_text(encoding='utf-8-sig'))
 except ValueError as ex:r=dict(status='REJECTED',error=str(ex),release_ready=False,installed_baseline_activated=False)
 (OUT/'neoui_reports/LIVE_BASELINE_REVIEW.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2));return 0 if r.get('reference_identity_and_receipt_checks_pass') else 2
if __name__=='__main__':raise SystemExit(main())
