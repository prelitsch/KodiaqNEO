#!/usr/bin/env python3
"""Capture bounded runtime evidence without executing firmware classes."""
from pathlib import Path
import zipfile,json,hashlib
from j9_inspect import Rom
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parents[1]
def main():
 p=next((ROOT/'Kodiaq Backup').rglob('*lsd.jxe'))
 if hashlib.sha256(p.read_bytes()).hexdigest()!='a55d9cfb69c5756f8202b7f7aa4079d4d5b637ae4c2fd0fe723f1d6816cbeea8':raise ValueError('runtime backup hash changed')
 wanted={'de/vw/mib/configuration/internal/SkinInformationServiceImpl':['readAmbienceColorMap','getMappedColor','setIntLightAmbientLightColor','getAmbientColor'], 'de/vw/mib/view/internal/ViewCompositorImpl$SkinInformationHandler':['receiveCurrentSkinMode','updateGlobalDynamicColor','receiveAmbientColor'], 'de/vw/mib/skin/internal/SkinImagePoolImpl':['createImage','createScaleImage','supportsSecondScaleImageBitmap'], 'de/vw/mib/graphics/image/Image':['<init>','getCurrentImage'],'de/vw/mib/graphics/image/ScaleImage':['<init>','getImageId','getImageId2'], 'de/vw/mib/graphics/Color':['getCurrentColor','mix'], 'de/vw/mib/widgets/ui/AbstractWidgetUI':['updateScaleImageDrawable'],'de/vw/mib/widgets/ui/AbstractImageUI':['paint'],'de/vw/mib/widgets/Scrollbar':['updateScrollbarImage'],'de/vw/mib/graphics/internal/drawable/renderer/image/ImageDrawableRenderer$SharedImageDrawable':['<init>']}
 evidence=[];shader=[]
 with zipfile.ZipFile(p) as z:
  r=Rom(z.read('rom.classes'))
  for name,methods in wanted.items():
   c=r.find(name)
   for m in r.methods(c):
    if m['name'] in methods:evidence.append(dict(class_name=name,class_offset=c,method=m['name'],descriptor=m['descriptor'],method_offset=m['offset'],code_sha256=hashlib.sha256(bytes.fromhex(m['code_hex'])).hexdigest(),references=m['candidate_cp_sites']))
  for name in z.namelist():
   if name.endswith('ImageComposition.glslf') or name.endswith('TextureCombine_RGBA_Modulate.glslf'):
    data=z.read(name);shader.append(dict(path=name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
  assert len(shader)==2
 result=dict(source=str(p.relative_to(ROOT)),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),inspection='static J9 metadata with method-count checks and reviewed instruction sequences; no firmware execution',methods=evidence,shaders=shader,findings=['two array halves are primary/secondary bitmap layers, not day/night banks','logical image creates day and night ScaleImage entries; pairs match on exact input','secondary bitmap is sampled separately and tinted by v_color.rgb before alpha-over primary','dynamic Color.mix multiplies channels and divides by 255','Scrollbar.updateScrollbarImage assigns state-selected images and colors; white foreground mask must remain uncolored'])
 (OUT/'neoui_reports/RUNTIME_TINT_EVIDENCE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('recorded',len(evidence),'method declarations and',len(shader),'shader hashes')
if __name__=='__main__':main()
