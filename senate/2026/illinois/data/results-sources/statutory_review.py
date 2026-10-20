from common import *
from legal_extract import Marked

def main():
 out=[]
 for x in parsefile(HERE/'statutory-section-request-plan.json'):
  m=parsefile(HERE/'receipts'/f"{x['id']}.json");b=body(m)
  try:s=b.decode('utf8');encoding='UTF-8'
  except UnicodeDecodeError:s=b.decode('cp1252');encoding='Windows-1252'
  h=HTML(s);t=' '.join(h.text);out.append(dict(section=x['section'],receipt_id=m['id'],source_url=m['url'],encoding=encoding,complete_text=t,source_notes=re.findall(r'\(Source:.*?\)',t,re.S),future_effective_text_must_be_checked=True))
 write(HERE/'operative-statutes-complete.json',out)
 print('complete code sections',len(out))
 for x in out:
  if x['section'] in ['1-9.1','1-9.2','17-1','18A-15','19-8','19A-15','19A-25','22-7','22-9.1','23-1.1a','23-2','23-3','23-4','23-5','23-20']:
   print('\nSECTION',x['section']);print(re.sub(r'\s+',' ',x['complete_text']))
if __name__=='__main__':main()
