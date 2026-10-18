"""Read-only comparison to actual independent turnout worker; never fixes peer."""
from extract import *
PEER=DATA/'turnout'
def readcsv(p):return list(csv.DictReader(gzip.open(p,'rt') if p.suffix=='.gz' else open(p)))
def main():
    result={'peer_agent_id':'46dcb766-b312-4aaf-ac85-921179115c95','scope':'independent parses of exact primary originals; schema differences explicit; no geographic approval','comparisons':[]}
    def compare(name,a,b,key,fields,transform=None):
        aa={key(r):r for r in a};bb={key(r):r for r in b};assert len(aa)==len(a) and len(bb)==len(b)
        errors=[];counts=collections.Counter()
        for k in aa.keys()&bb.keys():
            for f in fields:
                av=aa[k][f];bv=bb[k][f]
                if transform:av,bv=transform(f,av,bv)
                if av!=bv:
                    counts[f]+=1
                    if len(errors)<30:errors.append(dict(key=k,field=f,ours=av,peer=bv))
        result['comparisons'].append(dict(name=name,ours=len(a),peer=len(b),keys_only_ours=sorted(aa.keys()-bb.keys())[:30],keys_only_peer=sorted(bb.keys()-aa.keys())[:30],fields=list(fields),field_mismatch_counts=dict(counts),examples=errors,
                                           status='match' if not counts and aa.keys()==bb.keys() else 'differences'))
    a=readcsv(BASE/'candidate-method-controls.csv.gz');b=readcsv(PEER/'extracts/candidate-method-controls.csv.gz')
    fields=[x for x in a[0] if x!='scope']
    compare('all raw candidate/method/control positions; all counts, flags and source pointers',a,b,lambda r:(r['contest_label'],r['observation_scope'],r['source_pointer']),fields,
            lambda f,a,b:(json.loads(a),json.loads(b)) if f=='raw_row_json' else (a,b))
    result['scope_mapping']={'ours generic_write_in':'peer candidate; same original ALL_OTHER_CANDIDATES ID retained','ours control:TOTAL_VOTES/control:TOTAL_BALLOTS/control:PSEUDOCANDIDATE':'peer overlapping_control; numerical raw fields compared without scope relabel'}
    a=readcsv(BASE/'native-units.csv.gz');b=readcsv(PEER/'extracts/native-units.csv.gz')
    fields=[x for x in b[0] if x in a[0] and x not in ['identity_status','method_ids','raw_candidate_cells']]
    compare('all9823 combined hierarchy units and denominators',a,b,lambda r:(r['contest_label'],r['native_division_path']),fields)
    compare('all9823 raw candidate vectors and native method identities',a,b,lambda r:(r['contest_label'],r['native_division_path']),['method_ids','raw_candidate_cells'],lambda f,a,b:(json.loads(a),json.loads(b)))
    a=readcsv(BASE/'registration-participation.csv.gz');b=readcsv(PEER/'extracts/registration-participation.csv.gz')
    fields=[x for x in b[0] if x not in ['geography_key','level']]
    compare('all7500 VHM positions/controls/codes, distinct from database identities',a,b,lambda r:(r['source_id'],r['source_pointer']),fields)
    result['vhm_identity_convention']='Different versioned geography-key formatting and summary level labels excluded; every source id/pointer/county/name/code/ordinal/summary/count/percent compared.'
    a=readcsv(DATA/'county-baselines.csv');b=readcsv(DATA/'county-turnout.csv');fields=[x for x in b[0] if x in a[0]]
    compare('all46 counties every shared candidate/control/rank/registration field',a,b,lambda r:r['county_fips'],fields)
    ours=json.loads((BASE/'priority-set.json').read_text());peer=json.loads((PEER/'priority-set.json').read_text())
    fields=['total','unit_count','top15_votes','minimum80_count','minimum80_votes','threshold_integer','preceding_votes','crossing_key','crossing_name','crossing_votes','ordered_keys']
    result['priority']={f:{'ours':ours[f],'peer':peer[f],'match':ours[f]==peer[f]} for f in fields}
    result['native_orders']=[]
    for lab in LABELS:
        a=ours['comparisons'][lab]['native'];b=readcsv(PEER/'extracts'/(lab+'-native-order.csv'))
        result['native_orders'].append(dict(contest=lab,unit_count=len(b),order_match=a['ordered_keys']==[r['geography_key'] for r in b],
             every_vote_and_cumulative_match=all(x['votes']==int(y['candidate_votes']) and x['cumulative']==int(y['cumulative_votes']) and x['name']==y['name'] and x['county']==y['county'] for x,y in zip(a['order'],b)),
             minimum80_count=a['minimum80_count'],minimum80_votes=a['minimum80_votes'],preceding_votes=a['preceding_votes']))
    result['input_hashes']={str(p.relative_to(DATA)):sha(p.read_bytes()) for p in [DATA/'county-baselines.csv',DATA/'county-turnout.csv',BASE/'candidate-method-controls.csv.gz',PEER/'extracts/candidate-method-controls.csv.gz',BASE/'native-units.csv.gz',PEER/'extracts/native-units.csv.gz',BASE/'priority-set.json',PEER/'priority-set.json']}
    result['status']='pass' if all(x['status']=='match' for x in result['comparisons']) and all(x['match'] for x in result['priority'].values()) and all(x['order_match'] and x['every_vote_and_cumulative_match'] for x in result['native_orders']) else 'differences_retained'
    dump(BASE/'peer-reconciliation.json',result);print(compact({k:result[k] for k in ['status','comparisons']}))
if __name__=='__main__':main()
