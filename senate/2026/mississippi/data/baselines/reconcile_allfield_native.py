"""Own manual original eleven-field ledger versus frozen independent peer reads."""
import gzip,json
from collections import Counter
from sources import OUT,BASE,sha,original,save
from build_counties import writecsv
def main():
    path=BASE/'data/coordinator-qa/native-allfield-two-views/native-allfield-readings.json.gz';stored=path.read_bytes();raw=gzip.decompress(stored);assert sha(raw)=='13f37c2b7c662231c2561c191b6e13f07da227f0020b4516baf9d62d081516b0';peer=json.loads(raw);rows=[];checks=[]
    for filename in ['alcorn-readings.json','coahoma-updated-readings.json']:
        x=json.loads((OUT/filename).read_text());key=x['source_id'];p=peer['sources'][key];assert sha(original(key))==p['raw_sha256']==x['raw_sha256'];count=Counter()
        for pg in x['pages']:
            pp=next(a for a in p['pages'] if a['page']==pg['page']);assert pp['render_size']==pg['render_size'];assert pp['rotation_ccw']==pg['rotation_ccw'];assert abs(pp['deskew_angle_ccw']-pg['deskew_angle_ccw'])<1e-9
            for f in pg['fields']:
                pf=next(z for z in pp['fields'] if z['candidate']==f['field']);assert pf['row_bounds']==f['row_bounds']
                for i,(c,v) in enumerate(zip(pg['columns'],f['values'])):
                    box=[c['x_bounds'][0],f['row_bounds'][1],c['x_bounds'][1],f['row_bounds'][3]];physical=[j for j,b in enumerate(pf['cell_bounds']) if b==box];assert len(physical)==1;assert v==pf['values'][physical[0]];assert i==physical[0]
                    if c['unit_type']=='unused':assert v is None;count['unused_null']+=1
                    else:assert isinstance(v,int) and v>=0;count['numeric_including_TOTAL']+=1
                    rows.append(dict(key=f'{x["fips"]}:{key}:p{pg["page"]}:c{c["source_column"]}',county_fips=x['fips'],source_id=key,raw_sha256=x['raw_sha256'],source_page=pg['page'],source_column=c['source_column'],native_label_literal=c['native_label_literal'],role=c['unit_type'],candidate=f['field'],votes=v if v is not None else '',full_source_cell_bounds=json.dumps(box),render_size=json.dumps(pg['render_size']),rotation_ccw=pg['rotation_ccw'],deskew_angle_ccw=pg['deskew_angle_ccw'],reading_basis='own_independent_complete_original_visual_reading_then_frozen_peer_reconciliation'))
        checks.append(dict(source_id=key,raw_sha256=x['raw_sha256'],candidate_fields=11,counts=dict(count),own_ledger_path=f'data/baselines/{filename}',own_ledger_sha256=sha((OUT/filename).read_bytes()),all_values_and_physical_boxes_agree=True))
    writecsv(OUT/'native-allfield-reviewed.csv',rows)
    save(OUT/'native-allfield-peer-reconciliation.json',dict(status='pass_two_bounded_original_source_views_11candidate_fields',peer_reference_path=str(path.relative_to(BASE)),peer_stored_sha256=sha(stored),peer_original_sha256=sha(raw),sources=checks,numeric_positions_including_TOTAL=sum(s['counts']['numeric_including_TOTAL'] for s in checks),unused_null_positions=sum(s['counts']['unused_null'] for s in checks),compared_positions=len(rows),all_primary_county_controls='Validated independently in validate.py, all22 named candidate vectors',qualification='Read-only comparison AFTER own original visual readings; geometry only was shared. No peer vote copied into own ledger, no scope extrapolation to other counties/nativefields/currentgeography.'))
    print(len(rows),'allfield sourcepositions agree;407numeric+77unusednull')
if __name__=='__main__':main()
