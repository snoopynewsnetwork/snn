"""Verify the worker's bounded literal-case repair without replacing old witnesses."""
from pathlib import Path
import copy,csv,gzip,hashlib,io,json

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/franklin-2018-worker-case-history'

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))

def main():
 QA.mkdir(parents=True,exist_ok=True)
 hb,hpin=freeze(DATA/'turnout/2018-franklin-header-case-correction-history.json');h=json.loads(hb)
 assert sha(hb)=='0189810b78d3660e24af1cb29e9d79328d01d917d7ebb5c4a3e4f7553b40cbdb'
 pb,ppin=freeze(ROOT/h['prior_pin']);assert sha(pb)==h['prior_pin_sha256'];prior=json.loads(pb)
 old={};prior_pins=[]
 for a in prior['pins']:
  p=ROOT/a['stored_path'];z=p.read_bytes();assert len(z)==a['stored_bytes'] and sha(z)==a['stored_sha256'];b=gzip.decompress(z);assert len(b)==a['original_bytes'] and sha(b)==a['original_sha256']
  archived=DATA/'coordinator-qa/franklin-2018-original-native'/(Path(a['earlier_original_path']).name+'.gz')
  assert gzip.decompress(archived.read_bytes())==b
  old[Path(a['earlier_original_path']).suffix]=b
  prior_pins.append(dict(worker_prior_lossless_copy=pin(p),earlier_coordinator_lossless_copy=pin(archived),original_bytes=len(b),original_sha256=sha(b)))
 jb,jpin=freeze(ROOT/h['new_readings_path']);cb,cpin=freeze(ROOT/h['new_flat_path'])
 assert sha(jb)==h['new_readings_sha256'] and sha(cb)==h['new_flat_sha256']
 a=json.loads(old['.json']);b=json.loads(jb);expected=copy.deepcopy(a);changes=[]
 for s in expected['sources']:
  for r in s['rows']:
   if r['source_pdf_page']==2 and r['physical_source_column']==9:
    assert r['literal_source_header']=='McCall'
    changes.append(dict(source_id=s['source_id'],candidate=r['candidate'],source_pdf_page=2,physical_column=9,earlier_literal='McCall',corrected_source_literal='Mccall',votes=r['votes']))
    r['literal_source_header']='Mccall'
 assert len(changes)==6 and changes==h['changes'] and h['changed_position_count']==6
 assert expected==b,'Unexpected JSON source change beyond six header literals'
 before=list(csv.DictReader(io.StringIO(old['.csv'].decode())));after=list(csv.DictReader(io.StringIO(cb.decode())))
 assert len(before)==len(after)==132
 csv_changes=[]
 for i,(x,y)in enumerate(zip(before,after)):
  e=dict(x)
  if int(e['source_pdf_page'])==2 and int(e['physical_source_column'])==9:
   assert e['literal_source_header']=='McCall';e['literal_source_header']='Mccall';csv_changes.append(i)
  assert e==y,('Unexpected flat-field change',i)
 assert len(csv_changes)==6
 crops=[]
 for c in h['crops']:
  raster=ROOT/c['original_raster'];crop=ROOT/c['rendered_crop']
  assert pin(raster)['sha256']==c['original_raster_sha256'] and pin(crop)['sha256']==c['rendered_crop_sha256']
  s=next(s for s in b['sources']if s['source_id']==c['source_id'])
  assert s['source_raw_sha256']==c['source_raw_sha256']
  raw=gzip.decompress((ROOT/s['source_original_path']).read_bytes());assert sha(raw)==c['source_raw_sha256']
  crops.append(dict(source_id=c['source_id'],raw_original_sha256=sha(raw),stored_original=pin(ROOT/s['source_original_path']),worker_full_original_raster=pin(raster),worker_upright_original_crop=pin(crop),physical_source_column=9,actual_PDFpage=2,source_pixel_crop=c['source_pixel_crop'],rotation_clockwise_degrees=c['rotation_clockwise_degrees']))
 original_proof=DATA/'coordinator-franklin-2018-original-native-review.json'
 correction_proof=DATA/'coordinator-franklin-2018-header-case-correction.json'
 assert pin(original_proof)['sha256']=='c39e7ccc9f4e4a2b8c3be7df4768cf3b6e1560c8cd3492dec58c1a8a0c7dde19'
 assert pin(correction_proof)['sha256']=='414360063ec68c693e46a31ff934ff613eaff904b6b7e85b083b88b4dd7f4321'
 out=dict(status='pass_exact_six_header_only_Franklin2018_worker_correction_history',worker_history=hpin,worker_prior_pin_manifest=ppin,prior_worker_and_coordinator_bodies=prior_pins,corrected_worker_bodies=[jpin,cpin],candidate_positions_compared=132,changed_literal_header_fields=6,exact_changes=changes,worker_original_crop_evidence=crops,earlier_coordinator_original_review=pin(original_proof),separate_coordinator_original_case_addendum=pin(correction_proof),qualification='Both complete prior worker JSON/CSV bodies equal the earlier coordinator lossless captures. The current frozen bodies change exactly six PDF2 physical-column9 literal header fields from McCall to source Mccall, with every vote, role, physical position, original/render hash and other source field identical. The original coordinator transcript retains its earlier case error; a separate already pinned fresh original case review records the correction. This addendum verifies the worker provenance history and unchanged source semantics; it is not a new glyph reread of all132 positions, a source-publication change, cross-stage identity/current geography or whole historical/method/native887 acceptance.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-franklin-2018-worker-case-history-review.json';body=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==body,'Immutable correction history review changed'
 else:p.write_bytes(body)
 print(json.dumps(pin(p)))

if __name__=='__main__':main()
