"""Independent original-source extraction. Never reads preparation derivatives.

Run python extract.py. xlrd 2.0.2 is an external read-only dependency; set
PYTHONPATH if not installed. No downloads or peer writes occur in this script.
"""
from source_io import *
import collections, csv, io, re, sys, html
sys.dont_write_bytecode=True
if Path('/tmp/snn-xls-reading-libs').exists(): sys.path.insert(0,'/tmp/snn-xls-reading-libs')
import xlrd

TABLES = {
 '2024-senate-special':(2024,[17],['Pete Ricketts','Preston Love Jr.'],['Republican','Democratic']),
 '2024-senate-regular':(2024,[16],['Deb Fischer','Dan Osborn','Write-In Scatterings'],['Republican','By Petition',None]),
 '2024-president':(2024,[11,12],['Donald J. Trump & JD Vance','Kamala D. Harris & Tim Walz','Chase Oliver & Mike ter Maat','Cornel West & Melina Abdullah','Jill Stein & Samson Kpadenou','Write-In Scatterings'],['Republican','Democratic','Libertarian','Legal Marijuana NOW','BY PETITION',None]),
 '2022-governor':(2022,[13,14],['Jim Pillen & Joe Kelly','Carol Blood & Al Davis','Scott Zimmerman & Jason Blumenthal','Write-In Scatterings'],['Republican','Democratic','Libertarian',None]),
 '2020-senate':(2020,[16,17],['Ben Sasse','Chris Janicek','Gene Siadek','Preston Love Jr.','Write-In Scatterings'],['Republican','Democratic','Libertarian','Write-In',None])}

def canvasses():
    texts={y:pdftext(f'sos-{y}-canvass')[0].split('\f')for y in [2024,2022,2020]}
    configs={2024:([6,7],8,[8,9],7),2022:([6,7],7,[8,9],6),2020:([7,8],6,[9,10],7)}
    records=[]; controls={}; countysets=[]
    def readtable(y,pages,n,tid):
        pat=re.compile(r'([A-Za-z][A-Za-z .\'-]*?)\s{2,}('+r'\s+'.join([r'\d[\d,]*']*n)+r')(?=\s{2,}|$)')
        rows=[]
        for pn in pages:
            for ln,line in enumerate(texts[y][pn-1].splitlines(),1):
                if line.startswith('General Election'):continue
                for m in pat.finditer(line):
                    label=m[1].strip(); counts=[int(v.replace(',',''))for v in m[2].split()]
                    rows.append({'source_id':f'sos-{y}-canvass','table':tid,'actual_pdf_page':pn,
                      'source_line_1based':ln,'source_column_0based':m.start(),'county_literal':label,
                      'values':counts,'raw_line':line})
        footer=[r for r in rows if r['county_literal']in ['Total','Statewide Total']]
        assert len(footer)==1,(tid,footer)
        children=[r for r in rows if r not in footer]
        assert len(children)==93 and len({r['county_literal']for r in children})==93,(tid,len(children))
        assert [sum(r['values'][j]for r in children)for j in range(n)]==footer[0]['values'],tid
        countysets.append(set(r['county_literal']for r in children));records.extend(rows)
        controls[tid]={'statewide':footer[0],'counties':{r['county_literal']:r for r in children}}
    for y,(rp,rn,mp,mn)in configs.items():
        readtable(y,rp,rn,f'{y}-registration');readtable(y,mp,mn,f'{y}-voting-method')
    for tid,(y,p,c,party)in TABLES.items():
        readtable(y,p,len(c),tid)
        controls[tid]['candidate_columns']=[{'source_column_1based':j+1,'name':n,'party_literal':party[j],
          'scope':'scattering'if n=='Write-In Scatterings'else 'qualified_named_writein'if tid=='2020-senate'and j==3 else 'named_ballot_candidate'}for j,n in enumerate(c)]
    assert all(s==countysets[0]for s in countysets)
    for y in [2024,2022,2020]:
        for county,r in controls[f'{y}-registration']['counties'].items():
            assert sum(r['values'][1:-1])==r['values'][-1],(y,county,'reg')
        for county,r in controls[f'{y}-voting-method']['counties'].items():
            assert sum(r['values'][:-1])==r['values'][-1],(y,county,'method')
    jwrite(OUT/'extracts/state-controls.json',controls);jlwrite(OUT/'extracts/canvass-source-rows.jsonl.gz',records)
    return controls

def historical_html(controls):
    sid='sos-2024-observed-special-county-archive-20241204'
    rows=htmlrows(sid); byid={r['id']:r for r in rows if r['id']}
    counties={}; rawrows=[]
    def cand(r):
        if r is None:return None
        cc=[c['text']for c in r['cells']]
        return {'source_row_id':r['id'],'party_code_literal':cc[1]if len(cc)>1 else None,
          'name_literal':r['cells'][3]['text_literal']if len(cc)>3 else None,'votes':intcell(cc[4])if len(cc)>4 else None,
          'ballot_order_literal':cc[7]if len(cc)>7 else None,
          'contest_id_literal':cc[8]if len(cc)>8 else None,'row_complete':r['complete']}
    for r in rows:
        if re.fullmatch(r'ContentPlaceHolder1xuwgCounty_r_\d+',r['id']or''):
            c=[x['text']for x in r['cells']]; county=c[1].split(' County Precincts Reporting:')[0]
            vv=[cand(byid.get(r['id']+'_'+str(j)))for j in range(2)]
            assert [v['votes']for v in vv]==controls['2024-senate-special']['counties'][county]['values']
            counties[c[2]]={'county':county,'source_county_id_literal':c[2],'candidates':vv}
    assert len(counties)==93
    selected={}
    for r in LEDGER:
        if r['id'].startswith('sos-2024-special-native-archive-cty-')and r.get('status')==200:
            cid=re.search(r'[?&]cty=(\d+)',r['url'])[1]
            if cid not in selected or r.get('archive_entity_completeness',{}).get('complete_entity_claimed'):
                selected[cid]=r
    assert set(selected)==set(counties)
    native=[]; inventory=[]
    for cid,s in sorted(selected.items()):
        rr=htmlrows(s['id']); bi={r['id']:r for r in rr if r['id']}
        header=bi['ContentPlaceHolder1xuwgCounty_r_0'];hc=[c['text']for c in header['cells']]
        county=hc[1].split(' County Precincts Reporting:')[0];expected=int(hc[-1])
        assert county==counties[cid]['county']and hc[2]==cid
        cv=[cand(bi.get(header['id']+'_'+str(j)))for j in range(2)]
        assert [x['votes']for x in cv]==controls['2024-senate-special']['counties'][county]['values']
        raw=original(s['id']);complete=(b'</html>'in raw.lower() and not any('truncat' in str(v).lower()for k,v in s['headers'].items()if k.lower()=='warning'))
        text=raw.decode('utf-8-sig')
        def source_span(name):
            m=re.search(r'<span id="'+name+r'">(.*?)</span>',text,re.S)
            return html.unescape(re.sub('<[^>]+>','',m[1])).strip()if m else None
        status=source_span('lblHeader');clock=source_span('lblLastUpdated')
        unitrows=[]
        for r in rr:
            if re.fullmatch(r'ContentPlaceHolder1xuwgPrecinct_r_\d+',r['id']or''):
                cc=[c['text']for c in r['cells']];nid=cc[2]if len(cc)>2 else None
                vv=[cand(bi.get(r['id']+'_'+str(j)))for j in range(2)]
                v={'source_id':s['id'],'county':county,'source_county_id_literal':cid,
                  'source_header_row_id':r['id'],'native_id_literal':nid,'native_label_literal':r['cells'][1]['text_literal']if len(cc)>1 else None,
                  'kind':'administrative_countywide'if nid=='_TOT'else 'source_native_reporting_unit',
                  'entity_complete':complete,'candidates':vv,'generic_writeins':None,'ballots':None,
                  'registration':None,'blank':None,'under':None,'over':None,'method':'combined_unknown',
                  'publication_status_literal':status,'source_update_clock_literal':clock,'source_clock_timezone':None,
                  'source_line_1based':r['source_line_1based'],'character_start':r['character_start']}
                unitrows.append(v);native.append(v)
        children=[r for r in unitrows if r['kind']=='source_native_reporting_unit']
        sums=[sum((r['candidates'][j]or{}).get('votes')or 0 for r in children)for j in range(2)]
        if complete:
            assert len(children)==expected,(county,len(children),expected)
            assert all(x and x['votes']is not None for r in children for x in r['candidates'])
            assert sums==controls['2024-senate-special']['counties'][county]['values']
        inventory.append({'county':county,'source_id':s['id'],'source_county_id_literal':cid,
          'expected_source_native_count':expected,'retained_headers':len(children),'complete':complete,
          'known_votes':sums,'selected_for_disjoint_native_rollup':complete})
        inventory[-1].update({'publication_status_literal':status,'source_update_clock_literal':clock,'source_clock_timezone':None})
        rawrows.extend({'source_id':s['id'],**r}for r in rr if r['id']and re.match(r'ContentPlaceHolder1xuwg(?:County|Precinct)_r_',r['id']))
    rawrows.extend({'source_id':sid,**r}for r in rows if r['id']and r['id'].startswith('ContentPlaceHolder1xuwgCounty_r_'))
    jlwrite(OUT/'extracts/historical-html-all-positions.jsonl.gz',rawrows)
    jlwrite(OUT/'extracts/historical-html-native.jsonl.gz',native)
    jwrite(OUT/'extracts/historical-html-coverage.json',inventory)
    # Separate historical turnout publication, with every native table cell.
    sid='sos-2024-observed-turnout-archive-20241211';rr=htmlrows(sid)
    turnout=[r for r in rr if re.fullmatch(r'ContentPlaceHolder1xuwgResults_r_\d+',r['id']or'')]
    assert len(turnout)==93
    for r in turnout:
        cc=[c['text']for c in r['cells']];county=cc[1]
        assert [intcell(cc[2]),intcell(cc[3])]==[controls['2024-registration']['counties'][county]['values'][-1],controls['2024-voting-method']['counties'][county]['values'][-1]]
    jlwrite(OUT/'extracts/historical-turnout-positions.jsonl.gz',turnout)
    for sid in ['sos-2024-observed-public-all-csv-archive','sos-2024-observed-public-statewide-csv-archive']:
        rows=list(csv.reader(io.StringIO(original(sid).decode('utf-8-sig'))));assert len(rows[0])==15
        assert all(len(r)==16 and r[-1]==''for r in rows[1:])
        jlwrite(OUT/'extracts'/f'{sid}.rows.jsonl.gz',[{'source_row_1based':i+1,'cells':r}for i,r in enumerate(rows)])
    return native,inventory

DOUGLAS=[(2024,'U.S. Senator - 2-Yr Term','2024-senate-special'),(2024,'U.S. Senator','2024-senate-regular'),(2024,'U.S. President','2024-president'),(2022,'Governor','2022-governor'),(2020,'U.S. Senator','2020-senate')]
def douglas(controls):
    books={};topology=[];positions=[];units=[];checks=[]
    for y in [2024,2022,2020]:
        sid=f'county-douglas-{y}-native-xls';b=original(sid)
        books[y]=xlrd.open_workbook(file_contents=b,formatting_info=True)
        book=books[y]
        topology.append({'source_id':sid,'datemode':book.datemode,'sheets':[{'name':s.name,'nrows':s.nrows,'ncols':s.ncols}for s in book.sheets()],
          'instructions':[{'source_row_1based':i+1,'values':book.sheet_by_name('Instructions').row_values(i)}for i in range(book.sheet_by_name('Instructions').nrows)]})
        pdftext(f'county-douglas-{y}-summary-pdf')
    for y,sheet,contest in DOUGLAS:
        sid=f'county-douglas-{y}-native-xls';s=books[y].sheet_by_name(sheet);head=s.row_values(1)
        foot=[i for i in range(s.nrows)if s.cell_value(i,0)in ['Total','Totals']];assert len(foot)==1;foot=foot[0]
        assert all(all(v==''for v in s.row_values(i))for i in range(foot+1,s.nrows))
        cols=[j for j,h in enumerate(head)if h and h not in ['Ward-Precinct','Ward - Precinct','% of Vote']]
        for j in cols:
            assert all(s.cell_type(i,j)==2 and s.cell_value(i,j)==int(s.cell_value(i,j))for i in range(2,foot))
            assert sum(s.cell_value(i,j)for i in range(2,foot))==s.cell_value(foot,j)
        tc=head.index('Total Votes');ov=head.index('Over Votes');un=head.index('Under Votes')
        candcols=[j for j in cols if j not in [tc,ov,un]]
        # The source explicitly separates qualified Love2020 from other write-ins.
        statecols=candcols[:len(TABLES[contest][2])]
        expected=controls[contest]['counties']['Douglas']['values']
        assert [int(s.cell_value(foot,j))for j in statecols]==expected,(contest,head)
        for i in range(2,foot):
            assert sum(s.cell_value(i,j)for j in candcols)==s.cell_value(i,tc)
            units.append({'source_id':sid,'county':'Douglas','contest':contest,'sheet':sheet,
              'source_row_1based':i+1,'native_id_literal':s.cell_value(i,0),
              'native_label_literal':s.cell_value(i,0),'kind':'ward_precinct_combined_methods',
              'state_scope_candidate_values':[int(s.cell_value(i,j))for j in statecols],
              'candidate_fields':[{'source_column_1based':j+1,'label_literal':head[j],'votes':int(s.cell_value(i,j))}for j in candcols],
              'reported_total_votes':int(s.cell_value(i,tc)),'over':int(s.cell_value(i,ov)),'under':int(s.cell_value(i,un)),
              'contest_volume_arithmetic':int(sum(s.cell_value(i,j)for j in [tc,ov,un])),
              'ballots':None,'registration':None,'blank':None,'method':'early_and_polling_combined_by_source_instructions'})
        for i in range(s.nrows):positions.append({'source_id':sid,'sheet':sheet,'source_row_1based':i+1,'values':s.row_values(i),'cell_types':list(s.row_types(i))})
        checks.append({'source_id':sid,'contest':contest,'sheet':sheet,'header':head,'native_count':foot-2,
          'footer_source_row_1based':foot+1,'footer_values':s.row_values(foot),'numeric_native_footer_fields_checked':len(cols),
          'trailing_formatted_blank_rows':list(range(foot+2,s.nrows+1))})
    jlwrite(OUT/'extracts/douglas-original-positions.jsonl.gz',positions)
    jlwrite(OUT/'extracts/douglas-native.jsonl.gz',units)
    jwrite(OUT/'extracts/douglas-controls.json',{'topology':topology,'tables':checks})
    return units

LANC={'US President':'2024-president','US Senator 6 YR':'2024-senate-regular','US Senator 2 YR':'2024-senate-special'}
def lancaster(controls):
    sid='county-lancaster-2024-final-precinct-pdf-actual-archive';t,info=pdftext(sid)
    pages=t.split('\f');assert not pages.pop().strip()and len(pages)==1431
    contexts=[];statistics=[];labels=[];clocks=collections.Counter()
    numrow=re.compile(r'^\s*(.*?)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s*$')
    for pn,p in enumerate(pages,1):
        foot=re.search(r'Precinct Summary - (.*?)\s+([\d,]+) of 1,431',p)
        assert foot and int(foot[2].replace(',',''))==pn;clocks[foot[1].strip()]+=1
        label=re.search(r'Lancaster County, Nebraska\s*\n\s*\n([^\n]+)',p)[1].strip();labels.append(label)
        lines=p.splitlines()
        def fields(start,end):
            ff=[]
            for ln in range(start,end):
                m=numrow.fullmatch(lines[ln])
                if m:ff.append({'label_literal':m[1],'counts':[int(m[i].replace(',',''))for i in range(2,6)],
                  'source_line_1based':ln+1,'raw_line':lines[ln]})
            assert len({r['label_literal']for r in ff})==len(ff)
            for r in ff:assert r['counts'][0]==sum(r['counts'][1:]),(pn,r)
            return ff
        if re.search(r'^Statistics\s+TOTAL',p,re.M):
            e=next(i for i,l in enumerate(lines)if l.strip()=='US President')
            reg=re.search(r'^Registered Voters - Total\s+(\d[\d,]*)\s*$',p,re.M)
            stats=fields(0,e);assert {r['label_literal']for r in stats}=={'Ballots Cast - Total','Ballots Cast - Blank'}
            statistics.append({'source_id':sid,'actual_pdf_page':pn,'native_label_literal':label,'registered_total':int(reg[1].replace(',','')),
              'registration_methods':None,'source_turnout_percent':re.search(r'^Voter Turnout - Total\s+([\d.]+%)',p,re.M)[1],
              'fields':stats,'raw_block':'\n'.join(lines[:e])})
        for i,line in enumerate(lines):
            if line.strip()not in LANC:continue
            end=next(j for j in range(i+1,len(lines))if re.match(r'^\s*Contest Totals\s+',lines[j]))
            ff=fields(i,end+1);f={r['label_literal']:r['counts']for r in ff}
            contest=LANC[line.strip()];n=len(TABLES[contest][2]);names=[r['label_literal']for r in ff if re.match(r'^(Rep|Dem|Pet|Lib|Lmn) ',r['label_literal'])]
            assert len(names)==(5 if contest=='2024-president'else 2)
            assert set(f)==set(names+['Write-In Totals','Not Assigned','Total Votes Cast','Overvotes','Undervotes','Contest Totals'])
            for j in range(4):
                assert sum(f[k][j]for k in names+['Write-In Totals'])==f['Total Votes Cast'][j]
                assert f['Write-In Totals'][j]==f['Not Assigned'][j]
                assert sum(f[k][j]for k in ['Total Votes Cast','Overvotes','Undervotes'])==f['Contest Totals'][j]
            contexts.append({'source_id':sid,'county':'Lancaster','contest':contest,'contest_label_literal':line.strip(),
              'actual_pdf_page':pn,'native_id_literal':None,'native_label_literal':label,'kind':'county_pdf_native_reporting_context',
              'method_columns':['TOTAL','Election Day','Early Voting','Provisional'],'fields':ff,'raw_block':'\n'.join(lines[i:end+1]),
              'source_footer_clock_literal':foot[1].strip(),'source_footer_timezone':None})
    assert len(set(labels))==199 and len(statistics)==199
    assert collections.Counter(c['contest']for c in contexts)=={'2024-president':199,'2024-senate-special':198,'2024-senate-regular':198}
    st={r['native_label_literal']:r for r in statistics}
    for c in contexts:
        f={r['label_literal']:r['counts']for r in c['fields']};s=st[c['native_label_literal']]
        assert f['Contest Totals']==next(r['counts']for r in s['fields']if r['label_literal']=='Ballots Cast - Total')
    totals={}
    for contest in LANC.values():
        cs=[c for c in contexts if c['contest']==contest];names=[r['label_literal']for r in cs[0]['fields']]
        totals[contest]={n:[sum(next(f['counts'][j]for f in c['fields']if f['label_literal']==n)for c in cs)for j in range(4)]for n in names}
    for contest,fields in [('2024-senate-special',['Rep Pete Ricketts','Dem Preston Love Jr.']),('2024-senate-regular',['Rep Deb Fischer','Pet Dan Osborn','Write-In Totals'])]:
        assert [totals[contest][f][0]for f in fields]==controls[contest]['counties']['Lancaster']['values']
    extra=set(c['native_label_literal']for c in contexts if c['contest']=='2024-president')-set(c['native_label_literal']for c in contexts if c['contest']=='2024-senate-special')
    assert extra=={'New or Former Resident'}
    jlwrite(OUT/'extracts/lancaster-native-methods.jsonl.gz',contexts)
    jwrite(OUT/'extracts/lancaster-statistics.json',statistics)
    jwrite(OUT/'extracts/lancaster-controls.json',{'actual_pages':1431,'native_units_all_contexts':199,'source_clocks':dict(clocks),'totals':totals,
      'Senate_unavailable_contexts':[{'label':'New or Former Resident','Senate':None,'presidential_contest_volume':[1,0,1,0],'reason':'No Senate section in original; unavailable, not imputed zero.'}]})
    return contexts,statistics

def main():
    controls=canvasses();native,inventory=historical_html(controls);du=douglas(controls);la,stats=lancaster(controls)
    jwrite(OUT/'source/reused-originals.json',list(USED.values()))
    print(json.dumps({'canvass_tables':len(controls),'counties':93,'HTML_native_complete':sum(r['retained_headers']for r in inventory if r['complete']),
      'HTML_partial':sum(not r['complete']for r in inventory),'Douglas_contexts':len(du),'Lancaster_contexts':len(la),
      'special_county_controls':controls['2024-senate-special']['statewide']['values']}))
if __name__=='__main__':main()
