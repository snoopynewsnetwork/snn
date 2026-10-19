"""Freeze source-position hints without importing another reading's votes or labels.

The independent baseline's machine block aid is only a locator. Its OCR text,
numeric values, source-native labels and inferred roles are deliberately absent
from the output. Original Mississippi PDFs remain the transcription authority.
"""
import gzip
import json
from acquire_sources import BASE,OUT,receipts,sha,savejson

ROOT=BASE/'data/baselines/extracts/2018-blocks'
TARGET=OUT/'source/2018-vote-free-targets-v1.json'

def main():
    sources=[];pins=[]
    by_id={r['id']:r for r in receipts}
    for path in sorted(ROOT.glob('*.json.gz')):
        stored=path.read_bytes();raw=gzip.decompress(stored);source=json.loads(raw)
        sid=source['source_id'];assert sid==path.name[:-8] and sid in by_id
        assert source['raw_sha256']==by_id[sid]['raw_sha256']
        pins.append(dict(path=str(path.relative_to(BASE)),stored_sha256=sha(stored),
                         stored_bytes=len(stored),raw_sha256=sha(raw),raw_bytes=len(raw)))
        pages=[]
        for page in source['pages']:
            assert set(page)>=set(['page','render_size','rotation_ccw','deskew_angle_ccw','columns','fields'])
            columns=[]
            for col in page['columns']:
                columns.append(dict(source_column=col['source_column'],header_box=col['header_box']))
            fields=[]
            for field in page['fields']:
                fields.append(dict(candidate=field['candidate'],row_source_ordinal=field['row_source_ordinal'],
                                   candidate_label_box=field['label_box'],
                                   cells=[dict(source_column=c['source_column'],box=c['box']) for c in field['cells']]))
            pages.append(dict(page=page['page'],render_size=page['render_size'],
                              rotation_ccw=page['rotation_ccw'],deskew_angle_ccw=page['deskew_angle_ccw'],
                              columns=columns,fields=fields))
        sources.append(dict(source_id=sid,source_raw_sha256=source['raw_sha256'],
                            locator_status='machine_geometry_only_unaccepted',pages=pages))
    assert len(sources)==164
    counts=dict(source_views=len(sources),pages=sum(len(s['pages']) for s in sources),
                candidate_rows=sum(len(p['fields']) for s in sources for p in s['pages']),
                candidate_cell_targets=sum(len(f['cells']) for s in sources for p in s['pages'] for f in p['fields']),
                empty_machine_views=[s['source_id'] for s in sources if not s['pages']])
    output=dict(scope='Vote-free independent targeting only. Machine aid boxes may miss rows or columns; no vote, zero, header, role, native ID, current geometry or numeric polygon accepted.',
                source_aid_pins=pins,counts=counts,sources=sources)
    forbidden=('raw_ocr','value','values','native_label_ocr','label_literal','role','unit_type','party_literal')
    as_text=json.dumps(output)
    assert all('"'+x+'"' not in as_text for x in forbidden)
    savejson(TARGET,output)
    print('Vote-free 2018 locator',counts,'SHA256',sha(TARGET.read_bytes()))

if __name__=='__main__':main()
