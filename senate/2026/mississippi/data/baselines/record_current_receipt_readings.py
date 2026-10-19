"""Bounded own primary reading of current SOS instructions and remand opinion."""
import json
from sources import OUT,BASE,original,save,sha

def main():
    p=OUT/'source/current-receipt-inputs.json';x=json.loads(p.read_text());assert len(x['complete_original_pages'])==2
    for page in x['complete_original_pages']:
        path=BASE/page['full_original_render_path'];assert path.stat().st_size==page['bytes'] and sha(path.read_bytes())==page['sha256']
    text=x['complete_original_pages'][1]['text_layer'];assert 'AFFIRMED' in text and 'Watson v. RNC' in text and '255-1' in text
    raw=original('sos-2026-current-absentee-info');positions=[]
    for phrase in ['postmarked on or before Election Day','November 3, 2026','five (5) business days','November 10, 2026','Optical Mark Scanning Voting Machine','after the polls have closed']:
        needle=phrase.encode();start=raw.find(needle);assert start>=0,phrase
        positions.append(dict(literal=phrase,raw_UTF8_byte_start=start,raw_UTF8_byte_end_exclusive=start+len(needle)))
    save(OUT/'source/current-receipt-readings.json',dict(
        status='pass_bounded_own_primary_original_reading',input_path=str(p.relative_to(BASE)),input_bytes=p.stat().st_size,input_sha256=sha(p.read_bytes()),
        court_original=dict(source_id='court-2026-fifth-circuit-remand',raw_sha256=sha(original('court-2026-fifth-circuit-remand')),case_number='24-60395',document='255-1',filed_date_literal='09/09/2026',actual_PDFpages_visually_read=[1,2],basis='Both complete original pages independently rendered and visually read in own2xgrayscale rasters; source identities and operative page2 wording read directly, not copied from coordinator proof',operative_PDFpage=2,disposition='District court judgment affirmed on Supreme Court remand in light of Watson v. RNC,146S.Ct.2165(2026)',publication_designation='Opinion not designated for publication;5thCir.R.47.5',qualification='Actual September9 appellate disposition only. Complete later mandate/rehearing/district docket and all state exceptions are outside this bounded reading.'),
        SOS_original=dict(source_id='sos-2026-current-absentee-info',raw_sha256=sha(raw),FAQ_sections_read=[4,9,10],mail_postmark_deadline_printed='2026-11-03',mail_receipt_deadline_printed='2026-11-10',mail_receipt_business_days_printed=5,in_person_method_printed='Absentee paper ballot scanned into Optical Mark Scanning Voting Machine; counted on election night after polls close',raw_source_positions=positions,basis='Own exact retained full HTML body/hash checked and instruction clauses read; current primary web page independently inspected',qualification='Printed ordinary absentee administrative guidance. No complete eligibility/cure/witness/UOCAVA or later-law audit; no outstanding Senate vote count, release cadence or inferred remaining pool.'),
        processing_observation='MuPDF emitted two No common ancestor in structure tree warnings while returning both complete page rasters/text; original bytes unchanged and both full pages visually inspected',
        original_entities_reused_read_only=True,duplicate_raw_originals_stored=False,live_pool_inferred=False,current_results_admitted=False,complete_later_legal_audit=False,current2026_geography_approved=False))
    print('PASS bounded current original court2pages + SOSFAQ4/9/10; source guidance only, no live pool')
if __name__=='__main__':main()
