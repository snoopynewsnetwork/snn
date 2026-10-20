"""Post-freeze source-only associations and bounded captured-peer audit."""
import collections,csv,gzip,io,json,tarfile
from extract import ROOT,STATE,dump,en,sources,records
def load(name):return json.loads(gzip.decompress((ROOT/'extracted'/name).read_bytes()))
def norm(s):return s.upper().replace(' & ',' AND ')
def main():
    h=load('2024-senate.json.gz');apis=load('api-native-objects.json.gz');state=next(x for x in apis if x['scope_code']=='STATE');parent_api={norm(en(x['locality']['name'])):x for x in state['ballotItemWithBreakdown']['breakdownResults']};parents={};units=[];bulk=load('bulk-requested-offices.json.gz');heads=bulk['header'];bi={x:i for i,x in enumerate(heads)};grouped=collections.defaultdict(list)
    for rr in bulk['rows']:
        c=rr['cells'];grouped[(c[bi['OfficeId']],c[bi['LocalityCode']],c[bi['PrecinctName']])].append(rr)
    turns=load('enr-2024-turnout-report-records.json.gz');th=turns[0]['cells'];turns={ (r['cells'][2],r['cells'][3]):r for r in turns[1:] }
    method_sums=collections.defaultdict(int);api_method_sums=collections.defaultdict(int);bulkblank=[]
    for p in [r for r in h['rows'] if r['scope']=='Locality']:
        pa=parent_api[norm(p['name'])];code=pa['locality']['mapFeatureId'];a=next(x for x in apis if x['scope_code']==code);vec=lambda x:tuple(next(c['voteCount'] for c in x['ballotOptions'] if c['nativeId']==i) for i in ['cs534','cs535','wi-cc200'])
        index=collections.defaultdict(list)
        for i,x in enumerate(a['ballotItemWithBreakdown']['breakdownResults']):index[vec(x)].append((i,x))
        summary=a['ballotItemWithBreakdown']['summaryResults'];assert vec(summary)==tuple(p['votes'])==vec(pa)
        parents[p['name']]={'locality':p['name'],'code':code,'fips':'51'+code,'source_parent':pa['locality'],'api_jurisdiction':a['jurisdiction']['id'],'api_election':a['election'],'historical_record':p['record'],'voterTurnout':a['voterTurnout']}
        for r in [r for r in h['rows'] if r['scope']=='Precinct' and r['parent']==p['name']]:
            candidates=index[tuple(r['votes'])];assert len(candidates)==1
            i,x=candidates[0];label=en(x['precinct']['name']);export_label=label.rsplit(' (',1)[0] if label.endswith(')') else label;bg=grouped[('cc200',code,export_label)];bv=[sum(int(rr['cells'][bi['WriteInVote' if cid=='wi-cc200' else 'TOTAL_VOTES']]) for rr in bg if rr['cells'][bi['CandidateId']]==cid) for cid in ['cs534','cs535','wi-cc200']];assert bv==r['votes']
            tr=turns[(en(pa['locality']['name']),export_label)];voter=[z for z in a['voterTurnout'] if z['id']==x['precinct']['id']];assert len(voter)<=1
            u=dict(historical=r,code=code,fips='51'+code,api_source=a['source'],api_pointer=f'/ballotItemWithBreakdown/breakdownResults/{i}',api_native=x,api_voter_turnout=voter[0] if voter else None,turnout_csv={'header':th,'record':tr},bulk_senate_rows=bg,association='unique complete candidate vector within explicit parent; not geography/crossyear approval')
            units.append(u)
            for c in x['ballotOptions']:
                assert sum(g['voteCount'] for g in c['groupResults'])==c['voteCount']
                for g in c['groupResults']:method_sums[(c['nativeId'],g['groupId'])]+=g['voteCount']
            for rr in bg:
                if not rr['cells'][bi['PrecinctId']]:bulkblank.append(rr)
        for c in summary['ballotOptions']:
            for g in c['groupResults']:api_method_sums[(c['nativeId'],g['groupId'])]+=g['voteCount']
    assert method_sums==api_method_sums
    state_method={(c['nativeId'],g['groupId']):g['voteCount'] for c in state['ballotItemWithBreakdown']['summaryResults']['ballotOptions'] for g in c['groupResults']};assert method_sums==state_method
    dump('native-associations.json.gz',units);dump('parent-identities.json',parents);dump('method-state-controls.json',[dict(candidate=k[0],method_id=k[1],native_sum=v,locality_sum=api_method_sums[k],state=v) for k,v in method_sums.items()]);dump('bulk-blank-id-rows.json',{'rows':bulkblank,'count':len(bulkblank),'note':'Retained in constituent vectors, not deduplicated; counts checked literal zero.'})
    assert len(units)==2669 and len({u['api_native']['precinct']['id'] for u in units})==2669
    # President bulk independent candidate totals/localities/native vectors.
    ph=load('2024-president.json.gz');pc=['cs317','cs318','cs319','cs320','cs322','cs321','wi-cc122'];pres_errors=[]
    for r in [r for r in ph['rows'] if r['scope']=='Precinct']:
        code=parents[r['parent']]['code']; matches=[rs for (office,co,name),rs in grouped.items() if office=='cc122' and co==code and tuple(sum(int(z['cells'][bi['WriteInVote' if cid=='wi-cc122' else 'TOTAL_VOTES']]) for z in rs if z['cells'][bi['CandidateId']]==cid) for cid in pc)==tuple(r['votes'])]
        if len(matches)!=1:pres_errors.append({'record':r['record'],'matches':len(matches)})
    dump('president-bulk-control.json',{'native_unique_vector_matches':2669-len(pres_errors),'ambiguities':pres_errors,'scope':'Same-election numerical controls only; no automatic Senate/president precinct equivalence.'})
    # Read captured peer bytes only; no dependency on mutable peer helper or values for own build.
    with tarfile.open(ROOT/'peer-capture.tar.gz','r:gz') as t:
        peer=json.load(t.extractfile('data/turnout/priority-set.json'));csvrows=list(csv.DictReader(io.TextIOWrapper(t.extractfile('data/county-turnout.csv'),encoding='utf-8')))
        parentrows=list(csv.DictReader(io.TextIOWrapper(t.extractfile('data/turnout/locality-turnout.csv'),encoding='utf-8')))
    ownorder=json.loads((ROOT/'independent-priority.json').read_text());byrec={u['historical']['record']:u for u in units};diff=[];checks=collections.Counter()
    def check(rec,field,own,other):
        checks[field]+=1
        if own!=other:diff.append(dict(record=rec,field=field,own=own,peer=other))
    def key(n):return f'va:161257:csv-record:{n:04d}'
    for n,(r,p) in enumerate(zip(ownorder['native']['order'],peer['ordered_units']),1):
        u=byrec[r['record']];h=u['historical'];a=u['api_native'];check(h['record'],'ordered_key',key(h['record']),p['key']);check(h['record'],'literal',h['name'],p['label']);check(h['record'],'parent',h['parent'],p['parent_label']);check(h['record'],'candidates',h['votes'],[p['candidate_votes'][str(i)] for i in (2,3,4)]);check(h['record'],'cumulative',r['cumulative'],p['cumulative_votes']);check(h['record'],'whole_api_native',a,p['source_native_constituents']['enr_api']['full_native_object']);check(h['record'],'fips',u['fips'],p['parent_fips']);check(h['record'],'code',u['code'],p['parent_locality_code']);check(h['record'],'csv_total',str(h['total']),csvrows[n-1]['reported_candidate_writein_marks']);check(h['record'],'uuid',a['precinct']['id'],csvrows[n-1]['enr_native_id'])
    check(None,'all_order',[key(r['record']) for r in ownorder['native']['order']],peer['full_all_unit_order']);check(None,'priority_order',[key(r['record']) for r in ownorder['native']['order'][:1538]],peer['ordered_priority_keys']);check(None,'minimum80_count',ownorder['native']['minimum80_count'],peer['minimum80']['count']);check(None,'minimum80_votes',ownorder['native']['at_crossing'],peer['minimum80']['votes'])
    for r,p in zip(ownorder['locality']['order'],parentrows):
        check(r['record'],'parent_order',r['name'],p['locality']);check(r['record'],'parent_candidate_vector',r['votes'],[int(p[x]) for x in ['senate_2024_kaine','senate_2024_cao','senate_2024_generic_writeins']]);check(r['record'],'parent_native_count',sum(u['historical']['parent']==r['name'] for u in units),int(p['native_unit_count']))
    dump('peer-reconciliation.json',{'pre_peer_witness':'pre-peer-witness.json','captured_peer':'peer-capture.json','scope':'Captured priority-set, county native CSV and locality CSV; whole candidate/party/native/method objects compared to independent original extraction. Full original bytes pinned. No peer values adopted. Comparator/administrative additional audit separately.','counts':dict(checks),'differences':diff,'own_native':2669,'own_parents':133,'exact_minimum80':ownorder['native']['minimum80_count'],'coordinator_acceptance':None,'legal_eligible_generic_scope_established':False})
    print('source bridges',len(units),'blank-id rows',len(bulkblank),'president ambiguities',len(pres_errors),'peer differences',len(diff))
if __name__=='__main__':main()
