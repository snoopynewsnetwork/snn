"""Independent original ENR extraction; required offices only, originals complete.

XML method cells and JSON combined precinct rows remain distinct. Align choices
only after exact XML/JSON choice text/order and county totals agree. Match native
names only exactly within the same county/election; retain unmatched spellings.
"""
from extract import *
import zipfile,xml.etree.ElementTree as ET,re
def xml(sid):
    b,m=loadbody(SRC/(sid+'.meta.json'));z=zipfile.ZipFile(io.BytesIO(b));infos=[dict(name=x.filename,bytes=x.file_size,sha256=sha(z.read(x))) for x in z.infolist()]
    return ET.fromstring(z.read('detail.xml')),infos
def office(text):return re.sub(r'\s+',' ',text).strip()
def candidate(lab,text):
    aliases={'2024-pres':[(27,'Trump'),(7553,'Harris'),(8258,'Oliver'),(6882,'Stein'),(8260,'Cornel West'),(8261,'Terry'),(8259,'De La Cruz')],
             '2020-senate':[(3254,'Graham'),(3255,'Harrison'),(2268,'Bledsoe'),(6,'Write-In')],
             '2022-senate':[(3536,'Scott'),(870,'Matthews'),(6,'Write-In')],
             '2022-governor':[(3471,'McMaster'),(3473,'Cunningham'),(3472,'Reeves'),(6,'Write-In')]}
    # A retained original misspells West/Abdulla; explicit analysis alias only.
    if lab=='2024-pres' and text=='UNC Cornel Wes/ Melina Abdullat':return 8260
    out=[cid for cid,s in aliases[lab] if s.casefold() in text.casefold()];assert len(out)==1,(lab,text);return out[0]
def traverse(el,path):
    yield el,path
    for i,ch in enumerate(el):yield from traverse(ch,path+'/'+ch.tag+'['+str(i)+']')
def main():
    fips=json.loads((SRC/'county-fips-crosswalk.json').read_text())['counties'];positions=[];cells=[];native=[];controls=[];universes=[];archives=[];discrep=[];rollups=[]
    old=list(csv.DictReader(gzip.open(BASE/'candidate-method-controls.csv.gz','rt')))
    db={}
    for r in old:
        if r['division_type']=='County':db[(r['contest_label'],r['observation_scope'],r['division_name'],int(r['candidate_id']),r['method_id'])]=int(r['votes'])
    del old
    config={2024:[('2024-pres','President and Vice President')],2020:[('2020-senate','U.S. Senate')],2022:[('2022-senate','U.S. Senate'),('2022-governor','Governor and Lieutenant Governor')]}
    for year,spec in config.items():
        sr,sinfo=xml(f'legacy{year}-detailxml');archives.append(dict(source_id=f'legacy{year}-detailxml',members=sinfo))
        ct=sr.find('ElectionVoterTurnout');controls.append(dict(source_id=f'legacy{year}-detailxml',scope='state election',county='',source_pointer='/ElectionResult/ElectionVoterTurnout',source_clock=sr.findtext('Timestamp'),raw_attributes=compact(ct.attrib)))
        for i,c in enumerate(ct.find('Counties')):controls.append(dict(source_id=f'legacy{year}-detailxml',scope='county election state publication',county=c.get('name'),source_pointer=f'/ElectionResult/ElectionVoterTurnout/Counties/County[{i}]',source_clock=sr.findtext('Timestamp'),raw_attributes=compact(c.attrib)))
        statecontests={lab:next(c for c in sr.findall('Contest') if office(c.get('text'))==title) for lab,title in spec}
        for lab,title in spec:
            for idx,el in enumerate(sr):
                if el is statecontests[lab]:
                    for el,pointer in traverse(el,f'/ElectionResult/Contest[{idx}]'):positions.append(dict(source_id=f'legacy{year}-detailxml',contest_label=lab,source_pointer=pointer,tag=el.tag,raw_attributes=compact(el.attrib),text=el.text.strip() if el.text and el.text.strip() else ''))
        for county,cf in fips.items():
            sid=f'legacy{year}-county-'+county.lower()
            if json.loads((SRC/(sid+'.meta.json')).read_text())['http_status']!=200:
                assert year==2022 and county=='Clarendon'
                from clarendon import parse
                p,ce,na,co,un,ar=parse();positions.extend(p);cells.extend(ce);native.extend(na);controls.extend(co);universes.extend(un);archives.append(ar)
                discrep.append(dict(source=sid,scope='XML disabled per actual county settings; HTTP404; original enabled pinned TXT parsed independently, not zero-filled',status=404))
                continue
            root,info=xml(sid);archives.append(dict(source_id=sid,members=info));assert root.findtext('Region')==county
            clock=root.findtext('Timestamp');vt=root.find('VoterTurnout');assert vt is not None
            controls.append(dict(source_id=sid,scope='county election county publication',county=county,source_pointer='/ElectionResult/VoterTurnout',source_clock=clock,raw_attributes=compact(vt.attrib)))
            turnout={}
            for i,p in enumerate(vt.find('Precincts')):
                controls.append(dict(source_id=sid,scope='native election administrative',county=county,source_pointer=f'/ElectionResult/VoterTurnout/Precincts/Precinct[{i}]',source_clock=clock,raw_attributes=compact(p.attrib)))
                assert p.get('name') not in turnout;turnout[p.get('name')]=dict(p.attrib)
            details=json.loads(loadbody(SRC/(sid+'-details.meta.json'))[0]);summary=json.loads(loadbody(SRC/(sid+'-summary.meta.json'))[0])
            for lab,title in spec:
                found=[(i,c)for i,c in enumerate(root) if c.tag=='Contest' and office(c.get('text'))==title];assert len(found)==1,(sid,title)
                ci,c=found[0];pointer=f'/ElectionResult/Contest[{ci}]';chs=c.findall('Choice');ids=[candidate(lab,ch.get('text'))for ch in chs];assert len(set(ids))==len(ids)
                sj,ss=next((i,r)for i,r in enumerate(summary)if r['K']==c.get('key'));dj,dd=next((i,r)for i,r in enumerate(details['Contests'])if r['K']==c.get('key'))
                assert [ch.get('text')for ch in chs]==ss['CH'] and [int(ch.get('totalVotes'))for ch in chs]==ss['V'],(sid,lab)
                assert len(dd['P'])==len(dd['V']) and len(set(dd['P']))==len(dd['P'])
                for ix,ch in enumerate(chs):assert sum(v[ix] for v in dd['V'])==ss['V'][ix],(sid,lab,'combinedJSONcountyrollup',ix)
                universes.append(dict(source_id=sid,contest_label=lab,source_clock=clock,contest_pointer=pointer,contest_attributes=c.attrib,
                    source_choices=[dict(ordinal=i,raw_child_ordinal=list(c).index(ch),attributes=ch.attrib,analysis_candidate_id=ids[i])for i,ch in enumerate(chs)],summary_pointer=f'/{sj}',raw_summary=ss,details_pointer=f'/Contests/{dj}',raw_details_nonvectors={k:v for k,v in dd.items() if k not in ['P','V','T']}))
                for el,p in traverse(c,pointer):positions.append(dict(source_id=sid,contest_label=lab,source_pointer=p,tag=el.tag,raw_attributes=compact(el.attrib),text=el.text.strip() if el.text and el.text.strip() else ''))
                method_native=collections.defaultdict(dict)
                for chi,ch in enumerate(chs):
                    cid=ids[chi];cv=int(ch.get('totalVotes'));xmlsum=sum(int(v.get('votes'))for v in ch.findall('VoteType'))
                    if cv!=xmlsum:rollups.append(dict(source=sid,contest=lab,choice=ch.attrib,status='choice_vs_method_parent',choice_votes=cv,method_parent_votes=xmlsum))
                    dv=db[(lab,'combined',county,cid,'0')]
                    if dv!=cv:discrep.append(dict(source=sid,contest=lab,county=county,candidate_id=cid,scope='county combined',database=dv,legacy=cv,difference=dv-cv))
                    for vi,v in enumerate(ch.findall('VoteType')):
                        meth=v.get('name');mv=int(v.get('votes'));parts=sum(int(p.get('votes')) for p in v)
                        if mv!=parts:rollups.append(dict(source=sid,contest=lab,choice=ch.attrib,method=meth,status='method_parent_vs_native_children',parent=mv,children=parts,difference=mv-parts))
                        # Charleston's literal misspelling is retained in all output;
                        # this comparison-only alias is explicit, never a raw rename.
                        m_id={'Election Day':'1','Provisional':'2','Provionsal':'2','Early Voting':'5','Absentee By Mail':'6','Failsafe':'7','Failsafe Provisional':'8','In-Person Absentee':'9'}[meth]
                        dv=db.get((lab,'methods',county,cid,m_id))
                        if dv!=mv:discrep.append(dict(source=sid,contest=lab,county=county,candidate_id=cid,method=meth,scope='county method',database=dv,legacy=mv,difference=dv-mv if dv is not None else None))
                        for pi,p in enumerate(v):
                            name=p.get('name');pv=int(p.get('votes'));method_native[name][(cid,meth)]=pv
                            cells.append(dict(source_id=sid,contest_label=lab,county=county,county_fips=cf,source_contest_key=c.get('key'),choice_ordinal=chi,source_choice_key=ch.get('key'),source_choice_text=ch.get('text'),source_party=ch.get('party'),analysis_candidate_id=cid,method_ordinal=vi,method_name=meth,native_ordinal=pi,native_name=name,votes=pv,source_pointer=pointer+f'/Choice[{list(c).index(ch)}]/VoteType[{list(ch).index(v)}]/Precinct[{list(v).index(p)}]',raw_attributes=compact(p.attrib)))
                for pi,(name,vector) in enumerate(zip(dd['P'],dd['V'])):
                    total=sum(vector);a_id,b_id=PAIRS[lab];A=vector[ids.index(a_id)];B=vector[ids.index(b_id)];control=turnout.get(name)
                    bymethod=method_native.get(name);differences=[]
                    for cid,v in zip(ids,vector):
                        vals=[n for (cc,mm),n in (bymethod or {}).items() if cc==cid];vm=sum(vals) if vals else None
                        if vm!=v:differences.append(dict(candidate_id=cid,combined=v,methods=vm,difference=v-vm if vm is not None else None))
                    if differences:discrep.append(dict(source=sid,contest=lab,county=county,native_name=name,scope='native combined JSON vs XMLmethods exact name only',differences=differences))
                    native.append(dict(contest_label=lab,geography_key=f'SC:legacy:{lab}:{cf}:c{c.get("key")}:row{pi}',parent_key='SC:'+cf,county=county,county_fips=cf,native_division_id='',native_division_path=f'{sid}/c{c.get("key")}/P/{pi}',name=name,native_type='LegacyPrecinct',source_pointer=f'/Contests/{dj}/P/{pi}',source_id=sid+'-details',source_clock=clock,
                         candidate_votes=total,A=A,B=B,other=total-A-B,pair_votes=A+B,A_pair_share=A/(A+B) if A+B else None,A_name=chs[ids.index(a_id)].get('text'),B_name=chs[ids.index(b_id)].get('text'),
                         raw_choice_vector=compact(vector),choice_analysis_ids=compact(ids),source_total_control=(dd.get('T')or [None]*len(dd['P']))[pi],
                         raw_turnout_control=compact(control),registered_voters=int(control['totalVoters']) if control else None,ballots_control=int(control['ballotsCast']) if control else None,
                         ballots_minus_candidate_votes=int(control['ballotsCast'])-total if control else None,method_coverage='exact-name method rows reconcile' if not differences else 'original method allocation discrepancy retained',
                         identity_status='original historical source row; no DB/current/cross-year identity equivalence; ordinals scoped to source contest',raw_name=name))
    rows(BASE/'legacy-source-positions.csv.gz',positions);rows(BASE/'legacy-candidate-methods.csv.gz',cells);rows(BASE/'legacy-native-baselines.csv.gz',native);rows(BASE/'legacy-election-controls.csv.gz',controls)
    dump(BASE/'legacy-candidate-universe.json',universes);dump(BASE/'legacy-archive-members.json',archives);dump(BASE/'legacy-reconciliation.json',dict(archives=len(archives),county_archives=138,native_rows=len(native),method_cells=len(cells),source_positions=len(positions),database_vs_original_disagreements=discrep,original_method_rollup_disagreements=rollups,alias_rule='contest whitespace only; named candidate analysis links from explicit tokens; no native-name normalization'))
    rankings={};targets=[]
    from calculate import solve,unitrow
    for lab in LABELS:
        rs=[r for r in native if r['contest_label']==lab];T=sum(r['candidate_votes']for r in rs);W=[r['pair_votes']for r in rs];S=[r['A_pair_share']for r in rs]
        rankings[lab]=priority([dict(key=r['geography_key'],name=r['name'],county=r['county'],votes=r['candidate_votes'],source_id=r['source_id'],source_pointer=r['source_pointer'])for r in rs],T)
        for target in [0,.01]:
            sol=solve(W,S,target)
            for r,w,s in zip(rs,W,S):targets.append(unitrow(r,w,s,r['other'],sol,target,lab+'__legacy_native',lab,'original ENR combined JSON'))
    rows(BASE/'legacy-native-targets.csv.gz',targets);dump(BASE/'legacy-native-priority.json',rankings)
    print(compact(dict(archives=len(archives),positions=len(positions),cells=len(cells),native=len(native),disagreements=len(discrep),rollup_disagreements=len(rollups))))
if __name__=='__main__':main()
