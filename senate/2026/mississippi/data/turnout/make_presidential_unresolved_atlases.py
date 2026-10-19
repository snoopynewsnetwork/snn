"""Render untouched original 2024 cells still unresolved by two OCR passes.

Every card has both its full original cell and a magnified digit interior.
The index preserves source ID/hash/page/physical bounds and candidate position.
"""
import gzip,json
from PIL import Image,ImageDraw,ImageOps
from acquire_sources import OUT,savejson
from replay_presidential_digit_regions import original_page,digit_region

def main():
    source=OUT/'presidential-null-digit-region-aid.json.gz'
    data=json.loads(gzip.decompress(source.read_bytes()))
    items=[x for x in data['readings'] if x['second_ocr']['value'] is None]
    target=OUT/'qa/presidential-unresolved-atlases';target.mkdir(exist_ok=True)
    index=[];cache={}
    for start in range(0,len(items),100):
        group=items[start:start+100];page_no=start//100+1
        canvas=Image.new('RGB',(1600,1400),'white');draw=ImageDraw.Draw(canvas)
        for j,x in enumerate(group):
            sid=x['source_id'];page=x['page'];key=(sid,page)
            if key not in cache:
                # Original geometry record contains only source positions.
                p=OUT/'extracts/physical-native-v3'/f'{sid}.json.gz'
                d=json.loads(gzip.decompress(p.read_bytes()))
                record=next(z for z in d['pages'] if z['page']==page)
                cache[key]=original_page(sid,page,record)
                if len(cache)>3:cache.pop(next(iter(cache)))
            im=cache[key];full=im.crop(tuple(x['bounds']));digit=digit_region(im,x['bounds'])
            full.thumbnail((145,75));digit.thumbnail((145,42))
            cx=(j%10)*160;cy=(j//10)*140
            draw.text((cx+3,cy+1),f'{start+j+1:04d} {sid.split("-")[-1][:12]}',fill='black')
            draw.text((cx+3,cy+16),f'p{page}c{x["source_column"]} {x["candidate"][:12]}',fill='black')
            canvas.paste(full,(cx+4,cy+32));canvas.paste(digit,(cx+4,cy+107))
            index.append(dict(index=start+j+1,atlas=page_no,position=j+1,source_id=sid,source_raw_sha256=x['raw_sha256'],source_page=page,source_column=x['source_column'],candidate=x['candidate'],original_bounds=x['bounds'],first_ocr_value=x['original_value'],second_ocr_value=x['second_ocr']['value'],original_image=str((target/f'atlas-{page_no:03d}.png').relative_to(OUT.parent.parent))))
        canvas.save(target/f'atlas-{page_no:03d}.png');cache.clear()
    savejson(target/'index.json',dict(scope='Direct original image visual review queue; unresolved values are null, not zero.',count=len(index),cards=index))
    print('Original unresolved presidential cards:',len(index),'atlases:',(len(index)+99)//100)

if __name__=='__main__':main()
