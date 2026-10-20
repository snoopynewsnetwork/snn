"""Materialize full public response structures, not candidate-total projections.
HTML tables include every raw cell/attribute/blank; scripts remain original.
PDF text covers all pages and is explicitly an automated extract.
XLSX preserves complete XML member trees including cells/formulas/styles.
"""
from pathlib import Path
from xml.etree import ElementTree as ET
import csv,gzip,hashlib,io,json,re,subprocess,tempfile,zipfile
from bs4 import BeautifulSoup
O=Path(__file__).resolve().parent; S=O.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def out(name,v):
 p=O/'source/structures'/(name+'.json.gz');p.parent.mkdir(parents=True,exist_ok=True);z=gzip.compress(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode(),mtime=0);assert len(z)<40000000;p.write_bytes(z);return str(p.relative_to(O))
def xml(e):return dict(tag=e.tag,attributes=e.attrib,text=e.text,tail=e.tail,children=[xml(x)for x in e])
def main():
 index=[];seen=set()
 for f in sorted((O/'source/http').glob('*.json')):
  r=json.loads(f.read_text())
  if r.get('status')!=200 or not r.get('body'):continue
  h=r['body']['raw_sha256']
  if h in seen:continue
  seen.add(h);b=b''.join(gzip.decompress((O/part['path']).read_bytes())for part in r['body'].get('parts',[r['body']]));typ=r.get('headers',{}).get('Content-Type','').lower();v=dict(source_request=r['id'],url=r['requested_url'],original_body=r['body'])
  if b.startswith(b'%PDF'):
   with tempfile.TemporaryDirectory(prefix='ma-official-') as td:
    p=Path(td)/'source.pdf';p.write_bytes(b);q=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,timeout=90)
   txt=q.stdout.decode('utf-8','replace');v.update(format='PDF',extractor='pdftotext -layout, complete document; not visual inspection or OCR',returncode=q.returncode,stderr=q.stderr.decode('utf-8','replace'),text=txt,pages=txt.split('\f'),nonempty_text_characters=len(txt.strip()),scanned_or_extraction_gap=not bool(txt.strip()))
  elif b.startswith(b'PK') and ('spreadsheet'in typ or '.xlsx'in r['requested_url'].lower()):
   z=zipfile.ZipFile(io.BytesIO(b));members=[]
   for n in z.namelist():
    raw=z.read(n)
    if n.endswith(('.xml','.rels')):
     try:tree=xml(ET.fromstring(raw));error=None
     except Exception as e:tree=None;error=str(e)
     members.append(dict(name=n,bytes=len(raw),sha256=sha(raw),tree=tree,error=error))
    else:members.append(dict(name=n,bytes=len(raw),sha256=sha(raw),binary_retained_in_original=True))
   v.update(format='XLSX',members=members,blank_rule='Present empty cells/elements retained; absent cells remain absent, never converted to zero; shared strings/formulas/styles retained without invented recalculation')
  elif b.lstrip().startswith((b'{',b'[')):
   try:
    value=json.loads(b);nested=[]
    def walk(x,pointer=''):
     if isinstance(x,dict):
      for k,z in x.items():walk(z,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))
     elif isinstance(x,list):
      for i,z in enumerate(x):walk(z,pointer+'/'+str(i))
     elif isinstance(x,str)and '<table'in x.lower():
      d=BeautifulSoup(x,'html.parser');nested.append(dict(pointer=pointer,tables=[[[dict(tag=c.name,attributes=dict(c.attrs),raw_text=c.get_text())for c in row.find_all(['th','td'],recursive=False)]for row in t.find_all('tr')]for t in d.find_all('table')]))
    walk(value);v.update(format='JSON',complete_response=value,all_nested_HTML_tables=nested)
   except Exception as e:v.update(format='unparsed JSON-like',error=str(e))
  elif 'javascript'in typ or r['requested_url'].endswith('.js'):
   t=b.decode('utf-8','replace');v.update(format='JavaScript',complete_text=t,observed_calls=[dict(offset=m.start(),context=t[max(0,m.start()-120):m.end()+300]) for m in re.finditer(r'fetch\s*\(|XMLHttpRequest|\.ajax\s*\(|setInterval\s*\(|DataTable\s*\(|(?:config|constructor)\s*[:=(]',t)])
  elif 'html'in typ or b.lstrip().startswith(b'<'):
   s=BeautifulSoup(b,'html.parser');tables=[]
   for i,table in enumerate(s.find_all('table'),1):
    rows=[]
    for j,row in enumerate(table.find_all('tr'),1):rows.append(dict(ordinal=j,attributes=dict(row.attrs),cells=[dict(ordinal=k,tag=x.name,attributes=dict(x.attrs),raw_text=x.get_text(),text=x.get_text(' ',strip=True)) for k,x in enumerate(row.find_all(['th','td'],recursive=False),1)]))
    tables.append(dict(ordinal=i,attributes=dict(table.attrs),caption=table.caption.get_text()if table.caption else None,rows=rows))
   scripts=[]
   for i,x in enumerate(s.find_all('script'),1):
    t=x.get_text();scripts.append(dict(ordinal=i,attributes=dict(x.attrs),inline_text=t,observed_calls=[dict(offset=m.start(),context=t[max(0,m.start()-120):m.end()+300])for m in re.finditer(r'fetch\s*\(|XMLHttpRequest|\.ajax\s*\(|setInterval\s*\(|DataTable\s*\(|(?:config|constructor)\s*[:=(]',t)]))
   v.update(format='HTML',tables=tables,scripts=scripts,forms=[dict(attributes=dict(f.attrs),fields=[dict(tag=x.name,attributes=dict(x.attrs),text=x.get_text())for x in f.find_all(['input','select','option','button','textarea'])])for f in s.find_all('form')],meta=[dict(x.attrs)for x in s.find_all('meta')],blank_rule='Exact raw text retained separately from stripped text; absent fields unknown, source blanks preserved')
  else:v.update(format=typ or 'unknown',unparsed_full_original_retained=True)
  path=out(h,v);index.append(dict(source_request=r['id'],url=r['requested_url'],body_sha256=h,structure=path,format=v['format']))
 # Freeze individual historical acquisition receipts without any dependency on
 # a mutable newsroom receipt aggregate. Original body paths remain read-only.
 receipts=json.loads((S/'data/turnout/source/shared-originals.json').read_text());(O/'source/reused-original-receipts.json').write_text(json.dumps(receipts,indent=2,ensure_ascii=False)+'\n')
 csvsamples=[]
 for r in receipts:
  if not r['id'].endswith('-csv'):continue
  z=(S/r['immutable_body_path']).read_bytes();b=gzip.decompress(z);assert sha(b)==r['raw_sha256'];rows=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));v=dict(format='CSV',source_id=r['id'],receipt=r,all_records_including_ragged_headers_party_rows_blanks_and_footer=rows,record_lengths=[len(x)for x in rows],columns=[dict(column_1based=i+1,literal_header=h,party_raw=rows[1][i]if i<len(rows[1])else None,party_position_exists=i<len(rows[1]))for i,h in enumerate(rows[0])],blank_rule='An absent ragged party cell is distinct from present empty string; no synthetic numeric IDs/methods/control rows')
  path=out('original-'+r['id'],v);csvsamples.append(dict(source_id=r['id'],structure=path,body_path=r['immutable_body_path'],complete_records=len(rows)))
 (O/'structure-index.json').write_text(json.dumps(dict(responses=index,historical_csv=csvsamples),indent=2)+'\n');print(dict(responses=len(index),formats={k:sum(r['format']==k for r in index)for k in sorted({r['format']for r in index})},complete_original_CSVs=len(csvsamples)))
if __name__=='__main__':main()
