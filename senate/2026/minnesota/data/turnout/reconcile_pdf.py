"""Read-only independent 2020 canvass comparison of every available county control."""
import csv, gzip, json, re, subprocess
from pathlib import Path
from extract import shared, HERE, dump, csvwrite

def main():
    raw,_=shared('sos-2020-canvass-original')
    result=subprocess.run(['pdftotext','-layout','-','-'],input=raw,stdout=subprocess.PIPE,check=True).stdout.decode()
    # Source PDF byte hash verified before invoking Poppler; retain only needed tables.
    a=result.index('Minnesota Voter Statistics');b=result.index('U.S. President & Vice President',a)
    c=result.index('U.S. Senator',b);d=result.index('U.S. Representative',c)
    chunks={'statistics':result[a:b],'senate':result[c:d]}
    (HERE/'source/canvass-2020-required-tables.txt').write_text('\n'.join(chunks.values()))
    expected={r['COUNTYNAME'].casefold():r for r in csv.DictReader((HERE/'county-controls-2020.csv').open())}
    rows=[]
    for kind,chunk in chunks.items():
        for line in chunk.splitlines():
            m=re.fullmatch(r'\s*([A-Za-z. ]+?)\s+([\d,]+(?:\s+[\d,]+)*)\s*',line)
            if not m:continue
            name=m[1].strip();nums=[int(t.replace(',','')) for t in m[2].split()]
            if name.casefold() not in expected:continue
            r=expected[name.casefold()]
            fields=['REG7AM','EDR','AB_MB','FEDONLYAB','PRESONLYAB','TOTVOTING'] if kind=='statistics' else (['USSENLMN','USSENGLC','USSENR','USSENDFL'] if len(nums)==4 else ['USSENWI'])
            assert len(fields)==len(nums),(name,nums)
            for field,n in zip(fields,nums):
                rows.append(dict(county_fips=r['county_fips'],pdf_county_label=name,field=field,pdf=n,workbook=int(r[field]),difference=int(r[field])-n))
    assert len(rows)==87*11,len(rows)
    assert len({(r['county_fips'],r['field']) for r in rows})==len(rows)
    assert all(r['difference']==0 for r in rows),[r for r in rows if r['difference']]
    dump(HERE/'source/canvass-2020-reconciliation.json',dict(status='pass',source_id='sos-2020-canvass-original',county_count=87,county_fields_compared=len(rows),rows=rows))
    appendix=result.index('2020 STATE GENERAL ELECTION WRITE-INS')
    start=result.index('U.S. Senator',appendix);stop=result.index('U.S. Representative',start)
    named=result[start:stop]
    (HERE/'source/canvass-2020-senate-named-writeins.txt').write_text(named)
    names=['Josh D. Ondich','John Berman','George A. Dennis Jr','Stephen W Carlson','Jason U. Shaver','Rob Barrett, Jr.']
    namedrows=[]
    for line_index,line in enumerate(named.split('\n')):
        m=re.fullmatch(r'\s*([A-Za-z. ]+?)\s+([\d,]+(?:\s+[\d,]+)*)\s*',line)
        if not m or m[1].strip().casefold() not in expected:continue
        county=m[1].strip();nums=[int(t.replace(',','')) for t in m[2].split()]
        assert len(nums) in [4,2]
        r=expected[county.casefold()]
        for column,(name,n) in enumerate(zip(names[:4] if len(nums)==4 else names[4:],nums),1):
            namedrows.append(dict(county_fips=r['county_fips'],source_county_label=county,source_candidate_label=name,votes=n,
                                  pdftotext_line=result[:start].count('\n')+line_index+1,source_table_candidate_column=column,
                                  source_id='sos-2020-canvass-original',source_scope='2020 STATE GENERAL ELECTION WRITE-INS; printed appendix pages 17-22 of 24',
                                  native_allocation='unavailable',relationship_to_generic_WI='separate overlapping named report; never additive to USSENWI'))
    assert len(namedrows)==522 and len({(r['county_fips'],r['source_candidate_label']) for r in namedrows})==522
    totals={name:sum(r['votes'] for r in namedrows if r['source_candidate_label']==name) for name in names}
    assert list(totals.values())==[0,2,5,3,0,22]
    csvwrite(HERE/'source/named-writeins-2020.csv',namedrows,list(namedrows[0]))
    dump(HERE/'source/named-writeins-2020-controls.json',dict(source_id='sos-2020-canvass-original',county_count=87,explicit_county_candidate_cells=522,candidate_totals=totals,
         named_report_total=32,generic_workbook_WI=2261,scope_residual=2229,residual_status='unattributed; not classified invalid, eligible, blank, under or over',native_allocation='unavailable'))
    # Render the first county statistics page and first Senate page at a modest scale.
    for number,name in [(2,'2020-statistics-preview'),(13,'2020-senate-preview'),(result[:start].count('\f')+1,'2020-named-writeins-preview')]:
        subprocess.run(['pdftoppm','-f',str(number),'-l',str(number),'-scale-to','1400','-png','-singlefile','-',str(HERE/'source'/name)],input=raw,stdout=subprocess.DEVNULL,check=True)
    print('2020: 957 county-field comparisons, zero differences')

if __name__=='__main__':main()
