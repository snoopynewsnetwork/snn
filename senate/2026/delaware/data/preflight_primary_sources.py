#!/usr/bin/env python3
"""Original report HTML positions and named candidate controls; no geography approval."""
from pathlib import Path
import collections,csv,gzip,hashlib,html,io,json,re
D=Path(__file__).resolve().parent;N=D/'news'
def main():
 mf={a['id']:a for a in json.loads((N/'manifest.json').read_text())}
 def raw(sid):
  a=mf[sid];z=(N/a['asset']).read_bytes();b=gzip.decompress(z);assert hashlib.sha256(z).hexdigest()==a['stored_sha256'] and hashlib.sha256(b).hexdigest()==a['raw_sha256'];return b
 t=raw('sos-2024-general-report').decode('utf-8-sig');state=list(csv.DictReader(io.StringIO(raw('sos-2024-csv').decode('utf-8-sig'))));results={}
 for label,office in [('PresidentandVicePresident','President and Vice President'),('USSenator','U.S. Senator')]:
  sums=collections.Counter();units={};positions=[]
  pattern=r'<h4 class="electiondistrict-title '+label+r' ([^"]+)">(.*?)</h4>\s*<table[^>]*>(.*?)</table>'
  for m in re.finditer(pattern,t,re.S):
   key=m[1];name=html.unescape(re.sub('<[^>]+>','',m[2])).strip();assert key not in units;rr=[]
   for row in re.findall(r'<tr>(.*?)</tr>',m[3],re.S):
    fields={k:html.unescape(re.sub('<[^>]+>','',v)).strip() for k,v in re.findall(r'<td data-label="([^"]+)">(.*?)</td>',row,re.S)}
    if not fields:continue
    vals={k:int(fields[k].replace(',','')) for k in ['Machine Votes','Absentee Votes','Early Voting Votes','Total Votes']};assert vals['Machine Votes']+vals['Absentee Votes']+vals['Early Voting Votes']==vals['Total Votes'];sums[fields['Candidate']]+=vals['Total Votes'];rr.append({'raw_fields':fields,'numeric_fields':vals})
   units[key]={'name':name,'source_char_position':m.start(),'rows':rr};positions.append(m.start())
  controls={r['candidatename']:int(r['totalvotessum']) for r in state if r['office']==office};assert dict(sums)==controls,(label,sums,controls)
  assert len(units) in [530,533],(label,len(units))
  results[label]={'source_units':len(units),'candidate_rows':sum(len(u['rows']) for u in units.values()),'state_candidate_controls':controls,'named_candidate_total':sum(controls.values()),'source_units_by_literal_key':units}
 missing=sorted(set(results['PresidentandVicePresident']['source_units_by_literal_key'])-set(results['USSenator']['source_units_by_literal_key']));assert missing==['ElectionDistrict0228','ElectionDistrict3117','ElectionDistrict4117'];assert all(all(r['numeric_fields']['Total Votes']==0 for r in results['PresidentandVicePresident']['source_units_by_literal_key'][k]['rows']) for k in missing)
 out={'president_only_keys':missing,'status':'named_candidate_native_sums_pass_priority_unaccepted','sources':{k:mf[k] for k in ['sos-2024-general-report','sos-2024-csv','sos-2024-valid-writeins']},'headline_reporting_literal':re.findall(r'\d+ of \d+ Precincts Reporting',t),'tables':results,'scope':['President has533ED tables;Senate has530. Headline533/533 does not establish every contest has533 rows; retain absent Senate keys without fabrication.','County/RD/ED/Wilmington views overlap; do not sum views.','Separate official write-in PDF contains county/method totals, not ED allocation; no generic or missing count allocation.','President2024 is not Senate2024;2026ClassII uses2020Coons and2024BluntRochesterotherClassI.','Source native labels, FIPS and current boundaries are separate; no acceptedpriority/currentcrosswalk/livecadence.']};(D/'coordinator-primary-preflight.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:{a:b for a,b in v.items() if a!='source_units_by_literal_key'} for k,v in results.items()}))
if __name__=='__main__':main()
