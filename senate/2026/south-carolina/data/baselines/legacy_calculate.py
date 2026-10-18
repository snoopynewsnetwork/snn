"""Complete original-native method weights and bounded conditional targets."""
from calculate import *
def main():
    native=list(csv.DictReader(gzip.open(BASE/'legacy-native-baselines.csv.gz','rt')));keys={(r['contest_label'],r['county'],r['name']):r for r in native};groups=collections.defaultdict(dict);sources={}
    for r in csv.DictReader(gzip.open(BASE/'legacy-candidate-methods.csv.gz','rt')):
        k=(r['contest_label'],r['county'],r['native_name'],r['method_name']);cid=int(r['analysis_candidate_id']);assert cid not in groups[k];groups[k][cid]=int(r['votes']);sources[k]=r['source_id']
    baselines=[];targets=[];states=[]
    for lab in LABELS:
        rs=[];aa,bb=PAIRS[lab]
        for (label,county,name,method),v in groups.items():
            if label!=lab:continue
            n=keys[(label,county,name)];assert set(v)==set(json.loads(n['choice_analysis_ids']))
            A,B=v[aa],v[bb];total=sum(v.values());w=A+B
            r=dict(contest_label=lab,geography_key=n['geography_key']+':method:'+method,county=county,name=name+' / '+method,native_type='LegacyMethod',county_fips=n['county_fips'],A_name=n['A_name'],B_name=n['B_name'],A=A,B=B,other=total-w,source_id=sources[(label,county,name,method)],raw_method=method)
            rs.append(r)
        W=[r['A']+r['B']for r in rs];S=[r['A']/w if w else None for r,w in zip(rs,W)];T=sum(W)
        combined=sum(int(n['pair_votes'])for n in native if n['contest_label']==lab);assert T==combined
        for r,w,s in zip(rs,W,S):baselines.append(dict(**r,pair_votes=w,pair_weight=w/T,A_pair_share=s,local_tie_A_share=.5 if w else None,local_Aplus1_share=.505 if w else None,local_tie_shift_pp=100*(.5-s)if w else None,local_Aplus1_shift_pp=100*(.505-s)if w else None,share_pp1_net_gain=.02*w))
        for target in [0,.01]:
            sol=solve(W,S,target);states.append(dict(contest_label=lab,target_pair_margin_pp=target*100,native_methods=len(rs),**sol))
            for r,w,s in zip(rs,W,S):targets.append(unitrow(r,w,s,r['other'],sol,target,lab+'__legacy_methods',lab,'all original precinct/method source cells'))
    rows(BASE/'legacy-method-baselines.csv.gz',baselines);rows(BASE/'legacy-method-targets.csv.gz',targets);dump(BASE/'legacy-method-state-scenarios.json',states)
    print(compact(dict(native_methods=len(baselines),targets=len(targets),states=len(states))))
if __name__=='__main__':main()
