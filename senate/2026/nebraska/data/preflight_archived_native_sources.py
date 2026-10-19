"""Read the complete retained historical HTML, preserving partial archive entities.

Uses BeautifulSoup from the external read-only parsing environment. Native IDs
are publication-scoped strings. No geographic or cross-publication join follows.
"""
from pathlib import Path
import csv, gzip, hashlib, io, json, re
from bs4 import BeautifulSoup

DATA = Path(__file__).resolve().parent
NEWS = DATA / 'news'

def sha(b): return hashlib.sha256(b).hexdigest()

def original(row):
    stored = (NEWS / row['asset']).read_bytes()
    raw = gzip.decompress(stored)
    assert sha(stored) == row['stored_sha256']
    assert sha(raw) == row['raw_sha256'] and len(raw) == row['bytes']
    return raw

def cells(row):
    return [{'tag':c.name, 'text':c.get_text(' ', strip=True),
             'attributes':c.attrs, 'html':str(c)}
            for c in row.find_all(['th', 'td'], recursive=False)]

def parse_candidate(row):
    cc = cells(row)
    value = int(cc[4]['text'].replace(',', '')) if len(cc)>4 and re.fullmatch(r'[\d,]+', cc[4]['text']) else None
    return {'source_row_id':row['id'], 'row_attributes':row.attrs, 'cells':cc,
            'candidate_label':cc[3]['text'] if len(cc)>3 else None,
            'candidate_id_literal':cc[7]['text'] if len(cc)>7 else None,
            'race_id_literal':cc[8]['text'] if len(cc)>8 else None,
            'count':value}

def pin(path):
    b=path.read_bytes(); return {'path':str(path.relative_to(DATA.parent)), 'bytes':len(b), 'sha256':sha(b)}

def main():
    manifest=json.loads((NEWS/'manifest.json').read_bytes())
    state=next(r for r in manifest if r['id']=='sos-2024-observed-special-county-archive-20241204')
    soup=BeautifulSoup(original(state), 'html.parser')
    counties={}
    for row in soup.find_all('tr', id=re.compile(r'^ContentPlaceHolder1xuwgCounty_r_\d+$')):
        cc=cells(row); literal=cc[2]['text']
        name=cc[1]['text'].split(' County Precincts Reporting:')[0]
        candidates=[parse_candidate(soup.find('tr', id=row['id']+'_'+str(j))) for j in range(2)]
        assert literal not in counties
        counties[literal]={'county_name_literal':name,'source_header_row_id':row['id'],
            'header_cells':cc,'candidate_rows':candidates}
    assert len(counties)==93
    totals=[sum(c['candidate_rows'][j]['count'] for c in counties.values()) for j in range(2)]
    assert totals==[585103,349902]
    preflight=json.loads((DATA/'coordinator-primary-preflight.json').read_bytes())
    official=preflight['tables']['2024_Senate_ClassII_two_year']['county_rows']
    for c in counties.values():
        expected=official[c['county_name_literal']]['votes']
        assert [r['count']for r in c['candidate_rows']]==expected
    available=[r for r in manifest if r['id'].startswith('sos-2024-special-native-archive-cty-') and r.get('status')==200]
    selected={}
    for row in available:
        match=re.search(r'[?&]cty=(\d+)',row['url']); assert match
        key=row.get('historical_county_id_literal',match[1])
        assert key==match[1]
        # Complete successful recovery replaces selection, never an earlier receipt.
        prior=selected.get(key)
        if prior is None or row.get('archive_entity_completeness',{}).get('complete_entity_claimed'):
            selected[key]=row
    assert set(selected)==set(counties)
    records=[]; results=[]
    for key, source in sorted(selected.items()):
        raw=original(source); dom=BeautifulSoup(raw,'html.parser')
        header=dom.find('tr',id='ContentPlaceHolder1xuwgCounty_r_0'); hc=cells(header)
        assert hc[2]['text']==key
        name=hc[1]['text'].split(' County Precincts Reporting:')[0]
        assert name==counties[key]['county_name_literal']
        expected=int(hc[-1]['text'])
        county_candidates=[parse_candidate(dom.find('tr',id=header['id']+'_'+str(j))) for j in range(2)]
        county_counts=[r['count'] for r in county_candidates]
        assert county_counts==[r['count']for r in counties[key]['candidate_rows']]
        units=[]
        for row in dom.find_all('tr',id=re.compile(r'^ContentPlaceHolder1xuwgPrecinct_r_\d+$')):
            cc=cells(row); children=[]
            for j in range(2):
                child=dom.find('tr',id=row['id']+'_'+str(j))
                children.append(parse_candidate(child) if child else None)
            unit={'source_id':source['id'],'raw_sha256':source['raw_sha256'],
                'county_id_literal':key,'county_name_literal':name,'source_header_row_id':row['id'],
                'header_cells':cc,'literal_name':cc[1]['text'] if len(cc)>1 else None,
                'native_id_literal':cc[2]['text'] if len(cc)>2 else None,
                'candidate_rows':children}
            unit['role']='administrative_countywide' if unit['native_id_literal']=='_TOT' else 'source_native_precinct'
            units.append(unit)
        native=[r for r in units if r['role']=='source_native_precinct']
        admin=[r for r in units if r['role']=='administrative_countywide']
        complete=source.get('archive_entity_completeness',{}).get('complete_entity_claimed',
            b'</html>' in raw.lower() and not any('truncat' in str(v).lower() for k,v in source.get('headers',{}).items() if k.lower()=='warning'))
        known=[sum(r['candidate_rows'][j]['count'] for r in native if r['candidate_rows'][j] and r['candidate_rows'][j]['count'] is not None)for j in range(2)]
        missing=[sum(not r['candidate_rows'][j] or r['candidate_rows'][j]['count'] is None for r in native)for j in range(2)]
        if complete:
            assert len(native)==expected,(key,name,len(native),expected)
            assert missing==[0,0]
        residual=[known[j]-county_counts[j] for j in range(2)]
        results.append({'source_id':source['id'],'source_pin':source,'county_id_literal':key,
            'county_name_literal':name,'expected_source_native_count':expected,
            'retained_source_native_headers':len(native),'administrative_headers':len(admin),
            'entity_complete':bool(complete),'county_candidate_rows':county_candidates,
            'county_header_cells':hc,'known_native_candidate_sums':known,
            'missing_candidate_positions_in_retained_headers':missing,
            'native_known_minus_county_control':residual,
            'all_native_to_county_counts_match':complete and residual==[0,0],
            'administrative_candidate_counts':[[c['count'] if c else None for c in r['candidate_rows']]for r in admin]})
        records.extend(units)
    dest=NEWS/'extracts/archived-2024-special-native-original-positions.jsonl.gz'
    dest.write_bytes(gzip.compress(b''.join((json.dumps(r,separators=(',',':'))+'\n').encode()for r in records),mtime=0))
    complete=[r for r in results if r['entity_complete']]
    incomplete=[r for r in results if not r['entity_complete']]
    exports=[]
    for key in ['sos-2024-observed-public-all-csv-archive','sos-2024-observed-public-statewide-csv-archive']:
        source=next(r for r in manifest if r['id']==key)
        allrows=list(csv.reader(io.StringIO(original(source).decode('utf-8-sig'))))
        header=allrows[0];assert len(header)==15
        assert all(len(r)==16 and r[-1]==''for r in allrows[1:])
        selected_rows=[r for r in allrows[1:]if r[0]=='12464']
        assert len(selected_rows)==2 and [r[8].strip()for r in selected_rows]==['Pete Ricketts','Preston Love Jr.']
        vals=[int(r[11])for r in selected_rows]
        exports.append({'source_pin':source,'complete_header':header,'complete_rows':allrows[1:],
            'source_row_count':len(allrows)-1,'unheaded_trailing_empty_field_preserved':True,
            'selected_special_senate_rows':selected_rows,'selected_counts':vals,
            'selected_minus_final_canvass':[vals[j]-totals[j]for j in range(2)],
            'scope':'All-races or statewide public CSV, not precinct rows. Literal source clock has no zone. Retained November11 statewide export differs final controls despite displaying1326/1326; no completion or later correction cause inferred.'})
    assert exports[0]['selected_counts']==totals
    assert exports[1]['selected_counts']==[577711,341868]
    export_path=NEWS/'extracts/archived-2024-observed-public-csv-rows.json.gz'
    export_path.write_bytes(gzip.compress(json.dumps(exports,separators=(',',':')).encode(),mtime=0))
    out={'status':'pass_complete_county_controls_with_explicit_archived_native_gaps',
        'state_county_source':state,'county_rows':counties,'county_primary_candidate_controls':186,
        'state_candidate_totals':totals,'county_observations':results,
        'complete_native_entities':len(complete),'partial_archive_entities':len(incomplete),
        'complete_native_headers':sum(r['retained_source_native_headers']for r in complete),
        'partial_native_headers':sum(r['retained_source_native_headers']for r in incomplete),
        'expected_source_native_headers_all93':sum(r['expected_source_native_count']for r in results),
        'native_control_differences':[r for r in complete if not r['all_native_to_county_counts_match']],
        'original_positions':pin(dest),
        'observed_public_export_rows':pin(export_path),
        'public_export_scoped_controls':[{k:r[k]for k in ['source_row_count','selected_counts','selected_minus_final_canvass','scope']}for r in exports],
        'qualification':'Historical2024 publication only. All93 county candidate vectors independently match retained signed canvass county controls. Source county IDs are literal publication IDs, not FIPS. Administrative _TOT rows are separate. Declared Wayback length truncations remain incomplete, including missing candidate child rows. Known sums are never zero-filled or allocated. Complete HTML native count and candidate controls are checked separately, with any source differences retained. No current precinct, cross-year, BIFF, method or legal geographic equivalence, dispatch acceptance or complete statewide native acquisition is inferred.'}
    target=DATA/'coordinator-2024-archived-native-preflight.json'
    target.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['status','county_primary_candidate_controls','state_candidate_totals','complete_native_entities','partial_archive_entities','complete_native_headers','partial_native_headers']}))
    print('native_control_differences',[(r['county_name_literal'],r['native_known_minus_county_control'])for r in out['native_control_differences']])

if __name__=='__main__':main()
