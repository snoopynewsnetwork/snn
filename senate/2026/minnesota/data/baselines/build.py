"""Offline baseline build from independent original-workbook extraction."""
import collections,json
from extract import H,S,METHOD,readcsv,writecsv,dump
from definitions import CONTESTS

def baseline(c,raw,level,key):
 a=int(raw[c['A_field']]);b=int(raw[c['B_field']]);total=int(raw[c['prefix']+'TOTAL']);pair=a+b;ballots=int(raw['TOTVOTING']);share=a/pair if pair else None
 bucket_max=max(int(raw[f]) for f,_,_,_ in c['candidates']);winners=[(f,n) for f,n,_,_ in c['candidates'] if int(raw[f])==bucket_max] if total else []
 return dict(all_source_bucket_max_votes=bucket_max,all_source_bucket_winner_fields=json.dumps([f for f,_ in winners]),all_source_bucket_winner_names=json.dumps([n for _,n in winners]),outcome_scope='outcome compares A/B only; all-source bucket winners include generic-WI scope, not adjudicated eligible individual write-ins',contest=c['id'],year=c['year'],election_date=c['date'],stage='general',role=c['role'],level=level,unit_key=key,county_fips=raw['county_fips'],COUNTYNAME=raw['COUNTYNAME'],MCDNAME=raw.get('MCDNAME',''),PCTNAME=raw.get('PCTNAME',''),VTDID=raw.get('VTDID',''),source_id=f"sos-{c['year']}-precinct-original",source_sheet='Precinct-Results',source_row=raw.get('source_row','aggregated; see native source rows'),A_field=c['A_field'],A_name=next(x[1] for x in c['candidates'] if x[0]==c['A_field']),A_source_party='Democratic-Farmer-Labor',A_analytical_group='D',B_field=c['B_field'],B_name=next(x[1] for x in c['candidates'] if x[0]==c['B_field']),B_source_party='Republican',A=a,B=b,other=total-pair,all_candidate_votes=total,pair_votes=pair,pair_participation=pair/total if total else '',A_pair_share=share if share is not None else '',A_all_share=a/total if total else '',pair_margin_pp=100*(a-b)/pair if pair else '',all_margin_pp=100*(a-b)/total if total else '',net_A_minus_B=a-b,outcome='A' if a>b else 'B' if b>a else 'tie' if pair else 'no_positive_pair',closeness='no_positive_pair' if not pair else '<=5pp' if abs(100*(a-b)/pair)<=5 else '>5-10pp' if abs(100*(a-b)/pair)<=10 else '>10pp',TOTVOTING=ballots,ballots_minus_contest=ballots-total,REG7AM=int(raw['REG7AM']),EDR=int(raw['EDR']),REG7AM_plus_EDR=int(raw['REG7AM'])+int(raw['EDR']),under_votes='',over_votes='',blank_votes='',valid_named_writeins='',current_2026_equivalence='unverified',source_url=c['source_url'])

def rank(rows,field,key):
 ordered=sorted(rows,key=lambda r:(-int(r[field]),r[key]));total=sum(int(r[field]) for r in ordered);cum=0;out=[]
 for i,r in enumerate(ordered,1):
  prev=cum;cum+=int(r[field]);out.append(dict(rank=i,unit_key=r[key],COUNTYNAME=r['COUNTYNAME'],VTDID=r.get('VTDID',''),source_row=r.get('source_row',''),contest_votes=int(r[field]),cumulative_votes=cum,all_state_contest_votes=total,share=int(r[field])/total,cumulative_share=cum/total,in_minimum80=prev*5<total*4))
 selected=[r for r in out if r['in_minimum80']];return out,dict(total=total,top15=sum(r['contest_votes'] for r in out[:15]),minimum80_count=len(selected),minimum80_votes=selected[-1]['cumulative_votes'],previous_votes=selected[-2]['cumulative_votes'],crossing_key=selected[-1]['unit_key'],crossing_votes=selected[-1]['contest_votes'],outside_votes=total-selected[-1]['cumulative_votes'],order=[r['unit_key'] for r in out],priority_keys=[r['unit_key'] for r in selected],priority_names=[r['COUNTYNAME'] for r in selected])

def main():
 native=[];county=[];municipal=[];candidates=[];state=[]
 for cid,c in CONTESTS.items():
  c=dict(c,id=cid);y=c['year'];rr=readcsv(H/f'native-{y}.csv.gz');cc=readcsv(H/f'county-controls-{y}.csv');mm=readcsv(H/f'municipal-controls-{y}.csv.gz')
  for raw in rr:native.append(baseline(c,raw,'native',raw['native_key']))
  for raw in cc:county.append(baseline(c,raw,'county',raw['county_key']))
  # JSON-array key retains municipality names losslessly, scoped to source year + county.
  for raw in mm:municipal.append(baseline(c,raw,'municipal',json.dumps([y,raw['county_fips'],raw['MCDNAME']],ensure_ascii=False,separators=(',',':'))))
  for level,records,keyfn in [('native',rr,lambda r:r['native_key']),('county',cc,lambda r:r['county_key']),('municipal',mm,lambda r:json.dumps([y,r['county_fips'],r['MCDNAME']],ensure_ascii=False,separators=(',',':')))]:
   for raw in records:
    for f,name,party,control in c['candidates']:
     candidates.append(dict(contest=cid,level=level,unit_key=keyfn(raw),county_fips=raw['county_fips'],source_id=f'sos-{y}-precinct-original',source_sheet='Precinct-Results',source_row=raw.get('source_row','aggregate'),source_field=f,candidate_key=cid+':'+f,candidate_name=name,source_party=party,analytical_group='D' if f==c['A_field'] else 'R' if f==c['B_field'] else 'unaffiliated_with_analytical_pair',votes=int(raw[f]),writein_scope='generic registered and non-registered' if f.endswith('WI') else 'named ballot ticket',source_url=c['source_url']))
  sums={f:sum(int(r[f]) for r in rr) for f,_,_,_ in c['candidates']};assert sums=={f:n for f,_,_,n in c['candidates']}
  a=sums[c['A_field']];b=sums[c['B_field']];total=sum(sums.values());pair=a+b
  state.append(dict(contest=cid,role=c['role'],native_rows=len(rr),counties=len(cc),municipal_groups=len(mm),A=a,B=b,other=total-pair,all_candidate_votes=total,pair_votes=pair,A_pair_share=a/pair,pair_margin_pp=100*(a-b)/pair,all_margin_pp=100*(a-b)/total,net_A_minus_B=a-b,unbounded_tie_shift_share_pp=100*(b-a)/(2*pair),unbounded_Aplus1_shift_share_pp=100*(b-a)/(2*pair)+.5,ballots=sum(int(r['TOTVOTING']) for r in rr),zero_contest_native_rows=sum(int(r[c['prefix']+'TOTAL'])==0 for r in rr),contest_exceeds_ballots_rows=sum(int(r[c['prefix']+'TOTAL'])>int(r['TOTVOTING']) for r in rr),candidate_controls=sums,all_named_controls_match_primary=True,A_counties=sum(int(r[c['A_field']])>int(r[c['B_field']]) for r in cc)))
 for group in [native,county,municipal]:
  for cid in CONTESTS:
   units=[r for r in group if r['contest']==cid];pv=sum(r['pair_votes'] for r in units);av=sum(r['all_candidate_votes'] for r in units)
   for r in units:r['pair_weight']=r['pair_votes']/pv;r['all_candidate_weight']=r['all_candidate_votes']/av
 named=readcsv(S/'named-writeins-2020.csv') if (S/'named-writeins-2020.csv').exists() else []
 for r in county:
  if r['contest']=='2020-senate' and named:r['valid_named_writeins']=sum(int(x['votes']) for x in named if x['county_fips']==r['county_fips'])
 writecsv(H/'native-baselines.csv.gz',native);writecsv(H.parent/'county-baselines.csv',county);writecsv(H/'municipal-baselines.csv.gz',municipal);writecsv(H/'candidate-votes.csv.gz',candidates);dump(S/'candidate-identities.json',CONTESTS);dump(H/'state-baselines.json',state)
 priorities={}
 for year,prefix in [(2024,'USSEN'),(2022,'MNGOV'),(2020,'USSEN')]:
  for level,p,key in [('county',H/f'county-controls-{year}.csv','county_key'),('native',H/f'native-{year}.csv.gz','native_key')]:
   ordered,contract=rank(readcsv(p),prefix+'TOTAL',key);writecsv(H/f'{level}-{year}-ranked.csv.gz',ordered);priorities[f'{year}-{level}']=contract
 for year,prefix in [(2024,'USSEN'),(2022,'MNGOV'),(2020,'USSEN')]:
  mm=readcsv(H/f'municipal-controls-{year}.csv.gz')
  for r in mm:r['derived_key']=json.dumps([year,r['county_fips'],r['MCDNAME']],ensure_ascii=False,separators=(',',':'))
  ordered,contract=rank(mm,prefix+'TOTAL','derived_key');writecsv(H/f'municipal-{year}-ranked.csv.gz',ordered);priorities[f'{year}-municipal']=contract
 priorities['coordinator_acceptance_path']='data/coordinator-priority-acceptance.json'
 priorities['acceptance']='Historical research dispatch accepted only by external coordinator publication; no current legal reporting/geometry approval'
 dump(H/'priority-contract.json',priorities)
 print(json.dumps(state,indent=2))
if __name__=='__main__':main()
