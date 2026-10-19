"""Original source labels with physical row windows, no vote/control input."""
import argparse,json
from sources import OUT,save
from extract_replay_president import manual_row,NAMES
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',choices=['v10','v11'],default='v10');args=ap.parse_args()
    raw=json.loads((OUT/'source/presidential-original-row-proposals-v9.json').read_text());manual=json.loads((OUT/'source/presidential-original-label-manual-readings.json').read_text());assert not manual['unreviewed_cards'];index={(r['source_id'],r['page'],r['candidate']):r for r in manual['readings']};rows=[];pending=[]
    for p in raw['pages']:
        for i,f in enumerate(p['fields']):
            key=(p['source_id'],p['page'],f['candidate']);m=index.get(key);bounds=f.get('row_bounds');basis='Unique fresh original candidate-name OCR plus projected source printed rules; numeric acceptance separate';evidence=None
            if args.version=='v11' and not m:
                hits=f['raw_source_label_hits'];assert len(hits)==1;box=hits[0]['original_raster_box'];cy=(box[1]+box[3])/2;before=[y for y in p['projected_original_grid_y'] if y<cy];after=[y for y in p['projected_original_grid_y'] if y>cy];top=max(before) if before else None;bottom=min(after) if after else None;bounds=[0,top,p['render_size'][0],bottom] if top is not None and bottom is not None and 20<bottom-top<.15*p['render_size'][1] else None;basis='Unique fresh original candidate name center selects enclosing projected original printed rules. Raw Vision glyph boxes can extend across a neighboring rule, so their outer bbox is not treated as a whole field. Numeric acceptance separate.'
            if m:
                cy=m['manual_original_label_y'];before=[y for y in p['projected_original_grid_y'] if y<cy];after=[y for y in p['projected_original_grid_y'] if y>cy];top=max(before) if before else None;bottom=min(after) if after else None
                if top is not None and bottom is not None and 20<bottom-top<.15*p['render_size'][1]:bounds=[0,top,p['render_size'][0],bottom];basis='Original printed candidate name visually read, interior source-y point selects enclosing independently detected source rules';evidence=m['evidence_path']
                else:
                    v5=manual_row(p['source_id'],p['page'],f['candidate'],'v5')
                    if v5 and v5['render_size']==p['render_size'] and v5['rotation_ccw']==p['rotation_ccw'] and v5['deskew_angle_ccw']==p['deskew_angle_ccw']:bounds=v5['row_bounds'];basis='Original candidate label re-read; exact same source raster frame as earlier independently original-reviewed v5 row window';evidence=m['evidence_path']
                    elif p['source_id']=='sos-2024-county-choctaw' and p['page']==3:
                        endpoints=[500,569,636,702,769,835,902,968,1034,1100];bounds=[0,endpoints[i],p['render_size'][0],endpoints[i+1]];basis='All nine complete original candidate labels and their bordering rules visually read on source-y ticked cards. Estimated complete-field windows, not exact printed-rule polygons.';evidence=m['evidence_path']
                    else:bounds=None
            if bounds is None:pending.append(dict(source_id=p['source_id'],page=p['page'],candidate=f['candidate']));continue
            assert 0<=bounds[1]<bounds[3]<=p['render_size'][1];rows.append(dict(source_id=p['source_id'],raw_sha256=p['raw_sha256'],page=p['page'],candidate=f['candidate'],source_row=i+1,source_row_scope='Printed presidential-candidate sequence position on this original page, not overall table-row ID or current precinct ID',row_bounds=bounds,render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],raster_path=p['full_original_render_path'],raster_sha256=p['render_sha256'],raw_original_label_observations=f['raw_source_label_hits'],manual_label_reading=m,basis=basis,evidence_path=evidence))
    save(OUT/f'source/native-presidential-row-repairs-{args.version}.json',dict(qualification='1899 source presidential label/row positions only, no numerical values, peer field or county residual used. Fresh original label OCR identifies1871 source names;28 missing labels and18 unresolved row windows have separate original visual evidence. Candidate ordinal is explicitly a presidential sequence position, not overall source-table ID. Windows and OCR fields remain aids pending original numeric verification.',version=args.version,readings=rows,pending=pending));assert not pending,pending;assert len(rows)==1899;print('1899 original-label row positions,211pages; no vote/control input;',args.version)
if __name__=='__main__':main()
