#!/usr/bin/env python3
"""Extract complete PDF page/line text; image-only PDFs remain explicitly unparsed."""
import gzip,json,re,subprocess
from acquire import ROOT,SOURCE,dump,sha
from inspect_html import decode_body
out=[]
for f in sorted(SOURCE.glob('*.json')):
    m=json.loads(f.read_text())
    if not isinstance(m,dict) or 'body_path' not in m or not m.get('complete_response') or m.get('http_status')!=200:continue
    b=decode_body(m)
    if not b.startswith(b'%PDF'):continue
    p=subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True)
    sid=m['source_id'];(ROOT/'derived'/(sid+'.txt.gz')).write_bytes(gzip.compress(p.stdout,mtime=0))
    lines=[{'page':pi,'line':li,'text':line} for pi,page in enumerate(p.stdout.decode().split('\f'),1) for li,line in enumerate(page.splitlines(),1)]
    (ROOT/'derived'/(sid+'-lines.jsonl.gz')).write_bytes(gzip.compress(b''.join((json.dumps(l,ensure_ascii=False)+'\n').encode() for l in lines),mtime=0))
    out.append({'source_id':sid,'original_sha256':sha(b),'pages':p.stdout.count(b'\f'),'text_bytes':len(p.stdout),'nonwhitespace_text_chars':len(re.sub(r'\s','',p.stdout.decode())),'text_status':'image_only_or_unextractable' if len(re.sub(r'\s','',p.stdout.decode()))<40 else 'text_extracted_not_automatically_interpreted','text_path':'derived/'+sid+'.txt.gz'})
dump(ROOT/'document-extraction.json',out)
print(json.dumps(out,indent=2))
