"""Freeze only physical targeting geometry from the peer's immutable78 witness.

No peer votes, candidate names, native labels, parsed IDs or roles enter this
hint. The subsequent OCR reads our exact SOS original PDFs, never peer cells.
"""
import gzip
import json
from acquire_sources import BASE, OUT, receipts, sha, savejson

SNAP = BASE / 'data/baselines/source/native-2018-78views-v1/snapshot.json'
SNAP_SHA = '4df50caded4d9a1cdfd46081422e36002439b10aea28cfab1fb6dcf00f34621c'
DEST = OUT / 'source/2018-frozen78-vote-free-position-hints-v1.json'


def main():
    snap_raw = SNAP.read_bytes(); assert sha(snap_raw) == SNAP_SHA
    snap = json.loads(snap_raw)
    pin = next(x for x in snap['pins'] if x['original_path'] ==
               'data/baselines/native-2018-original-readings.json')
    stored = (BASE / pin['stored_path']).read_bytes(); raw = gzip.decompress(stored)
    assert len(stored) == pin['stored_bytes'] and sha(stored) == pin['stored_sha256']
    assert len(raw) == pin['original_bytes'] and sha(raw) == pin['original_sha256']
    peer = json.loads(raw)
    source_hashes = {r['id']: r['raw_sha256'] for r in receipts}
    sources = []
    for source in peer['sources']:
        sid = source['source_id']; assert source_hashes[sid] == source['raw_sha256']
        pages = []
        for page in source['pages']:
            columns = [dict(source_column=c['source_column'],
                            header_bounds=c['header_bounds']) for c in page['columns']]
            rows = [dict(source_row_ordinal=i+1, candidate_row_bounds=f['row_bounds'])
                    for i, f in enumerate(page['fields'])]
            assert [c['source_column'] for c in columns] == list(range(1, len(columns)+1))
            assert len(rows) == (4 if sid.startswith('sos-2018-county-') else 2)
            pages.append(dict(source_pdf_page=page['page'], render_size=page['render_size'],
                              physical_columns=columns, candidate_row_positions=rows))
        sources.append(dict(source_id=sid, source_raw_sha256=source['raw_sha256'],
                            pages=pages))
    assert len(sources) == 78 and len({s['source_id'] for s in sources}) == 78
    page_count = sum(len(s['pages']) for s in sources)
    positions = sum(len(p['physical_columns'])*len(p['candidate_row_positions'])
                    for s in sources for p in s['pages'])
    assert page_count == 144 and positions == 4752, (page_count, positions)
    output = dict(scope='Immutable value-free physical location hint for fresh OCR of exact SOS 2018 original PDFs. Peer votes, candidate names, native labels, roles and IDs excluded. Rectangles are targeting aids, not accepted source/geographic boxes.',
                  peer_snapshot_path=str(SNAP.relative_to(BASE)),
                  peer_snapshot_sha256=SNAP_SHA,
                  peer_full_ledger_raw_sha256=pin['original_sha256'],
                  peer_full_ledger_stored_sha256=pin['stored_sha256'],
                  source_views=78, original_pages=page_count,
                  tentative_candidate_cell_positions=positions, sources=sources)
    assert set(output)=={'scope','peer_snapshot_path','peer_snapshot_sha256',
                         'peer_full_ledger_raw_sha256','peer_full_ledger_stored_sha256',
                         'source_views','original_pages','tentative_candidate_cell_positions','sources'}
    for s in sources:
        assert set(s)=={'source_id','source_raw_sha256','pages'}
        for p in s['pages']:
            assert set(p)=={'source_pdf_page','render_size','physical_columns','candidate_row_positions'}
            assert all(set(c)=={'source_column','header_bounds'} for c in p['physical_columns'])
            assert all(set(r)=={'source_row_ordinal','candidate_row_bounds'} for r in p['candidate_row_positions'])
    if DEST.exists():
        previous=json.loads(DEST.read_text()); assert previous==output
    else:
        savejson(DEST, output)
    print('Frozen value-free2018 peer geometry:', len(sources), 'source views,',
          page_count, 'pages,', positions, 'tentative candidate cells;', sha(DEST.read_bytes()))


if __name__ == '__main__':
    main()
