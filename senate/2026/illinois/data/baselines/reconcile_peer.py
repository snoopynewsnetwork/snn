"""Freeze reciprocal peer captures, then compare all shared fields independently.
No producer data is overwritten. Run after original extraction is stabilized.
"""
import collections,csv,gzip,io,json
from pathlib import Path
from source_io import ROOT,STATE,sha,dump

def main():
    peer=STATE/'data/turnout/extract';dest=ROOT/'peer-capture';dest.mkdir(exist_ok=True);manifest=[]
    files=['county-all-years.csv','county-candidate-source-rows.csv','county-priorities.json','independent-controls.json','original-native-records.jsonl.gz','authority-inventory.json']
    files += [f'{prefix}-{y}.jsonl.gz'for prefix in ['native-units','authority-native','source-contexts']for y in ['2020','2022','2024']]
    for f in files:
        target=dest/(f if f.endswith('.gz')else f+'.gz')
        if target.exists():
            z=target.read_bytes();b=z if f.endswith('.gz')else gzip.decompress(z)
        else:
            b=(peer/f).read_bytes();z=b if f.endswith('.gz')else gzip.compress(b,mtime=0);target.write_bytes(z)
        manifest.append(dict(origin=str((peer/f).relative_to(STATE)),captured=str(target.relative_to(ROOT)),original_bytes=len(b),original_sha256=sha(b),stored_bytes=len(z),stored_sha256=sha(z),compression='original-gzip'if f.endswith('.gz')else 'gzip'))
    dump(dest/'manifest.json',manifest)
    def rows(f):
        p=dest/(f if f.endswith('.gz')else f+'.gz');b=gzip.decompress(p.read_bytes())
        if f.endswith('.csv'):return list(csv.DictReader(io.StringIO(b.decode())))
        if f.endswith('.jsonl.gz'):return [json.loads(s)for s in b.splitlines()]
        return json.loads(b)
    checks=0;errors=[]
    def check(ok,context):
        nonlocal checks
        checks+=1
        if not ok:errors.append(context)
    # Complete county field comparison, independent source-based candidate pairs included below.
    mine={(r['year'],r['county_key']):r for r in csv.DictReader((ROOT.parent/'county-baselines.csv').open())}
    pcount=rows('county-all-years.csv');check(len(mine)==len(pcount)==306,'county coverage306')
    cmap={'FIPS':'county_fips','county':'county_name','all_named_votes':'all_named_votes','native_printed_votes':'printed_votes','named_minus_native_printed':'additional_named_votes','native_generic_marks':'native_generic_writein_marks','native_raw_mark_universe':'printed_plus_generic_marks','generic_minus_additional_named':'generic_minus_named_difference','ballots_cast':'ballots_cast','historical_Total_Voters':'historical_Total_Voters'}
    peer_keys={}
    for p in pcount:
        key=(p['year'],p['county_authority_id']);m=mine[key];peer_keys[p['key']]=p['county_authority_id']
        for a,b in cmap.items():check(m[a]==p[b],['county',key,a,m[a],p[b]])
        check(sorted(json.loads(m['authority_members']),key=int)==sorted(p['authority_ids'].split(','),key=int),['county authority members',key])
    mc=list(csv.DictReader((ROOT/'extract/county-candidate-source-rows.csv').open()));pc=rows('county-candidate-source-rows.csv')
    md={(r['year'],r['county_key'],r['candidate_literal']):r for r in mc};pd={(r['year'],r['county_authority_id'],r['name']):r for r in pc};check(md.keys()==pd.keys(),'all1462county candidate keys')
    for key,m in md.items():
        p=pd[key]
        for a,b in {'candidate_literal':'name','party_literal':'party','votes':'votes','votes_literal':'votes_literal','percentage_literal':'percentage_literal','href_literal':'href','detail_url':'detail_url','table_id':'table_id'}.items():check(m[a]==p[b],['candidate',key,a])
        check(int(m['table_row'])==int(p['tr_position_0based'])+1,['candidate source position',key])
        check(m['source_id']=='original-turnout-'+p['source_id'],['candidate source id mapping',key])
    # Every one of the146370original rows and every literal field+source position.
    pr=rows('original-native-records.jsonl.gz');by=collections.defaultdict(list)
    for p in pr:by[str(p['year'])].append(p)
    for y in ['2020','2022','2024']:
        with gzip.open(ROOT/f'extract/{y}-raw-rows.csv.gz','rt')as f:mr=list(csv.DictReader(f))
        check(len(mr)==len(by[y]),['raw count',y])
        for m,p in zip(mr,by[y]):
            check(int(m['csv_record_1based_including_header'])==p['record_position_1based']+1,['source position',y,p['record_position_1based']])
            check(m['source_id']==p['source_id'],['raw source',y,p['record_position_1based']])
            for k,v in p['fields'].items():check(m[k]==v,['raw literal',y,p['record_position_1based'],k])
        mineunits=json.loads((ROOT/f'extract/{y}-units.json').read_text());pu=rows(f'native-units-{y}.jsonl.gz');ud={(r['JurisdictionID'],r['PrecinctName']):r for r in mineunits};check(len(ud)==len(pu),['native coverage',y])
        for p in pu:
            key=(p['authority_id'],p['precinct_name_literal']);m=ud[key]
            check([v-1 for v in m['source_positions']]==p['source_records_1based'],['native source positions',y,key])
            check(m['method']=='unavailable_no_source_column'and p['method']is None,['method unavailable',y,key])
            check(m['generic_writein_marks']==p['generic_writein_marks'],['native generic recorded aggregate',y,key])
            check(m['literal_category_record_sums']==p['literal_categories'],['native all literal category record aggregates and presence',y,key])
            for role in ['A','B']:check(m[role]==p['printed_candidate_votes'].get(m[role+'_name']),['native pair',y,key,role])
            check(set(m['printed_other_missing_candidates'])==set(p['missing_printed_candidate_rows']),['native sparse missing',y,key])
            check(len(m['presentation_contexts'])==len(p['source_contexts']),['native container presentation count',y,key])
    # All108authority category totals each year and source native context coverage.
    ma=collections.defaultdict(dict)
    for r in csv.DictReader((ROOT/'extract/authority-candidate-category-totals.csv').open()):ma[r['year'],r['JurisdictionID']][r['candidate_or_category_literal']]=int(r['votes'])
    for y in ['2020','2022','2024']:
        pa=rows(f'authority-native-{y}.jsonl.gz');check(len(pa)==108,['authority coverage',y])
        for p in pa:check(ma[y,p['authority_id']]==p['literal_categories'],['authority categories',y,p['authority_id']])
    pc=rows('county-priorities.json');mine=json.loads((ROOT/'priority/contracts.json').read_text())['contracts']
    for y in ['2020','2022','2024']:
        for mfield,pfield in [('all_named_votes','all_named_votes'),('native_printed_votes','printed_votes'),('native_raw_mark_universe','printed_plus_generic_marks'),('ballots_cast','ballots_cast')]:
            m=mine[f'county-{y}-{mfield}'];p=pc[f'{y}:{pfield}'];check(m['full_order']==[peer_keys[k]for k in p['full_order']],['full102order',y,pfield])
            for a,b in [('denominator','denominator'),('minimum_count','minimum80_count'),('before_votes','preceding_votes'),('crossing_votes','cumulative80_votes')]:check(m[a]==p[b],['exact80',y,pfield,a])
    result={'status':'pass'if not errors else 'fail','checks':checks,'errors':errors,'capture_manifest':'peer-capture/manifest.json','scope':'All shared county/candidate/literal raw fields/source positions, every authority category, all native contexts/missing pair/method fields,12full county orders and exact80 crossings. Not a current-boundary or legal native-writein-allocation approval.'}
    dump(ROOT/'peer-reconciliation.json',result);print(json.dumps({**result,'errors':errors[:10],'error_count':len(errors)},indent=2));assert not errors
if __name__=='__main__':main()
