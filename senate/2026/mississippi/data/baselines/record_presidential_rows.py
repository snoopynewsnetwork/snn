"""Independent original Jackson candidate-label/row-geometry repair.

All9 labels on EACH of original p2/3/4 visually read from a direct original
mosaic. Numeric column rules independently detected; no candidate values are
entered here and no missing row is assigned a zero.
"""
import gzip,json
from sources import OUT,save
from extract_replay_president import NAMES
def main():
    bounds={2:[576,628,676,724,772,820,866,914,962,1010],3:[578,630,676,724,772,820,866,914,962,1010],4:[576,628,676,724,772,818,866,914,962,1010]};rows=[]
    for pg,ys in bounds.items():
        p=OUT/'extracts/reviewed-replay/sos-2024-county-jackson'/f'p{pg:04d}.json.gz';x=json.loads(gzip.decompress(p.read_bytes()))
        for i,n in enumerate(NAMES):rows.append(dict(source_id=x['source_id'],raw_sha256=x['raw_sha256'],page=pg,candidate=n,render_size=x['render_size'],rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],row_bounds=[0,ys[i],x['render_size'][0],ys[i+1]],source_row=i+1,source_row_basis='Candidate order within presidential block, not printed rowID. Each label independently visually read on each original page; numeric horizontal rules independently detected.',raster_path=x['raster_path'],raster_sha256=x['raster_sha256'],evidence='qa/jackson-original-presidential-labels-p2-4.png'))
    save(OUT/'source/native-presidential-row-repairs.json',dict(readings=rows,qualification='Original field label/physical row repair only. Old v4 failed to locate ANY Jackson candidate row. No vote values supplied, no template-only inferred field order.'))
if __name__=='__main__':main()
