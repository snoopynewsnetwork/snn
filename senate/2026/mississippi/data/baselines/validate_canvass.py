"""Validate independent original-page summary readings without residual allocation."""
import csv,json,re
from sources import *
def main():
    ledger=json.loads((OUT/'canvass-readings.json').read_text());candidates=list(csv.DictReader((OUT/'candidate-votes.csv').open()));results=[];vector_checks=0
    for r in ledger['readings']:
        key=r['source_id'];county=re.sub(r' Updated$','',references()[key]['url'].rsplit('/',1)[-1].removesuffix('.pdf')).lower();dims=len(r['method_labels'])
        for contest,names in [('senate',ledger['senate_candidate_order']),('president',ledger['president_candidate_order'])]:
            d=r[contest];assert len(d['candidates'])==len(names)
            for name,values in zip(names,d['candidates']):
                assert len(values)==dims and all(isinstance(v,int) and v>=0 for v in values)
                if dims>1:assert values[0]==sum(values[1:]),(key,contest,name,values)
                rr=[z for z in candidates if z['county'].lower()==county and z['contest']=='2024-'+contest and (z['candidate_literal']==name if contest=='senate' else z['candidate_literal'].startswith('Presidential Electors for '+name+' for President'))];assert len(rr)==1,(key,name)
                expected=int(rr[0]['original_csv_votes'] if key=='sos-2024-county-pike' else rr[0]['votes']);assert values[0]==expected,(key,contest,name,values[0],expected);vector_checks+=1
            for field in ['generic_write_in_marks','overvotes','undervotes','contest_opportunities','total_votes_cast']:
                values=d.get(field)
                if values is None:continue
                assert len(values)==dims and all(isinstance(v,int) and v>=0 for v in values)
                if dims>1:assert values[0]==sum(values[1:]),(key,contest,field,values)
                vector_checks+=1
            named=[sum(row[i] for row in d['candidates']) for i in range(dims)];generic=d.get('generic_write_in_marks');over=d.get('overvotes');under=d.get('undervotes');opps=d.get('contest_opportunities');cast=d.get('total_votes_cast')
            if cast is not None and generic is not None:assert [a+b for a,b in zip(named,generic)]==cast
            known=[named[i]+sum(v[i] for v in [generic,over,under] if v is not None) for i in range(dims)]
            residual=[opps[i]-known[i] for i in range(dims)] if opps is not None else None
            if opps is not None and all(v is not None for v in [generic,over,under]):assert residual==[0]*dims,(key,contest,residual)
            results.append(dict(source_id=key,page=r['page'],contest=contest,method_labels=r['method_labels'],named_candidate_votes=named,generic_marks=generic,overvotes=over,undervotes=under,contest_opportunities=opps,unclassified_opportunity_residual=residual,qualification='Residual is arithmetic only, not allocated to missing under/over/blank fields; generic marks not inferred valid named votes.'))
    stats=json.loads((OUT/'canvass-statistics-readings.json').read_text());assert len({r['source_id'] for r in stats['readings']})==len(stats['readings'])
    for r in stats['readings']:
        assert r['raw_sha256']==sha(original(r['source_id']));assert (OUT/r['evidence']).exists();assert len(r['ballots_cast_total'])==len(r['method_labels'])
        for field in ['ballots_cast_total','ballots_cast_blank']:
            vv=r.get(field)
            if vv is not None:
                assert len(vv)==len(r['method_labels']) and all(type(v) is int and v>=0 for v in vv)
                if len(vv)>1:assert vv[0]==sum(vv[1:])
    lp=OUT/'source/2024-lincoln-independent-controls.json';lincoln=json.loads(lp.read_text());assert lincoln['statistics_ballots']==15898 and lincoln['statistics_minus_each_contest']==0 and not lincoln['registration_usable'] and lincoln['prior_source_readings_unchanged'];assert lincoln['senate_unclassified_residual']==172 and lincoln['president_unclassified_residual']==69
    for p in lincoln['original_pages']:assert sha((BASE/p['raster_path']).read_bytes())==p['raster_sha256'] and sha((BASE/p['receipt_path']).read_bytes())==p['receipt_sha256']
    p=BASE/lincoln['crop']['path'];assert p.stat().st_size==lincoln['crop']['bytes'] and sha(p.read_bytes())==lincoln['crop']['sha256']
    mp=OUT/'source/2024-montgomery-independent-controls.json';m=json.loads(mp.read_text());assert m['statistics']['ballots_cast_total']==[885] and m['statistics']['registered_voters_total']==6291 and m['statistics']['ballots_cast_blank']==[1] and m['statistics_minus_named_Senate']==-3464 and m['statistics_minus_named_President']==-3539 and not m['common_electorate_or_chronology_inferred']
    for pin in [m['original_page'],m['render_receipt'],m['crop']]:assert (BASE/pin['path']).stat().st_size==pin['bytes'] and sha((BASE/pin['path']).read_bytes())==pin['sha256']
    save(OUT/'canvass-validation.json',dict(status='pass_available_independent_readings',source_pages=len(ledger['readings']),checked_vectors=vector_checks,statistics_panels=len(stats['readings']),Lincoln_independent_controls=dict(path=str(lp.relative_to(BASE)),bytes=lp.stat().st_size,sha256=sha(lp.read_bytes())),controls=results))
    print('summary pages',len(ledger['readings']),'vectors',vector_checks)
if __name__=='__main__':main()
