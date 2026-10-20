"""Offline full-entity/newsroom configuration review; --seal writes self-only manifest."""
from pathlib import Path
import gzip,hashlib,json,re,sys,urllib.parse
H=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def packed(x):return (json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def pin(p):
 b=p.read_bytes();return {'path':p.name,'bytes':len(b),'sha256':sha(b)}
def original(name):
 r=json.loads((H/(name+'.receipt.json')).read_bytes())
 for hop in r['hops']:
  z=(H/hop['body_path']).read_bytes();b=gzip.decompress(z)
  assert sha(z)==hop['stored_sha256'] and len(z)==hop['stored_bytes']<40000000
  assert sha(b)==hop['raw_sha256'] and len(b)==hop['raw_bytes']<40000000
  assert hop['request_headers'] and hop['response_headers']
 return r,b
def run(seal=False):
 observations=[];raws={};hopcount=0
 for path in sorted(H.glob('*.receipt.json')):
  name=path.name.removesuffix('.receipt.json');r,b=original(name);assert r['status']==200
  assert r['requested_UTC'] and r['completed_UTC'];raws[name]=b
  observations.append({'id':name,'receipt':pin(path),'status':r['status'],'final_URL':r['final_url'],'complete_hops':len(r['hops']),'raw_bytes':len(b),'raw_SHA256':sha(b)})
  hopcount+=len(r['hops'])
 assert len(observations)==6 and hopcount==8
 # Verify source navigation instead of invented product paths.
 for parent,dest in [('wdbj-home','wdbj-results'),('wdbj-home','wdbj-state'),('wtvr-home','wtvr-politics'),('wtvr-politics','wtvr-guide')]:
  links=json.loads((H/(parent+'.election-links.json')).read_bytes());url=json.loads((H/(dest+'.receipt.json')).read_bytes())['requested_url'];assert url in {x['url'] for x in links}
 derived=[]
 for name in ['wdbj-home','wdbj-results']:
  text=raws[name].decode('utf-8');m=re.search(r'Fusion\.contentCache\s*=\s*',text);assert m
  cache,n=json.JSONDecoder().raw_decode(text[m.end():]);elections={k:v for k,v in cache.items() if k in ['gsync-elections','gsync-elections-featured']}
  assert elections and all('includeTestResults' in query for v in elections.values() for query in v)
  derived.append({'observation':name,'source_receipt':pin(H/(name+'.receipt.json')),'raw_entity_SHA256':sha(raws[name]),'Fusion_cache_character_start':m.end(),'Fusion_cache_character_end':m.end()+n,'complete_election_cache_objects':elections})
 result=derived[1]['complete_election_cache_objects']['gsync-elections'];assert len(result)==1
 query,container=next(iter(result.items()));data=container['data'];sel=data['selectedElection'];races=sel['races']
 assert json.loads(query)=={'arc-site':'wdbj','includeTestResults':False} and data['totalElections']==1
 assert sel['id']=='2713' and sel['name']=='2026 Virginia General Election' and sel['isActive'] is False
 assert len(races)==39 and sum(len(r['candidates']) for r in races)==143
 assert all(r['isTest'] is False for r in races) and all(c['votes']==0 for r in races for c in r['candidates'])
 senate=[r for r in races if r['name']=='U.S. Senate - Class II'];assert len(senate)==1 and senate[0]['id']=='61210'
 assert [(c['id'],c['name'],c['party'],c['votes']) for c in senate[0]['candidates']]==[('152650','Total Write-ins','Oth',0),('152651','Bert Mizusawa','R',0),('152652','Mark R. Warner','D',0)]
 featured=next(iter(derived[0]['complete_election_cache_objects']['gsync-elections-featured'].values()))['data'];assert featured['id'] is None and featured['races']==[] and featured['updatedDate'] is None
 guide=raws['wtvr-guide'].decode('utf-8');assert '2026 Election' in guide
 review={'status':'pass_bounded_primary_southwest_central_newsroom_scope_review','complete_requests':6,'complete_response_entities':8,'HTTP200_final_responses':6,'observations':observations,'WDBJ_literal_source_setup':{'selectedElection':sel['id'],'literal_name':sel['name'],'isActive':sel['isActive'],'includeTestResults':False,'all_races':39,'all_choices':143,'all_votes':0,'Senate_full_original_object':senate[0],'updatedDate':sel['updatedDate'],'dataTransformedAt':sel['dataTransformedAt'],'election_date_scope':'No separately established actual event-date field; title2026General is setup evidence, not sufficient November count admission.','upstream_supplier':'Gray GSync namespace observed; AP or independent count supplier not established from this bounded response.','measured_cadence':None},'WDBJ_home_featured_scope':featured,'WTVR_scope':'Current primary publisher politics category and linked2026voter guide retained as civic/counting context. Candidate/legal prose is newsroom evidence, not final official ballot/law verification; no numerical product or measured cadence established.','raw_definition':'Requests-decoded whole HTTP entities, not compressed wire frames. Configured/sent request headers, response headers/status/Location and every redirect body retained; UTC receipt-level request/completion clocks do not assert per-hop subsecond capture.','excluded_actions':'No candidate image, ad/social/account/contact/audio/video request, authentication/challenge bypass, browser/script execution, count ingestion, live collector or forecast.','current_official_choice_ID_native_geo_approval':False,'genuine_November_votes_or_measured_cadence':False,'old_news_manifest_or_worker_bytes_changed':False}
 outputs={'literal-election-cache.json':packed(derived),'review.json':packed(review)}
 for path,b in outputs.items():
  if seal:(H/path).write_bytes(b)
  else:assert (H/path).read_bytes()==b,path
 files=sorted(p for p in H.rglob('*') if p.is_file() and p!=H/'asset-manifest.json')
 for p in files:assert p.stat().st_size<40000000 and '__pycache__' not in p.parts
 manifest={'schema':'VA-bounded-primary-regional-news-v1','files':[{'path':str(p.relative_to(H)),**{k:v for k,v in pin(p).items() if k!='path'}} for p in files],'excludes_only':'asset-manifest.json','maximum':max(p.stat().st_size for p in files),'complete_files':len(files),'current_counts_or_geography_approved':False}
 if seal:(H/'asset-manifest.json').write_bytes(packed(manifest))
 else:assert json.loads((H/'asset-manifest.json').read_bytes())==manifest
 print(json.dumps({'status':review['status'],'requests':6,'hops':8,'files_excluding_manifest':len(files),'largest':manifest['maximum'],'no_count_admission':True}))
if __name__=='__main__':run('--seal' in sys.argv)
