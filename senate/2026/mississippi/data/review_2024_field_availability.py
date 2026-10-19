"""Verify source coverage and explicitly bounded panel-field availability."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,re,subprocess,tempfile
from review_allfield_milestone import load,sources
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/2024-field-availability-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0));assert p.read_bytes()==b
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 QA.mkdir(parents=True,exist_ok=True);ab,ap=freeze(DATA/'turnout/2024-field-availability.json');a=json.loads(ab);z=(ROOT/a['fullpage_OCR_locator_stored_path']).read_bytes();raw=gzip.decompress(z);assert len(z)==a['fullpage_OCR_locator_stored_bytes']and sha(z)==a['fullpage_OCR_locator_stored_sha256']and len(raw)==a['fullpage_OCR_locator_raw_bytes']and sha(raw)==a['fullpage_OCR_locator_raw_sha256'];inv=json.loads(raw);loc={s['source_id']:s for s in inv['sources']};assert len(loc)==82 and inv['source_views']==82 and inv['total_pdf_pages']==803
  # The locator is already a complete pinned immutable dependency; no duplicate body.
 sb,sp=freeze(ROOT/a['direct_original_summary_reading_path']);tb,tp=freeze(ROOT/a['direct_original_statistics_reading_path']);assert sha(sb)==a['direct_original_summary_reading_sha256']and sha(tb)==a['direct_original_statistics_reading_sha256'];summary={s['source_id']:s for s in json.loads(sb)['sources']};stats={s['source_id']:s for s in json.loads(tb)};assert len(summary)==15 and len(stats)==13
 _,items,peer_snapshot=load('82views','94576fcfa4b7b245e2d5baa9e8366e4489594804f41694ea04a9f6315e46b336');peer=sources(items);records={s['source_id']:s for s in a['preferred_sources']};assert set(records)==set(loc)==set(peer)
 flags=Counter();status_counts=Counter();original_pins=[];page_count=0
 for sid,r in records.items():
  source=loc[sid];stored=ROOT/r['source_original_path'];pdf=gzip.decompress(stored.read_bytes());assert sha(pdf)==r['source_raw_sha256']==source['raw_sha256']==peer[sid]['raw_sha256'];assert pdf.startswith(b'%PDF-')
  with tempfile.TemporaryDirectory()as td:
   p=Path(td)/'original.pdf';p.write_bytes(pdf);info=subprocess.run(['pdfinfo',str(p)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode();actual=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1])
  assert actual==source['page_count']==len(source['pages'])==r['source_pdf_pages_inspected_by_original_page_OCR'];assert [p['pdf_page']for p in source['pages']]==list(range(1,actual+1));page_count+=actual
  for page in source['pages']:assert re.fullmatch('[0-9a-f]{64}',page['render_sha256'])and len(page['render_size'])==2 and min(page['render_size'])>0 and isinstance(page['ocr_text'],str)
  su=summary.get(sid);st=stats.get(sid);assert r['direct_original_summary_page']==(su['page']if su else None)and r['direct_original_statistics_page']==(st['page']if st else None)
  expected={'statistics_registered_voters_field_printed':st is not None and st['registered_voters_total']is not None,'statistics_ballots_cast_field_printed':st is not None and st['ballots_cast_total']is not None,'statistics_blank_field_printed':st is not None and st['ballots_cast_blank']is not None,'senate_generic_write_in_row_printed':su is not None and su['senate'].get('Write-In Totals')is not None,'senate_overvote_row_printed':su is not None and su['senate'].get('Overvotes')is not None,'senate_undervote_row_printed':su is not None and su['senate'].get('Undervotes')is not None}
  for field,value in expected.items():assert r[field]is value;flags[field]+=value
  assert r['field_availability_status']==('direct_original_panel_read'if su or st else'not_located_by_allpage_original_OCR_no_numeric_field_accepted');status_counts[r['field_availability_status']]+=1
  if not(su or st):assert all(not v for v in expected.values())and 'No OCR absence' in r['availability_qualification']
  original_pins.append(dict(source_id=sid,stored_original=pin(stored),raw_PDF_bytes=len(pdf),raw_PDF_sha256=sha(pdf),independent_pdfinfo_page_count=actual,direct_summary_page=r['direct_original_summary_page'],direct_statistics_page=r['direct_original_statistics_page'],field_availability_status=r['field_availability_status']))
 assert page_count==803 and status_counts['direct_original_panel_read']==14 and status_counts['not_located_by_allpage_original_OCR_no_numeric_field_accepted']==68
 assert sum(sid in summary for sid in records)==14 and sum(sid in stats for sid in records)==12
 assert flags==dict(statistics_registered_voters_field_printed=12,statistics_ballots_cast_field_printed=12,statistics_blank_field_printed=6,senate_generic_write_in_row_printed=13,senate_overvote_row_printed=3,senate_undervote_row_printed=3)
 assert stats['sos-2024-county-lincoln']['ballots_cast_total']==15898 and stats['sos-2024-county-lincoln']['registered_voters_total']==0
 alternatives=a['nonadditive_alternative_sources'];assert {r['source_id']for r in alternatives}=={'sos-2024-county-pike','sos-2024-county-coahoma'}
 for r in alternatives:
  pdf=gzip.decompress((ROOT/r['source_original_path']).read_bytes());assert sha(pdf)==r['source_raw_sha256'];sid=r['source_id'];assert r['direct_original_summary_page']==(summary[sid]['page']if sid in summary else None)and r['direct_original_statistics_page']==(stats[sid]['page']if sid in stats else None)
 out=dict(status='pass_bounded_original2024_panel_availability_scope_and_raw_source_coverage',frozen_availability=ap,frozen_summary_ledger=sp,frozen_statistics_ledger=tp,complete_OCR_locator_dependency=pin(ROOT/a['fullpage_OCR_locator_stored_path']),immutable_independent_preferred82_source_witness=peer_snapshot,preferred_source_views=82,actual_original_PDF_pages_independently_counted=803,preferred_direct_summary_panels=14,preferred_direct_statistics_panels=12,separate_original_Pike_summary_panels=1,separate_original_Pike_statistics_panels=1,direct_panel_source_status_counts=dict(status_counts),field_availability_counts=dict(flags),original_source_pins=original_pins,nonadditive_alternative_source_records=alternatives,qualification='Every82preferred rawPDFhash and actualpdfinfo pagecount agrees immutable original-source witness; all803locator positions are present. The OCRtext/renderhash diagnostic is a locator, not newly accepted numeric evidence or absence proof. Sixty-eight not-located sources remain unavailable-in-review; false field flags there mean no field accepted in this review, NOT source-published zero or proof the field was never printed. Fourteen preferred summary/twelve preferred statistics panels plus separate originalPike are the bounded direct ledger scope. Generic/writein/method/registration/ballot fields keep exact publication/date/printed-zero/null semantics; no candidate-method allocation or complete-method approval follows. Older14all-version-summary/12statistics reciprocal358positions remain that older scope, not silently expanded to current15/13. CorrectedLincolnballots15898 is included. No native887/currentgeography or complete historical-method acceptance.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-2024-field-availability-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
