import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('common_device_sources', ROOT/'scripts/common-device-sources.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CommonDeviceSourceTests(unittest.TestCase):
    def test_source_only_catalog_is_current(self):
        result = catalog.build()
        self.assertTrue(result['source_only'])
        self.assertEqual({row['id'] for row in result['resources']}, set(catalog.RESOURCES))
        self.assertEqual(result['boot_policy']['component_id'], 'common:ssd-gm7-boot-repair')
        self.assertTrue(all(row['boot_policy'] == 'common:ssd-gm7-boot-repair' for row in result['models']))

    def test_toon_codec_is_locked(self):
        catalog.validate_codec()

    def test_unlocked_external_firmware_is_not_a_checked_in_payload(self):
        be201 = catalog.load(catalog.RESOURCES['resource:intel-be201-firmware'])
        self.assertTrue(all(row['availability'] == 'external-locked' for row in be201['files']))
        self.assertFalse(any((ROOT/'common/network/intel/be201'/row['path']).exists() for row in be201['files']))

    def test_bmi_source_closure_includes_the_header_and_service(self):
        bmi = catalog.load(catalog.RESOURCES['resource:bmi260-gyro'])
        self.assertIn('sources/bmi270.h', [row['path'] for row in bmi['files']])
        self.assertIn('sources/oxp3-gyro.service', [row['path'] for row in bmi['files']])

    def test_selected_advisory_transforms_reproduce_locked_final_bytes(self):
        cases = (
            ('common/gpu/intel/xe/xevmafix-724/transforms/xevma_model_advisory.py', 'xevma_model_advisory',
             'common/gpu/intel/xe/xevmafix-724/sources/load.py', 'common/gpu/intel/xe/xevmafix-724/final/load.py'),
            ('common/audio/realtek/alc245/speaker-route/transforms/speaker_model_advisory.py', 'speaker_model_advisory',
             'common/audio/realtek/alc245/speaker-route/sources/speaker_route.py', 'common/audio/realtek/alc245/speaker-route/final/speaker_route.py'),
        )
        for path, function, source, expected in cases:
            spec = importlib.util.spec_from_file_location(function, ROOT/path)
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            actual = getattr(module, function)((ROOT/source).read_bytes())
            self.assertEqual(hashlib.sha256(actual).hexdigest(), hashlib.sha256((ROOT/expected).read_bytes()).hexdigest())

    def test_migration_maps_match_every_declared_source_file(self):
        catalog.validate_migration()

    def test_gm7_is_fileless_provider_only(self):
        policy = catalog.gm7()
        self.assertEqual(policy['id'], 'ssd:gm7-boot-repair')
        self.assertEqual(policy['version'], 1)
        definition = catalog.load(catalog.GM7)['definitions']['ssd-gm7-boot-repair']
        self.assertEqual(definition['version'], '0.1.0')
        self.assertEqual(definition['ssd_boot_policy']['version'], 1)


if __name__ == '__main__':
    unittest.main()
