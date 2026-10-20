"""Offline parsed-HTML DOM/order/identifier/link tests + actual filter JS in Node VM.
This is not a browser screenshot or claim of manual browser observation.
"""
from pathlib import Path
from html.parser import HTMLParser
import json,subprocess,urllib.parse,hashlib,tempfile
from collections import defaultdict
from build import ROOT,STATE,load,native,dumps
class DOM(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.details=[];self.current=None;self.pre=False;self.in_script=False;self.script='';self.links=[];self.ids=set()
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:assert a['id'] not in self.ids;self.ids.add(a['id'])
  if t=='details':
   assert self.current is None
   self.current={'attrs':a,'text':'','pre':''};self.details.append(self.current)
  if t=='pre':self.pre=True
  if t=='script':self.in_script=True
  if t=='a' and 'href' in a:self.links.append(a['href'])
  if t=='img':self.links.append(a['src'])
 def handle_endtag(self,t):
  if t=='details':self.current=None
  if t=='pre':self.pre=False
  if t=='script':self.in_script=False
 def handle_data(self,s):
  if self.current:self.current['text']+=s
  if self.current and self.pre:self.current['pre']+=s
  if self.in_script:self.script+=s

def parse(p):
 d=DOM()
 with p.open() as f:
  while chunk:=f.read(1000000):d.feed(chunk)
 d.close();return d

def run(write=False):
 c=load((STATE/'data/turnout/priority-set.json').read_bytes());full=c['full_order'];pr=set(c['ordered_priority_keys']);source=defaultdict(list)
 for p in sorted((ROOT/'originals').glob('native-page-*/receipt.json')):
  for f in load(native(p.parent.name)[0])['features']:source['05'+f['attributes']['county_fips']].append(f)
 main=parse(ROOT/'index.html');historic=[x for x in main.details if x['attrs']['data-kind'] in ['priority','remainder']];parents=[x for x in main.details if x['attrs']['data-kind']=='parent']
 assert [x['attrs']['data-key'] for x in historic]==[u['key'] for u in full]
 assert [x['attrs']['data-key'] for x in parents]==[p['key'] for p in c['all75parents']]
 for i,(el,u) in enumerate(zip(historic,full)):
  packet=load(el['pre']);assert packet['complete_historical_source_observation']==u and packet['own_source_context_reference']['pointer']=='/full_order/'+str(i)
 for el,p in zip(parents,c['all75parents']):assert load(el['pre'])==p
 contexts=[x for x in main.details if x['attrs']['data-kind']=='context']
 assert [x['attrs']['data-root'] for x in contexts]==[k for k in c if k not in ['full_order','all75parents']]
 for el in contexts:assert load(el['pre'])==c[el['attrs']['data-root']]
 results=[];total_links=0;parsed_targets={ROOT/'index.html':main}
 for p in [ROOT/'index.html']+[ROOT/'atlas'/(parent['county_fips']+'.html') for parent in c['all75parents']]:
  doc=main if p.name=='index.html' else parse(p)
  if p.name!='index.html':
   code=p.stem;rows=[x for x in doc.details if x['attrs']['data-kind'] in ['priority','remainder']];native_rows=[x for x in doc.details if x['attrs']['data-kind']=='GIS'];expected=[u for u in full if u['county_fips']==code]
   assert [x['attrs']['data-key'] for x in rows]==[u['key'] for u in expected]
   for x,u in zip(rows,expected):assert load(x['pre'])['complete_historical_source_observation']==u
   assert [int(x['attrs']['data-source-id']) for x in native_rows]==[f['attributes']['objectid'] for f in source[code]]
   for x,f in zip(native_rows,source[code]):assert load(x['pre'])['complete_native_source_feature']==f
  for href in doc.links:
   url=urllib.parse.urlsplit(href)
   if url.scheme:continue
   target=(p.parent/urllib.parse.unquote(url.path)).resolve()
   assert target.is_file(),('broken local link',str(p),href)
   if url.fragment:
    # Historical URL fragments are exact literal IDs after exactly one URL decode.
    if target not in parsed_targets:parsed_targets[target]=parse(target)
    assert urllib.parse.unquote(url.fragment) in parsed_targets[target].ids,('missing source identifier anchor',href)
   total_links+=1
  results.append({'page':str(p.relative_to(ROOT)),'detail_rows':len(doc.details),'local_links':len(doc.links),'all_original_detail_fields_retained':True})
 # Real atlas JS executes against parsed actual detail nodes, with minimal DOM API.
 # No live-browser claim: no browser surface is available in this session.
 nodes=[{'dataset':{'kind':x['attrs']['data-kind']},'textContent':x['text'],'hidden':False} for x in main.details]
 payload={'script':main.script,'nodes':nodes}
 js='''const fs=require('fs'),vm=require('vm');const d=JSON.parse(fs.readFileSync(0,'utf8'));const input={value:'',addEventListener(){}},scope={value:'all',addEventListener(){}},count={textContent:''};const document={querySelector(q){return ({'#search':input,'#scope':scope,'#count':count})[q]},querySelectorAll(q){if(q!=='details[data-kind]')throw Error('selector');return d.nodes},getElementById(){return null}};const ctx={document,location:{hash:''}};vm.createContext(ctx);vm.runInContext(d.script,ctx);const checks=[];for(const [kind,q,expected] of [['all','',2932],['priority','',1056],['remainder','',1785],['parent','',75],['context','',16],['priority','GRASSEY OUTSIDE',1],['priority','unavailable-NONMATCH-xyz',0]]){scope.value=kind;input.value=q;vm.runInContext('filter()',ctx);const n=d.nodes.filter(x=>!x.hidden).length;if(n!==expected||Number(count.textContent)!==expected)throw Error(JSON.stringify({kind,q,n,expected}));checks.push({kind,query:q,count:n});}process.stdout.write(JSON.stringify({status:'pass',scope:'actual atlas filter JavaScript executed against parsed actual HTML nodes; not a live browser',checks}));'''
 proc=subprocess.run(['node','-e',js],input=json.dumps(payload).encode(),capture_output=True)
 assert proc.returncode==0,proc.stderr.decode()
 filters=load(proc.stdout)
 # Safely escaped full source JSON is decoded by HTML parser, never interpreted as tags.
 from build import detail
 escaped=DOM();escaped.feed('<details data-kind="fixture">'+detail({'literal':'<script>& "\' </pre><img onerror=x>'})+'</details>')
 assert load(escaped.details[0]['pre'])=={'literal':'<script>& "\' </pre><img onerror=x>'} and not escaped.script
 proof={'status':'pass','pages':results,'exact_main_historical_order':2841,'priority':1056,'remainder':1785,'whole_parent_contexts':75,'complete_contract_roots':18,'whole_separate_native_GIS_objects':2928,'local_links_validated':total_links,'filter_JS_tests':filters,'safe_escaping_negative':True,'manual_browser_review':False,'browser_availability':'CUA createBrowserTab chrome returned Browser is not available; listBrowsers returned []; no live browser observation claimed.'}
 if write:(ROOT/'qa/atlas-proof.json').write_text(dumps(proof))
 else:assert load((ROOT/'qa/atlas-proof.json').read_bytes())==proof
 return proof
if __name__=='__main__':
 import sys
 p=run('--write' in sys.argv);print('Atlas DOM/fields/order/links/filter tests passed for',len(p['pages']),'pages')
