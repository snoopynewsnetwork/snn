"""Reproduce independently original-read county special/runoff vectors and controls."""
import csv,json
from acquire_sources import BASE,OUT,savejson

def main():
 counties=list(csv.DictReader((BASE/'data/county-turnout.csv').open()));byname={r['county'].lower().replace(' ','-'):r for r in counties};data=json.loads((OUT/'historical-county-readings.json').read_text());rows=[];controls=[]
 for date,prefix,expected in [('2018-11-06','sos-2018-county-',{'Tobey Bernard Bartee':13852,'Mike Espy':386742,'Cindy Hyde-Smith':389995,'Chris McDaniel':154878}),('2018-11-27','sos-2018-runoff-county-',{'Mike Espy':420819,'Cindy Hyde-Smith':486769})]:
  readings=[r for r in data['readings'] if r['election_date']==date];sums={name:sum(r['candidate_votes'][name] for r in readings) for name in expected}
  for r in readings:
   source_key=r['source_id'].removeprefix(prefix);alias={'jackon':'jackson','jefferson-davis':'jeff-davis'}.get(source_key,source_key);c=byname[alias]
   for name,value in r['candidate_votes'].items():rows.append(dict(election_date=date,contest='United States-Senate special' if date.endswith('06') else 'United States-Senate special runoff',county=c['county'],fips=c['fips'],source_county_route_literal=source_key,candidate=name,votes=value,source_id=r['source_id'],raw_sha256=r['raw_sha256'],source_page=r['page'],source_TOTAL_column=r['source_column'],source_position_scope='County TOTAL control; native constituents separately reconciled',party_scope=r['party_scope']))
  controls.append(dict(election_date=date,reviewed_counties=len(readings),expected_counties=82,full_coverage=len(readings)==82,candidate_sums=sums,primary_certificate_candidate_controls=expected,differences={name:sums[name]-expected[name] for name in expected},all_candidates_reconcile=len(readings)==82 and sums==expected))
 with (OUT/'historical-county-candidate-votes.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 savejson(OUT/'historical-county-controls.json',dict(contests=controls,aliases=[dict(source_route='jackon',county='Jackson',fips='28059',evidence='2018 runoff original p4 explicitly prints County of Jackson; filename/index typo remains retained',preview='data/turnout/qa/sos-2018-runoff-county-jackon-p04-historical-upright.jpg'),dict(source_route='jefferson-davis',county_csv_literal='Jeff Davis',fips='28065',evidence='2018 runoff original p3 prints County of Jeff Davis; EAC source identifies JEFFERSON DAVIS.')],qualification='No source-vintage pooling or residual allocation. State reconciliation does not approve native/current geography.'))
 print(json.dumps(controls))
if __name__=='__main__':main()
