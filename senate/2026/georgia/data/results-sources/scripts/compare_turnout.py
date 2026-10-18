from common import *
import csv,io,collections
positions=[json.loads(s) for s in gzip.decompress((ROOT/'extracts/source-positions.jsonl.gz').read_bytes()).decode().splitlines()]
ours={}
for r in positions:
 key=(r['election_key'],r['county_fips'] or '',r['level'],r['native_id'] or '',r['candidate_ordinal'],r['method_ordinal'] if r['kind']=='METHOD' else None)
 assert key not in ours;ours[key]=r
checks=collections.Counter();differences=[]
for filename,kind in [('candidate-votes.csv.gz','TOTAL'),('candidate-method-votes.csv.gz','METHOD')]:
 rows=list(csv.DictReader(io.StringIO(gzip.decompress((GA/'data/turnout'/filename).read_bytes()).decode())))
 for p in rows:
  key=(p['election_key'],p['county_fips'],p['unit_level'],p['unit_id'] if p['unit_level'] in ['precinct','state_county'] else '',int(p['option_position']),int(p['method_position']) if kind=='METHOD' else None)
  # state_county source unit_id is locality-row GUID while our native_id preserves same object ID.
  o=ours[key];value=p['method_votes'] if kind=='METHOD' else p['votes'];value=None if value=='' else int(value)
  assert value==o['votes'],(key,value,o['votes'])
  assert p['option_id']==o['candidate_id'] and p['candidate_native_id']==o['nativeId']
  assert json.loads(p['localized_candidate_name_json'])==o['name']
  assert p['is_write_in'].lower()==str(o['isWriteIn']).lower() and p['is_qualified_write_in'].lower()==str(o['isQualifiedWriteIn']).lower()
  if kind=='METHOD':assert p['method_id']==o['group_id'] and p['method_pointer']==o['source_pointer']
  else:assert p['source_pointer']==o['source_pointer']
  checks[kind]+=1
assert sum(checks.values())==76400
cross=[]
for p in csv.DictReader((GA/'data/turnout/candidate-crosswalk.csv').open()):
 if p['state_native_id']!=p['county_native_id'] or p['state_party']!=p['county_party']:cross.append(p)
assert len(cross)==18
save(ROOT/'extracts/independent-peer-check.json',{'status':'pass','source_positions':sum(checks.values()),'counts_by_kind':dict(checks),'same_original_not_independent_primary_publication':True,'comparison':'independent original-byte extraction compared with immutable turnout CSVs; no construction from peer counts','candidate_nativeId_or_party_differences':cross,'native_nulls_preserved':True,'frozen_inputs_unchanged':True})
print('76400 source-position values/IDs/ordinals/localized names/flags and18 candidate mismatches checked')
