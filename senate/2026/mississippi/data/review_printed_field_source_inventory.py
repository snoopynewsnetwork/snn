"""Check complete retained packet/page inventory, not source-field absence."""
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gzip,hashlib,json,re,struct,subprocess,tempfile
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/printed-field-source-inventory-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0));assert p.read_bytes()==b
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 QA.mkdir(parents=True,exist_ok=True);b,scope_pin=freeze(DATA/'baselines/printed-field-source-scope.json');assert len(b)==3438253 and sha(b)=='6ac1b357d6cbc8d0e65a55dc62cb40c60c7c210dcd27c9be4524c6a500584113';scope=json.loads(b);o,overview_pin=freeze(ROOT/scope['original_layout_overview']['path']);assert sha(o)==scope['original_layout_overview']['sha256'];overview=json.loads(o);assert overview['source_count']==scope['source_documents']==352 and overview['page_count']==scope['original_PDFpages']==3238 and len(overview['atlases'])==41
 refs={r['id']:r for r in json.loads((DATA/'baselines/source/references.json').read_bytes())};sources={r['source_id']:r for r in scope['sources']};assert len(sources)==352;atlas_positions={};atlas_pins=[]
 for a in overview['atlases']:
  p=ROOT/a['path'];assert pin(p)=={k:a[k]for k in ['path','bytes','sha256']};rb=p.read_bytes();w,h=struct.unpack('>II',rb[16:24]);assert rb.startswith(b'\x89PNG\r\n\x1a\n');atlas_pins.append(pin(p))
  for entry in a['pages']:
   key=(entry['source_id'],entry['PDFpage']);assert key not in atlas_positions;atlas_positions[key]=entry;bounds=entry['atlas_pixel_bounds'];assert 0<=bounds[0]<bounds[2]<=w and 0<=bounds[1]<bounds[3]<=h
 def check_source(s):
  sid=s['source_id'];ref=refs[sid];p=ROOT/ref['path'];z=p.read_bytes();raw=gzip.decompress(z);assert sha(z)==ref['stored_sha256']and sha(raw)==s['source_raw_sha256']==ref['raw_sha256']and raw.startswith(b'%PDF-')
  with tempfile.TemporaryDirectory()as td:
   pdf=Path(td)/'original.pdf';pdf.write_bytes(raw);text=subprocess.run(['pdfinfo',str(pdf)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode();pages=int(re.search(r'^Pages:\s+(\d+)',text,re.M)[1])
  assert [p['PDFpage']for p in s['pages']]==list(range(1,pages+1))
  for page in s['pages']:
   entry=atlas_positions[sid,page['PDFpage']];assert entry['source_raw_sha256']==s['source_raw_sha256']and page['overview']['atlas']==next(a['path']for a in overview['atlases']if entry in a['pages'])and page['overview']['slot']==entry['atlas_slot']and page['overview']['bounds']==entry['atlas_pixel_bounds']
   if page['machine_locator']:assert(ROOT/page['machine_locator']).exists()
  return dict(source_id=sid,raw_PDF_sha256=sha(raw),raw_PDF_bytes=len(raw),stored_original=pin(p),independent_pdfinfo_pages=pages)
 with ThreadPoolExecutor(max_workers=4)as pool:checked=list(pool.map(check_source,sources.values()))
 counts=Counter()
 for r in checked:counts[int(r['source_id'].split('-')[1])]+=1
 assert counts=={2018:164,2020:104,2024:84}and sum(r['independent_pdfinfo_pages']for r in checked)==len(atlas_positions)==3238
 assert scope['vendor_native_profiles']==45 and scope['vendor_required_numeric_fields']==905 and scope['administrative_split_ballot_style_rows']==58 and scope['administrative_split_parent_TOTALs']==20
 out=dict(status='pass_bounded_complete_original_packet_page_inventory_and_layout_source_pins',frozen_printed_field_scope=scope_pin,frozen_original_layout_overview=overview_pin,source_documents=352,actual_original_pdfinfo_pages=3238,source_publications_by_year=dict(counts),complete_original_source_checks=checked,overview_atlas_pins=atlas_pins,worker_reported_overviews_visually_inspected=41,coordinator_freshly_visually_read_all41_overviews=False,producer_declared_field_scope={k:scope[k]for k in ['county_summary_panels','statistics_panels','additional_SEMS_E013_views','vendor_native_profiles','vendor_required_numeric_fields','administrative_split_ballot_style_rows','administrative_split_parent_TOTALs']},qualification='All352original raw/stored hashes and independently obtained actualPDFpagecounts match3238page inventory positions and41exact raster atlases/bounds. This checks source completeness and producer-declared located-field scope, not coordinator fresh glyph reading of all pages or proof no other publication/field exists. Downsampled/rotated layout overviews cannot establish numeric glyphs, source absence, exact digit/geography polygons or current IDs. Existing direct candidate/profile/panel proof remains the numeric basis. New Union split/style source58rows/20parentTOTALs has no printed candidate allocation; unknown weight/tie/selected targets must not become0/no-positive-pool. Montgomery885incompatibility and all prior named/control residuals remain unallocated. No full independent native extraction, method/currentgeometry or native887acceptance follows.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-printed-field-source-inventory-review.json';raw=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==raw
 else:p.write_bytes(raw)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
