"""Offline build of full historical hierarchy and bounded authority evidence.
All outputs confined to this question. No producer imports or network access.
Acceptance authority is referenced by path only; current matches stay unknown.
"""
from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,io,json,re
O=Path(__file__).resolve().parent;S=O.parents[1]
AUTHORITY='data/coordinator-priority-acceptance.json'
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode();b=gzip.compress(b,mtime=0)if p.suffix=='.gz'else b;assert len(b)<40000000;p.write_bytes(b)
def num(s):return int(s.replace(',',''))if s!=''else None
def main():
 c=load(S/'data/turnout/priority-set.json');ds=load(O/'municipal-discovery.json');gov=load(O/'municipal-government-directory.json');nav=load(O/'directory-navigation.json');http=[load(p)for p in sorted((O/'source/http').glob('*.json'))];byurl=defaultdict(list)
 for r in http:byurl[r['requested_url']].append(r)
 structures=load(O/'structure-index.json');byhash={x['body_sha256']:x for x in structures['responses']}
 # Retain all indexed directory fragments by exact source string offsets.
 # Search representations can omit material within an entry; no fragment is
 # falsely promoted to a complete original directory record.
 fragments=defaultdict(list)
 for f in [O/'source/local-directory-search.json',*sorted((O/'source/directory-search').glob('*.json')),*sorted((O/'source/search').glob('*.json'))]:
  z=load(f);t=z if isinstance(z,str)else z.get('response','')
  for page in re.finditer(r'(?m)^Find Local Election[^\n]*\((https?://[^\n]+)\)\n(.*?)(?=\n-+\n|\Z)',t,re.S):
   if page[1].split('?')[0]!='https://www.sec.state.ma.us/divisions/elections/voter-resources/find-my-local-election-office.htm':continue
   body=page[2]
   for m in re.finditer(r'(?m)^## ([^\n]+)\n(.*?)(?=^## |\Z)',body,re.S):
    name=m[1];roles=list(dict.fromkeys(re.findall(r'(?mi)^(?:Town Clerk|City Clerk|Elections? Commission(?:ers)?|Board of Election Commissioners|Election Department|Elections? Office)\s*$',m[2])))
    fragments[name].append(dict(source_file=str(f.relative_to(O)),response_pointer='/response'if isinstance(z,dict)else'',start=page.start(2)+m.start(),end=page.start(2)+m.end(),literal_heading=name,observed_role_lines=roles,source_original=False,entry_completeness='unverified indexed fragment; gaps may exist inside it'))
 scope_negatives=load(O/'source-scope-negatives.json');followjobs=load(O/'municipal-follow-requests.json');initialjobs=load(O/'municipal-requests.json');allparents=[];inventory=[];linked_ancillary=[]
 for i,(d,hp) in enumerate(zip(ds,c['all_parent_child_maps'])):
  name=d['source_parent_literal'];pk=hp['municipal_key'];assert json.loads(pk)[0]==name
  directory_matches=[b for b in gov['entries']if b['name']==d['research_full_name']];ns=[x for x in nav if x['parent_literal']==name];base={x['url']for x in d['selected_sources']}|{x['url']for x in ns if x['url']}
  initial=[r for r in http if re.match(f'muni-{i:03d}-',r['id'])]
  base.update(r['requested_url']for r in initial)
  requests={r['id']:r for u in base for r in byurl.get(u,[])};related_jobs=[]
  for j in followjobs:
   if j.get('reason','').startswith('bounded actual link for historical research parent '+name+':'):
    related_jobs.append(j)
    for r in byurl.get(j['url'],[]):requests[r['id']]=r
  for u in base:
   for r in byurl.get(u,[]):requests[r['id']]=r
  inspected=[];role_obs=[];plan_obs=[];external_links=[];format_obs=[];publications=[];gaps=[]
  for r in requests.values():
   ip=O/'source/inspect'/(r['id']+'.json');structure=byhash.get(r.get('body',{}).get('raw_sha256'))
   rec=dict(request_id=r['id'],receipt='source/http/'+r['id']+'.json',requested_url=r['requested_url'],final_url=r.get('final_url'),status=r['status'],error=r['error'],body=r.get('body'),structure=structure.get('structure')if structure else None,source_update_clock=None,measured_cadence=None,current_return_admitted=False)
   if any(n['historical_research_parent']==name and n['url']==r['requested_url'] for n in scope_negatives):rec['excluded_as_MA_official_result_authority']='wrong municipal research-parent attribution; see source-scope-negatives.json; no current identity inference'
   if r['status']!=200:gaps.append(dict(url=r['requested_url'],status=r['status'],error=r['error']))
   if structure:format_obs.append(dict(source_id=r['id'],format=structure['format'],structure=structure['structure']))
   if ip.exists():
    ins=load(ip);rec['inspection']=str(ip.relative_to(O));t=ins['text'];rec['title']=ins['title']
    if re.search(r'(?i)plymouthmassdems|rutlandtown\.com',r['requested_url']) or re.search(r'(?i)rutland,?\s+VT|rutland vermont',t):
     rec['excluded_as_MA_official_result_authority']='party site or wrong-state municipality; negative navigation evidence only'
    if r['status']==200 and not rec.get('excluded_as_MA_official_result_authority'):
     for m in re.finditer(r'(?i)\b(?:town clerk|city clerk|(?:board of )?(?:election|elections) commissioners?|(?:board of )?registrars(?: of voters)?|election office)\b',t):
      role_obs.append(dict(request_id=r['id'],literal=m[0],context_start=m.start(),context_end=m.end(),inspection=str(ip.relative_to(O))))
     for m in re.finditer(r'(?i)unofficial|certif(?:ied|ication)|election night|results.*(?:updated|available)|(?:updated|posted).*results|preliminary results|final results',t):
      plan_obs.append(dict(request_id=r['id'],start=m.start(),end=m.end(),context=t[max(0,m.start()-100):m.end()+300],interpretation='literal page evidence; may describe another election; no measured vote-update interval'))
     for x in ins['links']:
      if re.search(r'(?i)(?:election|voting|registrar|clerk|canvass|results)',x['text']+' '+x['url']):
       external_links.append(dict(source_id=r['id'],ordinal=x['ordinal'],tag=x['tag'],literal_href=x['literal_href'],url=x['url'],text=x['text'],public_fetch_allowed=x['public_fetch_allowed'],fetched=bool(byurl.get(x['url'])),official_result_publication_approval=False))
     if re.search(r'(?i)rutland,?\s+VT|rutland vermont',t):rec['geographic_scope_conflict']='Vermont text; excluded from MA authority/result evidence'
    if re.search(r'(?i)plymouthmassdems|rutlandtown\.com',r['requested_url']):rec['excluded_as_MA_official_result_authority']='party site or wrong-state municipality; retained negative navigation evidence only'
   inspected.append(rec)
  current=dict(target_date='2026-11-03',stage='General / State Election',office='Senator in Congress',source_parent_is_historical=True,current_date_native_id=None,current_election_native_id=None,current_stage_native_id=None,current_office_native_id=None,current_candidate_choice_ids=None,current_party_ids=None,current_reporting_unit_ids=None,current_method_ids=None,current_status_ids=None,geographic_match=None,genuine_November_returns=None,current_admission=False,eligible_unprocessed_votes=None,measured_cadence=None,correction_clock=None,completion_meaning=None)
  fragment=fragments.get(d['research_full_name'],[]);roles=list(dict.fromkeys(z for x in fragment for z in x['observed_role_lines']))
  evidence=dict(schema='MA bounded shared municipal parent investigation v1',research_parent_ordinal=i+1,source_parent_key=pk,source_parent_literal=name,research_full_name=d['research_full_name'],authority_path=AUTHORITY,priority_parent=d['priority_parent'],historical_parent_full_object=hp,government_directory_matching_blocks=directory_matches,government_directory_correspondence='historical name research attribution only; not a current ID or boundary match',government_directory_duplicate_literal=len(directory_matches)>1,secretary_local_election_directory=dict(url='https://www.sec.state.ma.us/divisions/elections/voter-resources/find-my-local-election-office.htm',raw_HTML_access='403 after ordinary redirect/cookie attempt',raw_field_completeness=False,indexed_fragment_references=fragment,raw_missing_fields_remain_unknown=True),distinct_authority_roles=dict(indexed_directory_role_lines=roles,actual_page_role_occurrences=role_obs,precinct_canvass='presiding officers/precinct clerk: c54 ss104-107; not municipal clerk identity',municipal_certification='c54 s112: city/town clerk; Boston Board of Election Commissioners',post_election_absentee_canvass='c54 s95: registrars; distinct from clerk record transmission',recount='c54 s135: registrars determine, clerk amends and transmits',state_certification='c54 ss115-116: Governor/Council examination and Governor Senate certificate countersigned/transmitted by Secretary',local_current_named_official_ID=None),secretary_department_navigation=ns,searches=[str(p.relative_to(O))for p in sorted((O/'source/search').glob('*.json'))if name in load(p).get('queries',[])],bounded_chain_requests=inspected,actual_follow_request_constructors=related_jobs,observed_election_links=external_links,publication_status_and_plan_evidence=plan_obs,complete_format_samples=format_obs,access_gaps=gaps,current=current,scope='complete bounded parent evidence; shared across exact historical children; online election-night service is not guaranteed by statutory authority or a landing 200',completion_status='bounded investigation finished, with explicit source/access and future qualifications')
  path=O/'parents'/f'{i+1:03d}.json';dump(path,evidence);allparents.append(dict(source_parent_key=pk,source_parent_literal=name,priority_parent=d['priority_parent'],investigation=str(path.relative_to(O)),all_source_child_arrays=hp))
  inventory.append(dict(authority_scope='municipal research parent',source_parent_literal=name,research_full_name=d['research_full_name'],historical_parent_key=pk,priority_parent=str(d['priority_parent']).lower(),source_child_count=len(hp['native_keys_source_order']),priority_child_count=sum(k in c['ordered_priority_keys']for k in hp['native_keys_source_order']),inventory_only=str(not d['priority_parent']).lower(),authority_investigation=str(path.relative_to(O)),government_directory_raw_blocks_json=json.dumps(directory_matches,ensure_ascii=False),secretary_election_directory_role_lines_json=json.dumps(roles,ensure_ascii=False),clerk_role_evidence_json=json.dumps([x for x in role_obs if 'clerk'in x['literal'].lower()],ensure_ascii=False),commission_role_evidence_json=json.dumps([x for x in role_obs if 'commission'in x['literal'].lower()],ensure_ascii=False),registrar_role_evidence_json=json.dumps([x for x in role_obs if 'registrar'in x['literal'].lower()],ensure_ascii=False),canvass_and_certification='distinct precinct/city-town-clerk/Boston-board/registrar/Governor-Council roles; see full parent record',actual_public_URLs_json=json.dumps([r['requested_url']for r in inspected],ensure_ascii=False),HTTP_statuses_json=json.dumps([dict(id=r['request_id'],status=r['status'],error=r['error'])for r in inspected],ensure_ascii=False),formats_json=json.dumps(format_obs),secretary_raw_directory_complete='false',current_election_ID='',current_office_ID='',current_choice_IDs='',current_unit_IDs='',current_method_IDs='',current_status_IDs='',source_vote_update_clock='',source_timezone='',measured_vote_cadence='',known_eligible_remaining_votes='',current_November_returns_admitted='false'))
 # Complete source records accompany each ordered investigation. A rank is an
 # owned research ordinal, never a source-native or current precinct ID.
 parent_by_name={x['source_parent_literal']:x for x in allparents};leafs=[]
 for row in c['all_unit_order']:
  src=row['source_record'];name=src['literal_tuple'][0];parent=parent_by_name[name];rank=len(leafs)+1
  leafs.append(dict(schema='MA ordered complete shared-parent investigation v1',research_rank=rank,historical_native_key=row['native_key'],literal_tuple=src['literal_tuple'],partition='priority'if rank<=1470 else'remainder',complete_frozen_order_object=row,complete_original_source_record=src,parent_investigation=parent['investigation'],source_parent_key=parent['source_parent_key'],shared_parent_proof=dict(parent_literal=name,resource_scope='municipal authority research, not an independent precinct feed',parent_hierarchy_file='all-parent-hierarchy.json.gz',child_membership_array='native_keys_source_order',explicit_shared=True),current=dict(election_id=None,office_id=None,choice_ids=None,unit_id=None,method_ids=None,status_id=None,geographic_match=None,returns_admitted=False,eligible_remaining_votes=None),status='bounded shared-parent investigation complete'if rank<=1470 else'explicit remainder retained in statewide hierarchy; municipal authority inventoried'))
 dump(O/'priority-investigations.json.gz',leafs[:1470]);dump(O/'remainder-investigations.json.gz',leafs[1470:]);dump(O/'all-parent-hierarchy.json.gz',dict(schema='complete 351 historical research parents; all arrays retained',parents=allparents,ordered_full_keys=[r['native_key']for r in c['all_unit_order']],ordered_priority_keys=c['ordered_priority_keys'],ordered_remainder_keys=c['ordered_remainder_keys'],current_identity_approved=False))
 state=[('Secretary of the Commonwealth / Elections Division','https://www.sec.state.ma.us/divisions/elections/elections-and-voting.htm','state-guidance-1.json','certified results after local review; expressly no state Election Night results'),('PD43+ state publication','https://electionstats.state.ma.us/index.php','http/pd43-current-root.json','historical publication; office dropdown 6 is not admitted November ENR identity'),('Governor and Governor\u2019s Council','https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section115','http/law54-115.json','statutory canvass/certification; no observed public ENR feed'),('United States Senate','https://www.senate.gov/about/origins-foundations/electing-appointing-senators/contested-senate-elections/','http/senate-contests.json','distinct federal judge of its own elections/returns/qualifications; not a municipal remedy')]
 for name,url,evidence,role in state:
  v={k:''for k in inventory[0]};v.update(authority_scope='state/federal publication or legal authority',research_full_name=name,actual_public_URLs_json=json.dumps([url]),authority_investigation='source/'+evidence,canvass_and_certification=role,priority_parent='false',inventory_only='true',secretary_raw_directory_complete='false',current_November_returns_admitted='false');inventory.append(v)
 with (S/'data/official-results-sources.csv').open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(inventory[0]));w.writeheader();w.writerows(inventory)
 with (O/'all-unit-index.csv').open('w',newline='')as f:
  w=csv.writer(f);w.writerow(['research_rank','historical_literal_key','source_parent_key','partition','complete_investigation_file','zero_based_record'])
  for i,r in enumerate(leafs):w.writerow([i+1,r['historical_native_key'],r['source_parent_key'],r['partition'],'priority-investigations.json.gz'if i<1470 else'remainder-investigations.json.gz',i if i<1470 else i-1470])
 summary=dict(schema='MA official bounded research coverage v1',authority_path=AUTHORITY,municipal_inventory=351,state_federal_authorities=4,priority_parents=sum(x['priority_parent']for x in allparents),ordered_priority_investigations=1470,explicit_remainder=924,all_native_contexts=2394,whole_historical_parent_objects=351,distinct_leaf_feeds_claimed=0,government_web_directory_numbered_lines=gov['line_count'],government_web_directory_raw_heading_blocks=len(gov['entries']),government_duplicate_municipal_heading='Harvard',department_navigation_attempts=sum(x.get('navigation_kind')=='department directory'for x in nav),homepage_fallback_navigation_attempts=sum(x.get('navigation_kind')=='homepage fallback'for x in nav),directory_destinations_exposed=sum(bool(x['url'])for x in nav),secretary_election_directory_raw_complete=False,indexed_directory_parents_with_fragments=sum(bool(fragments.get(d['research_full_name']))for d in ds),priority_parent_HTTP_attempts=sum(any(x['bounded_chain_requests']) for x in [load(O/p['investigation']) for p in allparents if p['priority_parent']]),priority_parent_HTTP_200=sum(any(r['status']==200 and not r.get('excluded_as_MA_official_result_authority') for r in x['bounded_chain_requests']) for x in [load(O/p['investigation']) for p in allparents if p['priority_parent']]),actual_response_receipts=len(http),response_statuses=dict(Counter(str(r['status'])for r in http)),complete_structural_samples=dict(Counter(r['format']for r in structures['responses'])),complete_historical_CSV_samples=len(structures['historical_csv']),current_November_returns_admitted=False,current_matching_or_ID_approval=False,known_eligible_remaining_votes=None,measured_vote_publication_cadence=None,bounded_research_finished=True,coordinator_acceptance_or_publication=False)
 dump(O/'coverage.json',summary);print(summary)
if __name__=='__main__':main()
