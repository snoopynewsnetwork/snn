"""Independent OOXML extraction of primary workbooks; standard library only.
Read original retained bytes, never preflight/peer derivatives. CSV source values
stay strings. Original ZIP retains every office/cell/type/style/formula.
"""
import collections,csv,gzip,hashlib,io,json,re,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
H=Path(__file__).resolve().parent;S=H/'source';N=H.parent/'news'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
METHOD=['REG7AM','EDR','SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB','TOTVOTING']
DATES={2024:'2024-11-05',2022:'2022-11-08',2020:'2020-11-03'}
def sha(b):return hashlib.sha256(b).hexdigest()
def writecsv(p,rows):
    if not rows:return
    text=io.StringIO(newline='');w=csv.DictWriter(text,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);b=text.getvalue().encode()
    p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def readcsv(p):
    b=p.read_bytes();return list(csv.DictReader(io.StringIO((gzip.decompress(b) if p.suffix=='.gz' else b).decode())))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def workbook(year):
    manifest={r['id']:r for r in json.loads((N/'manifest.json').read_text())};sid=f'sos-{year}-precinct-original';m=manifest[sid];stored=(N/m['asset']).read_bytes();assert sha(stored)==m['stored_sha256'];b=gzip.decompress(stored);assert sha(b)==m['raw_sha256'] and len(b)==m['bytes']
    z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
    ss=[''.join(t.text or '' for t in si.iter('{'+NS['m']+'}t')) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    rels={x.get('Id'):x.get('Target') for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheets={}
    for sheet in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS):
        rel=sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id');path=rels[rel];path=path.lstrip('/') if path.startswith('/') else 'xl/'+path;rows=[]
        for r in ET.fromstring(z.read(path)).find('m:sheetData',NS):
            cells={}
            for c in r:
                if c.tag!='{'+NS['m']+'}c':continue
                v=c.find('m:v',NS);value=v.text if v is not None else None
                if c.get('t')=='s' and value is not None:value=ss[int(value)]
                elif c.get('t')=='inlineStr':value=''.join(t.text or '' for t in c.findall('.//m:t',NS))
                cells[c.get('r')]=dict(value=value,type=c.get('t'),formula=c.findtext('m:f',namespaces=NS))
            rows.append(dict(source_row=int(r.get('r')),cells=cells))
        sheets[sheet.get('name')]=dict(zip_path=path,rows=rows)
    return sid,m,sheets

def main():
    context={};controls={};anomalies=[];county_all={};native_all={}
    for year in [2024,2022,2020]:
        sid,m,sheets=workbook(year);rows=sheets['Precinct-Results']['rows'];raw_header={re.sub(r'\d+$','',k):v['value'] for k,v in rows[0]['cells'].items()};dups={k for k,n in collections.Counter(raw_header.values()).items() if n>1};header={k:v+('__'+k if v in dups else '') for k,v in raw_header.items()}
        county_lookup={}
        for r in sheets['Counties']['rows'][1:]:
            a={re.sub(r'\d+$','',k):v['value'] for k,v in r['cells'].items()}
            if a.get('A','').isdigit():county_lookup[a['A']]=(a['B'],a['C'])
        assert len(county_lookup)==87
        records=[];missing=[]
        for r in rows[1:]:
            vals={header[re.sub(r'\d+$','',k)]:v['value'] for k,v in r['cells'].items()}
            if vals.get('VTDID') in [None,'','End of worksheet']:continue
            assert re.fullmatch('[0-9]{9}',vals['VTDID'])
            cname,fips=county_lookup[vals['COUNTYCODE']];assert cname==vals['COUNTYNAME'].upper() and vals['VTDID']==fips+vals['PCTCODE']
            rec=dict(source_id=sid,election_date=DATES[year],source_sheet='Precinct-Results',source_row=str(r['source_row']),native_key=f"MN:{year}:VTDID:{vals['VTDID']}",county_key='MN:county:'+fips,county_fips=fips)
            rec.update({v:vals.get(v) for v in header.values()});records.append(rec)
            absent=[col for col,name in header.items() if name not in vals or vals[name] is None]
            if absent:missing.append(dict(source_row=r['source_row'],columns=absent))
        assert len({r['native_key'] for r in records})==len(records)
        assert len({(r['county_fips'],r['PCTCODE']) for r in records})==len(records)
        fields=METHOD.copy()
        if year==2022:fields.remove('PRESONLYAB');prefixes=['MNGOV']
        elif year==2024:prefixes=['USSEN','USPRS']
        else:prefixes=['USSEN','USPRS']
        fields += [x for x in header.values() if any(x.startswith(p) for p in prefixes)]
        assert all(re.fullmatch('[0-9]+',r.get(k) or '') for r in records for k in fields)
        for r in records:
            for p in prefixes:assert sum(int(r[k]) for k in fields if k.startswith(p) and k!=p+'TOTAL')==int(r[p+'TOTAL'])
            methods=sum(int(r[k]) for k in ['SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB'] if k in r)
            if methods!=int(r['TOTVOTING']):anomalies.append(dict(year=year,native_key=r['native_key'],source_row=r['source_row'],county_fips=r['county_fips'],PCTNAME=r['PCTNAME'],method_sum=methods,TOTVOTING=int(r['TOTVOTING']),method_minus_TOTVOTING=methods-int(r['TOTVOTING'])))
        counties=[];municipal=[]
        for fips in sorted({r['county_fips'] for r in records}):
            rr=[r for r in records if r['county_fips']==fips];first=rr[0];base=dict(county_key=first['county_key'],county_fips=fips,COUNTYCODE=first['COUNTYCODE'],COUNTYNAME=first['COUNTYNAME'],native_units=len(rr));base.update({k:sum(int(r[k]) for r in rr) for k in fields});counties.append(base)
            for name in sorted({r['MCDNAME'] for r in rr}):
                units=[r for r in rr if r['MCDNAME']==name];v=dict(county_key=first['county_key'],county_fips=fips,COUNTYCODE=first['COUNTYCODE'],COUNTYNAME=first['COUNTYNAME'],MCDNAME=name,native_units=len(units));v.update({k:sum(int(r[k]) for r in units) for k in fields});municipal.append(v)
        writecsv(H/f'native-{year}.csv.gz',records);writecsv(H/f'county-controls-{year}.csv',counties);writecsv(H/f'municipal-controls-{year}.csv.gz',municipal)
        context[str(year)]=dict(source_id=sid,source_sha256=m['raw_sha256'],source_bytes=m['bytes'],source_worksheet=sheets['Precinct-Results']['zip_path'],columns=header,original_columns=raw_header,duplicate_labels=sorted(dups),metadata={k:v for k,v in sheets.items() if k!='Precinct-Results'},missing_native_cells=missing,raw_all_offices='Complete original workbook referenced by hash; all native columns retained without interpreting unrelated offices')
        controls[str(year)]=dict(source_id=sid,native_rows=len(records),counties=len(counties),municipal_source_groups=len(municipal),sums={k:sum(int(r[k]) for r in records) for k in fields},method_discrepancy_rows=sum(r['year']==year for r in anomalies),method_minus_TOTVOTING=sum(r['method_minus_TOTVOTING'] for r in anomalies if r['year']==year))
    dump(S/'workbook-context.json',context);dump(S/'extraction-controls.json',controls);writecsv(S/'method-discrepancies.csv',anomalies)
    print(json.dumps(controls,indent=2))
if __name__=='__main__':main()
