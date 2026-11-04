"""The vendored parser must be authenticated before it can run."""
import importlib.util,marshal,shutil,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ParserAuthenticationTests(unittest.TestCase):
 def test_modified_parser_is_not_executed(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'scripts').mkdir();shutil.copy2(ROOT/'scripts/common-device-sources.py',root/'scripts/common-device-sources.py');shutil.copytree(ROOT/'vendor',root/'vendor');shutil.copy2(ROOT/'toon-parser-lock.json',root/'toon-parser-lock.json')
   marker=root/'executed';parser=root/'vendor/toon_format/__init__.py';parser.write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("executed")\n',encoding='utf-8')
   result=subprocess.run([sys.executable,'-B',str(root/'scripts/common-device-sources.py'),'check'],capture_output=True)
   self.assertNotEqual(result.returncode,0);self.assertFalse(marker.exists())
 def fixture(self,root):
  (root/'scripts').mkdir();shutil.copy2(ROOT/'scripts/common-device-sources.py',root/'scripts/common-device-sources.py');shutil.copytree(ROOT/'vendor',root/'vendor');shutil.copy2(ROOT/'toon-parser-lock.json',root/'toon-parser-lock.json')
 def test_preloaded_fake_module_is_not_used(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);self.fixture(root)
   code="""import importlib.util,sys,types
fake=types.ModuleType('toon_format');fake.loads=lambda *a,**k: {'compromised':True}
sys.modules['toon_format']=fake
spec=importlib.util.spec_from_file_location('common_fixture',sys.argv[1]);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.toon_format is not fake
assert module.toon_format.loads('x: 1',strict=True)=={'x':1}
"""
   result=subprocess.run([sys.executable,'-B','-c',code,str(root/'scripts/common-device-sources.py')],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr)
 def test_matching_malicious_pyc_is_not_executed(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);self.fixture(root)
   source=root/'vendor/toon_format/__init__.py'; cache=Path(importlib.util.cache_from_source(str(source)));cache.parent.mkdir(parents=True,exist_ok=True)
   marker=root/'executed';info=source.stat()
   malicious=compile('from pathlib import Path\nPath('+repr(str(marker))+').write_text("executed")\n',str(source),'exec')
   cache.write_bytes(importlib.util.MAGIC_NUMBER+struct.pack('<III',0,int(info.st_mtime)&0xffffffff,info.st_size&0xffffffff)+marshal.dumps(malicious))
   # Positive control proves the timestamp-valid pyc is executable even with -B.
   control=subprocess.run([sys.executable,'-B','-c','import sys;sys.path.insert(0,sys.argv[1]);import toon_format',str(root/'vendor')],capture_output=True,text=True)
   self.assertEqual(control.returncode,0,control.stderr);self.assertTrue(marker.is_file());marker.unlink()
   code="""import importlib.util,sys
spec=importlib.util.spec_from_file_location('common_fixture',sys.argv[1]);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.toon_format.loads('x: 1',strict=True)=={'x':1}
"""
   result=subprocess.run([sys.executable,'-B','-c',code,str(root/'scripts/common-device-sources.py')],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr);self.assertFalse(marker.exists())
if __name__=='__main__':unittest.main()