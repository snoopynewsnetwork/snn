"""Extract source-scoped EAVS ballot/registration/method controls and SEMS active snapshots.

Missing survey codes are never zeroed. County source row and raw strings retained.
Raw originals include unrelated fields without gratuitous derivative demographic tables.
"""
import csv,gzip,io,json,re,zipfile,xml.etree.ElementTree as ET
import fitz
from acquire_sources import BASE,OUT,receipts,source,savejson

def numeric(v):return int(v) if re.fullmatch(r'\d+',v) else None
def main():
    records=[];controls=[];fips_aliases={};codebooks=[]
    for year,start in [('2022','eac-2022-csv-2022'),('2024','eac-2024-csv-csv')]:
        r=next(r for r in receipts if r['id'].startswith(start));z=zipfile.ZipFile(io.BytesIO(source(r['id'])));member=next(x for x in z.namelist() if x.endswith('.csv'))
        rr=list(csv.DictReader(io.StringIO(z.read(member).decode('utf-8-sig'))));ms=[(i+2,x) for i,x in enumerate(rr) if x['State_Abbr']=='MS'];assert len(ms)==82 and len({x['FIPSCode'] for _,x in ms})==82
        fields=['A1a','A1b','A1c','A1d','A1d_Other','A1Comments','F1a','F1b','F1c','F1d','F1e','F1f','F1g','F1h','F1h_Other','F1i','F1i_Other','F1Comments']+[k for k in rr[0] if re.fullmatch(r'F2.*',k)]
        for pos,row in ms:
            fips=row['FIPSCode'][:5];assert len(fips)==5 and fips.startswith('28')
            fips_aliases[row['Jurisdiction_Name'].replace(' COUNTY','')]=fips
            for field in fields:
                if field not in row:continue
                raw=row[field];value=numeric(raw)
                records.append(dict(year=year,fips=fips,jurisdiction_literal=row['Jurisdiction_Name'],field=field,raw_value=raw,value=value,status='reported' if value is not None else 'source_missing_code' if raw.startswith('-') else 'text_or_blank',source_id=r['id'],archive_member=member,source_row=pos))
        cc=dict(year=year,source_id=r['id'],counties=len(ms),fields={})
        for field in fields:
            if field.endswith(('Comments','Other')):continue
            vals=[row[field] for _,row in ms if field in row];reported=[numeric(v) for v in vals if numeric(v) is not None]
            cc['fields'][field]=dict(reported_count=len(reported),reported_sum=sum(reported),source_code_counts={v:vals.count(v) for v in sorted(set(vals)) if numeric(v) is None})
        controls.append(cc)
    county=list(csv.DictReader((BASE/'data/county-turnout.csv').open()))
    for row in county:
        alias=row['county'].upper().replace('JEFF DAVIS','JEFFERSON DAVIS')
        assert row['fips']==fips_aliases[alias],(row['county'],row['fips'],fips_aliases[alias])
    with (OUT/'participation-controls.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    for r in receipts:
        if not r['id'].startswith(('eac-2022-codebook-2022','eac-2024-codebook-data')):continue
        z=zipfile.ZipFile(io.BytesIO(source(r['id'])));strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        for name in z.namelist():
            if not re.fullmatch(r'xl/worksheets/sheet\d+.xml',name):continue
            for row in ET.fromstring(z.read(name)).findall('m:sheetData/m:row',ns):
                values={}
                for c in row.findall('m:c',ns):
                    v=c.find('m:v',ns);v=v.text if v is not None else '';values[c.attrib['r']]=strings[int(v)] if c.attrib.get('t')=='s' and v else v
                if any(re.fullmatch(r'(A1[a-d]|A1Comments|F1[a-i]|F1[a-i]_Other|F1Comments|F2.*)',v) for v in values.values()):codebooks.append(dict(source_id=r['id'],member=name,source_cells=values))
    active=[]
    for r in receipts:
        if not r['id'].startswith('sos-registration-'):continue
        doc=fitz.open(stream=source(r['id']),filetype='pdf')
        for i,p in enumerate(doc):
            text=p.get_text();pattern=r'(?m)^(\d{2}) - ([^\n]+)\n([\d,]+)\n([\d,]+)\n([\d.]+)%'
            for m in re.finditer(pattern,text):
                code,label,pop,reg,pct=m.groups();alias=label.upper().replace('*','').replace('JEFF DAVIS','JEFFERSON DAVIS');active.append(dict(source_id=r['id'],source_page=i+1,source_county_code=code,county_literal=label,fips=fips_aliases[alias],reference_population_literal=pop,active_voters=int(reg.replace(',','')),source_percent_literal=pct,definition='SEMS active-voter monthly publication; not certified ballots or total registration; source first-Monday monthly policy'))
        assert sum(x['source_id']==r['id'] for x in active)==82
    with (OUT/'active-registration.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(active[0]));w.writeheader();w.writerows(active)
    savejson(OUT/'participation-summary.json',dict(eavs=controls,active_snapshots={sid:sum(x['active_voters'] for x in active if x['source_id']==sid) for sid in sorted({x['source_id'] for x in active})},scope='Different source dates/definitions; never rescale candidate votes to survey totals.',codebook_cells=codebooks))
    print(json.dumps(dict(controls=controls,active_rows=len(active))))

if __name__=='__main__':main()
