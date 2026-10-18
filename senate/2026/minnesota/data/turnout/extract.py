"""Independent standard-library OOXML extraction from exact shared originals.

No import of coordinator/peer code or prepared totals. Workbook source row and
column positions remain available; originals preserve every unrelated field.
"""
import collections, csv, gzip, hashlib, io, json, re, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEWS = HERE.parent / 'news'
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
YEARS = {2024: ['USSEN', 'USPRS'], 2022: ['MNGOV'], 2020: ['USSEN']}
STATS = ['REG7AM','EDR','SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB','TOTVOTING']

def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
def csv_bytes(rows, fields):
    s=io.StringIO(newline=''); w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    return s.getvalue().encode()
def csvwrite(p, rows, fields):
    b=csv_bytes(rows,fields);p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def shared(sid):
    m=next(m for m in json.loads((NEWS/'manifest.json').read_text()) if m['id']==sid)
    packed=(NEWS/m['asset']).read_bytes();assert sha(packed)==m['stored_sha256']
    b=gzip.decompress(packed);assert sha(b)==m['raw_sha256'] and len(b)==m['bytes']
    return b,dict(m, shared_path=str((NEWS/m['asset']).relative_to(HERE.parent.parent)), encoding='gzip; decompress to exact original bytes')

def readbook(y):
    b,manifest=shared(f'sos-{y}-precinct-original');z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
    strings=[''.join(v.itertext()) for v in ET.fromstring(z.read('xl/sharedStrings.xml')).findall(NS+'si')]
    rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheets={}
    for sh in ET.fromstring(z.read('xl/workbook.xml')).find(NS+'sheets'):
        target=rels[sh.get(REL)];target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        rows=[]
        for r in ET.fromstring(z.read(target)).find(NS+'sheetData'):
            cells={}
            for c in r:
                v=c.find(NS+'v');v=None if v is None else v.text
                if c.get('t')=='s':v=strings[int(v)]
                if c.get('t')=='inlineStr':v=''.join(c.find(NS+'is').itertext())
                cells[re.sub('[0-9]+$','',c.get('r'))]=dict(value=v,cell=c.get('r'),type=c.get('t'),formula=c.findtext(NS+'f'))
            rows.append(dict(source_row=int(r.get('r')),cells=cells))
        sheets[sh.get('name')]=dict(zip_path=target,rows=rows)
    return sheets,manifest

def extract():
    (HERE/'source').mkdir(parents=True,exist_ok=True)
    manifests=[];summaries={};meta={}
    for y,prefixes in YEARS.items():
        sheets,manifest=readbook(y);manifests.append(manifest)
        rs=sheets['Precinct-Results']['rows'];labels=[c['value'] for c in rs[0]['cells'].values()]
        duplicates={v for v,n in collections.Counter(labels).items() if n>1}
        columns={col: c['value']+('__'+col if c['value'] in duplicates else '') for col,c in rs[0]['cells'].items()}
        # Source-native FIPS table, not a fabricated sequential-code conversion.
        counties={}
        for r in sheets['Counties']['rows'][1:]:
            v={k:c['value'] for k,c in r['cells'].items()}
            if v.get('A','').isdigit(): counties[v['A']]=dict(county_code=v['A'],county_name_table=v['B'],county_fips=v['C'],source_row=r['source_row'])
        assert len(counties)==87
        selected=[v for v in columns.values() if not v.startswith(('USPRS','USSEN','USREP','MNSEN','MNLEG','MNCA','MNGOV','MNSOS','MNAUD','MNAG')) or any(v.startswith(p) for p in prefixes)]
        counts=[v for v in selected if any(v.startswith(p) for p in prefixes) or v in STATS]
        records=[];excluded=[]
        for r in rs[1:]:
            vals={columns[col]:c['value'] for col,c in r['cells'].items() if col in columns}
            if not re.fullmatch(r'27\d{7}',vals.get('VTDID') or ''):
                assert vals.get('VTDID') in (None,'','End of worksheet'),vals
                excluded.append(dict(source_row=r['source_row'],reason='footer or empty formatted row',VTDID=vals.get('VTDID')));continue
            ct=counties[vals['COUNTYCODE']]
            assert vals['VTDID']==ct['county_fips']+vals['PCTCODE']
            assert vals['COUNTYNAME'].upper()==ct['county_name_table']
            for field in counts:
                assert re.fullmatch(r'\d+',str(vals.get(field,''))),(y,r['source_row'],field,vals.get(field))
            for p in prefixes:
                assert sum(int(vals[k]) for k in counts if k.startswith(p) and k!=p+'TOTAL')==int(vals[p+'TOTAL'])
            rec=dict(source_id=f'sos-{y}-precinct-original',election_date={2024:'2024-11-05',2022:'2022-11-08',2020:'2020-11-03'}[y],source_sheet='Precinct-Results',source_row=r['source_row'],
                     native_key=f'MN:{y}:VTDID:{vals["VTDID"]}',county_key='MN:county:'+ct['county_fips'],county_fips=ct['county_fips'],
                     unit_kind='source precinct / Vote Tabulation District',current_2026_equivalence='unavailable',method_warning='2024 Notes: SIGNATURES may be too high / AB_MB too low in some mail precincts' if y==2024 and vals['COUNTYNAME'] in ['Clearwater','Swift','Winona'] else '')
            rec.update({k:vals.get(k) for k in selected});records.append(rec)
        assert len(records)==(4110 if y==2020 else 4103)
        assert len({r['VTDID'] for r in records})==len(records)
        assert len({(r['COUNTYCODE'],r['PCTCODE']) for r in records})==len(records)
        assert set(r['COUNTYCODE'] for r in records)==set(counties)
        fields=list(records[0]);csvwrite(HERE/f'native-{y}.csv.gz',records,fields)
        aggregate=[]
        for code,ct in counties.items():
            units=[r for r in records if r['COUNTYCODE']==code]
            a=dict(county_key='MN:county:'+ct['county_fips'],county_fips=ct['county_fips'],COUNTYCODE=code,COUNTYNAME=units[0]['COUNTYNAME'],native_units=len(units))
            a.update({k:sum(int(r[k]) for r in units) for k in counts});aggregate.append(a)
        csvwrite(HERE/f'county-controls-{y}.csv',aggregate,list(aggregate[0]))
        # Municipal labels are scoped source parents, not assumed legal IDs or cross-year matches.
        munis=[]
        for fips,label in sorted({(r['county_fips'],r['MCDNAME']) for r in records}):
            units=[r for r in records if (r['county_fips'],r['MCDNAME'])==(fips,label)]
            a=dict(county_fips=fips,MCDNAME=label,derived_key=json.dumps([y,fips,label],ensure_ascii=False,separators=(',',':')),native_municipal_id=None,native_units=len(units))
            a.update({k:sum(int(r[k]) for r in units) for k in counts});munis.append(a)
        csvwrite(HERE/f'municipal-controls-{y}.csv',munis,list(munis[0]))
        sums={k:sum(int(r[k]) for r in records) for k in counts}
        formula_diffs=[dict(native_key=r['native_key'],source_row=r['source_row'],TOTVOTING=int(r['TOTVOTING']),method_sum=sum(int(r[k]) for k in ['SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB'] if k in r)) for r in records if int(r['TOTVOTING'])!=sum(int(r[k]) for k in ['SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB'] if k in r)]
        summaries[str(y)]=dict(rows=len(records),counties=len(counties),municipal_source_labels=len(munis),totals=sums,mail_ballot_flags=dict(collections.Counter(r['MAILBALLOT'] for r in records)),
                              candidate_total_exceeds_TOTVOTING=[dict(native_key=r['native_key'],source_row=r['source_row'],PCTNAME=r['PCTNAME'],contest=p,candidate_votes=int(r[p+'TOTAL']),TOTVOTING=int(r['TOTVOTING'])) for r in records for p in prefixes if int(r[p+'TOTAL'])>int(r['TOTVOTING'])],
                              method_identity_discrepancies=formula_diffs,zero_candidate_total_units={p:[r['native_key'] for r in records if int(r[p+'TOTAL'])==0] for p in prefixes})
        meta[str(y)]=dict(source_id=manifest['id'],source_sha256=manifest['raw_sha256'],source_worksheet=sheets['Precinct-Results']['zip_path'],columns=columns,
                         metadata={k:sheets[k] for k in ['Notes','Fields','Counties']},excluded_precinct_sheet_rows=excluded,
                         original_sheets={k:dict(zip_path=v['zip_path'],row_count=len(v['rows'])) for k,v in sheets.items()})
    # Full manifests preserve actual download chain metadata; original bytes reused read-only.
    for sid in ['sos-2020-canvass-original','sos-2024-general-index','sos-2022-general-index','sos-2020-general-index','sos-results','sos-enr-home','sos-2024-precinct-index','sos-2022-precinct-index','sos-2020-precinct-index']:
        _,m=shared(sid);manifests.append(m)
    dump(HERE/'source/shared-originals.json',manifests)
    dump(HERE/'source/workbook-context.json',meta)
    dump(HERE/'source/extraction-controls.json',summaries)
    print(json.dumps(summaries,indent=2))

if __name__=='__main__': extract()
