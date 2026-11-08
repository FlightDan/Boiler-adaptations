import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class MaintenanceSplitTest(unittest.TestCase):
    def test_both_validated_model_packages_derive_without_bulk_copies(self):
        project = os.environ.get('BOILER_INSTALLER_ROOT')
        if not project:
            self.skipTest('Set BOILER_INSTALLER_ROOT to the installer checkout')
        sys.path.insert(0, project)
        from protocol.manifest import confined, validate_package
        transform = load('maintenance_split_packages', ROOT/'scripts/derive-legacy-maintenance.py')
        ids = ('f6641d0f82db2cca02114a37', '381dd40541f7fe7eb7c306ff')
        for item in ids:
            package = Path(project)/'cache/device-packages'/item
            with self.subTest(package=item):
                manifest = validate_package(package, allow_unsigned=True)
                changed, removed = transform.derive_package(manifest, lambda name: confined(package, name).read_bytes())
                prefix = 'payload/legacy/maintenance/app/'
                self.assertEqual(removed, {prefix + name for name in transform.REMOVED})
                self.assertIn(prefix + 'oxp3_maintenance/operations.py', changed)
                self.assertIn(prefix + 'oxp3_maintenance/cli.py', changed)
                self.assertIn('payload/legacy/components/maintenance_tool.py', changed)
                self.assertIn('payload/legacy/components/integration.py', changed)
                inventory = {row['path']: row for row in manifest['files']}
                target = prefix + 'entry.py'
                def tampered(name):
                    return b'bad' if name == target else confined(package, name).read_bytes()
                with self.assertRaises(ValueError):
                    transform.derive_package(manifest, tampered)

    def test_derived_runtime_preserves_activation_and_recovery_without_ui(self):
        supplied = os.environ.get('BOILER_OXP3_BASE')
        if not supplied:
            self.skipTest('Set BOILER_OXP3_BASE to the verified retained model input')
        original = Path(supplied)/'payload/legacy/maintenance'
        manifest = (original/'manifest.json').read_bytes()
        app = {p.relative_to(original/'app').as_posix(): p.read_bytes()
               for p in (original/'app').rglob('*') if p.is_file()}
        transform = load('maintenance_split', ROOT/'scripts/derive-legacy-maintenance.py')
        digest = hashlib.sha256(manifest).hexdigest()
        derived, generated = transform.derive(manifest, app, digest)
        with self.assertRaises(ValueError):
            transform.derive(manifest, dict(app, **{'entry.py': b'changed'}), digest)
        self.assertTrue(transform.REMOVED.isdisjoint(derived))
        release = json.loads((Path(supplied)/'payload/legacy/components/release.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            payload = Path(tmp)/'payload'
            folder = payload/'maintenance/app'
            for name, raw in derived.items():
                dest = folder/name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
            (folder.parent/'manifest.json').write_bytes(generated)
            bridge = load('maintenance_tool_split', ROOT/'brands/onexplayer/oxp3/bridge/embedded-maintenance-tool.py')
            files = bridge.files(Path(tmp)/'target', payload, release)
            retired = ('home/deck/Desktop/OXP3-Maintenance.desktop',
                       'home/deck/.local/share/applications/OXP3-Maintenance.desktop',
                       'home/deck/.config/systemd/user/oxp3-maintenance-check.service',
                       'home/deck/.config/systemd/user/oxp3-maintenance-check.timer')
            self.assertTrue(set(retired).isdisjoint(files))
            for name in ('etc/systemd/system/oxp3-maintenance-activate.service',
                         'usr/local/lib/oxp3-maintenance/entry.py',
                         'usr/local/lib/oxp3-maintenance/activation.json'):
                self.assertIn(name, files)
            self.assertTrue(any(p.startswith('usr/local/lib/oxp3-maintenance/releases/') for p in files))
            program = """import sys
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
from oxp3_maintenance import cli, operations
from pathlib import Path
import json, tempfile
with tempfile.TemporaryDirectory() as tmp:
 runtime = Path(tmp)
 prior = runtime/'releases'/'prior'
 prior.mkdir(parents=True)
 (prior/'entry.py').write_text('previous recovery generation')
 (runtime/'current-release.json').write_text(json.dumps({'version':'0.1.0','maintenance_runtime':'prior'}))
 with patch.object(operations.adoption, '_trusted'):
  files = operations.runtime_files(Path(sys.argv[1]), {'version':'0.2.0'}, {'components':{}}, installed_runtime=runtime)
 assert files['usr/local/lib/oxp3-maintenance/releases/prior/entry.py']['data'] == b'previous recovery generation'
with patch.object(operations, 'activate', return_value={'activation':'ok'}):
 assert cli.dispatch(cli.parser().parse_args(['activate'])) == {'activation':'ok'}
with patch.object(operations, 'restore', return_value={'recovery':'ok'}) as restore:
 assert cli.dispatch(cli.parser().parse_args(['recover'])) == {'recovery':'ok'}
 assert restore.call_args.kwargs['recovery'] is True
try:
 cli.dispatch(cli.parser().parse_args(['gui']))
except RuntimeError as exc:
 assert 'retired' in str(exc)
else:
 raise AssertionError('retired gui still runs')
"""
            subprocess.run([sys.executable, '-B', '-c', program, str(folder)], check=True)

if __name__ == '__main__':
    unittest.main()
