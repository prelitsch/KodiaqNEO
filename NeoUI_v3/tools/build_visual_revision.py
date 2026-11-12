#!/usr/bin/env python3
"""Mapped RGBA masters -> immutable, offline v2-based visual revision.

No original inputs, catalog, release policy, SD or vehicle files are written.
Uses only the Python standard library and the established MCF/PNG codecs.
"""
from pathlib import Path
import argparse
from contextlib import contextmanager
import hashlib
import html
import json
import shutil
import sys
import uuid
import zlib

from mcf_inventory import parse, write_png
from build_verified_v3 import rebuild, record_with_pixels
from visual_build import read_png_bytes

PROJECT = Path(__file__).resolve().parents[1]
V1 = 'dfb37cb771c58fb838d3797c3bf356e8fae9475aa980a236b7e9cba055f5cd58'
V2 = 'cfe0aabb1e67e2ea06a07ea365fc24f69e3901e0508a02e87ab8525b92dac103'
DESIGN = '86519e2621e63c3183d317fe6a0badca96030e38048db8962903707a74e2fd86'
INITIAL = '9d7b6601a7d1614b453a4b8428efeeff2daef9684471ff33f54fecb56d1cee09'
FIRMWARE = 'MHI2_ER_SKG13_P4526'
MU = '1440'
TARGET = '/net/mmx/mnt/app/eso/hmi/lsd/Resources/skin3/images.mcf'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(data):
    return dict(bytes=len(data), sha1=hashlib.sha1(data).hexdigest(), sha256=sha(data))


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


@contextmanager
def workspace_staging(root):
    # Python's Windows TemporaryDirectory uses a private ACL. Published build
    # folders must instead inherit the user's workspace ACL so previews open.
    root = root.resolve()
    folder = root/('.tmp-'+uuid.uuid4().hex)
    folder.mkdir()
    try:
        yield folder
    finally:
        if folder.exists():
            if folder.resolve().parent != root or not folder.name.startswith('.tmp-'):
                raise ValueError('refusing cleanup outside build staging directory')
            shutil.rmtree(folder)


def inside(base, relative):
    # Catalog paths are portable even though historical manifests use Windows slashes.
    rel = Path(str(relative).replace('\\', '/'))
    if rel.is_absolute() or ':' in str(rel) or '..' in rel.parts:
        raise ValueError('unsafe relative path: '+str(relative))
    path = (base/rel).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError('path leaves permitted directory: '+str(relative))
    return path


def load_context(project=PROJECT):
    project = project.resolve()
    inputs = {}
    specs = [('v1', 'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf', V1),
             ('v2', 'neoui_workspace/asset_dump/skin3_neoui_v2_pilot.mcf', V2),
             ('design', 'neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf', DESIGN)]
    for name, relative, expected in specs:
        path = project/relative
        if sha(path.read_bytes()) != expected:
            raise ValueError('reference hash mismatch: '+name)
        data, rows = parse(path)
        if len(rows) != 2345 or rebuild(data, rows, {}) != data:
            raise ValueError('reference count/no-op round trip: '+name)
        inputs[name] = dict(data=data, rows=rows, byid={r['id']: r for r in rows})
    ids = [r['id'] for r in inputs['v2']['rows']]
    if any([r['id'] for r in x['rows']] != ids for x in inputs.values()):
        raise ValueError('reference record ID/order mismatch')
    catalog = read_json(project/'resource-map.json')['resources']
    changes = read_json(project/'changesets/v3-design-54.json')
    named = {c['name']: c for c in changes['changes']}
    if (len(catalog) != 54 or len(named) != 54 or set(catalog) != set(named)
            or len({x['mcf_id'] for x in catalog.values()}) != 54):
        raise ValueError('54-resource whitelist uniqueness/mapping mismatch')
    v1, v2, design = [inputs[n]['byid'] for n in ('v1', 'v2', 'design')]
    v2_delta = {i for i in ids if v1[i]['record'] != v2[i]['record']}
    targets = {x['mcf_id'] for x in catalog.values()}
    if targets != {i for i in ids if v1[i]['record'] != design[i]['record']}:
        raise ValueError('target whitelist differs from the locked 54-record design delta')
    if len(v2_delta) != 94 or targets & v2_delta:
        raise ValueError('v2 preservation/target overlap invariant changed')
    protected = set(read_json(project/'neoui_reports/VERIFIED_MEDIA_BT_BUILD.json')['protected_menu_foundation_records'])
    if len(protected & v2_delta) != 74 or protected & targets:
        raise ValueError('protected MENU/foundation whitelist changed')
    for name, item in catalog.items():
        change = named[name]
        i = item['mcf_id']
        if i != change['mcf_id'] or item['master'] != change['master']:
            raise ValueError('catalog differs from reviewed changeset: '+name)
        if (sha(v2[i]['record']) != change['source_record_sha256']
                or sha(design[i]['record']) != change['new_record_sha256']
                or item['original_record_sha256'] != change['source_record_sha256']
                or item['design_record_sha256'] != change['new_record_sha256']
                or item['dimensions'] != [v2[i]['width'], v2[i]['height']]
                or v2[i]['mode'] != '0x1104' or item['format'] != 'RGBA8'
                or item['container'] != TARGET or item['firmware'] != FIRMWARE or item['mu'] != MU):
            raise ValueError('record/geometry/format guard: '+name)
        inside(project/'resources/masters', str(item['master']).replace('\\', '/').removeprefix('resources/masters/'))
        if not str(item['master']).replace('\\', '/').startswith('resources/masters/'):
            raise ValueError('master outside resources/masters: '+name)
    return dict(project=project, inputs=inputs, catalog=catalog, targets=targets,
                v2_delta=v2_delta, protected=protected)


def validate_container(ctx, path):
    data, rows = parse(path)
    base = ctx['inputs']['v2']
    if [r['id'] for r in rows] != [r['id'] for r in base['rows']]:
        raise ValueError('candidate ID/order mismatch')
    for row in rows:
        old = base['byid'][row['id']]
        if row['id'] not in ctx['targets'] and row['record'] != old['record']:
            raise ValueError('unmapped/v2 MENU record changed: '+str(row['id']))
        if (row['width'], row['height'], row['mode']) != (old['width'], old['height'], old['mode']):
            raise ValueError('geometry/format changed: '+str(row['id']))
        if row['id'] in ctx['targets']:
            validate_alpha(old['raw'], row['raw'], str(row['id']))
    if rebuild(data, rows, {}) != data:
        raise ValueError('candidate container alignment/no-op round trip')
    return data, rows


def validate_alpha(original, edited, name):
    if original[3::4] != edited[3::4]:
        raise ValueError('alpha mask changed: '+name)
    for k in range(0, len(original), 4):
        if not original[k+3] and original[k:k+4] != edited[k:k+4]:
            raise ValueError('transparent RGBA changed: '+name)


def previous(ctx, previous_build=None):
    project = ctx['project']
    if previous_build == 'initial':
        folder = None
    elif previous_build:
        folder = inside(project, previous_build)
    elif (project/'neoui_build/visual_builds/latest.json').exists():
        folder = inside(project, read_json(project/'neoui_build/visual_builds/latest.json')['build_directory'])
    else:
        folder = None
    if folder:
        if not folder.is_relative_to((project/'neoui_build/visual_builds').resolve()):
            raise ValueError('previous build must be a local visual build directory')
        manifest = read_json(folder/'manifest.json')
        path = folder/'candidate.mcf'
        if (manifest['source_v2']['sha256'] != V2
                or identity(path.read_bytes()) != manifest['candidate']):
            raise ValueError('previous build hash/lineage mismatch')
    else:
        path = project/'neoui_build/NeoUI_v3_v2_based_candidate.mcf'
        if sha(path.read_bytes()) != INITIAL:
            raise ValueError('initial v2-based predecessor hash mismatch')
    data, rows = validate_container(ctx, path)
    return data, rows


def prepare(ctx, master_root, declared, previous_data, previous_rows):
    unknown = set(declared)-set(ctx['catalog'])
    if unknown:
        raise ValueError('unmapped resource names: '+', '.join(sorted(unknown)))
    v2, design = [ctx['inputs'][n]['byid'] for n in ('v2', 'design')]
    prior = {r['id']: r for r in previous_rows}
    replacements, entries, snapshots = {}, [], {}
    expected = {str(i['master']).replace('\\', '/').removeprefix('resources/masters/') for i in ctx['catalog'].values()}
    actual = {p.relative_to(master_root).as_posix() for p in master_root.rglob('*') if p.is_file() and p.suffix.lower() == '.png'}
    if actual != expected or len(expected) != 54:
        raise ValueError('master file inventory differs from mapped PNGs; missing='+str(sorted(expected-actual))+' extra='+str(sorted(actual-expected)))
    for name, item in sorted(ctx['catalog'].items()):
        i = item['mcf_id']
        relative = str(item['master']).replace('\\', '/').removeprefix('resources/masters/')
        path = inside(master_root, relative)
        blob = path.read_bytes()
        raw = read_png_bytes(blob, *item['dimensions'])
        validate_alpha(v2[i]['raw'], raw, name)
        # Preserve exact encoded records for unchanged pixels (including PNG metadata-only edits).
        record = next((r['record'] for r in (prior[i], design[i], v2[i]) if r['raw'] == raw), None)
        if record is None:
            record = record_with_pixels(v2[i], raw)
        edited = record != prior[i]['record']
        if edited and name not in declared:
            raise ValueError('undeclared PNG edit: '+name+'; pass -Changed with the mapped name')
        replacements[i] = record
        snapshots[relative] = blob
        entries.append(dict(name=name, mcf_id=i, dimensions=item['dimensions'], master=item['master'],
                            master_sha256=sha(blob), alpha_sha256=sha(raw[3::4]), alpha_preserved=True,
                            source_record_sha256=sha(v2[i]['record']), previous_record_sha256=sha(prior[i]['record']),
                            new_record_sha256=sha(record), edited_from_previous=edited,
                            pixel_sha256=sha(raw), aliases=item['logical_aliases'],
                            scope=item['affected_scope'], confidence=item['confidence'], evidence=item['evidence']))
    data = rebuild(ctx['inputs']['v2']['data'], ctx['inputs']['v2']['rows'], replacements)
    if rebuild(ctx['inputs']['v2']['data'], ctx['inputs']['v2']['rows'], replacements) != data:
        raise ValueError('nondeterministic packing')
    return data, entries, snapshots


def restore_from_bundle(folder):
    """Independent placement using saved predecessor offsets, not the rebuild encoder."""
    recovery = read_json(folder/'recovery/index.json')
    _, rows = parse(folder/'candidate.mcf')
    new = {r['id']: r for r in rows}
    prefix = (folder/'recovery/prefix.bin').read_bytes()
    restored = bytearray(recovery['predecessor']['bytes'])
    restored[:len(prefix)] = prefix
    for old in recovery['records']:
        i = old['id']
        record = ((folder/f'recovery/{i}.bin').read_bytes() if i in recovery['changed_ids'] else new[i]['record'])
        if len(record) != old['size'] or sha(record) != old['sha256']:
            raise ValueError('recovery record mismatch: '+str(i))
        restored[old['offset']:old['offset']+old['size']] = record
    if identity(restored) != recovery['predecessor']:
        raise ValueError('independent predecessor restoration mismatch')
    return bytes(restored)


def previews(folder, entries, v2, prior, candidate):
    gallery = folder/'previews'
    gallery.mkdir()
    cards = []
    for e in entries:
        i = e['mcf_id']
        panels = []
        for label, row in [('v2', v2[i]), ('previous', prior[i]), ('new', candidate[i])]:
            filename = f'{i}_{label}.png'
            write_png(gallery/filename, row['width'], row['height'], row['raw'], 'RGBA')
            panels.append(f'<figure><figcaption>{label}</figcaption><img src="{filename}" alt="{label} {i}"></figure>')
        symbols = ', '.join(a.get('symbol', '') for a in e['aliases'])
        cards.append('<article data-edited="'+str(e['edited_from_previous']).lower()+'"><h2>'+html.escape(e['name'])+
                     f' · ID {i} · '+str(e['dimensions'])+'</h2><p>'+html.escape(e['scope'])+'</p><div>'+''.join(panels)+
                     '</div><details><summary>States and aliases</summary>'+html.escape(symbols)+'</details></article>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><title>NeoUI v3 resource review</title>
<style>body{background:#101720;color:#eff6fa;font:16px system-ui;margin:24px}article{border:1px solid #4a6170;padding:16px;margin:16px 0}h2{font-size:18px}article div{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0;max-width:100%;overflow:auto}figcaption{padding:6px}img{display:block;max-width:100%;height:auto;background:repeating-conic-gradient(#34404c 0 25%,#1b2530 0 50%) 0/16px 16px}button{padding:10px;cursor:pointer}details{margin-top:12px}</style>
<h1>NeoUI v3 · exact resource previews</h1><p>V2 / previous offline revision / new. All 54 mapped assets are shown at native size unless the viewport is smaller. These are decoded firmware assets, not full-screen or car-tested previews. Runtime tint, shared consumers and text remain controlled by the firmware. All v2 MENU records are retained exactly.</p>
<button onclick="document.querySelectorAll('article[data-edited=false]').forEach(x=>x.hidden=!x.hidden)">Toggle unchanged assets</button>'''+''.join(cards)+'</html>'
    (gallery/'index.html').write_text(page, encoding='utf-8')


def build(ctx, declared=(), previous_build=None, audit=False, master_root=None, output_root=None):
    project = ctx['project']
    output_root = output_root or project/'neoui_build/visual_builds'
    output_root = output_root.resolve()
    if not output_root.is_relative_to((project/'neoui_build/visual_builds').resolve()):
        raise ValueError('output directory must stay inside neoui_build/visual_builds')
    parent_data, parent_rows = previous(ctx, previous_build)
    data, entries, snapshots = prepare(ctx, master_root or project/'resources/masters', set(declared), parent_data, parent_rows)
    tool_hashes = {n: sha((project/'tools'/n).read_bytes()) for n in
                   ['build_visual_revision.py', 'mcf_inventory.py', 'build_verified_v3.py', 'visual_build.py']}
    inputs = dict(v2=V2, previous=sha(parent_data), masters={k: sha(v) for k,v in sorted(snapshots.items())},
                  tools=tool_hashes, python=sys.version, zlib=zlib.ZLIB_VERSION, declared=sorted(set(declared)))
    version = 'v3-'+sha(json.dumps(inputs, sort_keys=True).encode())[:20]
    if audit:
        return dict(status='OFFLINE INPUT AUDIT PASSED', edited_names=[e['name'] for e in entries if e['edited_from_previous']],
                    candidate=identity(data), release_ready=False)
    output_root.mkdir(parents=True, exist_ok=True)
    destination = output_root/version
    with workspace_staging(output_root) as folder:
        (folder/'candidate.mcf').write_bytes(data)
        validated, rows = validate_container(ctx, folder/'candidate.mcf')
        candidate = {r['id']: r for r in rows}
        prior = {r['id']: r for r in parent_rows}
        changed = [r['id'] for r in rows if r['record'] != prior[r['id']]['record']]
        if set(changed) != {e['mcf_id'] for e in entries if e['edited_from_previous']}:
            raise ValueError('encoded record diff differs from declared changes')
        for e in entries:
            if sha(candidate[e['mcf_id']]['raw']) != e['pixel_sha256']:
                raise ValueError('encoded pixels do not match master: '+e['name'])
        recovery = folder/'recovery'
        recovery.mkdir()
        prefix = parent_data[:52+len(parent_rows)*16+4]
        (recovery/'prefix.bin').write_bytes(prefix)
        for i in changed:
            (recovery/f'{i}.bin').write_bytes(prior[i]['record'])
        write_json(recovery/'index.json', dict(predecessor=identity(parent_data), changed_ids=changed,
                   records=[dict(id=r['id'], offset=r['offset'], size=r['record_bytes'], sha256=sha(r['record'])) for r in parent_rows]))
        restored = restore_from_bundle(folder)
        if restored != parent_data:
            raise ValueError('independent restore was not byte-identical')
        (folder/'restored_predecessor.mcf').write_bytes(restored)
        parse(folder/'restored_predecessor.mcf')
        for relative, blob in snapshots.items():
            path = inside(folder/'masters', relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        previews(folder, entries, ctx['inputs']['v2']['byid'], prior, candidate)
        manifest = dict(schema_version=1, version=version, status='PC-VALIDATED OFFLINE VISUAL BUILD; INSTALLATION BLOCKED',
                        firmware=FIRMWARE, mu=MU, target=TARGET, strategy='existing skin3 fallback; no new selectable slot',
                        source_v2=identity(ctx['inputs']['v2']['data']), previous=identity(parent_data), candidate=identity(validated),
                        inputs=inputs, entries=entries, changed_ids_against_previous=changed,
                        changed_ids_against_v2=[r['id'] for r in rows if r['record'] != ctx['inputs']['v2']['byid'][r['id']]['record']],
                        validation=dict(record_count=len(rows), all_records_decoded=True, all_crcs_verified=True,
                                        geometry_alpha_preserved=True, exact_record_whitelist=True,
                                        v2_changes_preserved=94, v2_menu_foundation_changes_preserved=74,
                                        protected_menu_foundation_records=len(ctx['protected']),
                                        deterministic=True, independent_restore_byte_identical=True),
                        release_ready=False, vehicle_tested=False, installer_included=False, installed_baseline_activated=False,
                        preview='previews/index.html')
        write_json(folder/'manifest.json', manifest)
        write_json(folder/'changeset.json', dict(previous=identity(parent_data), candidate=identity(data),
                   changes=[e for e in entries if e['edited_from_previous']]))
        (folder/'README.md').write_text(f'# {version}\n\nOffline v2-based visual build. Open previews/index.html for all mapped variants and changeset.json for the exact edit delta. All 94 v2 changes (including 74 MENU/foundation changes) and every unmapped record remain byte-identical to v2. Recovery reconstructs the previous offline build, not an assumed installed version. No installation is authorized.\n', encoding='utf-8')
        sums = [sha(p.read_bytes())+'  '+p.relative_to(folder).as_posix() for p in sorted(folder.rglob('*')) if p.is_file()]
        (folder/'SHA256SUMS').write_text('\n'.join(sums)+'\n', encoding='ascii')
        if destination.exists():
            expected = {p.relative_to(folder): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
            actual = {p.relative_to(destination): p.read_bytes() for p in destination.rglob('*') if p.is_file()}
            if actual != expected:
                raise ValueError('immutable build collision: '+version)
        else:
            # Publish only after all validation/previews/recovery succeed.
            folder.rename(destination)
    pointer = output_root/'latest.json'
    pending = output_root/'latest.json.tmp'
    write_json(pending, dict(build_directory=str(destination.relative_to(project)).replace('\\', '/'),
                            candidate=identity(data), release_ready=False, installed_baseline_activated=False))
    pending.replace(pointer)
    return manifest | dict(build_directory=str(destination))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--changed', action='append', default=[], help='Mapped semantic name; repeat for multiple edits')
    ap.add_argument('--previous-build', help='Project-relative visual build directory, or initial; default latest or initial v2-based candidate')
    ap.add_argument('--audit', action='store_true')
    args = ap.parse_args()
    try:
        result = build(load_context(), args.changed, args.previous_build, args.audit)
    except (ValueError, KeyError, OSError) as ex:
        print('BUILD FAILED: '+str(ex), file=sys.stderr)
        return 1
    print(json.dumps({k: result[k] for k in ['status', 'candidate', 'release_ready']} |
                     {k: result[k] for k in ['build_directory', 'changed_ids_against_previous', 'validation'] if k in result}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
