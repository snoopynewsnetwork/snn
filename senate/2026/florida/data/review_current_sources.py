"""Independent retained-source checks; setup/privacy/future-law are not live data."""
import gzip,hashlib,html,json,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'data/results-sources/source'
pins=[]
def raw(name):
 p=SOURCE/(name+'.receipt.json');r=json.loads(p.read_text());body=ROOT/r['body_path'];stored=body.read_bytes();b=gzip.decompress(stored)
 assert r['status']==200 and len(b)==r['raw_bytes'] and hashlib.sha256(b).hexdigest()==r['raw_sha256']
 assert len(stored)==r['stored_bytes'] and hashlib.sha256(stored).hexdigest()==r['stored_sha256']
 pins.append({'receipt':str(p.relative_to(ROOT)),'receipt_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'body':str(body.relative_to(ROOT)),'raw_sha256':r['raw_sha256'],'stored_sha256':r['stored_sha256'],'url':r['final_url']})
 return b

def plain(b):
 s=b.decode(errors='replace');s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',s,flags=re.S|re.I)
 return ' '.join(html.unescape(re.sub(r'<[^>]*>',' ',s)).split())

lake=plain(raw('webdiscovered-LAK'))
assert '2026 General Election Date: 11/3/2026' in lake
assert 'Ballots Cast: 0' in lake and 'Precincts Reporting: 0 / 92' in lake
for name in ['Ashley Moody (REP)','Angie Nixon (DEM)','Neil J. Gillespie (NPA)']:
 assert name+' 0 0 0 0 0.00%' in lake
assert all(x+': Not Reported' in lake for x in ['Election Day','Early Votes','Vote By Mail'])
assert 'between 1 and 29 votes' in lake and '98.0981(3)(a)' in lake

summary=json.loads(raw('pinellas-summary'));sen=next(r for r in summary if r['K']=='0004')
assert sen['C']=='United States Senator' and sen['PR']==sen['TP']==286
assert sen['V']==[260571,241729,3073,2984,3147,438] and sen['T']==sum(sen['V'])==511942
details=json.loads(raw('pinellas-details'));det=next(r for r in details['Contests'] if r['K']=='0004')
assert len(det['P'])==len(set(det['P']))==len(det['V'])==286
assert all(len(row)==6 and all(value=='protected' for value in row) for row in det['V'])
assert det['T'] is None and det['Eid']==det['Cid']==[]
settings=json.loads(raw('pinellas-electionsettings'))
clock=settings['websiteupdatedat'];assert '11/15/2024' in clock and 'EST' in clock

session=raw('law-2026-26')
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'law.pdf';p.write_bytes(session);text=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True,check=True).stdout
assert 'Section 34.' in text and 'shall take effect January 1, 2027' in text
for number,section in [(22,'102.111'),(23,'102.141'),(24,'102.166')]:
 start=text.index(f'Section {number}.');end=text.index(f'Section {number+1}.',start);block=text[start:end]
 assert section in block and not re.search(r'effective|take effect',block,re.I)
operative=plain(raw('operative2025-102.111'));assert '8 a.m.' in operative and '14th day after a general election' in operative

# The final judgment is a separate operative document, not an opinion-date inference.
judgment=raw('watson-docket-operative-85')
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'judgment.pdf';p.write_bytes(judgment);text=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True,check=True).stdout
assert 'June 29, 2026' in text and 'reversed' in text.lower() and 'remanded' in text.lower()
docket=plain(raw('watson-docket'));assert 'Jul 31 2026 Judgment Issued.' in docket

review={'status':'pass_with_operational_exclusions','source_pins':pins,'Lake_November_setup':{'date':'2026-11-03','ballots':0,'precincts_reporting':0,'precincts_total':92,'publisher_clock_literal':'10/15/2026 11:27:51 am','publisher_timezone':None,'all_three_Senate_choices_zero':True,'method_status':'Not Reported','genuine_votes_admitted':False},'Pinellas_historical':{'election_id':'122583','version':'355096','Senate_contest':'0004','unit_labels':286,'choice_positions_per_unit':6,'protected_native_cells':1716,'native_total':None,'native_candidate_IDs':[],'summary_counts':sen['V'],'summary_total':sen['T'],'publisher_clock_literal':clock,'numeric_native_reconciliation':'Unavailable from protected/null publication. Five named choices and generic write-in scope stay separate from legal valid/named county totals. No historical/current physical join inferred.'},'effective_date_review':{'law':'chapter2026-26','sections':[22,23,24],'default_effective':'2027-01-01','earlier_override_in_these_sections':False,'operative_pre2027_102111':'8am on14th day after general, giving November17,2026 ordinary state certification meeting; verify current calendar and later orders independently.','visual_pages':['data/coordinator-qa/law2026-26-section-22-26.png','data/coordinator-qa/law2026-26-section-34-36.png'],'qualification':'Complete relevant rendered pages independently read, including stricken8/added9 and the effective-date clause. Do not apply future codification to November2026.'},'Watson_judgment':{'document_date_literal':'June 29, 2026','docket_issue_date':'2026-07-31','disposition':'Reversed and remanded','scope':'Separate judgment face is dated June29; captured docket records issue July31. Those are distinct source clocks. No automatic change to Florida ordinary receipt deadline inferred from the federal case.'},'production_admission':'No genuine November counts, measured cadence, complete current candidate/unit universe or exact outstanding Senate votes admitted.'}
(ROOT/'data/coordinator-current-source-review.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({'status':review['status'],'source_entities':len(pins),'protected_cells':1716,'Lake_setup_only':True}))
