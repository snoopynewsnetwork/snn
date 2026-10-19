"""Independent original presidential rows on the bounded native replay pages.

Candidate row labels/bounds come from OWN full-original extraction, transformed
between owned rasters. Native x bounds are targeting hints only. No peer
presidential value is read. All words, row transforms and unresolved fields stay.
"""
import argparse,gzip,json,math,re,csv
from functools import lru_cache
from collections import defaultdict
from sources import OUT,BASE,save
from replay_reviewed_native import hint_snapshot
from compile_vision_grid import pixels
from extract_native import cell_key
NAMES=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump','Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski']
def rotate(x,y,w,h,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a));dx=x-w/2;dy=y-h/2;return w/2+c*dx+s*dy,h/2-s*dx+c*dy
def transform(x,y,old,new):
    ow,oh=old['render_size'];nw,nh=new['render_size'];a,b=rotate(x,y,ow,oh,-old['deskew_angle_ccw']);return rotate(a*nw/ow,b*nh/oh,nw,nh,new['deskew_angle_ccw'])
@lru_cache(None)
def row_repair_index(tag):
    path=OUT/('source/native-presidential-row-repairs.json' if tag is None else f'source/native-presidential-row-repairs-{tag}.json')
    if not path.exists():return {}
    return {(r['source_id'],r['page'],r['candidate']):r for r in json.loads(path.read_text())['readings']}
def manual_row(key,page,name,tag=None):
    if tag in ['v5','v10','v11','v12','v14']:
        found=row_repair_index(tag).get((key,page,name))
        if found:return found
    return row_repair_index(None).get((key,page,name))
def source_layouts(ledger_name=None):
    native=json.loads((OUT/(ledger_name or 'native-2024-senate-reviewed.json')).read_text());accepted={s['source_id']:s for s in native['sources']}
    if not ledger_name:return hint_snapshot()['sources'],accepted
    layouts=[]
    for s in native['sources']:
        pages=[]
        for p in s['pages']:
            cols=[]
            for c in p['columns']:
                hb=c['header_bounds'];b=c['fields']['Ty Pinkins']['source_box'];cols.append(dict(source_column=c['source_column'],header_bounds=hb,candidate_bounds={'Ty Pinkins':[hb[0],b[1],hb[2],b[3]]}))
            pages.append({k:p[k] for k in ['page','render_size','rotation_ccw','deskew_angle_ccw']}|dict(columns=cols))
        layouts.append(dict(source_id=s['source_id'],raw_sha256=s['raw_sha256'],pages=pages))
    return layouts,accepted
def field_filename(key,tag=None):
    return f'independent-presidential-fields-{tag}.json.gz' if tag else 'independent-presidential-fields-v2.json.gz' if key=='sos-2024-county-jackson' else 'independent-presidential-fields.json.gz'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ledger');ap.add_argument('--tag');ap.add_argument('--only');a=ap.parse_args();layouts,accepted=source_layouts(a.ledger);checks=[]
    if a.only:layouts=[s for s in layouts if s['source_id'] in a.only.split(',')]
    county=defaultdict(dict)
    for r in csv.DictReader((OUT/'candidate-votes.csv').open()):
        if r['contest']=='2024-president':county[r['county']][cell_key(r['candidate_literal'])]=int(r['votes'])
    for s in layouts:
        key=s['source_id'];pages=[];sums=defaultdict(int);unresolved=defaultdict(int);totals=defaultdict(list);count=0
        for p in s['pages']:
            v=json.loads(gzip.decompress((OUT/'extracts/reviewed-replay'/key/f'p{p["page"]:04d}.json.gz').read_bytes()));old=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/f'p{p["page"]:04d}.json.gz').read_bytes()));w,h=v['render_size'];cols=[]
            ownp=next(a for a in accepted[key]['pages'] if a['page']==p['page'])
            for c in p['columns']:
                nc=next(a for a in ownp['columns'] if a['header_bounds']==c['header_bounds']);box=c['candidate_bounds']['Ty Pinkins'];left,right=box[0],box[2];fields={}
                for name in NAMES:
                    fs=[f for f in old.get('fields',[]) if f['field']==name]
                    repair=manual_row(key,p['page'],name,a.tag)
                    locator=repair if repair else old
                    if repair:fs=[dict(field=name,source_row=repair['source_row'],row_bounds=repair['row_bounds'])]
                    if len(fs)!=1:
                        fields[name]=dict(value=None,status='candidate_row_not_independently_located_not_zero',source_row_matches=len(fs));continue
                    f=fs[0];cy=(f['row_bounds'][1]+f['row_bounds'][3])/2;oldx=(left+right)/2*locator['render_size'][0]/w;_,rowcy=transform(oldx,cy,locator,v);rowheight=(f['row_bounds'][3]-f['row_bounds'][1])*h/locator['render_size'][1];tokens=[]
                    for z in v['words']:
                        b=pixels(z,w,h);cx=(b[0]+b[2])/2;y=(b[1]+b[3])/2
                        if left<cx<right and abs(y-rowcy)<.38*rowheight:tokens.append(dict(text=z['text'],box=b,confidence=z['confidence']))
                    literal=' '.join(z['text'] for z in sorted(tokens,key=lambda z:z['box'][0]));ss=literal.replace(',','').strip();value=int(ss) if re.fullmatch(r'\d+',ss) else None
                    fields[name]=dict(value=value,literal=literal,tokens=tokens,source_row=f['source_row'],source_row_scope=repair.get('source_row_scope') if repair else 'Source parser full-table row index; unresolved metadata not silently normalized',own_candidate_row_bounds=f['row_bounds'],transformed_center_y=rowcy,rowheight=rowheight,physical_x_bounds=[left,right],status='independent_original_OCR_pending_controls' if value is not None else 'blank_or_unresolved_not_zero')
                if nc['role']=='source_native_reporting_constituent':
                    count+=1
                    for n,z in fields.items():
                        if z['value'] is None:unresolved[n]+=1
                        else:sums[n]+=z['value']
                if nc['role']=='source_TOTAL':
                    for n,z in fields.items():totals[n].append(z['value'])
                cols.append(dict(source_column=c['source_column'],header_bounds=c['header_bounds'],native_label_literal=nc['label_literal'],role=nc['role'],fields=fields))
            pages.append(dict(page=p['page'],render_size=v['render_size'],rotation_ccw=v['rotation_ccw'],deskew_angle_ccw=v['deskew_angle_ccw'],raster_path=v['raster_path'],raster_sha256=v['raster_sha256'],ocr_raster_path=v['ocr_raster_path'],ocr_raster_sha256=v['ocr_raster_sha256'],own_row_locator=f'data/baselines/extracts/native-v4/{key}/p{p["page"]:04d}.json.gz',columns=cols))
        dest=OUT/'extracts/reviewed-replay'/key/field_filename(key,a.tag);dest.write_bytes(gzip.compress(json.dumps(dict(source_id=key,raw_sha256=s['raw_sha256'],qualification='Independent source-native presidential OCR on reviewed Senate-source pages ONLY. Separate presidential-only/vendor/method pages require distinct coverage audit. All9candidate rows remain distinct; no residual allocations/assumed zeros. Pending complete native review and controls.',pages=pages),ensure_ascii=False).encode(),mtime=0))
        expected=county[accepted[key]['county']];record=dict(source_id=key,native_constituents=count,sums=dict(sums),unresolved=dict(unresolved),printed_TOTAL_readings=dict(totals),county_controls=expected,differences={n:sums[n]-expected.get(n,0) for n in NAMES});checks.append(record);print(key,count,record['differences'],record['unresolved'],flush=True)
    save(OUT/(f'replay-presidential-checks-{a.tag}.json' if a.tag else 'replay-presidential-checks.json'),checks)
if __name__=='__main__':main()
