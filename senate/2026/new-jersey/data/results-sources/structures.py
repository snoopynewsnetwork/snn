"""Full structure derivatives: no source field projection or source repair."""
from pathlib import Path
import json,gzip,hashlib,csv,io,xml.etree.ElementTree as ET
import sys
sys.dont_write_bytecode=True
import fitz
from inspect_pages import body,Page
P=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,obj):
 b=(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:list(x) if isinstance(x,(fitz.Rect,fitz.Point,fitz.Quad)) else str(x))+'\n').encode();z=gzip.compress(b,mtime=0);assert len(z)<40000000;(P/'structures'/name).write_bytes(z)
def schema(v,p=''):
 yield {'pointer':p,'type':type(v).__name__,'length':len(v) if isinstance(v,(list,dict,str)) else None,'null':v is None}
 if isinstance(v,dict):
  for k,x in v.items():yield from schema(x,p+'/'+k.replace('~','~0').replace('/','~1'))
 elif isinstance(v,list):
  for i,x in enumerate(v):yield from schema(x,p+'/'+str(i))
def main():
 (P/'structures').mkdir(exist_ok=True);index=[];done={}
 for f in sorted((P/'requests').glob('*.json')):
  r=json.loads(f.read_bytes())
  if not r.get('hops'):continue
  b=body(r);h=sha(b);item={'request_id':r['id'],'raw_sha256':h,'status':r['status']}
  if h in done:item.update(done[h]);index.append(item);continue
  kind=None;target=None
  if b.startswith(b'%PDF'):
   doc=fitz.open(stream=b,filetype='pdf');obj={'format':'complete PyMuPDF text/words on every page; originals definitive; no visual-view claim','metadata':doc.metadata,'page_count':len(doc),'pages':[{'page':i+1,'rectangle':list(pg.rect),'rotation':pg.rotation,'text':pg.get_text(),'words':pg.get_text('words'),'links':pg.get_links()} for i,pg in enumerate(doc)]};kind='PDF_all_pages';target=h+'.pdf-pages.json.gz';write(target,obj)
  else:
   try:v=json.loads(b);kind='JSON_complete_recursive_schema';target=h+'.json-schema.json.gz';write(target,{'schema':list(schema(v))})
   except (ValueError,UnicodeDecodeError):
    if r['final_url'].split('?')[0].endswith('.csv'):
     try:v=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));kind='CSV_all_rows_all_fields';target=h+'.csv-rows.json.gz';write(target,{'all_rows':v,'row_lengths':[len(x) for x in v]})
     except UnicodeDecodeError:pass
    elif r['final_url'].split('?')[0].endswith('.xml'):
     try:v=ET.fromstring(b);kind='XML_complete_recursive_tree';target=h+'.xml-tree.json.gz'
     except ET.ParseError:v=None
     if v is not None:
      def tree(x):return {'tag':x.tag,'attributes':dict(x.attrib),'text':x.text,'tail':x.tail,'children':[tree(c) for c in x]}
      write(target,tree(v))
  item.update(kind=kind,structure_asset='structures/'+target if target else None);done[h]={k:item[k] for k in ['kind','structure_asset']};index.append(item)
 (P/'structure-index.json').write_text(json.dumps(index,indent=2)+'\n');print('requests',len(index),'unique',len(done),'structured',sum(bool(x.get('kind')) for x in index))
if __name__=='__main__':main()
