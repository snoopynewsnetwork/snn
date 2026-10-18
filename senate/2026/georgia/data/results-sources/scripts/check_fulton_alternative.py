from common import *
import collections,re,io,zipfile
source='data/turnout/source/2024NovGen--fulton-county-ga.body.gz';d=json.loads(gzip.decompress((GA/source).read_bytes()));x=json.loads(gzip.decompress((ROOT/'extracts/observed-export-fulton2024-0-0.xlsx.json.gz').read_bytes()));rows=collections.defaultdict(dict)
for c in x['sheets'][2]['cells']:rows[int(re.search(r'\d+',c['address']).group())][re.match('[A-Z]+',c['address']).group()]=c['value']
excel={(v['A'],v['D']):(i,int(v['G'])) for i,v in rows.items() if v.get('B')=='President of the US' and v.get('E') is not None}
assert len(excel)==466*4
names=[u['precinct']['name'][0]['text'] for u in d['ballotItemWithBreakdown']['breakdownResults']];assert len(set(names))==466
nulls=[];diff=[];known=0
for j,u in enumerate(d['ballotItemWithBreakdown']['breakdownResults']):
 name=u['precinct']['name'][0]['text']
 for i,o in enumerate(u['ballotOptions']):
  label=o['name'][0]['text'];row,v=excel[(name,label)]
  if o['voteCount'] is None:nulls.append(dict(native_GUID=u['precinct']['id'],native_label=name,candidate_id=o['id'],candidate_name=label,app_pointer=f'/ballotItemWithBreakdown/breakdownResults/{j}/ballotOptions/{i}',app_value=None,xlsx_row=row,xlsx_value=v))
  else:
   known+=1
   if o['voteCount']!=v:diff.append((name,label,o['voteCount'],v))
assert len(nulls)==40 and not diff and sum(v for row,v in excel.values())==535238 and sum(z['xlsx_value'] for z in nulls)==18
r=js(ROOT/'raw/observed-export-fulton2024-0-0.http.json');z=zipfile.ZipFile(io.BytesIO(entity(r)));totals=collections.Counter()
for n in nulls:totals[n['candidate_name']]+=n['xlsx_value']
save(ROOT/'extracts/fulton-alternative-native-nulls.json',{'source_scope':'Fulton2024 XLSX alternative numeric cells, not replacement for accepted appJSON nulls','app_source':source,'xlsx_source':'observed-export-fulton2024-0-0','xlsx_last_modified_transport':r['headers'].get('last-modified'),'xlsx_core_metadata':z.read('docProps/core.xml').decode() if 'docProps/core.xml' in z.namelist() else None,'app_clocks':{k:d['election'][k] for k in ['asOf','lastUpdated']},'matched_by':'466 unique exact precinct labels+English option names within same2024 county; no current/geographic crosswalk','null_cells':nulls,'alternative_sum':18,'alternative_candidate_sums':dict(totals),'known_cell_count':known,'known_cell_differences':diff,'no_frozen_vector_mutation':True})
print('Fulton alternative40 cells/18 votes; known',known,'matched; source scopes remain separate')
