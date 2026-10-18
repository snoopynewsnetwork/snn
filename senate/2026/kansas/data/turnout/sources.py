"""Kansas turnout source readers. Standard library; no source files are edited."""
from pathlib import Path
import gzip, hashlib, io, json, posixpath, re, subprocess, zipfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
STATE = HERE.parent.parent
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def shared_manifest():
    return {r['id']: r for r in json.loads((STATE/'data/news/manifest.json').read_text())}

def source_bytes(source_id):
    shared = shared_manifest()
    if source_id in shared:
        m = shared[source_id]
        stored = (STATE/'data/news'/m['asset']).read_bytes()
        raw = gzip.decompress(stored)
        assert sha(stored) == m['stored_sha256'], source_id
        assert sha(raw) == m['raw_sha256'] and len(raw) == m['bytes'], source_id
        return raw
    m = next(r for r in json.loads((HERE/'source/acquisition.json').read_text()) if r['id'] == source_id)
    stored = (HERE/m['path']).read_bytes()
    assert sha(stored) == m['stored_sha256']
    raw = gzip.decompress(stored)
    assert sha(raw) == m['raw_sha256'] and len(raw) == m['raw_bytes']
    return raw

def worksheets(raw):
    """Resolve workbook relationships; preserve actual worksheet name and XML path."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    assert z.testzip() is None
    strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        strings = [''.join(v.itertext()) for v in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)]
    relations = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    for s in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS):
        target = relations[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        path = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
        doc = ET.fromstring(z.read(path))
        rows = []
        for row in doc.findall('s:sheetData/s:row', NS):
            cells = {}
            for cell in row.findall('s:c', NS):
                value = cell.find('s:v', NS)
                value = value.text if value is not None else None
                if cell.get('t') == 's' and value is not None:
                    value = strings[int(value)]
                elif cell.get('t') == 'inlineStr':
                    value = ''.join(cell.find('s:is', NS).itertext())
                # Retain explicitly present blank cells as None. An absent XML
                # cell remains absent; neither case is a reported zero.
                cells[re.sub(r'\d+$', '', cell.get('r'))] = value
            rows.append((int(row.get('r')), cells))
        yield s.get('name'), path, rows

def pdf_text(source_id):
    return subprocess.run(['pdftotext', '-layout', '-', '-'], input=source_bytes(source_id), stdout=subprocess.PIPE, check=True).stdout.decode('utf-8')

def dump_json(path, obj):
    (HERE/path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
