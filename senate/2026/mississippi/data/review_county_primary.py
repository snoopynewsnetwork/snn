"""Independent corrected primary county vector/order; no native acceptance."""
from pathlib import Path
import csv,gzip,hashlib,io,json
ROOT=Path(__file__).resolve().parents[1];NEWS=ROOT/'data/news'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 manifest=json.loads((NEWS/'manifest.json').read_bytes());r=next(r for r in manifest if r['id']=='sos-2024-recap-csv');stored=(NEWS/r['asset']).read_bytes();raw=gzip.decompress(stored)
 assert sha(stored)==r['stored_sha256'] and sha(raw)==r['raw_sha256'];rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
 senate=[r for r in rows if r['Office']=='United States-Senate'];assert len(senate)==164
 counties={};original_totals={};corrected_totals={}
 explicit={'Ty Pinkins':7130,'Roger F. Wicker':8205}
 for row in senate:
  county=row['County'];name=row['Candidate'];old=int(row['County Total']);n=explicit[name] if county=='Pike' else old
  counties.setdefault(county,{})[name]=n;original_totals[name]=original_totals.get(name,0)+old;corrected_totals[name]=corrected_totals.get(name,0)+n
 assert len(counties)==82 and corrected_totals=={'Ty Pinkins':451981,'Roger F. Wicker':763420}
 assert all(set(v)==set(explicit) for v in counties.values())
 ranking=[];cumulative=0
 for n,(name,values) in enumerate(sorted(counties.items(),key=lambda r:(-sum(r[1].values()),r[0])),1):
  cumulative+=sum(values.values());ranking.append({'rank':n,'county_literal':name,'source_candidates':values,'contest_votes':sum(values.values()),'cumulative_votes':cumulative})
 denominator=sum(corrected_totals.values());threshold=(4*denominator+4)//5;cross=next(r for r in ranking if r['cumulative_votes']>=threshold)
 assert denominator==1215401 and ranking[14]['cumulative_votes']==653846
 assert cross['rank']==41 and cross['county_literal']=='Newton' and cross['contest_votes']==9219
 assert ranking[39]['cumulative_votes']==970209 and cross['cumulative_votes']==979428 and threshold==972321
 primary_review=json.loads((ROOT/'data/coordinator-pike-update-review.json').read_bytes())
 assert primary_review['Senate_difference']==2718
 for check in primary_review['candidate_checks']:
  if check['office']=='United States-Senate':assert corrected_totals[check['candidate_literal']]==check['certified_state_reading']
 out={'status':'pass_county_primary_order_native_acceptance_pending','source_CSV_pin':{'path':'data/news/'+r['asset'],'raw_sha256':sha(raw),'stored_sha256':sha(stored)},'actual_Pike_replacement_source_review':'data/coordinator-pike-update-review.json','original_CSV_candidate_sums':original_totals,'corrected_explicit_primary_candidate_sums':corrected_totals,'denominator':denominator,'top15_votes':ranking[14]['cumulative_votes'],'threshold_integer80':threshold,'minimum80_count':41,'preceding40_votes':ranking[39]['cumulative_votes'],'priority_votes':cross['cumulative_votes'],'crossing':cross,'remainder41_votes':denominator-cross['cumulative_votes'],'full82_descending_order':ranking,'qualification':'Actual updated Pike candidate cells replace the earlier same-county CSV values; no scaling/residual allocation. Named SEMS/certified universe is separate from generic write-in marks in certain county originals. This checks county arithmetic only, not native coverage, validity/candidate-method allocation, legal current geography or dispatch acceptance.'}
 (ROOT/'data/coordinator-county-primary-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='full82_descending_order'}))
if __name__=='__main__':main()
