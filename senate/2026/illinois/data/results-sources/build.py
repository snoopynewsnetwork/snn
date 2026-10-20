"""Offline reconstruction of complete historical hierarchy plus current-source investigation.
External coordinator authority is read by PATH ONLY; no producer writes or scripts.
"""
from common import *
from boundary_guard import allowed_public_url
from collections import Counter,defaultdict

def receipt_ref(m):
 return dict(receipt_path='data/results-sources/receipts/'+m['id']+'.json',id=m['id'],url=m['url'],parent=m.get('parent'),method=m.get('method'),status=m.get('status'),complete=m.get('complete'),error=m.get('error'),final_url=m.get('final_url'),raw_path=m.get('path'),raw_bytes=m.get('raw_bytes'),raw_sha256=m.get('raw_sha256'),stored_bytes=m.get('stored_bytes'),stored_sha256=m.get('stored_sha256'),retrieved_at_utc=m.get('retrieved_at_utc'),source_clock_timezone=None)
def pub_fields(o):
 out=[]
 def walk(x,p):
  if isinstance(x,dict):
   for k,v in x.items():
    q=p+'/'+k.replace('~','~0').replace('/','~1')
    if re.search('date|time|updated|status|certif|final|electionname',k,re.I):out.append(dict(pointer=q,value=v,timezone='literal only; not inferred'))
    walk(v,q)
  elif isinstance(x,list):
   for i,v in enumerate(x):walk(v,p+'/'+str(i))
 walk(o,'');return out

def main():
 a=parsefile(ACCEPTANCE);p=parsefile(STATE/a['frozen_contract']['path']);directory=parsefile(HERE/'current-authority-directory.json');bydir={r['current_directory_selector_value']:r for r in directory}
 receipts=[parsefile(q) for q in sorted((HERE/'receipts').glob('*.json'))];byid={m['id']:m for m in receipts};schemata={x['receipt_id']:x for x in parsefile(HERE/'source-schema-inventory.json')};parents=[];excluded=[];summaries=[]
 for m in receipts:
  if not allowed_public_url(m['url']):excluded.append(dict(receipt_id=m['id'],url=m['url'],status=m.get('status'),disposition='irrelevant discovery GET excluded from result authority/feed proof; no account operations or credentials submitted'))
 write(HERE/'discovery-scope-findings.json',dict(finding='Initial broad literal-link discovery admitted irrelevant account/security/social landing GETs. Corrected deny guard and negative fixtures prevent recurrence. Full receipts retained; excluded from source findings.',excluded=excluded,diagnostic_transport_limit='Two unretained TLS-bundle diagnostics and one initial curl access-denial test preceded the full curl receipt helper; exact headers/UTC of those diagnostics are unavailable, no claims rely on them. All substantive acquisition receipts retain original entities or explicit failures.'))
 for i,old in enumerate(p['authority_inventory']):
  aid=old['authority_id'];current=bydir[aid];evidence=[m for m in receipts if (m['id']=='authority-'+aid or m['id'].startswith('authority-'+aid+'-')) and allowed_public_url(m['url'])];detail=byid.get('directory-detail-'+aid);assert detail and detail.get('complete') and detail.get('status')==200
  allrefs=[receipt_ref(m) for m in evidence];fullkeys=[k for k in a['ordered_full_keys'] if p['native_to_authority_parent_map'][k]==old['key']];prioritykeys=[k for k in a['ordered_priority_keys'] if p['native_to_authority_parent_map'][k]==old['key']];remkeys=[k for k in a['ordered_remainder_keys'] if p['native_to_authority_parent_map'][k]==old['key']]
  structured=[];document_samples=[];gaps=[];links=[];clocks=[]
  for m in evidence:
   if m['id'] in schemata:structured.append(dict(receipt=m['id'],sample_path=schemata[m['id']]['sample_path'],format=schemata[m['id']]['format']))
   if m.get('complete'):
    b=body(m)
    if b.startswith(b'%PDF'):document_samples.append(dict(receipt=m['id'],format='complete PDF',text_path='data/results-sources/text/'+m['id']+'.txt.gz' if (HERE/'text'/f"{m['id']}.txt.gz").exists() else None))
    elif b.lstrip().startswith((b'{',b'[')):
     try:clocks+= [dict(receipt=m['id'],**v) for v in pub_fields(json.loads(b))]
     except Exception:pass
    elif not b.startswith(b'PK'):
     try:
      h=HTML(b.decode('utf8',errors='replace'))
      for z in h.links:
       href=z.get('literal_href')
       if href and any(t in (z['text']+' '+href).lower() for t in ['result','canvass','clarity','platinum','2026','download','electionreport','enhancedvoting']):
        u=urljoin(m.get('final_url',m['url']),href)
        if allowed_public_url(u):links.append(dict(parent_receipt=m['id'],literal_href=href,link_text=z['text'],resolved_url=u,downloaded_anywhere=any(n['url'].split('#')[0]==u.split('#')[0] for n in receipts)))
     except Exception:pass
   if m.get('error') or m.get('status')!=200:gaps.append(dict(receipt=m['id'],status=m.get('status'),error=m.get('error'),url=m['url']))
  if not current['official_url_literal']:gaps.append(dict(field='current directory website',literal_value=None,note='State directory hyperlink absent; any search-discovered official site retained separately; blank not overwritten.'))
  if aid in ['24','36','93']:gaps.append(dict(field='bounded alternate local discovery',evidence_path='data/results-sources/blank-link-bounded-search.json',note='State detail plus exact county/Illinois election-office discovery queries did not establish an authoritative local online election publisher. Other-state matches, circuit courts, commercial directories and archival contact pages are not substituted as election channels. No outreach performed.'))
  if not structured:gaps.append(dict(field='structured count sample',value=None,note='No complete structured result feed reached by bounded published-link traversal; PDF/server HTML evidence and explicit requests remain.'))
  gaps.extend([dict(field='November count identifiers',value=None,note='No admitted full November navigation/election/contest/choice/unit mapping. Setup labels and candidate metadata do not supply complete count-key proof.'),dict(field='eligible unprocessed remaining ballots',value=None,note='No explicit validated eligible/unprocessed pool; registration, requested/sent, returned or setup-zero counts are not an exact remainder.'),dict(field='measured cadence',value=None,note='Bounded static samples do not establish a publication interval or correction lag.')])
  obj=dict(schema='il-official-parent-investigation/v1',historical_parent_key=old['key'],complete_historical_parent_object=old,historical_parent_pointer='/authority_inventory/'+str(i),frozen_contract_path=a['frozen_contract']['path'],historical_child_keys_ordered=fullkeys,priority_child_keys_ordered=prioritykeys,remainder_child_keys_ordered=remkeys,priority_parent=bool(prioritykeys),current_directory_research_association=current,directory_detail_receipt=receipt_ref(detail),directory_detail_complete_parse_path='data/results-sources/parsed/'+detail['id']+'.json.gz',association_qualification='Observed current directory selector roster correspondence for research only; not a legal boundary or current result leaf join. County/state historical combined views can overlap city slices.',local_requests=allrefs,complete_structured_samples=structured,complete_document_samples=document_samples,published_result_navigation=links,publisher_clock_fields=clocks,transport_clocks='Every receipt retains HTTP Date/Last-Modified/ETag etc separately from source clocks; no timezone inferred',source_specific_gaps=gaps,current_leaf_matches=None,admitted_november_returns=False,measured_cadence=None,exact_outstanding_eligible_ballots=None)
  path=HERE/'parents'/f'{aid}.json';write(path,obj);parents.append(dict(parent_key=old['key'],historical_name=old['name'],path=str(path.relative_to(STATE)),complete_historical_parent_object=old,full_ordered_children=fullkeys,priority_ordered_children=prioritykeys,remainder_ordered_children=remkeys))
  landing=byid.get('authority-'+aid)
  summaries.append(dict(kind='current_local_authority',directory_position_1based=current['directory_position_1based'],current_selector_value=aid,current_directory_label=current['current_directory_label'],directory_source='https://www.elections.il.gov/ElectionOperations/ElectionAuthorities.aspx?MID=cQHxtxVEmuo%3D',directory_fields_json=json.dumps(current['complete_directory_row'],ensure_ascii=False,separators=(',',':')),authority_url_literal=current['official_url_literal'],landing_status=landing.get('status') if landing else None,landing_error=landing.get('error') if landing else 'blank directory link',landing_final_url=landing.get('final_url') if landing else None,local_requests=len(evidence),parent_investigation_path=str(path.relative_to(STATE)),historical_reference_only=old['key'],historical_priority_children=len(prioritykeys),full_historical_children=len(fullkeys),structured_samples=len(structured),pdf_samples=len(document_samples),november_returns_admitted=False,current_leaf_mapping=None,measured_cadence=None,exact_eligible_outstanding_ballots=None))
 gzwrite(HERE/'historical-parent-hierarchy.json.gz',encode(parents))
 lookup={x['key']:(i,x) for i,x in enumerate(p['native_constituents'])};investigations=[]
 for rank,key in enumerate(a['ordered_full_keys'],1):
  i,x=lookup[key];parent=p['native_to_authority_parent_map'][key]
  investigations.append(dict(schema='il-shared-parent-leaf-investigation/v1',historical_rank=rank,priority_position=rank if rank<=5540 else None,remainder_position=rank-5540 if rank>5540 else None,key=key,historical_parent_key=parent,source_object_pointer='/native_constituents/'+str(i),frozen_contract_path=a['frozen_contract']['path'],complete_historical_native_source_object=x,parent_investigation_path='data/results-sources/parents/'+x['authority_id']+'.json',research_scope='shared parent investigation inherited without claiming a current leaf match',current_navigation_election_contest_choice_unit_mapping=None,current_geography_join=None,november_returns_admitted=False,unknown_remaining_ballots=None))
 for name,rows in [('investigations-priority',investigations[:5540]),('investigations-remainder',investigations[5540:])]:gzwrite(HERE/(name+'.jsonl.gz'),b''.join(encode(x) for x in rows))
 write(HERE/'hierarchy-index.json',dict(acceptance_path=str(ACCEPTANCE.relative_to(STATE)),source_scope='2024 printed-known president source observation grouping; no physical/current precinct count',ordered_full_keys=a['ordered_full_keys'],ordered_priority_keys=a['ordered_priority_keys'],ordered_remainder_keys=a['ordered_remainder_keys'],ordered_priority_parent_literals=a['ordered_priority_parent_literals'],full_parents=108,priority_parents=97,full_children=10062,priority_children=5540,remainder_children=4522,hierarchy_path='data/results-sources/historical-parent-hierarchy.json.gz',priority_records='data/results-sources/investigations-priority.jsonl.gz',remainder_records='data/results-sources/investigations-remainder.jsonl.gz'))
 columns=list(summaries[0]);out=io.StringIO(newline='');w=csv.DictWriter(out,columns);w.writeheader();w.writerows(summaries);(STATE/'data/official-results-sources.csv').write_text(out.getvalue())
 write(HERE/'acquisition-summary.json',dict(receipts=len(receipts),complete_entities=sum(bool(m.get('complete')) for m in receipts),status_counts=dict(Counter(str(m.get('status')) for m in receipts)),current_authorities=108,priority_parents=97,parents_with_local_requests=sum(x['local_requests']>0 for x in summaries),source_specific_parent_dossiers=108,structured_samples=len(schemata),admitted_november_returns=0,excluded_irrelevant_discovery_gets=len(excluded),individual_object_limit_bytes=39999999,source_clock_timezones='literal only; unspecified retained as unknown',automatic_rendering_scope='selected PDF pages only; actual visually inspected pages listed separately'))
 print(json.dumps(dict(parents=len(parents),priority=5540,remainder=4522,receipts=len(receipts))))
if __name__=='__main__':main()
