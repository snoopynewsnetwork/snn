#!/usr/bin/env python3
"""Build disjoint historical baselines, controls and independent peer audit."""
import csv,gzip,io,json,re,sys
from pathlib import Path
from urllib.parse import quote
sys.dont_write_bytecode=True
from extract import HERE,STATE,COUNTIES,FIPS,PRES,S22,S20,num
from acquire import dump,sha

CONTESTS={
 PRES:dict(year=2024,date='2024-11-05',contest='President and Vice-President',role='priority_president_no_2024_senate',A='harris_walz',B='trump_vance',candidates=['harris_walz','trump_vance','oliver_ter_maat','stein_ware','generic_write_ins']),
 S22:dict(year=2022,date='2022-11-08',contest='United States Senator',role='other_Class_III_seat_actual_midterm',A='hassan',B='bolduc',candidates=['hassan','bolduc','kauffman','scatter']),
 S20:dict(year=2020,date='2020-11-03',contest='United States Senator',role='same_Class_II_seat',A='shaheen',B='messner',candidates=['shaheen','messner','odonnell','scatter'])}
NAMES={
 'harris_walz':('Kamala D. Harris and Tim Walz','Democratic'),
 'trump_vance':('Donald J. Trump and JD Vance','Republican'),
 'oliver_ter_maat':('Chase Oliver and Mike ter Maat','Libertarian'),
 'stein_ware':('Jill Stein and Rudolph Ware','Green'),
 'generic_write_ins':('Write-Ins','generic_unallocated_not_a_candidate'),
 'hassan':('Maggie Hassan','Democratic'), 'bolduc':('Donald C. Bolduc','Republican'),
 'kauffman':('Jeremy Kauffman','Libertarian'),
 'shaheen':('Jeanne Shaheen','Democratic'), 'messner':('Corky Messner','Republican'),
 'odonnell':("Justin O’Donnell",'Libertarian'),
 'scatter':('Scatter','generic_unallocated_not_a_candidate')}
def loadgz(p):return [json.loads(x) for x in gzip.decompress(p.read_bytes()).splitlines()]
def native(sid):return loadgz(HERE/'native'/(sid+'.jsonl.gz'))
def csvout(p,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def subtotal(f):return sum(v for v in f.values() if v is not None)
def geo(row,year):
    label=row['native_label'].strip();county=row['county'];ward=re.fullmatch(r'(.+) Ward (\d+)(\*)?',label)
    return dict(county=county,county_fips=FIPS[county],native_label=row['native_label'],
        geography_key=f'nh-{year}-'+('pres' if year==2024 else 'senate')+':'+FIPS[county]+':'+quote(label,safe=''),
        kind='city_ward' if ward else 'town_or_territory_native_row',
        municipal_parent_label=ward[1] if ward else label,ward=int(ward[2]) if ward else None,
        literal_correction_marker=bool(ward and ward[3]) or label.endswith('*'),
        source_native_id=None,current_2026_equivalence='unverified',
        source_locator=row['source_locator'])

def census_ids(refs):
    ref=next(x for x in refs if x['id']=='census-nh-cousub-codes')
    b=gzip.decompress((STATE/ref['path']).read_bytes()).decode('utf-8-sig');out={}
    for r in csv.DictReader(io.StringIO(b),delimiter='|'):
        # Exact county-scoped name after Census legal-type suffix only. No
        # punctuation, abbreviation, fuzzy, spelling or ward-number crosswalk.
        name=re.sub(r' (town|city|township)$','',r['COUSUBNAME'])
        if name==r['COUSUBNAME']:continue
        for n in [name]:
            k=('33'+r['COUNTYFP'],n)
            if k in out:assert out[k][0]=='33'+r['COUNTYFP']+r['COUSUBFP']
            out[k]=('33'+r['COUNTYFP']+r['COUSUBFP'],r['COUSUBNAME'].endswith(' city'))
    return out

def run():
    refs=json.loads((HERE/'source/references.json').read_text());controls=json.loads((HERE/'source/controls.json').read_text());inv=json.loads((HERE/'source/extraction-inventory.json').read_text())
    cid=census_ids(refs);rows=[];candidates=[];states=[];counties=[];reconciliation=[]
    for item in inv:
        sid=item['source_id']
        if not item['native_rows']:continue
        ns=native(sid);cs=[c for c in controls if c['source_id']==sid];fields=list(ns[0]['fields']);issues=[]
        assert len({(r['county'],r['native_label']) for r in ns})==len(ns),sid
        for c in COUNTIES:
            group=[r for r in ns if r['county']==c];footer=next((r for r in cs if r['county']==c and r['scope']=='county_footer'),None);summary=next((r for r in cs if r['county']==c and r['scope']=='county_summary'),None)
            sums={k:sum(r['fields'][k] for r in group if r['fields'][k] is not None) for k in fields}
            for scope,control in [('footer',footer),('summary',summary)]:
                if control:
                    for k,v in sums.items():
                        observed=control['fields'][k]
                        if observed is not None and v!=observed:issues.append(dict(county=c,field=k,scope=scope,numeric_detail_sum=v,control=observed,residual=v-observed))
            # Method/party registration identity is checked at each native row.
        identities=[]
        for r in ns:
            f=r['fields']
            equations=[]
            if 'ballots_cast' in f:equations=[('regular_plus_absentee','ballots_cast',['regular','absentee'])]
            if 'checklist_total' in f:
                equations=[('party_checklist_sum','checklist_total',['republican','democratic','undeclared'])]
                if 'polling_place_registered_republican' in f:equations.append(('new_party_sum','polling_place_registered_total',['polling_place_registered_republican','polling_place_registered_democratic','polling_place_registered_undeclared']))
            for name,total,parts in equations:
                if all(f[k] is not None for k in [total]+parts) and f[total]!=sum(f[k] for k in parts):identities.append(dict(county=r['county'],native_label=r['native_label'],source_locator=r['source_locator'],equation=name,reported=f[total],component_sum=sum(f[k] for k in parts)))
        state=next((r for r in cs if r['scope']=='state_summary'),None)
        sums={k:sum(r['fields'][k] for r in ns if r['fields'][k] is not None) for k in fields}
        reconciliation.append(dict(source_id=sid,native_rows=len(ns),county_count=len({r['county'] for r in ns}),numeric_native_sums=sums,state_control=state['fields'] if state else None,county_control_disagreements=issues,native_identity_disagreements=identities,null_fields=sum(v is None for r in ns for v in r['fields'].values()),numeric_sums_do_not_impute_nulls=True))
    for sid,meta in CONTESTS.items():
        ns=native(sid);state=next(c for c in controls if c['source_id']==sid and c['scope']=='state_summary')
        for level,group in [('state',[state])]+[('county',[next(c for c in controls if c['source_id']==sid and c['county']==county and c['scope']=='county_footer')]) for county in COUNTIES]:
            r=group[0];f=r['fields'];a=f[meta['A']];b=f[meta['B']];pair=a+b;total=sum(f[k] for k in meta['candidates'] if f[k] is not None)
            out=dict(source_id=sid,year=meta['year'],scope=level,county=r['county'],county_fips=FIPS.get(r['county']),A=meta['A'],B=meta['B'],A_votes=a,B_votes=b,pair_votes=pair,reported_candidate_generic_total=total,other_reported=total-pair,pair_participation=pair/total,A_pair_share=a/pair,pair_margin_pp=100*(a-b)/pair,all_reported_margin_pp=100*(a-b)/total,fields=f,source_locator=r['source_locator'])
            (states if level=='state' else counties).append(out)
        for r in ns:
            g=geo(r,meta['year']);f=r['fields'];a=f[meta['A']];b=f[meta['B']];pair=a+b if a is not None and b is not None else None
            total=sum(f[k] for k in meta['candidates'] if f[k] is not None)
            q=a/pair if pair else None
            row={**{k:v for k,v in g.items() if k!='source_locator'},'source_id':sid,'year':meta['year'],'election_date':meta['date'],'contest':meta['contest'],'comparison_role':meta['role'],
                 'A_key':meta['A'],'A_name':NAMES[meta['A']][0],'A_party':NAMES[meta['A']][1],'B_key':meta['B'],'B_name':NAMES[meta['B']][0],'B_party':NAMES[meta['B']][1],
                 'A_votes':a,'B_votes':b,'pair_votes':pair,'reported_candidate_generic_total':total,'candidate_fields_complete':all(f[k] is not None for k in meta['candidates']),
                 'A_pair_share':q,'pair_margin_pp':100*(2*q-1) if q is not None else None,
                 'all_reported_margin_pp':100*(a-b)/total if pair and total else None,
                 'pair_participation':pair/total if pair is not None and total else None,
                 'source_locator_json':json.dumps(r['source_locator'],sort_keys=True),
                 **{k:v for k,v in f.items()},'raw_fields_json':json.dumps(r['raw_fields'],ensure_ascii=False,sort_keys=True)}
            row['outcome_pair']=('A' if a>b else 'B' if b>a else 'tie') if pair is not None else 'unavailable'
            rows.append(row)
            for key in meta['candidates']:
                candidates.append(dict(source_id=sid,geography_key=g['geography_key'],county=r['county'],native_label=r['native_label'],candidate_key=key,name=NAMES[key][0],party_or_scope=NAMES[key][1],votes=f[key],raw_value=r['raw_fields'][key],source_locator=r['source_locator']))
    csvout(STATE/'data/county-baselines.csv',rows)
    dump(HERE/'candidate-identities.json',NAMES);dump(HERE/'state-baselines.json',states);dump(HERE/'county-controls.json',counties)
    from extract import gzjson
    gzjson(HERE/'candidates.jsonl.gz',candidates);dump(HERE/'reconciliation.json',reconciliation)
    # Exact priority on 2024 native leaves only. Missing numeric cells stay null;
    # reported subtotal is an explicit aggregation, not an invented cell value.
    leaves=[]
    for r in native(PRES):
        g=geo(r,2024);f=r['fields'];match=cid.get((g['county_fips'],g['municipal_parent_label']));g['parent_cousub_geoid_2020']=match[0] if match else None
        if match and match[1] and g['ward'] is None:g['kind']='city_total_only_native_row'
        g['reported_candidate_write_in_votes']=sum(f[k] for k in CONTESTS[PRES]['candidates'] if f[k] is not None)
        leaves.append({**g,**f,'source_id':PRES,'numeric_fields_complete':all(x is not None for x in f.values())})
    leaves.sort(key=lambda r:(-r['reported_candidate_write_in_votes'],r['county_fips'],r['native_label'].strip()))
    total=sum(r['reported_candidate_write_in_votes'] for r in leaves);cum=0;cross=None
    for i,r in enumerate(leaves,1):
        cum+=r['reported_candidate_write_in_votes'];r.update(rank=i,cumulative_votes=cum)
        if cross is None and 5*cum>=4*total:cross=i
    for r in leaves:r.update(top15=r['rank']<=15,minimum80=r['rank']<=cross,priority=r['rank']<=max(15,cross))
    priority=dict(schema_version='nh-partisanship-priority-1.0',source_id=PRES,denominator=total,unit_count=len(leaves),sort='descending reported candidate+generic subtotal; county FIPS; trimmed literal label Unicode',all_units=leaves,full_ordered_keys=[r['geography_key'] for r in leaves],ordered_priority_keys=[r['geography_key'] for r in leaves if r['priority']],top15_votes=sum(r['reported_candidate_write_in_votes'] for r in leaves[:15]),minimum80_count=cross,minimum80_votes=leaves[cross-1]['cumulative_votes'],preceding_votes=leaves[cross-2]['cumulative_votes'],crossing_key=leaves[cross-1]['geography_key'],coordinator_acceptance_authority='data/coordinator-priority-acceptance.json',worker_acceptance_authority=False,current_geography_approval=False)
    dump(HERE/'priority-set.json',priority)
    csvout(HERE/'priority.csv',[{**{k:v for k,v in r.items() if k!='source_locator'},'source_locator_json':json.dumps(r['source_locator'],sort_keys=True)} for r in leaves])
    hierarchy=[]
    for sid,meta in CONTESTS.items():
        gs=[geo(r,meta['year']) for r in native(sid)]
        for county in COUNTIES:
            children=[g for g in gs if g['county']==county]
            parents=[]
            for parent in dict.fromkeys(g['municipal_parent_label'] for g in children):
                ls=[g for g in children if g['municipal_parent_label']==parent]
                assert not (len(ls)>1 and any(x['ward'] is None for x in ls))
                parents.append(dict(parent_label=parent,is_accounting_leaf=len(ls)==1 and ls[0]['ward'] is None,children=ls))
            hierarchy.append(dict(source_id=sid,county=county,county_fips=FIPS[county],county_is_control_not_leaf=True,parents=parents))
    dump(HERE/'hierarchy.json',hierarchy)
    peer_audit(leaves,priority)
    vintage_diff(inv,controls)
    print(json.dumps(dict(baseline_rows=len(rows),native_per_contest=320,priority_count=cross,priority_votes=priority['minimum80_votes'],all_votes=total)))

def peer_audit(leaves,priority):
    peer=STATE/'data/county-turnout.csv';proot=STATE/'data/turnout';diff=[];checks=[]
    with peer.open() as f:prs=list(csv.DictReader(f))
    assert len(prs)==len(leaves)
    for a,b in zip(leaves,prs):
        for k in ['rank','geography_key','county','county_fips','native_label','kind','municipal_parent_label','ward','parent_cousub_geoid_2020','reported_candidate_write_in_votes','harris_walz','trump_vance','oliver_ter_maat','stein_ware','generic_write_ins','undervotes','overvotes','cumulative_votes','top15','minimum80','priority','source_id']:
            av=a.get(k);av='' if av is None else str(av)
            if av!=b[k]:diff.append(dict(rank=a['rank'],field=k,own=av,peer=b[k]))
        for k,v in [('source_sheet',a['source_locator']['sheet']),('source_row',str(a['source_locator']['source_row']))]:
            if b[k]!=v:diff.append(dict(rank=a['rank'],field=k,own=v,peer=b[k]))
        expected='complete_numeric' if all(a[k] is not None for k in CONTESTS[PRES]['candidates']) else 'numeric_subtotal_only_blank_fields_retained'
        if b['candidate_field_completeness']!=expected:diff.append(dict(rank=a['rank'],field='candidate_field_completeness',own=expected,peer=b['candidate_field_completeness']))
        for k,v in [('share_numerator',a['reported_candidate_write_in_votes']),('share_denominator',priority['denominator'])]:
            if int(b[k])!=v:diff.append(dict(rank=a['rank'],field=k,own=v,peer=b[k]))
    p=json.loads((proot/'priority-set.json').read_text())
    for field in ['full_ordered_keys','ordered_priority_keys']:
        if priority[field]!=p[field]:diff.append(dict(field=field,own='different',peer='different'))
    # Source-scoped reconciliation; no cross-year or across-document identity join.
    source_diffs=[];raw_diffs=[];type_diffs=[];field_count=0;raw_count=0;type_count=0
    for f in sorted((HERE/'native').glob('*.jsonl.gz')):
        pf=proot/'native'/f.name
        if not pf.exists():continue
        own=loadgz(f);other=loadgz(pf)
        def ident(r):return (r['county'],r['native_label'],json.dumps(r['source_locator'],sort_keys=True))
        # Peer omits A for ordinary rows; compare sheet/row/page/line plus explicit
        # side-by-side G when present. Keep original locators in both packages.
        def key(r):
            loc=r['source_locator'];return (r['county'],r['native_label'],loc.get('sheet'),loc.get('source_row'),loc.get('page'),loc.get('line'),loc.get('label_column',loc.get('source_column_start','A')))
        def fields(r,scope='fields'):return {('ballots_total' if k=='ballots_cast' else k):v for k,v in r[scope].items()}
        oo={key(r):fields(r) for r in own};pp={key(r):fields(r) for r in other}
        for k in oo.keys()|pp.keys():
            if oo.get(k)!=pp.get(k):source_diffs.append(dict(source_id=f.stem,identity=k,own=oo.get(k),peer=pp.get(k)))
        own_raw={key(r):fields(r,'raw_fields') for r in own};peer_raw={key(r):fields(r,'raw_fields') for r in other}
        for k in own_raw.keys()|peer_raw.keys():
            if own_raw.get(k)!=peer_raw.get(k):raw_diffs.append(dict(source_id=f.stem,identity=k,own=own_raw.get(k),peer=peer_raw.get(k)))
        field_count+=sum(len(x) for x in oo.values());raw_count+=sum(len(x) for x in own_raw.values())
        # Native administrative records retain whole-row type evidence in raw/.
        # Compare the original BIFF types in each field's actual source column.
        rawrows=loadgz(HERE/'raw'/f.name);byloc={(r.get('sheet'),r.get('source_row')):r for r in rawrows}
        own_by_key={key(r):r for r in own}
        for r in other:
            if 'cell_types' not in r:continue
            o=own_by_key[key(r)];loc=o['source_locator'];rawrow=byloc[(loc.get('sheet'),loc.get('source_row'))]
            if isinstance(o.get('cell_types'),dict):types=list(o['cell_types'].values())
            else:
                offset=6 if loc.get('label_column')=='G' else 0
                types=rawrow['cell_types'][offset+1:offset+1+len(o['fields'])]
            type_count+=len(types)
            if types!=r['cell_types']:type_diffs.append(dict(source_id=f.stem,identity=key(r),own=types,peer=r['cell_types']))
        checks.append(dict(source_id=f.name.removesuffix('.jsonl.gz'),own_count=len(own),peer_count=len(other),full_candidate_method_fields_equal=oo==pp))
    audit=dict(peer_csv_path=str(peer.relative_to(STATE)),peer_csv_sha256=sha(peer.read_bytes()),peer_priority_sha256=sha((proot/'priority-set.json').read_bytes()),priority_field_disagreements=diff,source_native_checks=checks,source_native_disagreements=source_diffs,parsed_fields_compared=field_count,raw_values_compared=raw_count,BIFF_types_compared=type_count,raw_value_disagreements=raw_diffs,BIFF_type_disagreements=type_diffs,priority_arithmetic_equal=not diff,coordinator_acceptance_authority='data/coordinator-priority-acceptance.json',worker_acceptance_authority=False,unverified_geography_crosswalk='No historical or November2026 boundary equivalence, clerk authority or current precinct approval follows from these comparisons.')
    dump(HERE/'peer-reconciliation.json',audit)

def vintage_diff(inv,controls):
    groups=[['sos-archived-2022-ge-us-senator'+x+'-xls' for x in ['','-1','-2','-5']],['2024-ge-president-xls','2024-ge-president-0-xls',PRES],['2022-ge-ballots-cast-xls','2022-ge-ballots-cast-2-xls','2022-ge-ballots-cast-3-xls'],['2024-ge-ballots-cast-'+x+'-xls' for x in ['0','1','6','11','14']],['2022-ge-names-on-checklist-1-xlsx','2022-ge-names-on-checklist-2-xlsx'],['2024-ge-names-on-checklist-4-xlsx','2024-ge-names-on-checklist-7-xlsx']]
    out=[]
    for group in groups:
        base=group[-1];bn=native(base);bs={(r['county'],r['native_label'].strip()):r for r in bn}
        for sid in group[:-1]:
            ns=native(sid);diff=[]
            for r in ns:
                k=(r['county'],r['native_label'].strip());other=bs.get(k)
                if not other:diff.append(dict(identity=k,scope='literal_label_not_matched_no_imputation'));continue
                for f,v in r['fields'].items():
                    if v!=other['fields'].get(f):diff.append(dict(county=r['county'],native_label=r['native_label'],field=f,source_value=v,comparison_value=other['fields'].get(f),source_locator=r['source_locator'],comparison_locator=other['source_locator']))
            st=next(x for x in controls if x['source_id']==sid and x['scope']=='state_summary')
            bst=next(x for x in controls if x['source_id']==base and x['scope']=='state_summary')
            out.append(dict(source_id=sid,comparison_id=base,state_source=st['fields'],state_comparison=bst['fields'],native_differences=diff,interpretation='Literal source-version field comparison only; suffix/capture/Last-Modified do not establish legal amendment chronology or geographic equivalence.'))
    dump(HERE/'vintage-disagreements.json',out)

if __name__=='__main__':run()
