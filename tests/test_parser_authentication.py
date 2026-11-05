"""The vendored parser must be authenticated before it can run."""
import shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ParserAuthenticationTests(unittest.TestCase):
 def test_modified_parser_is_not_executed(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'scripts').mkdir();shutil.copy2(ROOT/'scripts/common-device-sources.py',root/'scripts/common-device-sources.py');shutil.copytree(ROOT/'vendor',root/'vendor');shutil.copy2(ROOT/'toon-parser-lock.json',root/'toon-parser-lock.json')
   marker=root/'executed';parser=root/'vendor/toon_format/__init__.py';parser.write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("executed")\n',encoding='utf-8')
   result=subprocess.run([sys.executable,'-B',str(root/'scripts/common-device-sources.py'),'check'],capture_output=True)
   self.assertNotEqual(result.returncode,0);self.assertFalse(marker.exists())
if __name__=='__main__':unittest.main()