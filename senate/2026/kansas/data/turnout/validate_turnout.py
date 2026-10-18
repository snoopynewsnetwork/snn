#!/usr/bin/env python3
"""Offline integer, provenance, native-scope and peer checks; never edits inputs.

Default writes deterministic validation.json. --check-only also checks its own
pinned output hash without rewriting it, avoiding validation/manifest cycles.
"""
import argparse, csv, gzip, json, re
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from urllib.parse import unquote, urlsplit
from sources import HERE, STATE, source_bytes, worksheets, pdf_text, sha, dump_json, shared_manifest
from build_turnout import IDENTITIES, SOURCES, BROAD, unit_key, vote_value

def jsonl(p):return [json.loads(x) for x in gzip.open(p,'rt')]

def main(check_only=False):
    checks=[]
    def check(name,condition,detail=None):
        checks.append({'check':name,'pass':bool(condition),'detail':detail})
        if not condition:raise AssertionError((name,detail))
    county=list(csv.DictReader((STATE/'data/county-turnout.csv').open()))
    rankings=json.loads((HERE/'rankings.json').read_text()); contract=json.loads((HERE/'priority-set.json').read_text())
    check('county identity uniqueness and exact105 coverage',len(county)==105 and len({r['county_fips'] for r in county})==105 and len({r['county_key'] for r in county})==105)
    census={}
    for line in source_bytes('county-codes-2020').decode().splitlines():
        a=line.split('|')
        if a[0]=='KS':census[a[1]+a[2]]=a[4][:-7]
    check('all105 FIPS/name/key joins match primary Census code list',all(census.get(r['county_fips'])==r['county'] and r['county_key']=='US-KS-'+r['county_fips'] for r in county))
    for prefix in IDENTITIES:
        for r in county:assert sum(int(r[prefix+'_'+k]) for k in IDENTITIES[prefix])==int(r[prefix+'_total'])
    controls=list(csv.DictReader((HERE/'extracts/candidate-controls.csv').open()))
    check('all23 named-candidate county sums equal independent primary statewide PDF controls',len(controls)==23 and all(int(r['difference'])==0 and sum(int(c[r['contest']+'_'+r['candidate_key']]) for c in county)==int(r['control_votes']) for r in controls))
    check('primary2026 exact13 candidate party controls',sum(int(r['control_votes']) for r in controls if r['contest']=='senate_primary_2026' and r['party']=='D')==224076 and sum(int(r['control_votes']) for r in controls if r['contest']=='senate_primary_2026' and r['party']=='R')==338732)
    for measure,r in rankings.items():
        order=r['all_unit_order'];values=[x['votes'] for x in order];cum=0
        assert len(order)==105 and len({x['county_fips'] for x in order})==105
        assert order==sorted(order,key=lambda x:(-x['votes'],x['county_fips']))
        assert sum(values)==r['denominator'] and sum(Fraction(v,r['denominator']) for v in values)==1
        for rank,x in enumerate(order,1):
            cum+=x['votes'];assert rank==x['rank'] and cum==x['cumulative_votes']
            assert Fraction(x['share_exact'])==Fraction(x['votes'],r['denominator'])
        n=r['minimum80_count'];assert sum(values[:15])==r['top15_votes']
        assert 5*sum(values[:n-1])<4*r['denominator']<=5*sum(values[:n])
        assert sum(values[:n-1])==r['preceding_votes'] and sum(values[:n])==r['minimum80_votes']
        assert r['remainder_votes']==sum(values[n:]) and r['remainder_count']==105-n
    check('all10 county measure orders, weights, integer minimum80 and remainders',len(rankings)==10)
    check('primary order and exact crossing', [x['county_key']for x in rankings['president_2024']['all_unit_order']]==contract['full_all_unit_order']==[r['county_key']for r in county] and contract['denominator']==1327591 and contract['minimum80']['minimum80_count']==23 and contract['minimum80']['crossing']['county_fips']=='20191' and contract['minimum80']['preceding_votes']==1057110 and contract['minimum80']['minimum80_votes']==1067659)
    check('priority/top15/remainder membership conserved',contract['ordered_priority_keys']==[r['county_key'] for r in county if r['priority80']=='1'] and contract['ordered_top15_keys']==[r['county_key']for r in county if r['top15']=='1'] and contract['ordered_priority_keys']+contract['ordered_remainder_keys']==contract['full_all_unit_order'])
    check('unreported write-in under over blank fields remain unavailable',all(all(r[f]=='' for f in ['generic_write_in_2024','valid_named_write_in_2024','undervotes_2024','overvotes_2024','blank_ballots_2024']) for r in county))
    units=jsonl(HERE/'extracts/native-units.jsonl.gz');obs=jsonl(HERE/'extracts/candidate-observations.jsonl.gz');footers=jsonl(HERE/'extracts/county-summary-observations.jsonl.gz')
    um={u['unit_key']:u for u in units};og=defaultdict(list)
    for o in obs:og[o['unit_key']].append(o)
    check('native keys unique and exact22031 coverage',len(um)==len(units)==22031 and set(um)==set(og))
    expected={BROAD:4567,'sos-2024-president-precinct':4566,'sos-2022-senate-precinct':4535,'sos-2020-senate-precinct':3867,'sos-2026-senate-primary-precinct':4496}
    unknown={BROAD:0,'sos-2024-president-precinct':13,'sos-2022-senate-precinct':12,'sos-2020-senate-precinct':19,'sos-2026-senate-primary-precinct':31}
    check('native all105 county coverage in each source family',Counter(u['source_id']for u in units)==expected and all(len({u['county_fips']for u in units if u['source_id']==s})==105 for s in expected))
    check('native blank redacted counts preserved by family',Counter({s:sum(u['unknown_named_cells']>0 for u in units if u['source_id']==s) for s in expected})==unknown)
    for u in units:
        assert u['unit_key']==unit_key(u['source_id'],u['sheet'],u['county_native'],u['native_id_fields'])
        oo=og[u['unit_key']];named=[x for x in oo if x['category']=='named_candidate']
        assert len(named)==len(IDENTITIES[u['contest']]) and len({x['candidate_key']for x in named})==len(named)
        assert u['named_candidate_numeric_sum']==sum(x['votes'] for x in named if x['votes'] is not None)
        assert u['unknown_named_cells']==sum(x['votes'] is None for x in named)
        if not u['unknown_named_cells']:assert u['named_candidate_total']==u['named_candidate_numeric_sum']
        else:assert u['named_candidate_total'] is None
        if u['reported_total_votes_cast'] is not None:
            assert u['reported_total_votes_cast']==u['named_candidate_total']+u['generic_write_in_votes']
    check('all native candidate identities, zeros, missingness, integer sums and contest totals',True)
    raw={};raw_count=0
    for sid in expected:
        orig=list(worksheets(source_bytes(sid)))
        extracted=jsonl(HERE/'extracts'/f'{sid}-rows.jsonl.gz')
        reconstructed=[{'source_id':sid,'sheet':s,'xml_path':p,'row':n,'cells':d}for s,p,rs in orig for n,d in rs]
        assert reconstructed==extracted
        for r in extracted:raw[(sid,r['sheet'],r['row'])]=r['cells']
        raw_count+=len(extracted)
        assert sha(source_bytes(sid))==contract['source_hashes'][sid]
    check('all94008 source worksheet rows including headers raw blanks and unrelated fields agree original OOXML',raw_count==94008)
    coords=set()
    for o in obs+footers:
        k=(o['source_id'],o['sheet'],o['row'],o['column'])
        assert k not in coords;coords.add(k)
        value=raw[k[:3]].get(o['column'])
        assert value==o['raw_value'] and vote_value(value)==(o['votes'],o['value_status'])
    check('every detail and footer value matches exact original source position',len(obs)==121053 and len(footers)==96,{'detail':len(obs),'footer':len(footers)})
    check('comma-formatted Wyandotte2020 footer retained',sum(o['source_id']=='sos-2020-senate-precinct' and o['sheet']=='WYANDOTTE' and o['row']==131 for o in footers)==4)
    check('generic write-in scope separately conserved',{r['county']:int(r['generic_write_in_2020_published_supplement'])for r in county if r['generic_write_in_2020_published_supplement']!=''}=={'Shawnee':94,'Sedgwick':242,'Wyandotte':120})
    flattened=[x for c in contract['all_geography_coverage']for f in c['source_native_families']for x in f['constituents']]
    check('contract preserves all525 county-family groups and exact native constituents',len(flattened)==len(units)==len({x['unit_key']for x in flattened}) and len(contract['all_geography_coverage'])==105 and sum(len(c['source_native_families'])for c in contract['all_geography_coverage'])==525)
    for x in flattened:
        u=um[x['unit_key']]
        assert all(x[k]==u[k]for k in x)
    check('all constituent native objects unchanged relative to full source extraction',True)
    native_order=list(csv.DictReader(gzip.open(HERE/'extracts/native-unit-order.csv.gz','rt')))
    for sid in expected:
        order=[x for x in native_order if x['source_id']==sid]
        known=[x for x in order if x['known_count_rank']!=''];missing=[x for x in order if x['known_count_rank']=='']
        assert len(order)==expected[sid] and len(missing)==unknown[sid]
        desired=sorted([u for u in units if u['source_id']==sid and u['named_candidate_total'] is not None],key=lambda u:(-u['named_candidate_total'],u['county_fips'],u['sheet'],u['source_rows']))
        assert [x['unit_key']for x in known]==[u['unit_key']for u in desired]
        assert all(x['named_candidate_total']=='' for x in missing)
    nr=json.loads((HERE/'native-ranking-2024.json').read_text());values=[um[k]['named_candidate_total']for k in nr['all_unit_order']];n=nr['minimum80_count']
    check('full4567-context native order minimum80 and remainder',len(values)==4567 and sum(values)==1327591 and sum(values[:15])==36633 and n==1477 and 5*sum(values[:n-1])<4*sum(values)<=5*sum(values[:n]) and sum(values[n:])==nr['remainder_votes'])
    diffs=list(csv.DictReader((HERE/'extracts/native-county-reconciliation.csv').open()))
    residual=Counter()
    for r in diffs:
        assert int(r['county_control_minus_numeric_native_sum'])==int(r['county_control_votes'])-int(r['numeric_native_sum'])
        residual[r['source_id']]+=int(r['county_control_minus_numeric_native_sum'])
    check('known residuals retained without native allocation',dict(residual)=={'sos-2024-president-precinct':44,'sos-2022-senate-precinct':8,'sos-2020-senate-precinct':0,'sos-2026-senate-primary-precinct':22})
    admin=jsonl(HERE/'extracts/county-administration.jsonl.gz');ac=json.loads((HERE/'administrative-controls.json').read_text())
    check('all administrative families retain105 county records',Counter(r['source_id']for r in admin)=={BROAD:105,'turnout-2022':105,'registration-2024-november':105,'registration-2026-october':105,'inactive-2026-october':105})
    check('2024 source vintages remain distinct',ac['turnout2024_broad_footer']['ballots_cast']==1343020 and ac['turnout2024_broad_footer']['registered_voters']==2031120 and ac['2024_release']['ballots_cast']==1344147 and ac['2024_release_minus_broad']=={'ballots_cast':1127,'registered_voters':12,'allocation':'unresolved; no county adjustments'})
    text=re.sub('<[^>]+>',' ',source_bytes('certification-2024').decode())
    check('2024 certification release original controls and method sum',all(v in text for v in ['1,344,147','2,031,132','137,644','557,209','649,294']) and 137644+557209+649294==1344147)
    text=re.sub('<[^>]+>',' ',source_bytes('statistics-data').decode())
    check('2020 statewide turnout and method controls remain source scoped',all(v in text for v in ['1,375,125','1,938,560','459,229','371,854','544,042','45,671']) and 459229+371854+544042==1375125)
    check('2026 active inactive total exact bounds',all(int(r['active_voters_2026_10_01'])+int(r['inactive_voters_2026_10_01'])==int(r['registered_voters_2026_10_01'])for r in county) and sum(int(r['registered_voters_2026_10_01'])for r in county)==2027520 and ac['2026_registration_internal_date']==['2026-10-01'])
    anomalies=[r['county']for r in county if int(r['senate_2022_total'])>int(r['ballots_cast_2022'])]
    check('source inconsistent2022 ballot bounds explicitly retained',set(anomalies)=={'Sumner','Rice','Wilson','Phillips','Washington'} and [r['county']for r in county if int(r['ballots_cast_2022'])>int(r['registered_voters_2022'])]==['Stevens'],{'candidate_votes_exceed_ballots':sorted(anomalies),'ballots_exceed_registration':['Stevens'],'treatment':'retained as source inconsistency; excluded from clean weights'})
    check('2024 candidate votes bounded by source ballots',all(int(r['president_2024_total'])<=int(r['ballots_cast_2024_broad']) for r in county))
    check('four N/A mail cells remain unknown not zero',{r['county']for r in admin if r['source_id']=='turnout-2022' and r['advance_ballots_returned_by_mail'] is None}=={'Bourbon','Cherokee','Osage','Rice'})
    spot=json.loads((STATE/'data/news/sumner-2022-control.json').read_text())
    st=pdf_text('sumner-2022-actual-linked-summary');section=st.split('U.S. Senate',1)[1].split('U.S. Hse of Reps',1)[0]
    def numbers(label):
        line=next(line for line in section.splitlines()if line.strip().startswith(label))
        return [int(v.replace(',',''))for v in re.findall(r'\d[\d,]*',line[len(line)-len(line.lstrip())+len(label):])]
    candidate_methods={'Jerry Moran':numbers('REP Jerry Moran'),'David C. Graham':numbers('LIB David C. Graham'),'Mark R. Holland':numbers('DEM Mark R. Holland')}
    for name,vals in candidate_methods.items():assert vals[0]==spot['named_Senate_candidates'][name] and sum(vals[1:])==vals[0]
    generic=numbers('Write-In Totals');under=numbers('Undervotes');over=numbers('Overvotes');total=numbers('Contest Totals');cast=numbers('Total Votes Cast')
    check('supplemental Sumner2022 original county method and ballot distinction independently verified',spot['ballots_cast']==7932 and spot['blank_ballots']==4 and sum(v[0]for v in candidate_methods.values())==7869 and generic[0]==3 and under[0]==60 and over[0]==0 and cast[0]==7872 and total==[7932,6117,1720,4,5,1,85] and all(sum(v[i]for v in candidate_methods.values())+generic[i]+under[i]+over[i]==total[i]for i in range(7)),{'scope':'single external supplemental county control; statewide CSV and native families unchanged'})
    peer=json.loads((HERE/'peer-agreement.json').read_text())
    check('actual peer agreement and pinned assets',peer['status']=='pass' and not peer['mismatches'] and peer['turnout_csv_sha256']==sha((STATE/'data/county-turnout.csv').read_bytes()) and all(sha((STATE/r['path']).read_bytes())==r['sha256'] for r in peer['peer_assets']))
    refs=json.loads((HERE/'source/shared-references.json').read_text())
    for r in refs:
        p=HERE/r['path'];data=p.read_bytes();assert len(data)==r['stored_bytes'] and sha(data)==r['stored_sha256']
        if r.get('compression','').startswith('gzip'):
            original=gzip.decompress(data);assert len(original)==r['original_bytes'] and sha(original)==r['original_sha256']
    check('shared original stored and decompressed hashes sizes',True,{'referenced_assets':len(refs)})
    acquisition=json.loads((HERE/'source/acquisition.json').read_text())
    for r in acquisition:
        if 'path' not in r:assert 'error'in r;continue
        data=(HERE/r['path']).read_bytes();rawbytes=gzip.decompress(data)
        assert len(data)==r['stored_bytes'] and sha(data)==r['stored_sha256'] and len(rawbytes)==r['raw_bytes'] and sha(rawbytes)==r['raw_sha256']
    check('new acquisition complete gzip bytes hashes status metadata redirects retained',True,{'captures':len(acquisition),'failed_or_unavailable':[r['id']for r in acquisition if r.get('status')!=200]})
    markdown=[STATE/'turnout.md',HERE/'source/SCHEMA.md'];link_count=0
    for p in markdown:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):
            if urlsplit(target).scheme or target.startswith('#'):continue
            dest=unquote(target.split('#')[0]);assert (p.parent/dest).exists(),(p,target);link_count+=1
    check('all relative report and schema links resolve',True,{'relative_links':link_count})
    owned=[STATE/'turnout.md',STATE/'data/county-turnout.csv']+[p for p in HERE.rglob('*')if p.is_file()]
    check('strict individual artifact size limit and no dependency cache directories',all(p.stat().st_size<40_000_000 for p in owned) and not any(p.name in {'node_modules','__pycache__','.cache'}for p in HERE.rglob('*')))
    manifest=json.loads((HERE/'asset-manifest.json').read_text())
    expected_paths={str(p.relative_to(STATE))for p in owned if p.name!='asset-manifest.json'}
    check('asset manifest includes all owned deliverables',expected_paths=={r['path']for r in manifest['assets']})
    for r in manifest['assets']:
        if not check_only and r['path']=='data/turnout/validation.json':continue
        p=STATE/r['path'];assert p.stat().st_size==r['bytes'] and sha(p.read_bytes())==r['sha256'],r['path']
    check('owned asset hashes and sizes verified',True,{'mode':'check-only includes validation self hash' if check_only else 'validation output self hash verified by final check-only pass'})
    check('external coordinator accepted research scope path only no reverse hash',contract.get('coordinator_acceptance_record')=='../coordinator-priority-acceptance.json' and json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text())['accepted'] and 'coordinator_acceptance_sha256'not in contract)
    result={'status':'pass','validation_scope':'offline preservation and arithmetic; known source inconsistencies remain qualified',
        'county_count':105,'native_identities':22031,'detail_observations':len(obs),'footer_observations':len(footers),
        'checks':checks,'material_gaps':['No statewide generic/valid named write-in, under/over or blank controls in the priority source universe.',
          '2024 broad versus release ballot/registration vintages differ; no county allocation imposed.',
          '2022 turnout ballot table violates named-vote/registration bounds in specified counties.',
          'Blank/redacted native cells and positive residuals remain unallocated.',
          'Current court receipt rule and approved November2026 geometry require official-results/maps review.'],
        'coordinator_acceptance':'external path-only record; no current geographic or live forecast approval'}
    if not check_only:dump_json('validation.json',result)
    print(json.dumps({'status':'pass','checks':len(checks),'counties':105,'native_identities':22031,'mode':'check-only'if check_only else 'write validation'}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check-only',action='store_true');main(parser.parse_args().check_only)
