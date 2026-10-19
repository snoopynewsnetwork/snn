"""Read-only reused primary PDFs: independent visual/text verification, no result IDs."""
from pathlib import Path
import gzip,hashlib,json,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 target=DATA/'coordinator-current-ballot-review.json'
 refs=json.loads((DATA/'baselines/source/references.json').read_bytes())
 expected={'sos-2026-sample-ballot':('36752cfc3c7b44da74a42e9d49571221f4f8d48381259ab2f6b7ebed723bd67f',87597),'sos-2026-majority-chart':('db334a82e345229a3b2c516e7262da309ec98e82caea94ea4a8fed7eecce9ce7',214529),'sos-2026-vote-rule-clarification':('fffddeeadc1db28c6a9f0bc1769b48328f0fb9e202be8ef0bb78098e0614b8fc',107728),'sos-2026-absentee-availability':('2512914f59e5772d21ecd15fed61ecdec0702ab134fdc85328239d522f0960b4',110987)}
 pins=[];texts={}
 for sid,(digest,size) in expected.items():
  r=next(r for r in refs if r['id']==sid);s=(ROOT/r['path']).read_bytes();b=gzip.decompress(s);assert sha(b)==digest==r['raw_sha256'] and len(b)==size and sha(s)==r['stored_sha256']
  pins.append(dict(r))
  if sid=='sos-2026-vote-rule-clarification':
   parent=b.decode();assert 'Majority_Chart.pdf' in parent
   chart=next(x for x in refs if x['id']=='sos-2026-majority-chart');assert chart['url'] in parent
   continue
  if sid=='sos-2026-absentee-availability':
   parent=b.decode()
   for phrase in ['feed it directly into voting machines','These ballots will not be tabulated until election night','mail-in absentee voting process remains unchanged']:
    assert phrase in parent
   assert 'https://legiscan.com/MS/text/HB859/id/3393148' in parent
   continue
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'source.pdf';p.write_bytes(b);texts[sid]=subprocess.check_output(['pdftotext','-layout','-f','1','-l','1',str(p),'-']).decode()
 assert re.search(r'U\.S\. Senate\s+Plurality',texts['sos-2026-majority-chart'])
 text=texts['sos-2026-sample-ballot'];assert 'SAMPLE Official Election Ballot' in text and 'Tuesday, November 3, 2026' in text
 for name,label in [('Scott Colom','Democrat'),('Cindy Hyde-Smith','Republican'),('Ty Pinkins','Independent')]:assert re.search(re.escape(name)+r'\s+'+label,text)
 pages=[]
 for f in ['majority-chart-page1.png','sample-ballot-page1.png']:
  p=DATA/'coordinator-qa'/f;pages.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size})
 out={'status':'pass_primary_publication_and_independent_visual_read','primary_originals_reused_read_only':pins,'visual_pages':pages,'current_Senate_sample':{'date':'2026-11-03','vote_for':1,'printed':[{'name':'Scott Colom','label':'Democrat'},{'name':'Cindy Hyde-Smith','label':'Republican'},{'name':'Ty Pinkins','label':'Independent'}],'writein_space':True,'document_status':'SAMPLE; not signed final certificate or withdrawal registry'},'SOS_office_specific_chart':{'U.S._Senate':'Plurality','state_executives':'Majority','ordinary_vs_special':'Ordinary chart is not a repeal/inference about the separate2018 special runoff stage'},'scope':'Primary SOS press-parent/chart authority and actual November sample independently read. No ENR IDs, complete eligible-writein universe, no later substitution claim, no approved geography or probability. Official-results worker must later check exact current statutes/orders and election-specific receipt/reporting rules.'}
 out['SOS_2026_in_person_absentee_method_change']={'publication_date':'2026-09-21','paper_ballot':'fed directly into voting machine rather than envelope and ballot box','tabulation':'not until election night','mail_in_process':'SOS says unchanged','observed_legislation_href':'https://legiscan.com/MS/text/HB859/id/3393148','scope':'Primary SOS description independently checked. Historical combined absentee/method counts are not automatically equivalent to November2026 categories. No source-ID, reporting allocation, timing/cadence or operative receipt-rule conclusion follows.'}
 target.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'primary_originals':len(pins),'visually_read_pages':2,'USSenate_rule':'Plurality','sample_candidates':3,'current_absentee_method_warning':True}))
if __name__=='__main__':main()
