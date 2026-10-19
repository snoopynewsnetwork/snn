"""Fresh original Humphreys2020 Senate transcription, followed by frozen-source comparison."""
from pathlib import Path
import gzip,hashlib,json,re
D=Path(__file__).resolve().parent;R=D.parent
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
# Typed from four complete original Poppler page renders before opening worker candidate values.
TYPED={2:[[670,625,110,311,294,2,15,463,13,317,56],[214,140,2,10,3,34,38,156,62,87,57],[4,7,0,0,1,1,0,6,0,7,0]],3:[[51,208,3135]+[None]*8,[117,103,1023]+[None]*8,[1,2,29]+[None]*8]}
CODES={2:['4010','1020','2020','3010','5010','1010','2030','2010','3030','5030','5020'],3:['4030','3020',None]+[None]*8}
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(R)),'bytes':len(b),'sha256':sha(b)}
def main():
 op=D/'coordinator-qa/humphreys-2020-original-native-review/source-and-original-render-pins.json';rp=json.loads(op.read_bytes());assert len(rp)==4
 for x in rp:
  raw=gzip.decompress((R/x['source_path']).read_bytes());assert sha(raw)==x['source_raw_sha256']and len(raw)==x['source_raw_bytes'];b=(R/x['coordinator_original_raster_path']).read_bytes();assert sha(b)==x['raster_sha256']and len(b)==x['raster_bytes']
 sums=[sum(TYPED[2][i])+sum(TYPED[3][i][:2])for i in range(3)];assert sums==[r[2]for r in TYPED[3]]==[3135,1023,29]
 own={'scope':'Direct complete-original three-Senate rows, both separately captured2020Humphreys publications','candidate_order':NAMES,'typed_original_rows_by_actual_PDFpage':TYPED,'printed_codes_by_physical_column':CODES,'literal_header_qualification':{'actual_PDFpage':2,'physical_column':8,'certain_text_prefix':'Isola North','suffix_after_digit2':'I/l glyph unresolved; no exact suffix substitution asserted','certain_separate_printed_code':'2010'},'source_position_hints_from_worker':True,'candidate_values_transcribed_before_opening_worker_candidate_fields':True,'read_before_comparison_source_role':'PDF2eleven native,PDF3two native thenTOTALc3and eight unprinted template columns','own_original_render_pointers':pin(op)}
 ownpath=D/'coordinator-qa/humphreys-2020-original-native-review/typed-original-readings.json';b=(json.dumps(own,indent=2)+'\n').encode()
 if ownpath.exists():assert ownpath.read_bytes()==b
 else:ownpath.write_bytes(b)
 snap=D/'baselines/source/native-2020-40views-v1/snapshot.json';sb=snap.read_bytes();assert sha(sb)=='1b64e40325e3cca12abaf03db59aa5ac58115759ded3cc6cd2d08d03486dfdf3';m=json.loads(sb);p=next(x for x in m['pins']if x['original_path'].endswith('native-2020-additional-readings.json'));z=(R/p['stored_path']).read_bytes();assert sha(z)==p['stored_sha256'];raw=gzip.decompress(z);assert sha(raw)==p['original_sha256'];ss={x['source_id']:x for x in json.loads(raw)['sources']};found=[]
 for sid in ['sos-2020-county-humphreys','sos-2020-county-humphreys-amended']:
  s=ss[sid];assert len(s['pages'])==2;nc=0;null=0
  for p in s['pages']:
   page=p['page'];assert len(p['columns'])==11
   for i,col in enumerate(p['columns']):
    role='source_native_reporting_constituent'if page==2 or i<2 else'source_TOTAL'if i==2 else'unused_template_column';assert col['role']==role
    code=CODES[page][i]
    if code is not None:assert code in col['label_literal']
   byname={f['candidate']:f['values']for f in p['fields']}
   for name,values in zip(NAMES,TYPED[page]):assert byname[name]==values
   nc+=sum(v is not None for row in TYPED[page]for v in row);null+=sum(v is None for row in TYPED[page]for v in row)
  assert nc==42 and null==24;found.append({'source_id':sid,'raw_sha256':s['raw_sha256'],'numeric_positions':nc,'unused_null_positions':null,'native_constituents':13,'TOTAL_actual_PDFpage':3,'TOTAL_physical_column':3,'candidate_native_sums_and_printed_TOTALs':dict(zip(NAMES,sums))})
 out={'status':'pass_fresh_complete_original_Humphreys2020_Senate_reread_two_publications','immutable_worker_snapshot_pin':pin(snap),'coordinator_original_transcription_pin':pin(ownpath),'coordinator_original_render_pointer_pin':pin(op),'source_comparisons':found,'numeric_positions':84,'unused_null_positions':48,'literal_header_suffix_ambiguity_retained':own['literal_header_qualification'],'qualification':'Every typed three-Senate numeric and unused/null position matches the frozen source views. First physical Belzoni4010column is actually printed and is retained despite the machine omission. Source/render hints preceded independent original numeric reading; candidate fields were compared afterward. Each publication remains a distinct raw original. Matching vectors do not establish release chronology, native physical identity, historical method coverage,2024equivalence or current geography. This covers two publications only.','historical_native_complete':False,'formal_dispatch_accepted':False,'current_geography_approved':False}
 p=D/'coordinator-humphreys-2020-native-original-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps({'status':out['status'],'output_pin':pin(p)}))
if __name__=='__main__':main()
