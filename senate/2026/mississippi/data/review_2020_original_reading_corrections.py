"""Retain original-glyph correction histories separately from source versions."""
from pathlib import Path
import gzip,hashlib,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/2020-source-reading-corrections'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 findings=[]
 for tag,page,expected,old,new in [('perry',2,'ad1bebb4e1abe1b57555eefdaf66bd75a502e714a7fd43b74503f2d544b0fd83','Beaumont Senior Citizens 1120','Beaumont Senior Citizens 5120'),('webster',3,'594723278e3d2f8f39e154da0c6de3559196f592b4f01955a4d4c97b1274ab81',4057,4067)]:
  p=DATA/f'turnout/2020-native-{tag}-correction-history.json';raw=p.read_bytes();copy=QA/(p.name+'.gz')
  if copy.exists():assert gzip.decompress(copy.read_bytes())==raw
  else:copy.write_bytes(gzip.compress(raw,mtime=0))
  h=json.loads(raw);assert h['initial_direct_fullpage_read']==old and h['corrected_direct_original_crop_read']==new and h['source_page']==page
  for kind in ['original_raster','source_crop']:
   assert pin(ROOT/h[kind])['sha256']==h[kind+'_sha256']
  prior=DATA/f'coordinator-qa/turnout-2020-native-extensions/{tag}-2020-native-original-readings.json.gz';b=gzip.decompress(prior.read_bytes());a=json.loads(b);original=ROOT/a['source_original_path'];pdf=gzip.decompress(original.read_bytes());assert sha(pdf)==expected==a['source_raw_sha256']
  if tag=='perry':assert all(r['literal_native_label']==new for r in a['rows']if r['source_page']==2 and r['source_column']==3)
  else:assert next(r for r in a['rows']if r['source_page']==3 and r['source_column']==7 and r['candidate']=='Cindy Hyde-Smith')['votes']==new
  findings.append(dict(source_id=h['source_id'],raw_original_sha256=expected,stored_original=pin(original),actual_PDFpage=page,physical_column=h['physical_column'],frozen_source_transcript_copy=pin(prior),exact_worker_history=pin(p),lossless_worker_history_copy=pin(copy),worker_original_raster=pin(ROOT/h['original_raster']),worker_reading_crop=pin(ROOT/h['source_crop']),fresh_complete_coordinator_original_render=pin(QA/f'{tag}-p{page}-complete-original.png'),coordinator_render_parameters=dict(renderer='pdftoppm',DPI=150,deskew_rotation_enhancement='none'),initial_reading=old,corrected_original_glyph_reading=new,source_vintage_change=False,source_native_vote_allocation=False))
 out=dict(status='pass_bounded_original_Perry_header_and_Webster_TOTAL_glyph_review',original_findings=findings,qualification='Coordinator viewed both retained original-only crops and freshly rendered/read the hash-checked complete originals. The source glyphs are5120 and4067. This followed known worker exceptions, not a prior-blind transcript. Perry changes a source header parse; Webster corrects a TOTAL transcription after a closure check prompted rereading, without allocating any native vote or claiming a changed source publication. Initial readings and correction triggers remain exact history. Only these two glyph exceptions are fresh coordinator findings; not a new all-field or whole historical-method/geographic acceptance.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-2020-original-reading-corrections-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable original correction review changed'
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
