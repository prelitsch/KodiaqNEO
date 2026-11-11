#!/usr/bin/env python3
"""Audit immutable design artifacts versus v2; generate catalog, never deployment bytes."""
from pathlib import Path
import hashlib,json,zipfile
from mcf_inventory import parse,write_png
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parent
DEVICE='/net/mmx/mnt/app/eso/hmi/lsd/Resources/skin3/images.mcf'
DESIGN=OUT/'neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf'
def digest(b):return dict(bytes=len(b),sha1=hashlib.sha1(b).hexdigest(),sha256=hashlib.sha256(b).hexdigest())
def key(i,entry):
 n=entry.get('logical_id')
 if n is not None and 797<=n<=812:return 'media.transport.'+['pause','play','previous','next'][(n-797)//4]+'.c'+['02','04','06','07'][(n-797)%4]
 names={2127:'home.panel.primary',2126:'home.panel.ambient',19:'lists.divider',84:'lists.scrollbar.track',2221:'vehicle.trip.decorative_road',1000:'shared.action.setup',1014:'shared.action.tuner',1015:'shared.action.media',1024:'vehicle.action.view',1707:'shared.action.tile.normal',1714:'shared.action.tile.selected',1716:'shared.action.tile.pressed',1717:'shared.action.tile.left_separator',1719:'shared.action.tile.last_selected',2217:'media.bt.card.source',2202:'media.bt.card.source_off',2214:'media.generic.card.source_and_art_border',2199:'media.generic.card.source_off',1036:'media.action.playlist',1131:'lists.type090.normal',1133:'lists.type090.pressed',1134:'lists.type090.disabled',984:'nav.action.announcements.c04',985:'shared.action.tv.c06',986:'nav.action.switch_map.c06',987:'nav.action.poi.c06',988:'nav.action.new_destination.c06',989:'nav.action.new_destination.c04',990:'nav.action.my_destinations.c06',991:'nav.action.my_destinations.c04',992:'nav.action.map_view.c06',993:'nav.action.map_view.c04',1647:'shared.page.previous.c07',1648:'shared.page.previous.c06',1649:'shared.page.previous.c04',1650:'shared.page.next.c07',1651:'shared.page.next.c06',1652:'shared.page.next.c04'}
 return names[i]
def audit():
 policy=json.loads((OUT/'release-policy.json').read_text());build=json.loads((OUT/'neoui_reports/VERIFIED_MEDIA_BT_BUILD.json').read_text());states={};rows={};sources={'mib_pre_neoui':ROOT/'skin3_before_NeoUI.mcf','neoui_v1':OUT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf','neoui_v2_pilot':OUT/'neoui_workspace/asset_dump/skin3_neoui_v2_pilot.mcf','v3_design':DESIGN}
 for name,p in sources.items():
  data,rs=parse(p);info=digest(data)
  if name in policy['known_reference_states'] and info!=policy['known_reference_states'][name]:raise ValueError('reference state changed: '+name)
  if name=='v3_design' and info['sha256']!=build['candidate_sha256']:raise ValueError('design artifact changed')
  if len(rs)!=2345 or (rows and [r['id'] for r in rs]!=list(next(iter(rows.values())))):raise ValueError('MCF ID/count/order mismatch')
  states[name]=dict(path=str(p.relative_to(ROOT)),record_count=len(rs),**info);rows[name]={r['id']:r for r in rs}
 v1,v2,v3=[rows[n] for n in ['neoui_v1','neoui_v2_pilot','v3_design']];a={i for i in v1 if v1[i]['record']!=v2[i]['record']};b={i for i in v1 if v1[i]['record']!=v3[i]['record']};protected=set(build['protected_menu_foundation_records'])
 if len(a)!=94 or len(b)!=54 or a&b:raise ValueError('baseline conflict assumptions changed; review required')
 byentry={x['mcf_id']:x for x in build['entries']};catalog={};changes=[]
 for i in sorted(b):
  entry=byentry[i];name=key(i,entry);row=v3[i];master=OUT/'resources/masters'/Path(*name.split('.')).with_suffix('.png')
  # First export only; preserve any subsequent editable master, never overwrite it.
  if not master.exists():write_png(master,row['width'],row['height'],row['raw'],'RGBA')
  item=dict(mcf_id=i,container=DEVICE,local_design_container=str(DESIGN.relative_to(OUT)),baseline='neoui_v1 design reference; live predecessor unknown',dimensions=[row['width'],row['height']],format='RGBA8',palette=None,compression='zlib; MCF mode0x1104',alpha='preserve byte-for-byte',master=str(master.relative_to(OUT)),master_publication='source-derived; local-only; no redistribution rights established',master_sha256=hashlib.sha256(master.read_bytes()).hexdigest(),original_record_sha256=hashlib.sha256(v1[i]['record']).hexdigest(),design_record_sha256=hashlib.sha256(row['record']).hexdigest(),design_pixel_sha256=hashlib.sha256(row['raw']).hexdigest(),logical_aliases=entry['aliases'],state_source='symbol Cxx codes or explicit named resource; image arrays retained in linked evidence; no guessed runtime labels',display_location=entry.get('screen','Media transport'),affected_scope=entry.get('scope',build['shared_scope']),confidence=entry['confidence'],evidence=['neoui_reports/VERIFIED_MEDIA_BT_BUILD.json','neoui_reports/MEDIA_BT_RESOURCE_EVIDENCE.json','neoui_reports/VEHICLE_NAV_RESOURCE_EVIDENCE.json','neoui_reports/RUNTIME_TINT_EVIDENCE.json'],device_validation='not performed for v3',unsafe_classes='no safety/status, map renderer, layout or compiled code edits')
  item.update(firmware=policy['firmware'],mu=policy['mu'],source_container_sha256=states['neoui_v1']['sha256'],day_night_variants='identical source day/night record pairs on exact traced images.res; no selector edits',variants=[a['symbol'] for a in entry['aliases']],affected_scope=entry.get('scope',entry.get('screen','media transport')+'; existing skin3 resources, all listed aliases/shared consumers; no skin0/1/2 edits'))
  if i in build['new_media_bt_records']:item['affected_scope']=build['shared_scope']
  if name in catalog:raise ValueError('semantic key collision')
  catalog[name]=item;changes.append(dict(name=name,mcf_id=i,source_record_sha256=item['original_record_sha256'],new_record_sha256=item['design_record_sha256'],master=item['master'],shared_scope=item['affected_scope']))
 with zipfile.ZipFile(ROOT/'Kodiaq_NeoUI_v2_Car_Pilot_Kit.zip') as z:
  script=next(n for n in z.namelist() if n.endswith('/run.sh'));archived=z.read(script)
 result=dict(status='RECONCILED; RELEASE BLOCKED pending fresh live baseline and reviewed rebased release',states=states,source_of_v2_install_findings='updated AGENTS.md; console-reported successful replacement, not post-reboot verification',stale_handoff_claims='root context/technical/design/task docs and old V2_SCOPE_AUDIT say not installed; superseded by updated AGENTS.md',archived_v2_script_sha256=hashlib.sha256(archived).hexdigest(),archived_script_note='ZIP source predates field fixes: no df storage guard. Do not treat this archived script as the exact executed fixed version.',v2_changed_ids=sorted(a),v3_design_changed_ids=sorted(b),overlap_ids=sorted(a&b),v2_foundation_changed_ids=sorted(a&protected),direct_v2_to_v1_based_v3_record_changes=len(a|b),v2_changes_that_would_be_reverted_by_old_container=94,preserved_graphics_sha256=states['v3_design']['sha256'],release_ready=False,installed_baseline=None,rebase_plan='After fresh exact baseline confirmation: retain every predecessor record except explicitly reviewed54 design targets; compare against that predecessor; restore that exact predecessor. Do not copy old container over v2.',future_restore_target='exact verified predecessor; RESTORE_V2 only if v2 confirmed; never reuse the v1 design recovery ZIP as v2 rollback')
 r=OUT/'neoui_reports';(r/'PIPELINE_RECONCILIATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8');(OUT/'resource-map.json').write_text(json.dumps(dict(schema_version=1,status='design catalog; not live baseline',resources=catalog),indent=2),encoding='utf-8');(OUT/'changesets').mkdir(exist_ok=True);(OUT/'changesets/v3-design-54.json').write_text(json.dumps(dict(status='preserved offline design changes; not an install manifest',source=states['neoui_v1'],target=states['v3_design'],changes=changes),indent=2),encoding='utf-8')
 index=['# Named graphics index','','Local editable masters are source-derived, excluded from Git. Numeric IDs come from verified manifests, not appearance. This catalog describes v1-based design work; it does not select an installed baseline.','','| Semantic name | MCF | Geometry |','|---|---|---|']
 for n,v in catalog.items():index.append('| '+n+' | '+str(v['mcf_id'])+' | '+'×'.join(map(str,v['dimensions']))+' |')
 (r/'RESOURCE_NAME_INDEX.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
 inventory=['# Labeled reference and recovery inventory','','These references are distinct and hash-verified on PC. Only the pre-NeoUI file is labeled a historical PC backup. Cached install payloads are not fresh independent backups of the installed unit. No file was copied to/from an SD card or vehicle. No backup was overwritten.','','| State label | PC provenance | Bytes | SHA256 |','|---|---|---:|---|']
 for n,v in states.items():inventory.append('| '+n+' | '+v['path']+' | '+str(v['bytes'])+' | '+v['sha256']+' |')
 inventory+=['','Current installed predecessor, selected skin, owner/mode and mount state remain UNKNOWN. Historical v1 mode777/root:root is not a v3 instruction. Existing v1 design recovery archives restore v1 only. A confirmed-v2 release requires separately labeled, independently verified exact-v2 predecessor backups and original-state recovery copies; do not rename a v1 payload/backup to v2.','']
 (r/'BACKUP_REFERENCE_INVENTORY.md').write_text('\n'.join(inventory),encoding='utf-8')
 return result
def main():
 r=audit();print('PASS: v2=94, design=54, overlap=0; direct old-container replacement would revert94 including74 MENU/foundation records. RELEASE BLOCKED. Graphics bytes preserved.')
if __name__=='__main__':main()
