#!/usr/bin/env python3
"""Independent originals-first SD extraction. No shared or peer writes."""
import csv, gzip, hashlib, io, json, posixpath, re, subprocess, tempfile, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
DATA = BASE.parent
NEWS = DATA / 'news'
PEER = DATA / 'turnout/source'
SRC = BASE / 'source'
NS = {'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(b): return hashlib.sha256(b).hexdigest()
def js(path, obj): path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
def gz(path, obj): path.write_bytes(gzip.compress(json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
def csvout(path, rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def original(a, root):
    if 'asset_parts' in a:
        parts=[]
        for p in a['asset_parts']:
            b=(root/p['asset']).read_bytes();assert len(b)==p['bytes']<40000000 and sha(b)==p['sha256'];parts.append(b)
        z=b''.join(parts);assert len(z)==a['stored_bytes']
    else:
        z=(root/a['asset']).read_bytes();assert len(z)<40000000
    assert sha(z)==a['stored_sha256']
    b=gzip.decompress(z);assert sha(b)==a['raw_sha256'] and len(b)==a.get('raw_bytes',a.get('bytes'))
    return b
def text_pdf(b):
    with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
        f.write(b);f.flush()
        return subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True).stdout.decode()
def table(t, start, end, n):
    begin=t.index(start);finish=t.index(end,begin+len(start));rows=[];footer=None
    for page,x in enumerate(t.split('\f'),1):
        pos=sum(len(z)+1 for z in t.split('\f')[:page-1])
        for ln,line in enumerate(x.splitlines(),1):
            at=pos+x.index(line) if line else pos
            if not begin<=at<finish: continue
            m=re.fullmatch(r"\s*([A-Za-z][A-Za-z .'-]*?)\s+("+r'\s+'.join([r'[\d,]+']*n)+r')\s*',line)
            if not m:continue
            name=m[1].strip();v=[int(z.replace(',',''))for z in m[2].split()]
            if name=='General Election - November':continue # dated page heading, not a county row
            if name=='Total':footer=v
            else:rows.append(dict(county=name,counts=v,pdf_page=page,pdf_line=ln,raw_line=line))
    assert len(rows)==66 and len({r['county']for r in rows})==66
    assert footer==[sum(r['counts'][j]for r in rows)for j in range(n)]
    return rows,footer
def workbook(raw):
    z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
    strings=[''.join(s.itertext())for s in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
    rel={x.get('Id'):x.get('Target')for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheets=[]
    for i,s in enumerate(ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS),1):
        target=rel[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        member=target.lstrip('/')if target.startswith('/')else posixpath.normpath('xl/'+target)
        rows=[]
        for row in ET.fromstring(z.read(member)).findall('m:sheetData/m:row',NS):
            cells=[]
            for c in row.findall('m:c',NS):
                v=c.find('m:v',NS);rv=v.text if v is not None else None;value=rv
                if c.get('t')=='s':value=strings[int(rv)]
                if c.get('t')=='inlineStr':value=''.join(c.find('m:is',NS).itertext())
                cells.append(dict(address=c.get('r'),type=c.get('t'),raw_v=rv,value=value,attributes=c.attrib,cell_xml=ET.tostring(c,encoding='unicode')))
            rows.append(dict(row=int(row.get('r')),attributes=row.attrib,cells=cells))
        sheets.append(dict(ordinal=i,name=s.get('name'),attributes=s.attrib,member=member,rows=rows))
    return dict(shared_strings=strings,sheets=sheets,members=[dict(name=i.filename,bytes=i.file_size,crc=i.CRC,sha256=sha(z.read(i.filename)))for i in z.infolist()])
def values(row):return {re.sub(r'\d+$','',c['address']):c['value']for c in row['cells']}

def main():
    SRC.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((NEWS/'manifest.json').read_text());mf={a['id']:a for a in manifest}
    js(SRC/'shared-news-receipts.json',manifest)
    receipts=[];texts={}
    # Original documents retained once in read-only shared evidence.
    ids=['sos-2024-general-canvass','sos-2022-general-canvass','sos-2020-general-canvass',
         'sos-2024-general-county-aurora-clark','sos-2024-county-clay-faulk','sos-2024-county-grant-lyman','sos-2024-county-marshall-ziebach',
         'sos-2022-precinct-canvass','sos-2022-general-recount','sos-2020-general-county-canvass']
    for k in ids:
        a=mf[k];b=original(a,NEWS);t=text_pdf(b);texts[k]=t
        (SRC/(k+'.txt.gz')).write_bytes(gzip.compress(t.encode(),mtime=0))
        receipts.append(dict(source_id=k,receipt=a,root_relative_to_baselines='../news',text_pages=t.count('\f')))
    books={};peer_receipts=[]
    for y in [2024,2022,2020]:
        k=f'returns-{y}-archive';a=json.loads((PEER/(k+'.receipt.json')).read_text());t=text_pdf(original(a,PEER));books[y]=t
        (SRC/(k+'.txt.gz')).write_bytes(gzip.compress(t.encode(),mtime=0));peer_receipts.append(a)
    a=json.loads((PEER/'census-counties2020.receipt.json').read_text());b=original(a,PEER);peer_receipts.append(a)
    fips={r['COUNTYNAME'].removesuffix(' County'):r['STATEFP']+r['COUNTYFP']for r in csv.DictReader(io.StringIO(b.decode()),delimiter='|')if r['STATE']=='SD'}
    assert len(fips)==66 and all(v.startswith('46')for v in fips.values());js(SRC/'county-identities.json',fips)
    js(SRC/'peer-original-receipts.json',peer_receipts)
    specs={2024:('sos-2024-general-canvass','Presidential Electors',4,[('Kamala D. Harris and Tim Walz','DEM'),('Chase Oliver and Mike ter Maat','LIB'),('Donald J. Trump and JD Vance','REP'),('Robert F. Kennedy, Jr. and Nicole Shanahan','IND')],0,2,'President','not_Senate'),
           2022:('sos-2022-general-canvass','United States Senator',3,[('Brian L. Bengs','DEM'),('Tamara J Lesnar','LIB'),('John R. Thune','REP')],0,2,'Senate','other_ClassIII_midterm'),
           2020:('sos-2020-general-canvass','United States Senator',2,[('Mike Rounds','REP'),('Dan Ahlers','DEM')],1,0,'Senate','same_ClassII')}
    county=[];candidates=[];controls={}
    for y,(sid,start,n,names,ai,bi,contest,seat) in specs.items():
        rows,footer=table(texts[sid],start,'United States Representative',n)
        controls[str(y)]=dict(source_id=sid,columns=names,candidate_totals=footer,named_total=sum(footer))
        for r in rows:
            a,b=r['counts'][ai],r['counts'][bi];total=sum(r['counts']);pair=a+b
            row=dict(year=y,election_date={2024:'2024-11-05',2022:'2022-11-08',2020:'2020-11-03'}[y],contest=contest,seat_context=seat,county=r['county'],county_fips=fips[r['county']],source_id=sid,source_status='signed_state_canvass',pdf_page=r['pdf_page'],pdf_line=r['pdf_line'],a_name=names[ai][0],a_ballot_party=names[ai][1],b_name=names[bi][0],b_ballot_party=names[bi][1],a_votes=a,b_votes=b,other_named_votes=total-pair,all_named_votes=total,pair_votes=pair,pair_participation=pair/total,a_pair_share=a/pair,a_all_named_share=a/total,a_minus_b_net=a-b,a_minus_b_pair_margin_pp=100*(a-b)/pair,a_minus_b_all_named_margin_pp=100*(a-b)/total,blank_votes='',undervotes='',overvotes='',generic_writeins='',named_valid_writeins='',method='not_separately_reported')
            county.append(row)
            for j,(name,party) in enumerate(names):candidates.append(dict(year=y,contest=contest,seat_context=seat,county=r['county'],county_fips=fips[r['county']],candidate=name,ballot_party=party,votes=r['counts'][j],printed_candidate_column=j+1,source_id=sid,pdf_page=r['pdf_page'],pdf_line=r['pdf_line'],raw_line=r['raw_line']))
    csvout(DATA/'county-baselines.csv',county);csvout(BASE/'county-candidates.csv',candidates);js(SRC/'state-controls.json',controls)
    # Separate published native source with literal candidate headers; no certified residual allocation.
    native=[];differences=[];footerrows=[]
    keys=['sos-2024-public-presidential-precinct-export-684','sos-2024-public-statewide-export-postback-684','sos-2024-public-aurora-export-postback-684']
    evidence={k:workbook(original(mf[k],NEWS))for k in keys};gz(SRC/'workbooks-complete-cells.json.gz',evidence)
    book=evidence[keys[0]];assert len(book['sheets'])==66
    for s in book['sheets']:
        rr={r['row']:r for r in s['rows']};h=values(rr[7]);tot=next(r for r in s['rows']if values(r).get('B')=='TOTALS');name=s['name']
        expected=next(r for r in county if r['year']==2024 and r['county']==name)
        assert ['Harris' in h['C'],'Oliver' in h['D'],'Trump' in h['E'],'Kennedy' in h['F']]==[True]*4
        local=[]
        for r in s['rows']:
            if not 7<r['row']<tot['row']:continue
            v=values(r);c=[int(v[x])for x in 'CDEF'];total=sum(c);pair=c[0]+c[2]
            row=dict(native_key=f"sd:2024:pres:{fips[name]}:sheet{s['ordinal']}:row{r['row']}",year=2024,contest='President',county=name,county_fips=fips[name],sheet=s['ordinal'],sheet_member=s['member'],source_row=r['row'],native_label=v['B'],official_native_id='',method_label='literal_absentee_unit'if 'absentee' in v['B'].lower()else'not_separately_identified',harris_dem=c[0],oliver_lib=c[1],trump_rep=c[2],kennedy_ind=c[3],all_named_votes=total,a_votes=c[0],b_votes=c[2],pair_votes=pair,other_named_votes=c[1]+c[3],pair_participation=pair/total if total else '',a_pair_share=c[0]/pair if pair else '',source_id=keys[0],raw_source_sha256=mf[keys[0]]['raw_sha256'],source_status='published_unofficial_691_reporting',blank_votes='',undervotes='',overvotes='',ballots_cast='',registered_voters='')
            native.append(row);local.append(row)
        footer=[int(values(tot)[x])for x in 'CDEF'];assert footer==[sum(r[k]for r in local)for k in ['harris_dem','oliver_lib','trump_rep','kennedy_ind']]
        cert=[expected['a_votes'],next(r['votes']for r in candidates if r['year']==2024 and r['county']==name and r['ballot_party']=='LIB'),expected['b_votes'],next(r['votes']for r in candidates if r['year']==2024 and r['county']==name and r['ballot_party']=='IND')]
        for j,(key,party) in enumerate(specs[2024][3]):differences.append(dict(county=name,county_fips=fips[name],candidate=key,ballot_party=party,public_native_sum=footer[j],signed_state_control=cert[j],public_minus_signed=footer[j]-cert[j],allocated_residual=False))
        footerrows.append(dict(county=name,sheet_ordinal=s['ordinal'],footer_row=tot['row'],footer=footer,native_rows=len(local),header_literals=h,source_headings=[values(rr[i])for i in range(1,8)if i in rr]))
    assert len(native)==691 and len({r['native_key']for r in native})==691
    csvout(BASE/'native-2024.csv',native);csvout(BASE/'native-signed-differences.csv',differences);js(SRC/'native-2024-footers.json',footerrows)
    # Full native 2022 Senate original PDF rows, including wrapped labels, continuations and totals.
    rows22=[];pages22=[]
    for page,t in enumerate(texts['sos-2022-precinct-canvass'].split('\f'),1):
        if 'United States Senator' not in t:continue
        name=re.search(r'^\s*([A-Za-z ]+) County\s*$',t,re.M)[1].strip();lines=t.splitlines();start=next(i for i,l in enumerate(lines)if 'Precinct Name' in l)
        # Numeric rows are exact. Raw complete page/line positions preserve wrapped label ambiguities.
        pending=[];out=[]
        for ln,line in enumerate(lines[start+1:],start+2):
            m=re.fullmatch(r'\s*(.*?)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*',line)
            if m:
                label=m[1].strip();v=[int(m[i].replace(',',''))for i in [2,3,4]]
                if label=='Total':
                    pages22.append(dict(county=name,pdf_page=page,footer=v,raw_line=line));break
                if pending:label=' '.join(pending+[label]);pending=[]
                out.append(dict(native_key=f'sd:2022:senate:{fips[name]}:page{page}:line{ln}',year=2022,contest='Senate',county=name,county_fips=fips[name],pdf_page=page,pdf_line=ln,native_label=label,raw_line=line,a_votes=v[0],lesnar_lib=v[1],b_votes=v[2],pair_votes=v[0]+v[2],other_named_votes=v[1],all_named_votes=sum(v),official_native_id='',method_label='literal_absentee_unit'if 'absentee' in label.lower()else'not_separately_identified',source_id='sos-2022-precinct-canvass',source_status='published_precinct_canvass'))
            elif line.strip() and not re.fullmatch(r'\s*\d+ of \d+\s*',line):
                # Wrapped source labels before/after centered number rows remain explicit fragments.
                pending.append(line.strip())
        rows22.extend(out)
    assert len(pages22)==65 # 66 Senate pages: Minnehaha continues on a second page.
    balances22=[]
    for name in fips:
        rs=[r for r in rows22 if r['county']==name];expected=next(r for r in county if r['year']==2022 and r['county']==name)
        actual=[sum(r[k]for r in rs)for k in ['a_votes','lesnar_lib','b_votes']];want=[expected['a_votes'],expected['other_named_votes'],expected['b_votes']]
        balances22.append(dict(county=name,native_rows=len(rs),actual=actual,signed=want,difference=[x-y for x,y in zip(actual,want)]))
        if name!='Yankton':assert actual==want,(name,actual,want)
        else:assert not rs # Original 1,420-page PDF contains no Yankton County pages.
    csvout(BASE/'native-2022.csv',rows22);js(SRC/'native-2022-balances.json',balances22);js(SRC/'native-2022-footers.json',pages22)
    js(SRC/'original-reference-index.json',receipts)
    print(json.dumps(dict(county_rows=len(county),native2024=len(native),native2022=len(rows22),controls=controls)))
if __name__=='__main__':main()
