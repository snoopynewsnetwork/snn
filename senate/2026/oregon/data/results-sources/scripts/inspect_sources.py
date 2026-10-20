"""Whole-response structural inspection; extracted text is a derivative, never raw."""
from acquire import R,S,body
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import json,gzip,subprocess,tempfile,csv,io,re
class HTML(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=False);self.tokens=[];self.links=[];self.a=None;self.text=[];self.skip=0
 def handle_starttag(self,t,a):
  self.tokens.append(['start',self.getpos(),t,a]);d=dict(a)
  if t in ['script','style']:self.skip+=1
  if t=='a':self.a={'position':self.getpos(),'attributes':a,'href':d.get('href'),'label':''};self.links.append(self.a)
 def handle_startendtag(self,t,a):self.tokens.append(['empty',self.getpos(),t,a])
 def handle_endtag(self,t):
  self.tokens.append(['end',self.getpos(),t])
  if t in ['script','style']:self.skip=max(0,self.skip-1)
  if t=='a':self.a=None
 def handle_data(self,x):
  self.tokens.append(['data',self.getpos(),x])
  if self.a is not None:self.a['label']+=x
  if not self.skip and x.strip():self.text.append(x.strip())
 def handle_entityref(self,n):self.tokens.append(['entity',self.getpos(),n])
 def handle_charref(self,n):self.tokens.append(['charref',self.getpos(),n])
 def handle_comment(self,x):self.tokens.append(['comment',self.getpos(),x])
def inspect(rec):
 b=body(rec);o={'key':rec['key'],'source_request':'data/results-sources/requests/'+rec['key']+'.json','final_url':rec['final_url'],'error':rec['error'],'status':rec['entities'][-1]['status'] if rec['entities'] else None}
 if b.startswith(b'%PDF'):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'source.pdf';p.write_bytes(b)
   x=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True)
   info=subprocess.run(['pdfinfo',str(p)],capture_output=True)
  o.update(format='pdf',text=x.stdout.decode('utf8','replace'),extraction_error=x.stderr.decode(),pdfinfo=info.stdout.decode(),pdfinfo_error=info.stderr.decode(),pdf_final_EOF=b.rstrip().endswith(b'%%EOF'))
 else:
  charset=re.search(br'charset=[\"\']?([A-Za-z0-9_-]+)',b[:12000],re.I)
  encoding=charset.group(1).decode() if charset else 'utf8'
  try:s=b.decode(encoding,'replace')
  except LookupError:s=b.decode('utf8','replace')
  o['decoded_charset']=encoding
  if '<html' in s.lower()[:10000] or '<!doctype html' in s.lower()[:1000]:
   p=HTML();p.feed(s);p.close()
   for a in p.links:a['resolved_url']=urljoin(rec['final_url'],a['href'] or '')
   o.update(format='html',tokens=p.tokens,links=p.links,text='\n'.join(p.text))
  else:
   o.update(format='text',text=s)
   try:o.update(format='json',complete_object=json.loads(s))
   except ValueError:
    if s.startswith('ContestID,'):
     rows=list(csv.reader(io.StringIO(s,newline='')));o.update(format='csv_complete_rows_with_header',complete_rows=rows,field_counts=[len(row) for row in rows])
 p=R/'structures'/(rec['key']+'.json.gz');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress((json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0));return o
def main():
 for p in sorted((R/'requests').glob('*.json')):
  target=R/'structures'/(p.stem+'.json.gz')
  if not target.exists():o=inspect(json.loads(p.read_bytes()));print(p.stem,o['format'],o['status'])
if __name__=='__main__':main()
