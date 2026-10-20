#!/usr/bin/env python3
from pathlib import Path
import csv,json,gzip,re,collections
from extract import raw,writejson,writecsv,clean,SPECS
P=Path(__file__).resolve().parent

def main():
 participation=list(csv.DictReader((P/'extracted/participation-totals.csv').open()));stats=json.loads((P/'extracted/report-statistics.json').read_text());out=[];coverage=[]
 base=list(csv.DictReader((P/'native-baselines.csv').open()));hier=json.loads((P/'extracted/participation-hierarchy.json').read_text())
 for r in stats:
  year=r['year'];rs=[x for x in participation if int(x['year'])==year];state=next(x for x in rs if x['scope']=='statewide');stcsv=[x for x in csv.DictReader((P/'extracted/state-original-csv-rows.csv').open()) if x['source_id']==SPECS[year][1]]
  out.append(dict(year=year,source_id=r['source_id'],results_header_reported_votes=r['reported_votes_literal'],results_header_registered_literal=r['registered_votes_literal'],results_header_reporting=r['precincts_reporting'],results_header_total=r['precincts_total'],results_csv_source_clock=stcsv[0]['xmlreporttime'],source_clock_timezone='not printed; not inferred from HTTP headers',participation_source_id=f'participation-{year}',participation_voted=int(state['total_voted']),participation_registered=int(state['total_registered']),header_minus_participation_voted=r['reported_votes_literal']-int(state['total_voted']),header_minus_participation_registered=r['registered_votes_literal']-int(state['total_registered']),source_disagreement='Different original publication controls; cause/revision chronology not established. No rescaling or forced denominator merge.',registered_definition='Registered/Voted totals from election-labelled report; active/inactive and exact voter-roll as-of date not printed in this source. Party-registration groups are not candidate votes.',blank_ballots=None,undervotes=None,overvotes=None,generic_writeins=None,unavailable_fields='These required historic report HTML/CSV and named write-in PDF products do not supply these quantities; report-header minus valid votes is not assigned to one category.'))
  edp={x['geo_key'] for x in hier if x['year']==year};edr={x['geo_key'] for x in base if int(x['year'])==year and x['view']=='byelectiondist'}
  cov=dict(year=year,report_ed_count=len(edr),participation_ed_count=len(edp),report_only=sorted(edr-edp),participation_only=sorted(edp-edr),scope='Different source inventories retained; matching names establish source identity evidence only, not equal geometry/vintage/current boundary.')
  for office in SPECS[year][2]:
   ed={x['geo_key'] for x in base if int(x['year'])==year and x['view']=='byelectiondist' and x['office_key']==office};cov[office+'_ed_count']=len(ed);cov[office+'_report_missing']=sorted(edr-ed)
  coverage.append(cov)
 writejson(P/'source/control-disagreements.json',out);writejson(P/'source/native-coverage-gaps.json',coverage)
 # Complete county source-scoped Registered/Voted controls, no invented ballot-method labels.
 writecsv(P/'county-participation-controls.csv',[x for x in participation if x['scope'] in ['county','statewide']])
 # Independent exact original link evidence; preserve real href and enclosing anchor position.
 ledgers=json.loads((P/'source/shared-sources.json').read_text())+json.loads((P/'source/current-acquisition.json').read_text())+json.loads((P/'source/additional-acquisition.json').read_text());links=[]
 for sid in ['sos-observed-general-archive','state-results']:
  t=raw(sid).decode('utf-8-sig')
  for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',t,re.S):
   if any(x in m[1] for x in ['GE2024','GE2022','GE2020','Write','candidatelist','regtotals','election_archive','PR2026']):links.append(dict(parent_source_id=sid,href=m[1],anchor=clean(m[2]),source_char_start=m.start(),source_char_end=m.end()))
 writejson(P/'source/discovery-chains.json',links)
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
