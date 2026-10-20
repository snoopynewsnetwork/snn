"""Reconstruct the complete original Somerset page and retain literal caption."""
from pathlib import Path
import gzip
import hashlib
import json
import fitz

S = Path(__file__).resolve().parents[1]
D = S / 'data/coordinator-somerset-caption-review'
D.mkdir(exist_ok=True)
sid = '2024-official-general-results-president-somerset'
source = S / ('data/turnout/source/' + sid + '.body.gz')
receipt_path = S / ('data/turnout/source/' + sid + '.receipt.json')
receipt = json.loads(receipt_path.read_bytes())
stored = source.read_bytes()
raw = gzip.decompress(stored)
assert hashlib.sha256(stored).hexdigest() == receipt['stored_sha256']
assert hashlib.sha256(raw).hexdigest() == receipt['raw_sha256']
assert len(raw) == receipt['raw_bytes'] == 10778
doc = fitz.open(stream=raw, filetype='pdf')
assert len(doc) == 1
page = doc[0]
words = page.get_text('words')
caption = 'Robert F. Kenndy Jr.'
assert caption in page.get_text()
png = D / 'president-original-page1.png'
page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False).save(png)


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


out = dict(status='original_literal_caption_preserved_with_complete_page_evidence',
           complete_original=pin(source), original_raw_bytes=len(raw), original_raw_sha256=hashlib.sha256(raw).hexdigest(),
           full_original_receipt=receipt, receipt_pin=pin(receipt_path), complete_render=pin(png),
           literal_caption=caption, other_publications_caption='Robert F. Kennedy Jr.',
           word_positions=[dict(x0=w[0], y0=w[1], x1=w[2], y1=w[3], text=w[4]) for w in words if w[4] in ('Robert', 'F.', 'Kenndy', 'Jr.')],
           actual_visual_scope='Coordinator actually inspected this complete original page render; the header visibly says Kenndy. No browser render claim.',
           qualification='Separate source caption and consistent candidate-column schema display; no source relabel, candidate vote repair, new legal identity or current join. Full raw header was already retained by both producers.')
(D / 'review.json').write_text(json.dumps(out, indent=2)+'\n')
print(pin(D/'review.json'))
