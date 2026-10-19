"""Bounded60-view source/control audit, explicit literal and reading-box exceptions."""
import csv,json
from collections import Counter
from sources import OUT,BASE,sha,original,save
def main():
    path=OUT/'native-2024-senate-reviewed-60views.json';x=json.loads(path.read_text());cc={r['fips']:r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};roles=Counter();keys=set();npositions=0
    for s in x['sources']:
        assert sha(original(s['source_id']))==s['raw_sha256'];sums=Counter();totals={}
        for p in s['pages']:
            w,h=p['render_size'];assert sha((BASE/p['raster_path']).read_bytes())==p['raster_sha256']
            for c in p['columns']:
                k=(s['source_id'],p['page'],c['source_column']);assert k not in keys;keys.add(k);roles[c['role']]+=1;hb=c['header_bounds'];assert 0<=hb[0]<hb[2]<=w+1 and 0<=hb[1]<hb[3]<=h+1
                for name,z in c['fields'].items():
                    npositions+=1;b=z['source_box'];assert 0<=b[0]<b[2]<=w+1 and 0<=b[1]<b[3]<=h+1
                    if c['role']=='unused_template_column':assert z['value'] is None and not c['label_literal'];continue
                    assert isinstance(z['value'],int) and z['value']>=0
                    if c['role']=='source_TOTAL':assert name not in totals;totals[name]=z['value']
                    else:assert c['label_literal'];sums[name]+=z['value']
        ex={'Ty Pinkins':int(cc[s['county_fips']]['2024-senate_A']),'Roger F. Wicker':int(cc[s['county_fips']]['2024-senate_B'])};assert dict(sums)==totals==ex
    assert len(x['sources'])==60 and roles=={'source_native_reporting_constituent':1373,'source_TOTAL':60,'unused_template_column':305};assert npositions==3476 and len(keys)==1738
    dif=x['source_literal_peer_disagreements'];assert len(dif)==1 and dif[0]['own_original_literal']=='Forrestry' and dif[0]['frozen_peer_literal']=='Forestry';assert (OUT/dif[0]['evidence']).exists();rep=x['accepted_reading_box_repairs'];assert len(rep)==6
    for r in rep:
        assert r['source_id']=='sos-2024-county-itawamba';assert r['targeting_box']!=r['accepted_original_reading_box'];assert (OUT/r['evidence']).exists()
    rows=list(csv.DictReader((OUT/'native-2024-senate-reviewed-60views.csv').open()));assert len(rows)==npositions and len({(r['key'],r['candidate']) for r in rows})==len(rows)
    save(OUT/'native-reviewed-validation-60views.json',dict(status='pass_bounded_original60view_counts_with_explicit_source_literal_and_reading_box_differences',ledger_path=str(path.relative_to(BASE)),ledger_sha256=sha(path.read_bytes()),source_views=60,pages=sum(len(s['pages']) for s in x['sources']),native_constituents=1373,native_numeric_candidate_positions=2746,TOTAL_candidate_positions=120,unused_null_candidate_positions=610,all_source_hashes_and_original_render_hashes_verified=True,all60_parent_candidate_controls_exact=True,source_literal_peer_disagreements=dif,accepted_reading_box_repairs=rep,claim_exact_accepted_box_agreement_with_peer=False,statewide_native_complete=False,presidential_native_complete=False,current2026_geography_approved=False))
    print('pass60boundedviews/3476positions; literalForrestry and6acceptedboxrepairs explicit')
if __name__=='__main__':main()
