"""Read-only primary candidate-list and certification-announcement preparation."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,json,urllib.parse
DATA=Path(__file__).resolve().parent
STATE=DATA.parent
NEWS=DATA/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b))
class Links(HTMLParser):
 def __init__(self):super().__init__();self.hrefs=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a'and'href'in dict(attrs):self.hrefs.append(dict(attrs)['href'])
def main():
 m={r['id']:r for r in json.loads((NEWS/'manifest.json').read_bytes())};chain=[]
 for parent,child in [('sos-2026-election-parent','sos-final-general-candidate-pdf'),('sos-2026-general-certification-notice-parent','sos-2026-general-certification-notice-pdf')]:
  pr,ch=m[parent],m[child];b=gzip.decompress((NEWS/pr['asset']).read_bytes());assert sha(b)==pr['raw_sha256']and pr['status']==ch['status']==200;p=Links();p.feed(b.decode());matches=[h for h in p.hrefs if urllib.parse.urljoin(pr['final_url'],h)==ch['url']];assert len(matches)==1
  raw=gzip.decompress((NEWS/ch['asset']).read_bytes());assert sha(raw)==ch['raw_sha256']and raw.startswith(b'%PDF-');chain.append(dict(parent_source_id=parent,parent_original=pin(NEWS/pr['asset']),parent_raw_sha256=sha(b),literal_child_href=matches[0],resolved_child_URL=ch['url'],child_source_id=child,child_original=pin(NEWS/ch['asset']),child_raw_bytes=len(raw),child_raw_sha256=sha(raw),child_HTTP_receipt=ch))
 assert chain[0]['child_raw_sha256']=='d27a071715896b8c82b8cce8d48200b4207ba10c44f1778f56f92c4efcd7cf96'and chain[1]['child_raw_sha256']=='9f044775f2ef3569879c8d3043f0be8b04128173d37ca9e72a37bb8cacc8ebcb'
 rows=[dict(source_row=i+1,office_literal='For United States Senator',term_years=6,vote_for=1,party_literal=party,candidate_literal=name)for i,(party,name)in enumerate([('Republican','Pete Ricketts'),('Legal Marijuana NOW','Mike Marvin'),('Nebraska Working People','Robin Richards'),('America First','Chuck Conboy'),('By Petition','Dan Osborn')])]
 app=json.loads((DATA/'coordinator-current-app-preflight.json').read_bytes());old=app['senate_catalog_rows'];assert len(old)==5 and {r['ID']for r in old}=={148};catalog={(' '.join(r['name'].split()),r['Party'].casefold())for r in old};assert catalog=={(r['candidate_literal'],r['party_literal'].casefold())for r in rows}
 out=dict(status='bounded_primary_certification_announcement_and_final_candidate_list_review_no_worker_launch',source_chains=chain,actual_complete_candidate_list_pages=24,reviewed_candidate_list_actualPDFpage=1,printed_list_date='9/11/2026',printed_election='November 3, 2026 General Election',Senate_rows=rows,primary_certification_announcement_date='September 11, 2026',announcement_actual_PDFpages=1,announcement_scope='SOS announces certification of final candidate/ballot-measure list for November3general',fresh_complete_original_pages_visually_reviewed=[pin(NEWS/'qa/current-certification/candidate-list-p1-original.png'),pin(NEWS/'qa/current-certification/certification-notice-p1-original.png')],renderer=dict(program='pdftoppm',longest_dimension_pixels=3500,enhancement_rotation='none'),already_retained_final_candidate_PDF_reused_without_duplicate=True,current_setup_comparison=dict(existing_preflight=pin(DATA/'coordinator-current-app-preflight.json'),all_five_literal_names_and_parties_match=True,party_case_difference=dict(list_literal='Legal Marijuana NOW',setup_literal='Legal Marijuana Now'),repeated_contest_or_search_ID=148,unique_candidate_IDs_established=False,current_counts_admitted=False),qualification='Both actual primary parent hrefs resolve to retained complete originals; the previously acquired24page candidate list is reused exactly and firstpage five Senate rows freshly viewed alongside the newly acquired complete onepage certification announcement. DanOsborn remains literalByPetition and the other four source parties remain separate; no Democratic Senate label is invented. A press announcement and filed candidate listing do not supply a signed certification instrument, full eligible namedwritein/withdrawal/latercourt scope, November feed candidateIDs, current reporting geometry, or genuine counts. ID148 repeats across all5setupchoices and is not five unique candidateIDs. All21laterstates remain queued and no new research worker/priority acceptance follows.',current_counts_admitted=False,priority_accepted=False,new_worker_launched=False)
 p=DATA/'coordinator-current-certification-preflight.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
