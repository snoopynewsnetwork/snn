"""Read-only reciprocal audit of independently built partisanship assets.

No peer outputs are changed. Keys compare identical source publications and
positions, never establish a geographic crosswalk between publications.
"""
from source_io import *
from build import readjl
import datetime
PEER=ROOT/'data/baselines'
TABLE_MAP={'2024-senate-special':'senate2024special','2024-senate-regular':'senate2024regular','2024-president':'president2024','2022-governor':'governor2022','2020-senate':'senate2020',
 '2024-registration':'registration2024','2024-voting-method':'votingmethod2024','2022-registration':'registration2022','2022-voting-method':'votingmethod2022','2020-registration':'registration2020','2020-voting-method':'votingmethod2020'}
def main():
    paths=['extracts/state-controls.json','extracts/native-special.jsonl.gz','extracts/douglas-native-contexts.jsonl.gz','extracts/lancaster-native-contexts.jsonl.gz',
      'extracts/douglas-original-rows.jsonl.gz','extracts/lancaster-statistics.json','extracts/administrative-partial-alternatives.jsonl.gz','extracts/independent-controls.json']
    pins=[{'path':str((PEER/p).relative_to(ROOT)),'sha256':sha((PEER/p).read_bytes()),'bytes':(PEER/p).stat().st_size}for p in paths]
    a=json.loads((OUT/'extracts/state-controls.json').read_text());b=json.loads((PEER/'extracts/state-controls.json').read_text());cells=0
    for own,peer in TABLE_MAP.items():
        assert set(a[own]['counties'])==set(b[peer]['county'])and len(b[peer]['county'])==93
        for c,r in a[own]['counties'].items():
            assert r['values']==b[peer]['county'][c],(own,c);cells+=len(r['values'])
        assert a[own]['statewide']['values']==b[peer]['state']
    own=readjl(OUT/'extracts/selected-native-disjoint.jsonl.gz');peer=readjl(PEER/'extracts/native-special.jsonl.gz')
    assert [r['key']for r in own]==[r['key']for r in peer]and len(peer)==1326
    c=json.loads((OUT/'priority-set.json').read_text());common=0;identity_differences=[]
    for o,p in zip(own,peer):
        assert [o['candidate_values'][1],o['candidate_values'][0],o['priority_votes_state_scope']]==[p['A'],p['B'],p['pair_votes']]
        if o['county_fips']!=p['county_fips']:identity_differences.append({'key':o['key'],'county':o['county'],'Census_verified_FIPS':o['county_fips'],'peer_FIPS':p['county_fips']})
        for x,y in [('source_id','source_id'),('county','county'),('native_label_literal','label'),('rank','rank'),('generic_writeins','generic_writeins'),('ballots','ballots'),('registration','registration'),('under','under'),('over','over')]:
            assert o[x]==p[y],(o['key'],x,o[x],p[y]);common+=1
        if o['source_kind']=='historical_state_HTML':assert o['source_position']==p['source_pointer']and o['native_id_literal']==p['native_id_literal']
        elif o['source_kind']=='county_BIFF':assert o['source_position']=={'sheet':p['source_pointer']['sheet'],'row_1based':p['source_pointer']['row']}and o['native_label_literal']==p['label']and o['contest_volume_arithmetic']==p['ballot_reconstruction']
        else:assert o['source_position']=={'actual_pdf_page':p['source_pointer']['page']}and o['blank']==p['blank']
        assert p['cumulative_pair_votes']==c['primary_ranking']['full_order'][o['rank']-1]['cumulative_votes']
        assert p['priority']==(o['rank']<=765)
    # Every selected Douglas field in all five contests, including raw % cells,
    # datemode/date cells, footer and formatted blanks; compare exact source rows.
    orows=readjl(OUT/'extracts/douglas-original-positions.jsonl.gz');prows=readjl(PEER/'extracts/douglas-original-rows.jsonl.gz')
    pp={(p['source_id'],p['sheet'],p['row']):p for p in prows};rawcells=0
    for o in orows:
        p=pp[o['source_id'],o['sheet'],o['source_row_1based']]
        assert o['values']==p['values']and o['cell_types']==p['types'];rawcells+=len(o['values'])
    ol=readjl(OUT/'extracts/lancaster-native-methods.jsonl.gz');pl=readjl(PEER/'extracts/lancaster-native-contexts.jsonl.gz')
    pp={(r['source_id'],r['page'],r['contest']):r for r in pl};methodcells=0
    for o in ol:
        p=pp[o['source_id'],o['actual_pdf_page'],TABLE_MAP[o['contest']]]
        assert o['native_label_literal']==p['label']and o['method_columns']==p['methods']
        f={r['label_literal']:r['counts']for r in o['fields']};assert f==p['fields'];methodcells+=sum(len(v)for v in f.values())
        assert o['source_footer_clock_literal'].split()==p['clock'].split()
    os=json.loads((OUT/'extracts/lancaster-statistics.json').read_text());ps=json.loads((PEER/'extracts/lancaster-statistics.json').read_text());ps={r['page']:r for r in ps}
    for o in os:
        p=ps[o['actual_pdf_page']];assert o['native_label_literal']==p['label']and o['registered_total']==p['registered']
        assert {r['label_literal']:r['counts']for r in o['fields']}==p['fields']
    pa=readjl(PEER/'extracts/administrative-partial-alternatives.jsonl.gz');oa=c['administrative_and_partial_alternates'];assert len(pa)==len(oa)==329
    pi={(r['source_id'],r['header_row_id']):r for r in pa}
    for o in oa:
        p=pi[o['source_id'],o['source_position']]
        assert o['native_label_literal']==p['label']and o['native_id_literal']==p['native_id_literal']
        assert o['candidate_values']==[r['votes']if r else None for r in p['children']]
    for parent in c['all93_parents']:
        rows=[r for r in peer if r['county']==parent['county']]
        assert parent['full_child_keys']==[r['key']for r in rows]
        assert parent['priority_child_keys']==[r['key']for r in rows if r['priority']]
        assert parent['full_child_named_votes']==sum(r['pair_votes']for r in rows)
    proof={'status':'pending_FIPS_repair_other_compared_fields_agree'if identity_differences else 'pass_reciprocal_read_only_original_extraction_agreement','identity_differences':identity_differences,'peer_agent_id':'bf15a495-7e21-44b4-abd9-d8d7f83bb88e',
      'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'peer_inputs':pins,'canvass_tables':11,'canvass_county_vectors':1023,'canvass_numeric_county_cells':cells,
      'native_source_order':1326,'native_named_candidate_cells':2652,'common_native_fields':common,'all93_parent_full_and_priority_maps':not identity_differences,
      'Douglas_raw_rows':len(orows),'Douglas_raw_cell_values_and_types':rawcells,'Lancaster_contexts':len(ol),'Lancaster_method_count_cells':methodcells,
      'Lancaster_statistics_contexts':len(os),'administrative_partial_objects':329,
      'minimum80':{'count':765,'votes':748190,'preceding_count':764,'preceding_votes':747645,'crossing':'Lancaster / 10 D-1 / page685 / 545'},
      'semantic_notes':['Peer A=Love and B=Ricketts; turnout candidate_values=[Ricketts,Love], explicitly compared in reversed order.',
        'Turnout records literal Douglas Ward-Precinct field as native_id_literal; peer has no separate machine ID. Raw workbook token, sheet and row agree; this is no cross-publication ID mapping.',
        'Turnout method descriptions state combined/unknown; peer null method or descriptive TOTAL. Every actual Lancaster method column/count and Douglas combined original field agrees.',
        'Comparison proves shared original extraction, historical arithmetic/order only. Generic write-in eligibility, current unit/boundary identities and coordinator acceptance remain separate.'],
      'coordinator_acceptance':False,'current_geography_approval':False}
    jwrite(OUT/'peer-agreement.json',proof);print(json.dumps({k:proof[k]for k in ['status','canvass_numeric_county_cells','native_source_order','Douglas_raw_cell_values_and_types','Lancaster_method_count_cells','administrative_partial_objects']}))
if __name__=='__main__':main()
