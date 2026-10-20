"""Reopen every original entity and all 201 BIFF workbooks independently."""
import gzip,hashlib,io,json,sys,zipfile
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import quote
from replay_authority import STATE,OWN,parse,digest,semantic,CONTRACT,loadpin
sys.path.insert(0,'/private/tmp/al-turnout-deps')
import xlrd

def receipt_body(r,base):
    chunks=[]
    for p in r['parts']:
        b=(base/p['path']).read_bytes()
        assert len(b)==p['bytes'] and digest(b)==p['sha256']
        chunks.append(b)
    b=gzip.decompress(b''.join(chunks))
    assert len(b)==r['original_bytes'] and digest(b)==r['original_sha256']
    assert r['headers'] and r['requested_url'] and r['final_url'] and r['retrieved_at_utc']
    return b

def replay():
    witness=parse((STATE/'data/turnout/source/original-first-witness.json').read_bytes())
    counts=Counter(); originals={};refs=[]
    for src in witness['sources']:
        if src['kind']=='shared_original':
            r=src['receipt'];path=Path(r['shared_path'])
            if not path.is_absolute():path=STATE.parents[2]/path
            z=path.read_bytes();assert len(z)==r['stored_bytes'] and digest(z)==r['stored_sha256']
            b=gzip.decompress(z);assert len(b)==r['bytes'] and digest(b)==r['raw_sha256']
            assert r['headers'] and r['retrieved_at_utc']
            refs.append({'path':str(path.relative_to(STATE.parents[2])),'stored_bytes':len(z),'stored_sha256':digest(z),
                         'raw_bytes':len(b),'raw_sha256':digest(b),'role':'complete original historical entity',
                         'receipt_pointer':'data/turnout/source/original-first-witness.json#/sources/'+str(len(refs))})
        else:
            r=parse((STATE/'data/turnout'/src['receipt']).read_bytes());b=receipt_body(r,STATE/'data/turnout')
            refs.append({'parts':[dict(p,path='senate/2026/alabama/data/turnout/'+p['path']) for p in r['parts']],
                'raw_bytes':len(b),'raw_sha256':digest(b),'role':'complete original acquired entity',
                'receipt_pointer':'data/turnout/source/original-first-witness.json#/sources/'+str(len(refs))})
        originals[digest(b)]=b;counts['original_entities']+=1
        if 'members' in src:
            z=zipfile.ZipFile(io.BytesIO(b));assert z.namelist()==[m['name'] for m in src['members']]
            for m in src['members']:
                info=z.getinfo(m['name']);v=z.read(m['name'])
                assert len(v)==m['bytes'] and digest(v)==m['sha256']
                assert info.CRC==m['zip_crc32'] and list(info.date_time)==m['zip_date_time']
                counts['original_zip_members']+=1
    # Every own fresh producer receipt has separately verified complete parts/entity.
    a=parse((STATE/'data/coordinator-priority-acceptance.json').read_bytes())
    for pin in a['complete_source_companion_files']:
        name=pin['path']
        if '/source/http/' in name and name.endswith('.receipt.json'):
            r=parse(loadpin(pin));base=STATE/('data/baselines' if '/baselines/' in name else 'data/turnout')
            if r.get('parts'):
                receipt_body(r,base);counts['individual_receipts']+=1
            elif r.get('stored_path_relative_baselines'):
                z=(base/r['stored_path_relative_baselines']).read_bytes()
                assert len(z)==r['stored_bytes'] and digest(z)==r['stored_sha256']
                b=gzip.decompress(z)
                assert len(b)==r['original_bytes'] and digest(b)==r['original_sha256']
                assert r['headers'] and r['retrieved_at_utc']
                counts['individual_receipts']+=1
    for year,native_count,total in [(2024,2085,2265090),(2022,2074,1414238),(2020,2111,2316445)]:
        rawwork=parse(gzip.decompress((STATE/f'data/turnout/source/workbooks-{year}.json.gz').read_bytes()))
        units=parse((STATE/f'data/turnout/native-units-{year}.json').read_bytes())
        bymember=defaultdict(list)
        for u in units:bymember[u['source_member']].append(u)
        assert len(units)==native_count and sum(u['reported_candidate_votes'] for u in units)==total
        assert units==sorted(units,key=lambda u:(-u['reported_candidate_votes'],u['key']))
        archive=next(b for b in originals.values() if b.startswith(b'PK') and any(x['member']['name'] in zipfile.ZipFile(io.BytesIO(b)).namelist() for x in rawwork[:1]))
        z=zipfile.ZipFile(io.BytesIO(archive));assert len(rawwork)==67
        for work in rawwork:
            m=work['member'];b=z.read(m['name']);assert digest(b)==m['sha256']
            book=xlrd.open_workbook(file_contents=b,formatting_info=True)
            assert book.nsheets==len(work['sheets'])
            for sw,sh in zip(work['sheets'],book.sheets()):
                assert sw['name']==sh.name and sw['nrows']==sh.nrows and sw['ncols']==sh.ncols
                assert sw['merged_cells']==[list(x) for x in sh.merged_cells] and sw['visibility']==sh.visibility
                assert len(sw['rows'])==sh.nrows
                for i,r in enumerate(sw['rows']):
                    assert r['row_1based']==i+1
                    assert r['values']==sh.row_values(i) and r['types']==list(sh.row_types(i))
                    counts['typed_cells']+=sh.ncols
                for u in bymember[m['name']]:
                    if u['source_sheet']!=sh.name:continue
                    col=u['column_1based']-1
                    assert u['native_label']==sh.cell_value(0,col)==u['native_id']
                    assert u['key']==f"AL:{year}:general:{u['county_fips']}:col{col+1:03d}:"+quote(u['native_label'],safe='')
                    assert u['member_sha256']==digest(b)
                    for group in ['candidate_votes','contest_other_fields','administrative_fields']:
                        for c in u[group]:
                            row=c['row_1based']-1
                            assert c['column_1based']==col+1
                            assert [c['contest_literal'],c['party_literal'],c['candidate_literal']]==sh.row_values(row)[:3]
                            cell=sh.cell(row,col)
                            assert c['xls_type']==cell.ctype and c['raw_value']==cell.value
                            assert c['value']==(int(cell.value) if cell.ctype==2 else None)
                            counts['raw_native_candidate_admin_positions']+=1
                    counts['native_contexts']+=1
            counts['workbooks']+=1
        if year==2024:
            contract=parse(loadpin(CONTRACT));assert units==contract['units']
    return {'status':'PASS','counts':dict(counts),'xlrd_version':xlrd.__version__,
            'receipt_qualification':'Old source receipts do not invent missing request headers/end times; their recorded status, headers and clocks remain exact.',
            'current_admission':False},refs

if __name__=='__main__':
    result,refs=replay()
    if '--audit' not in sys.argv:
        (OWN/'original-references.json').write_text(json.dumps(refs,indent=2)+'\n')
        (OWN/'qa/original-replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
