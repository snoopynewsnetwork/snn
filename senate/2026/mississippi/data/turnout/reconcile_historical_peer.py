"""Read-only independent comparison of all original 2018 county-stage controls."""
import json
from acquire_sources import BASE, OUT, sha, savejson

def main():
 paths=[OUT/'historical-county-readings.json',BASE/'data/baselines/county-2018-readings.json']
 own,peer=[json.loads(p.read_text()) for p in paths]
 aa={r['source_id']:r for r in own['readings']};bb={r['source_id']:r for r in peer['readings']}
 assert set(aa)==set(bb) and len(aa)==164
 differences=[];position_differences=[];compared=0
 for sid,a in aa.items():
  b=bb[sid]
  assert a['raw_sha256']==b['raw_sha256'],sid
  assert a['page']==b['source_positions']['page'],sid
  assert set(a['candidate_votes'])==set(b['candidate_values']),sid
  for name,v in a['candidate_votes'].items():
   compared+=1
   if v!=b['candidate_values'][name]:differences.append(dict(source_id=sid,candidate=name,own=v,peer=b['candidate_values'][name]))
  if a['source_column']!=b['source_positions']['source_column']:position_differences.append(dict(source_id=sid,own=a['source_column'],peer=b['source_positions']['source_column']))
 expected_position_difference=[dict(source_id='sos-2018-county-issaquena',own=4,peer=6)]
 # Own old merged-machine ordinal points at the very same source TOTAL box.
 # Separate full-original native rereads establish its physical ordinal as 6;
 # retain both metadata vintages instead of rewriting the county control.
 native=json.loads((OUT/'2018-issaquena-two-stage-native-original-readings.json').read_text())
 original=next(s for s in native['sources'] if s['source_id']=='sos-2018-county-issaquena')
 qualified=position_differences==expected_position_difference and original['physical_TOTAL_column']==6 and original['prior_county_control_machine_TOTAL_ordinal']==4 and aa[original['source_id']]['source_positions']['header_bounds']==bb[original['source_id']]['source_positions']['header_box']
 savejson(OUT/'historical-county-peer-reconciliation.json',dict(status='agree_all_164_original_source_entities_492_candidate_values_with_one_qualified_ordinal_vintage' if not differences and qualified else 'differences_require_review',input_pins=[dict(path=str(p.relative_to(BASE)),sha256=sha(p.read_bytes()),bytes=p.stat().st_size) for p in paths],original_entities=164,compared_candidate_values=compared,candidate_differences=differences,accepted_TOTAL_ordinal_differences=position_differences,qualified_machine_vs_physical_ordinal=qualified,qualification='All candidate values, source hashes and pages agree. Issaquena Nov6 own old merged-machine TOTAL ordinal4 and peer corrected physical ordinal6 target the same original box. Separate full-original native rereads establish physical6. The metadata versions remain distinct; no general ordinal or native-geography agreement inferred.'))
 assert compared==492 and not differences and qualified
 print('164 originals / 492 candidate values agree; Issaquena Nov6 machine4 versus physical6 explicitly qualified')

if __name__=='__main__':main()
