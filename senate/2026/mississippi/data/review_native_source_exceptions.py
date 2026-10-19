"""Record bounded original-source disagreements without changing worker evidence."""
from pathlib import Path
import gzip
import hashlib
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
NAMES = ['Ty_Pinkins','Roger_F_Wicker']
TUNICA = [[30,226,202,7,225,168,129,212,126,169,195,108],
          [38,95,10,60,47,27,265,44,111,34,50,46]]
KEMPER = [[348,74,24,42,119,89,234,259,74,130,321,164,208,148],
          [153,228,36,183,57,17,126,208,182,73,123,176,134,128]]
ITAWAMBA = {3:[[151,70,39,20,12,33,31,49,21,43,100],
                [955,421,524,155,159,225,328,694,189,575,294]],
             4:[[14,26,15,5,2,5,106,128,3,36,39],
                [120,421,124,87,95,84,278,477,178,629,590]]}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}


def snapshot():
    dest = DATA/'coordinator-qa/native-source-exceptions-snapshot-1.json.gz'
    if not dest.exists():
        source = DATA/'turnout/native-reviewed-2024.json'
        raw = source.read_bytes()
        ledger = json.loads(raw)
        assert source.read_bytes() == raw
        ids = ['sos-2024-county-tunica','sos-2024-county-kemper',
               'sos-2024-county-itawamba','sos-2024-county-lincoln']
        body = {'working_turnout_ledger_pin':pin(source),
                'source_objects':{sid:ledger['sources'][sid] for sid in ids}}
        for key,relative in [
            ('baseline_manual_repairs','baselines/replay-60views-manual-repairs.json'),
            ('baseline_header_disagreements','baselines/replay-60views-original-label-disagreements.json'),
            ('baseline_Itawamba_full_row_readings','baselines/itawamba-original-row-readings.json')]:
            p = DATA/relative
            b = p.read_bytes()
            body[key] = {'pin':pin(p),'reading':json.loads(b)}
            assert p.read_bytes() == b
        dest.write_bytes(gzip.compress((json.dumps(body,indent=2)+'\n').encode(),mtime=0))
    return json.loads(gzip.decompress(dest.read_bytes())),pin(dest)


def main():
    snap,snap_pin = snapshot()
    sources = snap['source_objects']
    manifest = json.loads((DATA/'coordinator-qa/tunica-kemper-2024-renders.json').read_bytes())
    manifest += json.loads((DATA/'coordinator-qa/itawamba-2024-original-renders.json').read_bytes())
    manifest += [json.loads((DATA/'coordinator-qa/lincoln-2024-original-render.json').read_bytes())]
    for r in manifest:
        b = (ROOT/r['path']).read_bytes()
        assert sha(b) == r['sha256'] and len(b) == r['bytes']
        meta = r['source_pin']
        stored = (ROOT/meta['path']).read_bytes()
        assert sha(stored) == meta['stored_sha256']
        assert sha(gzip.decompress(stored)) == meta['raw_sha256'] == sources[meta['id']]['raw_sha256']
    tunica = sources['sos-2024-county-tunica']
    native = [c for p in tunica['pages'] for c in p['columns'] if c['role']=='native_reporting_constituent']
    assert len(native) == 12
    for name,values in zip(NAMES,TUNICA):
        assert [c[name] for c in native] == values
    assert [sum(v) for v in TUNICA] == [1797,827]
    totals = [c for p in tunica['pages'] for c in p['columns'] if c['role']=='source_TOTAL']
    assert len(totals) == 1 and [totals[0][n] for n in NAMES] == [1797,827]
    nulls = [c for p in tunica['pages'] for c in p['columns'] if c['role']=='unused_template_column']
    assert len(nulls) == 9 and all(c[n] is None for c in nulls for n in NAMES)
    primary = json.loads((DATA/'coordinator-county-primary-review.json').read_bytes())
    county = next(c['source_candidates'] for c in primary['full82_descending_order'] if c['county_literal']=='Tunica')
    assert county == {'Ty Pinkins':1798,'Roger F. Wicker':827}
    kemper = sources['sos-2024-county-kemper']
    pages = {p['page']:p for p in kemper['pages']}
    assert list(pages) == [6,7,8]
    assert all(c['role']=='parallel_native_observation' for c in pages[6]['columns'])
    native = [c for p in kemper['pages'] for c in p['columns'] if c['role']=='native_reporting_constituent']
    assert len(native) == 14
    for name,values in zip(NAMES,KEMPER):
        assert [c[name] for c in native] == values
        assert [c[name] for c in pages[6]['columns']] == values[:11]
    assert [c['label_literal'] for c in pages[6]['columns']] == [c['label_literal'] for c in pages[7]['columns']]
    assert [sum(v) for v in KEMPER] == [2234,1824]
    totals = [c for p in kemper['pages'] for c in p['columns'] if c['role']=='source_TOTAL']
    assert len(totals) == 1 and [totals[0][n] for n in NAMES] == [2234,1824]
    frozen = json.loads((DATA/'turnout/qa/milestones/native-2024-60views/native-reviewed-2024.json').read_bytes())
    itawamba = frozen['sources']['sos-2024-county-itawamba']
    for page_number,values in ITAWAMBA.items():
        page = next(p for p in itawamba['pages'] if p['page']==page_number)
        for name,row in zip(NAMES,values):
            assert [c[name] for c in page['columns']] == row
    repairs = [r for r in snap['baseline_manual_repairs']['reading']['readings']
               if r['source_id']=='sos-2024-county-itawamba']
    assert len(repairs) == 6
    for r in repairs:
        page = next(p for p in itawamba['pages'] if p['page']==r['page'])
        column = next(c for c in page['columns'] if c['source_column']==r['source_column'])
        assert r['candidate'] == 'Ty Pinkins'
        assert r['candidate_bounds'] == column['candidate_bounds'][r['candidate']]
        assert r['accepted_reading_bounds'] != r['candidate_bounds']
        assert r['value'] == ITAWAMBA[r['page']][0][r['source_column']-1]
    lincoln = frozen['sources']['sos-2024-county-lincoln']
    column = next(c for p in lincoln['pages'] if p['page']==3 for c in p['columns'] if c['source_column']==11)
    assert column['label_literal'] == 'Forestry'
    assert [column[n] for n in NAMES] == [179,364]
    disagreement = next(r for r in snap['baseline_header_disagreements']['reading']['disagreements']
                        if r['source_id']=='sos-2024-county-lincoln')
    assert disagreement['own_original_literal']=='Forrestry' and disagreement['frozen_peer_literal']=='Forestry'
    rotated = [pin(DATA/'coordinator-qa'/name) for name in [
        'itawamba-2024-original-p3-upright.png','itawamba-2024-original-p4-upright.png',
        'lincoln-2024-original-p3-upright.png']]
    output = {'status':'pass_bounded_original_readings_with_retained_source_geometry_and_literal_disagreements',
        'frozen_issue_snapshot':snap_pin,'original_complete_page_renders':manifest,
        'orthogonally_rotated_full_page_views':rotated,
        'Tunica':{'PDF3_ESS_named_candidates':[1798,827],'PDF7_8_SEMS_native_vectors':TUNICA,
                  'SEMS_printed_TOTAL':[1797,827],'SEMS_minus_ESS_and_CSV':[-1,0],
                  'source_ES&S_report_clock_literal':'11/15/2024 3:18 PM, zone unspecified',
                  'generic_writein_ESS':3,'ESS_source_total_votes_cast':2628,
                  'ESS_contest_total_ballots':2745,
                  'qualification':'No native unit receives the missing Pinkins vote; generic marks are not allocated or declared legally valid named write-ins. Same retained PDF contains both scopes; no release chronology or cause follows.'},
        'Kemper':{'parallel_unofficial_PDF6_printed_page':1,'official_PDF7_printed_page':2,
                  'official_PDF8_printed_page':3,'parallel_candidate_positions':22,
                  'additive_native_constituents':14,'official_native_vectors':KEMPER,
                  'printed_TOTAL':[2234,1824],
                  'qualification':'All11 parallel first-page headers and both Senate vectors equal the official page, but all original observations remain. PDF6 is non-additive; count only disjoint official PDF7–8 for this source view. No chronology or current-geography equivalence inferred.'},
        'Itawamba':{'complete_original_Senate_rows':ITAWAMBA,'numeric_candidate_positions':44,
                    'explicit_target_vs_accepted_reading_box_differences':repairs,
                    'qualification':'Own full-original readings confirm Clay49 and Kirkville36. Six expanded reading boxes remain distinct from immutable targeting hints. Numeric agreement is not exact accepted-box agreement or general glyph-coverage validation.'},
        'Lincoln':{'PDF_page':3,'physical_column':11,'original_header_literal':'Forrestry',
                   'frozen60_header_literal':'Forestry','named_candidate_values':[179,364],
                   'qualification':'The double-r spelling is visible on the original. This is a transcription/literal disagreement, not a whitespace alias. Frozen bytes remain unchanged; working correction requires explicit history. No vote or geography change inferred.'},
        'scope':'Coordinator independently rendered/read the bounded original pages identified above. Other source pages/candidate fields and the full statewide/native/Pres/method gates remain open. Original source clocks, candidate control discrepancies, repeated observations and reading-box expansions remain explicit; none is repaired by residual allocation or an assumed geographic join.'}
    (DATA/'coordinator-native-source-exceptions-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'status':output['status'],'Tunica_delta':[-1,0],
                      'Kemper_parallel_positions':22,'Itawamba_numeric_positions':44,
                      'expanded_reading_boxes':len(repairs),'Lincoln_original_literal':'Forrestry'}))


if __name__ == '__main__':
    main()
