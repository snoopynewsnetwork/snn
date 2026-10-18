#!/usr/bin/env python3
"""Independent original-byte extract. xlrd 2.0.2 and Poppler are external.

BIFF source rows preserve all literal values and types. OOXML rows preserve
cell addresses/types/formulas/cached values and complete original ZIP bytes.
PDF text retains every page and line, including headings, blank/dash cells.
"""
import csv
import gzip
import hashlib
import io
import json
import pathlib
import posixpath
import re
import subprocess
import sys
sys.dont_write_bytecode = True
import xml.etree.ElementTree as ET
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
NEWS = ROOT.parent/'news'
if pathlib.Path('/tmp/snn-xls-reading-libs').exists():
    sys.path.insert(0, '/tmp/snn-xls-reading-libs')
import xlrd


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dump(name, value):
    p = ROOT/name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def gzjsonl(name, rows):
    p = ROOT/name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(gzip.compress(b''.join((json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n').encode() for r in rows), mtime=0))


def sources():
    pinned = ROOT/'source/shared-originals.json'
    if pinned.exists():
        refs=json.loads(pinned.read_text())
    else:
        shared = json.loads((NEWS/'manifest.json').read_text())
        refs = []
        for m in shared:
            if m['id'].startswith(('sos-', 'archive-cdx-', 'nara-')):
                refs.append(dict(m, shared_path='../news/'+m['asset'], reuse='Read-only exact hash; no copied original', redirect_history_status='Existing manifest supplies final URL and response headers, not complete redirect-hop headers.'))
        dump('source/shared-originals.json', refs)
    result = {}
    for m in refs:
        b = (NEWS/m['asset']).read_bytes()
        assert sha(b) == m['stored_sha256']
        decoded = gzip.decompress(b)
        assert sha(decoded) == m['raw_sha256'] and len(decoded) == m['bytes']
        result[m['id']] = decoded
    for p in sorted((ROOT/'source').glob('*.json')):
        m = json.loads(p.read_text())
        if not isinstance(m, dict) or 'body_path' not in m:
            continue
        b = (p.parent/m['body_path']).read_bytes()
        assert sha(b) == m['stored_sha256']
        body = gzip.decompress(b)
        assert sha(body) == m['original_sha256'] and len(body) == m['original_bytes']
        hdr = (p.parent/m['headers_path']).read_bytes()
        assert sha(hdr) == m['headers_sha256']
        decoded = gzip.decompress(body) if body.startswith(b'\x1f\x8b') and b'content-encoding: gzip' in hdr.lower() else body
        m.update(decoded_original_bytes=len(decoded), decoded_original_sha256=sha(decoded), http_content_decoding='gzip' if decoded != body else 'identity')
        p.write_text(json.dumps(m, indent=2)+'\n')
        result[m['id']] = decoded
    return result


def workbook(sid, body):
    rows = []
    if body.startswith(bytes.fromhex('d0cf11e0')):
        b = xlrd.open_workbook(file_contents=body, formatting_info=True)
        for si, s in enumerate(b.sheets()):
            for ri in range(s.nrows):
                rows.append(dict(source_id=sid, sheet=s.name, sheet_index=si,
                                 source_row=ri+1, values=s.row_values(ri),
                                 cell_types=list(s.row_types(ri))))
    elif body.startswith(b'PK'):
        ns = {'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        z = zipfile.ZipFile(io.BytesIO(body))
        ss = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
        rels = {e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for si, s in enumerate(ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',ns)):
            rid = s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            path = posixpath.normpath('xl/'+rels[rid])
            for r in ET.fromstring(z.read(path)).findall('m:sheetData/m:row',ns):
                vals, cells = [], []
                for c in r:
                    addr = c.attrib['r']; letters = re.match('[A-Z]+',addr)[0]
                    ci = 0
                    for x in letters: ci = ci*26+ord(x)-64
                    while len(vals)<ci: vals.append('')
                    v=c.find('m:v',ns); f=c.find('m:f',ns)
                    raw=v.text if v is not None else None
                    typ=c.attrib.get('t','n')
                    value = ss[int(raw)] if typ=='s' and raw is not None else ''.join(c.find('m:is',ns).itertext()) if typ=='inlineStr' else float(raw) if typ=='n' and raw is not None else raw if raw is not None else ''
                    vals[ci-1]=value
                    cells.append(dict(address=addr,attributes=c.attrib,raw_value=raw,formula=f.text if f is not None else None,parsed_value=value))
                rows.append(dict(source_id=sid,sheet=s.attrib['name'],sheet_index=si,source_row=int(r.attrib['r']),values=vals,OOXML_cells=cells))
    else:
        raise ValueError((sid, body[:16]))
    gzjsonl('extracts/'+sid+'-rows.jsonl.gz',rows)
    return rows


def main():
    src = sources(); index = []
    for sid, body in src.items():
        if body.startswith((bytes.fromhex('d0cf11e0'), b'PK')):
            rows=workbook(sid,body)
            index.append(dict(source_id=sid,original_sha256=sha(body),rows=len(rows),sheets=list(dict.fromkeys(r['sheet'] for r in rows))))
        elif body.startswith(b'%PDF') and not sid.startswith('nara-'):
            t = subprocess.run(['pdftotext','-layout','-','-'],input=body,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
            (ROOT/'extracts').mkdir(exist_ok=True)
            (ROOT/'extracts'/f'{sid}.txt.gz').write_bytes(gzip.compress(t.stdout,mtime=0))
            lines=[]
            for page,text in enumerate(t.stdout.decode().split('\f'),1):
                for line,content in enumerate(text.splitlines(),1):
                    lines.append(dict(source_id=sid,page=page,line=line,text=content))
            gzjsonl('extracts/'+sid+'-lines.jsonl.gz',lines)
            index.append(dict(source_id=sid,original_sha256=sha(body),text_bytes=len(t.stdout),pages=t.stdout.count(b'\f')))
    dump('extracts/index.json',index)
    print(json.dumps(index,indent=2))


if __name__ == '__main__': main()
