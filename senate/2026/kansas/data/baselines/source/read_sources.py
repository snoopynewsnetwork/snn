"""Independent Kansas baseline readers; originals are referenced, never rewritten."""
from pathlib import Path
import gzip, hashlib, io, json, posixpath, re, subprocess, zipfile
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT/'data/baselines'
N = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(b): return hashlib.sha256(b).hexdigest()
def metadata():
    result={}
    for base, file in [(ROOT/'data/news','manifest.json'),(ROOT/'data/turnout/source','acquisition.json')]:
        for m in json.loads((base/file).read_text()):
            if 'asset' in m:
                m=dict(m, stored_path=str(base/m['asset']))
            elif 'path' in m:
                m=dict(m, stored_path=str(base.parent/m['path']))
            else: continue
            result[m['id']]=m
    own=HERE/'source/acquisition.json'
    if own.exists():
        for m in json.loads(own.read_text()): result[m['id']]=dict(m,stored_path=str(HERE/m['path']))
    return result
def raw(sid):
    m=metadata()[sid]; p=Path(m['stored_path']); b=p.read_bytes()
    assert sha(b)==m['stored_sha256'],sid
    b=gzip.decompress(b)
    assert sha(b)==m['raw_sha256'],sid
    assert len(b)==m.get('raw_bytes',m.get('bytes')),sid
    return b
def workbook(sid):
    z=zipfile.ZipFile(io.BytesIO(raw(sid))); assert z.testzip() is None
    ss=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        ss=[''.join(t.text or '' for t in si.iter('{'+N['s']+'}t')) for si in E.fromstring(z.read('xl/sharedStrings.xml'))]
    rel={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    for s in E.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',N):
        target=rel[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        path=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
        doc=E.fromstring(z.read(path)); rows=[]
        for row in doc.findall('s:sheetData/s:row',N):
            cells={}
            for c in row.findall('s:c',N):
                v=c.find('s:v',N); val=v.text if v is not None else None
                if c.get('t')=='s' and val is not None: val=ss[int(val)]
                if c.get('t')=='inlineStr': val=''.join(t.text or '' for t in c.iter('{'+N['s']+'}t'))
                cells[re.sub('[0-9]+$','',c.get('r'))]=val
            rows.append((int(row.get('r')),cells))
        yield s.get('name'),path,rows
def pdf(sid):
    return subprocess.run(['pdftotext','-layout','-','-'],input=raw(sid),stdout=subprocess.PIPE,check=True).stdout.decode()
if __name__=='__main__':
    for sid in ['sos-2024-president-county','sos-2024-president-precinct','sos-2022-senate-precinct','sos-2020-senate-precinct','sos-2026-senate-primary-precinct','turnout-2022','registration-2024-november']:
        print('\nSOURCE',sid)
        for name,path,rows in workbook(sid):
            populated=[(i,{k:v for k,v in c.items() if v is not None}) for i,c in rows if any(v is not None for v in c.values())]
            print(name,path,'rows',len(rows),'first',populated[:7],'last',populated[-3:])
