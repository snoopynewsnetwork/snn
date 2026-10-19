#!/usr/bin/env python3
"""Read-only original extraction; Poppler required. Complete sources remain immutable."""
import gzip,json,subprocess,tempfile,zlib,re,zipfile,io,xml.etree.ElementTree as ET
from pathlib import Path
from inspect_sources import read_receipt
ROOT=Path(__file__).resolve().parent
rs=json.loads((ROOT/'acquisition.json').read_text());out={}
for r in rs:
 b=read_receipt(r);enc=next((v for k,v in r['headers'].items() if k.lower()=='content-encoding'),'');b=gzip.decompress(b) if enc=='gzip' else zlib.decompress(b) if enc=='deflate' else b
 if b.startswith(b'%PDF'):
  # All original PDFs retained; complete layout text for selected current/legal/result documents.
  if r['county']=='STATE' or r['id'] in ['deep2-87','deep2-89','deep3-44','deep4-35','deep4-36','deep2-51','deep2-69','deep2-24','deep2-25','county-teller-follow-3','county-delta-follow-3']:
   with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
    f.write(b);f.flush();s=subprocess.check_output(['pdftotext','-layout',f.name,'-']).decode()
   out[r['id']]={'type':'PDF-complete-layout-text','text':s,'source_receipt':r['id']}
 elif b.startswith(b'PK'):
  with zipfile.ZipFile(io.BytesIO(b)) as z:
   # Retain complete member index, original XML bytes via ZIP original, full shared strings and every cell attributes/raw children.
   ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
   shared=ET.fromstring(z.read('xl/sharedStrings.xml')) if 'xl/sharedStrings.xml' in z.namelist() else []
   strings=[''.join(n.itertext()) for n in shared]
   sheets={}
   for name in z.namelist():
    if re.match('xl/worksheets/sheet[0-9]+.xml$',name):
     tree=ET.fromstring(z.read(name));sheets[name]=[{'attributes':dict(c.attrib),'complete_xml':ET.tostring(c,encoding='unicode'),'decoded_shared_string':strings[int(c.find('s:v',ns).text)] if c.get('t')=='s' and c.find('s:v',ns) is not None else None} for c in tree.findall('.//s:c',ns)]
   out[r['id']]={'type':('XLSX-all-cells' if 'xl/workbook.xml' in z.namelist() else 'ZIP-member-index; complete aggregate CSVs in aggregate-exports.json'),'source_receipt':r['id'],'members':[{'filename':a.filename,'CRC':a.CRC,'file_size':a.file_size,'compress_size':a.compress_size} for a in z.infolist()],'shared_strings':strings,'sheets':sheets}
(ROOT/'document-extracts.json.gz').write_bytes(gzip.compress((json.dumps(out,ensure_ascii=False,separators=(',',':'),sort_keys=True)+'\n').encode(),mtime=0));print('documents',len(out))
