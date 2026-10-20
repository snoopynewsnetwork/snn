#!/usr/bin/env python3
"""In-memory corruptions of real scoped records must be rejected; writes no source values."""
from pathlib import Path
import json,copy
from invariants import source_guard,order_guard,admission_guard
D=Path(__file__).resolve().parent

def main():
 a=json.loads((D/'original-extract.json').read_text());o=json.loads((D/'sensitivity.json').read_text());p=json.loads((D/'priority-set.json').read_text());result=[]
 for guard,valid in [(source_guard,a),(order_guard,o),(admission_guard,p)]:guard(valid)
 def reject(name,guard,obj,mutation):
  z=copy.deepcopy(obj);mutation(z)
  try:guard(z)
  except (AssertionError,KeyError,TypeError):result.append(dict(fixture=name,rejected=True));return
  raise AssertionError('Corruption escaped: '+name)
 def maskzero(z):
  f=next(f for r in z['2024-senate']['rows']for f in r['fields']if f['literal']=='*');f['value']=0
 reject('protected_candidate_numeric_zero',source_guard,a,maskzero)
 reject('missing_historical_source_object',source_guard,a,lambda z:z.pop('2020-senate'))
 reject('missing_native_administrative_row',source_guard,a,lambda z:z['2024-senate']['rows'].pop(next(i for i,r in enumerate(z['2024-senate']['rows'])if r['administrative'])))
 reject('duplicate_native_key',source_guard,a,lambda z:z['2024-senate']['rows'].__setitem__(5,copy.deepcopy(z['2024-senate']['rows'][4])))
 reject('missing_full_metadata_object',source_guard,a,lambda z:z['2024-senate']['metadata'].pop('contest'))
 def swap(z):
  r=z['native-2024-senate-complete-candidate-rows-only']['order'];r[0],r[1]=r[1],r[0]
 reject('wrong_descending_order',order_guard,o,swap)
 reject('incorrect_minimum80_prefix',order_guard,o,lambda z:z['native-2024-senate-complete-candidate-rows-only'].__setitem__('minimum80_count',1391))
 reject('duplicate_full_order_key',order_guard,o,lambda z:z['county-2024-senate']['order'][1].__setitem__('key',z['county-2024-senate']['order'][0]['key']))
 reject('invalid_dispatch_admission',admission_guard,p,lambda z:z.__setitem__('accepted_for_dispatch',True))
 reject('county_dispatch_substitution',admission_guard,p,lambda z:z.__setitem__('ordered_priority_keys',z['county_sensitivity']['metrics']['ordered_priority_keys']))
 reject('fabricated_certified_native_minimum',admission_guard,p,lambda z:z.__setitem__('certified_native_minimum80',1392))
 reject('missing_parent_child_key',admission_guard,p,lambda z:z['county_contexts'][0]['source_native_constituent_keys'].pop())
 reject('invented_current_crosswalk',admission_guard,p,lambda z:z['constituents'][0].__setitem__('current_2026_crosswalk','2026'))
 (D/'negative-fixtures.json').write_text(json.dumps(dict(status='passed',fixtures=result,valid_controls_accepted=3,source_mutation=False),indent=2)+'\n');print('Negative fixtures passed:',len(result))
if __name__=='__main__':main()
