#!/usr/bin/env python3
import sys,json,re,zipfile,io
sys.dont_write_bytecode=True
from acquire import fetch,read,ROOT
s=read(json.loads((ROOT/'evidence/lcc-precincts2025.request.json').read_text())).decode()
options=dict((name,url) for url,name in re.findall(r'<option value="([^"]+\.zip)">([^<]+)</option>',s))
contract=json.loads((ROOT.parent/'data/turnout/priority-set.json').read_text())
for c in contract['county_order'][:24]:
 key='lcc2025-'+c['county_fips']; b,m=fetch(key,options[c['name']])
 if b.startswith(b'PK'): z=zipfile.ZipFile(io.BytesIO(b));print(c['name'],len(z.infolist()),'members',sum(x.file_size for x in z.infolist()),'uncompressed',flush=True)
 else: print('NONZIP',c['name'],b[:80],flush=True)
