"""Verify six source-label changes against complete retained derivative bodies."""
from pathlib import Path
import copy,csv,gzip,hashlib,io,json

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/winston-2018-header-history'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 QA.mkdir(parents=True,exist_ok=True);q=QA/(p.name+'.gz')
 b=gzip.decompress(q.read_bytes())if q.exists()else p.read_bytes()
 if not q.exists():q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 hp=DATA/'turnout/2018-winston-header-original-correction-history.json';hb,hpin=freeze(hp);h=json.loads(hb)
 mp=ROOT/h['prior_manifest'];mb,mpin=freeze(mp);assert sha(mb)==h['prior_manifest_sha256'];m=json.loads(mb)
 bodies=[];changes=[]
 for p in m['pins']:
  z=(ROOT/p['archive_path']).read_bytes();old=gzip.decompress(z);assert len(z)==p['stored_bytes']and sha(z)==p['stored_sha256']and len(old)==p['raw_bytes']and sha(old)==p['raw_sha256']
  new,npin=freeze(ROOT/p['original_path']);bodies.append(dict(prior_pin=p,later_frozen=npin))
  kind='json'if p['original_path'].endswith('.json')else'csv';claimed=next(r for r in h['derivative_comparisons']if r['derivative']==kind);assert sha(new)==claimed['current_sha256']
  if kind=='json':a=json.loads(old);b=json.loads(new);ar=[r for s in a['sources']for r in s['rows']];br=[r for s in b['sources']for r in s['rows']]
  else:ar=list(csv.DictReader(io.StringIO(old.decode())));br=list(csv.DictReader(io.StringIO(new.decode())))
  assert len(ar)==len(br)==132;found=[]
  for x,y in zip(ar,br):
   if x!=y:
    assert {k for k in x if x[k]!=y[k]}=={'literal_source_header'}and x['literal_source_header']=='Nann Waiya'and y['literal_source_header']=='Nanih Waiya'
    assert int(x['source_pdf_page'])==2 and int(x['physical_source_column'])==8
    found.append(dict(source_id=x['source_id'],source_pdf_page=2,physical_source_column=8,candidate=x['candidate'],old='Nann Waiya',new='Nanih Waiya'));x['literal_source_header']='Nanih Waiya'
  assert len(found)==6 and found==claimed['changes']
  if kind=='json':assert a==b
  else:assert ar==br
  changes.append(dict(derivative=kind,compared_source_positions=132,label_only_changes=found))
 evidence=[]
 for r in h['original_crops']:
  assert pin(ROOT/r['full_original_raster'])['sha256']==r['full_original_raster_sha256']and pin(ROOT/r['crop_path'])['sha256']==r['crop_sha256'];assert r['original_literal']=='Nanih Waiya'
  evidence.append(dict(full_original_raster=pin(ROOT/r['full_original_raster']),original_crop=pin(ROOT/r['crop_path']),original_pixel_box=r['crop_from_original_pixels'],rotation_clockwise_degrees=r['rotation_clockwise_degrees']))
 out=dict(status='pass_exact_six_label_only_source_corrections_with_prior_bytes_retained',worker_history=hpin,prior_manifest=mpin,complete_derivative_bodies=bodies,comparisons=changes,worker_original_evidence=evidence,qualification='The complete prior JSON becomes the later frozen JSON with exactly six literal header replacements; every other source field is exact, and all132 CSV positions preserve votes, roles, raw source hashes and physical locators. Complete source rasters/crops are hash-verified. This is not a fresh coordinator glyph reread or raster/numeric/geographic polygon identity claim. Frozen earlier witnesses stay unchanged; no current geography or native887 acceptance follows.',formal_native887_dispatch_accepted=False)
 p=DATA/'coordinator-winston-2018-source-header-history-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
