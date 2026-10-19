#!/usr/bin/env python3
"""Read-only original replay; writes only this question's derivatives.

Uses Python3, Poppler and xlrd (external temporary installation permitted via
NE_XLRD_PATH; no dependencies/cache directories belong in delivered assets).
No producer/coordinator parser is imported, no mutable news manifest is read.
"""
import collections,csv,gzip,hashlib,io,json,os,pathlib,re,subprocess,sys
sys.dont_write_bytecode=True
if os.environ.get('NE_XLRD_PATH'):sys.path.insert(0,os.environ['NE_XLRD_PATH'])
import xlrd
from acquire import D,sha,readj,writej
from htmlkit import Tree
S=D.parent.parent
def jl(p):return [json.loads(x)for x in gzip.decompress(p.read_bytes()).splitlines()]
def cells(n):return [x for x in n.children if getattr(x,'tag',None)in ['td','th']]
def main():
    contract=readj(S/'data/turnout/priority-set.json');ledger=readj(S/'data/turnout/source/shared-news-ledger.json');receipts={x['id']:x for x in ledger};used={}
    def original(sid):
        r=receipts[sid];z=(S/'data/news'/r['asset']).read_bytes();raw=gzip.decompress(z)
        assert sha(z)==r['stored_sha256'] and len(raw)==r['bytes'] and sha(raw)==r['raw_sha256'];used[sid]=r;return raw
    def pdf(sid):return subprocess.run(['pdftotext','-layout','-','-'],input=original(sid),check=True,capture_output=True).stdout.decode().split('\f')[:-1]
    units=[];html_fields=0;admin=0
    sids=sorted({x['source_id']for x in contract['constituents']if x['source_kind']=='historical_state_HTML'})
    for sid in sids:
        raw=original(sid);assert b'</html>' in raw.lower();dom=Tree(raw.decode(errors='replace')).root
        rows={x.attrs['id']:x for x in dom.all('tr')if 'id'in x.attrs};h=cells(rows['ContentPlaceHolder1xuwgCounty_r_0']);cid=h[2].text();county=h[1].text().split(' County Precincts Reporting:')[0]
        for key,tr in rows.items():
            if not re.fullmatch(r'ContentPlaceHolder1xuwgPrecinct_r_\d+',key):continue
            cc=cells(tr);native=cc[2].text();vals=[]
            for i in [0,1]:
                rr=rows[key+'_'+str(i)];fc=cells(rr);vals.append(int(fc[4].text().replace(',','')));html_fields+=sum(len(n.attrs)+1 for n in fc)
            assert key+'_2'not in rows
            if native=='_TOT':admin+=1;continue
            units.append(dict(key=f'NE:2024-special:html:{cid}:{native}',county=county,values=vals,generic=None,source_id=sid,position=key,label=cc[1].literal_text()))
    books={}
    for year in [2024,2022,2020]:
        sid=f'county-douglas-{year}-native-xls';books[sid]=xlrd.open_workbook(file_contents=original(sid),formatting_info=True)
    rawrows=jl(S/'data/turnout/extracts/douglas-original-positions.jsonl.gz');rawcells=0
    for r in rawrows:
        sh=books[r['source_id']].sheet_by_name(r['sheet']);i=r['source_row_1based']-1
        assert sh.row_values(i)==r['values'] and list(sh.row_types(i))==r['cell_types'];rawcells+=len(r['values'])
    contexts=jl(S/'data/turnout/extracts/douglas-native.jsonl.gz');douglas_numeric=0
    for r in contexts:
        sh=books[r['source_id']].sheet_by_name(r['sheet']);row=sh.row_values(r['source_row_1based']-1);headers=sh.row_values(1);assert row[0]==r['native_label_literal']
        for f in r['candidate_fields']:
            i=f['source_column_1based']-1;assert row[i]==f['votes'] and headers[i]==f['label_literal'];douglas_numeric+=1
        for literal,key in [('Total Votes','reported_total_votes'),('Over Votes','over'),('Under Votes','under')]:assert row[headers.index(literal)]==r[key];douglas_numeric+=1
        assert all(r[k]is None for k in ['ballots','registration','blank'])
    sh=books['county-douglas-2024-native-xls'].sheet_by_name('U.S. Senator - 2-Yr Term');headers=sh.row_values(1);cols=[next(i for i,h in enumerate(headers)if str(h).startswith(s))for s in ['Pete Ricketts','Preston Love','Write-ins']]
    end=next(i for i in range(sh.nrows)if sh.cell_value(i,0)in ['Total','Totals'])
    for i in range(2,end):
        label=sh.cell_value(i,0);v=[int(sh.cell_value(i,j))for j in cols];units.append(dict(key='NE:2024-special:douglas-biff:'+label,county='Douglas',values=v[:2],generic=v[2],source_id='county-douglas-2024-native-xls',position=dict(sheet=sh.name,row_1based=i+1),label=label))
    sid='county-lancaster-2024-final-precinct-pdf-actual-archive';pages=pdf(sid);assert len(pages)==1431
    rowrx=re.compile(r'^\s*(.*?)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s*$');derived={};stats={}
    for page,text in enumerate(pages,1):
        label=re.search(r'Lancaster County, Nebraska\s*\n\s*\n([^\n]+)',text)[1].strip()
        if re.search(r'^Statistics\s+',text,re.M):
            reg=int(re.search(r'^Registered Voters - Total\s+(\d[\d,]*)',text,re.M)[1].replace(',',''));fields={}
            for literal in ['Ballots Cast - Total','Ballots Cast - Blank']:
                line=next(l for l in text.splitlines()if l.startswith(literal));m=rowrx.fullmatch(line);v=[int(x.replace(',',''))for x in m.groups()[1:]];assert v[0]==sum(v[1:]);fields[literal]=v
            stats[page]=dict(label=label,registration=reg,fields=fields)
        for contest in ['US President','US Senator 6 YR','US Senator 2 YR']:
            m=re.search(r'^\s*'+re.escape(contest)+r'\s*$',text,re.M)
            if not m:continue
            tail=text[m.end():];end=re.search(r'^\s*Contest Totals\s+.*$',tail,re.M);fields=[]
            for line in tail[:end.end()].splitlines():
                m=rowrx.fullmatch(line)
                if m:
                    v=[int(x.replace(',',''))for x in m.groups()[1:]];assert v[0]==sum(v[1:]);fields.append(dict(label_literal=m[1],counts=v))
            derived[page,contest]=fields
            f={x['label_literal']:x['counts']for x in fields}
            # Every method balances, avoiding the nested Not Assigned overlap.
            assert f['Write-In Totals']==f['Not Assigned']
            for method in range(4):
                candidates=[x for x in fields if x['label_literal'].startswith(('Rep ','Dem ','Lib ','Lmn ','Pet '))]
                assert sum(x['counts'][method]for x in candidates)+f['Write-In Totals'][method]==f['Total Votes Cast'][method]
                assert f['Total Votes Cast'][method]+f['Overvotes'][method]+f['Undervotes'][method]==f['Contest Totals'][method]
            if contest=='US Senator 2 YR':units.append(dict(key=f'NE:2024-special:lancaster-pdf:page-{page}',county='Lancaster',values=[f['Rep Pete Ricketts'][0],f['Dem Preston Love Jr.'][0]],generic=f['Write-In Totals'][0],source_id=sid,position=dict(actual_pdf_page=page),label=label))
    peer=jl(S/'data/turnout/extracts/lancaster-native-methods.jsonl.gz');assert len(peer)==len(derived)==595;methodcells=0
    for r in peer:
        fields=derived[r['actual_pdf_page'],r['contest_label_literal']];assert fields==[{k:f[k]for k in ['label_literal','counts']}for f in r['fields']];methodcells+=4*len(fields)
    ps=readj(S/'data/turnout/extracts/lancaster-statistics.json');assert len(ps)==len(stats)==199
    for r in ps:
        s=stats[r['actual_pdf_page']];assert s['label']==r['native_label_literal'] and s['registration']==r['registered_total'];assert s['fields']=={f['label_literal']:f['counts']for f in r['fields']}
    assert sum(x['registration']for x in stats.values())==206570 and sum(x['fields']['Ballots Cast - Total'][0]for x in stats.values())==161160
    resident=[s for s in stats.values()if s['label']=='New or Former Resident'];assert len(resident)==1 and resident[0]['registration']==0 and resident[0]['fields']['Ballots Cast - Total']==[1,0,1,0]
    assert collections.Counter('HTML'if ':html:'in u['key']else 'BIFF'if ':douglas-biff:'in u['key']else 'PDF'for u in units)==dict(HTML=895,BIFF=233,PDF=198)
    # Independently read county controls from the original state book, page17.
    text=pdf('sos-2024-canvass')[16];controls={}
    for line in text.splitlines():
        if line.startswith('General Election'):continue
        for m in re.finditer(r'([A-Za-z][A-Za-z .\'-]*?)\s+(\d[\d,]*)\s+(\d[\d,]*)(?=\s{2,}|$)',line):
            name=m[1].strip()
            if name not in ['Total','Page']:controls[name]=[int(m[2].replace(',','')),int(m[3].replace(',',''))]
    assert len(controls)==93,len(controls)
    groups=collections.defaultdict(lambda:[0,0])
    for u in units:
        for i,v in enumerate(u['values']):groups[u['county']][i]+=v
    assert dict(groups)==controls
    assert [sum(u['values'][i]for u in units)for i in [0,1]]==[585103,349902]
    units.sort(key=lambda u:(-sum(u['values']),u['key']));assert [u['key']for u in units]==contract['ordered_full_keys']
    for a,b in zip(units,contract['constituents']):assert a['key']==b['key'] and a['values']==b['candidate_values'] and a['generic']==b['generic_writeins'] and a['label']==b['native_label_literal'],(a,{k:b[k]for k in ['key','candidate_values','generic_writeins','native_label_literal']})
    assert sum(sum(x['values'])for x in units[:765])==748190 and sum(sum(x['values'])for x in units[:764])==747645
    assert sum(sum(x['values'])for x in units[:15])==26773 and sum(sum(x['values'])for x in units[765:])==186815
    observed=sum(u['generic']for u in units if u['generic']is not None);assert observed==1078
    alt=sorted(units,key=lambda u:(-sum(u['values'])-(u['generic'] or 0),u['key']));s=0;n=0
    while 5*s<4*(935005+observed):s+=sum(alt[n]['values'])+(alt[n]['generic']or 0);n+=1
    assert(n,s)==(765,749234);assert {x['key']for x in units[:765]}-{x['key']for x in alt[:765]}=={'NE:2024-special:html:39:0003'}
    assert {x['key']for x in alt[:765]}-{x['key']for x in units[:765]}=={'NE:2024-special:lancaster-pdf:page-419'}
    csvs=[]
    for sid in ['sos-2024-observed-public-all-csv-archive','sos-2024-observed-public-statewide-csv-archive']:
        rows=list(csv.reader(io.StringIO(original(sid).decode('utf-8-sig'))));assert len(rows[0])==15 and all(len(r)==16 and r[-1]==''for r in rows[1:]);sen=[r for r in rows[1:]if r[0]=='12464'];assert len(sen)==2;csvs.append(dict(source_id=sid,header=rows[0],rows=len(rows)-1,selected_complete_rows=sen,values=[int(x[11])for x in sen]))
    assert csvs[0]['values']==[585103,349902] and csvs[1]['values']==[577711,341868]
    out=dict(status='pass_original_replay_named_historical_scope',HTML_originals=91,HTML_native=895,HTML_admin_excluded=admin,HTML_raw_cell_attribute_checks=html_fields,Douglas_original_rows=len(rawrows),Douglas_raw_values_types=rawcells,Douglas_contexts=len(contexts),Douglas_numeric_fields=douglas_numeric,Lancaster_original_pages=len(pages),Lancaster_contexts=len(derived),Lancaster_method_cells=methodcells,Lancaster_statistics=len(stats),Lancaster_registration=206570,Lancaster_registration_difference_unallocated=164,Lancaster_ballots199=161160,Lancaster_Senate_ballots198=161159,resident_ballots=1,native_count=len(units),parent_count=len(groups),candidate_totals=[585103,349902],named_denominator=935005,minimum80=765,priority_votes=748190,preceding_votes=747645,top15_votes=26773,remainder_count=561,remainder_votes=186815,observed_generic=1078,unknown_generic_units=895,partial_sensitivity_membership_changed=True,csv_versions=csvs,original_source_ids=sorted(used),qualification='Full method/raw cell replay and all93county controls pass. Generic nulls remain null; partial sensitivity uses observed marks only for arithmetic and proves no eligible-universe robustness. No cross-publication or current-unit join.')
    writej(D/'historical-replay.json',out)
    (D/'extracts/original-replayed-native.json.gz').write_bytes(gzip.compress(json.dumps(units,separators=(',',':')).encode(),mtime=0))
    writej(D/'historical-original-receipts.json',list(used.values()));print(json.dumps({k:v for k,v in out.items()if k not in ['csv_versions','original_source_ids']}))
if __name__=='__main__':main()
