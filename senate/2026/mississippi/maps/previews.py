#!/usr/bin/env python3
"""Static render of originals, all SVG contact sheets, and an overview PDF."""
import json,gzip,fitz
from PIL import Image,ImageDraw
from acquire import ROOT,STATE,body,savejson,sha

def build():
    inputs=[]
    for k in ['lamar-precinct-pdf','desoto-voting-map-pdf','lafayette-locations','desoto-precinct-pdf','pearl-river-locations']:
        rec=json.loads((ROOT/f'source/{k}.receipt.json').read_text());raw=body(rec);doc=fitz.open(stream=raw,filetype='pdf')
        for n,p in enumerate(doc):
            scale=min(1600/p.rect.width,1600/p.rect.height);p.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False).save(str(ROOT/f'previews/{k}-p{n+1}.png'))
        (ROOT/f'previews/{k}-text.txt').write_text(''.join(p.get_text() for p in doc));inputs.append(dict(source_id=k,raw_sha256=sha(raw),pages=len(doc),rendered_pages=list(range(1,len(doc)+1))))
    c=json.loads((STATE/'data/turnout/priority-set.json').read_text());s=next(x for x in c['source_native_inventory'] if x['source_id']=='sos-2024-county-lauderdale');raw=gzip.decompress((STATE/s['original_path']).read_bytes());assert sha(raw)==s['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');doc[8].get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(str(ROOT/'previews/lauderdale-original-p9.png'));inputs.append(dict(source_id=s['source_id'],raw_sha256=sha(raw),rendered_page=9))
    s=next(x for x in json.loads((ROOT/'shared-map-references.json').read_text())['sources'] if x['id']=='maris-2020-precinct-metadata');doc=fitz.open(stream=body(s),filetype='pdf');doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(str(ROOT/'previews/maris-metadata-p1.png'));inputs.append(dict(source_id=s['id'],raw_sha256=s['raw_sha256'],rendered_page=1))
    files=sorted((ROOT/'previews').glob('*.svg'));sheets=[]
    for b in range(0,len(files),25):
        subset=files[b:b+25];sheet=Image.new('RGB',(2000,1700),'white');draw=ImageDraw.Draw(sheet)
        for j,p in enumerate(subset):
            doc=fitz.open(str(p));pix=doc[0].get_pixmap(matrix=fitz.Matrix(.38,.38),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);x=(j%5)*400;y=(j//5)*340;sheet.paste(im,(x,y));draw.text((x+8,y+311),p.stem[:48],fill='black')
        out=ROOT/f'previews/contact-{b//25+1}.png';sheet.save(out);sheets.append(out)
    for key in ['desoto-native','harrison-native','lamar-webmap-collection']:
        doc=fitz.open(str(ROOT/f'previews/{key}.svg'));doc[0].get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False).save(str(ROOT/f'previews/{key}.png'))
    # PDF is an explicitly labeled derivative contact atlas, not a native boundary export.
    pdf=fitz.open();pages=sheets+[ROOT/f'previews/{k}.png' for k in ['desoto-voting-map-pdf-p1','lamar-precinct-pdf-p1','lafayette-locations-p1','lauderdale-original-p9','pearl-river-locations-p1','pearl-river-locations-p2']]
    for i,p in enumerate(pages):
        page=pdf.new_page(width=842,height=595);page.insert_text((24,23),f'Mississippi map research preview {i+1}/{len(pages)} | {p.stem}',fontsize=11);page.insert_image(fitz.Rect(20,34,822,561),filename=str(p),keep_proportion=True);page.insert_text((24,581),'Shared references only. No source-native join, legal boundary finding, November approval or vote allocation.',fontsize=9)
    pdf.set_metadata(dict(title='Mississippi qualified map reference previews',author='Election-night research',creationDate='',modDate=''));pdf.save(str(ROOT/'previews/map-preview-atlas.pdf'),garbage=4,deflate=True,no_new_id=True)
    qa=fitz.open(str(ROOT/'previews/map-preview-atlas.pdf'));sheet=Image.new('RGB',(1684,420*((len(qa)+3)//4)),'white')
    for i,p in enumerate(qa):
        pix=p.get_pixmap(matrix=fitz.Matrix(.5,.5),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);sheet.paste(im,((i%4)*421,(i//4)*420+40))
    sheet.save(ROOT/'previews/atlas-render-contact.png')
    savejson(ROOT/'preview-render.json',dict(original_pdf_inputs=inputs,svg_previews_rendered=len(files),contact_sheets=4,atlas_pages=len(pdf),renderer='PyMuPDF '+fitz.VersionBind,qualification='Static render output; actual visual inspections are separately recorded in visual-qa.json. All originals remain unchanged.'))
    print('static SVG/PNG/PDF previews',len(files),len(pdf))

if __name__=='__main__':build()
