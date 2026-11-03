"""Verify inventory regeneration does not implicitly publish workspace files."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('source_inventory', ROOT / 'scripts/refresh-model-source-inventory.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class ModelSourceInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inventory = self.root / tool.INVENTORY
        self.inventory.write_text(json.dumps(dict(schema_version=1, kind='CanonicalAdaptationSourceFiles', files=[])))
        (self.root / 'reviewed.toon').write_bytes(b'kind: Fixture\n')
        (self.root / 'unreviewed.toon').write_bytes(b'kind: Unlisted\n')

    def test_only_explicit_paths_and_stale_byte_detection(self):
        tool.refresh(self.root, add=['reviewed.toon'])
        self.assertEqual([r['path'] for r in json.loads(self.inventory.read_bytes())['files']], ['reviewed.toon'])
        (self.root / 'reviewed.toon').write_bytes(b'kind: NewFixture\n')
        with self.assertRaisesRegex(ValueError, 'stale'):
            tool.refresh(self.root, check=True)
        tool.refresh(self.root)
        self.assertEqual(tool.refresh(self.root, check=True), 1)

    def test_private_addition_does_not_change_inventory(self):
        before = self.inventory.read_bytes()
        with self.assertRaisesRegex(ValueError, 'outside the active source inventory'):
            tool.refresh(self.root, add=['.local/private.toon'])
        self.assertEqual(self.inventory.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
