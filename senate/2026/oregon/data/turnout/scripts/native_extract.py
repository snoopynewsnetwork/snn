#!/usr/bin/env python3
"""Source-scoped native observations. No allocation from county residuals.

Native labels are versioned within county/source, not cross-year geometry IDs.
Repeated totals and method presentations are retained and marked nonadditive.
"""
from pathlib import Path
import csv, gzip, io, json, re
from collections import defaultdict
OUT=Path(__file__).resolve().parents[1]
SRC=OUT/'source'
INV=json.loads((SRC/'original-inventory.json').read_bytes())
COUNTIES={r['county']:r['county_fips']for r in json.loads((SRC/'county-wide.json').read_bytes())}
SPECS=json.loads((OUT/'candidate-universe.json').read_bytes())
VISUAL=json.loads((SRC/'visual-row-transcriptions.json').read_bytes()) if (SRC/'visual-row-transcriptions.json').exists()else []
NUM=r'[\d,]+'
units={};observations=[];issues=[]

def val(s):return int(s.replace(',',''))
def read(key,acquired=False):
    p=SRC/('acquired'if acquired else '')/(key+'.layout.txt.gz')
    return gzip.decompress(p.read_bytes()).decode(errors='replace')

def pages(key,acquired=False):
    text=read(key,acquired).split('\f')
    for i,t in enumerate(text,1):
        refined=SRC/'refined-ocr'/f'{key}-p{i:03d}.txt.gz'
        if refined.exists() and len(t.strip())<100:
            yield i,gzip.decompress(refined.read_bytes()).decode(),'refined_OCR'
            continue
        o=SRC/'ocr'/f'{key}-p{i:03d}.txt.gz'
        if o.exists() and len(t.strip())<100:
            yield i,gzip.decompress(o.read_bytes()).decode(),'OCR'
        else:yield i,t,'PDF_text'

def canonical(label,contest):
    s=label.lower().replace('1','i')
    names=[x for x in SPECS if x['contest']==contest]
    for r in names:
        name=r['candidate'].lower()
        if name=='misc.':
            if re.search(r'write.?in|misc',s):return r['column_index']
        elif name.split()[-1].lower()in s:return r['column_index']
    return None

def get(key,county,contest,label,presentation='native',native_id=None):
    k=(key,contest,label,presentation)
    if k not in units:
        summary=bool(re.search(r'^(?:totals?|grand totals?|precinct totals|county total|all precincts)$',label,re.I))
        if native_id is None:
            m=re.fullmatch(r'Precinct\s+(\d[\w/-]*)',label)
            if m:native_id=m[1]
            elif re.fullmatch(r'\d+(?:/\d+)?',label):native_id=label
        units[k]=dict(source_key=key,county=county,county_fips=COUNTIES[county],contest=contest,
            unit_literal=label,source_native_id=native_id,presentation=presentation,
            unit_key=f'OR:{contest[:4]}:{COUNTIES[county]}:{key}:{label}',
            geographic_class='nonadditive_summary'if summary else 'native_reporting_unit_unreviewed_geometry',
            additive=not summary,acceptance_status='unaccepted_source_scoped_normalization_consult_county_reconciliation',choices={},fields={},locators=[])
    return units[k]

def add(u,label,count,locator,kind='candidate',method='reported_total',native_choice_id=None):
    ci=canonical(label,u['contest'])if kind=='candidate'else None
    o=dict(source_key=u['source_key'],county=u['county'],county_fips=u['county_fips'],contest=u['contest'],
        unit_literal=u['unit_literal'],unit_key=u['unit_key'],label_literal=label,value=count,
        kind=kind,method_literal=method,canonical_column=ci,native_choice_id=native_choice_id,**locator)
    observations.append(o)
    if kind=='candidate'and ci is not None and method=='reported_total':
        # Conflicts are explicit; never overwrite an earlier differing value.
        if str(ci) in u['choices']and u['choices'][str(ci)]!=count:
            issues.append(dict(issue='conflicting_candidate_observations',unit=u['unit_key'],column=ci,old=u['choices'][str(ci)],new=count,locator=locator))
        else:u['choices'][str(ci)]=count
    if kind=='control'and method=='reported_total':
        if label in u['fields']and u['fields'][label]!=count:
            issues.append(dict(issue='conflicting_source_control',unit=u['unit_key'],field=label,old=u['fields'][label],new=count,locator=locator))
        else:u['fields'][label]=count
    if locator not in u['locators']:u['locators'].append(locator)

def vertical(key,county,year):
    current=None;active=None;u=None
    for pg,text,layer in pages(key):
        lines=text.splitlines()
        for line_no,line in enumerate(lines,1):
            s=re.sub(r'\s+',' ',line.strip());loc=dict(page=pg,line=line_no,text_layer=layer,raw_line=line)
            m=re.fullmatch(r'Precinct\s*(\d[\w/-]*)',s)
            if m:
                current=s;active=None
            elif s.lower()=='all precincts':
                current='All Precincts';active=None
            # The first named candidate can recover a heading whose scan/OCR
            # glyphs are unreadable. This never supplies an absent count.
            if re.match(r'^(?:(?:REP|DEM|PGP|LBT|PRO) )?Jo Rae Perkins\s+\d',s):
                active=f'{year}-senate';u=get(key,county,active,current or 'UNRESOLVED_SOURCE_UNIT')
            elif year==2022 and re.match(r'^Tina Kotek\s+\d',s):
                active='2022-governor';u=get(key,county,active,current or 'UNRESOLVED_SOURCE_UNIT')
            if re.fullmatch(r'US Senator(?: Federal)?(?: \(VGNone\))?(?: \(Vote for 1\))?',s,re.I):
                active=f'{year}-senate';u=get(key,county,active,current or 'UNRESOLVED_SOURCE_UNIT')
            elif year==2022 and re.fullmatch(r'Governor(?: Statewide Partisan)?(?: \(VGNone\))?(?: \(Vote for 1\))?',s,re.I):
                active='2022-governor';u=get(key,county,active,current or 'UNRESOLVED_SOURCE_UNIT')
            elif year==2024 and re.fullmatch(r'(?:United States |US )?President and Vice President \(Vote for 1\)',s,re.I):
                active='2024-president';u=get(key,county,active,current or 'UNRESOLVED_SOURCE_UNIT')
            elif re.search(r'\(Vote for \d\)|^Vote For \d|^VOTE FOR \d',s,re.I)and not re.fullmatch(r'(?:\(Vote for 1\)|Vote For 1|VOTE FOR 1)',s,re.I):
                active=None
            if not active or not u:continue
            bm=re.match(r'('+NUM+r') ballots \(('+NUM+r') over voted ballots, ('+NUM+r') overvotes, ('+NUM+r') undervotes\)(?:, ('+NUM+r') registered voters)?',s)
            if bm:
                for label,v in zip(['ballots','over_voted_ballots','overvotes_in_ballot_heading','undervotes_in_ballot_heading','registered_voters'],bm.groups()):
                    if v is not None:add(u,label,val(v),loc,'control')
                continue
            m=re.fullmatch(r'(.+?)\s+('+NUM+r')\s+([\d.,]+)%\s*(.*?)',s)
            if m:
                label=m[1].strip();v=val(m[2]);ci=canonical(label,active)
                if ci is not None:
                    add(u,label,v,loc)
                    extras=m[4].split()
                    if extras and all(re.fullmatch(NUM,x)for x in extras):
                        for method,n in zip(['AB','ED','EV'],extras):add(u,label,val(n),loc,'candidate',method)
                elif label.lower()=='total':add(u,'Total',v,loc,'control')
            else:
                cm=re.fullmatch(r'(Overvotes|Undervotes)\s+('+NUM+r')',s,re.I)
                if cm:add(u,cm[1].lower(),val(cm[2]),loc,'control')

def scytl_table(key,county,year,acquired=False,only=None):
    # Header-based column decoding preserves partial column presentations.
    for pg,text,layer in pages(key,acquired):
        ls=text.splitlines();start=next((i for i,l in enumerate(ls)if re.match(r'^\s*Precinct\s+(?:Ballots|Total)\b',l)),None)
        if start is None:continue
        pre='\n'.join(ls[:start]);heading=next((re.sub(r'\s+',' ',s.strip())for s in reversed(ls[:start])if re.search(r'\(Vote\s+for\s+1\)',s)),'')
        if 'US Senator'in heading:contest=f'{year}-senate'
        elif year==2022 and heading.startswith('Governor'):contest='2022-governor'
        elif year==2024 and ('President' in heading):contest='2024-president'
        else:continue
        if only and contest!=only:continue
        header_lines=ls[start:start+4];header=' '.join(header_lines);hasbr='Ballots' in ls[start]
        columns=[]
        for r in [x for x in SPECS if x['contest']==contest]:
            token={'Donice Noelle Smith':'Donice','R Leon Noble':'R Leon','Robert F Kennedy Jr':'Robert F'}.get(r['candidate'],r['candidate'].split()[0])
            if r['candidate']=='Misc.':token='Write-in'
            pattern=r'\b'+r'\s+'.join(map(re.escape,token.lower().split()))+r'\b'
            positions=[m.start()for line in header_lines if (m:=re.search(pattern,line.lower()))]
            if positions:columns.append((min(positions),r['candidate']))
        columns=[x[1]for x in sorted(columns)]
        hasunder='Under'in header;hasover='Over'in header
        for j,line in enumerate(ls[start+1:],start+2):
            m=re.match(r'^\s*(Precinct\s+[\w/-]+|Total)\s+(.+?)\s*$',line)
            if not m:continue
            reviewed=next((r for r in VISUAL if r['source_key']==key and r['PDF_page']==pg and r['refined_text_line_1based']==j),None)
            if reviewed:
                u=get(key,county,contest,reviewed['unit_literal']);loc=dict(page=pg,line=j,text_layer='direct_visual_transcription',raw_line=line,review_path='source/visual-row-transcriptions.json')
                for field,n in zip(reviewed['columns'],reviewed['integer_columns_in_printed_order']):
                    add(u,field,n,loc,'candidate'if field in [r['candidate']for r in SPECS if r['contest']==contest]else 'control')
                continue
            u=get(key,county,contest,re.sub(r'\s+',' ',m[1]));loc=dict(page=pg,line=j,text_layer=layer,raw_line=line)
            tail=re.sub(r'[\d.,]+\s*%','',m[2]);tokens=tail.split()
            if layer=='refined_OCR':
                tokens=[t.rstrip('.°').strip('_')for t in tokens if t not in ['=','|','—','_','«']]
            if not all(re.fullmatch(NUM,t)for t in tokens):
                issues.append(dict(issue='table_row_unparsed',source_key=key,page=pg,line=j,raw_line=line));continue
            nums=[val(t)for t in tokens]
            fields=(['ballots','registered_voters','Total']if hasbr else ['Total'])+columns+(['overvotes']if hasover else [])+(['undervotes']if hasunder else [])
            if len(fields)!=len(nums):
                issues.append(dict(issue='table_column_count',source_key=key,page=pg,line=j,fields=fields,values=nums,raw_line=line));continue
            for field,n in zip(fields,nums):add(u,field,n,loc,'candidate'if field in columns else 'control')

def sov_csv(key,county,year,acquired=False):
    if acquired:
        p=SRC/'acquired';r=json.loads((p/(key+'.receipt.json')).read_bytes());s=gzip.decompress((p/r['response_entities'][-1]['asset']).read_bytes()).decode()
    else:s=read(key)
    rows=csv.DictReader(io.StringIO(s))
    for i,r in enumerate(rows,2):
        if not re.match(r'^US Senator|^President and Vice President',r['Contest']):continue
        if year!=2024 and not r['Contest'].startswith('US Senator'):continue
        contest=f'{year}-'+('senate'if r['Contest'].startswith('US Senator')else 'president')
        label=r.get('Precinct','COUNTY_TOTAL');u=get(key,county,contest,label,presentation='native'if 'Precinct'in r else 'nonadditive_county_summary',native_id=label if 'Precinct'in r else None)
        if 'Precinct'not in r:u['additive']=False;u['geographic_class']='nonadditive_summary'
        loc=dict(CSV_record_1based=i,raw_source_row=r)
        add(u,r['Choice'],val(r['Votes']),loc,native_choice_id=r.get('Choice Order'))
        # Choice-specific overvotes are not contest overvote ballots.
        for k,v in r.items():
            if k in ['ContestOrder','Contest','Contest ID','Choice Order','Choice','Precinct','Votes']:continue
            add(u,k,val(v),loc,'source_choice_control',method='choice_scoped')
        u.setdefault('native_contest_id',r['Contest ID'])

def yamhill_csv():
    s=read('2020-35');lines=s.splitlines();rows=csv.DictReader(lines[1:])
    for i,r in enumerate(rows,3):
        if r['Contest Title']!='US Senator':continue
        u=get('2020-35','Yamhill','2020-senate',r['#Precinct'],native_id=r['Precinct ID'])
        loc=dict(CSV_record_1based=i,raw_source_row=r)
        lab=r['Choice Name'];kind='administrative_writein_scope'if lab in ['Rejected write-ins','Unassigned write-ins']else 'candidate'
        add(u,lab,val(r['Total Votes']),loc,kind,native_choice_id=r['Choice ID'])
        add(u,lab,val(r['Vote by Mail Votes']),loc,kind,'Vote by Mail',r['Choice ID'])
        for k in ['Registered Voters','Ballots Cast','Total Overvotes','Total Undervotes','Total Invalid Votes',
                  'Vote by Mail Overvotes','Vote by Mail Undervotes','Vote by Mail Invalid Votes']:
            add(u,k,val(r[k]),loc,'source_choice_control','choice_scoped')
        u['native_contest_id']=r['Contest ID']

def umatilla_csv():
    rs=list(csv.reader(io.StringIO(read('2020-29'))))
    begin=next(i for i,r in enumerate(rs)if 'US Senator Federal'in r)
    header=rs[begin+3];fields=header[1:10]
    for i,r in enumerate(rs[begin+4:],begin+5):
        if not r or not r[0]:break
        if not(re.match(r'\d',r[0])or r[0].lower()in ['totals','total']):break
        u=get('2020-29','Umatilla','2020-senate',r[0]);loc=dict(CSV_record_1based=i,raw_source_row=r)
        assert len(r[1:10])==len(fields)
        for f,v in zip(fields,r[1:10]):add(u,f,val(v),loc,'candidate'if canonical(f,'2020-senate')is not None else 'control')

def clearballot_table_2024(key,county):
    for pg,text,layer in pages(key,True):
        if not re.search(r'(?:United States President and Vice President - Vote for one|President, 4-Year Term)',text):continue
        for j,line in enumerate(text.splitlines(),1):
            m=re.match(r'^\s*([\d/]+|Precinct Totals|Totals|Grand Totals|Total)\s+(.+?)\s*$',line)
            if not m:continue
            t=re.sub(r'[\d.]+%','',m[2]).split()
            if not all(re.fullmatch(NUM,x)for x in t):continue
            ns=list(map(val,t))
            if len(ns)!=14:
                issues.append(dict(issue='clearballot_column_count',source_key=key,page=pg,line=j,values=ns,raw_line=line));continue
            fields=[x['candidate']for x in SPECS if x['contest']=='2024-president']
            if county=='Clackamas':fields=fields[:7]+['Cast Votes','undervotes','overvotes','Misc.','Vote by Mail Ballots Cast','Total Ballots Cast','Registered Voters']
            else:fields+=['Cast Votes','undervotes','overvotes','Vote by Mail Ballots Cast','Total Ballots Cast','Registered Voters']
            u=get(key,county,'2024-president',m[1]);loc=dict(page=pg,line=j,text_layer=layer,raw_line=line)
            # Clear Ballot repeats the full county as a bare numeric 0 row.
            # These are explicitly retained as a nonadditive presentation.
            if m[1] in ['0','000']:
                u['additive']=False;u['geographic_class']='nonadditive_county_summary_numeric_0'
            for field,n in zip(fields,ns):add(u,field,n,loc,'candidate'if field in [x['candidate']for x in SPECS if x['contest']=='2024-president']else 'control')

def federal_vertical(key,county,year,acquired=False,style='electionware'):
    """Benton/Tillamook/Marion/Grant/Sherman per-geography presentations."""
    current=None;contest=None;u=None
    for pg,text,layer in pages(key,acquired):
        ls=text.splitlines()
        for i,line in enumerate(ls,1):
            s=re.sub(r'\s+',' ',line.strip());loc=dict(page=pg,line=i,text_layer=layer,raw_line=line)
            if re.match(r'^\d{2}\s*-\s*\w',s):current=s;contest=None
            if style=='tillamook':
                if year==2020 and s.startswith('Tillamook County - '):current=s.split(' - ',1)[1];contest=None
                if year==2022:
                    # Literal unit appears after county/election header, before
                    # contest. Unit labels on every original first page.
                    if s.endswith('Tillamook County'):
                        after=[x.strip()for x in ls[i:i+5]if x.strip()]
                        if after and len(after[0])<80:current=after[0]
            if style=='marion':
                m=re.match(r'^(\d{3})\s+([\d,]+) of ([\d,]+) registered voters',s)
                if m:current=m[1];contest=None
            if style=='detail':
                m=re.search(r'Precinct\s+(.+)',s,re.I)
                if m and not any(x in s for x in ['Results','Reporting','Report','Summary']):current=m[1].strip();contest=None
            is_senate=bool(re.fullmatch(r'(?:U\.?S\.?|United States) Senat(?:or|e)(?: Federal)?(?: - (?:6 Year Term - )?Vote for (?:one|One))?',s,re.I))
            is_gov=year==2022 and bool(re.fullmatch(r'Governor(?: Statewide Partisan)?(?: - (?:4 Year Term - )?Vote for (?:one|One))?',s,re.I))
            if is_senate or is_gov:
                contest=f'{year}-'+('senate'if is_senate else 'governor');u=get(key,county,contest,current or 'UNRESOLVED_SOURCE_UNIT')
            elif re.search(r' - Vote for|\(Vote for|^US Representative|^State Representative|^Secretary of State|^State Treasurer|^Oregon ',s,re.I)and not re.fullmatch(r'Vote For 1',s,re.I):
                contest=None
            if not contest:continue
            m=re.match(r'(.+?)\s+('+NUM+r')(?:\s+([\d.,]+)%)?(?:\s+('+NUM+r')\s+([\d.,]+)%)?$',s)
            if not m:continue
            label=m[1].strip();ci=canonical(label,contest)
            if ci is not None:
                if re.search(r'Not Assigned|Rejected|Unassigned',label,re.I):
                    add(u,label,val(m[2]),loc,'administrative_writein_scope');continue
                add(u,label,val(m[2]),loc)
                if style=='marion':
                    add(u,label,val(m[2]),loc,'candidate','Absentee Voting')
                    if m[4] is not None:add(u,label,val(m[4]),loc,'candidate','Total_nonadditive_repeat')
            elif re.search(r'Cast Votes:|Total Votes Cast|Contest Totals|Overvotes|Undervotes|Over Votes|Under Votes',label,re.I):
                add(u,label,val(m[2]),loc,'control')

def electionware_rows(key,county,year,acquired=False):
    """Contest tables; each source's administrative write-in columns stay distinct."""
    for pg,text,layer in pages(key,acquired):
        lines=text.splitlines();norm=[re.sub(r'\s+',' ',x.strip())for x in lines]
        hit=next((i for i,s in enumerate(norm)if re.fullmatch(r'US Senator(?: Federal)?|Governor(?: Statewide Partisan)?',s,re.I)),None)
        if hit is None:continue
        contest=f'{year}-'+('governor'if norm[hit].lower().startswith('governor')else 'senate')
        nspec=[x['candidate']for x in SPECS if x['contest']==contest]
        if not nspec:continue
        # Source header templates inspected from the complete relevant pages.
        if key in {'2020-04','2022-04'}:fields=nspec+['Total Votes Cast','overvotes','undervotes','Contest Total']
        elif key=='2022-03':fields=nspec+['Total Votes Cast','overvotes','undervotes']
        elif key=='2022-29':fields=nspec+['Write-in: Not Assigned','Total Votes Cast','overvotes','undervotes','Contest Total']
        elif key=='2022-00':fields=nspec+['Write-in: Not Assigned','overvotes','undervotes','Contest Total']
        elif key in {'2020-03','2020-30'}:fields=nspec+['Write-in: Not Assigned','Total Votes Cast','overvotes','undervotes']
        elif key=='2020-26':fields=nspec+['Total Votes Cast','overvotes','undervotes','Contest Total']
        else:continue
        for i in range(hit+1,len(lines)):
            line=lines[i];s=norm[i]
            m=re.match(r'^(.+?)\s{2,}('+NUM+r'(?:[\s\d,]*))\s*$',line.strip())
            if not m:continue
            label=m[1].strip()
            if not (re.match(r'\d',label)or label.lower()in ['total','totals']):continue
            tokens=m[2].split()
            if len(tokens)!=len(fields):
                # Still preserve the literal source row and observed identity.
                get(key,county,contest,label)
                issues.append(dict(issue='electionware_column_count',source_key=key,page=pg,line=i+1,raw_line=line,expected=fields,values=tokens));continue
            u=get(key,county,contest,label);loc=dict(page=pg,line=i+1,text_layer=layer,raw_line=line)
            for field,n in zip(fields,tokens):
                kind='administrative_writein_scope'if field=='Write-in: Not Assigned'else 'candidate'if field in nspec else 'control'
                add(u,field,val(n),loc,kind)

def main():
    vertical_keys=['2020-13','2020-14','2020-32','2020-33','2022-09','2022-13','2022-14','2022-21','2022-32',
                  '2020-06','2020-09','2020-12','2020-16','2022-05','2022-06','2022-12','2022-16','2022-31']
    for key in vertical_keys:
        r=next(x for x in INV if x['source_key']==key);county=Path(r['member_name']).stem;vertical(key,county,r['year'])
    vertical('2024-Wasco','Wasco',2024)
    # The original first page's generic write-in glyph was missed by OCR.
    # Direct visual inspection of the full original page reads 5 (not an
    # inferred residual); its other seven counts and explicit Total agree.
    u=get('2024-Wasco','Wasco','2024-president','Precinct 01')
    add(u,'Write-in',5,dict(page=1,text_layer='direct_visual_transcription',
        raw_line='Write-in 5 0.28%',review_path='source/SCHEMA.md'))
    for key in ['2020-07','2020-17','2020-19','2020-21','2022-07','2022-17','2022-19','2022-33']:
        r=next(x for x in INV if x['source_key']==key);scytl_table(key,Path(r['member_name']).stem,r['year'])
    for key in ['2022-01']:
        r=next(x for x in INV if x['source_key']==key);federal_vertical(key,Path(r['member_name']).stem,r['year'])
    federal_vertical('benton-2020-precincts','Benton',2020,True)
    federal_vertical('benton-2022-precincts','Benton',2022,True)
    for key in ['2020-28','2022-28']:
        federal_vertical(key,'Tillamook',int(key[:4]),style='tillamook')
    for key in ['2020-23','2022-23']:
        federal_vertical(key,'Marion',int(key[:4]),style='marion')
    for key in ['2020-04','2020-03','2020-26','2020-30','2022-00','2022-03','2022-04','2022-29']:
        r=next(x for x in INV if x['source_key']==key);electionware_rows(key,Path(r['member_name']).stem,r['year'])
    sov_csv('2020-25','Multnomah',2020)
    umatilla_csv()
    yamhill_csv()
    sov_csv('multnomah-2024-sovc2','Multnomah',2024,True)
    sov_csv('multnomah-2024-sovc1','Multnomah',2024,True)
    for key,c in [('clackamas-2024-canvass','Clackamas'),('marion-2024-canvass','Marion')]:clearballot_table_2024(key,c)
    scytl_table('multnomah-2024-president','Multnomah',2024,True)
    scytl_table('washington-2024-precincts','Washington',2024,True)
    dest=OUT/'native'
    (dest/'units.json').write_text(json.dumps(list(units.values()),ensure_ascii=False,indent=2)+'\n')
    b=''.join(json.dumps(x,ensure_ascii=False)+'\n'for x in observations).encode()
    (dest/'observations.jsonl.gz').write_bytes(gzip.compress(b,mtime=0))
    (dest/'extraction-issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n')
    summary=defaultdict(lambda:dict(units=0,complete_vectors=0,sums=defaultdict(int)))
    for u in units.values():
        if not u['additive']:continue
        k=(u['source_key'],u['county'],u['contest']);summary[k]['units']+=1
        n=len([x for x in SPECS if x['contest']==u['contest']])
        if len(u['choices'])==n:summary[k]['complete_vectors']+=1
        for c,v in u['choices'].items():summary[k]['sums'][c]+=v
    out=[]
    for k,v in summary.items():out.append(dict(source_key=k[0],county=k[1],contest=k[2],**v))
    (dest/'reconciliation-in-progress.json').write_text(json.dumps(out,indent=2)+'\n')
    for x in out:print(x['source_key'],x['contest'],x['units'],x['complete_vectors'],dict(x['sums']))
    print('issues',len(issues),'observations',len(observations))

if __name__=='__main__':main()
