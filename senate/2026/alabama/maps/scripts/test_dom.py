"""Complete HTML DOM/source-object checks and actual embedded JS execution in Node."""
from pathlib import Path
from html.parser import HTMLParser
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];S=ROOT.parent
class DOM(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.details=None;self.pre=False;self.text='';self.units=[];self.parents=[];self.roots={};self.features=[];self.attrs=[];self.scripts=[];self.inscript=False;self.script='';self.urls=[];self.options=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='details':self.details=d
  if t=='pre':self.pre=True;self.text=''
  if t=='script':self.inscript=True;self.script=''
  for k in ['src','href']:
   if k in d:self.urls.append(d[k])
 def handle_data(self,s):
  if self.pre:self.text+=s
  if self.inscript:self.script+=s
 def handle_endtag(self,t):
  if t=='pre':
   self.pre=False;d=self.details or {};c=d.get('class');v=json.loads(self.text)
   if c=='unit':self.units.append(v);self.attrs.append(d)
   elif c=='parent':self.parents.append(v)
   elif c=='root-context':self.roots[d['data-root']]=v
   elif c=='native-feature':self.features.append(v)
  if t=='details':self.details=None
  if t=='script':self.inscript=False;self.scripts.append(self.script)
def run():
 p=DOM();p.feed((ROOT/'index.html').read_text());c=json.loads((S/'data/turnout/priority-set.json').read_bytes());parents=json.loads((ROOT/'county-investigations.json').read_bytes())
 assert p.units==c['units'] and p.parents==parents and p.roots=={k:v for k,v in c.items() if k not in ['units','parents']}
 assert len(p.attrs)==2085 and len({r['id'] for r in p.attrs})==2085
 assert [r['data-key'] for r in p.attrs]==c['full_order']
 assert [r['data-key'] for r in p.attrs if r['data-tier']=='priority']==c['ordered_priority_keys']
 assert [r['data-key'] for r in p.attrs if r['data-tier']=='remainder']==c['remainder_keys']
 assert len(p.scripts)==1 and len(p.features)==157
 for u in p.urls:
  assert not u.lower().startswith(('javascript:','data:text','//'))
  if not u.startswith(('http://','https://','#')):assert (ROOT/u.split('#')[0].split('?')[0]).exists(),u
 tests=[{'url':'http://offline.test/maps/index.html','count':2085},{'url':'http://offline.test/maps/index.html?tier=priority','count':887},{'url':'http://offline.test/maps/index.html?tier=remainder','count':1198},{'url':'http://offline.test/maps/index.html?q=OAK%20GROVE%20BAPT','count':sum('oak grove bapt' in (u['key']+' '+u['county']+' '+u['native_label']).lower() for u in c['units'])},{'url':'http://offline.test/maps/index.html?county=99999&tier=invalid','count':2085}]
 for pp in parents:
  f=pp['county_fips']
  for tier in ['','priority','remainder']:
   tests.append({'url':'http://offline.test/maps/index.html?county='+f+'&tier='+tier,'count':len(pp['ordered_source_rank_children'] if not tier else pp['ordered_'+tier+'_children'])})
 tests.append({'url':'http://offline.test/maps/index.html?q=%3C%2Fscript%3E%3Cimg%20onerror%3Dalert(1)%3E','count':0})
 script="""const fs=require('node:fs'),vm=require('node:vm');const input=JSON.parse(fs.readFileSync(0,'utf8'));let results=[];for(const test of input.tests){let location={href:test.url};const elements={county:{value:'',options:input.counties.map(value=>({value})),addEventListener(){}},tier:{value:'',addEventListener(){}},query:{value:'',addEventListener(){}},count:{textContent:''}};const rows=input.rows.map(a=>({dataset:{county:a['data-county'],tier:a['data-tier'],search:a['data-search'],key:a['data-key']},hidden:false}));let replacement;const sandbox={URL,location,document:{getElementById:id=>elements[id],querySelectorAll:selector=>{if(selector!=='details.unit')throw Error('unexpected selector');return rows}},history:{replaceState:(s,t,u)=>replacement=String(u)}};vm.createContext(sandbox);vm.runInContext(input.script,sandbox);const got=rows.filter(r=>!r.hidden).length;if(got!==test.count)throw Error(JSON.stringify({test,got}));if(elements.count.textContent!==`${got} of 2085 contexts`)throw Error('counter');results.push({url:test.url,count:got,storedURL:replacement});}process.stdout.write(JSON.stringify({status:'PASS',cases:results.length,results}));"""
 data={'script':p.scripts[0],'rows':p.attrs,'counties':['']+[pp['county_fips'] for pp in parents],'tests':tests};result=subprocess.run(['node','-e',script],input=json.dumps(data).encode(),capture_output=True);assert result.returncode==0,result.stderr.decode();j=json.loads(result.stdout)
 out={'status':'PASS','complete_native_objects':2085,'complete_parents_with_investigations':67,'complete_other_root_contexts':len(p.roots),'complete_native_service_objects':len(p.features),'exact_orders':True,'escaped_source_objects':True,'relative_links':True,'JavaScript_filter_count_URL_tests':j,'execution_scope':'Entire generated HTML parsed with Python HTMLParser; actual embedded JS executed by Node vm against minimal DOM elements populated from complete parsed attributes. CUA reported no available browser; no browser visual/DOM execution claim.'};print(json.dumps(out,indent=2))
if __name__=='__main__':run()
