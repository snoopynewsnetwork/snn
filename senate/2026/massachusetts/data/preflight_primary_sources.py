#!/usr/bin/env python3
"""Municipal/ward/precinct original CSV controls; hierarchy remains disjoint."""
import collections,csv,gzip,hashlib,io,json
from pathlib import Path
D=Path(__file__).resolve().parent;N=D/'news'
def main():
 m={a['id']:a for a in json.loads((N/'manifest.json').read_text())}
 def read(sid):
  a=m[sid];z=(N/a['asset']).read_bytes();b=gzip.decompress(z);assert hashlib.sha256(z).hexdigest()==a['stored_sha256'] and hashlib.sha256(b).hexdigest()==a['raw_sha256'];return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 municipal=read('sos-2024-senate-municipal-csv');native=read('sos-2024-senate-precinct-csv');assert municipal[0][3:]==native[0][3:];M=municipal[2:-1];U=native[2:-1];assert len(M)==351 and len(U)==2394;assert municipal[-1]==native[-1];controls=[int(x.replace(',','')) for x in municipal[-1][3:]];by={r[0]:[int(v.replace(',','')) for v in r[3:]] for r in M};assert len(by)==351;agg=collections.defaultdict(collections.Counter);keys=set()
 for ordinal,r in enumerate(U,2):
  k=tuple(r[:3]);assert k not in keys;keys.add(k);v=[int(x.replace(',','')) for x in r[3:]];assert sum(v[:4])==v[4]
  for i,x in enumerate(v):agg[r[0]][i]+=x
 assert set(agg)==set(by);assert all([agg[k][i] for i in range(5)]==by[k] for k in by);assert [sum(r[i] for r in by.values()) for i in range(5)]==controls
 out={'status':'source_municipal_native_controls_pass_no_priority_accepted','source_ids':['sos-pd43-root','sos-2024-senate-view','sos-2024-senate-municipal-csv','sos-2024-senate-precinct-csv'],'sources':{k:m[k] for k in ['sos-2024-senate-municipal-csv','sos-2024-senate-precinct-csv']},'municipal_literal_header_rows':municipal[:2],'native_literal_header_rows':native[:2],'municipalities':351,'source_native_contexts':2394,'state_control_columns':municipal[0][3:],'state_controls':controls,'reported_candidate_plus_All_Others':sum(controls[:3]),'Blanks':controls[3],'Total_Votes_Cast':controls[4],'municipal_native_control_comparisons':351*5,'municipal_source_rows':municipal,'native_source_rows':native,'scope':['City/Town parent and ward/precinct detail are overlapping observations; never add them.','SourceWard dash and Pct number/letter remain literal; no physical precinct or current compatibility inferred.','AllOthers separate from named candidates, not blank, and not allocated to individual valid write-ins.','No2026forecast, exact80priority, livefeed/cadence or approved currentgeometry from thispreflight.']};(D/'coordinator-primary-preflight.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['sources','municipal_source_rows','native_source_rows']},indent=2))
if __name__=='__main__':main()
