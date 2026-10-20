from common import *
import xml.etree.ElementTree as ET
from collections import Counter

def main():
 rows=list(csv.DictReader(io.StringIO((STATE/'data/official-results-sources.csv').read_text())));lines=['# Illinois bounded authority findings','', 'Each row has an independently downloaded state detail body. Counts are historical source observations, never approved current precincts. Linked dossiers retain every request, exact source URL, fields, raw body and source-specific gaps. Blank state directory hrefs remain blank even when an official site was separately discovered.','', '| Current directory label / historical reference | Priority / all historical groups | Actual bounded observations | Specific source/access limit |','|---|---:|---|---|']
 for r in rows:
  aid=r['current_selector_value'];p=parsefile(HERE/'parents'/f'{aid}.json');refs=p['local_requests'];pdf=p['complete_document_samples'];js=p['complete_structured_samples'];best=[]
  for x in refs:
   if x['id'].endswith('search-official') or any(t in (x.get('final_url') or '') for t in ['platinumelectionresults','clarityelections','dupageresults','gbsvote','livevoterturnout']):
    if not x['id'].endswith(('-main','-webconfig','-config','-versions','-current-version')):best.append(x)
  if not best:best=[x for x in refs if x['id']!='authority-'+aid and x.get('complete')][:2]
  if not best and refs:best=refs[:1]
  obs='; '.join('['+x['id']+']('+x['url'].replace(' ','%20')+') HTTP '+str(x['status']) for x in best[:3]) or 'State detail '+aid+'; directory website blank; no local publisher established'
  obs+=f'; {len(refs)} local requests, {len(pdf)} complete PDFs, {len(js)} complete structured samples'
  errors=[x for x in p['source_specific_gaps'] if 'receipt' in x]
  limit='; '.join(x['receipt']+': '+str(x.get('status'))+(' '+x['error'] if x.get('error') else '') for x in errors[:2])
  if not r['authority_url_literal']:limit+='; state website href blank'
  if not limit:limit='November full count-key mapping, eligible unprocessed pool and measured cadence remain unresolved'
  lines.append('| ['+r['current_directory_label']+'](parents/'+aid+'.json) / '+r['historical_reference_only']+' | '+r['historical_priority_children']+' / '+r['full_historical_children']+' | '+obs.replace('|','\\|')+' | '+limit.replace('|','\\|')+' |')
 (HERE/'parent-findings.md').write_text('\n'.join(lines)+'\n')
 root=ET.fromstring(body(parsefile(HERE/'receipts/state-candidate-file-xml.json')));candidates=[dict(x.attrib) for x in root if x.get('OfficeName')=='UNITED STATES SENATOR']
 office_links={x['literal_href'] for x in parsefile(HERE/'parsed/state-senate-candidates-all.json.gz')['links'] if x['text']=='UNITED STATES SENATOR' and 'CandidateList.aspx?' in x['literal_href']};assert len(office_links)==1
 write(HERE/'november-candidate-scope.json',dict(scope='bounded official filing/status and signed local specimen; not exhaustive local declarations or later changes',complete_state_download_rows=len(root),all_status_senate_records=candidates,current_state_navigation_election_id='sejIrI+Qmww=',current_office_selector_metadata='13387',current_office_detail_href=next(iter(office_links)),state_counts_election_id=None,state_counts_contest_choice_unit_keys=None,state_website_print_clock_literal='10/19/2026 8:11:09 PM',state_website_print_clock_timezone=None,rockford_specimen=dict(receipt='authority-110-L1-3',pdf_page_1based=1,visually_observed_signature=True,ballot_order=['DON TRACY / REPUBLICAN','JULIANA STRATTON / DEMOCRATIC','WHITFIELD HARRINGTON JR / AMERICAN CENTER PARTY'],senate_writein_blank_on_inspected_page=False),cook_declared_writein_scope=dict(receipt='cook-november-writeins',literal_heading='Official List of Write-In Candidates (Suburban Cook County)',senate_entry_observed=False,absence_not_statewide_exhaustion=True),later_exceptions='Regular notarized local declaration deadline Sept3; late sustained-objection exception may run through Oct27; local declarations and later orders not exhausted. No statewide write-in zero imputed.'))
 visual=parsefile(HERE/'previews/render-scope.json')
 for x in visual:
  x['actual_visual_inspection']=True;x['inspection_note']={'rockford-november-specimen':'Inspected entire rendered page1: visible Executive Director signature/certification block; R,D,American Center Senate order; no Senate write-in blank; other contests have blanks. Signature identity not independently authenticated.','state-active-candidates':'Inspected rendered page1: November3 header; website-generated Oct19 8:11:09PM clock with no printed timezone; three printed Senate candidates/parties/file times. This is a website candidate list, not signed statewide certification.','calendar-mail-counting':'Inspected rendered PDF page53: 48-hour uncounted-category notice, Nov10 supporting-material date, Nov17 mail count; calendar says certification prior to Election Day, narrower wording than section19-8 ElectionDay-or-earlier.'}[x['id']]
 write(HERE/'previews/actual-visual-review.json',dict(browser_used=False,whole_pdf_visual_review=False,pages=visual))
 print('parent table',len(rows),'candidate metadata',len(candidates))
if __name__=='__main__':main()
