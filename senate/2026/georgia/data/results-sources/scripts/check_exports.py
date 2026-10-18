from common import *
import collections,re
state=js(ROOT/'extracts/state-controls.json');result=[]
positions=[json.loads(s) for s in gzip.decompress((ROOT/'extracts/source-positions.jsonl.gz').read_bytes()).decode().splitlines()]
for fp in sorted((ROOT/'extracts').glob('observed-export*.xlsx.json.gz')):
 id=fp.name.removesuffix('.xlsx.json.gz');d=json.loads(gzip.decompress(fp.read_bytes()));ek=next((e for e in state if e in id),'2024NovGen');office=state[ek]['contest_name'][0]['text'];scope='fulton' if 'fulton' in id else 'state'
 rec={'source_id':id,'election_key':ek,'office':office,'scope':scope,'workbook_xml':d['workbook_xml'],'sheets':[]}
 for si,s in enumerate(d['sheets']):
  rows=collections.defaultdict(dict)
  for c in s['cells']:rows[int(re.search(r'\d+',c['address']).group())][re.match('[A-Z]+',c['address']).group()]=c['value']
  sel=[{'row':i,'cells':v} for i,v in rows.items() if v.get('A' if si<2 else 'B')==office]
  assert sel
  labels=collections.Counter(x['cells'].get('C' if si<2 else 'D') for x in sel);countcol='F' if si==0 else 'G'
  rec['sheets'].append({'member':s['member'],'header':rows[1],'selected_rows':sel,'labels':dict(labels),'blank_selected_values':sum(x['cells'].get(countcol) in [None,''] for x in sel),'non_numeric_selected_values':[(x['row'],x['cells'].get(countcol)) for x in sel if x['cells'].get(countcol) not in [None,''] and not str(x['cells'][countcol]).isdigit()]})
 # All selected state totals and county-level candidate allocations checked independently against JSON, by exact display name.
 first=rec['sheets'][0]['selected_rows'];xcounts={x['cells']['C']:int(x['cells']['F']) for x in first if x['cells']['C'] not in ['Total Votes','Ballots Cast']}
 expected=state[ek]['candidates'] if scope=='state' else {x['name'][0]['text']:x['votes'] for x in positions if x['level']=='county' and x['election_key']==ek and x['county_fips']=='13121' and x['kind']=='TOTAL'}
 assert xcounts==expected
 rec['summary_matches_app']=True
 if scope=='state':
  countyrows=rec['sheets'][2]['selected_rows'];names={x['cells']['A'] for x in countyrows};assert len(names)==159
  agg=collections.Counter()
  for x in countyrows:
   v=x['cells']
   if v['D'] in expected:agg[v['D']]+=int(v['G'])
  assert dict(agg)==expected
  rec['county_count']=len(names);rec['all_county_candidates_match_state']=True
  rec['worksheet_geography']='159 actual county names, even where sheet is named Precinct Results'
 else:
  rec['native_labels']=len({x['cells']['A'] for x in rec['sheets'][2]['selected_rows']});assert rec['native_labels']==466
  rec['native_candidate_blank_count']=sum(x['cells']['D'] in expected and x['cells'].get('G') in [None,''] for x in rec['sheets'][2]['selected_rows'])
 rec['writein_allocation']='No qualified-write-in names, generic Write-In or Unresolved Write-In rows exist in the selected2024 presidential worksheet scopes;858 remains unallocated' if ek=='2024NovGen' else 'Separate historical Senate stage'
 result.append(rec)
save(ROOT/'extracts/export-controls.json',result)
print([(r['source_id'],[s['labels'] for s in r['sheets']][:1],r.get('native_candidate_blank_count')) for r in result])
