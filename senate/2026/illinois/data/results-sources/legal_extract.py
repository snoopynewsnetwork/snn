from common import *
class Marked(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=True);self.deleted=0;self.inserted=0;self.runs=[];self.feed(s)
 def handle_starttag(self,t,a):
  if t in ['strike','s','del']:self.deleted+=1
  if t in ['u','ins']:self.inserted+=1
  if t in ['tr','p','br']:self.runs.append(dict(text='\n',deleted=bool(self.deleted),inserted=bool(self.inserted)))
 def handle_endtag(self,t):
  if t in ['strike','s','del']:self.deleted-=1
  if t in ['u','ins']:self.inserted-=1
 def handle_data(self,d):self.runs.append(dict(text=d,deleted=bool(self.deleted),inserted=bool(self.inserted)))
def main():
 out=[]
 for id in ['law-ftp-104-0852','law-ftp-104-0434','law-ftp-104-0532','law-ftp-104-0695','law-hb1832-amendment']:
  m=parsefile(HERE/'receipts'/f'{id}.json');b=body(m)
  try:s=b.decode('utf8');encoding='UTF-8'
  except UnicodeDecodeError:s=b.decode('cp1252');encoding='Windows-1252 fallback, raw entity remains exact'
  marked=Marked(s);current=''.join(r['text'] for r in marked.runs if not r['deleted']);full=''.join(r['text'] for r in marked.runs)
  gzwrite(HERE/'text'/f'{id}-current-markup-applied.txt.gz',current.encode());gzwrite(HERE/'text'/f'{id}-all-marked-runs.json.gz',encode(marked.runs))
  targets=[]
  for section in ['2A-1','19-2','19-8','1A-50','1-21','1-23','1-9.1']:
   needle='Sec. '+section+'.';start=current.find(needle)
   if start<0:continue
   end=current.find('(Source:',start);end=current.find(')',end)+1 if end>=0 else -1
   if end>start:targets.append(dict(section=section,full_enacted_or_proposed_section_text=current[start:end],character_start=start,character_end=end,source_receipt=id,legal_role='proposed amendment only, not an operative rule' if 'amendment' in id else 'enacted public act; selected current text only, not complete later-law audit'))
  out.append(dict(receipt_id=id,encoding=encoding,full_current_text_path='data/results-sources/text/'+id+'-current-markup-applied.txt.gz',complete_marked_runs_path='data/results-sources/text/'+id+'-all-marked-runs.json.gz',sections=targets))
 write(HERE/'legal-source-sections.json',out)
 print([(x['receipt_id'],[s['section'] for s in x['sections']]) for x in out])
if __name__=='__main__':main()
