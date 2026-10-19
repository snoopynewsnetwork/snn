#!/usr/bin/env python3
"""Run supplied preflight computations with only write destinations isolated.
The original code and shared inputs remain read-only. This reproduction is distinct
from extract.py's independent original parsing. No source numerical logic changes.
"""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;DATA=D.parent;NEWS=DATA/'news'
checks=[]
for name in ['preflight_primary_sources.py','preflight_2024_public_native_export.py']:
 original=(DATA/name).read_text();code=original
 if name=='preflight_primary_sources.py':
  code=code.replace("D=Path(__file__).resolve().parent;N=D/'news'",f"D=Path({str(D)!r});N=Path({str(NEWS)!r})")
  code=code.replace("(N/'extracts/sos-2020-general-canvass.txt')","(D/'extracts/preflight-2020-general-canvass.txt')")
  code=code.replace("D/'coordinator-primary-preflight.json'","D/'preflight-primary-reproduction.json'")
 else:
  code=code.replace("DATA=Path(__file__).resolve().parent",f"DATA=Path({str(DATA)!r})")
  code=code.replace("NEWS/'extracts/2024-public-presidential-native-original-positions.jsonl.gz'",f"Path({str(D/'extracts/preflight-native-positions.jsonl.gz')!r})")
  code=code.replace("NEWS/'extracts/2024-public-exports-complete-OOXML-rows.json.gz'",f"Path({str(D/'extracts/preflight-complete-OOXML.json.gz')!r})")
  code=code.replace("DATA/'coordinator-2024-public-native-export-preflight.json'",f"Path({str(D/'preflight-native-reproduction.json')!r})")
 assert code!=original
 exec(compile(code,str(DATA/name),'exec'),{'__name__':'__main__','__file__':str(DATA/name)})
 checks.append({'source_script':str((DATA/name).relative_to(DATA.parent)),'sha256':hashlib.sha256(original.encode()).hexdigest(),'adaptation':'only output destinations and constants pointing to those destinations; all shared reads stay read-only','status':'pass'})
(D/'preflight-execution.json').write_text(json.dumps(checks,indent=2)+'\n')
