"""Bounded original Alcorn2020 native-source review; no cross-year joins."""
from pathlib import Path
import csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent;ROOT=DATA.parent
DEST=DATA/'coordinator-qa/alcorn-2020-original-native-review'
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
# Confirmed on fresh complete original Poppler150dpi pages after seeing worker
# readings; therefore this is a source re-read, not a prior-blind transcription.
P2=[[237,11,192,289,439,249,159,33,174,218,138],
[1089,73,600,401,840,1218,777,311,1367,830,326],
[43,0,19,17,24,39,34,10,33,18,11]]
P3=[[200,172,611,133,207,179,3641],[748,679,440,889,614,414,11616],[27,31,15,24,20,13,378]]
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 inputs={};pins=[]
 for name,expected in [('native-2020-additional-readings.json','21a5d2ed5c03520bdadabc1800473761e99acabb90f73d57285edbbe99df9f50'),('native-2020-additional-candidate-votes.csv','58f27d66c9edcfed4bb7819ec8f1297033e22c1bd3e3679c9648e01401904cb9')]:
  p=DEST/(name+'.gz')
  if not p.exists():
   b=(DATA/'baselines'/name).read_bytes();assert sha(b)==expected
   p.write_bytes(gzip.compress(b,mtime=0))
  b=gzip.decompress(p.read_bytes());assert sha(b)==expected;inputs[name]=b;pins.append(pin(p))
 ledger=json.loads(inputs['native-2020-additional-readings.json']);assert len(ledger['sources'])==1;s=ledger['sources'][0]
 assert s['source_id']=='sos-2020-county-alcorn';ref=json.loads((DEST/'source.json').read_bytes())
 raw=gzip.decompress((ROOT/ref['path']).read_bytes());assert sha(raw)==s['raw_sha256']=='ca72c1a647f7676be3cf03a076eba7c35473517d0a1cc96ff1adbceb3a806dff'
 count=0;nulls=0;flat=list(csv.DictReader(io.StringIO(inputs['native-2020-additional-candidate-votes.csv'].decode())))
 for p,values in zip(s['pages'],[P2,[v+[None]*4 for v in P3]]):
  assert [f['candidate']for f in p['fields']]==NAMES
  assert [f['values']for f in p['fields']]==values
  if p['page']==3:assert p['columns'][6]['role']=='source_TOTAL'and p['columns'][6]['label_literal']=='TOTAL'
  for f in p['fields']:
   for col,v in zip(p['columns'],f['values']):
    r=next(r for r in flat if int(r['source_page'])==p['page']and int(r['source_column'])==col['source_column']and r['candidate']==f['candidate'])
    assert (None if r['votes']==''else int(r['votes']))==v
    assert r['source_raw_sha256']==s['raw_sha256']and r['role']==col['role']and r['literal_native_label']==col['label_literal']
    if col['role']=='unused_template_column':assert v is None;nulls+=1
    else:assert type(v)is int;count+=1
 assert count==54 and nulls==12 and len(flat)==66
 assert all(sum(P2[i])+sum(P3[i][:6])==P3[i][6]for i in range(3))
 out=dict(status='pass_bounded_fresh_complete_original_Alcorn2020_Senate_native_reread',
 source_pin=ref,immutable_worker_input_pins=pins,
 coordinator_complete_original_page_pins=[pin(DEST/f'original-{n:02d}.png')for n in [2,3]],
 candidate_order=NAMES,PDF2_readings=P2,PDF3_native_and_TOTAL_readings=P3,
 native_constituents=17,numeric_positions=54,unused_null_positions=12,
 actual_TOTAL_PDFpage=3,actual_TOTAL_physical_column=7,
 source_native_sums=dict(zip(NAMES,[v[6]for v in P3])),
 qualification='All54 numeric glyphs and12 unused blanks were reread from fresh complete original Poppler150dpi pages after seeing worker readings; this is not a prior-blind transcription. The source partition closes independently printedTOTAL. Physical seventh-columnTOTAL is verified on actualPDF3, separately from unchanged earlier proposal metadata. Source reading windows and historical labels are not legal polygons or a2024/current ID join. Generic,under/over,ballots,registration andmethod fields absent from these selectedSEMSrows remain unknown. Only this2020 publication is covered; all104publication/native completeness and dispatch acceptance are not inferred.',
 historical_native_complete=False,formal_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-alcorn-2020-native-original-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(dict(status=out['status'],output_pin=pin(p))))
if __name__=='__main__':main()
