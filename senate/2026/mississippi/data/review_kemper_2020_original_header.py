"""Record the narrow original Kemper label finding without rewriting witnesses."""
from pathlib import Path
import gzip,hashlib,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/kemper-2020-original-header'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 source=DATA/'baselines/source/sos-2020-county-kemper.body.gz';raw=gzip.decompress(source.read_bytes());assert sha(raw)=='f0f5318f6b5c42efb0ca68c5c70a97f19c243a134c113bce2819e9f5b809ced6'
 snapshot=DATA/'baselines/source/native-2020-55views-v1/snapshot.json';s=json.loads(snapshot.read_bytes());p=next(p for p in s['pins']if p['original_path'].endswith('native-2020-additional-readings.json'));b=gzip.decompress((ROOT/p['stored_path']).read_bytes());assert sha(b)==p['original_sha256'];a=next(a for a in json.loads(b)['sources']if a['source_id']=='sos-2020-county-kemper');page=next(p for p in a['pages']if p['page']==2);col=next(c for c in page['columns']if c['source_column']==9);assert col['label_literal']=='Lynnville'
 values={f['candidate']:f['values'][8]for f in page['fields']};assert values=={'Mike Espy':133,'Cindy Hyde-Smith':180,'Jimmy L. Edwards':2}
 worker=DATA/'turnout/2020-native-kemper-header-review.json';wb=worker.read_bytes();copy=QA/'turnout-original-header-review.json.gz'
 if copy.exists():assert gzip.decompress(copy.read_bytes())==wb
 else:copy.write_bytes(gzip.compress(wb,mtime=0))
 w=json.loads(wb);assert w['accepted_original_read']=='Lynville'and w['peer_derivative_label']=='Lynnville'
 out=dict(status='original_literal_header_difference_confirmed',source_id='sos-2020-county-kemper',stored_original_pin=pin(source),original_PDF_sha256=sha(raw),original_PDF_bytes=len(raw),actual_PDFpage=2,physical_column=9,coordinator_original_glyph_read='Lynville',frozen55_derivative_literal='Lynnville',candidate_values_directly_read_on_complete_original_page=values,coordinator_full_unaltered_original_render=pin(QA/'page2-original.png'),render_parameters=dict(renderer='pdftoppm',actual_PDFpage=2,resolution_DPI=200,pixel_size=[2183,1692],deskew_rotation_enhancement='none'),coordinator_exact_original_crop=pin(QA/'page2-column9-header-crop.png'),coordinator_upright_crop=pin(QA/'page2-column9-header-upright.png'),crop_parameters=dict(pixel_box_left_top_right_bottom=[1710,280,1848,532],upright_rotation_clockwise_degrees=90,enhancement='none'),earlier_worker_header_review_exact_copy=pin(copy),earlier_worker_header_review_original_bytes=len(wb),earlier_worker_header_review_original_sha256=sha(wb),frozen55_source_witness=pin(snapshot),qualification='Fresh coordinator Poppler full original page and an unchanged-pixel cropped/rotated header independently read one n, Lynville. Reading occurred after the source exception and frozen derivative were known; no prior-blind claim. Votes133/180/2 and role agree; literal labels differ. Earlier immutable55/60/65 derivatives and bounded reviews stay unchanged, with this explicit later original-label exception. A worker must retain its own original reread/correction history in any later version. No label normalization, numeric allocation, historical/current precinct identity, parsed-ID equivalence or native887 approval follows.',literal_label_agreement_with_frozen55=False,numeric_values_agree=True,current_geography_approved=False,formal_native887_dispatch_accepted=False)
 p=DATA/'coordinator-kemper-2020-original-header-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable original review changed'
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
