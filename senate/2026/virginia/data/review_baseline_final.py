"""Independent original-byte, complete-source and conditional-math review.

Does not import producer code or read the active turnout's current derivatives.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, gzip, hashlib, io, json, math, re, tarfile

S = Path(__file__).resolve().parents[1]
B = S/'data/baselines'
N = 0
MAX = 0.

def ck(v, label=''):
    global N
    N += 1
    assert v, (N,label)

def close(a,b,tol=1e-7):
    global MAX
    ck(math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol,(a,b,abs(a-b)))
    MAX=max(MAX,abs(a-b))

def sha(b): return hashlib.sha256(b).hexdigest()
def load(p):
    p=B/p;b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def rows(p):
    with (B/p).open(newline='') as f:return list(csv.DictReader(f))

mf=load('asset-manifest.json');ck(mf['excludes_only']=='data/baselines/asset-manifest.json')
actual={str(p.relative_to(S)) for p in B.rglob('*') if p.is_file()}|{'county-partisanship.md','data/county-baselines.csv'}
ck(len(mf['files'])==299 and {r['path'] for r in mf['files']}==actual-{'data/baselines/asset-manifest.json'})
for r in mf['files']:
    b=(S/r['path']).read_bytes();ck(len(b)==r['bytes']<40000000 and sha(b)==r['sha256'])
for p in B.rglob('*'):ck(not set(p.parts)&{'__pycache__','node_modules','.venv','.pytest_cache'})

src={};source_entities=0
for r in load('source/input-pins.json')['sources']:
    b=(S/r['receipt_path']).read_bytes();ck(len(b)==r['receipt_bytes'] and sha(b)==r['receipt_sha256'])
    ck(json.loads(b)==r['receipt'])
    for e in r['entities']:
        b=(S/e['path']).read_bytes();ck(len(b)==e['bytes'] and sha(b)==e['sha256'])
        raw=gzip.decompress(b);ck(len(raw)==e['raw_bytes'] and sha(raw)==e['raw_sha256']);source_entities+=1
    src[r['id']]=raw
ck(len(src)==166)
w=load('pre-peer-witness.json');a=(B/w['archive']['path']).read_bytes();ck(sha(a)==w['archive']['sha256'])
with tarfile.open(fileobj=io.BytesIO(a),mode='r:gz') as z:
    for r in w['files']:ck(sha(z.extractfile(r['path']).read())==r['sha256'])

# Parse every literal CSV row independently, including physical positions.
hist={};native={};parent_aggregates={};source_record_count=0;source_candidate_cells=0
for key,sid,hid,expected in [('2024-senate','fresh-2024-csv','fresh-2024-html',2669),('2024-president','president-csv','president-html',2669),('2020-senate','fresh-2020-csv','fresh-2020-html',2846),('2018-senate','fresh-2018-csv','fresh-2018-html',2825)]:
    h=load('extracted/'+key+'.json.gz');original=csv.reader(io.StringIO(src[sid].decode('utf-8-sig'),newline=''));rawrows=[];prev=0
    for ordinal,cells in enumerate(original,1):
        rawrows.append(dict(record=ordinal,line_start=prev+1,line_end=original.line_num,cells=cells));prev=original.line_num
    ck(rawrows==h['raw_records']);source_record_count+=len(rawrows)
    for a,b in zip(rawrows,h['raw_records'],strict=True):
        for x,y in zip(a['cells'],b['cells'],strict=True):ck(x==y)
    header=rawrows[0]['cells'];party=rawrows[1]['cells'];last=header.index('Total Votes Cast');ck(header==h['headers'] and party==h['parties'])
    ck(h['candidate_columns']==[dict(position=i,name=header[i],party_literal=party[i]) for i in range(2,last)])
    hydrate=json.loads(re.search(rb'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',src[hid]).group(1));ck(hydrate==load('extracted/'+hid+'-hydration.json.gz'))
    contest=hydrate['props']['pageProps']['contest']
    byname={r['displayName']:r for r in contest['candidates']}
    ck(all(header[j] in byname for j in range(2,len(header))))
    expected_rows=[];parent=None
    for raw in rawrows[2:]:
        cells=raw['cells'];scope,name=cells[:2]
        if scope=='Locality':parent=name
        votes=[int(v) for v in cells[2:last]];source_candidate_cells+=len(votes)
        ck(sum(votes)==int(cells[last]))
        expected_rows.append(dict(source_key=f"{key}:record:{raw['record']}",record=raw['record'],line_start=raw['line_start'],line_end=raw['line_end'],scope=scope,parent=parent if scope!='State' else None,name=name,votes=votes,total=int(cells[last]),undervotes_literal=cells[last+1] if len(cells)>last+1 else None))
    ck(expected_rows==h['rows'])
    ns=[r for r in expected_rows if r['scope']=='Precinct'];ps=[r for r in expected_rows if r['scope']=='Locality'];st=next(r for r in expected_rows if r['scope']=='State')
    ck(len(ns)==expected and len(ps)==133 and len({r['name'] for r in ps})==133)
    ck(sum(r['name'].endswith(' City') for r in ps)==38 and sum(r['name'].endswith(' County') for r in ps)==95)
    ck([sum(r['votes'][i] for r in ns) for i in range(last-2)]==st['votes']==h['native_sums'])
    for i,v in enumerate(st['votes']):ck(byname[header[i+2]]['nVotes']==v)
    agg={}
    for p in ps:
        children=[r for r in ns if r['parent']==p['name']]
        agg[p['name']]=dict(votes=[sum(r['votes'][i] for r in children) for i in range(last-2)],total=sum(r['total'] for r in children))
    hist[key]=h;native[key]=ns;parent_aggregates[key]=agg

ck(sum(map(len,native.values()))==11009)
for file,scope,count in [('native-baselines.csv','Precinct',11009),('../county-baselines.csv','Locality',532)]:
    table=rows(file);ck(len(table)==count)
    for r in table:
        h=hist[r['contest']];x=next(a for a in h['rows'] if a['source_key']==r['source_key']);v=x['votes'];pair=sum(v[:2]);total=sum(z['total'] for z in native[r['contest']]);P=sum(sum(z['votes'][:2]) for z in native[r['contest']])
        ck(scope==r['scope']==x['scope'] and r['literal_label']==x['name'] and int(r['source_record'])==x['record'])
        ck(json.loads(r['candidate_votes_json'])==v and json.loads(r['candidate_names_json'])==[q['name'] for q in h['candidate_columns']] and json.loads(r['candidate_parties_json'])==[q['party_literal'] for q in h['candidate_columns']])
        ck(int(r['A_votes'])==v[0] and int(r['B_votes'])==v[1] and int(r['other_reported'])==sum(v[2:]) and int(r['all_candidate_reported'])==x['total'])
        ck(int(r['pair_votes'])==pair and int(r['net_A_minus_B'])==v[0]-v[1] and not r['ballots_cast'] and not r['registration'])
        close(float(r['pair_weight']),pair/P,1e-14);close(float(r['reported_weight']),x['total']/total,1e-14);close(float(r['gain_net_per_one_A_share_pp']),.02*pair)
        if pair:close(float(r['A_pair_share']),v[0]/pair,1e-14);close(float(r['pair_margin']),(v[0]-v[1])/pair,1e-14)
        else:ck(not r['A_pair_share'] and not r['pair_margin'])
        ck(int(r['native_aggregate_all'])==(parent_aggregates[r['contest']][x['name']]['total'] if scope=='Locality' else x['total']))

api={r['source']:r for r in load('extracted/api-native-objects.json.gz')};ck(len(api)==134)
original_api={sid:json.loads(src[sid]) for sid in api}
for sid,r in api.items():
    raw=original_api[sid]
    for k in ['ballotItemWithBreakdown','precincts','election','localityElections','voterRegistration','voterTurnout','jurisdiction']:ck(r[k]==raw[k])
def ptr(x,path):
    for k in path.split('/')[1:]:x=x[int(k)] if isinstance(x,list) else x[k]
    return x
method_rows=load('extracted/method-rows.json.gz')
for r in method_rows:
    g=ptr(original_api[r['source']],r['path']);ck(all(r[k]==v for k,v in g.items()))
    opt=ptr(original_api[r['source']],r['path'].rsplit('/groupResults/',1)[0]);ck(opt['id']==r['candidate_id'] and opt['nativeId']==r['candidate_nativeId'])
association=load('native-associations.json.gz');ck(len(association)==2669)
method_source={}
for u in association:
    x=u['api_native'];index={o['nativeId']:o for o in x['ballotOptions']};original=u['historical']
    # Historical source rows remain exact typed records, not an inferred polygon join.
    ck(original in hist['2024-senate']['rows'])
    for g in index['cs534']['groupResults']:
        v=[next(a['voteCount'] for a in index[c]['groupResults'] if a['groupId']==g['groupId']) for c in ['cs534','cs535','wi-cc200']]
        method_source[original['source_key']+':method:'+g['groupId']]=v
ck(len(method_source)==13345)

# Independent direct evaluations at sorted clipping breakpoints, then linear interpolation.
def clipped_root(weights,qs,target):
    points=sorted({-1.,1.}|{-q for w,q in zip(weights,qs) if w}|{1-q for w,q in zip(weights,qs) if w})
    def net(d):return math.fsum(w*(2*min(1,max(0,q+d))-1) for w,q in zip(weights,qs))
    lo,hi=0,len(points)-1
    while hi-lo>1:
        k=(lo+hi)//2
        if net(points[k])<target:lo=k
        else:hi=k
    a,b=points[lo],points[hi];fa,fb=net(a),net(b)
    ck(fa-1e-7<=target<=fb+1e-7)
    return a if fb==fa else a+(target-fa)*(b-a)/(fb-fa)

def audit_scenario(rs, summary, W,Q,V, fields):
    P=math.fsum(W);F=math.fsum(V);base=math.fsum(w*(2*q-1) for w,q in zip(W,Q));target=float(summary['target_pair_margin'])*P
    close(float(summary['pair_denominator']),P);close(float(summary[fields['F']]),F);close(float(summary['baseline_net']),base)
    d=clipped_root(W,Q,target);unbounded=(target-base)/(2*P)
    close(float(summary[fields['delta']]),d,1e-10);close(float(summary[fields['unbound']]),unbounded,1e-12)
    nets=[]
    for r,w,q,v in zip(rs,W,Q,V,strict=True):
        close(float(r[fields['pool']]),w);close(float(r[fields['volume']]),v)
        if w:
            close(float(r[fields['q']]),q,1e-13);share=min(1,max(0,q+d));close(float(r[fields['share']]),share,1e-10);close(float(r[fields['net']]),w*(2*share-1))
            required=(w+target-(base-w*(2*q-1)))/(2*w);close(float(r[fields['selected']]),required,1e-8)
            ck(r['selected_only_status']==('secured' if required<0 else 'impossible' if required>1 else 'feasible'))
            nets.append(w*(2*share-1))
        else:ck(not r[fields['q']] and not r[fields['share']] and r['selected_only_status']=='no-positive-pool')
        close(float(r['gain_net_per_share_pp']),.02*w)
        close(float(r['pair_weight']),w/P,1e-13);close(float(r[fields['weight']]),v/F,1e-13)
    close(math.fsum(nets),target,1e-6)
    return abs(float(summary[fields['delta']])-d),abs(math.fsum(nets)-target)

historical=defaultdict(list)
for r in rows('historical-unit-targets.csv'):historical[r['scenario']].append(r)
max_shift=max_residual=0.
hf=dict(F='all_candidate_denominator',delta='bounded_share_shift',unbound='unbounded_share_shift',pool='pair_volume',volume='all_candidate_volume',q='baseline_A_share',share='bounded_target_share',net='bounded_target_net',selected='selected_only_required_share',weight='all_candidate_weight')
for s in rows('historical-state-targets.csv'):
    rs=historical[s['scenario']];key=s['volume_basis'];h=hist[key]
    xs=native[key] if s['scope']=='native' else [dict(source_key=r['source_key'],**parent_aggregates[key][r['name']]) for r in h['rows'] if r['scope']=='Locality']
    ck([r['source_key'] for r in rs]==[r['source_key'] for r in xs])
    W=[sum(r['votes'][:2]) for r in xs];Q=[r['votes'][0]/w if w else 0 for r,w in zip(xs,W)];V=[r['total'] for r in xs]
    a,b=audit_scenario(rs,s,W,Q,V,hf);max_shift=max(max_shift,a);max_residual=max(max_residual,b)

settings=load('build-settings.json');sensitivity=defaultdict(list)
for r in rows('sensitivity-localities.csv'):sensitivity[r['scenario']].append(r)
sf=dict(F='all_denominator',delta='bounded_shift',unbound='unbounded_shift',pool='pair_volume',volume='volume',q='baseline_share',share='target_share',net='target_net',selected='selected_only_raw_share',weight='all_weight')
for s in rows('sensitivity-state.csv'):
    rs=sensitivity[s['scenario']];ck(len(rs)==133 and len({r['locality'] for r in rs})==133)
    mix=parent_aggregates[s['mix_anchor']];pref=parent_aggregates[s['preference_anchor']];base=parent_aggregates['2024-senate'];allvolume=settings['volume_bases'][s['volume_anchor']];mixden=sum(r['total'] for r in mix.values());W=[];Q=[];V=[]
    names=[r['name'] for r in hist[s['preference_anchor']]['candidate_columns']];candidates=Counter()
    for r in rs:
        name=r['locality'];v=allvolume*mix[name]['total']/mixden;p=sum(base[name]['votes'][:2])/base[name]['total'];w=v*p;q=pref[name]['votes'][0]/sum(pref[name]['votes'][:2]);V.append(v);W.append(w);Q.append(q)
        close(float(r['participation']),p,1e-13)
        allocations=json.loads(r['other_allocations_json']);others=pref[name]['votes'][2:]
        ck(set(allocations)==set(names[2:]))
        for i,n in enumerate(names[2:]):close(allocations[n],1 if len(others)==1 else others[i]/sum(others),1e-13)
        counts=json.loads(r['target_candidate_votes_json']);close(math.fsum(counts.values()),v)
        close(counts[names[0]],w*float(r['target_share']));close(counts[names[1]],w*(1-float(r['target_share'])))
        for n,f in allocations.items():close(counts[n],v*(1-p)*f)
        candidates.update(counts)
    a,b=audit_scenario(rs,s,W,Q,V,sf);max_shift=max(max_shift,a);max_residual=max(max_residual,b)
    targetcounts=json.loads(s['target_candidate_votes_json']);ck(set(targetcounts)==set(candidates))
    for n,v in targetcounts.items():close(v,candidates[n],1e-6)

method_targets=defaultdict(list)
for r in rows('native-method-targets.csv'):method_targets[r['target']].append(r)
for target,rs in method_targets.items():
    ck(len(rs)==13345 and {r['key'] for r in rs}==set(method_source))
    W=[sum(method_source[r['key']][:2]) for r in rs];Q=[method_source[r['key']][0]/w if w else 0 for r,w in zip(rs,W)];V=[sum(method_source[r['key']]) for r in rs];P=math.fsum(W);delta=clipped_root(W,Q,float(target)*P)
    for r,w,q,v in zip(rs,W,Q,V):
        close(float(r['volume']),v);close(float(r['pair']),w)
        if w:close(float(r['target_share']),min(1,max(0,q+delta)),1e-10)
        else:ck(not r['baseline_share'] and r['selected_status']=='no-positive-pool')

result=dict(status='pass_independent_original_source_baseline_and_clipped_math_review',checks=N,exact_owned_targets=299,complete_owned_files=300,complete_original_source_receipts=166,complete_original_entities=source_entities,original_logical_contest_records=source_record_count,original_candidate_cells=source_candidate_cells,required_contests=4,all_parent_localities=133,counties=95,independent_cities=38,native_baseline_rows=11009,locality_election_baseline_rows=532,source_native_method_units=13345,candidate_method_source_objects=40035,historical_state_scenarios=len(historical),historical_target_rows=sum(map(len,historical.values())),historical_volume_mix_preference_scenarios=len(sensitivity),sensitivity_unit_targets=sum(map(len,sensitivity.values())),method_target_rows=sum(map(len,method_targets.values())),maximum_independent_bounded_shift_difference=max_shift,maximum_independent_state_net_residual=max_residual,source_scalar_or_null_repairs=False,producer_imports_writes_or_current_peer_discovery=False,all_nonpriority_retained=True,raw_2018_locality_footer_generic_difference_unallocated=36,reported_parent_footer_weights_source_scoped='2018 raw locality footer reported weights retain36mark shortfall against native denominator; complete native-aggregated parent scenario weights close separately, no rescaling',current_geographic_or_legal_writein_feed_approval=False,reviewed_manifest=dict(path='data/baselines/asset-manifest.json',bytes=(B/'asset-manifest.json').stat().st_size,sha256=sha((B/'asset-manifest.json').read_bytes())))
(S/'data/coordinator-baseline-final-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],checks=N,native_rows=11009,scenarios=len(historical)+len(sensitivity),max_shift_difference=max_shift,max_net_residual=max_residual)))
