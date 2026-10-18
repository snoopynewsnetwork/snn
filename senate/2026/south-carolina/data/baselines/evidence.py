"""Document primary vectors, current ballot evidence and original route audit."""
from extract import *
import re,html
def main():
    pinned=BASE/'shared-reference-evidence.json'
    news=[r['metadata']for r in json.loads(pinned.read_text())]if pinned.exists()else json.loads((DATA/'news/manifest.json').read_text());refs=[];scripts={}
    for m in news:
        if 'asset' not in m:
            refs.append(dict(metadata=m,reuse='shared retrieval failure/metadata only, no original bytes claimed'));continue
        p=DATA/'news'/m['asset'];s=p.read_bytes();raw=gzip.decompress(s);assert sha(s)==m['stored_sha256'] and sha(raw)==m['raw_sha256']
        refs.append(dict(metadata=m,body_path=os.path.relpath(p,BASE),stored_bytes=len(s),reuse='complete shared original read-only; includes cross-state newsroom scope, no SC vote filter applied to original'))
        scripts[m['id']]=raw.decode(errors='replace')
    q=next(q for q in re.findall(r'\.gql`(.*?)`',scripts['sos-history-contest-script-27'],re.S)if 'query GetContestGranular('in q)
    frags=[q for q in re.findall(r'\.gql`(.*?)`',scripts['sos-history-contest-script-23'],re.S)if any(('fragment '+n+' ')in q for n in ['CoreContest','CandidateContestWithParties','granularDivision'])]
    q=re.sub(r'\$\{[^}]+\}','',q+'\n'+'\n'.join(frags));audits=[]
    for lab in LABELS:
        for mode in ['combined','methods']:
            r=json.loads((SRC/(lab+'-'+mode+'.request.json')).read_text());assert r['query']==q and r['operationName']=='GetContestGranular'
            audits.append(dict(source_id=lab+'-'+mode,query_identical_to_independently_reextracted_original_JS=True,contest_id=r['variables']['contestId'],splitParty=r['variables']['splitParty']))
    dump(BASE/'shared-reference-evidence.json',refs);dump(BASE/'source-chain-audit.json',audits)
    universe=json.loads((BASE/'candidate-universe.json').read_text());states=[];primary={}
    for lab,u in universe.items():
        real=[c for c in u['combined_metadata']['candidates']if c['candidate']['pseudocandidate']in[None,'ALL_OTHER_CANDIDATES']];total=sum(c['nVotes']for c in real)
        for c in real:states.append(dict(contest_label=lab,event_date=u['contest']['event']['startDate'],candidate_id=c['candidateId'],party_id=c['partyId'],display_name=c['displayName'],party=next((p['name']for p in u['combined_metadata']['parties']if int(p['id'])==c['partyId']),''),pseudocandidate=c['candidate']['pseudocandidate'],votes=c['nVotes'],contest_denominator=total,all_candidate_share=c['nVotes']/total))
        primary[lab]=dict(database_total=total,complete_candidates=[dict(candidate_id=c['candidateId'],name=c['displayName'],votes=c['nVotes'],pseudocandidate=c['candidate']['pseudocandidate'])for c in real])
    primary['publication_disagreements']=[
        dict(source='NARA signed December9,2024 SCcertificate, both pages',scope='seven presidential slates',total=2548140,Terry=5352,agreement='allseven totals agree with official history database and original ENR'),
        dict(source='HouseClerk2024 PDFpage64 printed62, visually verified',scope='six presidential party rows; Constitution/Terry omitted',total=2542788,missing_from_database_scope=5352,action='retain omission; no cause/release chronology inferred'),
        dict(source='HouseClerk2020 PDFpage62 printed60, visually verified',scope='three named Senate candidates only; generic write-in absent',total=2512810,missing_from_database_scope=2294,party_disagreement='Bledsoe Constitution/CON in Clerk and original ENR; Conservative/274 in history database'),
        dict(source='HouseClerk2022 PDFpage44 printed42, visually verified',scope='Scott/Matthews/genericWriteIn all3',total=1695702,agreement='exact')]
    primary['turnout_scope_note']='VHM printed-list active+some inactive; BCM PDF Total Registered status scope not specified; original ENR registered/totalVoters retained by release. Contest votes, election ballots and registration never substituted.'
    dump(BASE/'primary-controls.json',primary);rows(BASE/'state-candidates.csv',states)
    t=loadbody(SRC/'candidate-general-senate.meta.json')[0].decode();items=[]
    for m in re.finditer(r'<tr data-index="(\d+)" data-key="(\d+)">(.*?)</tr>',t,re.S):
        fs=[html.unescape(re.sub('<[^>]*>','',x)).strip()for x in re.findall(r'<td[^>]*>(.*?)</td>',m[3],re.S)]
        items.append(dict(source_ordinal=int(m[1]),tracking_candidate_id=m[2],office=fs[0],name_on_ballot=fs[2],party=fs[4],status=fs[6]))
    active=[r for r in items if r['status']=='Active'];assert len(active)==4 and len(items)==14
    charleston=loadbody(SRC/'charleston-current-ballot.meta.json')[0].decode()
    for r in active:assert r['name_on_ballot']in charleston
    dump(BASE/'current-ballot-evidence.json',dict(general_election_id='22596',date='2026-11-03',all_tracking_records=items,current_general_names=active,
        authority='Official Charleston County current On the Ballot publication plus official State Election Commission general-election name-on-ballot/status publication; four named options, write-in permitted by law',
        primary_urls=['https://www.charlestoncounty.gov/departments/bevr/?r=321','https://vrems.scvotes.sc.gov/Candidate/CandidateSearch?electionId=22596'],
        current_names_verified=True,results_candidate_ids_verified=False,tracking_id_warning='These are filing/tracking IDs, not November ENR choice IDs. No old historical or primary ID is mapped into November. Refresh final official results configuration before live admission.',
        final_certified_ballot_pdf_verified=False,limits='Current public general ballot publication verified; final ballot certification document and actual November result choice IDs remain unverified. Prior detail URLs resolved against POSTslash incorrectly redirect to search; corrected document-base captures retained separately.'))
    print(compact(dict(state_candidates=len(states),current_active_names=len(active),historical_query_audits=len(audits),shared_originals=len(refs))))
if __name__=='__main__':main()
