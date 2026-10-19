"""Separate referenced named-reading coverage from embedded working payload scope."""
from pathlib import Path
import collections,gzip,hashlib,json

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/working-2024-named-coverage'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 QA.mkdir(parents=True,exist_ok=True);q=QA/(p.name+'.gz')
 b=gzip.decompress(q.read_bytes())if q.exists()else p.read_bytes()
 if not q.exists():q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 ab,ap=freeze(DATA/'turnout/2024-named-contract-coverage-audit.json');a=json.loads(ab);cb,cp=freeze(DATA/'turnout/priority-set.json');c=json.loads(cb);coherent_contract_pin=sha(cb)==a['priority_contract_sha256']
 assert c['status']=='in_progress_not_coordinator_accepted'and c['current_2026_geographic_approval']is False and not(c.get('peer_agreement')or{}).get('native_fields_complete')
 recorded=a['all11_original_source_reading_pins'];assert len(recorded)==82
 pins={}
 for sid,r in recorded.items():
  p=DATA/'turnout'/r['path'];b,pn=freeze(p);assert sha(b)==r['sha256'];pins[r['path']]=pn
 sources=[r for r in c['source_native_constituents']if r['role']=='native_reporting_constituent'and r['source_id']not in('sos-2024-county-coahoma','sos-2024-county-pike')]
 assert len(sources)==1736 and {r['source_id']for r in sources}==set(recorded)
 bysource=collections.Counter(r['source_id']for r in sources)
 for sid,r in recorded.items():
  if r['native_constituents']is not None:assert r['native_constituents']==bysource[sid]
 coor=json.loads((DATA/'coordinator-preferred82-presidential-replay-review.json').read_bytes());assert coor['preferred_source_views']==82 and coor['preferred_native_constituents']==1736
 embedded=collections.Counter();embedded_sources=set();missing=[]
 for r in sources:
  v=r.get('separately_scoped_contests',{}).get('2024-president',{}).get('candidate_votes',{});embedded[len(v)]+=1
  if v:
   assert len(v)==9 and all(type(x)is int and x>=0 for x in v.values());embedded_sources.add(r['source_id'])
  else:missing.append(r['key'])
 order=c['all_unit_order'];assert len(order)==1736 and [r['key']for r in order]==c['source_native_preferred_ordered_keys']and c['ordered_priority_keys']==[r['key']for r in order[:887]]and c['priority_count']==887
 cumulative=0
 for i,r in enumerate(order,1):
  assert r['rank']==i and r['named_candidate_votes']==sum(r['candidate_votes'].values());cumulative+=r['named_candidate_votes'];assert cumulative==r['cumulative_votes']
 assert cumulative==1215400 and order[885]['cumulative_votes']==972157 and order[886]['cumulative_votes']==972656
 assert c['top15']['votes']==60019 and c['minimum80']['count']==887 and c['minimum80']['crossing_votes']==499
 out=dict(status='bounded_referenced_original_readings_verified_working_contract_freeze_deferred',frozen_working_contract=cp,frozen_worker_coverage_audit=ap,coverage_audit_expected_contract_sha256=a['priority_contract_sha256'],coverage_audit_matches_captured_working_contract=coherent_contract_pin,frozen_original_reading_reference_bodies=list(pins.values()),reference_source_views=82,reference_native_constituents=1736,prior_independent_named_source_review=pin(DATA/'coordinator-preferred82-presidential-replay-review.json'),embedded_nine_presidential_candidate_native_records=embedded[9],embedded_presidential_source_views=len(embedded_sources),native_records_without_embedded_presidential_vectors=len(missing),source_keys_without_embedded_presidential_vectors=missing,verified_primary_native_order_units=1736,verified_priority_prefix_units=887,source_named_Senate_denominator=1215400,qualification='The frozen coverage audit points to complete original preferred82 named readings, already independently source-reviewed. The separately captured in-progress contract does not match that audit hash and reflects a rebuild version; these two bodies cannot form a coherent final freeze. Its embedded presidential vectors cover35native/two views;1701remaining native records do not embed those fields. Complete referenced extraction is distinct from complete contract payload. Final integration must preserve complete named-source objects through embedded fields or exact pinned external data and a matching final contract hash. Mutable rebuilds are not accepted witnesses; original immutable887v1 stays unchanged and no formal dispatch acceptance is granted.',complete_embedded_all11_payload=False,formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-working-2024-named-coverage-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
