import ast
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tdp_sources',
    ROOT / 'brands/onexplayer/x2-mini/bridge/tdp_sources.py')
tdp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tdp)


class X2TdpSources(unittest.TestCase):
    def test_scope_and_locked_sources(self):
        rows = {row['path']: row for row in json.loads((ROOT / 'source-lock.json').read_bytes())['files']}
        raw = (ROOT / (tdp.PREFIX + tdp.PROVIDER)).read_bytes()
        provider = ast.parse(tdp.transform(tdp.PROVIDER, raw, rows))
        policy = next(node for node in provider.body
                      if isinstance(node, ast.FunctionDef) and node.name == 'pl1_minimum')
        inputs = {}

        class DevicePath:
            def __init__(self, name):
                self.name = name

            def __truediv__(self, name):
                return DevicePath(self.name + '/' + name)

            def read_text(self):
                if self.name not in inputs:
                    raise FileNotFoundError(self.name)
                return inputs[self.name]

        scope = {'Path': DevicePath, 'MIN_WATTS': 10}
        exec(compile(ast.Module(body=[policy], type_ignores=[]), '<policy>', 'exec'), scope)
        minimum = scope['pl1_minimum']
        self.assertEqual(minimum(), 10)
        inputs.update({'/sys/class/dmi/id/sys_vendor': 'ONE-NETBOOK',
                       '/sys/class/dmi/id/product_name': 'ONEXPLAYER X2Mini',
                       '/proc/cpuinfo': 'model name : Intel(R) Arc(TM) G3 Extreme'})
        self.assertEqual(minimum(), 8)
        inputs['/sys/class/dmi/id/product_name'] = 'ONEXPLAYER 3'
        self.assertEqual(minimum(), 10)
        inputs['/sys/class/dmi/id/product_name'] = 'ONEXPLAYER X2 Mini'
        self.assertEqual(minimum(), 8)
        inputs['/proc/cpuinfo'] = 'model name : Another CPU'
        self.assertEqual(minimum(), 10)
        with self.assertRaisesRegex(ValueError, 'public baseline'):
            tdp.transform(tdp.PROVIDER, raw + b'\n', rows)
        for name in (tdp.HELPER, tdp.PLUGIN):
            output = tdp.transform(name, (ROOT / (tdp.PREFIX + name)).read_bytes(), rows)
            if name == tdp.HELPER:
                ast.parse(output)
            else:
                self.assertIn(b'key==="pl1"?Number(power?.pl1_min_watts??10)', output)
