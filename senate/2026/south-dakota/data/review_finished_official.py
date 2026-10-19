"""Producer-free offline final official-source and current raw-schema audit."""
from pathlib import Path
from collections import Counter
import ast, csv, gzip, hashlib, io, json, posixpath, re, zipfile
import xml.etree.ElementTree as ET

D = Path(__file__).resolve().parent
S = D.parent
R = D / 'results-sources'
N = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def load(p):
    return json.loads(p.read_bytes())

def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))

def semantic(x):
    return sha(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())

def pointer(x, path):
    for key in path.split('/')[1:] if path else []:
        key = key.replace('~1','/').replace('~0','~')
        x = x[int(key)] if isinstance(x,list) else x[key]
    return x

def workbook(raw):
    z = zipfile.ZipFile(io.BytesIO(raw))
    assert z.testzip() is None
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for v in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',N):
            shared.append(''.join(v.itertext()))
    rels = {v.attrib['Id']:v.attrib['Target'] for v in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    out = []
    for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',N):
        rid = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        member = posixpath.normpath('xl/'+rels[rid])
        if member.startswith('xl/xl/'):
            member = member[3:]
        if member.startswith('/'):
            member = member[1:]
        rows = []
        for row in ET.fromstring(z.read(member)).findall('m:sheetData/m:row',N):
            cells = {}
            for cell in row.findall('m:c',N):
                value = cell.find('m:v',N)
                value = value.text if value is not None else None
                if cell.attrib.get('t') == 's' and value is not None:
                    value = shared[int(value)]
                elif cell.attrib.get('t') == 'inlineStr':
                    value = ''.join(cell.find('m:is',N).itertext())
                cells[re.sub(r'\d+$','',cell.attrib['r'])] = value
            rows.append((row.attrib['r'],cells))
        native = [(i,x['B'],x['C'],x['D']) for i,x in rows
                  if x.get('B') and x['B'] != 'TOTALS' and str(x.get('C','')).isdigit()]
        totals = [(i,x['C'],x['D']) for i,x in rows if x.get('B') == 'TOTALS']
        assert len(totals) == 1 and totals[0][1:] == ('0','0')
        assert all(x[2:] == ('0','0') for x in native)
        assert any('0 of 656' in str(x.get('A','')) for _,x in rows)
        out.append(dict(county=sheet.attrib['name'],native=native,footer=totals))
    return out

def main():
    mf = load(R/'asset-manifest.json')
    owned = mf['owned_assets']; dependencies = mf['read_only_dependencies']
    assert len(owned) == 526 and len(dependencies) == 279
    for v in owned+dependencies:
        assert pin(S/v['path']) == {k:v[k] for k in ['path','bytes','sha256']}
        assert v['bytes'] < 40_000_000
    actual = {str(p.relative_to(S)) for p in R.rglob('*') if p.is_file()} | {'official-results.md','data/official-results-sources.csv'}
    assert actual == {v['path'] for v in owned} | {'data/results-sources/asset-manifest.json'}
    assert not any(p.name in ['__pycache__','.venv','node_modules'] for p in R.rglob('*'))
    for p in R.rglob('*.py'):
        ast.parse(p.read_bytes(),filename=str(p))
    receipts = {}; bodies = {}; statuses = Counter()
    for p in sorted((R/'raw').glob('*.receipt.json')):
        r = load(p); assert p.name == r['id']+'.receipt.json'
        statuses[r['status']] += 1
        parts = []
        for q in r['stored_parts']:
            b = (R/q['path']).read_bytes()
            assert len(b) == q['bytes'] and sha(b) == q['sha256']
            parts.append(b)
        b = gzip.decompress(b''.join(parts))
        assert len(b) == r['raw_bytes'] and sha(b) == r['raw_sha256']
        assert r['method'] in ['GET','POST'] and r['url'].startswith(('http:','https:'))
        assert r['retrieved_utc'] and r['completed_utc'] and 'headers' in r and 'redirects' in r
        receipts[r['id']] = r; bodies[r['id']] = b
    assert len(receipts) == 211 and statuses == Counter({200:204,403:3,None:4})
    c = load(D/'turnout/priority-set.json')
    dep = load(R/'dependency-verification.json')
    assert len(dep['exact_read_only_references']) == 279
    for v in dep['exact_read_only_references']:
        assert pin(S/v['path']) == {k:v[k] for k in ['path','bytes','sha256']}
    for v in dep['complete_semantic_objects']:
        assert semantic(pointer(c,v['JSON_pointer'])) == v['recursive_semantic_sha256']
    assert len(dep['complete_semantic_objects']) == 2141
    units = c['all_units']
    assert len(units) == 691 and sum(x['contest_votes'] for x in units) == 428728
    assert sum(x['contest_votes'] for x in units[:303]) == 342947
    assert sum(x['contest_votes'] for x in units[:304]) == 343402
    assert sum(x['contest_votes'] for x in units[304:]) == 85326
    assert c['certification_robustness']['proven'] is False
    priorities = load(R/'ordered-priority-records.json')
    remainder = load(R/'ordered-remainder-records.json')
    assert len(priorities) == 304 and len(remainder) == 387
    for i,(v,u) in enumerate(zip(priorities+remainder,units)):
        assert v['historical_key'] == u['key'] and v['rank'] == i+1
        ref = v['complete_historical_object']
        assert pointer(c,ref['JSON_pointer']) == u
        assert semantic(u) == ref['recursive_semantic_sha256']
        assert v['current_native_identifier'] is None
    dirs = load(R/'authority-directory.json')
    for v in dirs['rows']:
        assert v['source_row_HTML'] in bodies['county-directory'].decode()
    assert len(dirs['rows']) == 66 and all(len(v['fields']) == 9 for v in dirs['rows'])
    investigations = load(R/'county-investigations.json')['investigations']
    assert len(investigations) == 39
    for v in investigations:
        assert receipts['county-'+v['county_fips']]['status'] == 200
    assert len(list(csv.DictReader((S/'data/official-results-sources.csv').open()))) == 67
    exports = {k:workbook(v) for k,v in bodies.items() if k.endswith('-native-xlsx')}
    assert len(exports) == 39
    normalized = []
    for k,v in exports.items():
        assert len(v) == 65 and sum(len(x['native']) for x in v) == 654
        assert 'Charles Mix' not in {x['county'] for x in v}
        normalized.append(v)
    assert all(x == normalized[0] for x in normalized)
    counts = {x['county']:len(x['native']) for x in normalized[0]}
    turnout = json.loads(bodies['state-turnout-service'])['d']
    assert len(turnout) == 66 and sum(x['TotalPrecincts'] for x in turnout) == 673
    assert sum(x['Voters'] for x in turnout) == 618804
    differences = []
    for x in turnout:
        assert x['IsReported'] is False and x['PrecinctsReporting'] == 0
        name = x['CountyName'].replace(' (Vote Center)','')
        n = counts.get(name)
        if n != x['TotalPrecincts']:
            differences.append((name,x['TotalPrecincts'],n))
    assert differences == [('Brookings',10,5),('Charles Mix',11,None),('Hughes',6,3)]
    csvrows = list(csv.reader(io.StringIO(bodies['state-csv'].decode())))
    assert len(csvrows[0]) == 14 and all(len(x) == 15 for x in csvrows[1:])
    senate = [x for x in csvrows[1:] if x[0] == '14412']
    assert [(x[7],x[2],x[11],x[13]) for x in senate] == [('24967','REP','0','="0/656"'),('24887','IND','0','="0/656"')]
    autocomplete = json.loads(bodies['state-candidate-service'])['d']
    assert len(autocomplete) == 358
    assert [x['ID'] for x in autocomplete if x['desc']=='United States Senator'] == [215,215]
    law = json.loads(bodies['sessionlaw-ch73-json'])
    assert (law['SessionLawId'],law['DocumentId'],law['Chapter']) == (33903,306614,73)
    text = re.sub(r'<[^>]*>',' ',law['Html'])
    text = ' '.join(text.split())
    for required in ['Signed March 26, 2026','12-19-10','12-19-41','day before','emergency']:
        assert required in text, required
    for k,n,h in [('lincoln-ballot',120975,'67e503745b532a71bf07077fb0d5e93767317dc349f03ec02b1fcec509385f15'),('hanson-ballot',176689,'fb0cf2b4c440d563a1f8c886bc4f044222dda8d9733cb1ec0dec0d6b38746ff8')]:
        assert len(bodies[k]) == n and sha(bodies[k]) == h and bodies[k].startswith(b'%PDF')
    out = dict(status='pass_independent_frozen_official_package_and_current_raw_schema_review',
        manifest=pin(R/'asset-manifest.json'), validation=pin(R/'validation.json'),
        owned_membership_exact=526, read_only_dependencies=279,
        full_recursive_contract_objects=2141, complete_receipts=211,
        authority_count=67, priority_parent_requests=39, full_native=691, priority=304, remainder=387,
        independent_OOXML_exports=39, county_sheets_each=65, zero_native_each=654,
        all39_complete_source_row_vectors_equal=True, missing_native_county='Charles Mix',
        turnout_service_counties=66, turnout_service_precincts=673, Senate_banner_and_CSV=656,
        turnout_service_registrations=618804, source_scope_differences=differences,
        search_ID215_distinct_from_race14412_choiceIDs=True,
        chapter73_signed='2026-03-26', operative_emergency_vs_2025_manual_qualified=True,
        physical_ballot_originals=[dict(id=k,receipt=pin(R/'raw'/(k+'.receipt.json'))) for k in ['lincoln-ballot','hanson-ballot']],
        current_returns_or_leaf_geography_or_cadence_approved=False,
        certified_native_minimum_or_membership_approved=False,
        qualification='Independent complete source-byte/schema/preservation audit. Original ballot visual and law reading evidence is separately retained. Historical public/signed194 discrepancy remains unallocated; setup scopes and zero counts are not November returns. Complete later court/military/ballot scope remains qualified.')
    target = D/'coordinator-finished-official-review.json'
    b = (json.dumps(out,indent=2)+'\n').encode()
    if target.exists(): assert target.read_bytes() == b
    else: target.write_bytes(b)
    print(json.dumps(pin(target)))

if __name__ == '__main__':
    main()
