"""Read-only full-field comparison with the actual independent SC peer.

Derived schemas have explicit key mappings; source values are never rewritten.
"""
import csv,gzip,io,json
from pathlib import Path
from acquire import H,sha
from build_turnout import dump
P=H.parent/'baselines'
def csvload(p):return list(csv.DictReader(io.StringIO((gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes()).decode())))
def signature(row):return tuple(row[k]for k in ['contest_label','observation_scope','division_path','candidate_id','party_id','method_id'])
def canon(k,v):
    if k in ['raw_row_json','raw_division','method_ids','raw_candidate_cells']:return json.loads(v)
    if k=='scope':return 'overlapping_control'if v.startswith('control:')else('candidate'if v=='generic_write_in'else v)
    if k=='level':return {'state_summary':'summary','county_summary':'summary','vhm_native_precinct':'precinct','unassigned_administrative':'unassigned'}.get(v,v)
    return v
def compare(a,b,key,exclude=()):
    ai={key(r):r for r in a};bi={key(r):r for r in b};assert len(ai)==len(a)and len(bi)==len(b)and set(ai)==set(bi)
    common=set(a[0])&set(b[0])-set(exclude);diff=[]
    for sig,row in ai.items():
        for k in sorted(common):
            if canon(k,row[k])!=canon(k,bi[sig][k]):diff.append(dict(key=sig,field=k,own=row[k],peer=bi[sig][k]))
    assert not diff,diff[:3]
    return dict(rows=len(a),fields=sorted(common),compared_cells=len(a)*len(common))
def main():
    evidence={};out={}
    for own,peer in [('extracts/candidate-method-controls.csv.gz','candidate-method-controls.csv.gz'),('extracts/native-units.csv.gz','native-units.csv.gz'),('extracts/registration-participation.csv.gz','registration-participation.csv.gz'),('../county-turnout.csv','../county-baselines.csv'),('candidate-universe.json','candidate-universe.json'),('extracts/legacy-candidate-methods.csv.gz','legacy-candidate-methods.csv.gz'),('extracts/legacy-json-native-units.csv.gz','legacy-native-baselines.csv.gz')]:
        for side,path in [('own',H/own),('peer',P/peer)]:evidence[f'{side}:{own if side=="own"else peer}']=dict(path=__import__('os').path.relpath(path,H),bytes=path.stat().st_size,sha256=sha(path.read_bytes()))
    out['candidate_method_controls']=compare(csvload(H/'extracts/candidate-method-controls.csv.gz'),csvload(P/'candidate-method-controls.csv.gz'),signature)
    out['native_hierarchy']=compare(csvload(H/'extracts/native-units.csv.gz'),csvload(P/'native-units.csv.gz'),lambda r:(r['contest_label'],r['native_division_path']),exclude=['identity_status'])
    # Both schemas retain literal requested county and native source code/ordinal;
    # their derived geography-key strings differ. Match the actual source row.
    out['registration']=compare(csvload(H/'extracts/registration-participation.csv.gz'),csvload(P/'registration-participation.csv.gz'),lambda r:(r['source_id'],r['source_pointer']),exclude=['geography_key'])
    out['counties']=compare(csvload(H/'../county-turnout.csv'),csvload(P/'../county-baselines.csv'),lambda r:r['county_fips'])
    a=json.loads((H/'candidate-universe.json').read_text());b=json.loads((P/'candidate-universe.json').read_text())
    for label in a:
        assert a[label]['contest_metadata']==b[label]['contest']
        g=b[label]['combined_metadata'];assert a[label]['candidate_metadata']==g['candidates']and a[label]['method_metadata']==g['voteChannels']and a[label]['party_metadata']==g['parties']
        md=json.loads(__import__('acquire').body(label+'-methods'))['data']
        assert b[label]['methods_contest']==md['contest']
        for field in ['candidates','parties','voteChannels']:assert b[label]['methods_metadata'][field]==md['contestGranularData'][field]
    out['complete_candidate_party_method_contest_metadata']=True
    pr=json.loads((P/'priority-set.json').read_text());mine=json.loads((H/'priority-set.json').read_text());shared=['total','unit_count','top15_votes','threshold_integer','minimum80_count','minimum80_votes','preceding_votes','crossing_key','crossing_name','crossing_votes','ordered_keys']
    assert all(mine[k]==pr[k]for k in shared)
    lc=json.loads((H/'legacy-json-reconciliation.json').read_text());pn=json.loads((P/'legacy-native-priority.json').read_text())
    for label in lc:
        if label!='contests':continue
        for key,val in lc[label].items():
            st=val['native_ranking'];peer=pn[key]
            for k in ['total','unit_count','top15_votes','threshold_integer','minimum80_count','minimum80_votes','preceding_votes']:assert st[k]==peer[k],(key,k)
            rows=csvload(H/f'extracts/{key}-original-combined-native-order.csv');assert [(r['name'],r['county'],int(r['candidate_votes']),int(r['cumulative_votes']))for r in rows]==[(r['name'],r['county'],r['votes'],r['cumulative'])for r in peer['order']]
    # Every original XML candidate/method/native cell, including raw attributes.
    own=csvload(H/'extracts/legacy-candidate-methods.csv.gz');peer=csvload(P/'legacy-candidate-methods.csv.gz');xmlpeer=[r for r in peer if r['source_id'].startswith('legacy')and r['source_id']!='legacy2022-clarendon-pinned-detailtxt']
    def key(r):return(r['contest_label'],r['county'],r.get('history_candidate_id',r.get('analysis_candidate_id')),r.get('method',r.get('method_name')),r['native_name'])
    ai={key(r):r for r in own};bi={key(r):r for r in xmlpeer};assert set(ai)==set(bi)and len(ai)==len(own)==len(xmlpeer)
    for k,r in ai.items():
        q=bi[k];assert r['votes']==q['votes']and r['source_id']==q['source_id']and r['source_pointer']==q['source_pointer']and json.loads(r['raw_attributes'])==json.loads(q['raw_attributes'])
        assert r['choice_key']==q['source_choice_key']and r['choice_text']==q['source_choice_text']and r['party']==q['source_party']
    out['original_XML_native_candidate_methods']=dict(rows=len(own),all_raw_attributes_keys_labels_and_pointers_equal=True)
    txt=csvload(H/'extracts/clarendon-2022-txt-candidate-methods.csv');txt=[r for r in txt if r['level']=='native'];tp=[r for r in peer if r['source_id']=='legacy2022-clarendon-pinned-detailtxt'];assert len(txt)==len(tp)==1176
    ta={(r['contest_label'],r['native_name'],r['candidate_label'],r['method']):r for r in txt};tb={(r['contest_label'],r['native_name'],r['source_choice_text'],r['method_name']):r for r in tp};assert set(ta)==set(tb)
    for k,r in ta.items():assert r['votes']==tb[k]['votes']and r['party']==tb[k]['source_party']
    out['Clarendon_TXT_native_candidate_methods']=dict(rows=len(txt),all_counts_raw_names_candidates_methods_parties_equal=True)
    own=csvload(H/'extracts/legacy-json-native-units.csv.gz');peer=csvload(P/'legacy-native-baselines.csv.gz');ai={(r['contest_label'],r['county'],r['native_name']):r for r in own};bi={(r['contest_label'],r['county'],r['name']):r for r in peer};assert set(ai)==set(bi)
    for k,r in ai.items():
        q=bi[k];assert r['candidate_votes']==q['candidate_votes']and r['source_id']==q['source_id']and r['native_name_pointer']==q['source_pointer']
        src=__import__('extract_legacy_json').rawsource(r['source_id'])[0];d=json.loads(src);ptr=r['candidate_vector_pointer'].split('/');v=d['Contests'][int(ptr[2])]['V'][int(ptr[4])];assert v==json.loads(q['raw_choice_vector'])
    out['original_JSON_native_rows']=dict(rows=len(own),all_counts_source_ids_names_and_pointers_equal=True)
    out['full_county_and_original_native_orders_thresholds']=True
    dump('peer-agreement.json',dict(status='pass_independent_shared_fields',peer_agent_id='2a77ed30-c478-46c3-8980-817b50d4e679',comparison='independent turnout code reads original-source/peer extracts only; no peer writes',evidence=evidence,checks=out,explicit_schema_differences=['VHM derived geography_key formats differ; exact original source_id/pointer and all other common fields compared; summary/native level labels mapped explicitly','Candidate scope labels map generic_write_in to included candidate and control:pseudotype to overlapping_control; original pseudotypes/flags compared unchanged','Native identity_status prose differs; raw identities, candidate/method vectors, source pointers and every other common field compared','Original combined JSON native keys differ; same-source names/pointers/counts/vectors and entire order compared','Clarendon TXT locators use line/column fields here; every original text/field locator separately validated','Candidate interpretation uses explicit original/DB IDs; raw Bledsoe party disagreement remains'],coordinator_acceptance='external authority path only in priority contract; this comparison does not accept current geography'))
    print(json.dumps({k:(v.get('rows')if isinstance(v,dict)else v)for k,v in out.items()},indent=2))
if __name__=='__main__':main()
