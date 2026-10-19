"""Freeze only physical source targeting boxes from immutable peer142v2.

The initial78 boxes must be byte-semantic identical to the earlier value-free
hint. This new hint carries no votes, labels, candidate names, roles or IDs.
"""
import gzip
import json
from acquire_sources import BASE, OUT, receipts, savejson, sha

SNAP=BASE/'data/baselines/source/native-2018-142views-v2/snapshot.json'
SNAP_SHA='9fba26e5f69b1e844b62e1b262b48701daf0ddef3cf747c83d610d12202036fe'
OLD=OUT/'source/2018-frozen78-vote-free-position-hints-v1.json'
DEST=OUT/'source/2018-peer142-new64-vote-free-position-hints-v1.json'


def make_hint(source):
    pages=[]
    for page in source['pages']:
        columns=[{'source_column':c['source_column'],'header_bounds':c['header_bounds']}
                 for c in page['columns']]
        rows=[{'source_row_ordinal':i+1,'candidate_row_bounds':field['row_bounds']}
              for i,field in enumerate(page['fields'])]
        pages.append({'source_pdf_page':page['page'],'render_size':page['render_size'],
                      'physical_columns':columns,'candidate_row_positions':rows})
    return {'source_id':source['source_id'],'source_raw_sha256':source['raw_sha256'],
            'pages':pages}


def main():
    snap_raw=SNAP.read_bytes();assert sha(snap_raw)==SNAP_SHA
    snap=json.loads(snap_raw)
    pin=next(x for x in snap['pins'] if x['original_path']=='data/baselines/native-2018-original-readings.json')
    stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored)
    assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256']
    assert len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
    peer=json.loads(raw);assert len(peer['sources'])==142
    old=json.loads(OLD.read_text());old_by={s['source_id']:s for s in old['sources']}
    originals={r['id']:r['raw_sha256'] for r in receipts}
    newer=[]
    for source in peer['sources']:
        sid=source['source_id'];assert originals[sid]==source['raw_sha256']
        hint=make_hint(source)
        if sid in old_by:
            assert hint==old_by[sid],sid
        else:
            newer.append(hint)
    assert len(newer)==64
    doc={'scope':'Only position boxes/source IDs/raw hashes from immutable peer142v2 newly added beyond prior78; no peer votes, labels, roles, candidate names or IDs. OCR of our exact originals remains diagnostic until full source review.',
         'peer_snapshot_path':str(SNAP.relative_to(BASE)),
         'peer_snapshot_sha256':SNAP_SHA,
         'peer_full_ledger_raw_sha256':pin['original_sha256'],
         'peer_full_ledger_stored_sha256':pin['stored_sha256'],
         'old78_hint_sha256':sha(OLD.read_bytes()),
         'new_source_views':64,
         'new_original_pages':sum(len(s['pages']) for s in newer),
         'new_tentative_candidate_positions':sum(len(p['physical_columns'])*len(p['candidate_row_positions']) for s in newer for p in s['pages']),
         'sources':newer}
    if DEST.exists():assert json.loads(DEST.read_text())==doc
    else:savejson(DEST,doc)
    print('New value-free2018 source hint',len(newer),doc['new_original_pages'],
          doc['new_tentative_candidate_positions'],sha(DEST.read_bytes()))


if __name__=='__main__':main()
