"""Coordinator read-only audit of retained newsroom bodies and actual setup flags.
No fetch, script execution, live collector or source admission.
"""
from pathlib import Path
import gzip,hashlib,json,sys
S=Path(__file__).resolve().parents[1];D=S/'data';ND=D/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def pin(p):
 b=p.read_bytes();return{'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
prior=D/'coordinator-newsroom-original-review.json'
observations=[r['complete_receipt']for r in json.loads(prior.read_bytes())['complete_individual_receipts_and_body_pins']]if '--check'in sys.argv else json.loads((ND/'manifest.json').read_bytes());assert len(observations)==21
bodies={};pins=[]
for r in observations:
 p=ND/r['asset'];stored=p.read_bytes();raw=gzip.decompress(stored)
 assert len(stored)<40000000 and sha(stored)==r['stored_sha256']and len(raw)==r['bytes']and sha(raw)==r['raw_sha256']
 bodies[r['id']]=raw;pins.append({'complete_receipt':r,'stored_body':pin(p),'complete_raw_sha256':sha(raw),'complete_raw_bytes':len(raw)})
s=bodies['whsv-results'].decode();start=s.index('Fusion.contentCache=')+len('Fusion.contentCache=');cache,length=json.JSONDecoder().raw_decode(s[start:]);fullkey=next(iter(cache['gsync-elections']));request=json.loads(fullkey);data=cache['gsync-elections'][fullkey]['data'];selected=data['selectedElection'];featured=next(iter(cache['gsync-elections-featured'].values()))['data']
assert request=={'arc-site':'whsv','includeTestResults':False}and selected['id']=='2677'and not selected['isActive']and selected['name']=='2026 General Election'
assert data['elections'][0]['isTest']is False and '"displayTestData":true'in s
choices=[c for r in selected['races']for c in r['candidates']];assert len(selected['races'])==12 and all(c['votes']==0 for c in choices)
assert not any('senat'in r['name'].lower()for r in selected['races'])and all(r['isTest']is False for r in selected['races'])
assert featured['id']is None and featured['races']==[]and not featured['isActive']
actual={'original_HTML':next(r['stored_body']for r in pins if r['complete_receipt']['id']=='whsv-results'),'complete_cache_raw_character_span':[start,start+length],'cache_semantic_sha256':sha(canon(cache)),'complete_cache':cache,'separate_component_displayTestData':True,'note':'UI displayTestData true is separate from actual source request includeTestResults false. No test votes or Senate product inferred.'}
p=D/'coordinator-newsroom-whsv-complete-cache.json.gz';raw=(json.dumps(actual,indent=2,ensure_ascii=False)+'\n').encode();stored=gzip.compress(raw,mtime=0)
if '--check'in sys.argv:assert p.read_bytes()==stored
elif p.exists():assert p.read_bytes()==stored
else:p.write_bytes(stored)
assert b'52020/31145.html'in bodies['wtop-primary-results']
assert next(r for r in observations if r['id']=='wtop-primary-ap')['status']==403
assert b'2026-November-General'in bodies['elect-results']and b'<app-root'in bodies['elect-november-linked']
assert next(r for r in observations if r['id']=='nyt-elections')['status']==403
out={'status':'pass_retained_complete_newsroom_entities_and_precise_setup_flag_scopes','legacy_complete_observations':21,'complete_individual_receipts_and_body_pins':pins,'WHSV':{'selected_election_id':'2677','isActive':False,'request_includeTestResults':False,'separate_component_displayTestData':True,'selected_isTest':False,'races':12,'choices':len(choices),'all_votes_zero':True,'Senate_race_present':False,'updatedDate':selected['updatedDate'],'transformation_clock':selected['dataTransformedAt'],'complete_cache_derivative':pin(p),'genuine_November_admission':False},'WTOP':'Actual primary AP organization52020/layout31145 iframe retained; sampled product403, no verified November Senate product or independent supplier.', 'ELECT':'Actual current-index November route points to Angular app-root shell. No counts or IDs admitted from HTTP200 shell.','NYT':'Retained direct403, exact November Senate source/automated access/cadence remains unverified; manual comparison gate.','provenance_limit':'Legacy captures preserve complete retained response entity, final URL/status/final response headers and retrieval UTC. They do not preserve complete intermediate redirect bodies/headers or TLS/wire framing; no such claim made. Later bounded regional packs have separate full response-hop receipts.','source_or_producer_writes':False,'new_acquisition_or_browser_render':False,'current_legal_ballot_IDs_geography_vote_pool_or_cadence_approval':False}
body=(json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode();p=D/'coordinator-newsroom-original-review.json'
if '--check'in sys.argv:assert p.read_bytes()==body
else:p.write_bytes(body)
print(json.dumps({'status':out['status'],'legacy_observations':21,'WHSV':out['WHSV']}))
