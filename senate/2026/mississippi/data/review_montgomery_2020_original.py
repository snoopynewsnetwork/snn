"""Fresh complete original publication status and three Senate source rows."""
from pathlib import Path
import gzip,hashlib,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/montgomery-2020-source-status'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 p=DATA/'baselines/source/sos-2020-county-montgomery.body.gz';raw=gzip.decompress(p.read_bytes());assert sha(raw)=='f99e828ec13028890e44a9cde10bdfa28fbb607cb84b9cdc391597cf6650b3ce'
 values={2:{'Mike Espy':[219,326,221,141,18,105,68,53,173,32,8],'Cindy Hyde-Smith':[257,177,235,47,132,95,15,82,563,241,91],'Jimmy L. Edwards':[5,7,5,2,4,1,0,2,20,5,4]},3:{'Mike Espy':[645,95,8,152,2264]+[None]*6,'Cindy Hyde-Smith':[211,86,73,433,2738]+[None]*6,'Jimmy L. Edwards':[13,3,1,14,86]+[None]*6}}
 sp=DATA/'baselines/source/native-2020-75views-v1/snapshot.json';s=json.loads(sp.read_bytes());a=next(a for a in s['pins']if a['original_path'].endswith('native-2020-additional-readings.json'));b=gzip.decompress((ROOT/a['stored_path']).read_bytes());assert sha(b)==a['original_sha256'];source=next(a for a in json.loads(b)['sources']if a['source_id']=='sos-2020-county-montgomery');assert source['raw_sha256']==sha(raw)
 for p in source['pages']:
  page=p['page'];assert page in [2,3]and p['source_status_literal']=='Unofficial Recapitulation'and p['printed_footer_page_literal']==f'Page : {page-1}'
  for f in p['fields']:assert f['values']==values[page][f['candidate']]
 sums={n:sum(values[2][n])+sum(values[3][n][:4])for n in values[2]};assert sums=={n:values[3][n][4]for n in values[2]}=={'Mike Espy':2264,'Cindy Hyde-Smith':2738,'Jimmy L. Edwards':86}
 out=dict(status='fresh_original_unofficial_status_and48_numeric18_null_fields_agree',source_id='sos-2020-county-montgomery',stored_original=pin(DATA/'baselines/source/sos-2020-county-montgomery.body.gz'),raw_PDF_sha256=sha(raw),raw_PDF_bytes=len(raw),source_original_status_title='Unofficial Recapitulation',actual_PDFpages=[2,3],printed_footer_page_numbers=[1,2],render_parameters=dict(renderer='pdftoppm',resolution_DPI=160,rotation_deskew_enhancement='none'),full_original_render_pins=[pin(QA/f'p{i}-original.png')for i in [2,3]],direct_original_three_candidate_vectors_by_PDFpage=values,native_constituents=15,physical_TOTAL=dict(actual_PDFpage=3,physical_column=5),numeric_fields=48,unused_null_fields=18,source_candidate_sums_and_printed_TOTALs=sums,immutable_worker_source_witness=pin(sp),qualification='Coordinator freshly read both complete unaltered original pages, directly transcribed all three Senate rows, and separately verified source title/footer. Reading follows the worker source finding and is not claimed prior blind. Both pages explicitly say Unofficial Recapitulation despite their official SOS index provenance; count agreement does not upgrade that printed source status or establish certification/release chronology. No independent fresh reading of all other75-publication glyphs, numeric crop polygon, historical/current identity, methods or native887 approval is inferred.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-montgomery-2020-original-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable review changed'
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
