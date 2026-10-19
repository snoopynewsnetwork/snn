"""Original OOXML native candidate-universe/order witness; no worker imports."""
from pathlib import Path
from collections import defaultdict, Counter
import gzip, hashlib, io, json, zipfile
import xml.etree.ElementTree as E

D=Path(__file__).resolve().parent
S=D.parent
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
    b=p.read_bytes()
    return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))

def main():
    ledger=D/'news/manifest.json'
    receipts={r['id']:r for r in json.loads(ledger.read_bytes())}
    source=receipts['sos-2024-all-races-xlsx']
    p=D/'news'/source['asset'];z=p.read_bytes();raw=gzip.decompress(z)
    # Initial news receipts use bytes for the full decoded original length;
    # stored SHA pins the complete gzip, whose length is measured separately.
    assert len(z)<40_000_000 and sha(z)==source['stored_sha256']
    assert len(raw)==source['bytes'] and sha(raw)==source['raw_sha256']
    book=zipfile.ZipFile(io.BytesIO(raw));assert book.testzip() is None
    shared=[''.join(si.itertext()) for si in E.fromstring(book.read('xl/sharedStrings.xml')).findall('m:si',N)]
    groups=defaultdict(list)
    for row in E.fromstring(book.read('xl/worksheets/sheet1.xml')).findall('m:sheetData/m:row',N):
        cells={}
        for cell in row.findall('m:c',N):
            v=cell.find('m:v',N);value=v.text if v is not None else None
            if cell.get('t')=='s' and value is not None:value=shared[int(value)]
            cells[''.join(x for x in cell.attrib['r'] if x.isalpha())]=value
        if cells.get('D')=='United States President':
            groups[(cells['A'],cells['B'])].append(dict(row=int(row.attrib['r']),cells=cells))
    assert len(groups)==985 and len({x[0] for x in groups})==44
    units=[];categories=Counter();overunder=Counter()
    for (county,label),rows in groups.items():
        assert len(rows)==13
        candidate=[];noncandidate=[]
        for r in rows:
            c=r['cells'];value=int(c['G'])
            if c['F'] in ['Overvotes','Undervotes']:
                noncandidate.append(dict(source_row=r['row'],literal_category=c['F'],raw_party=c.get('E'),votes=value));overunder[c['F']]+=value
            else:
                candidate.append(dict(source_row=r['row'],literal_candidate=c['F'],raw_party=c.get('E'),votes=value));categories[(c.get('E'),c['F'])]+=value
        assert len(candidate)==11 and len(noncandidate)==2
        units.append(dict(literal_county=county,literal_native_label=label,
            first_source_row=min(r['row'] for r in rows),last_source_row=max(r['row'] for r in rows),
            candidate_fields=candidate,noncandidate_fields=noncandidate,
            candidate_total=sum(r['votes'] for r in candidate)))
    assert len(categories)==11 and sum(categories.values())==905057
    assert overunder==Counter({'Overvotes':1215,'Undervotes':11194})
    ordered=sorted(units,key=lambda r:(-r['candidate_total'],r['first_source_row']))
    cumulative=0;crossing=None
    for rank,u in enumerate(ordered,1):
        previous=cumulative;cumulative+=u['candidate_total']
        u.update(rank=rank,cumulative=cumulative)
        if crossing is None and 5*cumulative>=4*905057:crossing=rank
    assert crossing==528 and ordered[526]['cumulative']==723753 and ordered[527]['cumulative']==724515
    assert ordered[527]['literal_county']=='Shoshone County' and ordered[527]['literal_native_label']=='Osburn'
    assert (ordered[527]['first_source_row'],ordered[527]['last_source_row'],ordered[527]['candidate_total'])==(11741,11753,762)
    assert ordered[528]['candidate_total']<762 and ordered[526]['candidate_total']>762
    assert sum(r['candidate_total'] for r in ordered[:15])==65391
    out=dict(status='pass_original_named_candidate_native_order_with_source_limits',
        original_receipt=source,stored_original=pin(p),original_complete_raw_SHA256=sha(raw),
        source_worksheet='xl/worksheets/sheet1.xml',native=985,all_county_parents=44,
        candidate_categories=[dict(raw_party=k[0],literal_candidate=k[1],votes=v)for k,v in categories.items()],
        candidate_denominator=905057,noncandidate_totals=dict(overunder),
        top15_native_votes=65391,integer_ceiling80=(4*905057+4)//5,
        minimum80_native=528,previous527=723753,votes528=724515,remainder_units=457,
        remainder_votes=905057-724515,threshold_vote_tie=False,
        tie_order='descending complete candidate votes, then ascending original first source row; representation may differ from source-scoped worker key tie ordering',
        full_source_order=ordered,coordinator_dispatch_accepted=False,
        current_geography_approved=False,
        qualification='Complete original11-candidate/write-in named source universe. Over/undervotes separate, never valid votes. County sensitivities do not replace this985-native order. Stats986/Boundary ballot residuals are separate source controls; no allocation, current join, or legal feed admission follows.')
    target=D/'coordinator-initial-native-order-review.json'
    b=(json.dumps(out,indent=2,ensure_ascii=False)+'\n').encode()
    if target.exists():assert target.read_bytes()==b
    else:target.write_bytes(b)
    print(json.dumps(pin(target)))

if __name__=='__main__':main()
