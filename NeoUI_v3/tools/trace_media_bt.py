#!/usr/bin/env python3
"""Read-only exact-input MEDIEN/BT resource and shared-state evidence."""
from pathlib import Path
import csv,hashlib,io,json,zipfile
from images_res import arrays,resolve
from j9_inspect import Rom
from trace_vehicle_nav import literal,RES,VIEWS
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
VIEW_HASH='6f7cad69cdc7077c4aefc747931124e9acdbfb8e3f22295d28ec9304b8452256'
RUNTIME_HASH='a55d9cfb69c5756f8202b7f7aa4079d4d5b637ae4c2fd0fe723f1d6816cbeea8'
TARGETS={2217,2202,2214,2199,1036,1131,1133,1134}
def sha(b):return hashlib.sha256(b).hexdigest()
def summary(m):return dict(method=m['name'],method_rom_offset=m['offset'],code_sha256=sha(bytes.fromhex(m['code_hex'])))
def trace():
 if sha(RES.read_bytes())!='8d491108101560fcb0f1eca3eff7b46c023a30b0b970c37ba2d4cd831d71e0d1' or sha(VIEWS.read_bytes())!=VIEW_HASH:raise ValueError('resource metadata changed')
 with (OUT/'neoui_reports/viewhandler_image_symbols.csv').open(encoding='utf-8') as f:symbols={int(r['id']):r['symbol'] for r in csv.DictReader(f)}
 mapping=resolve(RES,symbols);a=arrays(RES);bindings=[];scripts=[];modules={}
 with zipfile.ZipFile(VIEWS) as z:
  for module in ['Mbam','Mbab','Mns','Ma']:
   data=z.read(module+'.jxe');modules[module]=sha(data)
   with zipfile.ZipFile(io.BytesIO(data)) as j:r=Rom(j.read('rom.classes'))
   c=r.find('generated/de/vw/mib/media/view/internal/'+module)
   for m in r.methods(c):
    code=bytes.fromhex(m['code_hex'])
    for s in m['candidate_cp_sites']:
     arr=s['target'].startswith('getImageArray(')
     if not(arr or s['target'].startswith('getImage(')):continue
     p=s['pc'];n=literal(code,p)
     if n is None:continue
     if arr:
      if not 0<=n<len(a[2])//2:raise ValueError('array index out of range')
      start,length=a[2][n*2:n*2+2];refs=list(a[3][start:start+length])
     else:refs=[n]
     resources=[v for v in mapping if v['logical_id'] in set(refs)]
     # Reviewed families plus intentionally retained masks/transport/backgrounds.
     if not(any(v['mcf_id'] in TARGETS for v in resources) or n in [304,306,308,310,42,43,708,430,431,432,433,434,204,116,120,115,256] or (not arr and n in [20,136])):continue
     if code[p]!=0xb6:raise ValueError('unexpected invoke')
     field=next((v['target'] for v in m['candidate_cp_sites'] if p<v['pc']<=p+4 and v['opcode']=='0xb5'),None)
     bindings.append(dict(module=module,**summary(m),pc=p,lookup='getImageArray' if arr else 'getImage',argument=n,state_logical_ids=refs,literal_and_call_hex=code[max(0,p-3):p+3].hex(),assigned_field=field,resources=resources))
    if module=='Mbam' and any(t in m['name'] for t in ['ImageChoiceCoverImageScript','ScriptCoverImageAvailableScript','DisableButtonsScript','ButtonSetButtonBackgroundScript','ScriptAtLeastOnePlaymodeSupportedScript']):
     scripts.append(dict(module=module,**summary(m),reviewed_references=[dict(pc=s['pc'],target=s['target']) for s in m['candidate_cp_sites'] if any(t in s['target'] for t in ['resourceIconsAudioSource','resourceButtonsMedia','set_image','set_borderImage','set_enabled','set_visible','runScript','getAvdcAudioCurrentTrackInfo'])]))
  # Exact skin literal pool: array8 has state-specific alpha-white and green.
  with zipfile.ZipFile(io.BytesIO(z.read('CommonClasses.jxe'))) as j:r=Rom(j.read('rom.classes'))
  c=r.find('generated/de/vw/mib/view/internal/SkinLiteralPool');cl=next(m for m in r.methods(c) if m['name']=='<clinit>');code=bytes.fromhex(cl['code_hex']);puts=[s for s in cl['candidate_cp_sites'] if s['opcode']=='0xb3'];colors=[]
  for n in [8,40,44]:
   put=next(s for s in puts if s['target'].startswith('COLOR__ARRAY1_'+str(n)+'['));start=max(s['pc'] for s in puts if s['pc']<put['pc'])+3
   # Review ldc_w operands only at the exact constructor pattern, not byte scans.
   values=[]
   for p in range(start,put['pc']-8):
    if code[p:p+1]==b'\x13' and code[p+3:p+4]==b'\xb7' and code[p+6:p+7]==b'\xb7':
     index=int.from_bytes(code[p+1:p+3],'little');values.append(f'{r.u32(c+112+(index-1)*8):08X}')
   fields=sorted({s['target'] for s in cl['candidate_cp_sites'] if start<=s['pc']<put['pc'] and s['opcode']=='0xb2'})
   colors.append(dict(array=n,initializer_pc=[start,put['pc']],initializer_sha256=sha(code[start:put['pc']+3]),literal_argb=sorted(set(values)),shared_color_fields=fields,decision='retain exact masks, colors and runtime selection; do not force a baked cyan into this path'))
 runtime=next((ROOT/'Kodiaq Backup').rglob('*lsd.jxe'))
 if sha(runtime.read_bytes())!=RUNTIME_HASH:raise ValueError('runtime changed')
 with zipfile.ZipFile(runtime) as z:r=Rom(z.read('rom.classes'))
 c=r.find('generated/de/vw/mib/global/view/internal/script/CommonScript');ms=r.methods(c);common=[]
 for m in ms:
  if m['name'] in ['runScriptScriptMediaMainChooseCoverImageDeclarationScriptMediaMainChooseCoverImageBehavior','runScriptMediaBtAudioMainMediaInfoScriptAtLeastOnePlaymodeSupportedDeclarationMediaBtAudioMainMediaInfoScriptAtLeastOnePlaymodeSupportedBehavior']:
   common.append(summary(m))
 choose=next(m for m in ms if 'runScriptScriptMediaMainChooseCoverImageDeclaration'==m['name'][:len('runScriptScriptMediaMainChooseCoverImageDeclaration')]);code=bytes.fromhex(choose['code_hex'])
 # Reviewed output tail: selected source array[0] -> outputs0/1; generic source array[0] ->2.
 if code[532:557].hex()!='0319420332b804000419420332b804000519340332b80400ac':raise ValueError('cover output dispatch changed')
 evidence=dict(status='Static exact-input bindings; no firmware execution or head-unit rendering test',viewhandler_sha256=VIEW_HASH,images_res_sha256=sha(RES.read_bytes()),runtime_sha256=RUNTIME_HASH,module_sha256=modules,bindings=bindings,view_scripts=scripts,common_scripts=common,color_arrays=colors,findings=['Mbam is MediaBtAudioMain; source card arrays344/396 resolve BT2217/off2202; generic arrays347/399 resolve2214/off2199.','Common cover script passes selected source array[0] to default/error outputs0/1; generic source array[0] to border output2. Mbam applies set_imageDefault, set_imageError, set_borderImage.','Dynamic cover ResourceLocator and cover availability script remain unchanged. Generic source2214 also supplies the artwork border; it is shared beyond Bluetooth.','Media transport arrays304/306/308/310 confirm all existing sixteen 120px play/pause/skip variants; preserve existing modifications.','Media source-list background arrays147 feed resourceButtonsMediaType341/342, then source button background script; MCF1131/1133/1134 are shared TYPE090 states.','Mix/repeat use image-color array8 (alpha white, white and green); TYPE904 array204 has no bitmap records. Preserve these masks and renderer state colors.','Seekbar arrays42/43 and indicator708 resolve61/39/917; slider color arrays40/44 contain state tints. Retain all seekbar pixels and behavior.','MEDIA background20 aliases MENU foundation2331/2330 and remains exact. Spot136/1889 is fully transparent; no panel is invented there.'])
 if not TARGETS<={x['mcf_id'] for b in bindings for x in b['resources']}:raise ValueError('missing proposed asset binding')
 return evidence,mapping
def main():
 e,_=trace();(OUT/'neoui_reports/MEDIA_BT_RESOURCE_EVIDENCE.json').write_text(json.dumps(e,indent=2),encoding='utf-8');print('PASS:',len(e['bindings']),'media bindings;',len(e['view_scripts']),'cover/state scripts; tint paths retained')
if __name__=='__main__':main()
