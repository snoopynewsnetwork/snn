#!/usr/bin/env python3
"""Only required county registration/returned-ballot totals; no demographics."""
from pathlib import Path
import csv,gzip,json,re
OUT=Path(__file__).resolve().parents[1]
SRC=OUT/'source'/'acquired'
def main():
    counties={r['county']:r['county_fips']for r in json.loads((OUT/'source'/'county-wide.json').read_bytes())}
    rows=[];footers=[]
    for year,page,key in [(2020,5,'sos-2020-participation-archived'),(2022,5,'sos-2022-participation-archived'),(2024,6,'sos-2024-participation-archived-20241227')]:
        text=gzip.decompress((SRC/(key+'.layout.txt.gz')).read_bytes()).decode().split('\f')[page-1]
        ns=2 if year==2024 else 4
        pat=re.compile(r'^\s*([A-Za-z ]+?)\s+(\d.+?)\s*$')
        ys=[];ft=[]
        for i,line in enumerate(text.splitlines(),1):
            m=pat.match(line)
            if not m:continue
            name=m[1].strip()
            if name not in counties and name.lower()!='total':continue
            nums=re.sub(r'[\d.]+%','',m[2]).split()
            assert len(nums)==ns and all(re.fullmatch(r'[\d,]+',t)for t in nums),(year,line,nums)
            values=[int(v.replace(',',''))for v in nums]
            r=dict(year=year,county=name,county_fips=counties.get(name,''),
                registration_Number_Eligible=values[-2],ballots_Returned=values[-1],
                scope='official statistical summary total; Ballots Returned, not canvass ballots cast',
                source_key=key,PDF_page=page,text_line_1based=i,raw_line=line)
            (ft if name.lower()=='total'else ys).append(r)
        assert len(ys)==36 and len(ft)==1
        for field in ['registration_Number_Eligible','ballots_Returned']:
            assert sum(r[field]for r in ys)==ft[0][field]
        rows+=ys;footers+=ft
    with (OUT/'participation-controls.csv').open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (OUT/'source'/'participation-footers.json').write_text(json.dumps(footers,indent=2)+'\n')
    print([{k:r[k]for k in ['year','registration_Number_Eligible','ballots_Returned']}for r in footers])
if __name__=='__main__':main()
