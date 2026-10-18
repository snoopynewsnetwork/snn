"""Independent bounded original candidate-table and current-code review."""
import csv,gzip,hashlib,html,io,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
RAW=ROOT/'results-sources/raw'
def entity(name):
 meta=json.loads((RAW/(name+'.meta.json')).read_text());stored=(RAW/(name+'.body.gz')).read_bytes();b=gzip.decompress(stored)
 assert hashlib.sha256(b).hexdigest()==meta['original_sha256']
 return b,{'source':str((RAW/(name+'.meta.json')).relative_to(ROOT)),'url':meta['requested_url'],'sha256':meta['original_sha256'],'bytes':len(b)}
def plain(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s))).strip()
def main():
 b,ref=entity('candidate-general-senate-results-search2');s=b.decode();assert 'value="22596"' in s
 rows=[]
 for match in re.finditer(r'<tr\s+data-index="(\d+)"\s+data-key="(\d+)"[^>]*>(.*?)</tr>',s,re.S):
  cells=[plain(c) for c in re.findall(r'<td\b[^>]*>(.*?)</td>',match[3],re.S)]
  assert len(cells)==7 and cells[0]=='U.S. Senate'
  rows.append({'ordinal':int(match[1]),'tracking_id':match[2],'name':cells[2],'party':cells[4],'filing_scope':cells[5],'status':cells[6]})
 assert len(rows)==14
 b,export_ref=entity('candidate-senate-export-search2');export=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))));assert len(export)==14
 for row,e in zip(rows,export):
  assert row['name']==e['Ballot Name (first - middle)']+' '+e['Ballot Name (last - suffix)'] and row['party']==e['Party'] and row['status']==e['Status']
 active=[r for r in rows if r['status']=='Active'];assert [(r['name'],r['party'],r['tracking_id']) for r in active]==[('Annie Andrews','Democratic','24011'),('Darline Graham','Republican','25300'),('Mark Hackett','Constitution','24195'),('Kasie Whitener','Libertarian','23917')]
 _,pdf_ref=entity('candidate-senate-print-search2')
 sections=[]
 for name,section,required in [('code-13','SECTION 7-13-2210.',['results in a tie vote','two weeks following']),('code-15','SECTION 7-15-700.',['military-overseas ballot','business day before the county canvass'])]:
  b,r=entity(name);t=plain(b.decode());start=t.index(section);end=t.find('SECTION ',start+len(section));block=t[start:end];assert all(x in block for x in required);sections.append({'section':section,'original':r,'complete_section_text':block})
 result={'status':'pass_original_candidate_tables_and_code','election_tracking_id':'22596','candidate_rows':rows,'active_candidates':active,'table_original':ref,'csv_original':export_ref,'print_pdf_original':pdf_ref,'visual_review':'Coordinator viewed exact retained PDF page1:November3 general header and all14 status rows; four Active names/parties match.','current_code_sections':sections,'limits':['Candidate tracking IDs are not ENR candidate/contest IDs.','Not a signed statewide final-ballot certificate or full future substitution/withdrawal proof.','General highest-vote rule and tie-only runoff distinct from primary majority.','Grant v Belangia Aug18 opinion remands remedy/timing; no later operative remedy/stay/mandate verified here.']}
 (ROOT/'coordinator-current-source-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'all_status_rows':14,'active_names':[r['name'] for r in active],'code_sections':len(sections)}))
if __name__=='__main__':main()
