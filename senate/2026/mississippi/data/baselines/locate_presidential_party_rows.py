"""Original2024 printed party-line anchors for numeric reading regions.

Candidate name identity is independently source-read, including manual repairs.
Literal party labels align to the printed numeric line, avoiding a broken
horizontal rule across a multiline candidate paragraph. No vote enters locator.
"""
import gzip,json,re
from collections import Counter
from sources import OUT,BASE,save
from extract_replay_president import NAMES
PARTIES=['Democrat','Libertarian','Green','Constitution','Republican','Independent','Independent','Independent','Independent']
def main():
    inv=json.loads((OUT/'source/presidential-original-label-inventory.json').read_text());manual=json.loads((OUT/'source/presidential-original-label-manual-readings.json').read_text());mi={(r['source_id'],r['page'],r['candidate']):r for r in manual['readings']};rows=[];pending=[];status=Counter();duplicate=[]
    for p in inv['pages']:
        path=OUT/'extracts/presidential-original-labels'/f'{p["source_id"]}-p{p["page"]:04d}.json.gz';a=json.loads(gzip.decompress(path.read_bytes()));w,h=p['render_size'];left=p['original_crop_box'][2]-3;used=[]
        for f,party in zip(p['fields'],PARTIES):
            m=mi.get((p['source_id'],p['page'],f['candidate']));hits=f['raw_source_label_hits'];cy=m['manual_original_label_y'] if m else sum(hits[0]['original_raster_box'][1::2])/2 if len(hits)==1 else None
            candidates=[]
            if cy is not None:
                for z in a['source_observations_with_original_bounds']:
                    b=z['original_raster_box'];zy=(b[1]+b[3])/2
                    if b[0]>.50*left and re.search(r'\b'+party+r'\b',z['literal'],re.I) and abs(zy-cy)<.035*h:candidates.append(z)
            candidates.sort(key=lambda z:abs(sum(z['original_raster_box'][1::2])/2-cy));chosen=candidates[0] if candidates else None
            if chosen:
                b=chosen['original_raster_box'];y=(b[1]+b[3])/2;half=max((b[3]-b[1])*.65+4,h*.010);bounds=[0,max(0,y-half),w,min(h,y+half)];status['unique_nearest_literal_party_line']+=1;ident=tuple(b)
                if ident in used:duplicate.append(dict(source_id=p['source_id'],page=p['page'],candidate=f['candidate'],party=party,shared_party_box=b))
                used.append(ident)
                rows.append(dict(source_id=p['source_id'],raw_sha256=p['raw_sha256'],page=p['page'],candidate=f['candidate'],source_row=NAMES.index(f['candidate'])+1,source_row_scope='Printed presidential-candidate sequence number, not full table row/current ID',row_bounds=bounds,render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],raster_path=p['full_original_render_path'],raster_sha256=p['render_sha256'],candidate_label_source_hits=hits,manual_candidate_label_reading=m,expected_historical_printed_party_identity=party,original_party_literal=chosen['literal'],original_party_box=b,party_candidates=candidates,qualification='Original literal party line locates numeric glyph line only. Candidate identity separately source-read; all independent candidates stay named. Does not map2026parties/identities or imply numerical acceptance.'))
            else:status['printed_party_anchor_unresolved']+=1;pending.append(dict(source_id=p['source_id'],page=p['page'],candidate=f['candidate'],party=party,source_candidate_y=cy))
    save(OUT/'source/native-presidential-party-row-proposals-v14.json',dict(qualification='Original literal party/numeric-line targeting aids only, no vote/control/peer field. Candidate labels independently located from unchanged original crops/manual label repairs. Preserve unknown/multiple/reused anchors, no numeric/source-geometry acceptance.',status_counts=dict(status),readings=rows,pending=pending,reused_party_anchor_positions=duplicate));print(dict(status),'reused',len(duplicate));print(pending)
if __name__=='__main__':main()
