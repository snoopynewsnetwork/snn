#!/usr/bin/env python3
"""Optional online refresh to a NEW owned directory; follows actual public forms.

Default verifies frozen source originals, offline. --refresh DIRECTORY acquires
fresh original entities there, never overwriting the launch or shared evidence.
"""
import argparse,gzip,json
from pathlib import Path
from urllib.parse import urlencode,urljoin
import acquire
from build_turnout import HTML,source_read
P=Path(__file__).resolve().parent
def main():
    a=argparse.ArgumentParser();a.add_argument('--refresh',type=Path);args=a.parse_args()
    pins=json.loads((P/'source/shared-originals.json').read_bytes())
    for pin in pins:source_read(pin)
    if args.refresh is None:print('All frozen source original bytes verified offline.');return
    dest=args.refresh.resolve();assert dest.is_relative_to(P.resolve())
    assert not dest.exists(),'Refresh directory must be new.'
    (dest/'source').mkdir(parents=True);acquire.D=dest
    root='https://electionstats.state.ma.us/index.php';acquire.fetch(root,'pd43-root')
    doc=HTML(gzip.decompress((dest/'source/pd43-root.body.gz').read_bytes())).root
    form=next(f for f in doc.descendants('form')if any(n.attrs.get('name')=='office_id'for n in f.descendants('select')))
    assert form.attrs['method'].lower()=='get'
    select=next(n for n in form.descendants('select')if n.attrs.get('name')=='office_id')
    opts={n.text():n.attrs['value']for n in select.descendants('option')}
    for year,office,tag in [(2024,'U.S. Senate','2024-senate'),(2020,'U.S. Senate','2020-senate'),(2022,'Governor','2022-governor'),(2024,'President','2024-president')]:
        url=urljoin(root,form.attrs['action'])+'?'+urlencode(dict(year_from=year,year_to=year,office_id=opts[office],stage='General'))
        acquire.fetch(url,tag+'-search','pd43-root')
        d=HTML(gzip.decompress((dest/'source'/f'{tag}-search.body.gz').read_bytes())).root
        matches=[tr for tr in d.descendants('tr',cls='election_item')if office in tr.text()and str(year)in tr.text()and 'Statewide'in tr.text()]
        links={urljoin(url,n.attrs['href'])for tr in matches for n in tr.descendants('a')if '/elections/view/'in n.attrs.get('href','')};assert len(links)==1
        view=next(iter(links));acquire.fetch(view,tag+'-view',tag+'-search')
        d=HTML(gzip.decompress((dest/'source'/f'{tag}-view.body.gz').read_bytes())).root
        for v,scope in [('0','municipal'),('1','precinct')]:
            links={urljoin(view,n.attrs['href'])for n in d.descendants('a')if '/elections/download/'in n.attrs.get('href','')and 'precincts_include:'+v in n.attrs['href']};assert len(links)==1
            acquire.fetch(next(iter(links)),tag+'-'+scope+'-csv',tag+'-view')
if __name__=='__main__':main()
