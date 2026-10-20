"""Independent original-first extraction. No coordinator/peer parser or counts."""
import collections,gzip,io,json,re,subprocess,zipfile,xml.etree.ElementTree as ET
from common import *

FIELDS=[('contest_code',0,4),('candidate_code',4,7),('source_code',7,11),
        ('party',101,104),('district_type_id',104,107),('district_code',107,111),
        ('contest_title',111,167),('candidate_name',167,205),('source_name',205,235),
        ('district_name',235,260),('votes_allowed',260,262),('referendum_flag',262,263)]
def decode(line):
    assert len(line)==263,len(line)
    r={k:line[a:b].decode('latin1') for k,a,b in FIELDS}
    r.update(votes=int(line[11:17]),methods=[int(line[17+i*6:23+i*6]) for i in range(14)])
    assert sum(r['methods'])==r['votes']
    return r

def xml_rows(ident):
    z=zipfile.ZipFile(io.BytesIO(body(ident)))
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        strings=[''.join(t.text or '' for t in s.iter('{'+ns['m']+'}t')) for s in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    out=[]
    for member in z.namelist():
        if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',member):
            for row in ET.fromstring(z.read(member)).findall('.//m:row',ns):
                cells=[]
                for c in row:
                    v=c.find('m:v',ns);value=v.text if v is not None else None
                    if c.get('t')=='s' and value is not None:value=strings[int(value)]
                    if c.get('t')=='inlineStr':value=''.join(t.text or '' for t in c.findall('.//m:t',ns))
                    cells.append({'cell':c.get('r'),'type':c.get('t'),'value':value})
                out.append({'input':ident,'member':member,'row':int(row.get('r')),'cells':cells})
    return out

def main():
    all_members=[]; selected=[]; roots={}; comparisons=[]; view_controls=[]
    for year,lo,sh in [(2024,'ri-2024-layout-zip','ri-2024-original-data-zip'),
                        (2020,'ri-2020-observed-long-zip','ri-2020-observed-short-zip'),
                        (2022,'ri-2022-observed-long-zip','ri-2022-observed-short-zip')]:
        archives={};root_records=None
        for ident in [lo,sh]:
            b=body(ident);z=zipfile.ZipFile(io.BytesIO(b));views={}
            for i,m in enumerate(z.infolist()):
                raw=z.read(m);all_members.append({'input':ident,'zip_sha256':sha(b),'member_index':i,'member':m.filename,
                    'bytes':len(raw),'sha256':sha(raw),'crc32':f'{m.CRC:08x}','header_offset':m.header_offset,
                    'zip_datetime':list(m.date_time),'compress_size':m.compress_size})
                if not raw or m.filename.startswith('__MACOSX/'):continue
                if not m.filename.lower().endswith(('.txt','.asc')):continue
                rows=[];offset=0
                for line_no,rawline in enumerate(raw.splitlines(keepends=True),1):
                    line=rawline.rstrip(b'\r\n');assert len(line) in [101,263]
                    if ident==lo:
                        r=decode(line);r.update(year=year,input=ident,zip_sha256=sha(b),member=m.filename,
                            line=line_no,byte_start=offset,byte_end=offset+len(rawline),raw_record=line.decode('latin1'),
                            raw_line_sha256=sha(rawline))
                        rows.append(r)
                    else:rows.append(line.decode('latin1'))
                    offset+=len(rawline)
                views[m.filename]=rows
                if ident==lo:
                    controls=collections.defaultdict(lambda:collections.Counter())
                    for r in rows:controls[r['contest_title'].strip()][r['candidate_name'].strip()]+=r['votes']
                    view_controls.append({'input':ident,'member':m.filename,'records':len(rows),'all_candidate_controls':dict(controls)})
                    picked=[r for r in rows if r['contest_title'].strip() in ['Presidential Electors For:','Senator in Congress','Governor'] and
                        (year!=2022 or r['contest_title'].strip()=='Governor') and (year!=2024 or r['contest_title'].strip()!='Governor')]
                    selected+=picked
            archives[ident]=views
        root_long=next(k for k in archives[lo] if '/' not in k)
        root_short=next(k for k in archives[sh] if '/' not in k)
        lr=archives[lo][root_long];sr=archives[sh][root_short]
        assert len(lr)==len(sr)
        disagreements=[i+1 for i,(l,s) in enumerate(zip(lr,sr)) if l['raw_record'][:101]!=s]
        comparisons.append({'year':year,'long_root':root_long,'short_root':root_short,'records':len(lr),'numeric_prefix_disagreements':disagreements})
        root_selected=[r for r in selected if r['input']==lo and r['member']==root_long]
        roots[year]=root_selected
        selected_titles={v['contest_title'].strip() for v in root_selected}
        for member,rs in archives[lo].items():
            if member==root_long:continue
            diffs=[]
            for r,root in zip(rs,lr):
                if r['contest_title'].strip() in selected_titles and r['raw_record']!=root['raw_record']:
                    diffs.append({'line':r['line'],'source_code':r['source_code'],'candidate_code':r['candidate_code'],
                        'root_votes':root['votes'],'view_votes':r['votes'],'root_methods':root['methods'],'view_methods':r['methods']})
            comparisons.append({'year':year,'root':root_long,'member':member,'selected_differences':diffs})
    write_json('source/field-layout.json',{'indexing':'zero-based half-open byte positions; source PDF uses 1-based inclusive',
        'fields':[{'name':k,'start':a,'end':b} for k,a,b in FIELDS],
        'total_votes':[11,17],'method_slots':[[17+6*i,23+6*i] for i in range(14)],
        'method_labels':{'2020_format':['Election Day','Mail Ballots',None]+[None]*11,
                         '2020_html':['Polling place','Mail ballots','Emergency ballots'],
                         '2022_2024_format':['Election Day','Mail Ballots','Early Voting']+[None]*11},
        'missing':'Absent record is null; literal space-only text remains spaces in raw record and fields.'})
    write_json('source/zip-members.json',all_members)
    write_gz('witness/selected-all-views.jsonl.gz',selected)
    write_gz('witness/root-selected.jsonl.gz',[r for rows in roots.values() for r in rows])
    write_json('witness/zip-view-controls.json',view_controls)
    write_json('witness/view-comparison.json',comparisons)
    # Preserve raw selected workbook rows with cell identities; complete unrelated content stays in original XLSX.
    workbook_rows=[]
    for ident in ['board2024-xlsx','board2020-xlsx','board2022-xlsx','board2024-writeins-xlsx']:
        rs=xml_rows(ident)
        if ident=='board2024-writeins-xlsx':
            rs=[dict(r,cells=[c for c in r['cells'] if re.sub(r'\d','',c['cell']) in ['A','B','D','E']]) for r in rs]
        else:
            rs=[r for r in rs if r['row']==1 or any(c['cell'].startswith('H') and
                (c['value'] in ['Presidential Electors For:','Senator in Congress','Governor'] or
                 str(c['value']).startswith(('REGISTERED VOTERS','BALLOTS CAST','VOTER TURNOUT'))) for c in r['cells'])]
        write_gz('witness/'+ident+'-selected-cells.jsonl.gz',rs)
        print(ident,'selected rows',len(rs))
    for ident in ['boe-2024-summary','board2020-pdf','board2022-pdf','ri-2020-observed-format-description','ri-2022-description','board2020-writeins-pdf','board2022-writeins-pdf']:
        r=subprocess.run(['pdftotext','-layout','-','-'],input=body(ident),capture_output=True,check=True)
        (BASE/'witness'/f'{ident}.layout.txt.gz').write_bytes(gzip.compress(r.stdout,mtime=0))
    summary=[]
    for year,rows in roots.items():
        for title in dict.fromkeys(r['contest_title'].strip() for r in rows):
            rs=[r for r in rows if r['contest_title'].strip()==title];cand=collections.defaultdict(lambda:{'votes':0,'methods':[0]*14,'party':set(),'candidate_code':set()})
            for r in rs:
                c=cand[r['candidate_name'].strip()];c['votes']+=r['votes'];c['methods']=[x+y for x,y in zip(c['methods'],r['methods'])];c['party'].add(r['party']);c['candidate_code'].add(r['candidate_code'])
            for c in cand.values():c['party']=sorted(c['party']);c['candidate_code']=sorted(c['candidate_code'])
            summary.append({'year':year,'contest':title,'units':len(set(r['source_code'] for r in rs)),'records':len(rs),'candidates':dict(cand)})
    write_json('witness/independent-controls.json',summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
