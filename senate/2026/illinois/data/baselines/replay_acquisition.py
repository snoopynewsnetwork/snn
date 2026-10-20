"""Optional fresh HTTP replay; offline reproduction never needs network.

Follows literal archived parent hrefs and verified current selector onchange.
New captures receive a UTC prefix; archived sources are never overwritten.
Supports --county-pages, --csv-pages, --metadata-pages. No guessed IDs/events.
"""
import argparse,datetime,gzip,json
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from acquire import fetch
from source_io import ROOT,pins,raw,dump
from extract import YEARS
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--county-pages',action='store_true');ap.add_argument('--csv-pages',action='store_true');ap.add_argument('--metadata-pages',action='store_true');args=ap.parse_args();out=[];prefix=datetime.datetime.now(datetime.timezone.utc).strftime('replay-%Y%m%dT%H%M%S-');UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36'
    def capture(sid,url,parent,method='GET',payload=None):
        r=requests.request(method,url,data=payload,headers={'User-Agent':UA},timeout=55);b=r.content;z=gzip.compress(b,mtime=0)
        from source_io import sha
        path='source/'+prefix+sid+'.gz';assert len(z)<40000000;(ROOT/path).write_bytes(z)
        a=dict(id=prefix+sid,url=url,method=method,parent_source_id=parent,public_form_fields=payload,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=r.status_code,final_url=r.url,headers=dict(r.headers),request_headers=dict(r.request.headers),redirects=[dict(url=h.url,status=h.status_code,headers=dict(h.headers))for h in r.history],path=path,bytes=len(b),raw_sha256=sha(b),stored_sha256=sha(z),compression='gzip');out.append(a);return a,b
    try:
        if args.csv_pages or args.county_pages:
            registry={x['id']:x for x in pins()}
            for y in YEARS:
                sid='sos-2024-county-totals'if y=='2024'else f'sos-observed-{y}-county-page';a,b=capture('county-'+y,registry[sid]['final_url'],sid);s=BeautifulSoup(b,'html.parser')
                if args.csv_pages:
                    title=YEARS[y][2];label=s.find(string=lambda z:z and z.strip()==title);assert label
                    link=label.find_parent('div').find_next('a',href=True);assert '\\Downloads\\'in link['href']
                    capture('csv-'+y,urljoin(a['final_url'],link['href'].replace('\\','/')),a['id'])
                if args.county_pages:
                    name='ctl00$ContentPlaceHolder1$ddlJurisdictions';sel=s.find('select',attrs={'name':name});assert '__doPostBack'in sel.get('onchange','')and name in sel['onchange']
                    form=sel.find_parent('form');base={x['name']:x.get('value','')for x in form.select('input[type=hidden][name]')}
                    for x in form.select('select[name]'):
                        o=x.find('option',selected=True)or x.find('option');base[x['name']]=o['value']
                    default=sel.find('option',selected=True)['value']
                    for o in sel.find_all('option'):
                        if o['value']==default:continue # populated original GET is the source; same-default POST clears grids.
                        payload={**base,name:o['value'],'__EVENTTARGET':name,'__EVENTARGUMENT':''};aa,bb=capture('county-'+y+'-'+o['value'],urljoin(a['final_url'],form.get('action')or a['final_url']),a['id'],'POST',payload)
                        ss=BeautifulSoup(bb,'html.parser');assert ss.find('select',attrs={'name':name}).find('option',selected=True)['value']==o['value']
        if args.metadata_pages:
            import csv
            for r in csv.DictReader((ROOT/'extract/statewide-source-rows.csv').open()):capture('detail-'+r['year']+'-'+r['table_row'],r['detail_url'],r['source_id'])
    finally:
        dump(ROOT/'source/registry.json.gz',pins()+out)
    print(json.dumps({'new_response_entities':len(out),'prefix':prefix,'status':'Fresh replay saved separately; no substitution into pinned historical baseline without review.'}))
if __name__=='__main__':main()
