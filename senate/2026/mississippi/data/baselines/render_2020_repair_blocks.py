"""Original whole header/candidate blocks for2020 failed TOTAL/candidate aids.

Fresh independent whole-page Vision locates candidate labels; complete original
native headers and Senate blocks are displayed. No typed numeric values or
county control is used to target a source cell.
"""
import gzip,json,re
from PIL import Image,ImageDraw
from sources import OUT,BASE,save
from compile_vision_grid import pixels
PAT=[r'espy',r'hyde.?smith',r'jimmy|edwards']
def main():
    ledger=json.loads((OUT/'county-2020-readings.json').read_text());keys=[r['source_id'] for r in ledger['other_packet_gaps']]+[r['source_id'] for r in ledger['reading_card_repair_gaps']];cards=[];pointers=[];unlocated=[]
    for key in keys:
        candidates=[]
        for path in sorted((OUT/'extracts/vision-pages'/key).glob('*.json.gz')):
            v=json.loads(gzip.decompress(path.read_bytes()));w,h=v['render_size'];labels=[]
            for pat in PAT:
                hit=[z for z in v['observations'] if re.search(pat,z['text'],re.I) and pixels(z,w,h)[0]<.5*w]
                if len(hit)==1:labels.append(dict(pattern=pat,literal=hit[0]['text'],box=pixels(hit[0],w,h)))
            if len(labels)>=2:candidates.append((v,labels))
        if not candidates:unlocated.append(key);continue
        v,labels=max(candidates,key=lambda z:z[0]['page']);w,h=v['render_size'];im=Image.open(BASE/v['raster_path']);old=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/f'p{v["page"]:04d}.json.gz').read_bytes()));hc=old.get('columns',[]);header=[0,min(c['bounds'][1] for c in hc)-8,w,max(c['bounds'][3] for c in hc)+8] if hc else [0,int(.14*h),w,int(.34*h)]
        top=min(z['box'][1] for z in labels)-14;bottom=max(z['box'][3] for z in labels)+14
        if not any(re.search(r'jimmy|edwards',z['literal'],re.I) for z in labels):bottom+=80
        box=[0,max(0,int(top)),w,min(h,int(bottom))];head=im.crop(tuple(header));block=im.crop(tuple(box));head.thumbnail((1680,220));block.thumbnail((1680,250));card=Image.new('RGB',(1700,510),'white');d=ImageDraw.Draw(card);i=len(cards)+1;d.text((8,5),f'{i}. {key}; original PDF page {v["page"]} — complete source header / candidate block',fill='black');card.paste(head,(8,28));card.paste(block,(8,255));cards.append(card);pointers.append(dict(source_id=key,raw_sha256=v['source_raw_sha256'],page=v['page'],render_size=v['render_size'],rotation_ccw=v['rotation_ccw'],deskew_angle_ccw=v['deskew_angle_ccw'],raster_path=v['raster_path'],raster_sha256=v['raster_sha256'],original_header_box=header,original_candidate_block_box=box,fresh_original_candidate_label_anchors=labels,review_card=i,qualification='Last original page with at least2fresh Senate label anchors. Target proposal only; displayed original TOTAL/field labels must be visually verified, no control-fitted position.'))
    for j in range(0,len(cards),4):
        sub=cards[j:j+4];atlas=Image.new('RGB',(1700,510*len(sub)),'white')
        for k,c in enumerate(sub):atlas.paste(c,(0,k*510))
        atlas.save(OUT/'qa'/f'2020-repair-whole-blocks-{j//4+1}.png')
    save(OUT/'source/2020-repair-block-pointers.json',pointers);save(OUT/'source/2020-repair-unlocated.json',unlocated);print(len(pointers),'wholeoriginal header+candidateblockcards;',len(unlocated),'unlocated')
if __name__=='__main__':main()
