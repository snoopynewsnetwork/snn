"""Original-only field-label strips for missing/rotated presidential locators."""
import gzip,json
from PIL import Image,ImageDraw
from sources import OUT,BASE,save,sha
from extract_replay_president import source_layouts
def main():
    layouts,_=source_layouts('native-2024-senate-reviewed-84views.json');missing={'itawamba','scott','amite','webster','winston'};cards=[];pointers=[]
    for s in layouts:
        key=s['source_id']
        if key.removeprefix('sos-2024-county-') not in missing:continue
        for p in s['pages']:
            raw=json.loads(gzip.decompress((OUT/'extracts/reviewed-replay'/key/f'p{p["page"]:04d}.json.gz').read_bytes()));im=Image.open(BASE/raw['raster_path']);left=min(c['header_bounds'][0] for c in p['columns']);top=min(c['header_bounds'][3] for c in p['columns'])-10;bottom=min(c['candidate_bounds']['Ty Pinkins'][1] for c in p['columns']);box=[0,max(0,top),min(im.width,left+135),bottom];crop=im.crop(tuple(box));scale=min(690/crop.width,880/crop.height);crop=crop.resize((round(crop.width*scale),round(crop.height*scale)));card=Image.new('RGB',(780,940),'white');d=ImageDraw.Draw(card);i=len(cards)+1;d.text((6,5),f'{i}. {key} originalPDF{p["page"]}; source y ticks',fill='black');card.paste(crop,(70,35))
            for y in range((int(box[1])//25+1)*25,int(box[3]),25):pos=35+(y-box[1])*scale;d.text((5,pos),str(y),fill='black');d.line((55,pos,67,pos),fill='black')
            cards.append(card);pointers.append(dict(source_id=key,raw_sha256=s['raw_sha256'],page=p['page'],render_size=raw['render_size'],rotation_ccw=raw['rotation_ccw'],deskew_angle_ccw=raw['deskew_angle_ccw'],raster_path=raw['raster_path'],raster_sha256=raw['raster_sha256'],source_box=box,card=i,qualification='Original field labels/first native columns only; margin source-y ticks are a position aid, no vote/control/peer text overlaid.'))
    for start in range(0,len(cards),2):
        atlas=Image.new('RGB',(1560,940),'#eeeeee')
        for j,c in enumerate(cards[start:start+2]):atlas.paste(c,(j*780,0))
        atlas.save(OUT/'qa'/f'presidential-original-row-labels-{start//2+1}.png')
    save(OUT/'source/presidential-original-row-review-pointers.json',pointers);print(len(cards),'originalfieldlabelstrips with source-only ticks')
if __name__=='__main__':main()
