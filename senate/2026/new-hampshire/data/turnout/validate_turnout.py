#!/usr/bin/env python3
"""Meaningful stdlib-only offline checks; known source defects are explicit.

Run manifest.py after any edits, then rerun this validator to verify its hashes.
No network, Git, source refresh, native identity imputation or peer-file edits.
"""
import collections
import csv
from fractions import Fraction
import gzip
import hashlib
import json
import pathlib
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT=pathlib.Path(__file__).resolve().parent
STATE=ROOT.parent.parent
PRES='sos-2024-president-archived-original'
S22='sos-archived-2022-ge-us-senator-5-xls'
S20='sos-2020-senate-archived-original'


def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def jl(p):return [json.loads(x)for x in gzip.decompress((ROOT/p).read_bytes()).splitlines()]
def n(v):
    if isinstance(v,(int,float)):
        assert v==int(v)and v>=0
        return int(v)
    if isinstance(v,str)and re.fullmatch(r'[\d,]+',v):return int(v.replace(',',''))
    return None


def main():
    checked=[]
    q=load('priority-set.json');rr=q['all_units'];csvrows=list(csv.DictReader((ROOT.parent/'county-turnout.csv').open()))
    assert len(rr)==len(csvrows)==320
    assert len({x['geography_key']for x in rr})==320
    assert len({(x['county'],x['native_label'].strip())for x in rr})==320
    assert [x['geography_key']for x in rr]==q['full_ordered_keys']==[x['geography_key']for x in csvrows]
    order=sorted(rr,key=lambda x:(-x['reported_candidate_write_in_votes'],x['county_fips'],x['native_label'].strip()))
    assert [x['geography_key']for x in rr]==[x['geography_key']for x in order]
    candidate_fields=['harris_walz','trump_vance','oliver_ter_maat','stein_ware','generic_write_ins']
    expected=dict(harris_walz=418488,trump_vance=395523,oliver_ter_maat=4425,stein_ware=3680,generic_write_ins=4073,undervotes=4482,overvotes=362)
    for k,v in expected.items():assert sum(x[k]for x in rr if x[k]is not None)==v,(k,v)
    for row,c in zip(rr,csvrows):
        assert row['reported_candidate_write_in_votes']==sum(row[k]for k in candidate_fields if row[k]is not None)
        for k in expected:assert c[k]==(''if row[k]is None else str(row[k])),(row['native_label'],k)
        assert row['native_label']==c['native_label']
        assert row['source_native_id']is None
        assert all(x['source_native_id']is None for x in row['available_constituents'])
        assert c['ballots_cast_2024']==c['registration_2024']==''
    total=sum(x['reported_candidate_write_in_votes']for x in rr);assert total==q['denominator']==826189
    assert sum(Fraction(x['reported_candidate_write_in_votes'],total)for x in rr)==1
    cum=0;cross=None
    for i,row in enumerate(rr,1):
        cum+=row['reported_candidate_write_in_votes'];assert row['rank']==i and row['cumulative_votes']==cum
        assert row['share_denominator']==total and row['share_numerator']==row['reported_candidate_write_in_votes']
        if cross is None and cum*5>=total*4:cross=i
    assert cross==143
    assert sum(x['reported_candidate_write_in_votes']for x in rr[:15])==185659==q['top15']['votes']
    assert rr[141]['cumulative_votes']==660378 and rr[142]['cumulative_votes']==662624 and rr[142]['display_label']=='Tilton'
    assert 5*rr[141]['cumulative_votes']<4*total<=5*rr[142]['cumulative_votes']
    assert q['ordered_priority_keys']==q['ordered_minimum80_keys']==[x['geography_key']for x in rr[:143]]
    assert q['remainder_ordered_keys']==[x['geography_key']for x in rr[143:]]
    assert len(rr[143:])==177 and sum(x['reported_candidate_write_in_votes']for x in rr[143:])==163565
    checked.append('320 unique complete native rows; candidate universe; all-unit order; rational weights; CSV null preservation; top15; integer minimal80; complete remainder')
    assert collections.Counter(x['kind']for x in rr)==dict(city_ward=73,city_total_only_native_row=1,town_or_territory_native_row=246)
    parent_keys=set()
    for parent in q['hierarchy']['parent_summaries']:
        assert not parent['counted_in_state']
        assert not parent_keys.intersection(parent['constituent_keys']);parent_keys.update(parent['constituent_keys'])
        assert all(next(x for x in rr if x['geography_key']==k)['kind']=='city_ward'for k in parent['constituent_keys'])
    assert len(parent_keys)==73 and len(q['hierarchy']['parent_summaries'])==12
    assert sum(x['parent_cousub_geoid_2020']is None for x in rr)==18
    assert sum(x['candidate_field_completeness']!='complete_numeric'for x in rr)==20
    assert sum(x['reporting_status'].startswith('printed-ticket')for x in rr)==16
    assert not any(x['display_label']=='TOTALS'or x['display_label'].endswith(' County')for x in rr)
    checked.append('Disjoint city-parent hierarchy, no county/summary overlap, explicit 18 unavailable GEOIDs and all unpopulated administrative cases')
    controls=load('controls.json');audits={x['source_id']:x for x in load('reconciliation.json')}
    source_native_count=0;field_count=0;position_count=0
    for coverage in q['source_native_coverage']:
        sid=coverage['source_id'];b=(ROOT/coverage['path']).read_bytes();assert sha(b)==coverage['sha256']
        ns=[json.loads(x)for x in gzip.decompress(b).splitlines()]
        assert len(ns)==coverage['native_rows']==len(coverage['constituents'])==320
        assert len({(r['county'],r['native_label'])for r in ns})==320
        if 'sheet'in ns[0]['source_locator']:
            raw={(x['sheet'],x['source_row']):x for x in jl('extracts/'+sid+'-rows.jsonl.gz')}
            for r in ns:
                pos=r['source_locator'];x=raw[pos['sheet'],pos['source_row']]
                offset=6 if pos.get('source_column_start')=='G'else 0
                assert x['values'][offset]==r['native_label']
                values=x['values'][offset+1:]
                # Relevant values occur in exact original row order; intentional
                # separator blanks in checklist sheets remain in raw rows.
                cursor=0
                for v in r['raw_fields'].values():
                    while cursor<len(values)and values[cursor]!=v:cursor+=1
                    assert cursor<len(values),(sid,r['native_label'],v)
                    cursor+=1
                position_count+=1
        else:
            raw={(x['page'],x['line']):x['text']for x in jl('extracts/'+sid+'-lines.jsonl.gz')}
            for r in ns:
                pos=r['source_locator'];line=raw[pos['page'],pos['line']]
                assert line.lstrip().startswith(r['native_label'])
                tail=line.lstrip()[len(r['native_label']):].split()
                assert [str(v)for v in r['raw_fields'].values()if v!='']==tail,(sid,r['native_label'],tail)
                position_count+=1
        for r,c in zip(ns,coverage['constituents']):
            assert c['native_label']==r['native_label']and c['locator']==r['source_locator']and c['source_native_id']is None
            for k,v in r['fields'].items():assert n(r['raw_fields'][k])==v
            field_count+=len(r['fields'])
        state=controls[sid]['summary']['TOTALS']['fields'];audit=audits[sid]
        actual={k:sum(r['fields'][k]for r in ns if r['fields'][k]is not None)for k in state}
        assert actual==audit['native_numeric_sums']
        assert state==audit['state']
        if sid in [PRES,S22,S20,'2020-ge-ballots-cast-xls','2020-ge-names-on-checklist-xlsx','2022-ge-ballots-cast-3-xls','2022-ge-names-on-checklist-2-xlsx','2024-ge-names-on-checklist-7-xlsx']:
            assert actual==state,(sid,actual,state)
            for c in audit['counties']:
                assert all(x in [0,None]for x in c['detail_minus_footer'].values())
                assert all(x in [0,None]for x in c['footer_minus_summary'].values())
        source_native_count+=len(ns)
    assert controls[S22]['summary']['TOTALS']['fields']==dict(hassan=332490,bolduc=275631,kauffman=12390,scatter=464)
    assert controls[S20]['summary']['TOTALS']['fields']==dict(messner=326229,shaheen=450778,odonnell=18421,scatter=486)
    xls22=jl('native/'+S22+'.jsonl.gz');pdf22=jl('native/sos-archived-2022-ge-us-senator-remediated-1-pdf.jsonl.gz')
    assert [(x['county'],x['fields'])for x in xls22]==[(x['county'],x['fields'])for x in pdf22]
    checked.append('All retained source-native rosters/fields/positions, raw null/type scope, full selected primary county/state controls and independent 2022 PDF count vectors')
    for sid,x in load('sensitivity.json').items():
        rows=x['ordered'];den=sum(r['volume']for r in rows);assert den==x['denominator']and len(rows)==320
        assert [(r['volume'],r['county_fips'],r['native_label'].strip())for r in rows]==sorted([(r['volume'],r['county_fips'],r['native_label'].strip())for r in rows],key=lambda r:(-r[0],r[1],r[2]))
        cut=x['minimum80']['count'];before=sum(r['volume']for r in rows[:cut-1]);at=before+rows[cut-1]['volume']
        assert 5*before<4*den<=5*at
        assert before==x['minimum80']['preceding_votes']and at==x['minimum80']['votes']
        assert sum(r['volume']for r in rows[:15])==x['top15']['votes']
        assert sum(Fraction(r['volume'],den)for r in rows)==1
    sens=load('sensitivity.json');fixed={(r['county'],r['display_label'])for r in rr[:143]}
    for sid,want in [('2024-ge-ballots-cast-14-xls',666554),('2024-ge-names-on-checklist-7-xlsx',817376),(S22,495056)]:
        matched=[r for r in sens[sid]['ordered']if(r['county'],r['native_label'].strip())in fixed]
        assert len(matched)==143 and sum(r['volume']for r in matched)==want
    assert audits['2024-ge-ballots-cast-14-xls']['native_minus_state']==dict(regular=0,absentee=1,ballots_total=1)
    adm={x['source_id']:x for x in load('administrative-audit.json')}
    h=[x for x in adm['2024-ge-names-on-checklist-7-xlsx']['equation_disagreements']if x['scope']=='native'];assert len(h)==1 and h[0]['native_label']=='Hopkinton'and h[0]['reported_total']==3 and h[0]['components_minus_reported_total']==293
    checked.append('Independent source-scoped sensitivities and exact known administrative defects, with no residual repair')
    # Direct primary national controls, including the 2022 vintage disagreement.
    text=gzip.decompress((ROOT/'extracts/house-clerk-2024.txt.gz').read_bytes()).decode().split('NEW HAMPSHIRE',1)[1].split('FOR UNITED STATES REPRESENTATIVE',1)[0]
    for label,value in [('Democratic',418488),('Republican',395523),('Libertarian',4425),('Green',3680),('Write-in',4073),('Under Votes',4482),('Over Votes',362)]:
        m=re.search(re.escape(label)+r'\s*\.+\s*([\d,]+)',text);assert m and n(m[1])==value
    text22=gzip.decompress((ROOT/'extracts/house-clerk-2022.txt.gz').read_bytes()).decode().split('NEW HAMPSHIRE',1)[1].split('FOR UNITED STATES REPRESENTATIVE',1)[0]
    assert re.search(r'Bolduc[^\n]*275,928',text22)and re.search(r'Hassan[^\n]*332,193',text22)
    fec=gzip.decompress((ROOT/'extracts/fec-pres-2024.txt.gz').read_bytes()).decode()
    assert re.search(r'^NH\s+4,073\s+826,189\s*$',fec,re.M)
    checked.append('Primary House Clerk seven-field and FEC candidate-universe controls; older 2022 Clerk split retained')
    for contest in load('contest-candidates.json'):
        sf=controls[contest['source_id']]['summary']['TOTALS']['fields']
        assert {x['project_field_key']:x['statewide_source_count']for x in contest['fields']}==sf
        assert len(contest['fields'])==len({x['project_field_key']for x in contest['fields']})
        assert contest['literal_headers']
    hrefs={x['literal_href']for x in load('source/official-index-links.json')['links']}
    assert hrefs=={'/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-president_3.xls','/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-ballots-cast_14.xls','/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-names-on-checklist_7.xlsx'}
    checked.append('Candidate/header identity universe, exact official-index link selection and complete fixed-priority administrative/2022 label comparisons')
    originals=0
    for m in load('source/shared-originals.json'):
        b=(ROOT/m['shared_path']).read_bytes();assert len(b)<40_000_000 and sha(b)==m['stored_sha256']
        body=gzip.decompress(b);assert len(body)==m['bytes']and sha(body)==m['raw_sha256'];originals+=1
    for path in sorted((ROOT/'source').glob('*.json')):
        m=json.loads(path.read_text())
        if not isinstance(m,dict)or 'body_path'not in m:continue
        stored=(path.parent/m['body_path']).read_bytes();assert sha(stored)==m['stored_sha256']and len(stored)==m['stored_bytes']
        entity=gzip.decompress(stored);assert sha(entity)==m['original_sha256']and len(entity)==m['original_bytes']
        hdr=(path.parent/m['headers_path']).read_bytes();assert sha(hdr)==m['headers_sha256']
        decoded=gzip.decompress(entity)if m.get('http_content_decoding')=='gzip'else entity
        assert sha(decoded)==m['decoded_original_sha256']and len(decoded)==m['decoded_original_bytes']
        assert m['requested_url']and m['final_url']and m['retrieved_utc'];originals+=1
    for m in load('source-inventory.json'):
        b=(ROOT/m['path']).read_bytes();assert sha(b)==m['stored_sha256']and len(b)==m['stored_bytes']
    checked.append('All retained original/stored/HTTP-decoded hashes, byte sizes, exact reconstruction, request metadata and source-reference bounds')
    links=[]
    for file in [STATE/'turnout.md',ROOT/'source/SCHEMA.md']:
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',file.read_text()):
            link=link.strip('<>');u=urlsplit(link)
            if u.scheme or link.startswith('#'):continue
            target=(file.parent/unquote(u.path)).resolve();assert target.exists()or target==ROOT/'validation.json',(str(file),link)
            assert STATE in target.parents or target==STATE,(str(file),link)
            links.append(str(target.relative_to(STATE)))
    allpaths=[STATE/'turnout.md',ROOT.parent/'county-turnout.csv']+sorted(p for p in ROOT.rglob('*')if p.is_file())
    assert all(p.stat().st_size<40_000_000 for p in allpaths)
    assert not any('__pycache__'in p.parts or p.suffix=='.pyc'for p in allpaths)
    manifest_path=ROOT/'asset-manifest.json'
    if manifest_path.exists():
        assets=load('asset-manifest.json')['assets'];expected_paths={str(p.relative_to(STATE))for p in allpaths if p!=manifest_path}
        assert {x['path']for x in assets}==expected_paths
        for r in assets:
            p=(STATE/r['path']).resolve();assert STATE in p.parents
            b=p.read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256'],r['path']
    checked.append('All relative report/schema links and strict below-40,000,000-byte bounds; complete manifest hashes when present')
    peer=load('peer-agreement.json')
    peer_evidence_vintage_updates=[]
    if peer.get('agreement_claimed'):
        assert peer['status']=='agreed_after_independent_full_comparison'
        assert peer['mismatches']==[]
        for m in peer['peer_assets']:
            p=(STATE/m['path']).resolve();assert STATE in p.parents
            b=p.read_bytes()
            if sha(b)!=m['sha256']or len(b)!=m['bytes']:
                # The actual peer subsequently added verification counters and
                # the frozen contract reference. Accepted historical witness
                # bytes stay pinned; counting inputs may not change here.
                assert m['path']=='data/baselines/peer-reconciliation.json',m['path']
                updated=json.loads(b)
                assert updated['peer_csv_sha256']==sha((ROOT.parent/'county-turnout.csv').read_bytes())
                assert updated['peer_priority_sha256']==sha((ROOT/'priority-set.json').read_bytes())
                assert updated['priority_arithmetic_equal']is True
                for k in ['priority_field_disagreements','source_native_disagreements','raw_value_disagreements','BIFF_type_disagreements']:assert updated[k]==[]
                assert len(updated['source_native_checks'])==23
                assert all(x['own_count']==x['peer_count']==320 and x['full_candidate_method_fields_equal']for x in updated['source_native_checks'])
                peer_evidence_vintage_updates.append(dict(path=m['path'],accepted_observation_sha256=m['sha256'],current_sha256=sha(b),scope='Peer expanded metadata/counters and references frozen contract; no native/count/order disagreement. Accepted reciprocal witness itself remains unchanged.'))
    authority=q['coordinator_acceptance_authority']
    assert authority=='data/coordinator-priority-acceptance.json'and q['worker_acceptance_authority']is False
    ap=STATE/authority
    acceptance=json.loads(ap.read_text())if ap.exists()else None
    acceptance_observation=dict(path=authority,accepted=False,scope='No worker acceptance authority')
    if acceptance and acceptance.get('accepted'):
        contract=(ROOT/'priority-set.json').read_bytes()
        assert sha(contract)==acceptance['contract_sha256']=='11c042966c67a50e496ad6f839afd8e3c8b28afe6e2761c6cda1aa51f7ce90fc'
        assert len(contract)==acceptance['contract_bytes']==3653481
        assert q['full_ordered_keys']==acceptance['full_ordered_keys']and q['ordered_priority_keys']==acceptance['ordered_priority_keys']and q['remainder_ordered_keys']==acceptance['remainder_ordered_keys']
        pr=acceptance['peer_agreement'];assert sha((STATE/pr['path']).read_bytes())==pr['sha256']
        review=acceptance['independent_coordinator_review'];assert sha((STATE/review['path']).read_bytes())==review['sha256']
        acceptance_observation=dict(path=authority,accepted=True,accepted_at_utc=acceptance['accepted_at_utc'],scope=acceptance['acceptance_scope'],contract_preserved=True,current_geometry_approval=False)
        checked.append('Formal external historical acceptance verified against frozen contract, exact priority/remainder/order, pinned reciprocal evidence and independent coordinator review; no reverse acceptance hash')
    supplement=load('peer-control-agreement.json')
    assert supplement['mismatches']==[]and supplement['counts']['control_records']==483 and supplement['counts']['control_fields']==2289
    for m in supplement['peer_assets']:
        b=(STATE/m['path']).read_bytes();assert sha(b)==m['sha256']and len(b)==m['bytes'],m['path']
    result=dict(schema_version='nh-turnout-offline-validation-1',status='pass',checks=checked,
                counts=dict(priority_native_rows=320,retained_source_rosters=len(q['source_native_coverage']),source_native_records=source_native_count,source_native_fields=field_count,source_positions_checked=position_count,original_captures_verified=originals,relative_links_verified=len(links)),
                priority=dict(denominator=826189,top15_votes=185659,minimum80_count=143,preceding_votes=660378,crossing='Tilton',crossing_votes=2246,cumulative=662624,remainder_count=177,remainder_votes=163565),
                limitations=['Known administrative source discrepancies preserved; see administrative-audit.json.','Candidate generic write-ins do not establish named/valid write-in allocations.','Historical native labels/Census references do not approve current boundaries or clerk authority.'],
                independent_peer_status=peer['status'],peer_evidence_vintage_updates=peer_evidence_vintage_updates,coordinator_acceptance=acceptance_observation,manifest_policy='Manifest includes this deterministic validation; regenerate manifest after changing any owned artifact, then rerun validation.')
    (ROOT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],counts=result['counts'],peer=result['independent_peer_status'])))


if __name__=='__main__':main()
