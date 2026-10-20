"""Independent bounded text/render audit of two complete primary court orders."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess
import sys
import fitz

S = Path(__file__).resolve().parents[1]
SOURCE = S/'data/results-sources'
D = S/'data/coordinator-current-order-review'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def main():
    D.mkdir(exist_ok=True)
    results = []
    for sid, pages, expected in [('usps-injunction', [47, 48], 49), ('scotus-eo-2026-stay', [1], 37)]:
        rp = SOURCE/'source/http'/f'{sid}.json'
        receipt = json.loads(rp.read_bytes())
        response = receipt['redirects'][-1]
        record = response['body']
        p = SOURCE/record['path']
        z = p.read_bytes()
        b = gzip.decompress(z)
        assert len(z) == record['stored_bytes'] and sha(z) == record['stored_sha256']
        assert len(b) == record['raw_bytes'] and sha(b) == record['raw_sha256']
        assert response['status'] == 200 and b.startswith(b'%PDF')
        text = subprocess.run(['pdftotext', '-layout', '-', '-'], input=b, capture_output=True, check=True).stdout
        tp = D/(sid+'.complete-layout.txt.gz')
        tp.write_bytes(gzip.compress(text, mtime=0))
        doc = fitz.open(stream=b, filetype='pdf')
        assert len(doc) == expected
        renders = []
        for page in pages:
            out = D/f'{sid}-original-page{page}.png'
            doc[page-1].get_pixmap(matrix=fitz.Matrix(1.3, 1.3), alpha=False).save(out)
            renders.append(dict(original_page=page, complete_original_page_render=pin(out)))
        if sid == 'usps-injunction':
            assert b'Document 156' in text and b'Filed 09/04/26' in text
            assert b'DMM Section 705.24.3.1' in text and b'November 3, 2026' in text
            assert b'request for a stay pending appeal is DENIED' in text
        else:
            assert b'26A124' in text and b'26A139' in text and b'August 24, 2026' in text
            assert b'grant' in text and b'the stay' in text
        results.append(dict(id=sid, source_receipt=pin(rp), complete_original_stored_body=pin(p),
                            raw_bytes=len(b), raw_sha256=sha(b), source_url=receipt['requested_url'],
                            original_source_retrieval_UTC=receipt['started_utc'], original_pages=len(doc),
                            complete_text_derivative=pin(tp), selected_renders=renders))
    out = dict(status='pass_bounded_complete_order_text_and_selected_original_render_audit', documents=results,
               scoped_observations=[
                   'Aug24SCOTUS26A124/26A139 grants a stay of the underlying executive-order injunction; the percuriam discusses standing/ripeness and EO14399. It is not the later Sept4 USPS-final-rule preliminary injunction.',
                   'Sept4Dkt156 in1:26-cv-13917-IT/related11549 is a49page order granting a preliminary injunction as to enumerated DMM provisions for elections before/onNov3,2026; it denies a trial-level stay request and dissolves theAug27TRO. This does not prove no later appellate action.'
               ],
               acquisition_scope='Independent text extraction and render from exactly pinned worker-retained complete original bodies; no new successful HTTP retrieval claimed. Coordinator web-open attempts to both URLs returned403; no missing web response headers/body invented.',
               actual_visual_scope='Record actual selected-page visual review only after viewing the three generated complete original-page images; full text extraction is not full visual inspection.',
               later_docket_or_current_operative_exhaustiveness=False,
               producer_mutation_or_import=False)
    (D/'review-pending-visual.json').write_text(json.dumps(out, indent=2)+'\n')
    if '--record-viewed' in sys.argv:
        out['actual_visual_scope'] = 'Coordinator actually viewed all three complete generated original-page images in this review: Sept4Dkt156 pages47/48 and Aug24SCOTUS firstpage. No entire49/37page visual or browser-render claim.'
        out['source_render_warnings'] = 'MuPDF emitted format error: No common ancestor in structure tree, three times while rendering. Original bytes unchanged; all selected complete images were actually viewed and legible.'
        out['status'] = 'pass_bounded_order_text_and_actual_three_selected_original_page_views'
        (D/'review.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'documents': len(results), 'generated_selected_pages': 3, 'pending_visual': str(D/'review-pending-visual.json')}))


if __name__ == '__main__':
    main()
