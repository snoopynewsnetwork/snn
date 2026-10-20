#!/usr/bin/env python3
"""Retain actual 2024 vice-president columns without adding to president."""
from pathlib import Path
import csv,gzip,json,re
OUT=Path(__file__).resolve().parents[1]
def main():
    pg=gzip.decompress((OUT/'source/2024-abstract.layout.txt.gz').read_bytes()).decode().split('\f')[1]
    assert 'US Vice President'in pg
    headers=['Shanahan / Nicole (WTP)','ter Maat / Mike (L)','Vance / JD (R)','Ware / Rudolph (PG)','**Walz / Tim (D)','Misc.']
    ps=[0,2,4,5,6,7]
    original=list(csv.DictReader((OUT/'county-candidates.csv').open()))
    rows=[];footer=[]
    for i,l in enumerate(pg.splitlines(),1):
        m=re.fullmatch(r'\s*([A-Za-z ]+?)\s+'+r'\s+'.join([r'([\d,]+)']*6)+r'\s*',l)
        if not m:continue
        name=m[1].strip();vs=[int(x.replace(',',''))for x in m.groups()[1:]]
        if name.lower()=='total':footer=vs;continue
        for j,v in enumerate(vs):
            parent=next(r for r in original if r['contest']=='2024-president'and r['county']==name and int(r['column_index'])==ps[j])
            assert int(parent['votes'])==v
            rows.append(dict(county=name,county_fips=parent['county_fips'],office_literal='US Vice President',source_header_literal=headers[j],
                votes=v,nonadditive=True,overlaps_presidential_column=ps[j],source_key='2024-abstract',PDF_page=2,text_line_1based=i,raw_line=l))
    assert len(rows)==36*6 and [sum(r['votes']for r in rows if r['source_header_literal']==h)for h in headers]==footer
    with (OUT/'nonadditive-vice-president.csv').open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
