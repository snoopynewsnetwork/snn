"""Independent Poppler extraction and bounded original-glyph Union checks."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
import tempfile

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
DEST = DATA / 'coordinator-qa/union-profile-review'
NAMES = ['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump',
         'Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski',
         'Ty Pinkins','Roger F. Wicker']
# Read from independently rendered complete original pages/statistics panels.
MANUAL = {(20,'senate_contest_total'):1055, (20,'voter_turnout_percent'):73.57,
          (24,'voter_turnout_percent'):73.72, (26,'voter_turnout_percent'):81.67,
          (34,'voter_turnout_percent'):67.69, (46,'voter_turnout_percent'):74.30,
          (48,'registration_total'):1703}
SUMMARY = dict(zip(NAMES,[1807,12,17,12,10559,4,6,52,9,1779,10484])) | {
    'president_generic_write_in':18, 'president_contest_total':12533,
    'senate_generic_write_in':84, 'senate_contest_total':12533,
    'registration_total':17084, 'ballots_cast_total':12533, 'ballots_blank':1}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(path):
    b = path.read_bytes()
    return {'path':str(path.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}


def frozen(path):
    target = DEST / (path.name+'.gz')
    if not target.exists():
        b = path.read_bytes()
        assert path.read_bytes() == b
        target.write_bytes(gzip.compress(b,mtime=0))
    return gzip.decompress(target.read_bytes()),pin(target)


def number(line):
    token = line.split()[-1]
    if re.fullmatch(r'\d+(?:\.\d+)?%',token):
        return float(token[:-1])
    if re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)',token):
        return int(token.replace(',',''))
    return None


def parse(text):
    before,pres = text.split('President United States',1)
    pres,sen = pres.split('Senate United States',1)
    sen = sen.split('1st Congressional',1)[0]
    named = [line for line in pres.splitlines() if re.match(r'^\s*[DLGCRI1]\s+',line)]
    senate = [line for line in sen.splitlines() if re.match(r'^\s*[DR]\s+',line)]
    assert len(named) == 9 and len(senate) == 2
    fields = dict(zip(NAMES,named+senate))
    for prefix,section in [('president',pres),('senate',sen)]:
        for suffix,label in [('generic_write_in','write-in totals'),('contest_total','contest totals')]:
            lines = [line for line in section.splitlines() if label in line.lower()]
            assert len(lines) == 1
            fields[prefix+'_'+suffix] = lines[0]
    for name,pattern in [('registration_total','Registered Voters'),('ballots_cast_total','Ballots Cast.*Total'),
                         ('ballots_blank','Ballots Cast.*Blank'),('voter_turnout_percent',r'Voter\s*Turnout')]:
        lines = [line for line in before.splitlines() if re.search(pattern,line)]
        assert len(lines) == 1
        fields[name] = lines[0]
    assert len(fields) == 19
    return {k:{'raw_line':line,'raw_token':line.split()[-1],'parsed_value':number(line)} for k,line in fields.items()}


def main():
    DEST.mkdir(exist_ok=True)
    ledger_raw,ledger_pin = frozen(DATA / 'turnout/native-profile-union-readings.json')
    csv_raw,csv_pin = frozen(DATA / 'turnout/native-profile-fields.csv')
    controls_raw,controls_pin = frozen(DATA / 'turnout/native-profile-controls.json')
    ledger = json.loads(ledger_raw)
    controls = next(r for r in json.loads(controls_raw)['checks'] if r['source_id'] == ledger['source_id'])
    meta = next(s for s in json.loads((DATA / 'turnout/source/acquisition.json').read_bytes()) if s['id'] == ledger['source_id'])
    stored = (ROOT / meta['path']).read_bytes()
    raw = gzip.decompress(stored)
    assert sha(raw) == meta['raw_sha256'] == ledger['raw_sha256'] and sha(stored) == meta['stored_sha256']
    assert len(ledger['profiles']) == 20 and [p['source_page'] for p in ledger['profiles']] == list(range(16,55,2))
    own_text = {}
    with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
        f.write(raw)
        f.flush()
        for p in ledger['profiles']:
            text = subprocess.run(['pdftotext','-layout','-f',str(p['source_page']),'-l',str(p['source_page']),f.name,'-'],
                                  check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode()
            own_text[p['source_page']] = {'text':text,'fields':parse(text)}
    comparisons = []
    direct = 0
    values = {}
    for p in ledger['profiles']:
        page = p['source_page']
        assert p['source_raw_sha256'] == meta['raw_sha256'] and p['source_id'] == meta['id']
        assert p['role'] == 'native_vendor_profile_source_view' and p['method_literal'] == 'TOTAL'
        assert p['unprinted_fields'] == {'under':None,'over':None,'method_breakdown':None}
        assert p['source_timezone'] is None
        original_evidence = p['original_visual_evidence']
        assert pin(ROOT / original_evidence['original_render_path'])['sha256'] == original_evidence['render_sha256']
        assert p['printed_native_id'] == re.search(r'(\d{3})$',p['native_label_literal']).group(1)
        assert set(p['fields']) == set(own_text[page]['fields'])
        values[page] = {}
        for name,field in p['fields'].items():
            extracted = own_text[page]['fields'][name]
            parsed = extracted['parsed_value']
            if parsed is None:
                assert (page,name) in MANUAL
                value = MANUAL[page,name]
            else:
                value = parsed
                direct += 1
            assert value == field['value'],(page,name,value,field['value'])
            comparisons.append({'page':page,'field':name,'raw_line':extracted['raw_line'],
                                'raw_token':extracted['raw_token'],'strict_parsed_value':parsed,
                                'accepted_value':value,'manual_original_reading':parsed is None})
            values[page][name] = value
        assert p['unallocated_contest_residuals']['president'] == values[page]['president_contest_total'] - sum(values[page][n] for n in NAMES[:9]) - values[page]['president_generic_write_in']
        assert p['unallocated_contest_residuals']['senate'] == values[page]['senate_contest_total'] - sum(values[page][n] for n in NAMES[9:]) - values[page]['senate_generic_write_in']
    assert direct == 373 and len(comparisons) == 380
    assert {(r['page'],r['field']) for r in comparisons if r['manual_original_reading']} == set(MANUAL)
    sums = {k:sum(p[k] for p in values.values()) for k in SUMMARY}
    assert sums == SUMMARY == ledger['field_sums']
    assert len(controls['source_field_comparisons']) == 18
    assert {r['field'] for r in controls['source_field_comparisons']} == set(SUMMARY)
    assert all(r['profile_sum'] == r['source_county_panel_value'] == SUMMARY[r['field']] for r in controls['source_field_comparisons'])
    assert controls['unallocated_contest_residuals'] == {'senate':186,'president':37}
    rows = [r for r in csv.DictReader(io.StringIO(csv_raw.decode(),newline='')) if r['source_id'] == meta['id']]
    seen = set()
    for r in rows:
        key = (int(r['source_page']),r['source_field'])
        assert key not in seen
        seen.add(key)
        assert float(r['value']) == values[key[0]][key[1]]
        assert r['source_raw_sha256'] == meta['raw_sha256'] and r['source_method_literal'] == 'TOTAL'
    assert len(seen) == 380
    renders = json.loads((DATA / 'coordinator-qa/union-profile-independent-renders.json').read_bytes())
    for r in renders:
        assert pin(ROOT / r['path'])['sha256'] == r['sha256']
    replay_raw,replay_pin = frozen(DATA / 'baselines/union-native-profile-peer-reconciliation.json')
    replay = json.loads(replay_raw)
    assert replay['field_positions'] == 380 and replay['source_views'] == 20
    assert replay['value_differences'] == replay['exact_text_layer_position_differences'] == replay['label_differences'] == []
    reference_path = ROOT / replay['peer_snapshot_path']
    reference_stored = reference_path.read_bytes()
    assert sha(reference_stored) == replay['peer_stored_sha256']
    reference_raw = gzip.decompress(reference_stored)
    assert sha(reference_raw) == replay['peer_original_sha256']
    reference_rows = list(csv.DictReader(io.StringIO(reference_raw.decode(),newline='')))
    # The working aggregate CSV can also contain subsequently added Pike rows.
    # Only the explicit Union scope is compared with the earlier frozen proof.
    assert len(reference_rows) == 380 and reference_rows == rows
    independent_raw,independent_pin = frozen(ROOT / replay['own_path'])
    assert sha(independent_raw) == replay['own_sha256']
    aliases = dict(zip(['pres_Harris','pres_Oliver','pres_Stein','pres_Terry','pres_Trump',
                       'pres_Shiva','pres_Claudia','pres_Kennedy','pres_Sonski','sen_Pinkins','sen_Wicker'],NAMES)) | {
        'registration':'registration_total','ballots_cast':'ballots_cast_total','blank_ballots':'ballots_blank',
        'printed_turnout':'voter_turnout_percent','pres_generic_write_in':'president_generic_write_in',
        'pres_contest_total':'president_contest_total','sen_generic_write_in':'senate_generic_write_in',
        'sen_contest_total':'senate_contest_total'}
    left = {(int(r['source_page']),r['source_field']):r for r in rows}
    independent_rows = list(csv.DictReader(io.StringIO(independent_raw.decode(),newline='')))
    assert len(independent_rows) == 380
    for r in independent_rows:
        field = aliases[r['field']]
        own = left[int(r['source_page']),field]
        assert float(r['value']) == float(own['value'])
        assert r['raw_sha256'] == own['source_raw_sha256']
        assert r['vendor_profile_code'] == own['printed_native_id']
        assert r['native_label_literal'] == own['label_literal']
        assert r['text_layer_literal'] == own['source_text_layer_literal']
        assert json.loads(r['original_word_bounds_points']) == json.loads(own['source_position'])
    output = {
        'status':'pass_20_Union_profiles_380_fields_18_count_vectors_explicit_text_image_differences',
        'source_pin':meta,'frozen_worker_inputs':[ledger_pin,csv_pin,controls_pin],
        'independent_peer_proof_snapshot':replay_pin,'independent_peer_CSV_snapshot':independent_pin,
        'earlier_turnout_Union_only_peer_reference':pin(reference_path),
        'working_aggregate_CSV_qualification':'Full snapshot can contain additional source scopes; only380 Union positions are reviewed here. Its whole-file hash is not substituted for the earlier Union-only proof hash.',
        'reciprocal_field_values_raw_text_bounds_labels_codes':380,
        'profile_count':20,'candidate_and_administrative_fields':380,
        'independent_strict_Poppler_values_agree':373,'separate_original_glyph_readings':[
            {'page':p,'field':n,'value':v} for (p,n),v in MANUAL.items()],
        'independent_original_renders':renders,'independent_field_comparisons':comparisons,
        'independent_additive_count_sums':sums,'additive_count_fields':18,
        'nonadditive_turnout_percentages':20,'arithmetic_residuals_only':{'president':37,'senate':186},
        'worker_image_text_differences':ledger['text_layer_original_visual_differences'],
        'summary_clock_literal':'11/14/2024 4:52 PM','profile_clock_literal':'11/14/2024 4:58 PM','source_timezone':None,
        'scope':'Separate complete Union ES&S profile source scope. An independent Poppler parse from exact original bytes agrees on373 values; seven explicit original-image readings resolve unparsed punctuation tokens without normalization or residual fitting. All18 additive count fields, including blank and both contest totals, close the independently read county summary/statistics panels; twenty printed percentages are non-additive. The coordinator has not freshly visually read every profile glyph. Literal truncated ticket labels, source profile codes, generic marks and missing under/over remain separate from SEMS/current identity, eligible write-in adjudication and method allocation. Exact raw text and independent worker agreement do not approve any geographic/crossyear join.'}
    text_bytes = (json.dumps(own_text,indent=2)+'\n').encode()
    (DEST / 'independent-Poppler-fields.json.gz').write_bytes(gzip.compress(text_bytes,mtime=0))
    (DATA / 'coordinator-union-profile-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['status','profile_count','candidate_and_administrative_fields','independent_strict_Poppler_values_agree','additive_count_fields','arithmetic_residuals_only']}))


if __name__ == '__main__':
    main()
