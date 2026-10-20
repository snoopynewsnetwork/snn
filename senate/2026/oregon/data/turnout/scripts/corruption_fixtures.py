#!/usr/bin/env python3
"""Independent in-memory corruption probes against preserved source objects and math.
No source/report/peer mutation. Each fixture records exact mutation and rejection.
"""
import sys
sys.dont_write_bytecode=True
import json,copy,argparse
from reciprocal import T,oj,oc,enc,sha,metric

def original_bundle():return dict(units=oj('native/units.json'),known=oj('known-native-ranking.json'),contract=oj('priority-set.json'),candidates=oc('county-candidates.csv'),inventory=oj('source/original-inventory.json'),methods=oj('native/observations.jsonl.gz') if False else [],receipts=oj('source/shared-original-pins.json'))
BASE=original_bundle()
def require(x,msg):
 if not x:raise AssertionError(msg)
def gate(b):
 c=b['contract'];k=b['known'];us=b['units'];cand=b['candidates'];inv=b['inventory']
 require(len(cand)==864 and len({(r['contest'],r['county_fips'],r['column_index'])for r in cand})==864,'864 unique original candidate positions')
 require(cand==BASE['candidates'],'source-bound candidate fields/parties/positions/raw values')
 require(inv==BASE['inventory'],'complete original membership/order/CRC/hash/role metadata')
 require(b['receipts']==BASE['receipts'],'full original source clock/header/request/status metadata')
 require(len(us)==len(BASE['units']),'complete native and administrative presentations')
 require(us==BASE['units'],'source-bound native/admin identity/null/control/locator objects')
 require(len(k['full_order'])==510,'complete known native membership, no county substitution')
 keys=[r['key']for r in k['full_order']];require(len(set(keys))==len(keys),'unique native keys')
 m=metric([(r['key'],sum(r['candidate_vector']))for r in k['full_order']])
 require(keys==[r['key']for r in m['full_order']],'descending full native order and exact tie key')
 require(k['minimum80']['count']==m['minimum80']and k['minimum80']['preceding_votes']==m['preceding_votes']and k['minimum80']['cumulative_votes']==m['crossing_votes'],'exact minimum integer80 predecessor and crossing')
 require(k['minimum80']['ordered_keys']==m['priority_keys']and k['remainder']['keys']==m['remainder_keys'],'full priority and remainder keys')
 for r in k['full_order']:
  require(len(r['candidate_vector'])==8 and sum(r['candidate_vector'])==r['reported_votes'],'source vector/report count')
  original=next(v for v in BASE['known']['full_order']if v['key']==r['key'])
  require(r['source_presentations']==original['source_presentations'],'all original companions/method/control presentations')
  require(r['current_result_id']is None and r['current_geometry_id']is None and not r['current_approval'],'no invented current native identity/admission')
 require(c['all_36_county_parents']==BASE['contract']['all_36_county_parents'],'all parent/child/admin/null/source arrays preserved')
 require(c['complete_order']is None and c['ordered_priority_keys']is None and c['minimum80']is None and c['top15']is None and c['remainder']is None,'canonical statewide unavailable, unknown membership not zero')
 require(not c['complete_coverage']and not c['canonical_certified_native_priority_available']and not c['current_source_accepted']and not c['current_geographic_approval']and not c['coordinator_acceptance']['accepted'],'current/canonical/coordinator admission false')
 return True

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();gate(BASE);cases=[]
 def probe(name,description,change):
  b=copy.deepcopy(BASE);change(b)
  try:gate(b)
  except AssertionError as e:cases.append(dict(fixture=name,mutation=description,status='rejected',reason=str(e)));return
  raise AssertionError('corruption admitted: '+name)
 probe('missing_original_source','Delete first complete original inventory object',lambda b:b['inventory'].pop(0))
 probe('missing_native','Delete first known native rank object',lambda b:b['known']['full_order'].pop(0))
 idx=next(i for i,r in enumerate(BASE['units'])if not r['additive'])
 probe('missing_administrative','Delete full nonadditive administrative unit '+BASE['units'][idx]['unit_key'],lambda b:b['units'].pop(idx))
 probe('missing_companion','Remove overlapping Multnomah PDF companion',lambda b:b['known']['full_order'][0]['source_presentations'].pop())
 unknown=next(i for i,p in enumerate(BASE['contract']['all_36_county_parents'])if p['unknown_native_membership'])
 probe('alter_null','Replace unknown native_reporting_unit_count null with zero',lambda b:b['contract']['all_36_county_parents'][unknown].update(native_reporting_unit_count=0))
 probe('alter_candidate_count','Increment first abstract original vote by one',lambda b:b['candidates'][0].update(votes=str(int(b['candidates'][0]['votes'])+1)))
 probe('alter_source_metadata','Change original receipt HTTP status 200 to 206',lambda b:b['receipts'][0].update(status=206))
 probe('alter_method_control','Change preserved native control without changing candidates',lambda b:b['units'][0]['fields'].update(ballots=b['units'][0]['fields']['ballots']+1))
 probe('duplicate_native_key','Replace second known native key with first',lambda b:b['known']['full_order'][1].update(key=b['known']['full_order'][0]['key']))
 def swap(b):b['known']['full_order'][0],b['known']['full_order'][1]=b['known']['full_order'][1],b['known']['full_order'][0]
 probe('wrong_descending_order','Swap first two ranked known units',swap)
 probe('wrong_minimum80','Increase known minimum80 count 213 to 214',lambda b:b['known']['minimum80'].update(count=214))
 probe('county_substitution','Replace known native rows with 36 parent count surrogates',lambda b:b['known'].update(full_order=[dict(key=p['county_key'],candidate_vector=[p['county_presidential_reported_votes']])for p in b['contract']['all_36_county_parents']]))
 probe('invalid_current_admission','Invent a current result ID on archived native source row',lambda b:b['known']['full_order'][0].update(current_result_id='invented-2026-id'))
 probe('invalid_canonical_admission','Set current canonical complete order to known-source-only keys',lambda b:b['contract'].update(complete_order=[r['key']for r in b['known']['full_order']],complete_coverage=True))
 # Independent exact-boundary case: 8 of 10 already equals 80%; strict-greater would incorrectly require two units.
 exact=metric([('a',8),('b',2)]);require(exact['minimum80']==1 and exact['preceding_votes']==0 and exact['crossing_votes']==8,'exact80 boundary')
 cases.append(dict(fixture='exact80_inclusive_positive',mutation='8/10 reaches exactly80%; minimum must be1',status='passed',actual=exact))
 result=dict(status='pass',positive_original_bundle=True,negative_fixtures=sum(r['status']=='rejected'for r in cases),exact_boundary_positive=True,cases=cases,qualification='In-memory altered source-native/admin/metadata/companion/count/null/identity/order gates; no producer or peer files were changed. Exact immutable-source object equality is distinct from mathematical order/threshold validation.')
 p=T/'source/corruption-fixtures.json'
 if args.write:p.write_bytes(enc(result))
 else:assert p.read_bytes()==enc(result),'negative fixture evidence reproduces exactly'
 print(json.dumps(dict(status='pass',negative_fixtures=result['negative_fixtures'],exact80_positive=True)))
if __name__=='__main__':main()
