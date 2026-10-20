"""Render complete acquired original PDF pages; originals remain once by hash."""
from pathlib import Path
import gzip
import hashlib
import json
import fitz

S = Path(__file__).resolve().parents[2]
O = S / 'data/news/coordinator-map-preparation'


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def main():
    rows = json.loads((O / 'acquisition-complete-v1.json').read_bytes())
    output = []
    for row in rows:
        if not row['id'].startswith('map-') or row['status'] != 200:
            continue
        raw = gzip.decompress((S / row['asset_path']).read_bytes())
        assert hashlib.sha256(raw).hexdigest() == row['raw_sha256']
        doc = fitz.open(stream=raw, filetype='pdf')
        directory = O / 'rendered' / row['id']
        directory.mkdir(parents=True, exist_ok=True)
        pages = []
        for i, page in enumerate(doc):
            scale = 1800 / max(page.rect.width, page.rect.height)
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            path = directory / f'p{i + 1:04}-complete.png'
            pix.save(str(path))
            text = directory / f'p{i + 1:04}-text.txt.gz'
            text.write_bytes(gzip.compress(page.get_text().encode(), mtime=0))
            pages.append(dict(page=i + 1, original_page_rect=list(page.rect),
                              render_scale=scale, complete_original_page=pin(path),
                              extracted_text=pin(text), automatically_rendered=True,
                              independently_viewed=False))
        output.append(dict(source_id=row['id'], raw_bytes=len(raw),
                           raw_sha256=row['raw_sha256'], pages=pages,
                           qualification='Text extraction and rendering are separate from actual visual inspection and geographic approval.'))
    p = O / 'render-receipts.json'
    p.write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps([dict(id=r['source_id'], pages=len(r['pages'])) for r in output]))


if __name__ == '__main__':
    main()
