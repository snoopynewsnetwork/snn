"""Parse actual enabled fixed-width TXT original where XML is disabled.

Every field is 30 characters, as verified by literal header alignment. Retain
entire original ZIP/TXT and exact byte offsets; do not synthesize an XML file.
"""
from extract import *
import zipfile
def parse():
    from legacy_extract import candidate
    sid='legacy2022-clarendon-pinned-detailtxt';b=loadbody(SRC/(sid+'.meta.json'))[0];z=zipfile.ZipFile(io.BytesIO(b));raw=z.read('detail.txt');lines=raw.decode().splitlines(keepends=True);offsets=[];pos=0
    for line in lines:offsets.append(pos);pos+=len(line.encode())
    positions=[];cells=[];native=[];controls=[];universes=[];discrep=[]
    fixed=lambda line:[line[i:i+30].strip() for i in range(0,len(line.rstrip('\r\n')),30)]
    start=next(i for i,l in enumerate(lines) if l.startswith('County') and 'Ballots Cast' in l)
    turnout={}
    for i in range(start+1,len(lines)):
        f=fixed(lines[i]);
        if not f or not f[0]:break
        controls.append(dict(source_id=sid,scope='native election administrative TXT' if f[0]!='Total:' else 'county election TXT',county='Clarendon',source_pointer=f'/detail.txt/line/{i+1}/byte/{offsets[i]}',source_clock='',raw_attributes=compact(dict(zip(['County','Registered Voters','Ballots Cast','Voter Turnout'],f)))))
        if f[0]=='Total:':break
        turnout[f[0]]=dict(registered=int(f[1]),ballots=int(f[2]),raw_fields=f)
    summary=json.loads(loadbody(SRC/'legacy2022-county-clarendon-summary.meta.json')[0]);details=json.loads(loadbody(SRC/'legacy2022-county-clarendon-details.meta.json')[0])
    for lab,title in [('2022-senate','U.S. Senate'),('2022-governor','Governor and Lieutenant Governor')]:
        first=next(i for i,l in enumerate(lines) if l.strip()==title+' (Vote For 1)');end=next(i for i in range(first+3,len(lines)) if lines[i].startswith('Totals:'))
        sj,ss=next((i,s)for i,s in enumerate(summary)if s['C'].strip()==title);dj,dd=next((i,d)for i,d in enumerate(details['Contests'])if d['K']==ss['K']);ids=[candidate(lab,c)for c in ss['CH']]
        header=fixed(lines[first+2]);assert header[:2]==['County','Registered Voters']
        n=len(ids);assert header[2:9]==['Election Day','Early Voting','Absentee By Mail','Failsafe','Provisional','Failsafe Provisional','Choice Total']
        for i in range(first,end+1):positions.append(dict(source_id=sid,contest_label=lab,source_pointer=f'/detail.txt/line/{i+1}/byte/{offsets[i]}',tag='fixed_width_txt_line',raw_attributes=compact(dict(byte_offset=offsets[i],raw_line=lines[i])),text=''))
        assert end-first-3==len(dd['P'])
        for pi,i in enumerate(range(first+3,end)):
            f=fixed(lines[i]);name=f[0];assert name==dd['P'][pi]
            vector=[int(f[2+7*ci+6])for ci in range(n)];assert vector==dd['V'][pi]
            total=sum(vector);assert total==int(f[2+7*n]);a_id,b_id=PAIRS[lab];A=vector[ids.index(a_id)];B=vector[ids.index(b_id)];tc=turnout.get(name)
            for ci,cid in enumerate(ids):
                assert sum(int(f[2+ci*7+mi])for mi in range(6))==vector[ci]
                for mi,meth in enumerate(header[2:8]):
                    field=2+ci*7+mi;v=int(f[field]);cells.append(dict(source_id=sid,contest_label=lab,county='Clarendon',county_fips='45027',source_contest_key=ss['K'],choice_ordinal=ci,source_choice_key=None,source_choice_text=ss['CH'][ci],source_party=ss['P'][ci],analysis_candidate_id=cid,method_ordinal=mi,method_name=meth,native_ordinal=pi,native_name=name,votes=v,source_pointer=f'/detail.txt/line/{i+1}/byte/{offsets[i]+field*30}',raw_attributes=compact(dict(raw_field=lines[i][field*30:(field+1)*30],raw_native_name=lines[i][:30]))))
            native.append(dict(contest_label=lab,geography_key=f'SC:legacy:{lab}:45027:c{ss["K"]}:row{pi}',parent_key='SC:45027',county='Clarendon',county_fips='45027',native_division_id='',native_division_path=f'legacy2022-county-clarendon/c{ss["K"]}/P/{pi}',name=name,native_type='LegacyPrecinct',source_pointer=f'/Contests/{dj}/P/{pi}',source_id='legacy2022-county-clarendon-details',source_clock='',candidate_votes=total,A=A,B=B,other=total-A-B,pair_votes=A+B,A_pair_share=A/(A+B) if A+B else None,A_name=ss['CH'][ids.index(a_id)],B_name=ss['CH'][ids.index(b_id)],raw_choice_vector=compact(vector),choice_analysis_ids=compact(ids),source_total_control=(dd.get('T')or[None]*len(dd['P']))[pi],raw_turnout_control=compact(tc),registered_voters=tc['registered'] if tc else None,ballots_control=tc['ballots'] if tc else None,ballots_minus_candidate_votes=tc['ballots']-total if tc else None,method_coverage='original TXT methods exactly reconcile with JSONcombined; XML disabled',identity_status='original historical source row; no DB/current/cross-year identity equivalence; ordinals scoped to source contest',raw_name=name))
        universes.append(dict(source_id=sid,contest_label=lab,raw_summary=ss,source_pointer=f'/detail.txt/line/{first+1}',source_choice_keys_status='not published in TXT/summary; no fabricated IDs',method_headers=header))
    return positions,cells,native,controls,universes,dict(source_id=sid,members=[dict(name='detail.txt',bytes=len(raw),sha256=sha(raw))])
