"""Same-vintage exact-name source comparison; unmatched names never normalized."""
from extract import *
def main():
    dbunits=list(csv.DictReader(gzip.open(BASE/'native-units.csv.gz','rt')));original=list(csv.DictReader(gzip.open(BASE/'legacy-native-baselines.csv.gz','rt')))
    db={};out=[];matched=set();candidate_diff=[]
    for r in dbunits:
        if r['native_type']!='Precinct':continue
        k=(r['contest_label'],r['county'],r['name']);assert k not in db;db[k]=r
    for r in original:
        k=(r['contest_label'],r['county'],r['name']);d=db.get(k)
        if d:
            matched.add(k);ids=json.loads(r['choice_analysis_ids']);vs=json.loads(r['raw_choice_vector']);dv={x['candidate_id']:x['votes']for x in json.loads(d['raw_candidate_cells'])}
            for cid,v in zip(ids,vs):
                if dv.get(cid)!=v:candidate_diff.append(dict(contest=k[0],county=k[1],name=k[2],candidate_id=cid,original=v,database=dv.get(cid)))
        out.append(dict(contest_label=k[0],county=k[1],original_name=k[2],original_key=r['geography_key'],database_key=d['geography_key']if d else None,status='exact source-name comparison; physical identity unverified' if d else 'unmatched spelling retained; no inferred alias',candidate_vector_matches=bool(d) and all(dv.get(cid)==v for cid,v in zip(ids,vs))))
    methodmap={'Election Day':'1','Early Voting':'5','In-Person Absentee':'9','Absentee By Mail':'6','Failsafe':'7','Provisional':'2','Failsafe Provisional':'8','Provionsal':'2'}
    dm={}
    for r in csv.DictReader(gzip.open(BASE/'candidate-method-controls.csv.gz','rt')):
        if r['observation_scope']=='methods' and r['division_type']=='Precinct':
            # County from full path only, through the retained native-unit dictionary.
            dm[(r['contest_label'],r['division_path'],int(r['candidate_id']),r['method_id'])]=int(r['votes'])
    mdiff=[];compared=0
    for r in csv.DictReader(gzip.open(BASE/'legacy-candidate-methods.csv.gz','rt')):
        k=(r['contest_label'],r['county'],r['native_name']);d=db.get(k)
        if not d:continue
        compared+=1;cid=int(r['analysis_candidate_id']);v=int(r['votes']);dv=dm.get((k[0],d['native_division_path'],cid,methodmap[r['method_name']]))
        if dv!=v:mdiff.append(dict(contest_label=k[0],county=k[1],name=k[2],database_key=d['geography_key'],candidate_id=cid,raw_original_method=r['method_name'],database_method_id=methodmap[r['method_name']],original=v,database=dv,difference=v-dv if dv is not None else None,source_id=r['source_id'],source_pointer=r['source_pointer']))
    multisets=[]
    for lab in LABELS:
        for county in sorted({r['county']for r in original if r['contest_label']==lab}):
            oo=[r for r in original if r['contest_label']==lab and r['county']==county];dd=[r for r in dbunits if r['contest_label']==lab and r['county']==county and r['native_type']=='Precinct']
            ids=sorted(json.loads(oo[0]['choice_analysis_ids']))
            ov=collections.Counter(tuple(dict(zip(json.loads(r['choice_analysis_ids']),json.loads(r['raw_choice_vector'])))[cid]for cid in ids)for r in oo)
            dv=collections.Counter(tuple({x['candidate_id']:x['votes']for x in json.loads(r['raw_candidate_cells'])}[cid]for cid in ids)for r in dd)
            multisets.append(dict(contest_label=lab,county=county,original_rows=len(oo),database_rows=len(dd),candidate_ids=ids,multiset_equal=ov==dv,scope='numerical multiset equality only; no identity or geographic join'))
    rows(BASE/'legacy-native-identity-comparison.csv.gz',out)
    dump(BASE/'legacy-database-comparison.json',dict(original_leaves=len(original),database_leaves=len(db),exact_name_matches=len(matched),original_unmatched=sum(r['database_key']is None for r in out),database_unmatched=[dict(contest=k[0],county=k[1],name=k[2],key=v['geography_key'])for k,v in db.items()if k not in matched],
        combined_candidate_differences=candidate_diff,county_candidate_vector_multisets=multisets,method_cells_compared=compared,method_differences=mdiff,method_alias='Charleston literal Provionsal compared with DB method2 Provisional; raw spelling never changed',identity_scope='same historical contest exact-name source comparison only; no physical/current/cross-year acceptance'))
    print(compact(dict(exact_names=len(matched),unmatched_original=len(original)-len(matched),combined_differences=len(candidate_diff),method_differences=len(mdiff))))
if __name__=='__main__':main()
