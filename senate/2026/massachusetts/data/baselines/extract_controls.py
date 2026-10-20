#!/usr/bin/env python3
"""Own extraction from explicitly qualified research-browser source representations."""
import collections,gzip,json,re
from extract_originals import ROOT,TAGS,dump,write_csv
def lines_for(fragment):
    out={}
    for p in sorted((ROOT/'source').glob('browser*.json')):
        for part in json.loads(p.read_text())['result'].split('--------------------------------------------------------------------------------'):
            if fragment not in part.lstrip().split('\n')[0]:continue
            for match in re.finditer(r'^L(\d+)(?:@[^:]+)?: (.*)',part,re.M):
                i=int(match[1]);s=match[2]
                if i in out:assert out[i]==s,(fragment,i)
                out[i]=s
    return out
def main():
    reg=lines_for('accessible-table/enrollment-breakdown-2024.htm)');assert all(i in reg for i in range(112,553))
    county=None;first=False;municipal=[];parents=[]
    for i,s in sorted(reg.items()):
        if s.startswith('## ') and ':' in s and i>=132:county=s[3:].split(':')[0];first=True
        cells=[c.strip() for c in s.split('|')]
        if i<132 or i>551 or len(cells)!=6 or not re.fullmatch(r'[\d,]+',cells[1]):continue
        vals=[int(c.replace(',','')) for c in cells[1:]]
        o=dict(source_URL='https://www.sec.state.ma.us/divisions/elections/research-and-statistics/accessible-table/enrollment-breakdown-2024.htm',source_line=i,raw_line=s,county_section_literal=county,municipal_label_literal=cells[0],registered_voters=vals[0],Democrat=vals[1],Republican=vals[2],Libertarian=vals[3],Unenrolled=vals[4],as_of='2024-10-26',active_inactive_split='not separately supplied in this table',representation='research-browser line text; original HTTP entity blocked403')
        if first:parents.append(o);first=False
        else:municipal.append(o)
    assert len(parents)==14 and len(municipal)==347 and len({(m['county_section_literal'],m['municipal_label_literal']) for m in municipal})==347
    registration_disagreements=[]
    for parent in parents:
        rows=[r for r in municipal if r['county_section_literal']==parent['county_section_literal']]
        registration_disagreements.append(dict(county=parent['county_section_literal'],municipal_rows=len(rows),sum_minus_county={col:sum(r[col] for r in rows)-parent[col] for col in ['registered_voters','Democrat','Republican','Libertarian','Unenrolled']}))
    sums={c:sum(r[c] for r in municipal) for c in ['registered_voters','Democrat','Republican','Libertarian','Unenrolled']}
    assert {c:sum(r[c] for r in parents) for c in sums}==dict(registered_voters=5142343,Democrat=1352937,Republican=434887,Libertarian=16467,Unenrolled=3302493)
    write_csv(ROOT/'registration2024-municipal-browser.csv',municipal)
    turnout=lines_for('voter-turnout-statistics.htm)');tr={}
    for i,s in turnout.items():
        cs=[c.strip() for c in s.split('|')]
        if len(cs)==4 and cs[0] in ['2020','2022','2024'] and i<157:tr[cs[0]]=dict(registered_voters=int(cs[1].replace(',','')),TotalVotesCast=int(cs[2].replace(',','')),turnout_percent_printed=cs[3],raw_line=s,source_line=i)
    assert set(tr)=={'2020','2022','2024'}
    method=lines_for('early-voting-statistics.htm)');ms={}
    for i,s in sorted(method.items()):
        m=re.fullmatch(r'November \d+, (2020|2022|2024) State Election',s)
        if not m:continue
        tail=[(n,t) for n,t in sorted(method.items()) if n>i and n<i+10]
        x={'source_line':i,'raw_lines':tail}
        for n,t in tail:
            if t.startswith('Total Ballots Cast'):x['TotalBallotsCast']=int(t.split('–')[1].strip().replace(',',''))
            if t.startswith('Mail –'):x['mail_percent_printed']=t.split('–')[1].strip()
            if t.startswith('Early –'):x['early_percent_printed']=t.split('–')[1].strip()
            if t.startswith('Election Day –'):x['ElectionDay_percent_printed']=t.split('–')[1].strip()
        ms[m[1]]=x
    assert set(ms)=={'2020','2022','2024'}
    for year,x in ms.items():assert 'TotalBallotsCast' in x
    controls=json.loads((ROOT/'controls.json').read_text());disagreements={}
    for tag,c in controls.items():
        year=tag[:4];disagreements[tag]=dict(PD43_TotalVotesCast=c['total_votes_cast'],turnout_page_TotalVotesCast=tr[year]['TotalVotesCast'],method_page_TotalBallotsCast=ms[year]['TotalBallotsCast'],PD43_minus_turnout=c['total_votes_cast']-tr[year]['TotalVotesCast'],PD43_minus_method=c['total_votes_cast']-ms[year]['TotalBallotsCast'])
    # Separate source-print metadata; no party normalization or numeric old-ID mapping.
    candidate_lines=lines_for('2026-state-election-candidates.htm)')
    cand=[dict(source_line=i,raw_line=s,name=s.split(',')[0],ballot_label=s.rsplit(',',1)[-1].strip()) for i,s in sorted(candidate_lines.items()) if 171<i<180 and s.strip()]
    assert len(cand)==4
    dump(ROOT/'source/current-candidates.json',dict(source_url='https://www.sec.state.ma.us/divisions/elections/research-and-statistics/2026-state-election-candidates.htm',office='Senator in Congress',stage='2026 State Election general list, not primary nominees',candidates=cand,source_release_clock=None,official_ballot_candidate_numeric_IDs=None,qualified_writein_list=None,ballot_facsimile_order_approval=False,qualification='Official current general-election publication observed with research browser; direct original entity403. Literal four printed candidates only, no assumption of complete valid write-in field or current numeric feed IDs.'))
    dump(ROOT/'statistics-controls.json',dict(representation='Independent research-browser extraction, NOT original HTTP entities; complete direct403 bodies and DNS failures retained separately',registration2024_municipal_coverage=347,registration2024_county_controls=parents,registration2024_municipal_sums=sums,registration2024_county_minus_municipal_disagreements=registration_disagreements,registration2024_missing_labels=['SUDBURY','NORTHBOROUGH','NORTHBRIDGE','OAKHAM'],registration2024_top_table_political_designations=35559,registration2024_asof='2024-10-26',turnout_page_state_elections=tr,method_page_state_elections=ms,source_disagreements=disagreements,registration_statewide_asof={'2020':dict(date='2020-10-24',registered=4812909),'2022':dict(date='2022-10-29',registered=4884076),'2024':dict(date='2024-10-26',registered=5142343)},native_registration_allocation=None,municipal_method_original_coverage=0,registration2020_2022_municipal_original_coverage=0,qualification='2024 accessible page prints347 municipal rows; Sudbury, Northborough, Northbridge and Oakham absent in observed representation. Complete source line112..552 coverage verified. County/state controls retained separately; municipal shortfalls NOT allocated to missing towns. Literal labels including source abbreviations/punctuation remain separate, no normalized join. State controls/date labels independently observed on official PDF browser representations and turnout/enrollment pages. Active/inactive breakdown not established. No registration/turnout-to-native join. No source rescaling, cause or chronology inferred for differences. Methods rounded percentages are not exact candidate totals; no method preference anchor inferred.'))
    hierarchy={}
    for tag in TAGS:
        c=json.loads(gzip.decompress((ROOT/'extract'/f'{tag}-original-extraction.json.gz').read_bytes()));parents=[]
        for p in c['objects']['municipal']:
            kids=[u for u in c['objects']['precinct'] if u['city_town']==p['city_town']];wards=collections.defaultdict(list)
            for u in kids:wards[u['ward']].append(u['key'])
            parents.append(dict(municipal_key=p['key'],city_town=p['city_town'],source_record_ordinal=p['record_ordinal'],native_keys=[u['key'] for u in kids],ward_groups=[dict(ward_literal=w,native_keys=ks,source_ward_total_row=False) for w,ks in wards.items()],source_empty_ward_pct_keys=[u['key'] for u in kids if u['ward']==u['pct']==''],separate_central_administrative_rows='not separately labeled in selected exports',numeric_unit_id=None))
        hierarchy[tag]=dict(parents=parents,native_count=c['controls']['native_count'],overlap_rule='Municipal parents overlap native children. Ward groups are descriptive, not additive observations. Only native rows summed per contest; no crossyear native equality.',current2026_approved=False)
    dump(ROOT/'native-hierarchy.json',hierarchy)
    print('2024registration347 printed municipal rows/14 county controls; shortfalls retained; hierarchy all contests')
if __name__=='__main__':main()
