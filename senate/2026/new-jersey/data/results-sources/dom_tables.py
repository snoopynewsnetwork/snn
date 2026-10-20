"""All original HTML table/row/cell fields; ordered source offsets, no vote-only projection."""
from pathlib import Path
from html.parser import HTMLParser
import json,gzip,re,sys
sys.dont_write_bytecode=True
from inspect_pages import body
P=Path(__file__).resolve().parent
class Attr(HTMLParser):
 def __init__(self):super().__init__();self.attrs=[]
 def handle_starttag(self,t,a):self.attrs=a
def attributes(s):
 p=Attr();p.feed(s);return p.attrs
def main():
 out=[];seen={}
 for f in sorted((P/'requests').glob('*.json')):
  r=json.loads(f.read_bytes())
  if not r.get('hops') or 'livevoterturnout.com/ENR/' not in r.get('final_url','') or not r['final_url'].split('?')[0].endswith('.html'):continue
  b=body(r);rawsha=r['hops'][-1]['raw_sha256']
  if rawsha in seen:out.append({'request_id':r['id'],'raw_sha256':rawsha,'structure_asset':seen[rawsha]});continue
  s=b.decode('utf-8-sig','replace');tables=[]
  for m in re.finditer(r'<table\b([^>]*)>.*?</table\s*>',s,re.S|re.I):
   table=m[0];rows=[]
   for rm in re.finditer(r'<tr\b([^>]*)>.*?</tr\s*>',table,re.S|re.I):
    row=rm[0];cells=[]
    for cm in re.finditer(r'<(td|th)\b([^>]*)>(.*?)</\1\s*>',row,re.S|re.I):cells.append({'tag':cm[1],'attributes':attributes('<'+cm[1]+cm[2]+'>'),'start_character_offset':m.start()+rm.start()+cm.start(),'end_character_offset':m.start()+rm.start()+cm.end(),'complete_inner_html':cm[3]})
    rows.append({'attributes':attributes('<tr'+rm[1]+'>'),'start_character_offset':m.start()+rm.start(),'end_character_offset':m.start()+rm.end(),'complete_raw_html':row,'cells':cells})
   tables.append({'attributes':attributes('<table'+m[1]+'>'),'start_character_offset':m.start(),'end_character_offset':m.end(),'complete_raw_html':table,'all_rows':rows})
  name='structures/'+rawsha+'.full-dom-tables.json.gz';z=gzip.compress((json.dumps({'raw_sha256':rawsha,'offset_encoding':'decodedUTF8characters','complete_tables':tables},ensure_ascii=False,indent=2)+'\n').encode(),mtime=0);assert len(z)<40000000;(P/name).write_bytes(z);seen[rawsha]=name;out.append({'request_id':r['id'],'raw_sha256':rawsha,'structure_asset':name,'table_count':len(tables)})
 (P/'complete-dom-index.json').write_text(json.dumps(out,indent=2)+'\n');print('DOMobservations',len(out),'uniquecompleteHTML',len(seen))
if __name__=='__main__':main()
