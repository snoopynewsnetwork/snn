"""Pin the independent second-worker Pike proof without changing prior witness."""
from pathlib import Path
import csv,gzip,hashlib,io,json

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
DEST=DATA/'coordinator-qa/pike-profile-peer-review'
ALIASES=dict(zip(['pres_Harris','pres_Oliver','pres_Stein','pres_Terry','pres_Trump',
                 'pres_Shiva','pres_Claudia','pres_Kennedy','pres_Sonski','sen_Pinkins','sen_Wicker'],
                ['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump',
                 'Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski','Ty Pinkins','Roger F. Wicker']))|{
 'registration':'registration_total','ballots_cast':'ballots_cast_total','blank_ballots':'ballots_blank',
 'printed_turnout':'voter_turnout_percent','pres_generic_write_in':'president_generic_write_in',
 'pres_total_votes_cast':'president_total_votes_cast','pres_contest_total':'president_contest_total',
 'sen_generic_write_in':'senate_generic_write_in','sen_total_votes_cast':'senate_total_votes_cast',
 'sen_contest_total':'senate_contest_total'}
EXPECTED={
 'pike-native-profile-readings.json':'7b5f5050aa00676a5cb016362d4554ee0540442884d2db084beaa4b9bcd0f266',
 'pike-native-profile-fields.csv':'5a57eec101659989704b24e2240b3e3334edd22520b2e4435845de2c49742e92',
 'pike-native-profile-peer-reconciliation.json':'2d3d985b33cf1482d2c093f72e095e78e21c593df27281bbb321b5d167cacec0'}

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}
def frozen(p):
 out=DEST/(p.name+'.gz')
 if not out.exists():
  raw=p.read_bytes();assert raw==p.read_bytes();out.write_bytes(gzip.compress(raw,mtime=0))
 return gzip.decompress(out.read_bytes()),pin(out)

def main():
 DEST.mkdir(exist_ok=True)
 values={};pins=[]
 for name,wanted in EXPECTED.items():
  raw,p=frozen(DATA/'baselines'/name);assert sha(raw)==wanted
  values[name]=raw;pins.append(p|{'original_sha256':sha(raw),'original_bytes':len(raw)})
 ledger=json.loads(values['pike-native-profile-readings.json'])
 proof=json.loads(values['pike-native-profile-peer-reconciliation.json'])
 rows=list(csv.DictReader(io.StringIO(values['pike-native-profile-fields.csv'].decode(),newline='')))
 prior=json.loads((DATA/'coordinator-pike-profile-review.json').read_bytes())
 assert len(rows)==525 and len(ledger['profiles'])==proof['source_views']==25
 assert proof['field_positions']==525 and proof['actual_profile_section_pages']==42
 assert proof['value_differences']==proof['label_differences']==[]
 assert proof['current_geography_approved'] is False and proof['source_hashes_pages_and_printed_codes_agree'] is True
 peer_stored=(ROOT/proof['peer_snapshot_path']).read_bytes()
 assert sha(peer_stored)==proof['peer_stored_sha256']
 peer_raw=gzip.decompress(peer_stored)
 assert sha(peer_raw)==proof['peer_original_sha256']
 old_peer=gzip.decompress((DATA/'coordinator-qa/pike-profile-review/native-profile-fields.csv.gz').read_bytes())
 assert peer_raw==old_peer
 peer_rows=[r for r in csv.DictReader(io.StringIO(peer_raw.decode(),newline='')) if r['source_id']==ledger['source_id']]
 a={(int(r['source_page']),r['source_field']):r for r in peer_rows}
 coordinator={(r['page'],r['field']):r['accepted_value'] for r in prior['field_comparisons']}
 seen=set();hashes={};windows=[]
 for row,window in zip(rows,proof['physical_reading_windows']):
  key=(int(row['source_page']),ALIASES[row['field']]);assert key not in seen;seen.add(key)
  peer=a[key];assert float(row['value'])==float(peer['value'])==coordinator[key]
  assert row['raw_sha256']==peer['source_raw_sha256']==ledger['raw_sha256']
  assert row['native_label_literal']==peer['label_literal']
  assert row['vendor_profile_code']==peer['printed_native_id']
  assert window['page']==row['source_page'] and window['field']==row['field']
  assert window['own_original_row_box_pixels']==json.loads(row['original_reading_box_pixels'])
  assert window['peer_source_position']==json.loads(peer['source_position'])
  assert window['own_render_size']==json.loads(row['render_size'])
  for field,digest in [('full_original_render_path','render_sha256'),('evidence_path','evidence_sha256')]:
   path=row[field];expected=row[digest]
   if path not in hashes:hashes[path]=pin(ROOT/path)
   assert hashes[path]['sha256']==expected
  windows.append(window)
 assert len(seen)==525
 for p,g in zip(ledger['profiles'],prior['profile_page_groups']):
  assert p['printed_profile_code']==g['printed_profile_code'] and p['source_pages']==g['source_pages']
  for f in p['fields']:
   assert f['value']==coordinator[f['source_page'],ALIASES[f['field']]]
 raw_extract=(ROOT/ledger['original_extract_path']).read_bytes();assert sha(raw_extract)==ledger['original_extract_sha256']
 repair=ledger['source_label_repair_history'];assert len(repair)==1
 assert repair[0]['profile_code']=='06' and repair[0]['accepted_value']==1
 counts={ALIASES[k]:v for k,v in ledger['controls']['field_sums'].items()}
 assert counts==prior['original_profile_count_sums']
 out={
  'status':'pass_525_independent_Pike_fields_and_reciprocal_proof_source_scoped',
  'frozen_independent_inputs':pins,'earlier_coordinator_original_review':pin(DATA/'coordinator-pike-profile-review.json'),
  'peer_frozen_aggregate_CSV':pin(ROOT/proof['peer_snapshot_path']),
  'raw_original_sha256':ledger['raw_sha256'],'profiles':25,'actual_section_pages':42,
  'candidate_admin_field_positions':525,'source_label_profile_code_checks':525,
  'additive_profile_count_vectors':20,'county_reported_count_vectors':19,'nonadditive_turnout_fields':25,
  'all_fields_match_separate_coordinator_extraction':True,
  'physical_reading_windows_kept_separately':windows,'original_raster_and_evidence_pins':list(hashes.values()),
  'independent_original_extract':pin(ROOT/ledger['original_extract_path']),
  'preserved_profile06_label_target_repair':repair,'raw_OCR_printed_literal_differences':len(ledger['raw_OCR_original_literal_differences']),
  'qualification':'Three independently original-derived Pike field sets agree at all525 positions. Baseline and turnout use different render scales and reading windows;525 source-window pairs remain separate with no exact-box equivalence claim. Nineteen county controls and20 additive profile COUNT vectors are distinct because profile blank1 is unprinted in the county panel. Original packet is not updated Pike or a disjoint addition to SEMS. This bounded original-source proof does not close statewide all-presidential/historical-native/method gates, approve current geography or authorize native887 dispatch.'}
 (DATA/'coordinator-pike-profile-peer-review.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k] for k in ['status','profiles','actual_section_pages','candidate_admin_field_positions','additive_profile_count_vectors','county_reported_count_vectors']}))

if __name__=='__main__':main()
