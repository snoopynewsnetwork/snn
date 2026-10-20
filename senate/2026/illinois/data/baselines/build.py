"""Independent primary county/authority/turnout extraction and reconciliation.
Original HTML sources are pinned by reference_shared.py, never peer derivatives.
"""
import collections,csv,gzip,io,json,re
from bs4 import BeautifulSoup
from source_io import ROOT,pins,raw,dump
from extract import YEARS,table,csvwrite

def main():
    allpins={x['id']:x for x in pins()};controls=json.loads((ROOT/'extract/independent-controls.json').read_text())
    names={};parents={};native={};authority=[];nativecats=[];county_candidates=[];summaries=[];coverage=[];turnouts=[]
    for year,(cs,hs,title,A,B)in YEARS.items():
        rr=list(csv.DictReader(io.StringIO(raw(cs).decode('utf-8-sig'))));cats=collections.defaultdict(collections.Counter);metadata=collections.defaultdict(list)
        for pos,r in enumerate(rr,2):
            jid=r['JurisdictionID'];names[jid]=r['JurisName'];cats[jid][r['CandidateName']]+=int(r['VoteCount']);metadata[jid].append((pos,r))
            if int(jid)>102 and r['JurisContainerID']!='0':
                if jid in parents:assert parents[jid]==r['JurisContainerID']
                parents[jid]=r['JurisContainerID']
        assert len(cats)==108
        native[year]=cats
        for jid,counts in cats.items():
            for name,v in counts.items():nativecats.append(dict(year=year,JurisdictionID=jid,candidate_or_category_literal=name,votes=v,raw_source=cs))
        # Exact actual election selector's county labels, source IDs, not fabricated FIPS.
        initial='original-turnout-county-selector-'+year+'-UA'
        ss=BeautifulSoup(raw(initial),'html.parser');opts=ss.find('select',attrs={'name':'ctl00$ContentPlaceHolder1$ddlJurisdictions'})
        opts={o['value']:o.get_text(' ',strip=True)for o in opts.find_all('option')};assert len(opts)==108
        statewide,stotal=table(hs,title);state_dict={r['candidate_literal']:r['votes']for r in statewide}
        county_sums=collections.Counter();fullcount=0
        for jid in sorted(opts,key=int):
            sid='original-turnout-authority-'+year+'-'+jid.zfill(3)
            assert sid in allpins,('missing original receipt',sid)
            soup=BeautifulSoup(raw(sid),'html.parser')
            elections=soup.find('select',attrs={'name':'ctl00$ContentPlaceHolder1$ddlElections'})
            selected=elections.find('option',selected=True)
            assert selected['value']=={'2020':'58','2022':'62','2024':'66'}[year]
            sel=soup.find('select',attrs={'name':'ctl00$ContentPlaceHolder1$ddlJurisdictions'}).find('option',selected=True)
            assert sel['value']==jid
            has_table=bool(soup.find_all('table'))
            coverage.append(dict(year=year,JurisdictionID=jid,selector_label=opts[jid],source_id=sid,has_table=has_table,empty_literal='No information was found for this election.' in soup.get_text(' ',strip=True),admitted_source=initial if jid=='1' and not has_table else sid,interpretation='county_combined' if int(jid)<=102 else 'city_selector_empty_no_inferred_zero'))
            if jid=='1' and not has_table:
                sid=initial;soup=ss
                assert soup.find('select',attrs={'name':'ctl00$ContentPlaceHolder1$ddlJurisdictions'}).find('option',selected=True)['value']=='1'
            if int(jid)>102:continue
            rows,total=table(sid,title);fullcount+=1
            for r in rows:
                county_sums[r['candidate_literal']]+=r['votes'];county_candidates.append(dict(year=year,county_key=jid,county=opts[jid],**r))
            observed={r['candidate_literal']:r['votes']for r in rows}
            members=[j for j in cats if j==jid or parents.get(j)==jid]
            expected=collections.Counter()
            for j in members:expected.update(cats[j])
            common=[r['candidate_literal']for r in statewide if r['candidate_literal']in controls[year]['candidate_categories']]
            for name in common:assert observed.get(name)==expected[name],(year,jid,name,observed.get(name),expected[name])
            assert A in observed and B in observed
            pair=observed[A]+observed[B];printed=sum(expected[name]for name in common);generic=sum(v for name,v in expected.items()if name.lower()=='write-in')
            summaries.append(dict(year=year,county_key=jid,county=opts[jid],contest=title,A_name=A,A_party='DEMOCRATIC',B_name=B,B_party='REPUBLICAN',A=observed[A],B=observed[B],pair_votes=pair,other_named=total-pair,all_named_votes=total,native_printed_votes=printed,native_generic_marks=generic,native_raw_mark_universe=printed+generic,named_minus_native_printed=total-printed,generic_minus_additional_named=generic-(total-printed),A_pair_share=observed[A]/pair,A_pair_margin=(observed[A]-observed[B])/pair,A_all_share=observed[A]/total,A_all_margin=(observed[A]-observed[B])/total,pair_participation=pair/total,authority_members=json.dumps(sorted(members,key=int)),county_source_id=sid,county_source_status='Official historical results webpage; certification not asserted solely from page',FIPS=''))
            summaries[-1].update(historical_pair_winner=A if observed[A]>observed[B]else B if observed[B]>observed[A]else'tie',pair_margin_band='within5pp'if abs(observed[A]-observed[B])/pair<=.05 else'5to10pp'if abs(observed[A]-observed[B])/pair<=.10 else'over10pp',source_plurality_winner=max(observed,key=observed.get))
            gp=any(k.lower()=='write-in'for k in expected)
            summaries[-1].update(native_generic_recorded_sum=generic,native_generic_source_present=gp,native_generic_observed=generic if gp else None)
        assert dict(county_sums)==state_dict,('literal county/state candidate mismatch',year,dict(county_sums),state_dict)
        assert fullcount==102
        # Whole-county ballots and historical source-labeled Total Voters, not native row registration sums.
        ts='original-turnout-turnout-'+year;soup=BeautifulSoup(raw(ts),'html.parser');t=soup.find('table',id='ContentPlaceHolder1_gvTurnout');assert t
        output=[]
        for n,tr in enumerate(t.find_all('tr'),1):
            f=[x.get_text(' ',strip=True)for x in tr.find_all(['th','td'],recursive=False)]
            if not f or f[0]=='Jurisdiction Name':continue
            assert len(f)==4
            r=dict(year=year,jurisdiction_literal=f[0],total_voters_literal=f[1],ballots_literal=f[2],percent_literal=f[3],total_voters=int(f[1].replace(',','')),ballots=int(f[2].replace(',','')),source_id=ts,table_id=t['id'],table_row=n)
            output.append(r)
        assert len(output)==103
        state=output[-1];assert state['jurisdiction_literal']=='All Jurisdictions'
        assert sum(r['ballots']for r in output[:-1])==state['ballots']and sum(r['total_voters']for r in output[:-1])==state['total_voters']
        for r in output[:-1]:
            ids=[j for j,v in opts.items()if v==r['jurisdiction_literal']];assert len(ids)==1 and int(ids[0])<=102
            r['county_key']=ids[0]
        turnouts.extend(output)
        controls[year].update(county_HTML_rows=fullcount,county_state_all_literal_candidates_exact=True,state_ballots=state['ballots'],state_total_voters_source_label=state['total_voters'],ballots_minus_all_named_contest=state['ballots']-stotal)
    # FIPS reference is independently downloaded Census code list, not sourceID arithmetic.
    census=list(csv.DictReader(io.StringIO(raw('census-county-codes').decode()),delimiter='|'))
    census=[r for r in census if r['STATE']=='IL'];assert len(census)==102
    def normal(name):return re.sub('[^a-z0-9]','',name.lower().removesuffix(' county'))
    cm={normal(r['COUNTYNAME']):r for r in census};assert len(cm)==102
    crosswalk=[];fips={}
    for jid,name in names.items():
        if int(jid)>102:continue
        c=cm[normal(name)];fips[jid]=c['STATEFP']+c['COUNTYFP']
        crosswalk.append(dict(county_source_ID=jid,ISBE_literal=name,Census_literal=c['COUNTYNAME'],FIPS=fips[jid],COUNTYNS=c['COUNTYNS'],source_id='census-county-codes',match_rule='Case, spacing and punctuation only; trailing County removed; unique102-to102 match, no precinct boundary inference'))
    assert len(set(fips.values()))==102
    csvwrite(ROOT/'county-code-crosswalk.csv',crosswalk)
    # Historic authority inventory includes city parent evidence across all three files.
    for jid in sorted(names,key=int):
        authority.append(dict(JurisdictionID=jid,authority_name_native=names[jid],authority_type='county_ex_city_if_child' if int(jid)<=102 else 'city_election_authority',historical_parent_county=parents.get(jid,jid),parent_FIPS=fips[parents.get(jid,jid)],parent_evidence='Literal nonzero JurisContainerID in original 2020/2022/2024 CSV; each printed candidate reconciled to combined county HTML',source_years='2020|2022|2024',native_current_compatibility='Unverified; matching historical/current name or ID alone is insufficient'))
    for row in summaries:
        row['FIPS']=fips[row['county_key']]
        t=next(t for t in turnouts if t['year']==row['year']and t.get('county_key')==row['county_key']);row.update(ballots_cast=t['ballots'],historical_Total_Voters=t['total_voters'],ballots_minus_contest=t['ballots']-row['all_named_votes'],ballot_contest_participation=row['all_named_votes']/t['ballots'],turnout_source=t['source_id'])
    csvwrite(ROOT.parent/'county-baselines.csv',summaries)
    csvwrite(ROOT/'extract/county-candidate-source-rows.csv',county_candidates)
    csvwrite(ROOT/'extract/authority-candidate-category-totals.csv',nativecats)
    csvwrite(ROOT/'authority-inventory.csv',authority)
    csvwrite(ROOT/'extract/selector-coverage.csv',coverage)
    csvwrite(ROOT/'extract/historical-turnout-source-rows.csv',turnouts,sorted(set().union(*(r.keys()for r in turnouts))))
    dump(ROOT/'extract/reconciled-controls.json',controls)
    # Source-backed candidate metadata preserves blank parties and write-in status.
    details=[]
    for r in csv.DictReader((ROOT/'extract/statewide-source-rows.csv').open()):
        sid=f'detail-{r["year"]}-{r["table_row"]}-public-retry';s=BeautifulSoup(raw(sid),'html.parser')
        fields={}
        for el in s.select('[id]'):
            eid=el['id']
            if eid.startswith('ContentPlaceHolder1_') and el.name in ['span','a','input']:
                val=el.get('value')if el.name=='input'else el.get_text(' ',strip=True)
                fields[eid]=val
        details.append({**r,'detail_source_id':sid,'complete_source_label_fields':fields,'detail_text':s.get_text(' ',strip=True)})
    dump(ROOT/'extract/historical-candidate-metadata.json',details)
    reg=list(csv.DictReader(io.StringIO(raw('original-turnout-registration-current-csv').decode('utf-8-sig'))))
    assert len(reg)==109 and reg[-1]['Name']=='Totals'
    assert sum(int(r['A'])for r in reg[:-1])==int(reg[-1]['A']) and sum(int(r['I'])for r in reg[:-1])==int(reg[-1]['I'])
    assert {r['JID']for r in reg[:-1]}==set(names)
    csvwrite(ROOT/'extract/current-registration-source-rows.csv',reg)
    regpage=BeautifulSoup(raw('original-turnout-registration-counts'),'html.parser').get_text(' ',strip=True)
    clock=re.search(r'Files were last updated:\s*(\d+/\d+/\d+\s+\d+:\d+\s*[AP]M)',regpage);assert clock
    dump(ROOT/'extract/current-registration-controls.json',dict(authority_rows=108,literal_A=int(reg[-1]['A']),literal_I=int(reg[-1]['I']),source_id='original-turnout-registration-current-csv',source_clock_page='original-turnout-registration-counts',clock_literal=clock[1],time_zone='not supplied in displayed clock',status='Unofficial numbers provided by jurisdictions; parent explicitly says fluctuate daily',code_definition='CSV literal A/I preserved. Parent download page does not define codes; no sum is substituted for historical Total Voters.',boundary_compatibility='not established by matching108IDs'))
    print(json.dumps({'county_rows':len(summaries),'authority_rows':len(authority),'literal_county_candidate_rows':len(county_candidates),'all_state_candidate_balances':'exact_three_years'},indent=2))
if __name__=='__main__':main()
