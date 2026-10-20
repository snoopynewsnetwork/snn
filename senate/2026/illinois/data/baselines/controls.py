"""Independent federal comparison, source denominator and sparse registration audits."""
import collections,csv,gzip,io,json,re,subprocess
from source_io import ROOT,raw,dump
from extract import csvwrite,YEARS
def main():
    for sid in ['isbe-2026-authority-guide','isbe-2026-calendar','original-fec-2024-president-pdf','fec-2020-book','fec-2022-book']:
        text=subprocess.run(['pdftotext','-layout','-','-'],input=raw(sid),capture_output=True,check=True).stdout
        (ROOT/f'extract/{sid}.txt.gz').write_bytes(gzip.compress(text,mtime=0))
    allstate=list(csv.DictReader((ROOT/'extract/statewide-source-rows.csv').open()));federal=[]
    maps={'2020':{'RICHARD J. DURBIN':'Durbin, Richard J.','MARK C. CURRAN JR.':'Curran, Mark C., Jr.','WILLIE L. WILSON':'Wilson, Willie L.','DANNY MALOUF':'Malouf, Danny','DAVID F. BLACK':'Black, David F.','KEVIN KEELY':'Keely, Kevin','LOWELL MARTIN SEIDA':'Seida, Lowell Martin','ALBERT A. SCHAAL':'Schaal, Albert A.'},'2022':{'TAMMY DUCKWORTH':'Duckworth, Tammy','KATHY SALVI':'Salvi, Kathy','BILL REDPATH':'Redpath, Bill','LOWELL MARTIN SEIDA':'Seida, Lowell Martin',"CONSTANT 'CONNOR' VLAKANCIC":"Vlakancic, Constant 'Connor'"}}
    for y in ['2020','2022']:
        sid=f'fec-{y}-book';s=gzip.decompress((ROOT/f'extract/{sid}.txt.gz').read_bytes()).decode();pages=s.split('\f');title='Durbin, Richard J.'if y=='2020'else'Duckworth, Tammy'
        match=[(i,p)for i,p in enumerate(pages,1)if title in p and ('3,278,930'if y=='2020'else'2,329,136')in p];assert len(match)==1
        page,text=match[0];start=text.index('ILLINOIS');part=text[start:]
        for r in [r for r in allstate if r['year']==y]:
            name=maps[y][r['candidate_literal']];line=next(l for l in part.splitlines()if name in l)
            # Last number before the final percentage is the general-election total.
            vals=re.findall(r'([\d,]+)\s+[\d.]+%',line);assert vals
            votes=int(vals[-1].replace(',',''));assert votes==int(r['votes'])
            federal.append(dict(year=y,ISBE_candidate=r['candidate_literal'],FEC_candidate=name,ISBE_votes=int(r['votes']),FEC_votes=votes,difference=0,FEC_PDF_page=page,FEC_printed_page='74'if y=='2020'else'23',FEC_source_id=sid,FEC_line_literal=line,comparison='Explicit display-name mapping for comparison only; no candidate records merged'))
    # FEC presidential pages retain row+column presentation. All27source labels remain separate.
    s=gzip.decompress((ROOT/'extract/original-fec-2024-president-pdf.txt.gz').read_bytes()).decode();pages=s.split('\f');p24=[]
    for page in range(2,7):
        line=next(l for l in pages[page-1].splitlines()if l.startswith('IL '));nums=[int(x.replace(',',''))for x in re.findall(r'\d[\d,]*',line)]
        p24.append(dict(page=page,Illinois_row_literal=line,numbers_left_to_right=nums))
    expected={2:[42,2877],3:[3062863,80426],4:[12,3510,1391,31023],5:[2449079],6:[1569,518,5633310]}
    assert all(r['numbers_left_to_right']==expected[r['page']]for r in p24)
    shared={'Kamala D. Harris','Donald J. Trump','Robert F. Kennedy Jr.'};seven={'Shiva Ayyadurai','Claudia De La Cruz','Joseph Kishore','Chase Oliver','Peter Sonski','Jill Stein','Cornel West'}
    sr=[r for r in allstate if r['year']=='2024'];assert sum(int(r['votes'])for r in sr if r['candidate_literal']in seven)==40424
    scattered=[r for r in sr if r['candidate_literal']not in shared|seven];assert len(scattered)==17 and sum(int(r['votes'])for r in scattered)==518
    dump(ROOT/'extract/federal-controls.json',dict(Senate_candidate_comparisons=federal,president_2024_FEC_rows=p24,printed_three_total=5592368,seven_additional_named_total=40424,seventeen_other_ISBE_source_rows_total=518,seventeen_other_ISBE_source_rows=scattered,all_ISBE_27_source_rows_total=5633310,qualification='FEC compiles state-provided votes: separate federal publication, not independent underlying votes or new certification. Matching aggregate518 does not merge apparent running mates/aliases into legal tickets.'))
    controls=[];regrows=[]
    county=list(csv.DictReader((ROOT.parent/'county-baselines.csv').open()))
    for y,(cs,*_)in YEARS.items():
        rr=list(csv.DictReader(io.StringIO(raw(cs).decode('utf-8-sig'))));cats=collections.defaultdict(collections.Counter);parents={r['JurisdictionID']:r['historical_parent_county']for r in csv.DictReader((ROOT/'authority-inventory.csv').open())};units=collections.defaultdict(list)
        for pos,r in enumerate(rr,2):cats[parents[r['JurisdictionID']]][r['CandidateName']]+=int(r['VoteCount']);units[r['JurisdictionID'],r['PrecinctName']].append((pos,r))
        for r in [r for r in county if r['year']==y]:
            c=cats[r['county_key']];nonvotes=[c.get(k)for k in ['Under Votes','Over Votes','Blank Ballots']];recorded=sum(c.values());b=int(r['ballots_cast'])
            controls.append(dict(year=y,county_key=r['county_key'],county=r['county'],ballots=b,all_named_contest=int(r['all_named_votes']),ballots_minus_named=b-int(r['all_named_votes']),under_votes_record_sum=c.get('Under Votes'),over_votes_record_sum=c.get('Over Votes'),blank_ballots_record_sum=c.get('Blank Ballots'),all_native_category_record_sum=recorded,ballots_minus_all_native_records=b-recorded,qualification='Absent categories null. Record sum is not an asserted exhaustive or nonoverlapping ballot partition. Generic marks never added to legally named votes.'))
        for (jid,name),rows in units.items():
            vals=list(dict.fromkeys(r['Registration']for _,r in rows));regrows.append(dict(year=y,JurisdictionID=jid,PrecinctName=name,registration_literals=json.dumps(vals),distinct_literal_count=len(vals),source_positions=json.dumps([p for p,_ in rows]),definition='Source Registration repeated per candidate/category; no voting-eligible denominator or crossyear/current compatibility inferred'))
    csvwrite(ROOT/'extract/denominator-source-reconciliation.csv',controls)
    csvwrite(ROOT/'extract/native-registration-observations.csv.gz',regrows)
    print(json.dumps({'federal_Senate_named_comparisons':len(federal),'federal2024_IL_rows':5,'denominator_county_rows':len(controls),'registration_native_observations':len(regrows)}))
if __name__=='__main__':main()
