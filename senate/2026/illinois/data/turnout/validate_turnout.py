#!/usr/bin/env python3
"""Meaningful offline raw/identity/candidate/denominator/order/asset QA.
--seal writes deterministic validation and a complete owned asset manifest.
Default verifies the existing seal without changing files.
"""
from pathlib import Path
from collections import Counter
import argparse,csv,gzip,hashlib,json,re
from urllib.parse import unquote,urlparse
D=Path(__file__).resolve().parent;STATE=D.parent.parent;E=D/'extract'
def sha(b):return hashlib.sha256(b).hexdigest()
def j(p):return json.loads(p.read_text())
def jl(p):return[json.loads(x)for x in gzip.decompress(p.read_bytes()).decode().splitlines()]
def csvp(p):return list(csv.DictReader(p.open()))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seal',action='store_true');args=ap.parse_args();checks=0;groups=Counter()
    def ck(condition,label):
        nonlocal checks;checks+=1;groups[label.split(':')[0]]+=1
        assert condition,label
    contract=j(D/'priority-set.json');control=j(E/'independent-controls.json');raw=jl(E/'original-native-records.jsonl.gz');state=csvp(E/'statewide-source-rows.csv');county=csvp(E/'county-candidate-source-rows.csv')
    ck(len(raw)==146370,'raw:all years records')
    for year in [2024,2022,2020]:
        rr=[r for r in raw if r['year']==year];units=jl(E/f'native-units-{year}.jsonl.gz');ctx=jl(E/f'source-contexts-{year}.jsonl.gz');auth=jl(E/f'authority-native-{year}.jsonl.gz');c=control[str(year)]
        ck(len(rr)==c['raw_rows'],'raw:year row count');ck(all(len(r['fields'])==12 for r in rr),'raw:all twelve fields');ck([r['record_position_1based']for r in rr]==list(range(1,len(rr)+1)),'raw:original ordered positions')
        ck(len(auth)==108,'coverage:108authorities');ck(len({a['authority_id']for a in auth})==108,'identity:unique authority IDs');ck(len(units)==c['authority_literal_precinct_groups'],'coverage:native observations');ck(len(ctx)==c['full_source_contexts'],'coverage:full contexts')
        ck(len({u['key']for u in units})==len(units),'identity:unique native keys');ck(sorted(i for u in units for i in u['source_records_1based'])==list(range(1,len(rr)+1)),'coverage:native record bijection');ck(sorted(i for u in ctx for i in u['source_records_1based'])==list(range(1,len(rr)+1)),'coverage:full context record bijection')
        total=Counter()
        for r in rr:total[r['fields']['CandidateName']]+=int(r['fields']['VoteCount'])
        ck(dict(total)==c['literal_category_sums'],'candidate:raw literal controls')
        from_units=Counter();from_auth=Counter()
        for u in units:
            from_units.update(u['literal_categories']);ck(u['method']is None,'method:no invented native method');ck(set(u['source_records_1based'])=={i for z in u['source_contexts']for i in z['source_records_1based']},'coverage:native presentations');ck(all((v is None)==(n in u['missing_printed_candidate_rows'])for n,v in u['printed_candidate_votes'].items()),'missing:printed cell null semantics')
            ck(u['printed_known_recorded_sum']==sum(v for v in u['printed_candidate_votes'].values()if v is not None),'candidate:printed recorded sum')
            ck((u['printed_observed_sum']is None)==u['administrative_only'],'missing:unavailable named pools')
        for a in auth:
            from_auth.update(a['literal_categories']);ck((a['generic_writein_marks']is None)==(not a['generic_writein_source_present']),'missing:authority generic observation presence');ck(a['generic_writein_recorded_sum']==sum(v for n,v in a['literal_categories'].items()if n.lower()=='write-in'),'candidate:authority generic recorded aggregate')
        ck(from_units==total==from_auth,'candidate:unit authority statewide category balance')
        sr={r['name']:int(r['votes'])for r in state if int(r['year'])==year};co=Counter()
        for r in county:
            if int(r['year'])==year:co[r['name']]+=int(r['votes'])
        ck(dict(co)==sr,'candidate:every county named candidate statewide balance');ck(sum(sr.values())==c['state_named_total'],'candidate:named statewide total')
        for field in ['printed_observed_sum','printed_plus_generic_observed']:
            order=jl(E/f'native-{year}-order-{field}.jsonl.gz');met=j(E/f'native-{year}-{field}-priority.json');validate_order(order,met,field,ck)
    for field in ['printed_observed_sum','printed_plus_generic_observed']:
        validate_order(jl(E/f'authority-2024-order-{field}.jsonl.gz'),j(E/f'authority-2024-{field}-priority.json'),field,ck)
    u=jl(E/'native-units-2024.jsonl.gz');admin=[r for r in u if r['administrative_only']];ck(len(admin)==4,'missing:four administrative pools');ck({r['authority_id']for r in admin}=={'51','59','65','108'},'missing:exact administrative authorities');ck(sum('Robert F. Kennedy Jr.'in r['missing_printed_candidate_rows']for r in u if not r['administrative_only'])==15,'missing:fifteen absent Kennedy cells')
    p=contract['primary_priority'];order=jl(E/'native-2024-order-printed_observed_sum.jsonl.gz');ck(contract['full_order']==[r['key']for r in order],'contract:complete full native order');ck(len(set(contract['ordered_priority_keys']))==5540,'contract:priority count unique');ck(contract['ordered_priority_keys']==[r['key']for r in order[:5540]],'contract:exact ordered priority keys');ck(contract['remainder_keys']==[r['key']for r in order[5540:]],'contract:exact ordered remainder');ck(p['denominator']==5592368 and p['top15_votes']==29572 and p['preceding_votes']==4473789 and p['cumulative80_votes']==4474312,'contract:exact primary arithmetic');ck(contract['coordinator_acceptance']is False and contract['current_geometry_approved']is False,'qualification:no self approval');ck(len(contract['native_to_authority_parent_map'])==10062,'coverage:all native parents');ck(len(contract['authority_inventory'])==108,'coverage:authority inventory');ck(len({a['county_fips']for a in contract['authority_inventory']})==102,'coverage:102county FIPS no103rd county')
    ck(all(a['county_fips'].startswith('17')and len(a['county_fips'])==5 for a in contract['authority_inventory']),'identity:parent FIPS format');ck(len(csvp(D.parent/'county-turnout.csv'))==108,'coverage:compatibility CSV preserves108authorities')
    cp=j(E/'county-priorities.json')
    for year in [2024,2022,2020]:
        for field in ['all_named_votes','printed_votes','printed_plus_generic_marks','ballots_cast','historical_Total_Voters']:
            rows=csvp(E/f'county-{year}-order-{field}.csv');met=cp[f'{year}:{field}'];values=[int(r[field])for r in rows];ck(len(rows)==102 and len({r['county_fips']for r in rows})==102,'county:complete102order');ck(values==sorted(values,reverse=True),'county:descending exact integer order');ck(sum(values)==met['denominator'],'denominator:county scope total');k=met['minimum80_count'];ck(5*sum(values[:k-1])<4*sum(values)<=5*sum(values[:k]),'threshold:county minimum integer80');ck(sum(values[:15])==met['top15_votes'],'threshold:county top15')
    ck(j(D/'peer-reconciliation.json')['status']=='pass','peer:independent reciprocal agreement')
    # Every original pin and every retained response (including failed bodies).
    for sid,r in j(E/'source-pins.json').items():
        f=STATE/r['path'];z=f.read_bytes();b=gzip.decompress(z);ck(sha(z)==r['stored_sha256']and len(z)==r['stored_bytes'],'source:stored pinned bytes');ck(sha(b)==r['raw_sha256']and len(b)==r['raw_bytes'],'source:reconstructed original bytes')
    for pth in (D/'source').rglob('*.receipt.json'):
        r=j(pth)
        if 'asset'not in r:continue
        f=D/'source'/r['asset'];z=f.read_bytes();b=gzip.decompress(z);ck(sha(z)==r['stored_sha256'],'source:receipt stored hash');ck(sha(b)==r['raw_sha256'],'source:receipt raw hash');ck(len(b)==r.get('raw_bytes',r.get('bytes')),'source:receipt raw size')
    for r in j(D/'source/external-originals.json'):
        z=(STATE/r['path']).read_bytes();b=gzip.decompress(z);ck(sha(z)==r['stored_sha256']and sha(b)==r['raw_sha256'],'source:external original exact hashes')
    for r in j(D/'source/provider-parent-receipts.json')['sources']:
        z=(STATE/r['path']).read_bytes();b=gzip.decompress(z)if r.get('compression')=='gzip'else z;ck(sha(z)==r['stored_sha256']and sha(b)==r['raw_sha256'],'source:external acquisition ancestor body hashes')
    for r in j(D/'peer-reconciliation.json')['snapshots']:
        z=(STATE/r['snapshot_path']).read_bytes();ck(sha(z)==r['sha256']and len(z)==r['bytes'],'peer:immutable reciprocal snapshot hash')
    owned=[STATE/'turnout.md',D.parent/'county-turnout.csv']+[p for p in D.rglob('*')if p.is_file()and p.name!='asset-manifest.json'and '__pycache__'not in p.parts]
    ck(not any(p.is_dir()and p.name in ['__pycache__','node_modules','.venv']for p in D.rglob('*')),'assets:no dependency cache directories')
    for f in owned:
        ck(f.stat().st_size<40000000,'assets:strict object size bound')
        if f.suffix=='.md':
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',f.read_text()):
                target=target.strip('<>');u=urlparse(target)
                if u.scheme or target.startswith('#'):continue
                rel=unquote(target.split('#')[0]);dest=(f.parent/rel).resolve();planned=args.seal and dest in {(D/'validation.json').resolve(),(D/'asset-manifest.json').resolve()};ck(dest.exists()or planned,'links:relative target exists')
    result={'status':'pass','checks':checks,'check_groups':dict(sorted(groups.items())),'primary_scope':'native printed-known source votes, missing cells null; no valid-WI allocation','primary_units':10062,'primary_known_named_pools':10058,'unavailable_named_pools':4,'primary_denominator':5592368,'top15_votes':29572,'minimum80_count':5540,'preceding_count':5539,'preceding_votes':4473789,'crossing_votes':523,'crossing_cumulative':4474312,'peer_checks':j(D/'peer-reconciliation.json')['checks'],'material_qualifications':['Legal native write-in allocation unavailable; 16469source-scope gap unallocated.','15Kennedy cells absent,4administrative named pools unavailable; no invented zeros.','2024native category total differs from ballot control by2470, unallocated.','Historical Registration source field and turnout-table Total Voters differ; current A/I definitions not expanded by inspected page.','No current geography approval, measured November cadence, forecast or collector.','Coordinator acceptance pending.']}
    validation=D/'validation.json';data=(json.dumps(result,indent=2)+'\n').encode()
    if args.seal:
        validation.write_bytes(data)
        paths=[STATE/'turnout.md',D.parent/'county-turnout.csv']+[p for p in D.rglob('*')if p.is_file()and p.name!='asset-manifest.json']
        manifest={'scope':'exclusive owned report/data only; self excluded to avoid circular hash','strict_max_bytes':39999999,'assets':[{'path':str(p.relative_to(STATE)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(paths)],'external_originals':[{'path':r['path'],'bytes':r['stored_bytes'],'sha256':r['stored_sha256']}for r in j(E/'source-pins.json').values()if not str(r['path']).startswith('data/turnout/')]}
        (D/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        ck(validation.exists()and j(validation)['status']=='pass','seal:validation exists')
        for r in j(D/'asset-manifest.json')['assets']:
            pth=STATE/r['path'];ck(pth.stat().st_size==r['bytes']and sha(pth.read_bytes())==r['sha256'],'seal:owned asset hash/size')
    print(json.dumps({'status':'pass','checks':checks,'groups':dict(groups),'sealed':args.seal}))
def validate_order(rows,met,field,ck):
    vals=[r[field]for r in rows];numeric=[v for v in vals if v is not None];ck(numeric==sorted(numeric,reverse=True),'order:descending native/authority');ck(sum(numeric)==met['denominator'],'denominator:native/authority source scope');ck([r['key']for r in rows]==met['full_order'],'order:complete order contract');cum=0
    for r in rows:
        cum+=r[field]or 0;ck(cum==r['cumulative_votes'],'order:exact cumulative');ck(r['share_denominator']==met['denominator'],'weights:common denominator');ck(r['share_numerator']==r[field],'weights:exact numerator')
    k=met['minimum80_count'];ck(5*sum(v or 0 for v in vals[:k-1])<4*sum(numeric)<=5*sum(v or 0 for v in vals[:k]),'threshold:native/authority minimum integer80');ck(sum(v or 0 for v in vals[:15])==met['top15_votes'],'threshold:native/authority top15');ck(met['remainder_votes']==sum(v or 0 for v in vals[k:]),'threshold:complete remainder')
if __name__=='__main__':main()
