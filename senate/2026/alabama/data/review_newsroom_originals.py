"""Read-only source audit and complete embedded cache reconstruction; no network."""
from pathlib import Path
import gzip,hashlib,json,sys
S=Path(__file__).resolve().parents[1];D=S/'data';R=D/'news';AL=S.name=='alabama'
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
proof=D/'coordinator-newsroom-original-review.json'
receipts=[p['complete_receipt'] for p in json.loads(proof.read_bytes())['complete_individual_receipts_and_body_pins']] if '--check' in sys.argv else json.loads((R/'manifest.json').read_bytes())
assert len(receipts)==(17 if AL else 26);bodies={};pins=[]
for r in receipts:
 stored=(R/r['asset']).read_bytes();raw=gzip.decompress(stored)
 assert len(stored)<40000000 and sha(stored)==r['stored_sha256'] and sha(raw)==r['raw_sha256'] and len(raw)==r['bytes']
 bodies[r['id']]=raw;pins.append({'complete_receipt':r,'stored_body':pin(R/r['asset']),'complete_raw_sha256':sha(raw),'complete_raw_bytes':len(raw)})
setups=[]
for sid,site,selectedid in [('wsfa-results','wsfa','2743'),('wbrc-results','wbrc',None)] if AL else [('kait-results','kait',None)]:
 text=bodies[sid].decode();start=text.index('Fusion.contentCache=')+len('Fusion.contentCache=');cache,length=json.JSONDecoder().raw_decode(text[start:])
 products=cache['gsync-elections'];assert len(products)==1;query=json.loads(next(iter(products)));assert query=={'arc-site':site,'includeTestResults':False}
 data=next(iter(products.values()))['data'];selected=data['selectedElection'];assert selected.get('id')==selectedid
 races=selected.get('races') or [];choices=[c for r in races for c in r.get('candidates',[])]
 assert all(c['votes']==0 for c in choices) and '"displayTestData":true' in text
 if selectedid is not None:assert selected['isActive'] is False and len(races)==48 and all(r['isTest'] is False for r in races)
 else:assert not races and data['elections']==[]
 senate=[r for r in races if r['name'].startswith('U.S. Senate')];assert len(senate)==(1 if selectedid else 0)
 item={'original_HTML':next(x['stored_body'] for x in pins if x['complete_receipt']['id']==sid),'complete_cache_raw_character_span':[start,start+length],'cache_semantic_sha256':sha(canon(cache)),'complete_cache':cache,'separate_UI_displayTestData':True,'request_includeTestResults':False,'scope':'Complete retained source cache; no script execution, test vote or current return admission'}
 path=D/('coordinator-newsroom-'+site+'-complete-cache.json.gz');b=gzip.compress((json.dumps(item,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0)
 if '--check' in sys.argv:assert path.read_bytes()==b
 elif path.exists():assert path.read_bytes()==b
 else:path.write_bytes(b)
 setups.append({'source':sid,'backend_parameters':query,'selected_election_id':selectedid,'selected_name':selected.get('name'),'selected_isActive':selected.get('isActive'),'listed_elections':data['elections'],'all_races':len(races),'all_choices':len(choices),'all_counts_zero':True if choices else None,'full_US_Senate_setup_objects':senate,'publisher_updatedDate':selected.get('updatedDate'),'dataTransformedAt':selected.get('dataTransformedAt'),'separate_UI_displayTestData':True,'complete_cache_derivative':pin(path),'admission':False})
assert next(r for r in receipts if r['id']=='nyt-elections')['status']==403
out={'status':'pass_complete_retained_news_entities_and_precise_widget_scopes','complete_legacy_observations':len(receipts),'complete_individual_receipts_and_body_pins':pins,'whole_embedded_setups':setups,'NYT':'Actual direct403 retained; precise November Senate product/access/cadence unverified. Manual observation required.','source_independence':'Shared Gray/GSync infrastructure or same official count reprints are overlapping upstream views, not demonstrated independent vote suppliers. Supplier independence/complete legal candidate roster unproved.','provenance_limit':'Legacy complete entity/finalURL/status/finalresponseheaders/UTC retained, not complete intermediate redirect bodies/headers or TLS/wire framing. Separate already reviewed regional followups retain full response hops.','no_new_acquisition_or_worker_writes':True,'no_current_votes_IDs_geography_law_cadence_pool_forecast_approval':True}
b=(json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode()
if '--check' in sys.argv:assert proof.read_bytes()==b
else:proof.write_bytes(b)
print(json.dumps({'status':out['status'],'legacy_entities':len(receipts),'whole_setups':[{k:r[k] for k in ['source','selected_election_id','all_races','all_choices','all_counts_zero']} for r in setups]}))
