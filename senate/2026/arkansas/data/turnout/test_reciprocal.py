#!/usr/bin/env python3
"""Actual captured-source negative inputs for the strict reciprocal boundary.

Each gzip fixture contains its complete input, not only a hash/patch. The
expected packet is built from individually pinned original bytes and the whole
frozen contract. No election value is taken from a peer calculator or scenario.
"""
import argparse,copy,gzip,json,pathlib
from reciprocal import Capture,Checks,derive,P,sha
F=P/'fixtures/reciprocal'
def valid(p,expected):
    ranks=p['rankrows'];keys=[r['key'] for r in ranks]
    assert len(keys)==2841 and len(set(keys))==2841,'complete unique native inventory'
    assert len(p['parents'])==75 and len(p['priority_parents'])==68,'all parent coverage'
    assert ranks==sorted(ranks,key=lambda r:(-r['votes'],r['key'])),'descending native order'
    total=sum(r['votes'] for r in ranks);assert total==1182676,'primary integer denominator'
    cum=0;first=None
    for i,r in enumerate(ranks,1):
        cum+=r['votes'];assert r['rank']==i and r['cumulative_votes']==cum and r['share_denominator']==total,'rank/cumulative/denominator'
        if first is None and 5*cum>=4*total:first=i
    assert first==1056 and p['priority']==keys[:first] and p['remainder']==keys[first:],'minimum80 and full remainder'
    assert ranks[first-2]['cumulative_votes']==946007 and ranks[first-1]['cumulative_votes']==946377,'exact crossing proof'
    assert all(v is False or v is None for v in p['approval'].values()),'current/legal/feed/forecast admission prohibited'
    for n in p['native']:
        assert n['native_id'] is None,'XLSX lacks native IDs'
        assert len(n['candidates'])==7 and sum(n['candidates'].values())==n['votes'],'candidate coverage/balance'
        assert set(n['methods'])=={'Election Day','Early Vote','Absentee','Provisional'},'method coverage'
        assert sum(sum(v.values()) for v in n['methods'].values())==n['votes'],'method/candidate denominator'
    Checks().eq(expected,p,'actual-original-source-packet')
def run(write=False):
    own=Capture('own');data=derive(own,Checks());contract=json.loads(own.own('priority-set.json'))
    stats=json.loads(own.own('orders/statistics.json'));ranks=[{f:r[f] for f in ['key','votes','rank','cumulative_votes','share_denominator']} for r in contract['full_order']]
    r=data['receipts']['2024-federal-state'][1];api_record=next(r for r in data['controls'] if r['lane']=='2024-api' and r['level']=='native')
    native_descriptor=next(r for r in data['inventories'] if r['year']==2024)
    metadata=next(r for r in data['metadata'] if r['year']==2024)
    packet=dict(rankrows=ranks,priority=contract['ordered_priority_keys'],remainder=contract['remainder_keys'],parents=[r['county_fips'] for r in contract['all75parents']],priority_parents=contract['priority_parent_fips'],native=data['native']['2024-xlsx'][:2],header=data['header'],header_cells=data['header_cells'],source=r,control=api_record,companion=native_descriptor,metadata=metadata,null_admin=dict(unavailable_cases=contract['unavailable_cases'],source_native_type=contract['full_order'][0]['unit_type'],native_ballots=contract['full_order'][0]['ballots_cast']),approval=dict(current_2026=False,geographic_legal=False,november_feed=False,collector=False,forecast=False,write_in_complete=None))
    valid(packet,packet)
    cases=[]
    def add(name,mutate):
        p=copy.deepcopy(packet);mutate(p);error=None
        try:valid(p,packet)
        except (AssertionError,KeyError,TypeError,ValueError) as e:error=str(e)
        assert error is not None,'negative fixture was accepted: '+name
        body=(json.dumps(p,ensure_ascii=False,separators=(',',':'))+'\n').encode();stored=gzip.compress(body,mtime=0);assert len(stored)<40000000
        filename=name+'.input.json.gz'
        if write:(F/filename).write_bytes(stored)
        else:assert (F/filename).read_bytes()==stored
        cases.append(dict(name=name,rejected=True,error=error,input_path='fixtures/reciprocal/'+filename,raw_sha256=sha(body),stored_sha256=sha(stored),raw_bytes=len(body),stored_bytes=len(stored)))
    if write:F.mkdir(parents=True,exist_ok=True)
    add('missing-native',lambda p:p['rankrows'].pop())
    add('missing-candidate',lambda p:p['native'][0]['candidates'].pop(next(iter(p['native'][0]['candidates']))))
    add('missing-method',lambda p:p['native'][0]['methods'].pop('Early Vote'))
    add('missing-null-field',lambda p:p['native'][0].pop('native_id'))
    add('missing-administrative-field',lambda p:p['null_admin'].pop('source_native_type'))
    add('missing-header',lambda p:p['header'].pop())
    add('missing-source-field',lambda p:p['source'].pop('parent'))
    add('missing-native-companion',lambda p:p['companion'].pop('raw'))
    add('wrong-control-total',lambda p:p['control']['raw'].__setitem__('totalVotes',p['control']['raw']['totalVotes']+1))
    add('missing-metadata-null',lambda p:p['metadata']['metadata'].pop('locationType'))
    add('wrong-native-id',lambda p:p['companion'].__setitem__('native_id','0'))
    add('wrong-descending-order',lambda p:p['rankrows'].__setitem__(slice(0,2),list(reversed(p['rankrows'][:2]))))
    add('off-by-one-minimum80',lambda p:p['priority'].pop())
    add('duplicate-native-key',lambda p:p['rankrows'].append(copy.deepcopy(p['rankrows'][0])))
    add('county-dispatch-substitute',lambda p:p.__setitem__('rankrows',p['rankrows'][:75]))
    def residual(p):
        names=list(p['native'][0]['candidates']);p['native'][0]['candidates'][names[1]]+=1;p['native'][0]['candidates'][names[2]]-=1
    add('residual-allocation-total-preserved',residual)
    add('current-geography-admission',lambda p:p['approval'].__setitem__('geographic_legal',True))
    add('november-feed-admission',lambda p:p['approval'].__setitem__('november_feed',True))
    add('unknown-ballots-to-zero',lambda p:p['null_admin'].__setitem__('native_ballots',0))
    add('all-is-not-election-day',lambda p:p['metadata']['vote_types']['1'].__setitem__('description','Election Day'))
    add('raw-header-type-change',lambda p:p['header_cells'][0].__setitem__('type',None))
    add('raw-v-change',lambda p:p['header_cells'][0].__setitem__('raw_value','999'))
    add('party-metadata-normalization',lambda p:p['metadata']['parties']['2097'].__setitem__('partyName','Green Party'))
    add('wrong-source-pointer',lambda p:p['control'].__setitem__('position','/response/contests/0'))
    proof=dict(schema='arkansas-reciprocal-negative-fixtures-v1',status='pass',positive_original_packet_passed=True,negative_cases=len(cases),all_rejected=True,fixtures=cases,scope='Actual complete captured-source inputs with full2841 order/1056priority/1785remainder and real raw/candidate/method/null/admin/header/metadata companions. Negative data are fixtures only, never canonical election results.')
    if write:(P/'reciprocal-fixtures.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(status='pass',negative_cases=len(cases),all_rejected=True),indent=2));return proof
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();run(args.write)
