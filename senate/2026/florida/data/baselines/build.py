#!/usr/bin/env python3
"""Build historical county baselines, explicit source conflicts and exact priorities."""
import csv,gzip,io,json,re
from collections import Counter,defaultdict
from pathlib import Path
from parse_sources import D,Tables,csvwrite,writejson,sha

def readcsv(p):
 with (gzip.open(p,'rt',newline='') if p.suffix=='.gz' else p.open(newline='')) as f:return list(csv.DictReader(f))
def norm(s):return s.lower().replace(' county','').strip()
def main():
 gaz=list(csv.DictReader(io.StringIO(gzip.decompress((D/'source/census-gazetteer.body.gz').read_bytes()).decode('utf-8-sig')),delimiter='\t'));gaz=[{k.strip():v.strip() for k,v in r.items()} for r in gaz];fips={norm(r['NAME']):r['GEOID'] for r in gaz};assert len(fips)==67
 official=readcsv(D/'official-county-candidates.csv');raw=readcsv(D/'compiled-county-candidates.csv');native=readcsv(D/'native-units.csv.gz');bycounty=defaultdict(list)
 for r in official:bycounty[(r['year'],r['contest'],norm(r['county']))].append(r)
 rawby=defaultdict(list)
 for r in raw:rawby[(r['year'],r['contest'],norm(r['county']))].append(r)
 geo={norm(r['county']):r['county_code'] for r in raw};rows=[];recon=[];native_counts=Counter((r['year'],r['contest'],norm(r['county'])) for r in native)
 for k,rs in sorted(bycounty.items()):
  year,contest,nm=k;rr=rawby[k];a=next(r for r in rs if r['party']=='DEM');b=next(r for r in rs if r['party']=='REP');A=int(a['votes']);B=int(b['votes']);total=sum(int(r['votes']) for r in rs);pair=A+B;other=total-pair
  rcat=Counter()
  for r in rr:rcat[r['category']]+=int(r['votes'])
  rawA=sum(int(r['votes']) for r in rr if r['party']=='DEM');rawB=sum(int(r['votes']) for r in rr if r['party']=='REP')
  row={'county_fips':fips[nm],'county_code':geo[nm],'county':rs[0]['county'],'year':year,'contest':contest,'stage':'general','seat_relationship':'other_Class_I_priority' if year=='2024' and contest=='senate' else 'same_Class_III_midterm' if contest=='senate' else 'presidential_separate','A_name':a['candidate_name'],'A_party':'DEM','B_name':b['candidate_name'],'B_party':'REP','A_votes':A,'B_votes':B,'other_valid_votes':other,'valid_named_writein_votes':sum(int(r['votes']) for r in rs if r['party']=='WRI'),'all_candidate_votes':total,'pair_votes':pair,'pair_participation_of_valid':pair/total,'A_pair_share':A/pair,'A_all_share':A/total,'pair_margin_pp':100*(A-B)/pair,'all_candidate_margin_pp':100*(A-B)/total,'A_minus_B_votes':A-B,'winner':'A' if A>B else 'B' if B>A else 'tie','closeness_band':'0_to_5pp' if abs(100*(A-B)/pair)<=5 else 'over5_to10pp' if abs(100*(A-B)/pair)<=10 else 'over10pp','compiled_A_votes':rawA,'compiled_B_votes':rawB,'compiled_other_printed_votes':rcat['named_candidate']-rawA-rawB,'compiled_generic_writein_marks':rcat['generic_writein_marks'],'compiled_overvotes':rcat['overvotes'],'compiled_undervotes':rcat['undervotes'],'native_context_count':native_counts[k],'native_method':'not_provided_in_19field_schema','source_id':rs[0]['source_id'],'source_tr_1based':rs[0]['source_tr_1based'],'source_raw_sha256':rs[0]['raw_sha256'],'source_status':'DOS Official Results','ballots_cast':'','registered_voters':'','blank_votes':'','compiled_to_official_named_discrepancy':rcat['named_candidate']-(total-sum(int(r['votes']) for r in rs if r['party']=='WRI'))}
  rows.append(row)
  for r in rs:
   matches=[z for z in rr if z['category']=='named_candidate' and z['party']==r['party'] and z['candidate_name'].lower()==r['candidate_name'].lower()];assert len(matches)<=1
   native_vote=int(matches[0]['votes']) if matches else None
   recon.append({'year':year,'contest':contest,'county_fips':fips[nm],'county_code':geo[nm],'county':r['county'],'candidate_name':r['candidate_name'],'party':r['party'],'official_votes':int(r['votes']),'compiled_named_votes':native_vote,'compiled_minus_official':native_vote-int(r['votes']) if native_vote is not None else None,'comparison_status':'named_source_difference' if native_vote is not None and native_vote!=int(r['votes']) else 'matched_named' if native_vote is not None else 'no_named_native_allocation_generic_scope_separate','official_source_id':r['source_id'],'official_source_tr':r['source_tr_1based']})
 for year,contest in [(str(y),c) for y,c in [(2024,'senate'),(2022,'senate'),(2024,'president'),(2020,'president')]]:
  rs=[r for r in rows if r['year']==year and r['contest']==contest];P=sum(r['pair_votes'] for r in rs);V=sum(r['all_candidate_votes'] for r in rs)
  for r in rs:r['state_pair_weight']=r['pair_votes']/P;r['state_all_candidate_weight']=r['all_candidate_votes']/V;r['gain_net_votes_per_1pp_A_share']=.02*r['pair_votes'];r['net_contribution_pair_margin_pp']=100*r['A_minus_B_votes']/P
 csvwrite(D.parent/'county-baselines.csv',rows);csvwrite(D/'source-discrepancies.csv',recon)
 states=[]
 for year,contest in [('2024','senate'),('2022','senate'),('2024','president'),('2020','president')]:
  rs=[r for r in rows if r['year']==year and r['contest']==contest];s={'year':year,'contest':contest,'counties':len(rs),'A_name':rs[0]['A_name'],'B_name':rs[0]['B_name']}
  for k in ['A_votes','B_votes','other_valid_votes','valid_named_writein_votes','all_candidate_votes','pair_votes','compiled_generic_writein_marks','compiled_overvotes','compiled_undervotes','native_context_count']:s[k]=sum(r[k] for r in rs)
  s['A_pair_share']=s['A_votes']/s['pair_votes'];s['pair_margin_pp']=100*(s['A_votes']-s['B_votes'])/s['pair_votes'];s['tie_unbounded_shift_share_pp']=-s['pair_margin_pp']/2;s['Aplus1_unbounded_shift_share_pp']=s['tie_unbounded_shift_share_pp']+.5;s['A_won_counties']=sum(r['A_votes']>r['B_votes'] for r in rs);states.append(s)
 csvwrite(D/'state-baselines.csv',states)
 order=sorted([r for r in rows if r['year']=='2024' and r['contest']=='senate'],key=lambda r:(-r['all_candidate_votes'],r['county_fips']));V=sum(r['all_candidate_votes'] for r in order);cum=0;ranked=[];cross=None
 for i,r in enumerate(order,1):
  prev=cum;cum+=r['all_candidate_votes'];ranked.append({'rank':i,'county_fips':r['county_fips'],'county_code':r['county_code'],'county':r['county'],'all_candidate_votes':r['all_candidate_votes'],'A_votes':r['A_votes'],'B_votes':r['B_votes'],'other_valid_votes':r['other_valid_votes'],'cumulative_votes':cum,'cumulative_share':cum/V,'four_total':4*V,'five_cumulative':5*cum})
  if cross is None and 5*cum>=4*V:cross=i
 csvwrite(D/'priority-order.csv',ranked);priority={'status':'independently_computed_pending_coordinator_acceptance','basis':'2024 Class I Senate DOS Official Results all six named candidates; not generic marks','total':V,'top15_total':sum(r['all_candidate_votes'] for r in order[:15]),'minimum80_count':cross,'minimum80_total':ranked[cross-1]['cumulative_votes'],'prior_total':ranked[cross-2]['cumulative_votes'],'crossing_county':ranked[cross-1]['county'],'crossing_votes':ranked[cross-1]['all_candidate_votes'],'remainder_counties':67-cross,'remainder_votes':V-ranked[cross-1]['cumulative_votes'],'threshold_integer_ceil':(4*V+4)//5,'ordering':'descending integer all_candidate_votes; ascending FIPS as tie-break','all67_order':ranked,'priority_fips':[r['county_fips'] for r in ranked[:max(15,cross)]],'native_universe':'all compiled5710 Senate contexts retained separately, no valid WI allocation or current geometry equivalence'};writejson(D/'priority-contract.json',priority)
 # Supervisor index is an all67 authority inventory, not67 individually tested web products.
 parser=Tables();parser.feed(gzip.decompress((D/'source/supervisors.body.gz').read_bytes()).decode());codes=sorted(set(re.search(r'county=([A-Z]{3})',a.get('href',''))[1] for a in parser.links if re.search(r'county=([A-Z]{3})',a.get('href',''))));assert len(codes)==67
 csvwrite(D/'county-authorities.csv',[{'county_fips':r['county_fips'],'county_code':r['county_code'],'county':r['county'],'official_directory_url':f"https://dos.elections.myflorida.com/supervisors/countyInfo.asp?county={r['county_code']}",'directory_inventory_verified':r['county_code'] in codes,'individual_county_channel_inspection':'not_assignment_scope_pending_official_results_worker','timezone_scope':'America/Chicago;America/New_York (split Gulf; location-specific verification)' if r['county_code']=='GUL' else 'America/Chicago' if r['county_code'] in ['BAY','CAL','ESC','HOL','JAC','OKA','SAN','WAL','WAS'] else 'America/New_York','native_contexts_2024_senate':r['native_context_count']} for r in order])
 print(json.dumps({k:v for k,v in priority.items() if k not in ['all67_order','priority_fips']},indent=2))
if __name__=='__main__':main()
