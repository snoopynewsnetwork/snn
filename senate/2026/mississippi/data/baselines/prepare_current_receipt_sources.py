"""Reuse exact retained primary court/administrative bytes without duplication."""
import gzip,json
from pathlib import Path
import fitz
from sources import OUT,BASE,save,sha
ROOT=BASE.parents[2]
SPECS=[
 ('court-2026-fifth-circuit-remand','fifth-circuit-september9-remand','33d18b2c4e2114a5a0c3f501637251daa2bec1caf8d05ae7b7e2f8f92104a78b','ac0eb5911e6a3c6f6f95ffb655f33916380bbd3226b928a6140fc9484941f408'),
 ('sos-2026-current-absentee-info','sos-current-absentee-information','58a780e1a9401c979d1613826602e1234c8243e1d95c9bba187cbc9dcc290f47','54daf5de2238e698ff952e6827c9b0e659c4ee1bd56b8d910a16d96d2feec120')]
def main():
    references=[];inputs=[];pages=[];qa=OUT/'qa/current-receipt-originals';qa.mkdir(exist_ok=True)
    for sid,name,receipt_hash,raw_hash in SPECS:
        rp=BASE/'data/coordinator-legal-preparation'/(name+'.receipt.json');rb=rp.read_bytes();assert sha(rb)==receipt_hash;r=json.loads(rb)
        bp=ROOT/r['body']['stored_path'];stored=bp.read_bytes();raw=gzip.decompress(stored)
        assert len(stored)==r['body']['stored_bytes']<40000000 and sha(stored)==r['body']['stored_sha256']
        assert len(raw)==r['body']['raw_bytes'] and sha(raw)==raw_hash==r['body']['raw_sha256'] and r['status']==200
        parent=None
        if name.startswith('fifth-'):
            pp=BASE/'data/coordinator-legal-preparation/fifth-circuit-published-form-docket-query.receipt.json';pb=pp.read_bytes();parent=json.loads(pb)
            assert sha(pb)=='0ed6d0a08612784c796c9dcf0b990f47945feb76b1704a0be586213b6d38d44b'
            body=ROOT/parent['body']['stored_path'];pstored=body.read_bytes();praw=gzip.decompress(pstored);assert sha(pstored)==parent['body']['stored_sha256'] and sha(praw)==parent['body']['raw_sha256']
            assert b'/opinions/unpub/24/24-60395.0.pdf' in praw
            inputs.append(dict(role='actual_official_parent_form_response',receipt_path=str(pp.relative_to(BASE)),receipt_sha256=sha(pb),body_path=str(body.relative_to(BASE)),raw_sha256=sha(praw),stored_sha256=sha(pstored),requested_url=parent['requested_url'],final_url=parent['final_url']))
            references.append(dict(id='court-2026-fifth-circuit-form-query',method=parent['method'],url=parent['requested_url'],final_url=parent['final_url'],status=parent['status'],headers=parent['response_headers'],redirects=parent['redirects'],retrieved_at_utc=parent['started_at_utc'],completed_at_utc=parent['completed_at_utc'],raw_sha256=sha(praw),raw_bytes=len(praw),stored_sha256=sha(pstored),stored_bytes=len(pstored),path=str(body.relative_to(BASE)),storage='read_only_exact_shared_original_entity_reuse',reference_manifest=str(pp.relative_to(BASE)),reference_manifest_sha256=sha(pb),parent_source_id='actual official FifthCircuit opinions form',qualification='Complete actual docket-query parent response retained read-only by exact hash; not an exhaustive later docket/mandate search.'))
            doc=fitz.open(stream=raw,filetype='pdf');assert len(doc)==2
            for i,p in enumerate(doc,1):
                q=qa/f'fifth-circuit-september9-remand-p{i}.png';q.write_bytes(p.get_pixmap(matrix=fitz.Matrix(2,2),colorspace=fitz.csGRAY).tobytes('png'));assert q.stat().st_size<40000000
                pages.append(dict(source_id=sid,PDFpage=i,full_original_render_path=str(q.relative_to(BASE)),bytes=q.stat().st_size,sha256=sha(q.read_bytes()),render_scale=2,source_rect=list(p.rect),text_layer=p.get_text(),numeric_polygons_approved=False))
        inputs.append(dict(source_id=sid,receipt_path=str(rp.relative_to(BASE)),receipt_bytes=len(rb),receipt_sha256=sha(rb),body_path=str(bp.relative_to(BASE)),raw_bytes=len(raw),raw_sha256=sha(raw),stored_bytes=len(stored),stored_sha256=sha(stored),requested_url=r['requested_url'],final_url=r['final_url'],HTTP_status=r['status'],capture_started_at_utc=r['started_at_utc'],capture_completed_at_utc=r['completed_at_utc'],source_discovery_scope=r['discovery_scope']))
        references.append(dict(id=sid,url=r['requested_url'],final_url=r['final_url'],status=r['status'],headers=r['response_headers'],redirects=r['redirects'],retrieved_at_utc=r['started_at_utc'],completed_at_utc=r['completed_at_utc'],raw_sha256=sha(raw),raw_bytes=len(raw),stored_sha256=sha(stored),stored_bytes=len(stored),path=str(bp.relative_to(BASE)),storage='read_only_exact_shared_original_entity_reuse',reference_manifest=str(rp.relative_to(BASE)),reference_manifest_sha256=sha(rb),parent_source_id='actual retained official FifthCircuit docket-form response' if parent else 'current official SOS absentee information page',qualification='Own hash verification of complete retained original HTTP entity; original receipt preserves exact request/final URLs, headers, redirects and clocks. No duplicate raw original.'))
    save(OUT/'source/shared-primary-references.json',references)
    save(OUT/'source/current-receipt-inputs.json',dict(inputs=inputs,complete_original_pages=pages,qualification='Source acquisition/render preparation only; actual reading observations and exhaustive later-law/docket review are separate.'))
    print('Verified shared primary originals',len(references),'complete new original-page renders',len(pages))
if __name__=='__main__':main()
