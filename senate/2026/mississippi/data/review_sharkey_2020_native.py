"""Fresh complete-original Sharkey2020 table reread, preserving both publications."""
from pathlib import Path
import gzip,hashlib,json
D=Path(__file__).resolve().parent;ROOT=D.parent;DEST=D/'coordinator-qa/sharkey-2020-original-native-review'
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
READINGS=[[176,185,228,150,267,100,48,321,3,33,1511],[30,119,80,88,243,4,0,20,30,49,663],[2,1,0,0,1,1,0,2,0,0,7]]
LABELS=['Anguilla Fifth District','Anguilla Fourth District','Cary Second District','Delta City Fifth District','Rolling Fork First District','Rolling Fork Fourth District','Rolling Fork Second District','Rolling Fork Third District','Spanish Fort First District','Straight Bayou Fourth District','TOTAL']
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 pagepins=json.loads((DEST/'source-and-original-render-pins.json').read_bytes());mp=D/'baselines/source/native-2020-22views-v1/snapshot.json';b=mp.read_bytes();assert sha(b)=='836e81cddc6c404f26c6ecd5c96c79fac20f9db6c2b28a492798ae61190766a3';m=json.loads(b);p=next(p for p in m['pins']if p['original_path'].endswith('native-2020-additional-readings.json'));stored=(ROOT/p['stored_path']).read_bytes();assert sha(stored)==p['stored_sha256'];raw=gzip.decompress(stored);assert sha(raw)==p['original_sha256'];sources={s['source_id']:s for s in json.loads(raw)['sources']};comparisons=[]
 for r in pagepins:
  ref=r['source'];sid=ref['id'];assert sid in ['sos-2020-county-sharkey','sos-2020-county-sharkey-amended'];s=sources[sid];b=(ROOT/ref['path']).read_bytes();assert sha(b)==ref['stored_sha256'];assert sha(gzip.decompress(b))==ref['raw_sha256']==s['raw_sha256'];assert pin(ROOT/r['render_path'])['sha256']==r['render_sha256'];assert len(s['pages'])==1;page=s['pages'][0];assert page['page']==2 and len(page['columns'])==11
  assert [f['candidate']for f in page['fields']]==NAMES and[f['values']for f in page['fields']]==READINGS
  assert [' '.join(c['label_literal'].split())for c in page['columns']]==LABELS
  assert [c['role']for c in page['columns']]==['source_native_reporting_constituent']*10+['source_TOTAL']
  assert all(sum(v[:10])==v[10]for v in READINGS)
  comparisons.append(dict(source_id=sid,raw_sha256=s['raw_sha256'],actual_PDFpage=2,native_constituents=10,TOTAL_physical_column=11,numeric_positions=33,unprinted_outer_margin_not_a_column=True,source_control=dict(zip(NAMES,[v[10]for v in READINGS])),original_render_pin=pin(ROOT/r['render_path'])))
 out=dict(status='pass_fresh_complete_original_Senate_reread_two_Sharkey2020_publications',immutable_worker_snapshot_pin=pin(mp),coordinator_page_source_pointers=pin(DEST/'source-and-original-render-pins.json'),candidate_order=NAMES,physical_source_header_order=LABELS,typed_original_rows_each_publication=READINGS,source_comparisons=comparisons,numeric_positions=66,unused_template_columns=0,qualification='Both complete originalPDF2 tables have ten native columns and theeleventh printedTOTAL; paper outside the righttable edge is not a twelfth template column. All66 Senate numeric glyphs were reread directly from fresh complete Poppler originals and match the immutable22publication witness. Both source hashes/publications remain separate despite identical vectors; no chronology, native identity or2024/current geography equivalence follows. Earlier source-coordinate aids and their extra outermargin proposal remain unchanged. Only these two Senate source views are covered, not full presidential/historical/method review or dispatch acceptance.',historical_native_complete=False,formal_dispatch_accepted=False,current_geography_approved=False)
 p=D/'coordinator-sharkey-2020-native-original-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(dict(status=out['status'],numeric_positions=66,output_pin=pin(p))))
if __name__=='__main__':main()
