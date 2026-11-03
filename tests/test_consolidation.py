"""Regression checks for lost, altered or incompletely inventoried source bytes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('consolidation', ROOT / 'scripts/check-consolidation.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class PreservationTests(unittest.TestCase):
    def test_preserved_candidate(self):
        result = checker.verify(ROOT)
        self.assertEqual(result['historical_files'], 500)
        self.assertEqual(result['attachments'], 1)

    def test_missing_original_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / checker.INVENTORY
            path.parent.mkdir(parents=True)
            data = json.loads((ROOT / checker.INVENTORY).read_bytes())
            data['files'].pop()
            path.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Incomplete'):
                checker.verify(root)

    def test_changed_preserved_archive_is_rejected(self):
        data = json.loads((ROOT / checker.INVENTORY).read_bytes())
        row = next(r for r in data['files'] if r['disposition'] == 'archived-byte-for-byte')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'changed-source'
            path.write_bytes((ROOT / row['archive_path']).read_bytes() + b'changed')
            with self.assertRaisesRegex(ValueError, 'Preserved bytes differ'):
                checker.check_bytes(path, row)

    def test_wrong_release_download_is_rejected(self):
        data = json.loads((ROOT / checker.INVENTORY).read_bytes())
        row = next(r for r in data['files'] if r['disposition'] == 'verified-immutable-release-attachment')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'input-source-r5.tar.gz'
            path.write_bytes(b'wrong archive')
            with self.assertRaisesRegex(ValueError, 'Preserved bytes differ'):
                checker.check_bytes(path, row)


if __name__ == '__main__':
    unittest.main()
