#!/usr/bin/env python3
"""Keep statistical/admin discrepancies and coverage separate from candidate votes."""
import json,pathlib,collections
from freeze import write
R=pathlib.Path(__file__).resolve().parents[1]
audit={}
for y in [2024,2022,2020]:
 us=json.loads((R/f'native-units-{y}.json').read_text());summary={};arithmetic=[];methods=[]
 for name in ['ballots_cast_source','blank_ballots_source','registration_source','under_votes_source','over_votes_source']:
  known=[u for u in us if u[name] is not None]
  summary[name]={'known_cells':len(known),'unknown_cells':len(us)-len(known),'known_sum':sum(u[name] for u in known),'unknown_keys':[u['key'] for u in us if u[name] is None],'all_numeric_zero_counties':[c for c in sorted(set(u['county'] for u in us)) if all(u[name]==0 for u in us if u['county']==c)],'scope':'raw source fields; no replacement from report or inferred zeros'}
 for u in us:
  t=u['reported_candidate_votes'];b=u['ballots_cast_source'];under=u['under_votes_source'];over=u['over_votes_source'];blank=u['blank_ballots_source']
  diff=t+under+over-b if None not in [b,under,over] else None
  if diff is None or diff!=0 or t>b:
   arithmetic.append({'key':u['key'],'county':u['county'],'native_label':u['native_label'],'candidate_votes':t,'ballots_cast_source':b,'blank_ballots_source':blank,'under_votes_source':under,'over_votes_source':over,'candidate_under_over_minus_ballots':diff,'candidate_under_over_blank_minus_ballots':None if diff is None or blank is None else diff+blank,'candidate_votes_exceed_ballots_source':t>b})
 for c in sorted(set(u['county'] for u in us)):
  methods.append({'county':c,'county_fips':next(u['county_fips'] for u in us if u['county']==c),'contexts':[{'method_context':m,'unit_count':len(g),'keys':[u['key'] for u in g],'candidate_votes':sum(u['reported_candidate_votes'] for u in g),'ballots_cast_source':sum(u['ballots_cast_source'] for u in g),'blank_ballots_known_sum':sum(u['blank_ballots_source'] for u in g if u['blank_ballots_source'] is not None)} for m in sorted(set(u['method_context'] for u in us if u['county']==c)) for g in [[u for u in us if u['county']==c and u['method_context']==m]]]})
 audit[str(y)]={'field_coverage':summary,'source_arithmetic_exceptions':arithmetic,'candidate_above_ballots_unit_count':sum(r['candidate_votes_exceed_ballots_source'] for r in arithmetic),'method_contexts_by_county':methods,'raw_registration_ranking_usable_as_statewide_registration_priority':False,'reason':'Numeric zeros in many county XLS registration rows and absent cells in 2024/2022 do not reproduce the separately printed statewide registered-voter totals. 2020 raw-field ranking is a published-cell sensitivity only.'}
write(R/'field-audit.json',json.dumps(audit,indent=2)+'\n')
print({y:{'candidate_above_ballots_unit_count':v['candidate_above_ballots_unit_count'],'arithmetic_exception_count':len(v['source_arithmetic_exceptions'])} for y,v in audit.items()})
