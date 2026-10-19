"""Offline bounded court/source chronology review; no election data or geographic admission."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,json,re,subprocess,tempfile
DATA=Path(__file__).resolve().parent;ROOT=DATA.parent;REPO=ROOT.parents[2];SRC=DATA/'coordinator-legal-preparation'
def sh(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(REPO)),'bytes':len(b),'sha256':sh(b)}
class H(HTMLParser):
 def __init__(self):super().__init__();self.text=[];self.links=[]
 def handle_data(self,s):self.text.append(s)
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='a'and'href'in d:self.links.append(d['href'])
def flatten(b):
 h=H();h.feed(b.decode(errors='replace'));return re.sub(r'\s+',' ',' '.join(h.text)).strip(),h.links
receipts={};raws={};pins=[]
for f in sorted(SRC.glob('*.receipt.json')):
 j=json.loads(f.read_bytes());b=(REPO/j['body']['stored_path']).read_bytes();assert len(b)==j['body']['stored_bytes']and sh(b)==j['body']['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==j['body']['raw_bytes']and sh(raw)==j['body']['raw_sha256']and j['status']==200
 receipts[j['id']]=j;raws[j['id']]=raw;pins.extend([pin(f),pin(REPO/j['body']['stored_path'])])
assert len(receipts)==7
faq,flinks=flatten(raws['sos-current-absentee-information']);docket,dlinks=flatten(raws['watson-scotus-docket']);index,ilinks=flatten(raws['fifth-circuit-opinions-september9']);query,qlinks=flatten(raws['fifth-circuit-published-form-docket-query'])
for text in ['postmarked on or before Election Day (November 3, 2026)','five (5) business days of the election, or November 10, 2026','Optical Mark Scanning Voting Machine'] :assert text in faq
for text in ['Jun 29 2026','Jul 31 2026','Judgment Issued']:assert text in docket
assert '/opinions/unpub/24/24-60395.0.pdf'in qlinks
assert '/opinions/unpub/24/24-60395.0.pdf'not in ilinks
assert 'name="docket"'in raws['fifth-circuit-opinions-september9'].decode()and'action="/opinions"'in raws['fifth-circuit-opinions-september9'].decode()
texts={};pagecounts={}
for key in ['watson-bound-opinion','fifth-circuit-september9-remand']:
 with tempfile.TemporaryDirectory()as td:
  p=Path(td)/'original.pdf';p.write_bytes(raws[key]);text=subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode();pages=text.split('\f');pages=[x for x in pages if x.strip()];pagecounts[key]=len(pages);texts[key]=pages
assert pagecounts=={'watson-bound-opinion':49,'fifth-circuit-september9-remand':2}
proof=texts['watson-bound-opinion'];assert 'PRELIMINARY PRINT'in proof[0]and'Page Proof Pending Publication'in proof[0]
assert 'fve (5) business days'in proof[9]and'It is so ordered'in proof[26]  # Original page10 glyphs visually read five; raw text-layer omission retained.
remand=' '.join(' '.join(texts['fifth-circuit-september9-remand']).split());assert 'Document: 255-1'in remand and'09/09/2026'in remand and'The judgment of the district court is AFFIRMED'in remand and'ON REMAND FROM'in remand
shared=[]
for name in ['watson-opinion','watson-docket','watson-docket-operative-85']:
 p=REPO/'senate/2026/florida/data/results-sources/source'/f'{name}.receipt.json';j=json.loads(p.read_bytes());b=(REPO/'senate/2026/florida'/j['body_path']).read_bytes();assert len(b)==j['stored_bytes']and sh(b)==j['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==j['raw_bytes']and sh(raw)==j['raw_sha256'];shared.extend([pin(p),pin(REPO/'senate/2026/florida'/j['body_path'])])
judgment=REPO/'senate/2026/florida/data/results-sources/watson-docket-operative-85.pages.json';jt=json.loads(judgment.read_bytes())['pages'][0]['text'];assert 'June 29, 2026'in jt and'reversed'in jt and'remanded'in jt;shared.append(pin(judgment))
renderpins=[]
for p in sorted((SRC/'previews').glob('*.png')):renderpins.append(pin(p))
assert len(renderpins)==7
out={'status':'pass_bounded_primary_court_and_current_SOS_instruction_preparation','source_capture_pins':pins,'original_page_render_pins':renderpins,'read_only_completed_Florida_original_pins':shared,'request_observations':7,'HTTP200':7,'actual_source_dates':{'Supreme_Court_opinion':'2026-06-29','Supreme_Court_judgment_face':'2026-06-29','Supreme_Court_docket_Judgment_Issued':'2026-07-31','Fifth_Circuit_Document255_1_filed':'2026-09-09','SOS_election_specific_availability_publication':'2026-09-21'},'findings':[{'source':'watson-bound-opinion','scope':'Official49-page PRELIMINARY PRINT / Page Proof Pending Publication, not a claim of final bound publication; earlier slip edition is retained separately read-only.','actual_PDFpages_visually_reviewed':[1,6,10,27],'printed_majority_pages_reviewed':[676,680,697],'page10_original_text_layer':'fve (5) business days','page10_visual_glyph_reading':'five (5) business days','result':'The majority rejects federal election-day statutory preemption of this Mississippi late-receipt provision; the operative conclusion reverses and remands. The ruling does not itself supply every state eligibility, cure, UOCAVA or current administrative deadline.'},{'source':'watson-scotus-docket','scope':'Fresh full official docket capture; opinion date and issuance entry remain separate clocks.','latest_proceeding_entry_observed':'July31,2026 Judgment Issued','complete_lower_court_or_future_docket_claim':False},{'source':'fifth-circuit-published-form-docket-query','scope':'Actual retained form action and literal input names/values recovered September9 unpublished disposition omitted from first broad date-bounded page; absence from that first page was not absence from the court.','observed_exact_case_links':[x for x in qlinks if '24-60395'in x]},{'source':'fifth-circuit-september9-remand','scope':'Both complete original pages independently rendered and visually inspected, Case24-60395 Document255-1.','actual_PDFpages_visually_reviewed':[1,2],'result':'On remand, the Fifth Circuit affirms the district court judgment in light of Watson. This is an actual post-Supreme-Court disposition; a complete later mandate/rehearing/district docket has not been recovered here.'},{'source':'sos-current-absentee-information','scope':'Current election-specific ordinary absentee instructions, separately sourced from the court judgment.','mail_postmark_deadline_printed':'2026-11-03','mail_receipt_deadline_printed':'2026-11-10','receipt_rule_printed_business_days':5,'in_person_absentee_method':'Paper ballot scanned into OMR; counted after polls close','independently_admitted_current_vote_or_remaining_pool':False}], 'remaining_gaps':['Complete later Fifth Circuit mandate/rehearing and district docket sequence is not independently recovered by an opinions index or Supreme Court docket.','Current full codified section and every exception, cure/signature/witness and UOCAVA rule require separate official-results review.','Publication metadata and HTTP capture clocks do not establish operational feed cadence, exact outstanding Senate votes, or expected reporting identities.'],'qualification':'Seven bounded current primary observations and exact retained court originals support this scoped chronology and printed state guidance. No worker-owned files, completed Florida originals, historical votes, native887 proposal or current-geography approval are changed.','formal_dispatch_accepted':False,'current_geography_approved':False,'current_results_admitted':False}
p=DATA/'coordinator-receipt-rule-primary-preparation.json';b=(json.dumps(out,indent=2)+'\n').encode()
if p.exists():assert p.read_bytes()==b,'Immutable review drift'
else:p.write_bytes(b)
print(json.dumps({'status':out['status'],'output_pin':pin(p),'observations':len(receipts),'original_PDF_render_pages':len(renderpins)}))
