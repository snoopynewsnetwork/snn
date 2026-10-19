#!/usr/bin/env python3
"""Bounded reciprocal proof against immutable captured peer bodies and pre-peer frozen turnout files."""
from pathlib import Path
import json,csv,io,gzip,hashlib,tarfile,collections,re,zipfile,xml.etree.ElementTree as ET,datetime
O=Path(__file__).resolve().parent;ST=O.parents[1];H=O/'history/sealed-v1';C=O/'peer-comparison/stable-v1';OUT=O/'peer-comparison/proof-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def obj(b):return json.loads(b)
def lines(b):return [json.loads(x)for x in gzip.decompress(b).splitlines()]
def csvs(b,compressed=False):return list(csv.DictReader(io.StringIO((gzip.decompress(b)if compressed else b).decode())))
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def gzcsv(p,head,rows):
 s=io.StringIO();w=csv.DictWriter(s,fieldnames=head);w.writeheader();w.writerows(rows);b=gzip.compress(s.getvalue().encode(),mtime=0);assert len(b)<40000000;p.write_bytes(b)
def main():
 OUT.mkdir(parents=True,exist_ok=True);snap=obj((H/'snapshot-index.json').read_bytes());archive=(H/snap['archive']).read_bytes();assert sha(archive)==snap['archive_sha256'];tar=tarfile.open(fileobj=io.BytesIO(gzip.decompress(archive)),mode='r');frozen={}
 for r in snap['files']:
  b=(ST/r['reference_path']).read_bytes()if r['storage']=='immutable_original_hash_reference'else tar.extractfile(r['archive_member']).read();assert sha(b)==r['sha256']and len(b)==r['bytes'];frozen[r['path']]=b
 assert len(frozen)==90
 def own(name):return frozen['data/turnout/'+name]
 cap=obj((C/'capture-index.json').read_bytes());peer={}
 for r in cap['files']:
  b=(ST/r['peer_path']).read_bytes()if r['storage']=='original_hash_reference'else(O/r['captured_path']).read_bytes();assert sha(b)==r['sha256']and len(b)==r['bytes'];peer[r['peer_path']]=b
 def pb(name):return peer['data/baselines/'+name]
 oldrows=lines(own('extracts/historical-source-rows.jsonl.gz'));newrows=lines(pb('extracts/original-csv-records.jsonl.gz'));assert len(oldrows)==len(newrows)==9831
 old={(r['source_id'],r['source_record']):r for r in oldrows};new={(r['source_id'],r['record_ordinal']):r for r in newrows};assert len(old)==len(new)==9831 and old.keys()==new.keys()
 cat=obj(own('extracts/candidate-universes.json'));props=obj(pb('source/historical-page-props.json'));assert {y:c['page_properties']for y,c in cat.items()}==props
 ownpins={r['id']:r for r in obj(own('source/shared-source-pins.json'))};peerpins=obj(pb('source/reused-originals.json'));sourcepairs=[]
 for pp in peerpins:
  op=ownpins[pp['id']];assert pp['raw_sha256']==op['raw_sha256']and pp['stored_sha256']==op['stored_sha256']and pp['bytes']==op['bytes']
  shared=(ST/'data/news'/op['asset']).read_bytes();assert sha(shared)==op['stored_sha256']and sha(gzip.decompress(shared))==op['raw_sha256']
  for field in ['url','final_url','retrieved_at_utc','status','headers']:assert pp[field]==op[field]
  sourcepairs.append(dict(source_id=pp['id'],raw_sha256=pp['raw_sha256'],stored_sha256=pp['stored_sha256'],raw_bytes=pp['bytes'],peer_reference=pp['path'],own_reference=op['reference_path']))
 assert len(sourcepairs)==7
 numeric=[];objects=collections.defaultdict(list);representations=[];native_cells=0
 for pos,p in new.items():
  q=old[pos];y=str(p['year']);head=cat[y]['header'];parties=cat[y]['party_header'];assert p['header_fields']==head and p['party_fields']==parties
  assert p['raw_fields']==q['raw_fields']and p['contest_id']==q['contest_id']and p['level_literal']==q['level_literal'];raw=p['raw_fields'];n=len(head)-4
  if p['level_literal']=='Precinct':assert p['key']==q['key']and p['county_literal']==q['county_literal']and p['native_id_literal']==q['native_id_literal']
  else:representations.append(dict(source_id=pos[0],record=pos[1],level=p['level_literal'],peer_key=p['key'],own_key=q['key'],peer_county=p['county_literal'],own_county=q['county_literal'],peer_native=p['native_id_literal'],own_native=q['native_id_literal'],mapping_basis='same source ID/1-based CSV record, not names or inferred crosswalk'))
  cc={c['displayName']:c for c in props[y]['contest']['candidates']};assert len(cc)==len(head)-2
  assert sum(map(int,raw[2:-2]))==int(raw[-2])==int(raw[-1])==q['candidate_votes'];assert q['candidate_values']==list(map(int,raw[2:-2]))
  for j in range(2,len(raw)):
   c=cc[head[j]];numeric.append(dict(source_id=pos[0],source_record=pos[1],source_column=j+1,year=y,level=p['level_literal'],own_key=q['key'],peer_key=p['key'],header_literal=head[j],party_literal=parties[j],literal_value=raw[j],value=int(raw[j]),role='candidate'if j<len(raw)-2 else 'pseudocandidate',candidate_in_contest_id=c['id'],candidate_id=c['candidate']['id'],isWriteIn=c['isWriteIn'],isMasked=c['isMasked'],pseudocandidate=c['candidate']['pseudocandidate']))
   if p['level_literal']=='Precinct'and j<len(raw)-2:native_cells+=1
  objects[p['year']].append(p)
 assert len(numeric)==121191 and native_cells==99514
 long=csvs(pb('extracts/all-candidate-votes.csv.gz'),True);lookup={(r['source_id'],int(r['source_record']),int(r['source_column'])):r for r in long};assert len(lookup)==len(long)==101529
 for r in numeric:
  if r['role']!='candidate':continue
  l=lookup[(r['source_id'],r['source_record'],r['source_column'])]
  for k,t in [('candidate_literal','header_literal'),('party_literal','party_literal'),('candidate_in_contest_id','candidate_in_contest_id'),('candidate_id','candidate_id')]:assert l[k]==r[t]
  assert int(l['votes'])==r['value']and l['isWriteIn_literal']==str(r['isWriteIn'])and l['isMasked_literal']==str(r['isMasked'])and l['pseudocandidate_literal']==''
 gzcsv(OUT/'source-position-map.csv.gz',list(numeric[0]),numeric)
 dump(OUT/'control-key-representations.json',representations)
 # Recompute peer's integer full orders directly from captured raw source counts, not its contract/calculator.
 oldranks=obj(own('extracts/native-rankings.json'));derived={};maps={}
 for y,rr in objects.items():
  native=[r for r in rr if r['level_literal']=='Precinct'];parents=[r for r in rr if r['level_literal']=='County'];state=[r for r in rr if r['level_literal']=='State'];assert len(parents)==64 and len(state)==1
  for p in parents:
   ch=[r for r in native if r['county_literal']==p['county_literal']];assert [sum(int(c['raw_fields'][j])for c in ch)for j in range(2,len(p['raw_fields']))]==list(map(int,p['raw_fields'][2:]))
  assert [sum(int(p['raw_fields'][j])for p in parents)for j in range(2,len(state[0]['raw_fields']))]==list(map(int,state[0]['raw_fields'][2:]))
  rows=sorted(native,key=lambda r:(-sum(map(int,r['raw_fields'][2:-2])),r['key']));total=sum(sum(map(int,r['raw_fields'][2:-2]))for r in rows);cum=0;order=[];cross=None
  for i,r in enumerate(rows,1):
   votes=sum(map(int,r['raw_fields'][2:-2]));previous=cum;cum+=votes;order.append(dict(rank=i,key=r['key'],county_literal=r['county_literal'],native_id_literal=r['native_id_literal'],candidate_votes=votes,cumulative_votes=cum,source_record=r['record_ordinal']))
   if cross is None and 5*cum>=4*total:cross=dict(count=i,key=r['key'],votes=votes,previous_count=i-1,previous_votes=previous,cumulative_votes=cum)
  prior=oldranks[str(y)];assert len(order)==prior['unit_count']and total==prior['total'];assert [r['key']for r in order]==[r['key']for r in prior['full_order']]
  for p,q in zip(order,prior['full_order']):assert all(p[f]==q[f]for f in ['rank','key','county_literal','native_id_literal','candidate_votes','cumulative_votes','source_record'])
  k=cross['count'];assert prior['minimum80_count']==k and prior['priority_votes']==cross['cumulative_votes']and prior['preceding_votes']==cross['previous_votes'];derived[str(y)]=dict(native_count=len(rows),county_count=64,denominator=total,top15=sum(r['candidate_votes']for r in order[:15]),crossing=cross,remainder_count=len(order)-k,remainder_votes=total-cross['cumulative_votes'],full_order=order)
  maps[str(y)]=[dict(county_literal=p['county_literal'],full_keys=[r['key']for r in order if r['county_literal']==p['county_literal']],priority_keys=[r['key']for r in order[:k]if r['county_literal']==p['county_literal']],remainder_keys=[r['key']for r in order[k:]if r['county_literal']==p['county_literal']],full_votes=sum(r['candidate_votes']for r in order if r['county_literal']==p['county_literal']),priority_votes=sum(r['candidate_votes']for r in order[:k]if r['county_literal']==p['county_literal']),remainder_votes=sum(r['candidate_votes']for r in order[k:]if r['county_literal']==p['county_literal']))for p in parents]
 dc=derived['2024'];pc=obj(pb('priority-contract.json'));po=csvs(pb('native-order.csv'));owncontract=obj(own('priority-set.json'));assert pc['ordered_keys']==[r['key']for r in dc['full_order']]
 assert pc['priority_keys']==[r['key']for r in dc['full_order'][:1992]]==owncontract['ordered_priority_keys'];assert pc['nonpriority_count']==1207 and pc['nonpriority_votes']==638512;assert pc['denominator']==3192745 and pc['top15']==39005 and pc['crossing']['cumulative']==2554233 and pc['crossing']['previous']==2553363 and pc['crossing']['votes']==870
 assert len(po)==3199
 for p,q in zip(po,dc['full_order']):
  for f in ['rank','candidate_votes','cumulative_votes','source_record']:assert int(p[f])==q[f]
  for f in ['key','county_literal','native_id_literal']:assert p[f]==q[f]
  assert (p['minimum80_member']=='True')==(q['rank']<=1992)
 oldmap={r['county']:r for r in csvs(own('county-native-coverage.csv'))};hier={r['county']:r for r in owncontract['county_native_hierarchy']}
 for m in maps['2024']:
  c=m['county_literal'];h=hier[c];o=oldmap[c];assert h['all_native_keys']==m['full_keys']and h['priority_native_keys']==m['priority_keys']
  assert int(o['native_records'])==len(m['full_keys'])and int(o['priority_native_records'])==len(m['priority_keys'])
  for f,pf in [('candidate_votes','full_votes'),('priority_candidate_votes','priority_votes'),('remainder_candidate_votes','remainder_votes')]:assert int(o[f])==m[pf]
 dump(OUT/'peer-raw-recomputed-rankings.json',derived);dump(OUT/'all-county-full-priority-remainder-maps.json',maps)
 # Source-scoped native null/method/admin fields and every candidate vector, all3years.
 nb=csvs(pb('native-baselines.csv.gz'),True);assert len(nb)==9636;native_by={r['key']:r for r in oldrows if r['level_literal']=='Precinct'};assert len(native_by)==len(nb)
 for r in nb:
  q=native_by[r['key']];header=cat[str(q['year'])]['header'];assert json.loads(r['candidate_vector_json'])==dict(zip(header[2:-2],q['candidate_values']))
  assert int(r['candidate_votes'])==q['candidate_votes']and int(r['source_record'])==q['source_record']
  for f in ['administrative_ballots','registered_voters','active_voters','inactive_voters','undervotes','overvotes','blank_votes','method']:assert r[f]==''
  assert q['method']is None and q['blank']is None and q['undervote']is None and q['overvote']is None and q['administrative_ballots']is None and q['registration']is None
  assert r['method_status']=='not supplied; source hasVoteChannels=False'
  assert int(r['source_Total_Votes_Cast'])==q['source_TOTAL_VOTES']and int(r['source_Total_Ballots_Cast'])==q['source_TOTAL_BALLOTS']
  assert r['A_name']==header[2]and r['B_name']==header[3]and int(r['A'])==q['candidate_values'][0]and int(r['B'])==q['candidate_values'][1]and int(r['other'])==sum(q['candidate_values'][2:])
 # All192county administrative fields/positions and source candidate vectors.
 cb=csvs(peer['data/county-baselines.csv']);assert len(cb)==192;admin=obj(own('extracts/county-administrative-controls.json'));county_position=[]
 for r in cb:
  y=r['year'];c=r['county_literal'];q=admin[y][c];assert int(r['administrative_ballots'])==q['ballots']and int(r['registered_voters'])==q['registered']and r['control_source']==q['source']
  expected=f"PDFpage{q['page']}:line{q['line']}"if 'page'in q else'HTMLtable-row'+str(q['table_row']);assert r['control_position']==expected
  src=old[(r['source_id'],int(r['source_record']))];assert json.loads(r['candidate_vector_json'])==dict(zip(cat[y]['header'][2:-2],src['candidate_values']));assert int(r['ballot_minus_candidate_gap'])==q['ballots']-src['candidate_votes']
  for f in ['blank_votes','undervotes','overvotes']:assert r[f]==''
  county_position.append(dict(year=y,county=c,source=q['source'],source_position=expected,ballots=q['ballots'],registered=q['registered']))
 dump(OUT/'county-administrative-position-map.json',county_position)
 # All3183sparse native stats against both representations AND actual original XML, including unvalued cells.
 os=lines(own('extracts/2024-native-statistics.jsonl.gz'));ps=lines(pb('extracts/turnout-original-cells.jsonl.gz'));assert len(os)==len(ps)==3183;ob={r['source_row']:r for r in os};pmap={r['source_row']:r for r in ps};assert ob.keys()==pmap.keys()
 z=zipfile.ZipFile(io.BytesIO(gzip.decompress((ST/'data/news'/ownpins['sos-2024-native-turnout']['asset']).read_bytes())));ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};ss=[''.join(x.itertext())for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)];xmlrows={};tail=0;empty=[];cellmap=[];ann=[];other=[]
 for _,row in ET.iterparse(z.open('xl/worksheets/sheet1.xml'),events=['end']):
  if row.tag!='{'+ns['s']+'}row':continue
  rowno=int(row.attrib['r']);cells={}
  for cell in row:
   v=cell.find('s:v',ns);v=v.text if v is not None else None;f=cell.find('s:f',ns);col=re.sub(r'\d','',cell.attrib['r']);cells[col]=dict(attributes=dict(cell.attrib),raw_v=v,text=ss[int(v)]if cell.get('t')=='s'and v is not None else v,formula=f.text if f is not None else None)
  row.clear()
  if rowno in ob:xmlrows[rowno]=cells
  elif set(k for k,c in cells.items()if c['text']is not None)=={'G'}and cells['G']['text']=='#VALUE!':tail+=1
  elif cells:other.append(dict(source_row=rowno,cells=cells))
 assert tail==1043548 and len(xmlrows)==3183
 for rowno,pcells in xmlrows.items():
  p=pmap[rowno];o=ob[rowno];assert p['raw_cells']==pcells;assert p['county_literal']==o['county_literal']and p['native_id_literal']==o['native_id_literal']and p['comparison_county_alias']==o['comparison_county']
  for col,c in pcells.items():
   address=c['attributes']['r'];oc=o['cells'].get(address)
   if c['raw_v']is None:
    assert oc is None;empty.append(dict(source_row=rowno,column=col,address=address,original_cell=c,own_representation='no non-null-v entry in sparse valued-cell derivative; complete original bytes retained',peer_representation='explicit raw_cells entry with raw_v/text null'))
   else:assert oc['attributes']==c['attributes']and oc['value']==c['raw_v']and oc['decoded']==c['text']and oc['formula']==c['formula']
   cellmap.append(dict(source_row=rowno,address=address,peer_column=col,own_address=address,raw_type=c['attributes'].get('t'),raw_v=c['raw_v'],text=c['text'],formula=c['formula'],own_valued_entry=oc is not None))
  for col,f in [('C','active'),('D','inactive'),('E','total'),('F','ballots')]:
   assert p['plain_numeric'][col]==o[f]and p['annotated_inclusive'][col]==o['published_'+f]
   if f in o['annotated_counts']:
    a=o['annotated_counts'][f];c=pcells[col];assert a['literal']==c['text']and a['raw_v']==c['raw_v']and a['source_type']=='s';ann.append(dict(source_row=rowno,address=c['attributes']['r'],raw_type='s',raw_v=c['raw_v'],shared_string_text=c['text'],plain=o[f],inclusive=o['published_'+f]))
 lanes=obj(pb('extracts/turnout-lanes.json'));assert lanes['explanatory']==other
 oldtail=obj(own('extracts/2024-workbook-footnotes-tail.json'));assert sum(oldtail['cached_error_only_tail'].values())==sum(lanes['tail_counts'].values())==tail
 for r in oldtail['other_rows']:
  p=next(x for x in other if x['source_row']==r['source_row'])
  for addr,c in r['cells'].items():
   q=p['cells'][re.sub(r'\d','',addr)];assert c['attributes']==q['attributes']and c['value']==q['raw_v']and c['decoded']==q['text']and c['formula']==q['formula']
 assert len(ann)==8
 for col,f in [('C','active'),('D','inactive'),('E','total'),('F','ballots')]:
  assert lanes['plain_numeric_known'][col]==sum(r[f]for r in os if r[f]is not None)
  assert lanes['annotated_inclusive_known'][col]==sum(r['published_'+f]for r in os if r['published_'+f]is not None)
  assert lanes['remaining_unprinted_fields'].get(col,0)==sum(r['published_'+f]is None for r in os)
 statkeys={(r['comparison_county_alias'],r['native_id_literal'])for r in ps};allkeys={(r['county_literal'],r['native_id_literal'])for r in newrows if r['year']==2024 and r['level_literal']=='Precinct'};extras=allkeys-statkeys;assert statkeys<=allkeys and len(extras)==16
 oldextra={(r['county'],r['native_literal'])for r in owncontract['csv_only_statistics_unavailable']};assert oldextra==extras
 for c,p in extras:assert next(r for r in dc['full_order']if r['county_literal']==c and r['native_id_literal']==p)['candidate_votes']==0
 dump(OUT/'OOXML-cell-position-map.json.gz.metadata.json',dict(rows=3183,explicit_source_cells=len(cellmap),representation_only_unvalued_cells=empty,annotated_cells=ann,tail_G_only_cached_VALUE_rows=tail,remaining_unprinted_inactive_fields=lanes['remaining_unprinted_fields'],CSV_only_statistics_unavailable=[dict(county=c,native=p)for c,p in sorted(extras)]))
 raw=b''.join((json.dumps(x,separators=(',',':'))+'\n').encode()for x in cellmap);(OUT/'OOXML-cell-position-map.jsonl.gz').write_bytes(gzip.compress(raw,mtime=0))
 # Independent primary control source positions vs captured peer replay evidence, separately from CSV agreement.
 proof=lines(own('extracts/independent-candidate-controls.jsonl.gz'));pp24=obj(pb('coordinator-public-native-export-preflight.json'))['contests'][0]['independent_2024_abstract_candidate_comparisons'];p24={(r['county'],r['CSV_header']):r for r in pp24};hc=obj(pb('coordinator-historical-controls-preflight.json'));p20={(r['county_literal'],r['candidate_literal']):r for r in hc['signed2020']['candidate_rows']};p22={r['county_literal']:r for r in hc['HTML2022']['sos-2022-senate-abstract']['records']};h22=hc['HTML2022']['sos-2022-senate-abstract']['header_literal'];comparisons=collections.Counter()
 for r in proof:
  y=r['year'];c=r['county'];name=r['header']
  if y==2024:p=p24[(c,name)];assert p['votes']==r['votes']and p['source_PDFpage']==r['page']and p['source_line']==r['line']
  elif y==2020:p=p20[(c.upper(),name)];assert p['votes']==r['votes']and p['page']==r['page']and p['line']==r['line']and p['raw_line']==r['raw_line']
  else:
   p=p22[c];j=next(i for i,s in enumerate(h22)if s.split(' (',1)[0]==name);assert int(p['raw_cells'][j].replace(',',''))==r['votes']and p['source_table_row']==r['table_row']
  comparisons[y]+=1
 assert dict(comparisons)=={2024:896,2022:576,2020:512}
 dump(OUT/'source-identity-clock-scope-map.json',dict(shared_exact_primary_objects=sourcepairs,own_shared_source_inventory_count=len(ownpins),peer_extraction_reused_inventory_count=len(peerpins),unmatched_own_inventory_ids=sorted(set(ownpins)-{r['id']for r in peerpins}),qualification='7same sourceIDs/raw/stored hashes/UTC/status/headers, not equality of33source inventories; fresh current source responses/candidate rosters are distinct vintages and outside reciprocal numerical scope. Full SSR page props and verification/source-file clocks compare exactly by source object.',null_representation='own JSONnull vs peer CSVempty for unavailable admin/method/blank/under/over; actual source fields stay separate',control_key_representation_count=len(representations)))
 result=dict(status='pass_bounded_reciprocal_original_source_QA',peer_id=cap['peer_id'],capture='peer-comparison/stable-v1/capture-index.json',frozen_own='history/sealed-v1/snapshot-index.json',scope='Equality applies only to exact captured stable source extraction/contract/order bodies; no claim about later peer final calculator, scenario, report or revised files',checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozen_files=90,captured_or_referenced_peer_files=len(cap['files']),checks=dict(all_original_source_records=9831,native_records_by_year={y:r['native_count']for y,r in derived.items()},all_selected_numeric_positions=121191,native_candidate_cells=99514,all_candidate_long_positions=101529,full_SSR_page_property_objects=3,full_SSR_candidate_and_pseudocandidate_objects=sum(len(p['contest']['candidates'])for p in props.values()),full_year_orders=3,all64_parent_full_priority_remainder_maps_each_year=True,source_control_key_representation_differences=len(representations),all_native_null_method_and_pseudoballot_contexts=len(nb),county_admin_positions=192,independent_primary_controls=dict(comparisons),statistics_records=3183,statistics_explicit_source_cells=len(cellmap),own_unvalued_cell_representation_omissions=len(empty),annotated_Montezuma_cells=8,unprinted_inactive_cells=18,cached_tail_rows=tail,CSV_only_contexts=16,shared_exact_primary_sources=7),candidate_priority={k:v for k,v in dc.items()if k!='full_order'},differences=[dict(kind='control-key/null representation',detail='195State/County keys differ; native keys exactly identical. Matched by source ID and source record only; no source object deduplication or geography substitution.'),dict(kind='sparseOOXML representation',detail=f'{len(empty)} actual unvalued worksheet cells are explicit in peer raw_cells and absent from own valued-cell derivative; exact original attributes/nulls now retained in supplemental map and both unchanged original sources remain hashed.'),dict(kind='source inventory scope',detail='Turnout33SOS source pins versus peer7reused extraction pins; all7shared source objects agree exactly. Additional current acquisitions/rosters have distinct scope/vintage, not asserted equal.')],formal_coordinator_acceptance=False,current_geography_approved=False,report_statement='Independent reciprocal QA passed against byte-exact captured stable extraction from Colorado baseline peer `451afcad-e3df-4c1d-b304-f195592df4fe`. All historical source counts, candidate/party/flag objects, source positions, native orders and the1,992/1,207 split agree within the recorded scope. Control-key/null and sparse-cell representation differences remain explicit. Later peer final calculations/reports are outside this equality claim; formal coordinator acceptance and current geography approval remain pending.')
 dump(O/'peer-agreement.json',result);dump(OUT/'proof-result.json',result)
 print(json.dumps({k:v for k,v in result.items()if k not in ['report_statement','differences']},indent=2))
if __name__=='__main__':main()
