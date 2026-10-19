"""Independent original Union profile source positions/text and review cards.

Only original page locations are shared hints. All text/boxes/raster glyphs are
extracted anew from hash-verified original bytes; no peer label/value is read.
"""
import gzip,io,json,re
import fitz
from PIL import Image,ImageDraw
from sources import OUT,BASE,original,sha,save
FIELDS=['registration','ballots_cast','blank_ballots','printed_turnout','pres_Harris','pres_Oliver','pres_Stein','pres_Terry','pres_Trump','pres_Shiva','pres_Claudia','pres_Kennedy','pres_Sonski','pres_generic_write_in','pres_contest_total','sen_Pinkins','sen_Wicker','sen_generic_write_in','sen_contest_total']
def main():
    key='sos-2024-county-union';raw=original(key);assert sha(raw)=='19a5a0a1138eda18230011669318540099456001a6c1406709743a4dcb384a09';doc=fitz.open(stream=raw,filetype='pdf');folder=OUT/'qa/union-independent-profiles';folder.mkdir(exist_ok=True);rows=[];cards=[]
    for i,page in enumerate(range(16,55,2),1):
        p=doc[page-1];txt=p.get_text();heads=p.search_for('Statistics');nextoffice=p.search_for('1st Congressional');assert len(heads)==1 and len(nextoffice)==1;top=heads[0].y1;bottom=nextoffice[0].y0
        numeric=[w for w in p.get_text('words') if 150<w[0]<230 and top<w[1]<bottom and re.fullmatch(r'[0-9.,]+%?',w[4])];numeric.sort(key=lambda w:w[1]);assert len(numeric)==19,(page,len(numeric),numeric)
        png=p.get_pixmap(matrix=fitz.Matrix(2.1,2.1),colorspace=fitz.csGRAY).tobytes('png');dest=folder/f'p{page:02d}-original.png';dest.write_bytes(png);im=Image.open(io.BytesIO(png));header=txt.split('Union County',1)[1].split('Statistics',1)[0].strip();card=Image.new('RGB',(760,650),'white');d=ImageDraw.Draw(card);d.text((8,5),f'{i}. ORIGINAL Union PDF{page}; text-layer header:{header}',fill='black');headercrop=im.crop((50,180,850,224));headercrop.thumbnail((735,65));card.paste(headercrop,(8,25));values=[]
        for j,(field,w) in enumerate(zip(FIELDS,numeric)):
            box=list(w[:4]);crop=im.crop((int((box[0]-2)*2.1),int((box[1]-2)*2.1),int((box[2]+2)*2.1),int((box[3]+2)*2.1)));crop=crop.resize((crop.width*2,crop.height*2));crop.thumbnail((290,28));y=95+j*28;d.text((10,y+5),field,fill='black');card.paste(crop,(320,y));values.append(dict(field=field,text_layer_literal=w[4],text_layer_word_bounds_points=box,value_proposal=int(w[4]) if w[4].isdigit() else None,proposal_status='Integer text-layer reading awaiting original-glyph review' if w[4].isdigit() else 'Printed turnout text' if field=='printed_turnout' else 'Punctuation ambiguity requires original glyph reading; no normalization'))
        cards.append(card);rows.append(dict(source_id=key,raw_sha256=sha(raw),source_page=page,text_layer_header_literal=header,raw_complete_page_text=txt,full_original_render_path=str(dest.relative_to(BASE)),render_sha256=sha(png),render_size=list(im.size),render_scale=2.1,fields=values,qualification='Independent text-layer source observations and original-only glyph cards. No accepted numeric values from peer tables or county residual. Other offices remain in complete original bytes/raw page text, not duplicated as unrelated numeric tables.'))
    for n in range(0,20,4):
        atlas=Image.new('RGB',(1520,1300),'#eeeeee')
        for j,c in enumerate(cards[n:n+4]):atlas.paste(c,((j%2)*760,(j//2)*650))
        atlas.save(folder/f'original-field-cards-{n//4+1}.png')
    save(OUT/'union-native-profile-original-extract.json',dict(source_id=key,raw_sha256=sha(raw),source_pages=20,required_fields=19,observations=380,qualification='Independent original source extraction and printed-number review aids only; profiles are distinct vendor-native source views, no SEMS/current crosswalk.',pages=rows));print('20source profiles/380requiredoriginalfieldglyphs;nopeerfieldsread')
if __name__=='__main__':main()
