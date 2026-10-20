"""Offline full-field extraction; Python 3 stdlib and optional Poppler for PDFs.
Raw character slices always refer to complete pinned original decoded entity.
No vendor IDs inferred from DOM IDs, select values, labels or ordering.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import csv,gzip,hashlib,html,io,json,re,subprocess,tempfile,zipfile
from freeze import S,R,load,pin,sha
def write(name,v):
    b=(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
    if name.endswith('.gz'):b=gzip.compress(b,mtime=0)
    assert len(b)<40_000_000;(R/name).write_bytes(b)
class Text(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.out=[]
    def handle_data(self,d):self.out.append(d)
def text(h):
    p=Text();p.feed(h);return ''.join(p.out)
def attrs(h):
    class A(HTMLParser):
        def handle_starttag(self,t,a):self.value=a
    a=A();a.feed(h);return getattr(a,'value',[])
def document(t,url):
    tables=[]
    for m in re.finditer(r'<table\b[^>]*>.*?</table\s*>',t,re.S|re.I):
        rows=[]
        for rm in re.finditer(r'<tr\b[^>]*>.*?</tr\s*>',m[0],re.S|re.I):
            cells=[]
            for cm in re.finditer(r'<(td|th)\b[^>]*>(.*?)</\1\s*>',rm[0],re.S|re.I):
                cells.append(dict(tag=cm[1],attrs=attrs(cm[0].split('>')[0]+'>'),text=text(cm[2]),normalized_text=re.sub(r'\s+',' ',text(cm[2])).strip(),source_start=m.start()+rm.start()+cm.start(),source_end=m.start()+rm.start()+cm.end()))
            rows.append(dict(attrs=attrs(rm[0].split('>')[0]+'>'),source_start=m.start()+rm.start(),source_end=m.start()+rm.end(),cells=cells))
        cap=re.search(r'<caption\b[^>]*>(.*?)</caption>',m[0],re.S|re.I)
        tables.append(dict(source_start=m.start(),source_end=m.end(),attrs=attrs(m[0].split('>')[0]+'>'),caption=dict(raw_html=cap[0],text=text(cap[1]),source_start=m.start()+cap.start(),source_end=m.start()+cap.end()) if cap else None,rows=rows))
    links=[]
    for m in re.finditer(r'<a\b[^>]*>.*?</a\s*>',t,re.S|re.I):
        aa=attrs(m[0].split('>')[0]+'>');h=dict(aa).get('href');links.append(dict(source_start=m.start(),source_end=m.end(),attrs=aa,literal_href=h,resolved_url=urljoin(url,h) if h else None,text=text(m[0])))
    scripts=[]
    for m in re.finditer(r'<script\b[^>]*>(.*?)</script\s*>',t,re.S|re.I):scripts.append(dict(source_start=m.start(),source_end=m.end(),attrs=attrs(m[0].split('>')[0]+'>'),body=m[1]))
    forms=[]
    for m in re.finditer(r'<(?:form|select)\b[^>]*>.*?</(?:form|select)\s*>',t,re.S|re.I):forms.append(dict(source_start=m.start(),source_end=m.end(),raw_html=m[0]))
    return dict(tables=tables,links=links,scripts=scripts,forms_and_selects=forms)
def main():
    sources=[]
    for p in sorted((R/'raw').glob('*.receipt.json')):
        m=load(p);sources.append(dict(source_id=m['id'],receipt=pin(p),body=pin(R/m['asset']),url=m.get('final_url'),status=m['status']))
        b=gzip.decompress((R/m['asset']).read_bytes());assert sha(b)==m['raw_sha256']
        if b.removeprefix(b'\xef\xbb\xbf').lstrip().startswith(b'<'):
            # Explicit UTF8: delcode falsely advertises UTF16 inside otherwise UTF8 HTML.
            t=b.decode('utf-8-sig');out=document(t,m.get('final_url') or m['requested_url']);out.update(source_id=m['id'],body=pin(R/m['asset']),decoded_encoding='utf-8-sig',native_current_IDs=None)
            write('extracts/'+m['id']+'.json.gz',out)
            (R/'extracts'/f'{m["id"]}.txt.gz').write_bytes(gzip.compress(re.sub(r'\s+',' ',text(t)).strip().encode(),mtime=0))
        elif b.startswith(b'%PDF'):
            with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
                f.write(b);f.flush();tx=subprocess.check_output(['pdftotext','-layout',f.name,'-'])
            (R/'extracts'/f'{m["id"]}.txt.gz').write_bytes(gzip.compress(tx,mtime=0))
        elif '.xlsx' in m['requested_url'].lower():
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                write('extracts/'+m['id']+'.json.gz',dict(source=pin(R/m['asset']),members=[dict(name=n,bytes=len(z.read(n)),sha256=sha(z.read(n)),full_xml=z.read(n).decode('utf-8') if n.endswith(('.xml','.rels')) else None)for n in z.namelist()],scope='All ZIP members retained in complete original; all XML/rels member strings retained without projections'))
        elif '.csv' in m['requested_url'].lower():
            rows=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));write('extracts/'+m['id']+'.json.gz',dict(header=rows[0],rows=rows[1:],all_columns_retained=True,source=pin(R/m['asset'])))
    historical=[]
    combined={x['id']:dict(id=x['id'],receipt=x) for x in load(R/'historical-auxiliary-receipts.json')}
    combined.update({x['id']:x for x in load(R/'historical-source-receipts.json')})
    for src in combined.values():
        p=S/'data/news'/src['receipt']['asset'];b=gzip.decompress(p.read_bytes());assert sha(b)==src['receipt']['raw_sha256']
        h=dict(id=src['id'],original=pin(p),receipt=src['receipt'],all_fields_retained=True)
        if b.startswith(b'%PDF'):
            with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
                f.write(b);f.flush();tx=subprocess.check_output(['pdftotext','-layout',f.name,'-'])
            (R/'extracts'/f'{src["id"]}.txt.gz').write_bytes(gzip.compress(tx,mtime=0))
            h.update(format='PDF',scope='Full original PDF; separate write-in sheets have no ED allocation')
        elif '.csv' in src['receipt']['url'].lower():
            rows=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));h.update(format='CSV',header=rows[0],rows=rows[1:])
        else:
            t=b.decode('utf-8-sig');h.update(format='HTML',**document(t,src['receipt'].get('final_url',src['receipt']['url'])))
        historical.append(h)
    write('extracts/historical-all-fields.json.gz',historical)
    write('source-index.json',sources)
    # Full current qualified AND declared rows, including non-Senate rows/blank cells.
    current=[]
    for sid,kind in [('candidates-current','qualified_observation'),('writeins-current','declared_observation')]:
        d=load(R/f'extracts/{sid}.json.gz');current.append(dict(source=sid,scope=kind,all_tables=d['tables'],current_vendor_choice_IDs=None,final_signed_later_exhaustiveness=False))
    write('extracts/current-candidate-literal-rows.json.gz',current)
    print('extracted',len(sources),'complete request entities and',len(historical),'immutable original historical sources')
if __name__=='__main__':main()
