"""Offline complete primary-publisher/widget source retention and scope audit."""
from pathlib import Path
import json,gzip,hashlib,re,html
H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=p.name,bytes=len(b),sha256=sha(b))
def main():
 observations=[];sources={}
 for p in sorted(H.glob('*.receipt.json')):
  r=json.loads(p.read_bytes());assert r['status']==200 and r['requested_UTC'] and r['completed_UTC']
  for hop in r['hops']:
   z=(H/hop['body_path']).read_bytes();b=gzip.decompress(z);assert (len(z),sha(z))==(hop['stored_bytes'],hop['stored_sha256']);assert (len(b),sha(b))==(hop['raw_bytes'],hop['raw_sha256']);assert hop['request_headers'] and hop['response_headers']
  s=b.decode('utf-8','replace');sources[r['id']]=s;title=re.search(r'<title[^>]*>(.*?)</title>',s,re.S|re.I)
  observations.append(dict(id=r['id'],receipt=pin(p),url=r['final_url'],status=r['status'],title=html.unescape(title[1]) if title else None,raw_bytes=len(b),raw_sha256=sha(b)))
 assert len(observations)==4
 assert any(r['literal_href']=='/politics/election-results' for r in json.loads((H/'wymt-home.election-links.json').read_text()))
 assert 'fullResultsKickerDestinationUri":"/politics/election-results/' in sources['wbko-home']
 widgets=[]
 for name,expected,races in [('wbko-results','2403',173),('wymt-results','2078',135)]:
  s=sources[name];cache,_=json.JSONDecoder().raw_decode(s.split('Fusion.contentCache=',1)[1]);full={k:v for k,v in cache.items() if 'election' in k};p=H/(name+'-complete-embedded-election-cache.json');p.write_text(json.dumps(full,indent=2,ensure_ascii=False,allow_nan=False)+'\n');d=next(iter(full['gsync-elections'].values()))['data'];e=d['selectedElection'];assert e['id']==expected and not e['isActive'] and 'Primary' in e['name'] and len(e['races'])==races
  query=next(iter(full['gsync-elections']));assert json.loads(query)['includeTestResults'] is False
  at=s.index('displayTestData');context=s[at-80:at+100];assert 'displayTestData":true' in context.replace(chr(92),'')
  senate=[r for r in e['races'] if r['name'].startswith('U.S. Senate')];assert len(senate)==2
  widgets.append(dict(id=name,full_object=pin(p),selected_id=e['id'],selected_name=e['name'],active=e['isActive'],complete_races=len(e['races']),complete_Senate_primary_objects=senate,updatedDate=e['updatedDate'],dataTransformedAt=e['dataTransformedAt'],all_election_entries=d['elections'],literal_frontend_flag_context=context,backend_parameters=json.loads(query)))
 out=dict(status='pass_bounded_southern_eastern_Kentucky_primary_widget_research',complete_requests=4,HTTP200=4,observations=observations,complete_widgets=widgets,original_news_aggregate_unchanged=True,current_November_counts_ids_cadence_or_supplier_independence_approved=False,scope='WBKO southern andWYMT eastern primary publishers acquired via actual homepage publicconfig/anchor chains. Complete inactive2403/2078primary products preserve every race/candidate/control/clock/null. FrontenddisplayTestData true/backendincludeTestResults false/listisTest false remain distinct; no override/countadmission. updatedDateZ primary clock and currentdataTransformedAtZ are separate. Refresh/carousel numeric settings are retained in complete source bytes, not measured cadence or proven units. SharedGray infrastructure is not independent statewide votes. No November roster/feed/eligible-remainder/legal/currentgeography approval.')
 (H/'review.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');p=H/'asset-manifest.json';rows=[pin(f) for f in sorted(H.iterdir()) if f.is_file() and f!=p];assert all(r['bytes']<40000000 for r in rows);p.write_text(json.dumps(dict(assets=rows,excludes_only=p.name),indent=2)+'\n');print(dict(requests=4,assets=len(rows),review=pin(H/'review.json')))
if __name__=='__main__':main()
