"""Keep actual statewide named rows separate from native generic categories."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
D=Path(__file__).resolve().parent;N=D/'news'
def sh(b):return hashlib.sha256(b).hexdigest()
def main():
 mf={x['id']:x for x in json.loads((N/'manifest.json').read_bytes())}
 def raw(sid):
  x=mf[sid];z=(N/x['asset']).read_bytes();assert sh(z)==x['stored_sha256'];b=gzip.decompress(z);assert len(b)==x['bytes']and sh(b)==x['raw_sha256'];return b
 sid='sos-observed-2024-federal-statewide-page';s=BeautifulSoup(raw(sid),'html.parser');label=s.find(string=lambda x:x and x.strip()=='PRESIDENT AND VICE PRESIDENT');t=label.find_parent('div').find_next('table');printed=[];total=None
 for tr in t.find_all('tr'):
  f=[c.get_text(' ',strip=True)for c in tr.find_all(['th','td'])]
  if not f or f[0]=='Candidate':continue
  assert len(f)==4
  if f[0]=='Vote Totals':total=int(f[2].replace(',',''));continue
  a=tr.find('a',href=True);printed.append({'candidate_label_literal':f[0],'party_literal':f[1],'total_literal':f[2],'votes':int(f[2].replace(',','')),'percentage_literal':f[3],'actual_historical_candidate_detail_href':a['href']if a else None,'actual_resolved_historical_candidate_detail_URL':urljoin(mf[sid]['final_url'],a['href'])if a else None})
 native='sos-2024-president-csv';c=collections.Counter()
 for r in csv.DictReader(io.StringIO(raw(native).decode('utf-8-sig'))):c[r['CandidateName']]+=int(r['VoteCount'])
 shared=[x for x in printed if x['candidate_label_literal']in c];other=[x for x in printed if x['candidate_label_literal']not in c];assert len(shared)==3 and len(other)==24
 assert all(c[x['candidate_label_literal']]==x['votes']for x in shared);assert sum(x['votes']for x in printed)==total==5633310
 generic={k:v for k,v in c.items()if k.lower()=='write-in'};named=sum(x['votes']for x in other);assert named==40942 and sum(generic.values())==57411
 out={'status':'pass_literal_statewide_named_source_rows_compared_to_native_printed_candidates','source_pins':{x:mf[x]for x in [sid,native]},'statewide_HTML_table_id':t.get('id'),'all_statewide_candidate_source_rows':printed,'statewide_HTML_total':total,'three_native_printed_candidate_total':sum(x['votes']for x in shared),'three_candidate_native_and_HTML_comparisons_exact':True,'additional24_named_statewide_row_total':named,'native_generic_case_variant_totals_separate':generic,'native_generic_total_separate':sum(generic.values()),'scope_difference_generic_minus_additional_named':sum(generic.values())-named,'native_named_writein_allocation_available_here':False,'qualification':['All27named source rows and actual candidate-detail hrefs remain literal; apparent running mates/aliases/spellings are not automatically joined into tickets. Historical href identities are not November2026count-feedIDs.','Three printed candidate totals reconcile native CSV exactly.24additional named statewide rows are not in that CSV; generic57411andnamed40942are separate reported source scopes with16469difference left unassigned.','Many minor source percentages literally<.01 despite nontrivial counts; source literals retained, not repaired or used for weights.','Actual statewide source, independent federal certification, county/authority/native valid-vote allocation and exact priority still require first-pair independent review. No native0or eligibility conclusion inferred from absent names.'],'formal_priority_accepted':False,'current_geography_approved':False}
 p=D/'coordinator-statewide-president-controls.json';b=(json.dumps(out,indent=2)+'\n').encode();p.write_bytes(b);print(json.dumps({'path':str(p),'bytes':len(b),'sha256':sh(b),'state_total':total,'named_rows_not_in_native':named,'generic_separate':sum(generic.values())}))
if __name__=='__main__':main()
