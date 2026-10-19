"""Source-label/printed-rule positions, no candidate votes or peer fields."""
import argparse,gzip,json,math
from collections import Counter
from PIL import Image,ImageDraw
from sources import OUT,BASE,save,sha
from extract_replay_president import NAMES,transform
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',choices=['v8','v9'],default='v8');args=ap.parse_args();version=args.version
    inv=json.loads((OUT/'source/presidential-original-label-inventory.json').read_text());pages=[];status=Counter();cards=[];hints=[]
    for p in inv['pages']:
        old=json.loads(gzip.decompress((OUT/'extracts/native-v4'/p['source_id']/f'p{p["page"]:04d}.json.gz').read_bytes()));w,h=p['render_size'];left=p['original_crop_box'][2]-3;transformed=[transform(left*old['render_size'][0]/w,y,old,p)[1] for y in old.get('grid_y',[])];fields=[]
        for i,f in enumerate(p['fields']):
            hits=f['raw_source_label_hits'];r=f.copy();bounds=None
            if len(hits)==1:
                box=hits[0]['original_raster_box'];cy=(box[1]+box[3])/2;before=[y for y in transformed if y<box[1]+2];after=[y for y in transformed if y>box[3]-2];top=max(before) if before else None;bottom=min(after) if after else None
                if top is not None and bottom is not None and 20<bottom-top<(h*.15 if version=='v9' else 160):bounds=[0,top,w,bottom];r.update(status='unique_fresh_original_label_and_projected_printed_rules',row_bounds=bounds)
                else:r.update(status='original_label_row_bounds_unresolved',preceding_rule=top,following_rule=bottom)
            status[r['status']]+=1;fields.append(r)
            if bounds is None:
                prior=[a for a in p['fields'][:i] if len(a['raw_source_label_hits'])==1];nxt=[a for a in p['fields'][i+1:] if len(a['raw_source_label_hits'])==1];cy=None
                if prior and nxt:
                    j=NAMES.index(prior[-1]['candidate']);k=NAMES.index(nxt[0]['candidate']);a=prior[-1]['raw_source_label_hits'][0]['original_raster_box'];b=nxt[0]['raw_source_label_hits'][0]['original_raster_box'];cy=(a[1]+a[3])/2+(i-j)/(k-j)*((b[1]+b[3]-a[1]-a[3])/2)
                else:
                    existing=[z for z in old['fields'] if z['field']==f['candidate']]
                    if len(existing)==1:cy=transform(left*old['render_size'][0]/w,sum(existing[0]['row_bounds'][1::2])/2,old,p)[1]
                    elif nxt:
                        k=NAMES.index(nxt[0]['candidate']);b=nxt[0]['raw_source_label_hits'][0]['original_raster_box'];cy=(b[1]+b[3])/2-(k-i)*h*.045
                    elif prior:
                        j=NAMES.index(prior[-1]['candidate']);a=prior[-1]['raw_source_label_hits'][0]['original_raster_box'];cy=(a[1]+a[3])/2+(i-j)*h*.045
                if cy is None:continue
                radius=.06*h if version=='v9' else 85;im=Image.open(BASE/p['full_original_render_path']);target=[0,max(0,math.floor(cy-radius)),int(left+2),min(h,math.ceil(cy+radius))];crop=im.crop(tuple(target));scale=min(720/crop.width,170/crop.height);crop=crop.resize((round(crop.width*scale),round(crop.height*scale)));card=Image.new('RGB',(840,230),'white');d=ImageDraw.Draw(card);cardno=len(cards)+1;d.text((5,5),f'{cardno}. {p["source_id"]} PDF{p["page"]}; {f["candidate"]} TARGET ONLY',fill='black');card.paste(crop,(90,35))
                tick=max(25,round(h/1500)*25) if version=='v9' else 25
                for y in range(math.ceil(target[1]/tick)*tick,target[3],tick):pos=35+(y-target[1])*scale;d.text((5,pos),str(y),fill='black');d.line((55,pos,85,pos),fill='black')
                cards.append(card);hints.append(dict(card=cardno,source_id=p['source_id'],page=p['page'],candidate=f['candidate'],source_box=target,render_size=p['render_size'],full_original_render_path=p['full_original_render_path'],render_sha256=p['render_sha256'],raw_status=r['status'],qualification='Neighbor anchors/prior rule grid provide a target only, never field identity. Original printed candidate label must be read; do not accept expected order.'))
        pages.append(p|dict(projected_original_grid_y=transformed,fields=fields))
    for start in range(0,len(cards),6):
        atlas=Image.new('RGB',(1680,690),'#eeeeee')
        for j,c in enumerate(cards[start:start+6]):atlas.paste(c,((j%2)*840,(j//2)*230))
        atlas.save(OUT/'qa'/f'presidential-original-label-repair-{version}-atlas-{start//6+1}.png')
    save(OUT/f'source/presidential-original-row-proposals-{version}.json',dict(qualification='Own source name/physical rule proposals only. Unknown labels/bounds require original visual reading. No vote/control/peer fields; no acceptance by candidate order alone.',source_pages=len(pages),status_counts=dict(status),pages=pages));save(OUT/f'source/presidential-original-label-repair-pointers-{version}.json',hints);print('211 source pages;',dict(status),';',len(cards),'original label repair cards')
if __name__=='__main__':main()
