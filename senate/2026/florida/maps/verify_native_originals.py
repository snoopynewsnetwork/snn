"""Offline repetition of coordinator original-review algorithm, adapted only to owned output paths. No raw original copies or worker imports."""
import collections,gzip,hashlib,io,json,pathlib,urllib.parse,zipfile
OUT=pathlib.Path(__file__).resolve().parent
ROOT=OUT.parent/'data'
NEWS=ROOT/'news'
TURNOUT=ROOT/'turnout'
sha=lambda b:hashlib.sha256(b).hexdigest()
def stream_json(path):
 with gzip.open(path,'rt') as f:
  for line in f:yield json.loads(line)
def main():
 manifest={r['id']:r for r in json.loads((NEWS/'manifest.json').read_text())}
 sources=[('2024','dos-2024-precinct-official-storage-alias',{'100000':'2024_president','120000':'2024_senate'}),('2022','dos-2022-precinct-official-storage-alias',{'120000':'2022_senate'}),('2020','dos-2020-precinct-zip',{'100000':'2020_president'})]
 native={};row_count=0;field_count=0;members_checked=0;pins=[];context_count=collections.Counter();raw_original_rows=0
 for year,source_id,codes in sources:
  source=manifest[source_id];stored=(NEWS/source['asset']).read_bytes();raw=gzip.decompress(stored)
  assert sha(stored)==source['stored_sha256'] and sha(raw)==source['raw_sha256']
  archive=zipfile.ZipFile(io.BytesIO(raw));assert archive.testzip() is None
  members={info.filename:archive.read(info) for info in archive.infolist()};members_checked+=len(members)
  for name,b in members.items():
   if name.lower().endswith('.txt'):raw_original_rows+=sum(bool(line.strip()) for line in b.splitlines())
  line_ordinals={}
  for name,body in members.items():
   if not name.lower().endswith('.txt'):continue
   offset=0;line_ordinals[name]={}
   for ordinal,line in enumerate(body.splitlines(keepends=True),1):
    line_ordinals[name][offset]=ordinal;offset+=len(line)
  extract=TURNOUT/'extracts'/f'native-source-rows-{year}.jsonl.gz'
  for row in stream_json(extract):
   assert row['source_id']==source_id
   b=members[row['source_member']]
   start=row['source_byte_offset'];end=start+row['source_line_bytes'];original=b[start:end]
   assert line_ordinals[row['source_member']][start]==row['source_row_1based']
   assert sha(original)==row['source_line_sha256']
   fields=original.decode(row['source_encoding']).rstrip('\r\n').split('\t')
   assert len(fields)==19 and fields==row['fields']
   assert fields[13] in codes and row['context']==codes[fields[13]]
   assert 'recount' not in row['source_member'].lower() and row['recount_overlap_excluded'] is False
   context=row['context'];key='/'.join([context,fields[0],fields[2],urllib.parse.quote(fields[5],safe=''),urllib.parse.quote(fields[6],safe='')])
   assert key==row['native_key']
   identity=(context,fields[0],fields[2],fields[5],fields[6]);n=native.setdefault(key,{'identity':identity,'source_id':source_id,'source_member':row['source_member'],'registration_observations':set(),'candidate_category_rows':[],'fields':fields})
   assert n['identity']==identity and n['source_member']==row['source_member']
   n['registration_observations'].add(tuple(fields[7:11]))
   n['candidate_category_rows'].append({'candidate_label':fields[14],'party':fields[15],'fvrs_id':fields[16],'doe_candidate_id':fields[17],'votes':int(fields[18]),'source_row_1based':row['source_row_1based']})
   row_count+=1;field_count+=19;context_count[context]+=1
  pins.append({'source_id':source_id,'ZIP_original_sha256':sha(raw),'ZIP_original_bytes':len(raw),'member_count':len(members),'selected_extract_path':str(extract.relative_to(ROOT)),'selected_extract_sha256':sha(extract.read_bytes())})
 worker_units=list(stream_json(TURNOUT/'extracts/native-units.jsonl.gz'))
 assert len(worker_units)==len(native)==23532
 for row in worker_units:
  n=native[row['native_key']];f=n['fields']
  for key,value in [('source_id',n['source_id']),('source_member',n['source_member']),('election_number',f[2]),('election_date',f[3]),('election_name',f[4]),('precinct_id',f[5]),('polling_location',f[6]),('contest_name',f[11]),('district',f[12]),('contest_code',f[13])]:assert row[key]==value
  assert {tuple(v) for v in row['registration_observations']}==n['registration_observations']
  assert row['candidate_category_rows']==n['candidate_category_rows']
 contract=json.loads((TURNOUT/'priority-set.json').read_text())
 assert len(contract['native_constituents'])==67
 represented=set()
 for group in contract['native_constituents']:
  assert len(group['units'])==group['constituent_count']
  for unit in group['units']:
   key=unit['native_key'];assert key in native and key not in represented;represented.add(key)
   for k in ['source_id','source_member']:assert unit[k]==native[key][k]
   fields=native[key]['fields']
   assert unit['election_number']==fields[2] and unit['precinct_id']==fields[5] and unit['polling_location']==fields[6] and unit['contest_code']==fields[13]
 primary_represented=len(represented)
 for group in contract['native_constituents']:
  for context,other in group['other_contexts'].items():
   assert len(other['units'])==other['constituent_count']
   for unit in other['units']:
    key=unit['native_key'];assert key in native and key not in represented
    represented.add(key);n=native[key];fields=n['fields']
    assert context==n['identity'][0]
    assert unit['source_id']==n['source_id'] and unit['source_member']==n['source_member']
    assert unit['election_number']==fields[2] and unit['election_date']==fields[3]
    assert unit['precinct_id']==fields[5] and unit['polling_location']==fields[6] and unit['contest_code']==fields[13]
    assert unit['precinct_id_available']==bool(fields[5].strip())
 assert represented==set(native)
 counts=collections.Counter(n['identity'][0] for n in native.values())
 assert dict(counts)=={'2024_president':5712,'2024_senate':5710,'2022_senate':6013,'2020_president':6097}
 assert primary_represented==5710 and len(represented)==23532 and row_count==211874 and field_count==4025606
 out={'status':'pass_original_selected_raw_fields_native_identities_and_vectors','original_ZIP_pins':pins,'ZIP_members_CRC_verified':members_checked,'whole_original_source_rows_preserved':raw_original_rows,'selected_source_positions':row_count,'original_field_comparisons':field_count,'all_native_contexts':len(native),'native_counts':dict(counts),'full_native_metadata_and_candidate_vectors':len(worker_units),'primary_contract_Senate_constituents_checked':primary_represented,'all_frozen_contract_constituents_checked':len(represented),'scope':'Complete original compiled native contexts, distinct from primary legal-valid named county vectors. No voting-method column, current geography or valid named-writein native allocation inferred.','contract_status':'Frozen identity objects verified; formal historical-dispatch authority is separate.','contract_bytes':(TURNOUT/'priority-set.json').stat().st_size,'contract_sha256':sha((TURNOUT/'priority-set.json').read_bytes())}
 (OUT/'native-original-validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
