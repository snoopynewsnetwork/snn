"""Read immutable originals; dependencies are stdlib and xlrd 2.x (external)."""
from pathlib import Path
import gzip, hashlib, json, subprocess, tempfile
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/turnout'
NEWS = ROOT / 'data/news'
LEDGER_PATH = OUT / 'source/shared-news-ledger.json'
LEDGER = json.loads((LEDGER_PATH if LEDGER_PATH.exists() else NEWS / 'manifest.json').read_bytes())
SOURCES = {r['id']: r for r in LEDGER}
USED = {}

def sha(b): return hashlib.sha256(b).hexdigest()

def original(sid):
    r = SOURCES[sid]
    p = NEWS / r['asset']; stored = p.read_bytes(); raw = gzip.decompress(stored)
    assert sha(stored) == r['stored_sha256'], sid
    assert sha(raw) == r['raw_sha256'] and len(raw) == r['bytes'], sid
    USED[sid] = dict(r, reference_path=str(p.relative_to(ROOT)), stored_bytes=len(stored))
    return raw

def pdftext(sid):
    raw = original(sid)
    assert raw.startswith(b'%PDF-') and raw.rstrip().endswith(b'%%EOF'), sid
    with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
        f.write(raw); f.flush()
        text = subprocess.check_output(['pdftotext', '-layout', f.name, '-'])
        info = subprocess.check_output(['pdfinfo', f.name]).decode()
    gzwrite(OUT / 'extracts' / (sid + '.txt.gz'), text)
    (OUT / 'extracts' / (sid + '.pdfinfo.txt')).write_text(info)
    return text.decode(), info

def gzwrite(p, b):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(gzip.compress(b, mtime=0))

def jwrite(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

def jlwrite(p, rows):
    gzwrite(p, ''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n' for r in rows).encode())

class Rows(HTMLParser):
    """Capture every TR and its direct TH/TD cells, including incomplete EOF rows.

    No DOM repair or source-key deduplication. Original HTML bytes are retained;
    positions are Unicode character offsets and 1-based source line numbers.
    """
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.text = text; self.offsets = [0]
        for l in text.splitlines(keepends=True): self.offsets.append(self.offsets[-1]+len(l))
        self.rows=[]; self.stack=[]; self.cellstack=[]
        self.feed(text); self.close()
        for r in self.stack:
            r['complete']=False; r['raw_html']=text[r['character_start']:]
        for c in self.cellstack: c['complete']=False
        for r in self.rows:
            for c in r['cells']:
                literal=''.join(c.pop('pieces')).strip()
                c['text_literal']=literal
                c['text']=' '.join(literal.split())
    def pos(self):
        l,c=self.getpos(); return l,c,self.offsets[l-1]+c
    def handle_starttag(self, tag, attrs):
        if tag=='tr':
            l,c,s=self.pos()
            r={'attributes':attrs,'id':dict(attrs).get('id'),'source_line_1based':l,
               'source_column_0based':c,'character_start':s,'cells':[], 'complete':False}
            self.rows.append(r); self.stack.append(r)
        elif tag in ['td','th'] and self.stack:
            l,c,s=self.pos()
            cell={'tag':tag,'attributes':attrs,'source_line_1based':l,
                  'character_start':s,'pieces':[], 'complete':False}
            self.stack[-1]['cells'].append(cell); self.cellstack.append(cell)
    def handle_endtag(self, tag):
        if tag in ['td','th'] and self.cellstack:
            c=self.cellstack.pop(); c['complete']=True
        if tag=='tr' and self.stack:
            r=self.stack.pop(); end=self.pos()[2]+len('</tr>')
            r['complete']=True; r['raw_html']=self.text[r['character_start']:end]
    def handle_data(self, data):
        for c in self.cellstack: c['pieces'].append(data)

def htmlrows(sid):
    return Rows(original(sid).decode('utf-8-sig')).rows

def intcell(s):
    import re
    return int(s.replace(',','')) if re.fullmatch(r'[0-9][0-9,]*',s) else None
