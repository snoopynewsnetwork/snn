#!/usr/bin/env python3
"""Derive all county requests solely from returned county slugs, IDs, and published route."""
import gzip,hashlib,json,pathlib
R=pathlib.Path(__file__).resolve().parents[1];N=R.parent/'news'
M={r['id']:r for r in json.loads((N/'manifest.json').read_text())}
SPECS=[('2024NovGen','sos-2024-general-api-data-selected'),('2020NovGen',None),('2021JanFedRun','sos-2021-federal-runoff-api-data-selected'),('2022NovGen','sos-2022-general-api-data-selected'),('2022DecGenRun','sos-2022-runoff-api-data-selected')]
refs=[];requests=[]
for eid,key in SPECS:
 if key:
  m=M[key];p=N/m['asset'];stored=p.read_bytes();b=gzip.decompress(stored)
  assert hashlib.sha256(b).hexdigest()==m['raw_sha256'];assert hashlib.sha256(stored).hexdigest()==m['stored_sha256']
  refs.append({**m,'path':str(p.relative_to(R.parent.parent)),'stored_bytes':len(stored),'entity_bytes':len(b),'role':'selected-state-contest','election_key':eid})
 else:b=gzip.decompress((R/'source/state-2020-selected.body.gz').read_bytes())
 d=json.loads(b);x=d['ballotItemWithBreakdown'];counties=x['breakdownResults']
 assert len(counties)==159
 slugs={c['name'][0]['text']:c['shortName'] for c in d['jurisdiction']['childLocalities']}
 for c in counties:
  name=c['locality']['name'][0]['text'];slug=slugs[name];cid=c['parentBallotItemId']
  requests.append({'id':eid+'--'+slug,'url':f'https://results.sos.ga.gov/results/public/api/elections/{slug}/{eid}/data/ballot-item/{cid}','election_key':eid,'county_name':name,'county_slug':slug,'county_ballot_item_id':cid,'parent':key or 'source/state-2020-selected.body.gz','parent_pointer':'/ballotItemWithBreakdown/breakdownResults; /jurisdiction/childLocalities'})
(R/'source/shared-references.json').write_text(json.dumps(refs,indent=2)+'\n')
(R/'source/requests-counties.json').write_text(json.dumps(requests,indent=2)+'\n')
print('returned county request count',len(requests))
