"""Whole historical native CSV structure and independent literal statewide HTML controls."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
from bs4 import BeautifulSoup
D=Path(__file__).resolve().parent;N=D/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 mf={x['id']:x for x in json.loads((N/'manifest.json').read_bytes())};results={};refs={}
 def raw(sid):
  x=mf[sid];z=(N/x['asset']).read_bytes();assert sha(z)==x['stored_sha256'];b=gzip.decompress(z);assert len(b)==x['bytes']and sha(b)==x['raw_sha256'];refs[sid]=x;return b
 for year in ['2020','2022']:
  sid=f'sos-observed-{year}-senate-native-csv';rows=list(csv.DictReader(io.StringIO(raw(sid).decode('utf-8-sig'))));c=collections.Counter();contexts=collections.defaultdict(list);authorities=collections.defaultdict(collections.Counter);duplicate=collections.Counter()
  for pos,r in enumerate(rows,2):
   assert len(r)==12 and r['ContestName']=='UNITED STATES SENATOR'and r['EISContestID']=='160';v=int(r['VoteCount']);assert v>=0;c[r['CandidateName']]+=v;key=tuple(r[x]for x in ['JurisdictionID','JurisContainerID','JurisName','PrecinctName']);contexts[key].append((pos,r));authorities[r['JurisdictionID']][r['JurisContainerID'],r['JurisName']]+=1;duplicate[r['JurisdictionID'],r['PrecinctName'],r['EISCandidateID']]+=1
  hs=f'sos-observed-{year}-federal-statewide-page';s=BeautifulSoup(raw(hs),'html.parser');label=s.find(string=lambda x:x and x.strip()=='UNITED STATES SENATOR');assert label is not None;table=label.find_parent('div').find_next('table');printed=[];total=None
  for tr in table.find_all('tr'):
   f=[x.get_text(' ',strip=True)for x in tr.find_all(['th','td'])]
   if not f or f[0]=='Candidate':continue
   assert len(f)==4
   if f[0]=='Vote Totals':assert total is None;total=int(f[2].replace(',',''))
   else:printed.append({'candidate_literal':f[0],'party_literal':f[1],'total_literal':f[2],'votes':int(f[2].replace(',','')),'percentage_literal':f[3]})
  assert total==sum(x['votes']for x in printed)
  common=[x for x in printed if x['candidate_literal']in c];state_only=[x for x in printed if x['candidate_literal']not in c];assert len(common)==(5 if year=='2020'else 3)
  for x in common:assert c[x['candidate_literal']]==x['votes']
  generic={k:v for k,v in c.items()if k not in {x['candidate_literal']for x in printed}};assert all(k.lower()=='write-in'for k in generic)
  native=[]
  for key,rr in contexts.items():
   native.append({'JurisdictionID':key[0],'JurisContainerID':key[1],'JurisName':key[2],'PrecinctName':key[3],'source_row_positions_1based_including_header':[p for p,r in rr],'raw_registration_literals':list(dict.fromkeys(r['Registration']for p,r in rr)),'source_candidate_ID_name_party_counts':[{'EISCandidateID':r['EISCandidateID'],'CandidateName':r['CandidateName'],'EISPartyID':r['EISPartyID'],'PartyName':r['PartyName'],'VoteCount_literal':r['VoteCount']}for p,r in rr]})
  results[year]={'native_CSV_source_id':sid,'separate_state_HTML_source_id':hs,'source_columns':list(rows[0]),'raw_data_rows':len(rows),'raw_field_positions':len(rows)*12,'authority_IDs':len(authorities),'authority_container_name_contexts':sum(len(x)for x in authorities.values()),'literal_native_contexts':len(contexts),'naive_authority_precinct_candidateID_duplicate_excess':sum(v-1 for v in duplicate.values()),'raw_candidate_and_category_sums':dict(c),'separate_statewide_HTML_candidate_rows':printed,'statewide_HTML_total':total,'native_printed_candidate_comparisons_exact':len(common),'named_state_HTML_rows_not_named_in_native_CSV':state_only,'named_state_HTML_only_total':sum(x['votes']for x in state_only),'native_generic_case_variants_separate':generic,'native_generic_sum_separate':sum(generic.values()),'complete_literal_source_native_contexts':native,'source_authority_contexts':[{'JurisdictionID':k,'containers':[{'JurisContainerID':c0,'JurisName':name,'raw_rows':count}for(c0,name),count in vv.items()]}for k,vv in authorities.items()],'method_column_present':False}
 out={'status':'pass_literal_native_Senate_sources_and_printed_candidate_HTML_controls_only','source_pins':refs,'years':results,'whole_raw_rows':sum(x['raw_data_rows']for x in results.values()),'whole_raw_field_positions':sum(x['raw_field_positions']for x in results.values()),'qualification':['Public Search button event and actual58/62election options led to returned literal county/federal-page links; backslash-style CSV hrefs normalized as actual root paths, with no guessed IDs.','All108sourceauthorities and allliteral container/precinct contexts are retained per year. SourceIDs are not FIPS, city/county views require explicit coverage and are not automatically additive.','Registration is literal and repeated across candidate/category rows; no repeated-sum voter total or raw-precinct physical identity claim.','2020/2022native CSVs have no method column. Apparent method words inside source precinct labels are not decoded to methods.','Statewide named small write-in rows remain separate from much larger native generic case variants. No native allocation, eligibility assumption or addition of overlapping source categories.','2020HTML DavidFBlack56711printspercentage<.01 despite its displayed total; raw literal percentage is preserved without repair.','No current2026candidate/precinct/method IDs, legal geographic crosswalk, full candidate priority or live cadence/remainder admitted.'],'formal_priority_accepted':False,'current_geography_approved':False}
 p=D/'coordinator-historical-senate-preflight.json';b=(json.dumps(out,indent=2)+'\n').encode();p.write_bytes(b);print(json.dumps({'path':str(p),'bytes':len(b),'sha256':sha(b),'raw_rows':out['whole_raw_rows'],'fields':out['whole_raw_field_positions'],'years':{k:{a:v for a,v in x.items()if a in ['authority_IDs','literal_native_contexts','statewide_HTML_total','named_state_HTML_only_total','native_generic_sum_separate','native_printed_candidate_comparisons_exact']}for k,x in results.items()}}))
if __name__=='__main__':main()
