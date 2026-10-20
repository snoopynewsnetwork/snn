import json,gzip
from urllib.parse import urljoin,urlencode
from bs4 import BeautifulSoup
from extract_originals import ROOT,originals,TAGS,sid,dump
def main():
    src=originals();root=src['sos-pd43-root'];doc=BeautifulSoup(root[1],'html.parser');form=doc.select_one('#search_form_elections form');assert form and form['method'].lower()=='get';chains=[]
    for tag in TAGS:
        view=src[sid(tag,'view')];d=BeautifulSoup(view[1],'html.parser');anchors=[urljoin(view[0]['final_url'],a['href']) for a in d.select('a[href]')]
        for scope in ['municipal','precinct']:assert src[sid(tag,scope+'-csv')][0]['url'] in anchors
        chain=dict(contest=tag,parent_root=root[0]['url'],view=view[0]['url'],downloads={scope:src[sid(tag,scope+'-csv')][0]['url'] for scope in ['municipal','precinct']},literal_download_anchors_verified=True)
        if tag!='2024-senate':
            search=src[sid(tag,'search')];q=BeautifulSoup(search[1],'html.parser');office={'2020-senate':'U.S. Senate','2022-governor':'Governor','2024-president':'President'}[tag];year=tag[:4]
            opt=[o for o in form.select('select[name=office_id] option') if o.get_text(' ',strip=True)==office];assert len(opt)==1
            fields=dict(year_from=year,year_to=year,office_id=opt[0]['value'],stage='General')
            assert search[0]['url']==urljoin(root[0]['url'],form['action'])+'?'+urlencode(fields)
            links=[a for a in q.select('tr.election_item a[href]') if urljoin(search[0]['url'],a['href'])==view[0]['url']];assert links
            assert office in links[0].find_parent('tr',class_='election_item').get_text(' ',strip=True)
            chain.update(search=search[0]['url'],literal_form_fields=fields,literal_search_view_anchor_verified=True)
        else:chain['initial_view_discovery']='Exact supplied official2024 Senate view, independently browsed; no invented search route'
        chains.append(chain)
    for key in ['worcester-authority','worcester-stream','2022-senate-search','classII','plurality-law','senate-schedule-law']:
        r=json.loads((ROOT/'source/http-network'/f'{key}.receipt.json').read_text());assert r['status']==200
    r=json.loads((ROOT/'source/http-network/2022-senate-search.receipt.json').read_text());text=BeautifulSoup(gzip.decompress((ROOT/r['stored_path']).read_bytes()),'html.parser')
    matches=[]
    for row in text.select('tr.election_item'):
        t=row.get_text(' ',strip=True)
        if 'U.S. Senate' in t and 'Statewide' in t and '2022' in t:matches.append(t)
    assert not matches
    dump(ROOT/'source/source-chain-checks.json',dict(status='pass',chains=chains,no_2022_statewide_US_Senate_election_items=True,receipt_qualifications='News launch receipts are frozen individually. When early receipts omit redirects/parent/status clocks, omission remains unknown; no later value is invented. Own direct HTTP attempts retain full redirect/header/UTC/error/status entities. Browser representations are separate from original bytes.'))
if __name__=='__main__':main()
