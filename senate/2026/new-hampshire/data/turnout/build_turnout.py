#!/usr/bin/env python3
"""Offline native-unit calculations from independently extracted originals.

No county substitution, missing-to-zero candidate recoding, geometry join,
rescaling or clerical-authority inference. Run extract.py first.
"""
import collections
import csv
import gzip
import io
import json
import pathlib
import re
import sys
sys.dont_write_bytecode = True
from urllib.parse import quote
from extract import ROOT, dump, gzjsonl, sha

PRES = 'sos-2024-president-archived-original'
SEN22 = 'sos-archived-2022-ge-us-senator-5-xls'
SEN20 = 'sos-2020-senate-archived-original'
COUNTIES = ['Belknap','Carroll','Cheshire','Coos','Grafton','Hillsborough','Merrimack','Rockingham','Strafford','Sullivan']
CF = {c:'33'+str(1+2*i).zfill(3) for i,c in enumerate(COUNTIES)}


def readrows(sid):
    return [json.loads(x) for x in gzip.decompress((ROOT/'extracts'/f'{sid}-rows.jsonl.gz').read_bytes()).splitlines()]


def num(v):
    if isinstance(v,(int,float)):
        assert v == int(v) and v >= 0
        return int(v)
    if isinstance(v,str) and re.fullmatch(r'[\d,]+',v): return int(v.replace(',',''))
    return None


def numeric_sum(values):
    return sum(x for v in values if (x:=num(v)) is not None)


def cid(x):
    for a,b in [('Harris','harris_walz'),('Trump','trump_vance'),('Oliver','oliver_ter_maat'),('Stein','stein_ware'),('Undervotes','undervotes'),('Overvotes','overvotes'),('Write-Ins','generic_write_ins'),('Bolduc','bolduc'),('Hassan','hassan'),('Kauffman','kauffman'),('Scatter','scatter')]:
        if a.lower() in str(x).lower(): return b
    raise ValueError(x)


def record(r,county,fields,values,label=None):
    label = r['values'][0] if label is None else label
    return dict(source_id=r['source_id'], county=county, county_fips=CF.get(county),
                native_label=label, sheet=r.get('sheet'), source_row=r.get('source_row'),
                page=r.get('page'), line=r.get('line'),
                source_native_id=None, native_id_status='No numeric reporting ID supplied; source label and locator retained.',
                fields=dict(zip(fields,[num(x) for x in values])), raw_fields=dict(zip(fields,values)),
                source_locator={k:r[k] for k in ['sheet','source_row','source_column_start','page','line'] if k in r},
                **({'cell_types':r['cell_types'][1:len(fields)+1]} if 'cell_types'in r else {}))


def contest_xls(sid):
    rr=readrows(sid); summary={}; native=[]; footers=[]; fields=None; county=None
    for r in rr:
        v=r['values']; label=str(v[0]).strip() if v else ''
        if label=='Summary By Counties':
            fields=[cid(x)for x in v[1:] if str(x).strip()];assert len(fields)==len(set(fields));continue
        if label.endswith(' County') and label[:-7] in COUNTIES:
            county=label[:-7]; fields=[cid(x)for x in v[1:] if str(x).strip()];assert len(fields)==len(set(fields));continue
        if fields is None or not label:continue
        if county is None:
            if label in COUNTIES or label=='TOTALS': summary[label]=record(r,label if label in COUNTIES else None,fields,v[1:len(fields)+1])
        elif label=='TOTALS':
            footers.append(record(r,county,fields,v[1:len(fields)+1]));county=None
        else:native.append(record(r,county,fields,v[1:len(fields)+1]))
    assert len(native)==320 and len(footers)==10,(sid,len(native),len(footers))
    return dict(source_id=sid,native=native,footers=footers,summary=summary)


def contest_pdf(sid,fields):
    lines=[json.loads(x) for x in gzip.decompress((ROOT/'extracts'/f'{sid}-lines.jsonl.gz').read_bytes()).splitlines()]
    native=[];summary={};footers=[];county=None
    pat=re.compile(r'^(.*?)\s{2,}([\d,]+|-)\s+([\d,]+|-)\s+([\d,]+|-)(?:\s+([\d,]+|-))?\s*$')
    for r in lines:
        txt=r['text']
        cm=re.match(r'^('+ '|'.join(COUNTIES)+r') County(?:\s|$)',txt)
        if cm:county=cm[1];continue
        m=pat.match(txt)
        if not m:continue
        label=m[1].strip();vals=[v if v is not None else '' for v in m.groups()[1:]]
        rr=dict(r,values=[label]+vals)
        if county:
            out=record(rr,county,fields,vals,label)
            if label=='TOTALS':footers.append(out);county=None
            else:native.append(out)
        elif label in COUNTIES or label=='TOTALS':summary[label]=record(rr,label if label in COUNTIES else None,fields,vals,label)
    assert len(native)==320 and len(footers)==10,(sid,len(native),len(footers))
    return dict(source_id=sid,native=native,footers=footers,summary=summary)


def volume(sid,checklist=False):
    rr=readrows(sid);native=[];footers=[];summary={};county=None;header=None
    if sid=='2020-ge-ballots-cast-xls':
        expanded=[]
        for sheet in dict.fromkeys(r['sheet']for r in rr):
            sr=[r for r in rr if r['sheet']==sheet]
            offsets=[0,6]if any(len(r['values'])>6 and 'COUNTY/BALLOTS CAST'in str(r['values'][6])for r in sr)else [0]
            for offset in offsets:
                for r in sr:
                    expanded.append(dict(r,values=r['values'][offset:offset+4],cell_types=r['cell_types'][offset:offset+4],source_column_start='G'if offset else 'A'))
        rr=expanded
    fields=(['republican','democratic','undeclared','checklist_total','polling_place_registered_total'] if sid.startswith('2020') else ['republican','democratic','undeclared','checklist_total','polling_place_registered_republican','polling_place_registered_democratic','polling_place_registered_undeclared','polling_place_registered_total']) if checklist else ['regular','absentee','ballots_total']
    for r in rr:
        v=r['values'];label=str(v[0]).strip() if v else ''
        cm=re.match(r'^('+ '|'.join(COUNTIES)+r') COUNTY/',label,re.I)
        if cm:county=next(c for c in COUNTIES if c.lower()==cm[1].lower());header=None;continue
        if len(v)>1 and v[1] in ['Republican','Regular']:
            header=[i for i,x in enumerate(v) if x!='' and i>0]
            continue
        if not label or header is None:continue
        if checklist and len(header)==9:header=[1,2,3,4,6,7,8,9]
        inds=header[:len(fields)]
        if len(inds)!=len(fields):continue
        vals=[v[i] if i<len(v) else '' for i in inds]
        if county:
            if label.lower() in ['totals','total']:
                footers.append(record(r,county,fields,vals));county=None;header=None
            elif any(num(x)is not None for x in vals):native.append(record(r,county,fields,vals))
        elif label.removesuffix(' County') in COUNTIES or label.lower()in ['totals','total']:
            c=label.removesuffix(' County');summary[c if c in COUNTIES else 'TOTALS']=record(r,c if c in COUNTIES else None,fields,vals)
    assert len(footers)==10,(sid,len(native),len(footers))
    return dict(source_id=sid,native=native,footers=footers,summary=summary)


def reconcile(ds):
    fields=list(ds['summary']['TOTALS']['fields']);audit=[]
    for c in COUNTIES:
        rows=[r for r in ds['native'] if r['county']==c]
        ff=[r for r in ds['footers']if r['county']==c];assert len(ff)==1
        sums={k:numeric_sum(r['raw_fields'][k]for r in rows)for k in fields}
        footer=ff[0]['fields'];summary=ds['summary'][c]['fields']
        audit.append(dict(county=c,native_rows=len(rows),numeric_sums=sums,footer=footer,summary=summary,
                          detail_minus_footer={k:sums[k]-footer[k] if footer[k] is not None else None for k in fields},
                          footer_minus_summary={k:footer[k]-summary[k]if footer[k]is not None and summary[k]is not None else None for k in fields}))
    sums={k:numeric_sum(r['raw_fields'][k]for r in ds['native'])for k in fields}
    state=ds['summary']['TOTALS']['fields']
    missing=[dict(county=r['county'],native_label=r['native_label'],fields=[k for k,v in r['fields'].items()if v is None],locator=r['source_locator'])for r in ds['native']if any(v is None for v in r['fields'].values())]
    return dict(source_id=ds['source_id'],native_rows=len(ds['native']),state=state,native_numeric_sums=sums,
                native_minus_state={k:sums[k]-state[k]if state[k]is not None else None for k in fields},counties=audit,missing_fields=missing)


def key(r):
    return 'nh-2024-pres:'+r['county_fips']+':'+quote(r['native_label'].strip(),safe='')


def ranking(rows,volume_field):
    order=sorted(rows,key=lambda r:(-r[volume_field],r['county_fips'],r['native_label'].strip()))
    total=sum(r[volume_field] for r in order);cum=0;cross=None;ranked=[]
    assert total>0
    for i,r in enumerate(order,1):
        cum+=r[volume_field];out=dict(r,rank=i,cumulative_votes=cum,share_numerator=r[volume_field],share_denominator=total)
        ranked.append(out)
        if cross is None and 5*cum>=4*total:cross=i
    top15=sum(r[volume_field]for r in ranked[:15]);crossvotes=ranked[cross-1]['cumulative_votes'];preceding=ranked[cross-2]['cumulative_votes']
    return dict(denominator=total,unit_count=len(order),volume_field=volume_field,
                top15=dict(count=15,votes=top15,denominator=total,percent=100*top15/total),
                minimum80=dict(count=cross,votes=crossvotes,denominator=total,percent=100*crossvotes/total,
                               preceding_count=cross-1,preceding_votes=preceding,crossing_key=ranked[cross-1].get('geography_key'),crossing_geography=ranked[cross-1]['native_label'].strip()),
                remainder=dict(count=len(order)-cross,votes=total-crossvotes,denominator=total),ordered=ranked)


def csvout(path,rows):
    with (ROOT/path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    datasets={}
    for sid in [PRES,'2024-ge-president-xls','2024-ge-president-0-xls',SEN22,'sos-archived-2022-ge-us-senator-xls','sos-archived-2022-ge-us-senator-1-xls','sos-archived-2022-ge-us-senator-2-xls']:
        datasets[sid]=contest_xls(sid)
    datasets[SEN20]=contest_pdf(SEN20,['messner','shaheen','odonnell','scatter'])
    p22='sos-archived-2022-ge-us-senator-remediated-1-pdf'
    datasets[p22]=contest_pdf(p22,['bolduc','hassan','kauffman','scatter'])
    for sid in ['2020-ge-ballots-cast-xls','2020-ge-names-on-checklist-xlsx','2024-ge-ballots-cast-14-xls','2024-ge-ballots-cast-6-xls','2022-ge-ballots-cast-xls','2022-ge-ballots-cast-2-xls','2022-ge-ballots-cast-3-xls','2024-ge-names-on-checklist-7-xlsx','2022-ge-names-on-checklist-1-xlsx','2022-ge-names-on-checklist-2-xlsx']:
        datasets[sid]=volume(sid,'checklist'in sid)
    for p in sorted((ROOT/'extracts').glob('2024-ge-*-rows.jsonl.gz')):
        sid=p.name.removesuffix('-rows.jsonl.gz')
        if ('ballots-cast'in sid or 'names-on-checklist'in sid)and sid not in datasets:datasets[sid]=volume(sid,'checklist'in sid)
    audits=[reconcile(d)for d in datasets.values()]
    dump('reconciliation.json',audits)
    for sid,ds in datasets.items():gzjsonl('native/'+sid+'.jsonl.gz',ds['native'])
    dump('controls.json',{sid:dict(summary=ds['summary'],footers=ds['footers'])for sid,ds in datasets.items()})
    long=[]
    for sid,ds in datasets.items():
        for r in ds['native']:
            for k,v in r['fields'].items():long.append(dict(source_id=sid,county=r['county'],native_label=r['native_label'],field=k,value=v,raw_value=r['raw_fields'][k],locator=r['source_locator']))
    gzjsonl('native-fields.jsonl.gz',long)
    primary=next(a for a in audits if a['source_id']==PRES)
    assert primary['state']==dict(harris_walz=418488,trump_vance=395523,oliver_ter_maat=4425,stein_ware=3680,undervotes=4482,overvotes=362,generic_write_ins=4073)
    assert all(x==0 for x in primary['native_minus_state'].values())
    assert all(all(x==0 for x in c['detail_minus_footer'].values()) and all(x==0 for x in c['footer_minus_summary'].values())for c in primary['counties'])
    assert next(a for a in audits if a['source_id']==SEN22)['state']==dict(hassan=332490,bolduc=275631,kauffman=12390,scatter=464)
    assert next(a for a in audits if a['source_id']==SEN20)['state']==dict(messner=326229,shaheen=450778,odonnell=18421,scatter=486)
    census=list(csv.DictReader(io.StringIO(gzip.decompress((ROOT/'source/census-nh-cousub-codes.body.gz').read_bytes()).decode()),delimiter='|'))
    for c,fips in CF.items():assert {r['STATEFP']+r['COUNTYFP']for r in census if r['COUNTYNAME']==c+' County'}=={fips}
    geography=[];rows=[]
    for r in datasets[PRES]['native']:
        label=r['native_label'].strip();m=re.fullmatch(r'(.+) Ward (\d+)',label);parent=m[1]if m else label
        # Exact county-scoped town/city identifier only. Abbreviations and
        # dissimilar administrative labels remain explicitly unmatched.
        match=[x for x in census if x['STATEFP']+x['COUNTYFP']==r['county_fips'] and x['COUSUBNAME'] in [parent+' town',parent+' city',parent+' township']]
        assert len(match)<=1
        fips=r['county_fips']+match[0]['COUSUBFP']if match else None
        kind='city_ward'if m else 'city_total_only_native_row'if match and match[0]['COUSUBNAME'].endswith(' city')else 'town_or_territory_native_row'
        g=dict(geography_key=key(r),county=r['county'],county_fips=r['county_fips'],native_label=r['native_label'],display_label=label,
               kind=kind,municipal_parent_label=parent,ward=m[2]if m else None,
               municipal_parent_key='nh-2024-parent:'+r['county_fips']+':'+quote(parent,safe=''),
               parent_cousub_geoid_2020=fips,parent_cousub_geoid_status='Exact county-scoped Census 2020 name match to explicit source parent; identifier only, no geometry/current equivalence.'if fips else 'Unavailable: source-native administrative/abbreviated label retained; no guessed crosswalk.',
               source_native_id=None,native_id_status=r['native_id_status'],source_locator=r['source_locator'],source_id=PRES,
               available_constituents=[dict(source_id=PRES,native_label=r['native_label'],source_native_id=None,locator=r['source_locator'],role='ranked accounting leaf')],
               finer_constituents_status='No finer ward/polling-site/method candidate rows supplied by this original; unavailable, never synthesized.',
               current_2026_equivalence='Unverified',clerk_authority_status='Not inferred from county/municipality name; verify actual clerk channel in official-results assignment.',
               numeric_fields_complete=all(v is not None for v in r['fields'].values()),missing_fields=[k for k,v in r['fields'].items()if v is None])
        g['reporting_status']='printed-ticket fields unpopulated; generic write-in numeric value retained; source does not explain administrative reporting arrangement' if all(r['fields'][k]is None for k in ['harris_walz','trump_vance','oliver_ter_maat','stein_ware']) else 'reported numeric counts; any individual blanks remain unavailable'
        geography.append(g)
        votes=numeric_sum(r['raw_fields'][k]for k in ['harris_walz','trump_vance','oliver_ter_maat','stein_ware','generic_write_ins'])
        rows.append(dict(g,reported_candidate_write_in_votes=votes,**r['fields'],candidate_field_completeness='complete_numeric'if all(r['fields'][k]is not None for k in ['harris_walz','trump_vance','oliver_ter_maat','stein_ware','generic_write_ins'])else 'numeric_subtotal_only_blank_fields_retained'))
    assert len({g['geography_key']for g in geography})==320
    rank=ranking(rows,'reported_candidate_write_in_votes');assert rank['denominator']==826189
    ordered=rank.pop('ordered');n=rank['minimum80']['count']
    contract=dict(schema_version='nh-turnout-priority-1.0',state='NH',election_date='2024-11-05',contest='President and Vice-President of the United States',basis_source_id=PRES,
                  status='provisional_pending_independent_peer_agreement_and_coordinator_acceptance',
                  coordinator_acceptance_authority='data/coordinator-priority-acceptance.json',
                  coordinator_acceptance_reference_scope='Path relative to the New Hampshire state directory. Only this external coordinator-owned record grants historical acceptance; the worker status remains provisional and grants no authority or current-boundary approval.',
                  worker_acceptance_authority=False,
                  denominator_definition='Reported four printed-ticket counts plus generic Write-Ins; exclude undervotes/overvotes. Numeric subtotals retain source blanks, not imputed actual zero.',
                  sort='Descending numeric candidate/write-in subtotal; ties by county FIPS then trimmed literal native label, Unicode codepoint order.',
                  coverage=dict(native_labels=320,ranked_accounting_leaves=320,county_controls=10,omitted_native_rows=0,county_summary_and_footer_rows_in_rank=0,municipal_parents_counted_with_wards=0),
                  **rank,ordered_priority_keys=[r['geography_key']for r in ordered[:max(15,n)]],
                  ordered_top15_keys=[r['geography_key']for r in ordered[:15]],ordered_minimum80_keys=[r['geography_key']for r in ordered[:n]],
                  full_ordered_keys=[r['geography_key']for r in ordered],remainder_ordered_keys=[r['geography_key']for r in ordered[n:]],
                  all_units=ordered,
                  hierarchy=dict(accounting='State > county control > explicit municipal parent > source ward leaf; unwarded town/city/territory is a leaf. Parents and controls are not additional votes.',
                                 parent_summaries=[dict(parent_key=k,constituent_keys=[r['geography_key']for r in ordered if r['municipal_parent_key']==k],counted_in_state=False)for k in sorted({r['municipal_parent_key']for r in ordered if r['kind']=='city_ward'})]))
    contract['source_native_coverage']=[]
    for sid,ds in datasets.items():
        np=ROOT/'native'/f'{sid}.jsonl.gz'
        contract['source_native_coverage'].append(dict(source_id=sid,native_rows=len(ds['native']),path='native/'+np.name,sha256=sha(np.read_bytes()),
             relationship_to_priority='Independent source/vintage roster; no cross-year geometry equivalence or abbreviated-label match inferred.',
             constituents=[dict(county=r['county'],native_label=r['native_label'],source_native_id=None,native_id_status=r['native_id_status'],locator=r['source_locator'],missing_fields=[k for k,v in r['fields'].items()if v is None])for r in ds['native']]))
    for r in ordered:
        for sid in ['2024-ge-ballots-cast-14-xls','2024-ge-names-on-checklist-7-xlsx']:
            matches=[x for x in datasets[sid]['native']if x['county']==r['county']and x['native_label'].strip()==r['native_label'].strip()]
            assert len(matches)<=1
            if matches:
                x=matches[0]
                r['available_constituents'].append(dict(source_id=sid,native_label=x['native_label'],source_native_id=None,locator=x['source_locator'],role='Separate administrative measure; literal county/label agreement only, not geometry approval.'))
            else:r['available_constituents'].append(dict(source_id=sid,native_label=None,source_native_id=None,locator=None,role='unavailable: no exact county/trimmed-label match; no abbreviation/name-similarity crosswalk'))
    dump('priority-set.json',contract)
    csvrows=[]
    for r in ordered:
        out={k:r[k]for k in ['rank','geography_key','county','county_fips','native_label','kind','municipal_parent_label','ward','parent_cousub_geoid_2020','reported_candidate_write_in_votes','harris_walz','trump_vance','oliver_ter_maat','stein_ware','generic_write_ins','undervotes','overvotes','candidate_field_completeness','cumulative_votes','share_numerator','share_denominator']}
        out.update(top15=r['rank']<=15,minimum80=r['rank']<=n,priority=r['rank']<=max(15,n),source_id=PRES,source_sheet=r['source_locator']['sheet'],source_row=r['source_locator']['source_row'],ballots_cast_2024='',registration_2024='',ballot_registration_status='Separate source-scoped tables; no automatic source/year name crosswalk.')
        csvrows.append(out)
    csvout('../county-turnout.csv',csvrows)
    dump('geography.json',geography)
    sensitivities={}
    for sid,fields in [(SEN22,['bolduc','hassan','kauffman','scatter']),(SEN20,['messner','shaheen','odonnell','scatter']),('2024-ge-ballots-cast-14-xls',['ballots_total']),('2022-ge-ballots-cast-3-xls',['ballots_total']),('2020-ge-ballots-cast-xls',['ballots_total']),('2024-ge-names-on-checklist-7-xlsx',['checklist_total']),('2022-ge-names-on-checklist-2-xlsx',['checklist_total']),('2020-ge-names-on-checklist-xlsx',['checklist_total'])]:
        rs=[dict(r,volume=numeric_sum(r['raw_fields'][k]for k in fields))for r in datasets[sid]['native']]
        sensitivities[sid]=ranking(rs,'volume')
    dump('sensitivity.json',sensitivities)
    # Every difference remains source-scoped. Identical literal labels permit a
    # textual comparison only; never a boundary/clerk crosswalk.
    differences=[]
    families=[[PRES,'2024-ge-president-0-xls','2024-ge-president-xls'],[SEN22,'sos-archived-2022-ge-us-senator-xls','sos-archived-2022-ge-us-senator-1-xls','sos-archived-2022-ge-us-senator-2-xls'],['2024-ge-ballots-cast-14-xls','2024-ge-ballots-cast-6-xls'],['2022-ge-ballots-cast-3-xls','2022-ge-ballots-cast-xls','2022-ge-ballots-cast-2-xls'],['2022-ge-names-on-checklist-2-xlsx','2022-ge-names-on-checklist-1-xlsx']]
    families[2]=['2024-ge-ballots-cast-14-xls']+sorted(s for s in datasets if s.startswith('2024-ge-ballots-cast-')and s!='2024-ge-ballots-cast-14-xls')
    families.append(['2024-ge-names-on-checklist-7-xlsx']+sorted(s for s in datasets if s.startswith('2024-ge-names-on-checklist-')and s!='2024-ge-names-on-checklist-7-xlsx'))
    for final,*earlier in families:
        base={(r['county'],r['native_label'].strip()):r for r in datasets[final]['native']}
        for sid in earlier:
            for r in datasets[sid]['native']:
                k=(r['county'],r['native_label'].strip());f=base.get(k)
                if f is None:differences.append(dict(base=final,compared=sid,county=k[0],label=k[1],status='literal_label_unmatched'));continue
                for field,v in r['fields'].items():
                    if v!=f['fields'][field]:differences.append(dict(base=final,compared=sid,county=k[0],label=k[1],field=field,base_value=f['fields'][field],compared_value=v,base_locator=f['source_locator'],compared_locator=r['source_locator']))
    dump('vintage-differences.json',differences)
    print(json.dumps(dict(coverage=contract['coverage'],top15=contract['top15'],minimum80=contract['minimum80'],remainder=contract['remainder'],source_native_counts={sid:len(ds['native'])for sid,ds in datasets.items()}),indent=2))


if __name__=='__main__':main()
