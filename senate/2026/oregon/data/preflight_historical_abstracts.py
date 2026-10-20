"""Verify complete2020/2022 originals and their36-county Senate/governor tables."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess
import tempfile

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def originals():
    mf = json.loads((DATA/'news/manifest.json').read_bytes())
    def body(sid):
        source = next(s for s in mf if s['id'] == sid)
        stored = (DATA/'news'/source['asset']).read_bytes()
        raw = gzip.decompress(stored)
        assert (len(raw),sha(raw),sha(stored)) == (source['bytes'],source['raw_sha256'],source['stored_sha256'])
        return source,raw
    parts_path = DATA/'coordinator-2022-abstract-parts.json'
    parts = json.loads(parts_path.read_bytes())
    chunks = []
    offset = 0
    part_sources = []
    for p in parts['source_parts']:
        source,raw = body(p['source_id'])
        assert source['status'] == 206
        assert p['offset'] == offset and p['length'] == len(raw)
        assert source['headers']['Content-Range'] == f'bytes {offset}-{offset+len(raw)-1}/{parts["raw_bytes"]}'
        assert source['headers']['CM-Revision-Number'] == '1'
        assert source['headers']['Last-Modified'] == 'Mon, 29 Dec 2025 23:09:24 GMT'
        offset += len(raw)
        chunks.append(raw)
        part_sources.append(source)
    raw22 = b''.join(chunks)
    assert (len(raw22),sha(raw22)) == (462872,'8d04f156cc9df40109a0275ee76271fb383d7bf0d88726b5661f54985523667f')
    assert len(raw22) == parts['raw_bytes'] and sha(raw22) == parts['raw_sha256']
    prefixes = []
    for sid in ['sos-2022-actual-abstract-record13735454','sos-2022-record13735454-byte-range-prefix-retry']:
        source,raw = body(sid)
        assert source['status'] == 500 and raw22[:len(raw)] == raw
        prefixes.append(source)
    source20,raw20 = body('sos-2020-actual-abstract-stream13735450')
    assert source20['status'] == 200
    assert (len(raw20),sha(raw20)) == (588518,'fc98c9712c09b0e9179e1208e70a754b56bf327dea22a1fe92194ee1f64dd474')
    return {'2020':raw20,'2022':raw22}, {'2020':source20,'2022':{
        'parts_manifest_path':str(parts_path.relative_to(ROOT)),'reconstruction':parts,
        'original_part_response_pins':part_sources,'retained_incomplete_HTTP500_observations':prefixes}}


def main():
    bodies,pins = originals()
    texts = {}
    infos = {}
    for year,raw in bodies.items():
        assert raw.startswith(b'%PDF') and b'%%EOF' in raw[-100:]
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'original.pdf'
            p.write_bytes(raw)
            infos[year] = subprocess.check_output(['pdfinfo',str(p)]).decode()
            texts[year] = subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode().split('\f')
        assert re.search(r'Pages:\s+'+('33' if year == '2020' else '30')+r'\b',infos[year])
    checks = []
    county_set = None
    for year,page,names,totals,heading in [
        ('2020',2,['Perkins Jo Rae (R)','Merkley Jeff (D)','Taher Ibrahim A (PG)','Dye Gary (L)','Misc.'],
         [912814,1321047,42239,42747,2402],'US Senator'),
        ('2022',1,['Perkins Jo Rae (R)','Pulju Dan (PG)','Wyden Ron (D)','Henry Chris (P)','Misc.'],
         [788991,23454,1076424,36883,2197],'US Senator'),
        ('2022',4,['Kotek Tina (D)','Smith Donice Noelle (C)','Noble R Leon (L)',
                   'Johnson Betsy (NAV)','Drazan Christine (R)','Misc.'],
         [917074,8051,6867,168431,850347,2113],'Governor')]:
        text = texts[year][page-1]
        assert heading in [line.strip() for line in text.splitlines()]
        n = len(names)
        pattern = re.compile(r'\s*([A-Za-z][A-Za-z ]*?)\s+'+r'\s+'.join([r'([\d,]+)']*n)+r'\s*')
        rows = []
        footer = []
        for ordinal,line in enumerate(text.splitlines(),1):
            match = pattern.fullmatch(line)
            if not match:
                continue
            label = match[1].strip()
            record = {'PDF_page':page,'text_line':ordinal,'raw_line':line,'county_literal':label,
                      'candidate_values':[int(v.replace(',','')) for v in match.groups()[1:]]}
            (footer if label.upper() == 'TOTAL' else rows).append(record)
        assert len(rows) == len({r['county_literal'] for r in rows}) == 36
        assert len(footer) == 1 and footer[0]['candidate_values'] == totals
        assert [sum(r['candidate_values'][j] for r in rows) for j in range(n)] == totals
        labels = {r['county_literal'] for r in rows}
        if county_set is None:
            county_set = labels
        assert labels == county_set
        checks.append({'year':year,'office_literal':heading,'candidate_column_order_read_from_original':names,
                       'source_county_rows':rows,'state_footer':footer[0],
                       'candidate_positions':36*n,'state_total_including_source_Misc':sum(totals)})
    previews = json.loads((DATA/'news/historical-abstract-rendered-pages.json').read_bytes())
    assert len(previews) == 3
    for p in previews:
        b = (ROOT/p['path']).read_bytes()
        assert sha(b) == p['sha256'] and len(b) == p['bytes']
        assert p['original_source_sha256'] == sha(bodies[p['year']])
    output = {'status':'pass_original_2020_2022_county_controls_with_explicit_range_reconstruction_no_native_acceptance',
        'original_pins':pins,'PDF_info_literal':infos,'county_candidate_checks':checks,
        'total_county_candidate_positions':sum(c['candidate_positions'] for c in checks),
        'complete_original_pages_rendered_and_visually_inspected':previews,
        'scope':'All36 source county rows and every candidate/Misc cell in the three selected tables sum exactly to printed state footers. The2022 complete original is reconstructed from three contiguous HTTP206 ranges at the publicly advertised Accept-Ranges route, with response metadata and both incomplete500 prefixes retained. No duplicate complete PDF is stored. One earlier unretained prefix request is disclosed in the retry receipt. The2020 original follows the actual public viewer pdfjsProcessing URL. Earlier discovery record IDs11125187/11125222/7888043 are voter-registration documents, not these candidate abstracts. Misc. remains source-scoped and is not automatically valid named write-ins. Full native precinct, candidate-method, eligibility, current reporting/geography and exact priority are separate worker tasks.'}
    (DATA/'coordinator-historical-abstract-preflight.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'status':output['status'],'candidate_positions':output['total_county_candidate_positions'],
                      'state_controls':{c['year']+'_'+c['office_literal']:c['state_total_including_source_Misc'] for c in checks}}))


if __name__ == '__main__':
    main()
