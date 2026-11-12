#!/usr/bin/env python3
"""Offline integration checks using exact local firmware references and isolated masters.

Never edit production masters or baseline inputs. All fixtures live in an ignored
temporary directory beneath NeoUI_v3/neoui_build/visual_builds.
"""
from pathlib import Path
import copy
import json
import shutil
import struct
import tempfile
import unittest
import zlib
from unittest.mock import patch

import build_visual_revision as b
from mcf_inventory import parse, write_png
from visual_build import read_png


class VisualRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = b.load_context()
        cls.root = b.PROJECT/'neoui_build/visual_builds'
        cls.root.mkdir(parents=True, exist_ok=True)
        paths = list((b.PROJECT/'resources/masters').rglob('*.png')) + [
            b.PROJECT/'resource-map.json', b.PROJECT/'changesets/v3-design-54.json', b.PROJECT/'release-policy.json',
            b.PROJECT/'neoui_workspace/asset_dump/skin3_neoui_v1_payload.mcf',
            b.PROJECT/'neoui_workspace/asset_dump/skin3_neoui_v2_pilot.mcf',
            b.PROJECT/'neoui_build/NeoUI_v3_MEDIA_BT_skin3.mcf', b.PROJECT/'neoui_build/NeoUI_v3_v2_based_candidate.mcf']
        cls.original_files = {p: b.sha(p.read_bytes()) for p in paths}

    @classmethod
    def tearDownClass(cls):
        for path, digest in cls.original_files.items():
            if b.sha(path.read_bytes()) != digest:
                raise AssertionError('original input/master changed by tests: '+str(path))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='.test-', dir=self.root)
        self.folder = Path(self.temp.name)
        self.masters = self.folder/'masters'
        # Fixtures start from locked design pixels, even if the user has edited real masters.
        for item in self.ctx['catalog'].values():
            row = self.ctx['inputs']['design']['byid'][item['mcf_id']]
            relative = str(item['master']).replace('\\','/').removeprefix('resources/masters/')
            write_png(self.masters/relative, row['width'], row['height'], row['raw'], 'RGBA')
        self.outputs = self.folder/'builds'

    def tearDown(self):
        self.temp.cleanup()

    def run_build(self, names=(), previous='initial'):
        return b.build(self.ctx, names, previous, master_root=self.masters, output_root=self.outputs)

    def master(self, name):
        item = self.ctx['catalog'][name]
        return self.masters/str(item['master']).replace('\\','/').removeprefix('resources/masters/')

    def recolor(self, name):
        item = self.ctx['catalog'][name]
        path = self.master(name)
        raw = bytearray(read_png(path, *item['dimensions']))
        k = next(k for k in range(0,len(raw),4) if raw[k+3])
        raw[k] ^= 1
        write_png(path, *item['dimensions'], bytes(raw), 'RGBA')
        return item['mcf_id']

    def test_no_edit_exact_initial_and_deterministic(self):
        first = self.run_build()
        folder = Path(first['build_directory'])
        self.assertEqual(first['candidate']['sha256'], b.INITIAL)
        self.assertEqual(first['changed_ids_against_previous'], [])
        self.assertEqual(first['validation']['v2_changes_preserved'], 94)
        self.assertEqual(first['validation']['v2_menu_foundation_changes_preserved'], 74)
        self.assertEqual(self.run_build()['build_directory'], str(folder))
        self.assertEqual(b.restore_from_bundle(folder), (folder/'candidate.mcf').read_bytes())
        self.assertTrue((folder/'previews/index.html').exists())
        self.assertEqual(len(list((folder/'previews').glob('*.png'))), 162)
        for line in (folder/'SHA256SUMS').read_text().splitlines():
            digest, relative = line.split('  ',1)
            self.assertEqual(b.sha((folder/relative).read_bytes()), digest)

    def test_two_successive_icon_edits_keep_previous_edit_and_all_v2_records(self):
        name = 'nav.action.new_destination.c06'
        i = self.recolor(name)
        with self.assertRaisesRegex(ValueError, 'undeclared'):
            self.run_build()
        self.assertFalse(self.outputs.exists())
        first = self.run_build([name])
        self.assertEqual(first['changed_ids_against_previous'], [i])
        prior = str(Path(first['build_directory']).relative_to(b.PROJECT))
        second_name = 'shared.action.media'
        j = self.recolor(second_name)
        second = self.run_build([second_name], prior)
        self.assertEqual(second['changed_ids_against_previous'], [j])
        _, rows = parse(Path(second['build_directory'])/'candidate.mcf')
        byid = {r['id']:r for r in rows}
        _, first_rows = parse(Path(first['build_directory'])/'candidate.mcf')
        self.assertEqual(byid[i]['record'], next(r['record'] for r in first_rows if r['id']==i))
        for ident in self.ctx['v2_delta'] | self.ctx['protected']:
            self.assertEqual(byid[ident]['record'], self.ctx['inputs']['v2']['byid'][ident]['record'])
        restored = b.restore_from_bundle(Path(second['build_directory']))
        self.assertEqual(b.identity(restored), first['candidate'])
        self.assertEqual(self.run_build([second_name], prior)['candidate'], second['candidate'])

    def test_invalid_alpha_aborts_without_publishing(self):
        name='nav.action.new_destination.c06'; item=self.ctx['catalog'][name]; path=self.master(name)
        raw=bytearray(read_png(path,*item['dimensions'])); raw[3]^=1
        write_png(path,*item['dimensions'],bytes(raw),'RGBA')
        with self.assertRaisesRegex(ValueError, 'alpha mask'):
            self.run_build([name])
        self.assertFalse(self.outputs.exists())

    def test_transparent_rgb_change_rejected(self):
        name='nav.action.new_destination.c06'; item=self.ctx['catalog'][name]; path=self.master(name)
        raw=bytearray(read_png(path,*item['dimensions']))
        k=next(k for k in range(0,len(raw),4) if not raw[k+3]); raw[k]^=1
        write_png(path,*item['dimensions'],bytes(raw),'RGBA')
        with self.assertRaisesRegex(ValueError,'transparent RGBA'):
            self.run_build([name])

    def test_png_metadata_only_save_keeps_mcf_bytes_exact(self):
        name='nav.action.new_destination.c06'; path=self.master(name); png=path.read_bytes()
        body=b'tEXtEditor\0metadata-only-save'
        chunk=struct.pack('>I',len(body)-4)+body+struct.pack('>I',zlib.crc32(body)&0xffffffff)
        path.write_bytes(png[:-12]+chunk+png[-12:])
        parent,rows=b.previous(self.ctx,'initial')
        result,entries,_=b.prepare(self.ctx,self.masters,set(),parent,rows)
        self.assertEqual(result,parent)
        self.assertFalse(any(e['edited_from_previous'] for e in entries))

    def test_wrong_geometry_and_corrupt_png_rejected(self):
        name='nav.action.new_destination.c06'; path=self.master(name); original=path.read_bytes()
        write_png(path,1,1,b'\0\0\0\0','RGBA')
        with self.assertRaisesRegex(ValueError, 'dimensions'):
            self.run_build([name])
        path.write_bytes(original[:-1]+bytes([original[-1]^1]))
        with self.assertRaisesRegex(ValueError, 'CRC'):
            self.run_build([name])

    def test_unknown_name_extra_master_and_path_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unmapped'):
            self.run_build(['guessed.icon'])
        shutil.copyfile(self.master('shared.action.media'), self.masters/'guessed.png')
        with self.assertRaisesRegex(ValueError, 'inventory'):
            self.run_build()
        with self.assertRaisesRegex(ValueError, 'unsafe relative'):
            b.inside(self.masters, '../outside.png')

    def test_recovery_tamper_and_immutable_collision_rejected(self):
        name='nav.action.new_destination.c06'; i=self.recolor(name); first=self.run_build([name]); folder=Path(first['build_directory'])
        recovery=folder/f'recovery/{i}.bin'; old=recovery.read_bytes(); recovery.write_bytes(old[:-1]+bytes([old[-1]^1]))
        with self.assertRaisesRegex(ValueError, 'recovery record'):
            b.restore_from_bundle(folder)
        recovery.write_bytes(old)
        pointer=(self.outputs/'latest.json').read_bytes()
        (folder/'README.md').write_text('collision')
        with self.assertRaisesRegex(ValueError, 'immutable build collision'):
            self.run_build([name])
        self.assertEqual((self.outputs/'latest.json').read_bytes(), pointer)

    def test_unmapped_predecessor_change_rejected(self):
        initial=self.run_build(); folder=Path(initial['build_directory'])
        data,rows=parse(folder/'candidate.mcf')
        from build_verified_v3 import rebuild, record_with_pixels
        row=next(r for r in rows if r['id'] in self.ctx['v2_delta'] and r['mode']=='0x1104')
        raw=bytearray(row['raw']); raw[0]^=1
        altered=rebuild(data,rows,{row['id']:record_with_pixels(row,bytes(raw))})
        (folder/'candidate.mcf').write_bytes(altered)
        manifest=b.read_json(folder/'manifest.json'); manifest['candidate']=b.identity(altered); b.write_json(folder/'manifest.json',manifest)
        with self.assertRaisesRegex(ValueError, 'unmapped/v2 MENU'):
            self.run_build(previous=str(folder.relative_to(b.PROJECT)))

    def test_reference_hash_and_catalog_tamper_rejected(self):
        fake=self.folder/'project/neoui_workspace/asset_dump'; fake.mkdir(parents=True)
        (fake/'skin3_neoui_v1_payload.mcf').write_bytes(b'wrong source')
        with self.assertRaisesRegex(ValueError, 'reference hash mismatch'):
            b.load_context(self.folder/'project')
        read=b.read_json
        def modified(path):
            obj=read(path)
            if path.name=='resource-map.json':
                obj=copy.deepcopy(obj); obj['resources']['shared.action.media']['mcf_id']=1808
            return obj
        with patch.object(b,'read_json',side_effect=modified):
            with self.assertRaisesRegex(ValueError, 'overlap|mapping|whitelist|catalog'):
                b.load_context()


if __name__=='__main__':
    unittest.main(verbosity=2)
