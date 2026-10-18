#!/usr/bin/env python3
"""Independently extract Kansas primary originals and calculate all-county priority.

No network, no peer writes. Rebuild from the repository root with Python 3 and
pdftotext. All unknown native cells stay unknown, including apparent zero-vote
precincts whose cells are blank. County controls never allocate those cells.
"""
from collections import Counter, defaultdict
import csv, datetime, gzip, html, io, json, re
from fractions import Fraction
from sources import HERE, STATE, source_bytes, worksheets, pdf_text, dump_json, sha, shared_manifest

BROAD = 'sos-2024-president-county'
SOURCES = {
    'president_2024': ('sos-2024-president-precinct', 'sos-2024-general-canvass', '2024-11-05', 'President / Vice President'),
    'senate_2022': ('sos-2022-senate-precinct', 'sos-2022-general-canvass', '2022-11-08', 'United States Senate'),
    'senate_2020': ('sos-2020-senate-precinct', 'sos-2020-general-canvass', '2020-11-03', 'United States Senate'),
    'senate_primary_2026': ('sos-2026-senate-primary-precinct', 'sos-2026-primary-canvass', '2026-08-04', 'United States Senate'),
}
# Explicit identities, not a fuzzy or party-only join. Source labels remain intact.
IDENTITIES = {
    'president_2024': {
        'harris': ('D', ['Kamala D. Harris / Tim Walz','Harris / Walz','DEM Harris and Walz']),
        'trump': ('R', ['Donald J. Trump / JD Vance','Trump / Vance','REP Trump and Vance']),
        'oliver': ('L', ['Chase Oliver / Mike ter Maat','Oliver / ter Maat','LIB Oliver and ter Maat']),
        'kennedy': ('i', ['Robert F. Kennedy Jr./ Nicole Shanahan','Kennedy Jr. / Shanahan','IND Kennedy Jr. and Shanahan','ind Kennedy Jr. and Shanahan']),
    },
    'senate_2022': {
        'holland': ('D', ['Holland, Mark R.','Mark R. Holland','DEM Mark R. Holland']),
        'moran': ('R', ['Moran, Jerry','Jerry Moran','REP Jerry Moran']),
        'graham': ('L', ['Graham, David C','David C Graham','David C. Graham','LIB David C Graham','LIB David C. Graham']),
    },
    'senate_2020': {
        'bollier': ('D', ['Bollier, Barbara','Barbara Bollier','DEM Barbara Bollier','Dem Barbara Bollier']),
        'marshall': ('R', ['Marshall, Roger','Roger Marshall','REP Roger Marshall','Rep Roger Marshall']),
        'buckley': ('L', ['Buckley, Jason','Jason Buckley','LIB Jason Buckley','Lib Jason Buckley']),
    },
    'senate_primary_2026': {
        'anderson': ('D',['Anderson, Damon','Damon Anderson']),
        'davis': ('D',['Davis, Christy','Christy Davis']),
        'hamilton': ('D',['Hamilton, Adam','Adam Hamilton']),
        'hart': ('D',['Hart, Jason','Jason Hart']),
        'latz': ('D',['Latz, Kevin','Kevin Latz']),
        'murray': ('D',['Murray, Erik','Erik Murray']),
        'neumann': ('D',['Neumann, Sandy Spidel','Sandy Spidel Neumann']),
        'parelkar': ('D',['Parelkar, Anne','Anne Parelkar']),
        'schmidt': ('D',['Schmidt, Patrick C.','Patrick C. Schmidt']),
        'soetaert': ('D',['Soetaert, Michael "Mike"','Michael "Mike" Soetaert']),
        'taylor': ('D',['Taylor, Noah','Noah Taylor']),
        'marshall': ('R',['Marshall, Roger','Roger Marshall']),
        'naramore': ('R',['Naramore, Pond','Pond Naramore']),
    },
}
ALIAS = {'Comanche ': 'Comanche'}
FOUR = {'Johnson','Sedgwick','Shawnee','Wyandotte'}

def identity(contest, label):
    matches = [k for k,(p,labels) in IDENTITIES[contest].items() if label in labels]
    assert len(matches) == 1, (contest,label,matches)
    return matches[0]

def vote_value(raw):
    if raw is not None and re.fullmatch(r'(\d+|\d{1,3}(,\d{3})+)',raw): return int(raw.replace(',','')), 'reported_integer'
    if raw is None or raw == '': return None, 'blank_unavailable'
    if 'redact' in raw.lower() or 'KSA 25-2701' in raw: return None, 'redacted'
    raise ValueError(('unrecognized vote value',raw))

def csv_output(path, rows, fields=None):
    rows = list(rows)
    if fields is None: fields = list(rows[0])
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream,fieldnames=fields,lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    data = stream.getvalue().encode()
    target = HERE/path
    target.write_bytes(gzip.compress(data,mtime=0) if str(path).endswith('.gz') else data)

def jsonl_output(path, rows):
    data = b''.join((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode() for r in rows)
    (HERE/path).write_bytes(gzip.compress(data,mtime=0))

def unit_key(source,sheet,county,fields):
    payload = json.dumps([source,sheet,county,fields],ensure_ascii=False,separators=(',',':'))
    return source+':'+sha(payload.encode())[:24]

def percent(n,d): return f'{100*n/d:.10f}'

def rank_counts(values):
    order = sorted(values,key=lambda n:(-values[n],FIPS[n]))
    total = sum(values.values()); running=0; out=[]; crossing=None
    for rank,n in enumerate(order,1):
        before=running; running += values[n]
        if crossing is None and 5*running >= 4*total: crossing=rank
        out.append({'rank':rank,'county':n,'county_fips':FIPS[n],'county_key':'US-KS-'+FIPS[n],
                    'votes':values[n],'cumulative_votes':running,'share_exact':str(Fraction(values[n],total)),
                    'share_pct':percent(values[n],total),'cumulative_share_pct':percent(running,total)})
    assert crossing is not None and sum(values[n] for n in order[:crossing-1])*5 < total*4
    return {'denominator':total,'top15_votes':sum(values[n] for n in order[:15]),
            'top15_share_exact':str(Fraction(sum(values[n] for n in order[:15]),total)),
            'top15_share_pct':percent(sum(values[n] for n in order[:15]),total),
            'minimum80_count':crossing,'minimum80_votes':out[crossing-1]['cumulative_votes'],
            'minimum80_share_pct':out[crossing-1]['cumulative_share_pct'],
            'preceding_count':crossing-1,'preceding_votes':out[crossing-2]['cumulative_votes'],
            'preceding_share_pct':out[crossing-2]['cumulative_share_pct'],
            'crossing':out[crossing-1],'remainder_count':len(order)-crossing,
            'remainder_votes':total-out[crossing-1]['cumulative_votes'],'all_unit_order':out}

def county_codes():
    out={}
    for line in source_bytes('county-codes-2020').decode().splitlines():
        a=line.split('|')
        if a[0]=='KS':
            assert a[4].endswith(' County')
            out[a[4][:-7]]=a[1]+a[2]
    assert len(out)==105 and len(set(out.values()))==105
    return out

def extract_original_rows(sid, sheets):
    # All original rows/cell values remain inspectable, including unrelated fields.
    jsonl_output('extracts/'+sid+'-rows.jsonl.gz',
      ({'source_id':sid,'sheet':s,'xml_path':p,'row':n,'cells':d} for s,p,rs in sheets for n,d in rs))

def main():
    global FIPS
    FIPS=county_codes()
    raw_sheets={sid:list(worksheets(source_bytes(sid))) for sid in [BROAD]+[v[0] for v in SOURCES.values()]+['turnout-2022','registration-2024-november','registration-2026-october','inactive-2026-october']}
    for sid,sheets in raw_sheets.items(): extract_original_rows(sid,sheets)
    units=[]; observations=[]; footers=[]; main_counties={}; county_counts={}; controls=[]; summaries=[]
    def add_unit(sid,sheet,xml,contest,county_native,fields,label,source_rows,vs,role='native_reporting_identity'):
        county=ALIAS.get(county_native,county_native); assert county in FIPS
        key=unit_key(sid,sheet,county_native,fields)
        row={'unit_key':key,'source_id':sid,'sheet':sheet,'xml_path':xml,'contest':contest,
             'election_date':'2024-11-05' if sid==BROAD else SOURCES[contest][2],
             'county_native':county_native,'county':county,'county_fips':FIPS[county],
             'county_key':'US-KS-'+FIPS[county],'native_id_fields':fields,'native_label':label,
             'source_rows':source_rows,'role':role,'geometry_status':'unverified_historical_identity',
             'method':'all_methods_combined_or_unspecified_by_source',
             'named_candidate_numeric_sum':sum(v['votes'] for v in vs if v['category']=='named_candidate' and v['votes'] is not None),
             'named_candidate_total':sum(v['votes'] for v in vs if v['category']=='named_candidate') if all(v['votes'] is not None for v in vs if v['category']=='named_candidate') else None,
             'unknown_named_cells':sum(v['category']=='named_candidate' and v['votes'] is None for v in vs),
             'generic_write_in_votes':next((v['votes'] for v in vs if v['category']=='generic_write_in'),None),
             'reported_total_votes_cast':next((v['votes'] for v in vs if v['category']=='reported_contest_total'),None)}
        if row['unknown_named_cells']: row['role']='native_identity_with_unavailable_counts'
        units.append(row)
        for v in vs:
            observations.append({'unit_key':key,'source_id':sid,'sheet':sheet,'xml_path':xml,
                                 'county_fips':FIPS[county],'county':county,'contest':contest,**v})
        return row
    def obs(contest,label,raw,row,col,party=None,category='named_candidate'):
        value,status=vote_value(raw)
        ck=identity(contest,label) if category=='named_candidate' else category
        return {'source_candidate_label':label,'candidate_key':ck,'category':category,
                'source_party_label':party,'verified_candidate_party':IDENTITIES[contest][ck][0] if category=='named_candidate' else None,
                'raw_value':raw,'votes':value,'value_status':status,'row':row,'column':col,'cell':f'{col}{row}'}
    # Broad original: four candidates for every exact A:F identity.
    groups=defaultdict(list); bs,bp,brs=raw_sheets[BROAD][0]
    for n,d in brs[1:]:
        assert d['G']=='President / Vice President'
        groups[tuple(d.get(c) for c in 'ABCDEF')].append((n,d))
    broad_counts={n:Counter() for n in FIPS}
    for fields,rs in groups.items():
        native=fields[4];county=ALIAS.get(native,native)
        vs=[obs('president_2024',d['H'],d.get('J'),n,'J',d.get('I')) for n,d in rs]
        assert len(vs)==4 and len({v['candidate_key'] for v in vs})==4
        u=add_unit(BROAD,bs,bp,'president_2024',native,dict(zip('ABCDEF',fields)),fields[5],[n for n,d in rs],vs,'district_location_precinct_context')
        assert u['unknown_named_cells']==0
        for v in vs:broad_counts[county][v['candidate_key']]+=v['votes']
    assert len(groups)==4567
    # Precinct originals: main101 and supplements, footers stored independently.
    for contest,(sid,pdf,date,race) in SOURCES.items():
        sheets=raw_sheets[sid]; ms,mp,mrs=sheets[0]; cg=defaultdict(list)
        for n,d in mrs[1:]:
            if not any(v is not None for v in d.values()):continue
            assert d['C']==race,(sid,n,d)
            cg[(d['A'],d['B'],d.get('G'))].append((n,d))
        counties={ALIAS.get(k[0],k[0]) for k in cg};assert counties==set(FIPS)-FOUR
        main_counties[sid]=sorted(counties)
        counts={n:Counter() for n in FIPS}
        for (native,precinct,vtd),rs in cg.items():
            vs=[obs(contest,d['D'],d.get('F'),n,'F',d.get('E')) for n,d in rs]
            assert len(vs)==len(IDENTITIES[contest]) and len({v['candidate_key'] for v in vs})==len(vs),(sid,native,precinct)
            add_unit(sid,ms,mp,contest,native,{'County':native,'Precinct':precinct,'VTD':vtd},precinct,[n for n,d in rs],vs)
            for v in vs:
                if v['votes'] is not None:counts[ALIAS.get(native,native)][v['candidate_key']]+=v['votes']
        for sheet,xml,rs in sheets[1:]:
            county=sheet.title();assert county in FOUR
            rd=dict(rs)
            if contest=='president_2024':
                start=3;hr=2
                names={'Johnson':'C','Sedgwick':'A','Shawnee':'B','Wyandotte':'A'}
                cols={'Johnson':'DEFG','Sedgwick':'BCDE','Shawnee':'CDEF','Wyandotte':'BCDE'}[county]
                idcols={'Johnson':'ABC','Sedgwick':'A','Shawnee':'AB','Wyandotte':'A'}[county]
            elif contest=='senate_2022':
                start=3;hr=2;names={n:'B' for n in FOUR}
                cols='EFG' if county=='Johnson' else 'CDE';idcols='ABCD' if county=='Johnson' else 'AB'
            elif contest=='senate_2020':
                start={'Johnson':4,'Shawnee':4,'Sedgwick':5,'Wyandotte':6}[county]
                hr=start-1;names={n:('B' if n=='Wyandotte' else 'A') for n in FOUR}
                cols='EFH' if county=='Wyandotte' else 'BCD';idcols='B' if county=='Wyandotte' else 'A'
            else:
                start=3 if county=='Shawnee' else 4;hr=start-1
                names={n:'A' for n in FOUR};cols='BCDEFGHIJKLMN';idcols='A'
            namecol=names[county]
            printed={}
            for n,d in rs:
                if n<start or not d.get(namecol):continue
                label=d[namecol]
                # The 2020 Wyandotte sheet has repeated page headers and unused rows.
                if contest=='senate_2020' and county=='Wyandotte' and label.upper()!='TOTALS' and not any(d.get(c,'').isdigit() for c in cols):continue
                vs=[]
                for col in cols:
                    header=rd[hr][col]
                    party=rd.get(2,{}).get(col) if contest=='senate_2020' and county in {'Johnson','Shawnee'} else None
                    if contest=='senate_primary_2026' and hr==3:party=rd.get(2,{}).get(col)
                    if party is None:
                        match=re.match(r'^(DEM|Dem|REP|Rep|LIB|Lib|IND|ind)\b',header)
                        party=match[1] if match else None
                    vs.append(obs(contest,header,d.get(col),n,col,party))
                    vs[-1]['source_header_context']={str(h):rd.get(h,{}).get(col) for h in range(1,hr+1)}
                if contest=='senate_2020' and county in {'Shawnee','Sedgwick','Wyandotte'}:
                    col='I' if county=='Wyandotte' else 'E'
                    vs.append(obs(contest,rd[hr][col],d.get(col),n,col,rd.get(2,{}).get(col) if county=='Shawnee' else None,'generic_write_in'))
                    vs[-1]['source_header_context']={str(h):rd.get(h,{}).get(col) for h in range(1,hr+1)}
                if contest=='senate_2020' and county=='Sedgwick':
                    vs.append(obs(contest,rd[hr]['F'],d.get('F'),n,'F',None,'reported_contest_total'))
                if label.upper() in {'COUNTY TOTALS','TOTALS'}:
                    for v in vs:
                        footers.append({'source_id':sid,'sheet':sheet,'county':county,'county_fips':FIPS[county],'contest':contest,**v})
                        if v['category']=='named_candidate':
                            assert v['votes'] is not None
                            printed[v['candidate_key']]=v['votes']
                    continue
                ids={col:{'header':rd.get(1,{}).get(col),'value':d.get(col)} for col in idcols}
                add_unit(sid,sheet,xml,contest,county,ids,label,[n],vs)
            if printed:
                assert set(printed)==set(IDENTITIES[contest])
                counts[county].update(printed)
            else:
                assert contest=='senate_2020' and county=='Wyandotte'
                for o in observations:
                    if o['source_id']==sid and o['county']==county and o['category']=='named_candidate' and o['votes'] is not None:
                        counts[county][o['candidate_key']]+=o['votes']
        # State certificate is independently parsed; no residual allocation.
        text=pdf_text(pdf); (HERE/'extracts'/f'{pdf}.txt').write_text(text)
        section=text.split(race,1)[1].split('United States House of Representatives 1',1)[0]
        parsed=[]
        for party,label,number in re.findall(r'^\s+([DRLi])-([^\n]+?)\s+([\d,]+)\s+[\d.]+%',section,re.M):
            ck=identity(contest,label.strip());value=int(number.replace(',',''));observed=sum(v[ck] for v in counts.values())
            controls.append({'contest':contest,'candidate_key':ck,'source_candidate_label':label.strip(),'party':party,'state_control_source':pdf,'control_votes':value,'county_sum':observed,'difference':observed-value})
            assert observed==value,(contest,ck,observed,value)
            parsed.append(ck)
        assert len(parsed)==len(IDENTITIES[contest])
        county_counts[contest]=counts
        if contest=='president_2024':
            assert counts==broad_counts,'broad/precinct county candidate discrepancy'
        for county in FIPS:
            uu=[u for u in units if u['source_id']==sid and u['county']==county]
            oo=[o for o in observations if o['source_id']==sid and o['county']==county]
            for ck in IDENTITIES[contest]:
                known=sum(o['votes'] for o in oo if o['candidate_key']==ck and o['votes'] is not None)
                unknown=sum(o['candidate_key']==ck and o['votes'] is None for o in oo)
                summaries.append({'source_id':sid,'contest':contest,'county_fips':FIPS[county],'county':county,'candidate_key':ck,
                                  'county_control_votes':counts[county][ck],'numeric_native_sum':known,
                                  'unavailable_native_cells':unknown,'county_control_minus_numeric_native_sum':counts[county][ck]-known,
                                  'allocation_status':'unallocated; original blank/redacted cells preserved'})
    # Complete county administrative measures, each with its own source and vintage.
    turnout24={};turnout22={};registration24={};registration26={};inactive26={};admin=[]
    for n,d in raw_sheets[BROAD][1][2][1:]:
        if d.get('B','').isdigit():
            row={'county_native':d['A'],'ballots_cast':int(d['B']),'registered_voters':int(d['C']),'published_turnout_literal':d['D'],'row':n}
            if d['A']=='Total':footer24=row
            else:turnout24[d['A']]=row
    for n,d in raw_sheets['turnout-2022'][0][2]:
        if (d.get('A') or '').endswith(' COUNTY'):
            county=d['A'][:-7].title();county='McPherson' if county=='Mcpherson' else county
            assert county in FIPS
            turnout22[county]={'advance_ballots_returned_by_mail':int(d['B']) if d['B'].isdigit() else None,'advance_ballots_returned_by_mail_raw':d['B'],'ballots_cast':int(d['D']),'registered_voters':int(d['F']),'row':n,'county_native':d['A']}
        elif (d.get('B') or '').isdigit() and not d.get('A'):
            footer22={'advance_ballots_returned_by_mail':int(d['B']),'ballots_cast':int(d['D']),'registered_voters':int(d['F']),'row':n}
    for sid,store,countcol,totalcol in [('registration-2024-november',registration24,'A','I'),('registration-2026-october',registration26,'B','J'),('inactive-2026-october',inactive26,'B','C')]:
        for n,d in raw_sheets[sid][0][2][1:]:
            if d[countcol]=='Grand Total':continue
            county=d[countcol];assert county in FIPS
            values={'registered_voters':int(d[totalcol]),'row':n}
            if sid=='inactive-2026-october':values.update(inactive=int(d['D']),active=int(d['F']),percentage_inactive_literal=d['E'])
            if 'A' in d and countcol=='B':values['source_date_excel_serial']=d['A']; values['source_date']=(datetime.datetime(1899,12,30)+datetime.timedelta(days=int(d['A']))).date().isoformat()
            store[county]=values
    assert all(set(t)==set(FIPS) for t in [turnout24,turnout22,registration24,registration26,inactive26])
    for metric in ['ballots_cast','registered_voters']:assert sum(t[metric] for t in turnout24.values())==footer24[metric]
    for metric in ['advance_ballots_returned_by_mail','ballots_cast','registered_voters']:assert sum(t[metric] for t in turnout22.values() if t[metric] is not None)==footer22[metric]
    for county in FIPS:
        assert registration26[county]['registered_voters']==inactive26[county]['registered_voters']
        assert inactive26[county]['active']+inactive26[county]['inactive']==inactive26[county]['registered_voters']
        for sid,store,scope in [(BROAD,turnout24,'2024 Turnout sheet; registration date/status unspecified'),('turnout-2022',turnout22,'2022 general turnout; registration date/status unspecified'),('registration-2024-november',registration24,'November 2024 registration; status not separated'),('registration-2026-october',registration26,'2026-10-01 registered voters'),('inactive-2026-october',inactive26,'2026-10-01 active and inactive')]:
            admin.append({'source_id':sid,'county':county,'county_fips':FIPS[county],'scope':scope,**store[county]})
    rankings={}
    for contest,counts in county_counts.items():rankings[contest]=rank_counts({n:sum(v.values()) for n,v in counts.items()})
    for name,store,metric in [('ballots_2024',turnout24,'ballots_cast'),('ballots_2022',turnout22,'ballots_cast'),('registration_2024_turnout_sheet',turnout24,'registered_voters'),('registration_2024_november',registration24,'registered_voters'),('registration_2026_october',registration26,'registered_voters'),('active_registration_2026_october',inactive26,'active')]:
        rankings[name]=rank_counts({n:r[metric] for n,r in store.items()})
    ranking=rankings['president_2024'];priority=[r['county'] for r in ranking['all_unit_order'][:ranking['minimum80_count']]]
    rows=[]
    for rankrow in ranking['all_unit_order']:
        n=rankrow['county'];f=FIPS[n]
        row={'county_fips':f,'county_key':'US-KS-'+f,'county':n,'rank':rankrow['rank']}
        for contest,counts in county_counts.items():
            row.update({contest+'_'+ck:counts[n][ck] for ck in IDENTITIES[contest]})
            row[contest+'_total']=sum(counts[n].values())
        row.update(president_2024_share_exact=rankrow['share_exact'],president_2024_share_pct=rankrow['share_pct'],president_2024_cumulative_votes=rankrow['cumulative_votes'],president_2024_cumulative_share_pct=rankrow['cumulative_share_pct'],top15=int(rankrow['rank']<=15),priority80=int(n in priority),
                   ballots_cast_2024_broad=turnout24[n]['ballots_cast'],registered_voters_2024_broad=turnout24[n]['registered_voters'],
                   ballots_cast_2022=turnout22[n]['ballots_cast'],registered_voters_2022=turnout22[n]['registered_voters'],advance_ballots_returned_by_mail_2022=turnout22[n]['advance_ballots_returned_by_mail'],
                   registered_voters_2024_november=registration24[n]['registered_voters'],registered_voters_2026_10_01=registration26[n]['registered_voters'],inactive_voters_2026_10_01=inactive26[n]['inactive'],active_voters_2026_10_01=inactive26[n]['active'],
                   generic_write_in_2024='',valid_named_write_in_2024='',undervotes_2024='',overvotes_2024='',blank_ballots_2024='',
                   candidate_universe='four named presidential tickets; unreported write-in/blank/under/over unavailable',source_id=BROAD)
        generic=[u['generic_write_in_votes'] for u in units if u['contest']=='senate_2020' and u['county']==n and u['generic_write_in_votes'] is not None]
        row['generic_write_in_2020_published_supplement']=sum(generic) if generic else ''
        rows.append(row)
    csv_output('../county-turnout.csv',rows)
    csv_output('extracts/candidate-controls.csv',controls)
    csv_output('extracts/native-county-reconciliation.csv',summaries)
    jsonl_output('extracts/county-administration.jsonl.gz',admin)
    jsonl_output('extracts/native-units.jsonl.gz',units)
    jsonl_output('extracts/candidate-observations.jsonl.gz',observations)
    jsonl_output('extracts/county-summary-observations.jsonl.gz',footers)
    # Source-family orders are separate overlapping views, never concatenated.
    native_orders=[]
    for sid in [BROAD]+[v[0] for v in SOURCES.values()]:
        us=[u for u in units if u['source_id']==sid]
        known=sorted([u for u in us if u['named_candidate_total'] is not None],key=lambda u:(-u['named_candidate_total'],u['county_fips'],u['sheet'],u['source_rows']))
        unknown=sorted([u for u in us if u['named_candidate_total'] is None],key=lambda u:(u['county_fips'],u['sheet'],u['source_rows']))
        for i,u in enumerate(known,1):native_orders.append({'source_id':sid,'unit_key':u['unit_key'],'county_fips':u['county_fips'],'known_count_rank':i,'named_candidate_total':u['named_candidate_total'],'order_scope':'reported complete integers only'})
        for u in unknown:native_orders.append({'source_id':sid,'unit_key':u['unit_key'],'county_fips':u['county_fips'],'known_count_rank':None,'named_candidate_total':None,'order_scope':'unorderable blank/redacted; preserved outside numerical order'})
    csv_output('extracts/native-unit-order.csv.gz',native_orders)
    broad_order=[x for x in native_orders if x['source_id']==BROAD]
    cum=0; native_cross=None; native15=0
    for i,x in enumerate(broad_order,1):
        before=cum;cum+=x['named_candidate_total']
        if i==15:native15=cum
        if native_cross is None and 5*cum>=4*ranking['denominator']:
            native_cross={'minimum80_count':i,'preceding_count':i-1,'preceding_votes':before,'minimum80_votes':cum,'crossing_key':x['unit_key'],'crossing_votes':x['named_candidate_total']}
    dump_json('native-ranking-2024.json',{'scope':'alternative disjoint 4567 exact broad source contexts; do not add to county totals',
        'denominator':cum,'top15_votes':native15,'top15_share_pct':percent(native15,cum),**native_cross,
        'minimum80_share_pct':percent(native_cross['minimum80_votes'],cum),
        'remainder_count':len(broad_order)-native_cross['minimum80_count'],'remainder_votes':cum-native_cross['minimum80_votes'],
        'all_unit_order':[x['unit_key'] for x in broad_order],'tie_break':'descending votes, county FIPS, worksheet, ordered source row positions'})
    dump_json('rankings.json',rankings)
    inventories=[]
    for sid in [BROAD]+[v[0] for v in SOURCES.values()]:
        us=[u for u in units if u['source_id']==sid]
        inventories.append({'source_id':sid,'unit_count':len(us),'county_count':len({u['county_fips'] for u in us}),
           'known_count_unit_count':sum(u['named_candidate_total'] is not None for u in us),
           'unknown_count_unit_count':sum(u['named_candidate_total'] is None for u in us),
           'zero_count_unit_count':sum(u['named_candidate_total']==0 for u in us),
           'county_control_vs_detail':'extracts/native-county-reconciliation.csv' if sid!=BROAD else 'all integer contexts agree candidate-by-candidate with all105 precinct-workbook county controls',
           'geometry':'historical identity only; VTD/native codes are not verified November2026 polygons'})
    dump_json('native-inventory.json',inventories)
    coverage=[]
    for rankrow in ranking['all_unit_order']:
        county=rankrow['county'];families=[]
        for sid in [BROAD]+[v[0] for v in SOURCES.values()]:
            us=[u for u in units if u['source_id']==sid and u['county']==county]
            families.append({'source_id':sid,'relationship_to_other_source_families':'overlapping alternative historical publication; do not add',
                'count_status':'some native cells unavailable' if any(u['unknown_named_cells'] for u in us) else 'reported complete integers',
                'constituents':[{'unit_key':u['unit_key'],'sheet':u['sheet'],'xml_path':u['xml_path'],'source_rows':u['source_rows'],
                  'native_label':u['native_label'],'native_id_fields':u['native_id_fields'],'named_candidate_total':u['named_candidate_total'],
                  'unknown_named_cells':u['unknown_named_cells'],'role':u['role'],'method':u['method'],
                  'geometry_status':u['geometry_status']} for u in us],
                'administrative_units':'no distinct central absentee/early/method identities published in these sheets; locality names containing Central are not classified as method boards',
                'unavailable_cases':[{'unit_key':u['unit_key'],'source_rows':u['source_rows'],'reason':'blank and/or redacted native candidate cells; see lossless row extraction and candidate observations'} for u in us if u['unknown_named_cells']]})
        coverage.append({**rankrow,'priority80':county in priority,'top15':rankrow['rank']<=15,'unit_type':'county','source_native_families':families,
             'current_2026_crosswalk_approval':'unavailable; no name/count equivalence asserted'})
    contract={'schema_version':'ks-turnout-priority-v1','state':'KS','research_date_utc':'2026-10-18',
      'status':'independent turnout extraction complete; peer reconciliation and coordinator acceptance pending',
      'coordinator_acceptance':False,'election_date':'2024-11-05','contest':'President / Vice President',
      'ranking_universe':'all four tickets reported in SOS statewide certificate and statewide files; write-ins/under/over not reported statewide in this source scope',
      'geographic_level':'all105 Kansas counties; complete source-native constituents are separate overlapping publication families',
      'denominator':ranking['denominator'],'top15_votes':ranking['top15_votes'],'top15_share_exact':ranking['top15_share_exact'],'top15_share_pct':ranking['top15_share_pct'],
      'minimum80':{k:v for k,v in ranking.items() if k not in ['all_unit_order','denominator','top15_votes','top15_share_pct','top15_share_exact']},
      'ordered_top15_keys':[r['county_key'] for r in ranking['all_unit_order'][:15]],
      'ordered_priority_keys':[r['county_key'] for r in ranking['all_unit_order'][:len(priority)]],
      'ordered_priority_names':priority,'full_all_unit_order':[r['county_key'] for r in ranking['all_unit_order']],
      'ordered_remainder_keys':[r['county_key'] for r in ranking['all_unit_order'][len(priority):]],
      'tie_break':'descending integer votes, then ascending county FIPS; no primary county ties',
      'source_hashes':{sid:sha(source_bytes(sid)) for sid in [BROAD]+[v[0] for v in SOURCES.values()]},
      'native_key_contract':'source_id + first24 hex SHA256 of compact UTF-8 JSON [source_id,sheet,county_native,native_id_fields]; fields retain exact literal values. No cross-family or cross-year join.',
      'native_unit_inventory':inventories,'candidate_observations':'extracts/candidate-observations.jsonl.gz','native_full_order':'extracts/native-unit-order.csv.gz',
      'all_geography_coverage':coverage,'ballot_registration_sensitivities':'rankings.json',
      'unavailable_statewide_fields':['generic write-ins','valid/named write-ins','undervotes','overvotes','blank ballots','candidate-by-method counts','approved November2026 native IDs/boundaries/crosswalk'],
      'alias_rules':ALIAS}
    dump_json('priority-set.json',contract)
    dump_json('administrative-controls.json',{'turnout2024_broad_footer':footer24,'turnout2022_footer':footer22,
        'registered_voters_2024_november_sum':sum(r['registered_voters'] for r in registration24.values()),
        'registered_voters_2026_october_sum':sum(r['registered_voters'] for r in registration26.values()),
        'inactive_2026_october_sum':sum(r['inactive'] for r in inactive26.values()),'active_2026_october_sum':sum(r['active'] for r in inactive26.values()),
        '2026_registration_internal_date':sorted({r['source_date'] for r in registration26.values()}),
        '2024_release':{'source':'certification-2024','ballots_cast':1344147,'registered_voters':2031132,'mail':137644,'advance_in_person':557209,'election_day':649294},
        '2024_release_minus_broad':{'ballots_cast':1344147-footer24['ballots_cast'],'registered_voters':2031132-footer24['registered_voters'],'allocation':'unresolved; no county adjustments'},
        '2020_statistics':{'source':'statistics-data','mail':459229,'advance_in_person':371854,'election_day':544042,'ballots_type_total':1375125,'provisional_ballots_cast_separate':45671,'scope':'published historical ballot-type table, not extra candidate votes'}})
    print(json.dumps({'county_rows':len(rows),'candidate_observations':len(observations),'native_units':len(units),'inventory':inventories,
                       'ranking':{k:v for k,v in ranking.items() if k!='all_unit_order'}},indent=2))

if __name__=='__main__': main()
