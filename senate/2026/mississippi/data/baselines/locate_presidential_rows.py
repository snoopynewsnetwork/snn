"""Fresh own-original candidate anchors and printed-rule row proposals.

No candidate numbers, county controls or peer fields enter this locator. All
unlocated/ambiguous labels and failed printed-rule proposals remain explicit.
These are reading aids requiring source review, never assumed zeros/order.
"""
import argparse,gzip,json,re
from collections import Counter
import numpy as np
from PIL import Image
from sources import OUT,BASE,save
from compile_vision_grid import pixels
from extract_replay_president import NAMES,source_layouts
TOKENS=['Harris','Oliver','Stein','Terry','Trump','Shiva','Claudia','Kennedy','Sonski']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',choices=['v1','v2'],default='v1');a=ap.parse_args()
    layouts,accepted=source_layouts('native-2024-senate-reviewed-84views.json');pages=[];status=Counter()
    for s in layouts:
        key=s['source_id']
        for p in s['pages']:
            path=OUT/'extracts/reviewed-replay'/key/f'p{p["page"]:04d}.json.gz';raw=json.loads(gzip.decompress(path.read_bytes()));w,h=raw['render_size'];im=Image.open(BASE/raw['raster_path']);array=np.asarray(im.convert('L'));left=min(c['header_bounds'][0] for c in p['columns']);right=max(c['header_bounds'][2] for c in p['columns']);upper=min(c['header_bounds'][3] for c in p['columns']);senate_top=min(c['candidate_bounds']['Ty Pinkins'][1] for c in p['columns']);dark=array[:,int(left):int(right)]<(230 if a.version=='v2' else 180);spread=dark.copy()
            if a.version=='v2':
                for dy in range(1,4):spread[dy:]|=dark[:-dy];spread[:-dy]|=dark[dy:]
            lines=np.flatnonzero(spread.mean(axis=1)>(.45 if a.version=='v2' else .55));clusters=[]
            for y in lines:
                if not clusters or y>clusters[-1][-1]+2:clusters.append([int(y)])
                else:clusters[-1].append(int(y))
            rules=[sum(ys)/len(ys) for ys in clusters];fields=[]
            for name,token in zip(NAMES,TOKENS):
                found=[]
                for z in raw['words']:
                    b=pixels(z,w,h)
                    if re.fullmatch(re.escape(token)+r'[,.:;]?',z['text'],re.I) and b[2]<left+4 and upper<b[1]<senate_top:found.append(dict(literal=z['text'],box=b,confidence=z['confidence']))
                rec=dict(candidate=name,anchor_token=token,raw_anchors=found,value_scope='No candidate vote or peer field read by this locator')
                if len(found)==1:
                    anchor=found[0]['box'];y=(anchor[1]+anchor[3])/2;before=[a for a in rules if upper-8<a<anchor[1]];after=[a for a in rules if anchor[3]<a<senate_top];top=max(before) if before else None;bottom=min(after) if after else None
                    if top is not None and bottom is not None and 18<bottom-top<150:rec.update(status='unique_original_label_and_printed_rule_proposal',source_row_bounds=[0,top,w,bottom])
                    else:rec.update(status='label_found_printed_rule_bounds_unresolved',prior_rule=top,next_rule=bottom)
                else:rec.update(status='candidate_label_missing' if not found else 'ambiguous_candidate_label')
                status[rec['status']]+=1;fields.append(rec)
            pages.append(dict(source_id=key,raw_sha256=s['raw_sha256'],page=p['page'],render_size=raw['render_size'],rotation_ccw=raw['rotation_ccw'],deskew_angle_ccw=raw['deskew_angle_ccw'],raster_path=raw['raster_path'],raster_sha256=raw['raster_sha256'],source_candidate_label_x_max=left,source_native_header_bottom=upper,source_Senate_top=senate_top,detected_rules=rules,fields=fields,qualification='Independent source label/rule positions only, not accepted from nine-row order or county candidate closure. Separate presidential-only/vendor pages remain outside this Senate-page locator.'))
    save(OUT/('source/native-presidential-fresh-row-proposals-v2.json' if a.version=='v2' else 'source/native-presidential-fresh-row-proposals.json'),dict(qualification='Own original candidate label / physical printed-rule proposals for reviewed Senate-native pages. No numerical values/peer derivatives used; ambiguous/missing fields not inferred.',version=a.version,rule_detection=dict(dark_threshold=230,vertical_spread_pixels=3,min_source_grid_fraction=.45) if a.version=='v2' else dict(dark_threshold=180,vertical_spread_pixels=0,min_source_grid_fraction=.55),source_pages=len(pages),status_counts=dict(status),pages=pages));print(len(pages),'pages',dict(status))
if __name__=='__main__':main()
