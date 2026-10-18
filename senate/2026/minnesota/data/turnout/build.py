"""Offline rankings and exact dispatch contract from independent extraction."""
import csv, gzip, json
from decimal import Decimal, localcontext
from pathlib import Path
from extract import HERE, STATS, csvwrite, dump, sha

def readcsv(name):
    p=HERE/name
    with (gzip.open(p,'rt',newline='') if p.suffix=='.gz' else p.open(newline='')) as f:return list(csv.DictReader(f))
def ratio(n,d):
    with localcontext() as c:
        c.prec=35;return str(Decimal(n)/Decimal(d))
def pct(n,d,digits=8): return f'{Decimal(n)*100/Decimal(d):.{digits}f}'
def rank(rows,field,key):
    ordered=sorted(rows,key=lambda r:(-int(r[field]),r[key]));total=sum(int(r[field]) for r in ordered)
    assert total>0
    cum=0;out=[]
    for i,r in enumerate(ordered,1):
        cum+=int(r[field]);out.append(dict(key=r[key],rank=i,votes=int(r[field]),cumulative_votes=cum,share=ratio(int(r[field]),total),cumulative_share=ratio(cum,total)))
    k=next(i for i,r in enumerate(out,1) if 5*r['cumulative_votes']>=4*total)
    return dict(denominator=total,field=field,tie_break='ascending exact key after descending integer count',unit_count=len(out),top15_votes=sum(r['votes'] for r in out[:15]),
                top15_share=ratio(sum(r['votes'] for r in out[:15]),total),minimum80_count=k,minimum80_votes=out[k-1]['cumulative_votes'],minimum80_share=ratio(out[k-1]['cumulative_votes'],total),
                previous_count=k-1,previous_votes=out[k-1]['cumulative_votes']-out[k-1]['votes'],crossing_key=out[k-1]['key'],
                priority_keys=[r['key'] for r in out[:max(15,k)]],remainder_votes=total-out[k-1]['cumulative_votes'],order=out)

def build():
    controls=json.loads((HERE/'source/primary-controls.json').read_text())
    extracted=json.loads((HERE/'source/extraction-controls.json').read_text())
    meta=json.loads((HERE/'source/workbook-context.json').read_text())
    counties={y:readcsv(f'county-controls-{y}.csv') for y in [2024,2022,2020]}
    native={y:readcsv(f'native-{y}.csv.gz') for y in counties}
    municipal=readcsv('municipal-controls-2024.csv')
    catalog=[]
    for y in counties:
        totals=extracted[str(y)]['totals']
        for p,cs in controls[str(y)]['contests'].items():
            assert set(cs)=={k for k in totals if k.startswith(p) and k!=p+'TOTAL'}
            assert totals[p+'TOTAL']==sum(c[2] for c in cs.values())
            for field,(name,party,votes) in cs.items():
                assert votes==totals[field]
                catalog.append(dict(election_year=y,contest_prefix=p,source_field=field,candidate=name,source_party_label=party,
                    source_party_code=field[len(p):],analytical_group='D' if field==p+'DFL' else ('R' if field==p+'R' else 'other'),
                    write_in_scope='registered and non-registered write-ins combined; named valid allocation unavailable' if field==p+'WI' else 'filed candidate',
                    primary_statewide_control=votes,native_sum=totals[field],difference=totals[field]-votes,control_url=controls[str(y)]['results_url']))
        for field,value in controls[str(y)]['statistics'].items():assert value==totals[field]
    csvwrite(HERE/'candidate-reconciliation.csv',catalog,list(catalog[0]))
    primary=rank(counties[2024],'USSENTOTAL','county_key');total=primary['denominator'];k=primary['minimum80_count'];priority=set(primary['priority_keys'])
    idx={y:{r['county_key']:r for r in rs} for y,rs in counties.items()}
    name={r['county_key']:r['COUNTYNAME'] for r in counties[2024]}
    metrics={}
    for y in counties:
        for p in controls[str(y)]['contests']:metrics[f'{y}_{p}']=rank(counties[y],p+'TOTAL','county_key')
        for f in ['TOTVOTING','REG7AM','EDR']:metrics[f'{y}_{f}']=rank(counties[y],f,'county_key')
    dump(HERE/'sensitivity.json',metrics)
    named_rows=list(csv.DictReader((HERE/'source/named-writeins-2020.csv').open()))
    named_fields={name:f'2020_USSEN_named_report_candidate_{i}' for i,name in enumerate(dict.fromkeys(r['source_candidate_label'] for r in named_rows),1)}
    flat=[]
    for r in primary['order']:
        key=r['key'];a=dict(rank=r['rank'],county=name[key],county_fips=idx[2024][key]['county_fips'],source_county_code=idx[2024][key]['COUNTYCODE'],county_key=key,
                           senate_2024_total=r['votes'],state_share=r['share'],cumulative_votes=r['cumulative_votes'],cumulative_share=r['cumulative_share'],top15=int(r['rank']<=15),minimum80=int(r['rank']<=k))
        for y in counties:
            source=idx[y][key];a[f'native_units_{y}']=source['native_units']
            for field in source:
                if field in extracted[str(y)]['totals']: a[f'{y}_{field}']=int(source[field])
            for p in controls[str(y)]['contests']:
                a[f'{y}_{p}_D_group']=int(source[p+'DFL']);a[f'{y}_{p}_R_group']=int(source[p+'R'])
                a[f'{y}_{p}_other_including_generic_writein']=int(source[p+'TOTAL'])-int(source[p+'DFL'])-int(source[p+'R'])
                for category in ['blank','undervote','overvote','valid_named_writein']:a[f'{y}_{p}_{category}']=None
                a[f'{y}_{p}_unavailable_categories_status']='not provided by selected workbook'
        a['method_warning_2024']='Notes warning: some mail precincts SIGNATURES high/AB_MB low' if name[key] in ['Clearwater','Swift','Winona'] else ''
        nr=[t for t in named_rows if t['county_fips']==a['county_fips']]
        assert len(nr)==6
        for t in nr:a[named_fields[t['source_candidate_label']]]=int(t['votes'])
        a['2020_USSEN_named_writein_report_total']=sum(int(t['votes']) for t in nr)
        a['2020_USSEN_generic_minus_named_scope_gap']=a['2020_USSENWI']-a['2020_USSEN_named_writein_report_total']
        a['2020_USSEN_named_report_scope']='separate overlapping PDF appendix; no native allocation; never add to generic votes'
        flat.append(a)
    csvwrite(HERE.parent/'county-turnout.csv',flat,list(flat[0]))
    nr=rank(native[2024],'USSENTOTAL','native_key')
    mr=rank(municipal,'USSENTOTAL','derived_key')
    for label,ranking,rs,key in [('native',nr,native[2024],'native_key'),('municipal',mr,municipal,'derived_key')]:
        ix={r[key]:r for r in rs};out=[]
        for r in ranking['order']:
            a=dict(r);a.update(ix[r['key']]);a['in_minimum80']=int(r['rank']<=ranking['minimum80_count']);a['in_top15']=int(r['rank']<=15);out.append(a)
        csvwrite(HERE/f'{label}-2024-ranked.csv.gz',out,list(out[0]))
    # All parent counties and each native constituent are explicit. County ranks
    # and leaf ranks are alternative disjoint views, never summed together.
    parent_entries=[]
    for r in primary['order']:
        key=r['key'];entry=dict(r,name=name[key],county_fips=idx[2024][key]['county_fips'],source_county_code=idx[2024][key]['COUNTYCODE'],in_priority=key in priority,native_constituents={})
        for y,units in native.items():
            entry['native_constituents'][str(y)]=[
                {f:u[f] for f in ['native_key','source_id','source_sheet','source_row','VTDID','PCTCODE','PCTNAME','MCDNAME','WARD','MAILBALLOT','unit_kind','method_warning','current_2026_equivalence']} |
                dict(candidate_votes=int(u['MNGOVTOTAL' if y==2022 else 'USSENTOTAL']),central_absentee_candidate_split='unavailable: workbook assigns no separate candidate-method rows',native_municipal_id=None)
                for u in units if u['county_key']==key]
        entry['current_2026_constituents']={'status':'unavailable/unapproved','reason':'Historical native IDs are not a verified November 2026 crosswalk'}
        parent_entries.append(entry)
    for ranking in [nr,mr]:
        ranking['complete_ordered_keys']=[r['key'] for r in ranking.pop('order')]
    contract=dict(schema_version='mn-turnout-priority/1.0',state='MN',election='2024-11-05 general',contest='U.S. Senator (Class I, other seat)',
                  denominator_scope='All reported filed-candidate votes plus generic registered/nonregistered write-ins; not ballots cast',source_id='sos-2024-precinct-original',
                  source_sha256=meta['2024']['source_sha256'],acceptance='pending independent peer and coordinator review',
                  coordinator_acceptance_path='data/coordinator-priority-acceptance.json',
                  ranking_geography='87 disjoint source county parents, FIPS from workbook Counties sheet; all native constituents retained',
                  hierarchy='Count each leaf exactly once within its county. Municipal/ward/county/state aggregations overlap their leaves and are alternative views, never additive.',
                  statewide_candidate_votes=total,top15={f:primary[f] for f in ['top15_votes','top15_share']},
                  minimum80={f:primary[f] for f in ['minimum80_count','minimum80_votes','minimum80_share','previous_count','previous_votes','crossing_key','remainder_votes']},
                  ordered_priority_keys=primary['priority_keys'],complete_ordered_county_keys=[r['key'] for r in primary['order']],remainder_keys=[r['key'] for r in primary['order'][k:]],
                  county_order=parent_entries,native_2024_ranking=nr,municipal_2024_ranking=mr,
                  unavailable_cases=[
                      'No source-native municipality ID in these result sheets; exact MCDNAME is retained, scoped to year/county, without a legal crosswalk claim.',
                      'No separate central absentee/early-vote candidate reporting identities in these workbooks; precinct totals already include the source allocation. No invented central rows.',
                      'No polling-site, vote-center, split-ballot-style, method-specific candidate, blank, undervote, overvote, or valid-named write-in allocation in the selected workbooks.',
                      'Source VTDID means Vote Tabulation District ID; it is not an approved Census VTD or November 2026 geometry/identity crosswalk.',
                      'Literal no data and blank ward/district/equipment values survive in native files; zero-vote source units remain in complete orders.'])
    freeze=HERE/'source/frozen-contract.json'
    if freeze.exists():
        expected=json.loads(freeze.read_text())
        encoded=(json.dumps(contract,ensure_ascii=False,indent=2)+'\n').encode()
        assert sha(encoded)==expected['sha256'] and len(encoded)==expected['bytes'],'Frozen dispatch contract would change'
        assert sha((HERE/'priority-set.json').read_bytes())==expected['sha256']
    else:
        dump(HERE/'priority-set.json',contract)
    # Concise human tables embedded into the hand-authored report template.
    def cnam(keys): return ', '.join(name[t] for t in keys)
    lines=[]
    lines+=['| Rank | County (FIPS) | Senate 2024 | State % | Cumulative % | Governor 2022 | Senate 2020 | 2024 ballots |','| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in primary['order']:
        key=r['key'];lines.append(f"| {r['rank']} | {name[key]} ({idx[2024][key]['county_fips']}) | {r['votes']:,} | {pct(r['votes'],total,4)} | {pct(r['cumulative_votes'],total,4)} | {int(idx[2022][key]['MNGOVTOTAL']):,} | {int(idx[2020][key]['USSENTOTAL']):,} | {int(idx[2024][key]['TOTVOTING']):,} |")
    (HERE/'county-ranking-table.md').write_text('\n'.join(lines)+'\n')
    lines=['| County-level denominator | State total | Top 15 votes/count | Top 15 % | Minimum 80% count / votes | Prior cumulative | Crossing county |','| --- | ---: | ---: | ---: | --- | ---: | --- |']
    for metric,r in metrics.items():
        lines.append(f"| {metric} | {r['denominator']:,} | {r['top15_votes']:,} | {pct(r['top15_votes'],r['denominator'])} | {r['minimum80_count']} / {r['minimum80_votes']:,} | {r['previous_votes']:,} | {name[r['crossing_key']]} |")
    (HERE/'sensitivity-table.md').write_text('\n'.join(lines)+'\n')
    summary=dict(top15_names=cnam([r['key'] for r in primary['order'][:15]]),priority_names=cnam(primary['priority_keys']),**{k:v for k,v in primary.items() if k!='order'},
                 native_top15_share=nr['top15_share'],native_min80_count=nr['minimum80_count'],native_min80_votes=nr['minimum80_votes'],
                 municipal_top15_share=mr['top15_share'],municipal_min80_count=mr['minimum80_count'],municipal_min80_votes=mr['minimum80_votes'])
    dump(HERE/'ranking-summary.json',summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':build()
