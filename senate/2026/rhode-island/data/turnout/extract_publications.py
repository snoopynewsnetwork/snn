"""Extract publication-scoped HTML hierarchy, candidate/method controls and XLSX cells."""
import re,io,zipfile,xml.etree.ElementTree as ET,collections,subprocess,urllib.parse
from acquire import allreceipts
from common import *
SELECTED={'Presidential Electors For:','Senator in Congress','Governor'}
def html_extract(r):
    b=original(r);tree=Tree(b).root;out=[]
    for ti,table in enumerate(tree.all('table'),1):
        title=table.attrs.get('summary','')
        if title not in SELECTED:continue
        for ri,tr in enumerate(table.all('tr'),1):
            cells=list(tr.all('td')); cand=next((x for x in cells if x.has('candidate')),None)
            total=next((x for x in cells if x.has('total') and x.has('votes')),None)
            if cand is None or total is None:continue
            out.append(dict(source_id=r['id'],source_raw_sha256=r['raw_sha256'],position=dict(table_ordinal=ti,row_ordinal=ri),contest=title,candidate=clean(cand.text()),party_text=[clean(x.text()) for x in cand.all('span')],total=int(clean(total.text()).replace(',','')),methods=[dict(label=clean(x.text()).rsplit(':',1)[0],votes=int(clean(x.text()).rsplit(':',1)[1])) for x in tr.all('li')]))
    return out,tree
def run():
    rs=allreceipts();html=[];parents=[];members=[];workrows=[]
    for r in rs:
        if r.get('status')!=200 or 'stored_path'not in r:continue
        b=original(r)
        if b.startswith(b'<!DOCTYPE') or b.startswith(b'<html'):
            if '-town-'in r['id'] or r['id']in ['ri-2024-general-old-authority','ri-2020-observed-state-summary','ri-2022-observed-historical-seed','ri-2024-senate']:
                hs,t=html_extract(r);html+=hs
                if '-town-'in r['id']:
                    heading=next(clean(n.text()) for n in t.all('h2') if n.attrs.get('id')=='contest-title');assert heading.startswith('Votes by municipality: ')
                    parent_name=heading.split(': ',1)[1];yr=r['id'][:4];children=[]
                    for label,u in links(b):
                        final=urllib.parse.urljoin(r['url'],u)
                        if final.startswith(r['url']) and re.fullmatch(r'\d{4}/',final[len(r['url']):]):
                            code=final[len(r['url']):].strip('/');children.append(dict(code=code,label=label,url=final))
                    assert children
                    parents.append(dict(year=yr,key='RI:municipality:'+r['url'].strip('/').split('/')[-1],name=parent_name,url=r['url'],source_id=r['id'],raw_sha256=r['raw_sha256'],status_text=next(clean(x.text()) for x in t.all('span') if x.has('updated_at')),children=children))
        if not r['id'].endswith('-xlsx') or 'writeins' in r['id']:continue
        z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip()is None;ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for i in z.infolist():
            by=z.read(i);members.append(dict(source_id=r['id'],member=i.filename,bytes=len(by),sha256=sha(by),crc=i.CRC))
        strings=[]
        if 'xl/sharedStrings.xml'in z.namelist():strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
        sheetnames=[x.attrib for x in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',ns)]
        for member in z.namelist():
            if not re.fullmatch(r'xl/worksheets/sheet\d+\.xml',member):continue
            root=ET.fromstring(z.read(member));header=None
            for row in root.findall('.//m:row',ns):
                cells={}
                for c in row:
                    v=c.find('m:v',ns);val=v.text if v is not None else ''.join(c.itertext());value=strings[int(val)] if c.attrib.get('t')=='s' else val
                    cells[c.attrib['r']]=dict(value=value,xml_type=c.attrib.get('t'),raw_v=None if v is None else v.text)
                vals={re.sub(r'\d+$','',k):v['value'] for k,v in cells.items()}
                if row.attrib['r']=='1':header=dict(cells=cells,sheetnames=sheetnames)
                title=vals.get('H','')
                if title in SELECTED or title.startswith(('REGISTERED VOTERS','BALLOTS CAST')):
                    workrows.append(dict(key=f"{r['raw_sha256']}:{member}:row{row.attrib['r']}",source_id=r['id'],source_raw_sha256=r['raw_sha256'],member=member,row=int(row.attrib['r']),header=header,cells=cells,columns=vals))
    dump(ROOT/'extracts/municipal-hierarchy.json',parents)
    dump(ROOT/'extracts/html-controls.json',html)
    dump(ROOT/'source/workbook-members.json',members)
    gzwrite(ROOT/'extracts/workbook-selected-rows.jsonl.gz',b''.join((json.dumps(x,separators=(',',':'))+'\n').encode() for x in workrows))
    for year in ['2020','2022','2024']:
        rows=[r for r in workrows if year in r['source_id']];cs=collections.defaultdict(lambda:[0]*4);scope=collections.defaultdict(set)
        for r in rows:
            d=r['columns'];k=(d['H'],d.get('I',''));cs[k]=[a+int(d.get(c,'0') or 0) for a,c in zip(cs[k],'CDEF')];scope[k].add(d['B'])
        print(year,[(k,v,len(scope[k])) for k,v in cs.items()])
    for year in ['2020','2022','2024']:
        print(year,'parents',sum(p['year']==year for p in parents),'children',sum(len(p['children']) for p in parents if p['year']==year))
if __name__=='__main__':run()
