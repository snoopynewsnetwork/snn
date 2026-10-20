"""Independent rejection guards for published-source preservation and nonadmission."""
from fractions import Fraction

def source_guard(extract):
 expected={'2024-senate':2201,'2020-senate':1959,'2022-governor':2196,'2024-president':2202}
 assert set(extract)==set(expected)
 for tag,v in extract.items():
  rows=v['rows'];n=v['candidate_count'];assert len({r['key']for r in rows})==len(rows)
  native=[r for r in rows if r['level']=='Precinct'];assert len(native)==expected[tag]and sum(r['administrative']for r in native)==33
  assert len([r for r in rows if r['level']=='County'])==33
  assert v['metadata']['contest']['id']==v['contest_id']
  for r in rows:
   assert len(r['fields'])==n+2 and [f['literal']for f in r['fields']]==r['raw_row'][2:]
   for f in r['fields']:
    assert f['value']==(int(f['literal'])if f['literal'].isdigit()else None)
   vals=[f['value']for f in r['fields'][:n]]
   assert r['candidate_votes']==(sum(vals)if None not in vals else None)

def order_guard(orders):
 assert len(orders)==18
 for v in orders.values():
  rows=v['order'];den=v['denominator'];keys=[r['key']for r in rows];assert len(set(keys))==len(keys)==v['unit_count']
  assert rows==sorted(rows,key=lambda r:(-r['votes'],r['source_order']))
  total=0;cut=None
  for rank,r in enumerate(rows,1):
   total+=r['votes'];assert r['rank']==rank and r['cumulative_votes']==total
   if cut is None and 5*total>=4*den:cut=rank
  assert cut==v['minimum80_count'];assert v['minimum80_votes']==rows[cut-1]['cumulative_votes'];assert v['preceding_votes']==(rows[cut-2]['cumulative_votes']if cut>1 else 0)
  assert v['crossing_key']==rows[cut-1]['key'];assert v['top15_votes']==sum(r['votes']for r in rows[:15])
  assert Fraction(v['top15_exact_fraction'])==Fraction(v['top15_votes'],den)
  assert v['ordered_priority_keys']==keys[:max(15,cut)]and v['ordered_remainder_keys']==keys[max(15,cut):]

def admission_guard(contract):
 assert contract['accepted_for_dispatch']is False and contract['ordered_priority_keys']==[]
 assert all(contract[k]is None for k in ['certified_native_top15','certified_native_minimum80','certified_native_full_order'])
 assert len(contract['constituents'])==2201 and len(contract['county_contexts'])==33
 keys=[r['key']for r in contract['constituents']];assert len(set(keys))==2201
 assert set(contract['complete_coverage_order'])==set(keys)and len(contract['complete_coverage_order'])==2201
 children=[k for r in contract['county_contexts']for k in r['source_native_constituent_keys']];assert len(children)==len(set(children))==2201 and set(children)==set(keys)
 assert sum(r['administrative']for r in contract['constituents'])==33
 for r in contract['constituents']:
  assert r['geometry_status']=='unavailable_unapproved'and r['current_2026_crosswalk']is None
  assert r['candidate_values']==[int(x)if x.isdigit()else None for x in r['source_candidate_literals']]
  assert r['complete_candidate_votes']==(sum(r['candidate_values'])if None not in r['candidate_values']else None)
