#!/usr/bin/env python3
"""Lossless raw entities stay authoritative; derive full PDF text and OOXML rows."""
from pathlib import Path
import gzip,hashlib,io,json,posixpath,re,subprocess,tempfile,zipfile,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(b):return hashlib.sha256(b).hexdigest()
def readjson(p):return json.loads(p.read_bytes())
def pack(p,x):
 b=(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();z=gzip.compress(b,mtime=0);assert len(z)<40000000;p.parent.mkdir(exist_ok=True);p.write_bytes(z)
def workbook(raw):
 z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
 ss=[]
 if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(t.itertext()) for t in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',N)]
 rel={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};out=[]
 for sheet in E.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',N):
  target=rel[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')];member=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target);rows=[]
  for row in E.fromstring(z.read(member)).findall('m:sheetData/m:row',N):
   cells={}
   for c in row.findall('m:c',N):
    v=c.find('m:v',N);f=c.find('m:f',N);rawv=v.text if v is not None else None;value=rawv
    if c.get('t')=='s' and rawv is not None:value=ss[int(rawv)]
    elif c.get('t')=='inlineStr':value=''.join(c.find('m:is',N).itertext()) if c.find('m:is',N) is not None else None
    cells[re.sub('[0-9]','',c.get('r'))]=dict(address=c.get('r'),value=value,type=c.get('t'),style=c.get('s'),raw_v=rawv,formula=f.text if f is not None else None)
   rows.append(dict(row=int(row.get('r')),attributes=dict(row.attrib),cells=cells))
  out.append(dict(name=sheet.get('name'),attributes=dict(sheet.attrib),member=member,worksheet_root_attributes=dict(E.fromstring(z.read(member)).attrib),rows=rows))
 return dict(shared_strings=ss,sheets=out,zip_members=[dict(name=x.filename,bytes=x.file_size,CRC=x.CRC,compressed_bytes=x.compress_size) for x in z.infolist()])
def main():
 index=[]
 prior={x["receipt"]:x for x in readjson(D/"extraction-index.json")} if (D/"extraction-index.json").exists() else {}
 for f in sorted((D/'receipts').glob('*.json')):
  r=readjson(f)
  if not r.get('stored_path') or r.get('http_status')!=200:continue
  raw=gzip.decompress((D/r['stored_path']).read_bytes());id=r['id']
  if id in prior and (D/prior[id]['derivative']).exists():
   existing=json.loads(gzip.decompress((D/prior[id]['derivative']).read_bytes()));assert existing['raw_sha256']==sha(raw);index.append(prior[id]);continue
  if raw.startswith(b'%PDF'):
   with tempfile.NamedTemporaryFile(suffix='.pdf') as p:
    p.write(raw);p.flush();text=subprocess.run(['pdftotext','-layout',p.name,'-'],check=True,capture_output=True).stdout.decode()
   rel='extracted/'+id+'-pdf-text.json.gz';pack(D/rel,dict(receipt=id,raw_sha256=sha(raw),tool='pdftotext -layout',pages=text.split('\f'),complete_text=text));index.append(dict(receipt=id,derivative=rel,type='PDF',pages=len(text.split('\f'))-1))
  elif raw.startswith(b'PK') and (id.startswith('native-export-') or 'ada-linked-2-deeper' in id):
   data=workbook(raw);rel='extracted/'+id+'-xlsx.json.gz';pack(D/rel,dict(receipt=id,raw_sha256=sha(raw),**data));index.append(dict(receipt=id,derivative=rel,type='XLSX',sheets=[dict(name=s['name'],rows=len(s['rows'])) for s in data['sheets']]))
 (D/'extraction-index.json').write_text(json.dumps(index,indent=2)+'\n');print('extractions',len(index))
if __name__=='__main__':main()
