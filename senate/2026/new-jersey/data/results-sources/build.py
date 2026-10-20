"""Deterministic official-source inventory and full575/233/342/21 products from exact originals."""
from pathlib import Path
from urllib.parse import urljoin
from collections import Counter
import json,gzip,re,html,csv,hashlib,sys
sys.dont_write_bytecode=True
from inspect_pages import body,inspect
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def load(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def write(n,v):
 b=(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 if n.endswith('.gz'):b=gzip.compress(b,mtime=0)
 assert len(b)<40000000; (P/n).write_bytes(b)
def plain(s):return html.unescape(re.sub('<[^>]*>',' ',s)).strip()
def slim(r):return {'request_id':r['id'],'receipt':'requests/'+r['id']+'.json','requested_url':r['requested_url'],'final_url':r.get('final_url'),'retrieved_at_utc':r['finished_utc'],'status':r.get('status'),'error':r.get('error'),'whole_hops':[{'status':h['status'],'response_url':h['response_url'],'raw_sha256':h['raw_sha256'],'raw_bytes':h['raw_bytes'],'headers':h['headers'],'asset':h.get('asset'),'reference_path':h.get('reference_path'),'ordered_exact_entity_parts':h.get('ordered_exact_entity_parts')} for h in r['hops']]}
def main():
 c=load(ROOT/'data/turnout/priority-set.json');assert len(c['all_units'])==575
 req={f.stem:load(f) for f in (P/'requests').glob('*.json')};directory=req['state-directory-public'];s=body(directory).decode();authorities=[]
 for block in re.split(r'<div class="card">',s)[1:]:
  m=re.search(r'<div class="card-header">.*?<a[^>]*>(.*?)</a>',block,re.S)
  if not m:continue
  county=plain(m[1]).replace(' County','');roles=[]
  for col in re.split(r'<div class="col-sm-4"[^>]*>',block)[1:]:
   col=col.split('</div>',1)[0];active=re.sub(r'<!--.*?-->','',col,flags=re.S);mh=re.search(r'<strong>(.*?)</strong>',active,re.S);role=plain(mh[1]) if mh else None
   lines=[plain(x) for x in re.split(r'<br\s*/?>',active,flags=re.I)];prefix=active[mh.end():active.find('Address:')] if mh and 'Address:' in active else '';name=re.sub(r'\s+',' ',plain(prefix)).strip() or None
   ls=[{'literal_href':html.unescape(h),'resolved_url':urljoin(directory['final_url'],html.unescape(h)),'label_raw_html':t,'label':plain(t)} for h,t in re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',active,re.S|re.I)]
   roleobj={'role_literal':role,'name_literal':name,'address_lines':[x for x in lines if 'Address:' in x],'office_hour_lines':[x for x in lines if 'Office Hours:' in x],'all_phone_fax_tokens':re.findall(r'\b\d{3}[-.]\d{3}[-.]\d{4}\b',plain(active)),'email_tokens':re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',plain(active)),'links':ls,'complete_lines':lines,'raw_column_html':col,'full_text':plain(col),'source_request_id':directory['id'],'blank_name':name is None,'blank_email':not bool(re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',plain(active))),'blank_link':not bool(ls)}
   roles.append(roleobj)
  authorities.append({'county':county,'county_fips':next(u['county_fips'] for u in c['all_units'] if u['county']==county),'roles':roles,'directory_last_updated_literal':'10/06/26','source_request_id':directory['id']})
 assert len(authorities)==21 and all(len(r['roles'])==3 for r in authorities);write('authorities.json',authorities)
 parents=[];unitpub={};native=load(ROOT/'data/baselines/extract/native-contests.json')
 for pub in native['2024-senate']:
  for row in pub['rows']:unitpub[row['key']]={'original_complete_row':row,'full_candidates':pub['candidates'],'all_page_headers':pub['headers'],'column_right_edges':pub['column_right_edges'],'nonadditive_footer':pub['footer']}
 claims=load(P/'county-findings.json') if (P/'county-findings.json').exists() else {}
 schemaidx={x['request_id']:x for x in load(P/'structure-index.json')}
 domidx={x['request_id']:x for x in load(P/'complete-dom-index.json')}
 # Assignment follows original directory roots, explicit county URLs, and the actual parent graph.
 assignment={}
 for a in authorities:
  slug=a['county'].lower().replace(' ','');ids=set()
  for n,r in req.items():
   u=re.sub('[^a-z]','',(r.get('final_url') or r['requested_url']).lower())
   if n.startswith(slug+'-') or slug in u and ('state-nav-61' in n or 'periodic' in n):ids.add(n)
  for _ in range(15):
   more={n for n,r in req.items() if r.get('parent') in ids};old=len(ids);ids|=more
   if len(ids)==old:break
  assignment[a['county']]=ids
 for a in authorities:
  county=a['county'];fips=a['county_fips'];us=[u for u in c['all_units'] if u['county_fips']==fips];ids=assignment[county];obs=[slim(req[n]) for n in sorted(ids)];complete_parent=next(p for p in c['county_coverage'] if p['county_fips']==fips)
  payloads=[];text_evidence=[]
  for n in sorted(ids):
   r=req[n]
   if not r.get('hops'):continue
   info=schemaidx.get(n)
   if info and info.get('kind'):payloads.append(info)
   if n in domidx:payloads.append(domidx[n])
   o=inspect(r)
   if o:
    text=o['full_text'];matches=list(re.finditer(r'(?i)unofficial|certif|remaining|counted|privacy|update|periodic|election night|general election|primary election',text));text_evidence.extend({'request_id':n,'text_start':m.start(),'text_end':min(len(text),m.end()+200),'literal_context':text[max(0,m.start()-100):m.end()+200]} for m in matches)
  parent={'parent_key':fips,'county':county,'authority_directory':a,'canvass_actor':{'role':'Board of County Canvassers','composition':'county board of elections acts as board; county clerk is clerk of board','statute':'19:6-26','county_meeting_statute':'19:19-1','scope':'nonadditive county canvass/correction authority distinct from public ENR publisher'},'historical_complete_parent':complete_parent,'source_ordered_children':[u['key'] for u in sorted(us,key=lambda u:(u['source_id'],u['page'],u['line']))],'rank_ordered_children':[u['key'] for u in us],'priority_children':[u['key'] for u in us if u['in_minimum80']],'remainder_children':[u['key'] for u in us if not u['in_minimum80']],'actual_bounded_public_requests':obs,'complete_structural_payloads':payloads,'findings':claims.get(county,{}),'published_release_plan_evidence':'release-plan-'+fips+'.json.gz','measured_candidate_publication_cadence':None,'November_accepted_unprocessed_eligible_pool':None,'genuine_November_counts_admitted':False,'current_choice_reporting_or_leaf_match_approved':False,'shared_parent_not_independent_leaf_feed':True}
  parents.append(parent)
  write('release-plan-'+fips+'.json.gz',text_evidence)
 write('county-investigations.json.gz',parents)
 pm={p['parent_key']:p for p in parents};allunits=[]
 for u in c['all_units']:
  allunits.append({'key':u['key'],'rank':u['rank'],'priority':u['in_minimum80'],'historical_complete_unit':u,'historical_complete_candidate_publication_context':unitpub[u['key']],'shared_parent_key':u['county_fips'],'shared_parent_resource':'county-investigations.json.gz','historical_original_reference_index':'../baselines/source/original-references.json','source_scope':'2024 six named candidate municipal/admin publication observation; no November identity or finest precinct inference','current_leaf_reporting_ID':None,'current_candidate_choice_IDs':None,'current_unit_method_crosswalk':None,'genuine_November_counts_admitted':False})
 write('all575-investigations.json.gz',allunits);write('priority233-investigations.json.gz',[{**u,'complete_shared_parent_investigation':pm[u['shared_parent_key']]} for u in allunits[:233]]);write('remainder342-investigations.json.gz',[{**u,'complete_shared_parent_investigation':pm[u['shared_parent_key']]} for u in allunits[233:]])
 write('full21-hierarchy.json.gz',{'authority_path':'../coordinator-priority-acceptance.json','historical_scope':c['universe'],'historical_hierarchy_literal':c['hierarchy'],'ordered_priority_parent_FIPS':list(dict.fromkeys(u['shared_parent_key'] for u in allunits[:233])),'source_parent_FIPS':[p['parent_key'] for p in parents],'all_ordered_keys':[u['key'] for u in allunits],'priority_ordered_keys':[u['key'] for u in allunits[:233]],'remainder_ordered_keys':[u['key'] for u in allunits[233:]],'full_parents':parents,'historical_full_root_fields_path':'../turnout/priority-set.json','no_current_geographic_or_leaf_crosswalk':True})
 write('request-index.json',{'requests':[{'request_id':n,'receipt':'requests/'+n+'.json','receipt_bytes':(P/'requests'/f'{n}.json').stat().st_size,'receipt_sha256':hashlib.sha256((P/'requests'/f'{n}.json').read_bytes()).hexdigest()} for n in sorted(req)],'admitted_November_votes':False,'observations_are_bounded_research_not_collector':True})
 fields=['state','county','county_fips','authority_role','name_literal','address_lines_json','office_hours_json','phone_fax_json','email_json','website_links_json','complete_raw_lines_json','raw_column_html','blank_name','blank_email','blank_link','source_request','canvass_role_statutes','shared_parent_key','inspection_request_ids_json','release_plan','measured_cadence','exact_eligible_unprocessed_pool','November_counts_admitted']
 rows=[]
 for a in authorities:
  for role in a['roles']:
   rows.append({'state':'NJ','county':a['county'],'county_fips':a['county_fips'],'authority_role':role['role_literal'],'name_literal':role['name_literal'],'address_lines_json':json.dumps(role['address_lines'],ensure_ascii=False),'office_hours_json':json.dumps(role['office_hour_lines'],ensure_ascii=False),'phone_fax_json':json.dumps(role['all_phone_fax_tokens']),'email_json':json.dumps(role['email_tokens']),'website_links_json':json.dumps(role['links'],ensure_ascii=False),'complete_raw_lines_json':json.dumps(role['complete_lines'],ensure_ascii=False),'raw_column_html':role['raw_column_html'],'blank_name':role['blank_name'],'blank_email':role['blank_email'],'blank_link':role['blank_link'],'source_request':directory['id'],'shared_parent_key':a['county_fips'],'inspection_request_ids_json':json.dumps(sorted(assignment[a['county']])),'release_plan':'county-findings.json and per-parent full release-plan evidence','November_counts_admitted':False})
  rows.append({'state':'NJ','county':a['county'],'county_fips':a['county_fips'],'authority_role':'Board of County Canvassers','canvass_role_statutes':'19:6-26;19:19-1 through 19:19-25','source_request':'law-context-66;law-context-67','shared_parent_key':a['county_fips'],'release_plan':'statutory canvass; no measured ENR cadence','November_counts_admitted':False})
 rows.extend([{'state':'NJ','authority_role':'Division of Elections / Secretary of State','name_literal':'Shirley U. Emehelu, Acting Secretary of State','complete_raw_lines_json':json.dumps([x for x in inspect(directory)['full_text'].splitlines() if any(t in x for t in ['Shirley','Mailing Address','Office Address','P.O. Box 304','225 West State','609-','nj.elections@sos.nj.gov','TTY/TDD','1-877-'])],ensure_ascii=False),'raw_column_html':s[max(0,s.rfind('Mailing Address')-200):s.rfind('Mailing Address')+1700],'source_request':'state-directory-public;state-results-public','address_lines_json':json.dumps(['Mailing: P.O. Box 304, Trenton, NJ 08625-0304','Office: 225 West State Street, 1st Floor, Trenton, NJ 08608']),'phone_fax_json':json.dumps(['609-292-3760','609-789-0124','609-777-1280','609-292-0034','1-877-658-6837']),'email_json':json.dumps(['nj.elections@sos.nj.gov']),'website_links_json':json.dumps(['https://nj.gov/state/elections/election-results.shtml']),'release_plan':'state does not post running election-night results; separate periodic reports','November_counts_admitted':False},{'state':'NJ','authority_role':'Board of State Canvassers','source_request':'law-context-66;law-context-68','canvass_role_statutes':'19:6-27;19:21;19:22-6;19:22-7','release_plan':'state canvass no later than30th day; no measured candidate publication cadence','November_counts_admitted':False}])
 with (ROOT/'data/official-results-sources.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 print({'authorities':len(rows),'county_parents':len(parents),'priority':233,'remainder':342,'all':len(allunits),'requests':len(req)})
if __name__=='__main__':main()
