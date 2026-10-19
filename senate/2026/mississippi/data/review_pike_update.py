"""Check manual readings of actual updated Pike and certified summary scans."""
from pathlib import Path
import csv,gzip,hashlib,io,json
ROOT=Path(__file__).resolve().parent.parent
NEWS=ROOT/'data/news'
manifest=json.loads((NEWS/'manifest.json').read_text())
def source(name):
 r=next(r for r in manifest if r['id']==name);stored=(NEWS/r['asset']).read_bytes();raw=gzip.decompress(stored)
 assert hashlib.sha256(raw).hexdigest()==r['raw_sha256'] and hashlib.sha256(stored).hexdigest()==r['stored_sha256']
 return r,raw
csv_receipt,b=source('sos-2024-recap-csv');rows=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
# Read from the complete, visually inspected updated Pike page4 and signed state summaries.
readings=[
 ('United States-Senate','Ty Pinkins',7130,451981),
 ('United States-Senate','Roger F. Wicker',8205,763420),
 ('United States-President','Presidential Electors for Kamala D. Harris',7402,466668),
 ('United States-President','Presidential Electors for Chase Oliver',20,2536),
 ('United States-President','Presidential Electors for Jill Stein',17,1873),
 ('United States-President','Presidential Electors for Randall Terry',13,1030),
 ('United States-President','Presidential Electors for Donald J. Trump',7943,747744),
 ('United States-President','Presidential Electors for Shiva Ayyadurai',10,688),
 ('United States-President','Presidential Electors for Claudia De la Cruz',9,1075),
 ('United States-President','Presidential Electors for Robert F. Kennedy Jr.',58,5387),
 ('United States-President','Presidential Electors for Peter Sonski',13,1007),
]
checks=[]
for office,start,new,state in readings:
 matches=[r for r in rows if r['Office']==office and r['Candidate'].startswith(start)]
 assert len(matches)==82 and len({r['County'] for r in matches})==82
 pike=next(r for r in matches if r['County']=='Pike');old=int(pike['County Total']);csv_sum=sum(int(r['County Total']) for r in matches)
 assert {int(r['State Total']) for r in matches}=={csv_sum}
 assert csv_sum-old+new==state
 checks.append({'office':office,'candidate_literal':pike['Candidate'],'CSV_Pike':old,'updated_Pike':new,'difference':new-old,'CSV_state_sum':csv_sum,'revised_state_sum':state,'certified_state_reading':state})
pins=[]
for name in ['sos-2024-recap-csv','sos-2024-certified-sen-pdf','sos-2024-certified-pres-pdf','sos-2024-county-pike','sos-2024-county-pike-updated','sos-2024-county-coahoma','sos-2024-county-coahoma-updated','sos-2024-county-recap-index']:
 r,_=source(name);pins.append({'source_id':name,'url':r['url'],'raw_sha256':r['raw_sha256'],'asset':'data/news/'+r['asset']})
links=json.loads((NEWS/'county-2024-links.json').read_text());assert len(links['links'])==84
assert {r['county_literal'] for r in links['links'] if 'Updated' in r['county_literal']}=={'Coahoma Updated','Pike Updated'}
previews=[]
for filename in ['sos-2024-county-pike-updated-04.png','sos-2024-county-coahoma-updated-3-rotated.png','sos-2024-county-coahoma-3-rotated.png','certified-senate-2024-page3.png','certified-president-2024-2.png']:
 p=NEWS/'previews'/filename;previews.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
result={'status':'pass_manual_primary_preflight_not_priority_acceptance','county_index_PDF_links':84,'county_count':82,'separate_updated_links':['Coahoma Updated','Pike Updated'],'candidate_checks':checks,'Senate_difference':sum(r['difference'] for r in checks if r['office']=='United States-Senate'),'President_difference':sum(r['difference'] for r in checks if r['office']=='United States-President'),'source_pins':pins,'visually_reviewed_pages':previews,'qualification':'The explicit updated Pike original explains every statewide Senate and presidential CSV/certificate candidate difference. No residual allocation or scaling. All82 county/native extractions, publication/certification chronology and full cross-source reconciliation still require independent question workers. Coahoma original and updated Senate totals both4533/2146 match CSV; no cause for its update inferred.'}
(ROOT/'data/coordinator-pike-update-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'candidate_checks':len(checks),'Senate_difference':result['Senate_difference'],'President_difference':result['President_difference']}))
