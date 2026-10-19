"""Original-only complete candidate readings of nonadditive 2024 SEMS alternatives.

Keep these publications outside the preferred82 coverage ledger and statewide sum.
Whole original page rasters, not OCR crop polygons, are the reading authority.
"""
import gzip,json
from collections import Counter
from sources import OUT,BASE,save,sha,original
from extract_replay_president import NAMES
from build_counties import writecsv
NAMES=NAMES+['Ty Pinkins','Roger F. Wicker']
VALUES={'coahoma':{2:[
[64,18,314,532,297,864,83,787,143,55,93],
[0,0,0,0,1,1,0,1,1,0,1],
[0,0,0,2,0,0,0,0,0,0,0],
[0,0,0,2,0,0,0,0,0,0,0],
[36,28,180,422,61,55,45,137,25,66,32],
[0,0,1,0,1,0,0,1,0,0,0],
[0,0,2,1,1,0,0,2,0,0,0],
[1,0,1,7,6,6,0,4,1,2,1],
[0,0,1,0,0,0,0,1,0,0,0],
[61,18,299,515,284,838,76,743,138,55,88],
[41,29,188,438,67,73,50,166,30,66,39]],3:[
[289,397,94,266,30,32,353,4711],
[0,0,0,2,0,0,0,7],
[0,1,0,2,0,0,0,5],
[0,0,0,0,3,0,1,6],
[39,23,115,558,144,27,15,2008],
[1,0,0,1,0,0,0,5],
[1,0,0,0,0,0,0,7],
[3,2,1,3,0,0,1,39],
[0,0,0,0,0,0,0,2],
[277,389,96,254,32,26,344,4533],
[49,33,112,574,143,29,19,2146]]}}
PENDING={}
EXPECTED={'coahoma':[4711,7,5,6,2008,5,7,39,2,4533,2146],
          'pike':[6091,17,15,11,6504,9,7,52,9,5898,6719]}
PENDING['pike']={2:[
[420,165,216,402,219,178,358,360,356,346,165],
[0,0,0,0,2,0,0,0,1,1,0],
[0,1,1,2,0,0,0,0,0,1,0],
[1,0,0,0,0,0,0,1,0,1,0],
[28,34,85,21,227,14,94,166,151,264,108],
[1,0,0,0,2,0,1,0,0,0,0],
[0,0,0,1,1,0,0,0,0,1,0],
[2,1,0,2,5,0,0,4,2,2,1],
[0,0,0,0,1,0,0,1,1,0,0]],3:[
[307,212,158,93,178,258,103,150,241,348,384],
[1,1,1,1,1,1,3,1,0,1,0],
[1,1,0,2,0,0,2,1,1,1,1],
[1,0,2,1,0,0,1,0,0,1,1],
[439,314,440,435,119,654,773,549,160,316,222],
[1,0,1,1,0,0,1,0,1,0,0],
[0,0,0,0,0,0,0,0,0,2,1],
[6,2,0,5,2,4,0,1,2,3,3],
[1,2,0,0,0,0,0,0,0,0,1]]}
PENDING['pike'][4]=[
[174,216,84,6091],
[0,2,0,17],
[0,0,0,15],
[1,0,0,11],
[288,402,201,6504],
[0,0,0,9],
[0,0,1,7],
[1,4,0,52],
[0,1,1,9]]
VALUES['pike']=PENDING.pop('pike')
def main():
    index={s['source_id']:s for s in json.loads((OUT/'native-2024-senate-reviewed-84views.json').read_text())['sources']};views=[];flat=[];counts=Counter()
    for county,pv in VALUES.items():
        sid='sos-2024-county-'+county;s=index[sid];assert sha(original(sid))==s['raw_sha256'];assert set(pv)=={p['page'] for p in s['pages']};sums=Counter();total={};pages=[]
        for p in s['pages']:
            meta=json.loads(gzip.decompress((OUT/'extracts/reviewed-replay'/sid/f'p{p["page"]:04d}.json.gz').read_bytes()));assert sha((BASE/meta['raster_path']).read_bytes())==meta['raster_sha256'];roles=[c['role'] for c in p['columns']];rows=pv[p['page']];assert len(rows) in [9,11];typed=len(rows)
            if typed==9:rows=rows+[[c['fields'][name]['value'] for c in p['columns']] for name in NAMES[-2:]]
            fs=[];counts['native_constituents']+=roles.count('source_native_reporting_constituent');counts['source_TOTAL_columns']+=roles.count('source_TOTAL');counts['unused_blank_columns']+=roles.count('unused_template_column');counts['source_pages']+=1
            for name,vs in zip(NAMES,rows):
                assert len(vs)<=len(roles);vs=vs+[None]*(len(roles)-len(vs));basis='Every glyph directly read on complete original page' if typed==11 or name not in NAMES[-2:] else 'Earlier own original-reviewed Senate fields reused at same raw hash/page/header grid, not peer derivative';fs.append(dict(candidate=name,values=vs,basis=basis))
                for c,v in zip(p['columns'],vs):
                    role=c['role']
                    if role=='unused_template_column':assert v is None;counts['unused_null_positions']+=1
                    else:
                        assert isinstance(v,int) and v>=0;counts['numeric_positions']+=1
                        if role=='source_native_reporting_constituent':sums[name]+=v
                        elif role=='source_TOTAL':total[name]=v
                        else:raise ValueError(role)
                    flat.append(dict(key=f'{s["county_fips"]}:{sid}:p{p["page"]}:c{c["source_column"]}',county_fips=s['county_fips'],source_id=sid,raw_sha256=s['raw_sha256'],source_page=p['page'],source_column=c['source_column'],literal_native_label=c['label_literal'],literal_printed_id=c.get('printed_native_id'),role=role,candidate=name,value=v,source_header_bounds_pixels=json.dumps(c['header_bounds']),full_original_render_path=meta['raster_path'],render_sha256=meta['raster_sha256'],render_size=json.dumps(p['render_size']),rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],numeric_position_scope='Whole original page candidate row in this physical source column; machine crop polygons not accepted'))
            pages.append(dict(page=p['page'],render_size=p['render_size'],full_original_render_path=meta['raster_path'],render_sha256=meta['raster_sha256'],roles=roles,headers=[{k:c[k] for k in ['source_column','label_literal','role','header_bounds']} for c in p['columns']],fields=fs))
        assert dict(sums)==total==dict(zip(NAMES,EXPECTED[county])),(county,sums,total,EXPECTED[county]);views.append(dict(source_id=sid,county=s['county'],county_fips=s['county_fips'],raw_sha256=s['raw_sha256'],preferred82=False,additive_to_preferred82=False,pages=pages,controls=dict(all11_native_candidate_sums=dict(sums),printed_TOTAL=total,all11_vectors_close=True),qualification='Independent original alternative publication only; source native partition not joined/deduplicated with updated or vendor views; no chronology or current geography inference. Unprinted generic/ballot/method controls remain unknown.'))
    counts['source_views']=len(views);save(OUT/'native-alternative-allfield-readings.json',dict(qualification='Original-only all11 candidate readings for two earlier SEMS publication alternatives, nonadditive to preferred82.',sources=views,counts=dict(counts),pending_sources=PENDING,complete_two_alternative_views=len(views)==2));writecsv(OUT/'native-alternative-allfield-candidate-votes.csv',flat);print('Alternative original all11 coverage',dict(counts))
if __name__=='__main__':main()
