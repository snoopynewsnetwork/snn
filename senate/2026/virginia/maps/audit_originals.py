"""Own whole-original reconstruction, without first-pair producer code imports.

Checks all frozen baseline receipt/entity originals, all legacy original bytes,
four full CSVs including every header/token/position, and every complete primary
native API object and all candidate×method constituents at original pointers.
"""
import collections,csv,gzip,hashlib,io,json,sys
from acquire import HERE,sha

S=HERE.parent
def audit():
    pins=json.loads((S/'data/baselines/source/input-pins.json').read_bytes())['sources']
    source={};entitycount=0;receiptcount=0;cache={}
    for row in pins:
        b=(S/row['receipt_path']).read_bytes();assert len(b)==row['receipt_bytes'] and sha(b)==row['receipt_sha256']
        assert json.loads(b)==row['receipt'];receiptcount+=1
        for ent in row['entities']:
            key=(ent['path'],ent['sha256'])
            if key not in cache:
                stored=(S/ent['path']).read_bytes();assert len(stored)==ent['bytes'] and sha(stored)==ent['sha256']
                raw=gzip.decompress(stored) if ent['path'].endswith('.gz') else stored
                assert len(raw)==ent['raw_bytes'] and sha(raw)==ent['raw_sha256'];cache[key]=raw
            entitycount+=1
        if row['entities']:source[row['id']]=cache[(row['entities'][-1]['path'],row['entities'][-1]['sha256'])]
    legacy=json.loads((S/'data/turnout/source/pinned-originals.json').read_bytes())
    for row in legacy:
        stored=(S/row['body_path']).read_bytes();raw=gzip.decompress(stored)
        assert len(stored)==row['stored_bytes'] and sha(stored)==row['stored_sha256'] and len(raw)==row['raw_bytes'] and sha(raw)==row['raw_sha256']
        receipt=(S/'data/turnout'/row['receipt_path']).read_bytes();assert sha(receipt)==row['receipt_sha256']
    c=json.loads((S/'data/turnout/priority-set.json').read_bytes());fullcsv={};nrows=0;primaryrecords={}
    for contest,sourceid in [('2018-senate','fresh-2018-csv'),('2020-senate','fresh-2020-csv'),('2024-senate','fresh-2024-csv'),('2024-president','president-csv')]:
        raw=source[sourceid];lines=raw.splitlines(keepends=True);offsets=[0]
        for line in lines:offsets.append(offsets[-1]+len(line))
        reader=csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline=''));rows=[];line_start=0
        for index,cells in enumerate(reader,1):
            end=reader.line_num
            rows.append({'record':index,'line_start':line_start+1,'line_end':end,'byte_start':offsets[line_start],'byte_end_exclusive':offsets[end],'raw':raw[offsets[line_start]:offsets[end]],'cells':cells});line_start=end
        assert line_start==len(lines)
        extracted=json.loads(gzip.decompress((S/'data/baselines/extracted'/f'{contest}.json.gz').read_bytes()))
        assert extracted['headers']==rows[0]['cells'] and extracted['parties']==rows[1]['cells']
        assert len(extracted['raw_records'])==len(rows)
        for actual,expected in zip(extracted['raw_records'],rows):
            assert actual=={k:expected[k] for k in ['record','line_start','line_end','cells']}
        if contest.endswith('senate'):
            year=contest[:4];rawrecords=[json.loads(line) for line in gzip.decompress((S/'data/turnout/extracts'/f'{year}-all-original-rows.jsonl.gz').read_bytes()).splitlines()]
            assert len(rawrecords)==len(rows)
            for actual,expected in zip(rawrecords,rows):
                assert actual['source_record']==expected['record'] and actual['physical_line_start']==expected['line_start'] and actual['physical_line_end']==expected['line_end']
                assert actual['byte_start']==expected['byte_start'] and actual['byte_end_exclusive']==expected['byte_end_exclusive']
                assert actual['raw_row_utf8']==expected['raw'].decode('utf-8-sig') and actual['cells']==expected['cells']
        fullcsv[contest]=rows;nrows+=len(rows)
        if contest=='2024-senate':primaryrecords={r['record']:r for r in rows}
    parent=None;parents={}
    for row in fullcsv['2024-senate']:
        if row['cells'] and row['cells'][0]=='Locality':parent=row['cells'][1]
        if row['cells'] and row['cells'][0]=='Precinct':parents[row['record']]=parent
    methodrecords=0;api={}
    for u in c['ordered_units']:
        original=primaryrecords[u['source_record']]
        assert u['cells']==original['cells'] and u['raw_row_utf8']==original['raw'].decode('utf-8-sig')
        assert u['byte_start']==original['byte_start'] and u['byte_end_exclusive']==original['byte_end_exclusive'] and u['physical_line_start']==original['line_start'] and u['physical_line_end']==original['line_end']
        assert u['parent_label']==parents[u['source_record']]
        assert u['candidate_votes']=={str(i):int(original['cells'][i]) for i in (2,3,4)}
        assert u['counts']=={str(i):int(original['cells'][i]) for i in (2,3,4,5)}
        native=u['source_native_constituents']['enr_api'];sourceid=native['source_id']
        if sourceid not in api:api[sourceid]=json.loads(source[sourceid])
        target=api[sourceid]
        for token in native['source_pointer'].split('/')[1:]:
            token=token.replace('~1','/').replace('~0','~');target=target[int(token)] if isinstance(target,list) else target[token]
        assert target==native['full_native_object']
        assert target['precinct']['id']==u['source_native_id'] and target['precinct']['isVirtual']==u['isVirtual']
        for candidate in target['ballotOptions']:assert len(candidate['groupResults'])==5;methodrecords+=len(candidate['groupResults'])
    assert methodrecords==40035 and len(api)==133
    bulk=list(csv.reader(io.StringIO(source['enr-2024-results-report'].decode('cp1252'),newline='')));headers=bulk[0]
    byrecord={i:dict(zip(headers,row)) for i,row in enumerate(bulk,1) if i>1}
    senate=[(i,row) for i,row in byrecord.items() if row['OfficeId']=='cc200'];blank=[(i,row) for i,row in senate if row['PrecinctId']=='']
    assert len(senate)==2685*3 and len(blank)==48 and all(int(row['TOTAL_VOTES'])==int(row['WriteInVote'])==0 for _,row in blank)
    used=[]
    for u in c['ordered_units']:
        export=u['source_native_constituents']['enr_results_export'];records=export['raw_source_records'];assert len(records) in (3,9)
        originals=[byrecord[i] for i in records]
        assert all(row['LocalityCode']==u['parent_locality_code'] and row['OfficeId']=='cc200' for row in originals)
        vector=collections.defaultdict(int)
        for row in originals:vector[row['CandidateId']]+=int(row['WriteInVote'] if row['CandidateId'].startswith('wi-') else row['TOTAL_VOTES'])
        assert dict(vector)==export['candidate_vector'];used+=records
    assert len(used)==len(set(used))==2685*3 and set(used)=={i for i,_ in senate}
    return {'status':'pass','complete_receipts':receiptcount,'complete_entity_observations':entitycount,'unique_original_entity_paths':len(cache),'legacy_whole_originals':len(legacy),'complete_historical_contest_CSVs':4,'all_literal_CSV_records':nrows,'full_primary_native_API_objects':2669,'all_explicit_local_parents':133,'whole_candidate_method_constituents':methodrecords,'all_Senate_bulk_constituent_rows':len(senate),'extra_blank_ID_rows':48,'blank_ID_rows_dropped':False,'producer_imports_or_writes':False,'geometry_or_current_equivalence':False}

if __name__=='__main__':
    result=audit();text=json.dumps(result,indent=2)+'\n';path=HERE/'original-reconstruction.json'
    if '--check' in sys.argv:assert path.read_text()==text
    else:path.write_text(text)
    print(text)
