"""Original-first independent ISBE CSV/HTML extraction. Requires beautifulsoup4."""
import collections,csv,gzip,io,json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from source_io import ROOT,raw,pins,dump,sha

YEARS={
 '2020':('sos-observed-2020-senate-native-csv','sos-observed-2020-federal-statewide-page','UNITED STATES SENATOR','RICHARD J. DURBIN','MARK C. CURRAN JR.'),
 '2022':('sos-observed-2022-senate-native-csv','sos-observed-2022-federal-statewide-page','UNITED STATES SENATOR','TAMMY DUCKWORTH','KATHY SALVI'),
 '2024':('sos-2024-president-csv','sos-observed-2024-federal-statewide-page','PRESIDENT AND VICE PRESIDENT','Kamala D. Harris','Donald J. Trump')}
FIELDS=['JurisdictionID','JurisContainerID','JurisName','EISCandidateID','CandidateName','EISContestID','ContestName','PrecinctName','Registration','EISPartyID','PartyName','VoteCount']
def csvwrite(path,rows,fields=None):
    rows=list(rows); fields=fields or list(rows[0])
    path.parent.mkdir(parents=True,exist_ok=True)
    stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=fields);w.writeheader();w.writerows(rows)
    b=stream.getvalue().encode()
    path.write_bytes(gzip.compress(b,mtime=0) if path.suffix=='.gz' else b)
def table(sid,contest):
    soup=BeautifulSoup(raw(sid),'html.parser')
    label=soup.find(string=lambda s:s and s.strip()==contest); assert label is not None
    t=label.find_parent('div').find_next('table');out=[];total=None
    source=next(x for x in pins() if x['id']==sid)
    for pos,tr in enumerate(t.find_all('tr'),1):
        cells=tr.find_all(['td','th'],recursive=False)
        f=[c.get_text(' ',strip=True)for c in cells]
        if not f or f[0]=='Candidate':continue
        assert len(f)==4, f
        if f[0]=='Vote Totals':total=int(f[2].replace(',',''));continue
        link=cells[0].find('a',href=True)
        out.append(dict(source_id=sid,table_id=t.get('id'),table_row=pos,candidate_literal=f[0],party_literal=f[1],votes=int(f[2].replace(',','')),votes_literal=f[2],percentage_literal=f[3],href_literal=link['href'] if link else '',detail_url=urljoin(source['final_url'],link['href']) if link else ''))
    assert total==sum(r['votes']for r in out)
    return out,total
def main():
    summary={};candidate_rows=[]
    for year,(cs,hs,title,A,B) in YEARS.items():
        b=raw(cs); reader=csv.DictReader(io.StringIO(b.decode('utf-8-sig')))
        assert reader.fieldnames==FIELDS
        rr=list(reader);cats=collections.Counter();contexts=collections.defaultdict(list);groups=collections.defaultdict(list); authorities=collections.defaultdict(list);naive=collections.Counter()
        for pos,r in enumerate(rr,2):
            assert len(r)==12 and r['ContestName']==title and int(r['VoteCount'])>=0
            row={'year':year,'source_id':cs,'csv_record_1based_including_header':pos,**r}
            cats[r['CandidateName']]+=int(r['VoteCount'])
            contexts[tuple(r[k]for k in ('JurisdictionID','JurisContainerID','JurisName','PrecinctName'))].append(row)
            groups[(r['JurisdictionID'],r['PrecinctName'])].append(row)
            authorities[(r['JurisdictionID'],r['JurisContainerID'],r['JurisName'])].append(row)
            naive[r['JurisdictionID'],r['PrecinctName'],r['EISCandidateID']]+=1
        # Exact raw fields and order retained, with explicit source-record position.
        csvwrite(ROOT/f'extract/{year}-raw-rows.csv.gz',({'year':year,'source_id':cs,'csv_record_1based_including_header':p,**r}for p,r in enumerate(rr,2)))
        printed,total=table(hs,title)
        common=[r for r in printed if r['candidate_literal']in cats]
        assert all(cats[r['candidate_literal']]==r['votes']for r in common)
        for r in printed: candidate_rows.append({'year':year,**r,'native_literal_match':r['candidate_literal']in cats})
        out=[]
        for n,(key,rows) in enumerate(contexts.items(),1):
            out.append({'year':year,'presentation_id':f'{year}:context:{n}','JurisdictionID':key[0],'JurisContainerID':key[1],'JurisName':key[2],'PrecinctName':key[3],'source_positions':[r['csv_record_1based_including_header']for r in rows],'registration_literals':list(dict.fromkeys(r['Registration']for r in rows)),'candidate_category_rows':[{k:r[k]for k in ('EISCandidateID','CandidateName','EISPartyID','PartyName','VoteCount')}for r in rows]})
        bb=(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n').encode();(ROOT/f'extract/{year}-contexts.json.gz').write_bytes(gzip.compress(bb,mtime=0))
        # Projection is an arithmetic context only. It does not declare physical geography.
        gr=[]
        for n,((jid,precinct),rows) in enumerate(groups.items(),1):
            cand=collections.defaultdict(list)
            for r in rows: cand[r['CandidateName']].append(r)
            def val(name):
                x=cand.get(name,[])
                assert len(x)<=1,(year,jid,precinct,name)
                return int(x[0]['VoteCount']) if x else None
            gr.append({'year':year,'unit_key':json.dumps([year,jid,precinct],ensure_ascii=False,separators=(',',':')),'JurisdictionID':jid,'PrecinctName':precinct,'A_name':A,'B_name':B,'A':val(A),'B':val(B),'printed_other_observed':sum(int(r['VoteCount'])for r in rows if r['CandidateName'] in {a['candidate_literal']for a in common}-{A,B}), 'printed_other_missing_candidates':[a['candidate_literal']for a in common if a['candidate_literal']not in cand], 'registration_literals':list(dict.fromkeys(r['Registration']for r in rows)), 'source_positions':[r['csv_record_1based_including_header']for r in rows], 'presentation_contexts':[list(k)for k in dict.fromkeys((r['JurisContainerID'],r['JurisName'])for r in rows)],'literal_category_record_sums':{name:sum(int(r['VoteCount'])for r in cr)for name,cr in cand.items()}, 'generic_writein_marks':sum(int(r['VoteCount'])for r in rows if r['CandidateName'].lower()=='write-in') if any(r['CandidateName'].lower()=='write-in'for r in rows) else None, 'generic_writein_recorded_sum':sum(int(r['VoteCount'])for r in rows if r['CandidateName'].lower()=='write-in'), 'generic_writein_source_present':any(r['CandidateName'].lower()=='write-in'for r in rows),'under_votes_observed':sum(int(r['VoteCount'])for r in rows if r['CandidateName']=='Under Votes') if 'Under Votes' in cand else None,'over_votes_observed':sum(int(r['VoteCount'])for r in rows if r['CandidateName']=='Over Votes') if 'Over Votes' in cand else None,'blank_ballots_observed':sum(int(r['VoteCount'])for r in rows if r['CandidateName']=='Blank Ballots') if 'Blank Ballots' in cand else None,'method':'unavailable_no_source_column','cross_year_current_compatibility':'unverified'})
        dump(ROOT/f'extract/{year}-units.json',gr)
        csvwrite(ROOT/f'extract/{year}-authority-contexts.csv',[dict(year=year,JurisdictionID=k[0],JurisContainerID=k[1],JurisName=k[2],source_rows=len(v),precinct_literals=len(set(r['PrecinctName']for r in v)),candidate_categories=json.dumps(dict(collections.Counter({name:sum(int(r['VoteCount'])for r in v if r['CandidateName']==name)for name in dict.fromkeys(r['CandidateName']for r in v)})),ensure_ascii=False))for k,v in authorities.items()])
        summary[year]={'source_id':cs,'source_raw_sha256':sha(b),'raw_rows':len(rr),'fields':len(rr)*12,'authorities':len({k[0]for k in authorities}),'authority_presentations':len(authorities),'native_presentations':len(contexts),'arithmetic_authority_precinct_contexts':len(groups),'pair_complete_contexts':sum(r['A']is not None and r['B']is not None for r in gr),'candidate_categories':dict(cats),'statewide_HTML_total':total,'statewide_HTML_rows':len(printed),'native_named_common_total':sum(r['votes']for r in common),'statewide_only_named_total':sum(r['votes']for r in printed if r['candidate_literal']not in cats),'generic_marks_separate':sum(v for k,v in cats.items()if k.lower()=='write-in'),'naive_ID_duplicate_excess':sum(n-1 for n in naive.values()),'method_column_present':False,'A':A,'B':B}
    dump(ROOT/'extract/independent-controls.json',summary)
    csvwrite(ROOT/'extract/statewide-source-rows.csv',candidate_rows)
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
