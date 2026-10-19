#!/usr/bin/env python3
"""Original Idaho OOXML and ZIP control preflight; no dispatch approval."""
import collections,csv,gzip,hashlib,io,json,zipfile,xml.etree.ElementTree as E
from pathlib import Path
D=Path(__file__).resolve().parent;N=D/'news';NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 m={x['id']:x for x in json.loads((N/'manifest.json').read_text())}
 def raw(sid):
  a=m[sid];s=(N/a['asset']).read_bytes();b=gzip.decompress(s);assert sha(s)==a['stored_sha256'] and sha(b)==a['raw_sha256'];return b
 def rows(b):
  z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None;ss=[''.join(n.itertext()) for n in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)];out=[]
  for row in E.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('s:sheetData/s:row',NS):
   cells={}
   for c in row:
    v=c.find('s:v',NS);t=v.text if v is not None else None;k=''.join(a for a in c.attrib['r'] if a.isalpha());cells[k]=ss[int(t)] if c.get('t')=='s' and t is not None else t
   out.append(dict(source_row=int(row.attrib['r']),cells=cells))
  return out
 races=rows(raw('sos-2024-all-races-xlsx'));stats=rows(raw('sos-2024-turnout-xlsx'));pres=[r for r in races[1:] if r['cells'].get('D')=='United States President'];counts=collections.Counter();county=collections.defaultdict(collections.Counter);native=collections.defaultdict(list)
 for r in pres:
  a=r['cells'];v=int(a['G']);key=(a.get('E'),a['F']);counts[key]+=v;county[a['A']][key]+=v;native[(a['A'],a['B'])].append(r)
 stats_county=collections.defaultdict(list);footers={}
 for r in stats[1:]:
  a=r['cells']
  if a['B']=='Total':assert a['A'] not in footers;footers[a['A']]=r
  else:stats_county[a['A']].append(r)
 stats_controls={}
 for c,rr in stats_county.items():
  vals={k:sum(int(r['cells'][k]) for r in rr) for k in 'CDEF'};expected={k:int(footers[c]['cells'][k]) for k in 'CDEF'};assert vals==expected,(c,vals,expected);stats_controls[c]=vals
  assert all(int(r['cells']['C'])+int(r['cells']['D'])==int(r['cells']['E']) for r in rr)
 assert len(county)==len(stats_county)==len(footers)==44
 statkeys={(r['cells']['A'],r['cells']['B']) for rr in stats_county.values() for r in rr}
 noncandidate={key:v for key,v in counts.items() if any(x in key[1].lower() for x in ['overvote','undervote'])};candidate={key:v for key,v in counts.items() if key not in noncandidate}
 stats_lookup={(r['cells']['A'],r['cells']['B']):r for rr in stats_county.values() for r in rr}
 paired=[]
 for key,rr in sorted(native.items()):
  r=stats_lookup[key];votes=sum(int(x['cells']['G']) for x in rr);ballots=int(r['cells']['F'])
  paired.append({'literal_key':list(key),'stats_source_row':r['source_row'],'president_source_rows':[x['source_row'] for x in rr],'president_all_category_votes':votes,'stats_ballots':ballots,'ballot_minus_president_category':ballots-votes})
 stats_only_rows=[stats_lookup[k] for k in sorted(statkeys-set(native))]
 results={'status':'original_primary_preflight_priority_unaccepted','race_original_sha256':sha(raw('sos-2024-all-races-xlsx')),'stats_original_sha256':sha(raw('sos-2024-turnout-xlsx')),'race_raw_rows':len(races)-1,'stats_raw_rows':len(stats)-1,'all_counties':44,'president_source_rows':len(pres),'president_contexts':len(native),'president_candidate_categories':[{'raw_party':k[0],'literal_candidate':k[1],'votes':v} for k,v in candidate.items()],'president_non_candidate_categories':[{'raw_party':k[0],'literal_category':k[1],'votes':v} for k,v in noncandidate.items()],'candidate_total':sum(candidate.values()),'non_candidate_total':sum(noncandidate.values()),'all_president_category_total':sum(counts.values()),'stats_native_contexts':len(statkeys),'stats_county_footer_rows':44,'stats_disjoint_totals':{k:sum(v[k] for v in stats_controls.values()) for k in 'CDEF'},'stats_only_keys':[list(k) for k in sorted(statkeys-set(native))],'president_only_keys':[list(k) for k in sorted(set(native)-statkeys)],'full_president_rows':pres,'county_stats_controls':stats_controls,'scope':['BlankParty cells retain column positions and null type; never collapse sparse OOXML cells into positional arrays.','All44Total rows overlap native stats; not extra precincts or additional ballots.','PartyIndependent retained for named candidates; JoelSkousenConstitution distinct from RandallTerryIndependent.','Native county/precinct labels remain literal, no current/cross-year geographic approval.','HouseClerk2024 total917466 versus FECvalid905057; their12409difference must be examined against raw noncandidate over/under categories, not rescaled.']}
 z=zipfile.ZipFile(io.BytesIO(raw('sos-2022-general-canvass-zip')));assert z.testzip() is None;results['2022_original_zip_members']=[dict(name=i.filename,bytes=i.file_size,crc32=f'{i.CRC:08x}',sha256=sha(z.read(i))) for i in z.infolist()];results['2022_scope']='Actual county and precinct statewide XLSX plus legislative/judicial XLS/XLSX complementary files; worker must independently extract Senate/Governor controls and hierarchy.'
 results['paired_stats_president_contexts']=paired;results['stats_only_rows']=stats_only_rows
 results['paired_nonzero_residuals']=[r for r in paired if r['ballot_minus_president_category']]
 results['paired_scope_summary']={'literal_pairs':len(paired),'equal_all_category_totals':sum(r['ballot_minus_president_category']==0 for r in paired),'net_ballot_minus_category':sum(r['ballot_minus_president_category'] for r in paired),'stats_only_ballots':sum(int(r['cells']['F']) for r in stats_only_rows),'qualification':'Literal labels only, not approved electorate/method/physical equivalence. All seven nonzero residuals are BoundaryCounty; its absentee and geographic source scopes differ, no allocation or cause inferred.'}
 (D/'coordinator-primary-preflight.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:v for k,v in results.items() if k not in ['full_president_rows','county_stats_controls','2022_original_zip_members','paired_stats_president_contexts']},indent=2))
if __name__=='__main__':main()
