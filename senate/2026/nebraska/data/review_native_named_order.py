"""Coordinator original-byte replay; no question-worker imports or vote inputs."""
from pathlib import Path
from collections import Counter,defaultdict
import gzip,hashlib,json,re,subprocess,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'/tmp/snn-xls-reading-libs')
import xlrd
from bs4 import BeautifulSoup
DATA=Path(__file__).resolve().parent;STATE=DATA.parent;NEWS=DATA/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
    b=p.read_bytes();return dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b))
def save_frozen(p,b):
    if p.exists():assert p.read_bytes()==b
    else:p.write_bytes(b)
def main():
    manifest=json.loads((NEWS/'manifest.json').read_bytes());sources={p['id']:p for p in manifest};used={}
    def original(p):
        z=(NEWS/p['asset']).read_bytes();b=gzip.decompress(z);assert sha(z)==p['stored_sha256']and sha(b)==p['raw_sha256']and len(b)==p['bytes'];used[p['id']]=p;return b
    # This old coordinator discovery body supplies only selected original receipts.
    # Every vote, label and source-row field below is reparsed from those originals.
    discovery=json.loads((DATA/'coordinator-2024-archived-native-preflight.json').read_bytes());units=[];counts=Counter();county=defaultdict(lambda:[0,0]);admin=0
    for a in discovery['county_observations']:
        if not a['entity_complete']:continue
        source=a['source_pin'];dom=BeautifulSoup(original(source),'html.parser');header=dom.find('tr',id='ContentPlaceHolder1xuwgCounty_r_0');cc=header.find_all(['td','th'],recursive=False);cty=cc[2].get_text(' ',strip=True);name=cc[1].get_text(' ',strip=True).split(' County Precincts Reporting:')[0]
        assert name not in('Douglas','Lancaster')
        for tr in dom.find_all('tr',id=re.compile(r'^ContentPlaceHolder1xuwgPrecinct_r_\d+$')):
            cc=tr.find_all(['td','th'],recursive=False);native=cc[2].get_text(' ',strip=True);label=cc[1].get_text(' ',strip=True)
            vals=[]
            for i in range(2):
                row=dom.find('tr',id=tr['id']+'_'+str(i));cells=row.find_all(['td','th'],recursive=False);vals.append(int(cells[4].get_text(' ',strip=True).replace(',','')))
            assert dom.find('tr',id=tr['id']+'_2')is None
            if native=='_TOT':admin+=1;continue
            key=f'NE:2024-special:html:{cty}:{native}';units.append(dict(key=key,county=name,literal_label=label,source_id=source['id'],raw_sha256=source['raw_sha256'],source_position=tr['id'],R_L=vals,generic_marks=None));counts['HTML']+=1
    src=sources['county-douglas-2024-native-xls'];book=xlrd.open_workbook(file_contents=original(src));s=book.sheet_by_name('U.S. Senator - 2-Yr Term');headers=s.row_values(1);rcol=next(i for i,h in enumerate(headers)if str(h).startswith('Pete Ricketts'));lcol=next(i for i,h in enumerate(headers)if str(h).startswith('Preston Love'));wcol=next(i for i,h in enumerate(headers)if str(h).startswith('Write-ins'))
    end=next(i for i in range(s.nrows)if s.cell_value(i,0)in('Totals','Total'))
    for i in range(2,end):
        label=s.cell_value(i,0);vals=[s.cell_value(i,j)for j in(rcol,lcol,wcol)];assert all(int(v)==v for v in vals)
        units.append(dict(key='NE:2024-special:douglas-biff:'+label,county='Douglas',literal_label=label,source_id=src['id'],raw_sha256=src['raw_sha256'],source_position=dict(sheet=s.name,row_1based=i+1),R_L=list(map(int,vals[:2])),generic_marks=int(vals[2])));counts['BIFF']+=1
    src=sources['county-lancaster-2024-final-precinct-pdf-actual-archive'];pdf=original(src);text=subprocess.run(['pdftotext','-layout','-','-'],input=pdf,capture_output=True,check=True).stdout.decode('utf8','replace');pages=text.split('\f');assert len(pages)==1432 and not pages[-1].strip()
    for page,text in enumerate(pages[:-1],1):
        if not re.search(r'^\s*US Senator 2 YR\s*$',text,re.M):continue
        label=re.search(r'Lancaster County, Nebraska\s*\n\s*\n([^\n]+)',text)[1].strip();section=text.split('US Senator 2 YR',1)[1].split('Contest Totals',1)[0];vectors={}
        for name in ['Rep Pete Ricketts','Dem Preston Love Jr.','Write-In Totals','Not Assigned']:
            line=next(l for l in section.splitlines()if re.match(r'^\s*'+re.escape(name)+r'\s+',l));m=re.fullmatch(r'\s*'+re.escape(name)+r'\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s*',line);assert m
            vectors[name]=[int(v.replace(',',''))for v in m.groups()];assert vectors[name][0]==sum(vectors[name][1:])
        assert vectors['Write-In Totals']==vectors['Not Assigned']
        units.append(dict(key=f'NE:2024-special:lancaster-pdf:page-{page}',county='Lancaster',literal_label=label,source_id=src['id'],raw_sha256=src['raw_sha256'],source_position=dict(actual_pdf_page=page),R_L=[vectors['Rep Pete Ricketts'][0],vectors['Dem Preston Love Jr.'][0]],generic_marks=vectors['Write-In Totals'][0],all_original_candidate_method_vectors=vectors));counts['PDF']+=1
    assert counts==dict(HTML=895,BIFF=233,PDF=198)and len(units)==len({p['key']for p in units})==1326,(dict(counts),len(units),len({p['key']for p in units}))
    for p in units:
        for i,v in enumerate(p['R_L']):county[p['county']][i]+=v
    controls=json.loads((DATA/'coordinator-primary-preflight.json').read_bytes())['tables']['2024_Senate_ClassII_two_year']['county_rows'];assert len(county)==93
    for name,vals in county.items():assert vals==controls[name]['votes']
    assert [sum(p['R_L'][i]for p in units)for i in range(2)]==[585103,349902]
    named=sorted(units,key=lambda p:(-sum(p['R_L']),p['key']));D=935005
    def prefix(order,volume,denominator):
        n=0;s=0
        while 5*s<4*denominator:s+=volume(order[n]);n+=1
        return dict(count=n,votes=s,preceding=s-volume(order[n-1]),crossing=order[n-1]['key'])
    crossing=prefix(named,lambda p:sum(p['R_L']),D);assert crossing==dict(count=765,votes=748190,preceding=747645,crossing='NE:2024-special:lancaster-pdf:page-685')
    assert sum(sum(p['R_L'])for p in named[:15])==26773
    observed=sum(p['generic_marks']for p in units if p['generic_marks']is not None);assert observed==1078
    partial=sorted(units,key=lambda p:(-sum(p['R_L'])-(p['generic_marks']if p['generic_marks']is not None else 0),p['key']));v=lambda p:sum(p['R_L'])+(p['generic_marks']if p['generic_marks']is not None else 0)
    part=prefix(partial,v,D+observed);assert part['count']==765 and part['votes']==749234
    removed=set(p['key']for p in named[:765])-set(p['key']for p in partial[:765]);added=set(p['key']for p in partial[:765])-set(p['key']for p in named[:765]);assert removed=={'NE:2024-special:html:39:0003'}and added=={'NE:2024-special:lancaster-pdf:page-419'}
    assert 5*748190>=4*(D+232) and 5*748190<4*(D+233)
    assert 5*(747645+1794)<4*(D+1794) and 5*(747645+1795)>=4*(D+1795)
    qa=DATA/'coordinator-qa/initial-native-named-order-v1';qa.mkdir(parents=True,exist_ok=True)
    transcript=(json.dumps(named,ensure_ascii=False,indent=2)+'\n').encode();outpath=qa/'original-derived-full1326.json.gz';save_frozen(outpath,gzip.compress(transcript,mtime=0))
    peerpath=DATA/'turnout/extracts/selected-native-disjoint.jsonl.gz';peerbody=peerpath.read_bytes();peer=[json.loads(l)for l in gzip.decompress(peerbody).splitlines()];save_frozen(qa/'turnout-selected-native-at-review.jsonl.gz',peerbody)
    assert [p['key']for p in peer]==[p['key']for p in named]
    for a,b in zip(named,peer):assert a['R_L']==b['candidate_values']and a['generic_marks']==b['generic_writeins']and a['county']==b['county']
    out=dict(status='pass_independent_original_named_native_order_with_unresolved_writein_scope',source_originals=list(used.values()),complete_HTML_entities=91,complete_PDF_pages=1431,selected_BIFF_sheet='U.S. Senator - 2-Yr Term',counts=dict(counts),full_native=1326,parent_counties=93,source_named_candidate_controls=[585103,349902],source_named_denominator=D,top15_native=26773,named_crossing=crossing,remainder_native=561,remainder_named_votes=186815,original_derived_transcript=pin(outpath),compared_peer_body=pin(qa/'turnout-selected-native-at-review.jsonl.gz'),source_order_and_candidate_generic_fields_exact=True,unknown_HTML_generic_fields=895,partial_observed_generic_marks=observed,partial_scenario=dict(denominator=D+observed,prefix=part,removed=sorted(removed),added=sorted(added)),eligible_writein_membership_robustness_established=False,algebra=dict(additional_eligible_wholly_outside_fixed765_to_fail=233,additional_eligible_wholly_inside_fixed764_to_pass=1795),no_current_identity_or_formal_dispatch_approval=True,qualification='Original-byte extraction imports no worker module or producer votes. Existing coordinator discovery receipts identify originals only; namedvotes/nativekeys/labels and availablegeneric/methodfields freshly parsed. Partialscenario adds only1078observedmarks as arithmetic;895unprintedgeneric staynull in source records, not datazero. Eligiblemarkvalidity/universe/wholecandidate minimum not established. All93county named controls close independently. This bounded review is not final worker freeze or fulladditional source/method/ballot/registration agreement.')
    p=DATA/'coordinator-initial-native-named-order-review.json';b=(json.dumps(out,indent=2)+'\n').encode();save_frozen(p,b);print(json.dumps(pin(p)))
if __name__=='__main__':main()
