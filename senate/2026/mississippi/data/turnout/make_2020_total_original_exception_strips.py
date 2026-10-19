"""Original-only broad candidate strips where a 2020 TOTAL locator is uncertain.

Uses source ID/page, transform and broad candidate y position only.  No peer
candidate value or printed TOTAL ordinal is used in a strip.
"""
import gzip,io,json
import fitz
from PIL import Image,ImageDraw
from acquire_sources import BASE,OUT,receipts,sha,savejson

IDS='amite attala claiborne desoto hancock jefferson-davis jefferson-davis-amended kemper lamar lowndes madison montgomery neshoba newton noxubee rankin walthall washington-amended yalobusha-amended'.split()
R={r['id']:r for r in receipts}

def main():
    idx=json.loads((OUT/'qa/2020-county-total-originals/index.json').read_text())
    selected=[x for x in idx['entries'] if x['source_id'].removeprefix('sos-2020-county-') in IDS]
    assert len(selected)==len(IDS)
    out=OUT/'qa/2020-county-total-originals/broad-exception-strips';out.mkdir(exist_ok=True)
    entries=[]
    for e in selected:
        sid=e['source_id'];r=R[sid];raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256']
        doc=fitz.open(stream=raw,filetype='pdf');page=doc[e['source_page']-1]
        im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.7,2.7),colorspace=fitz.csGRAY).tobytes('png')))
        im=im.rotate(e['rotation_ccw'],expand=True).rotate(e['deskew_angle_ccw'],fillcolor=255)
        assert list(im.size)==e['full_original_render_size']
        y0=max(0,e['source_bounds'][1]-15);y1=min(im.height,e['source_bounds'][3]+100)
        region=[max(0,e['source_bounds'][0]//2),y0,im.width,y1]
        strip=im.crop(tuple(region))
        p=out/f'{sid}.png';strip.save(p)
        entries.append(dict(source_id=sid,source_raw_sha256=r['raw_sha256'],source_page=e['source_page'],original_render_size=list(im.size),original_source_bounds=region,strip_path=str(p.relative_to(BASE)),strip_sha256=sha(p.read_bytes()),scope='Original page candidate region only; source-position y hint widened, all numeric columns retained.'))
        if sid=='sos-2020-county-jefferson-davis-amended':
            # This original candidate block starts above the peer's row hint.
            # Preserve a complete original-source band including Espy's row.
            complete=im.crop((0,0,im.width,min(im.height,y1)))
            cp=out/f'{sid}-complete-Senate.png';complete.save(cp)
            entries[-1]['complete_original_candidate_band']=str(cp.relative_to(BASE))
            entries[-1]['complete_original_candidate_band_sha256']=sha(cp.read_bytes())
    for i in range(0,len(entries),3):
        batch=entries[i:i+3];w=max(Image.open(BASE/x['strip_path']).width for x in batch);h=0
        for x in batch:h+=Image.open(BASE/x['strip_path']).height+36
        atlas=Image.new('RGB',(w,h),'white');dr=ImageDraw.Draw(atlas);at=0
        for x in batch:
            dr.text((4,at+4),x['source_id']+' ORIGINAL PDF p'+str(x['source_page']),fill='black')
            at+=28;pic=Image.open(BASE/x['strip_path']);atlas.paste(pic,(0,at));at+=pic.height+8
        atlas.save(out/f'atlas-{i//3+1:02d}.png')
    savejson(OUT/'2020-total-original-broad-exception-strips.json',dict(scope='Hash-checked original broad strips only; diagnostic image extraction, no numerical transcription.',source_count=len(entries),entries=entries))
    print(len(entries),'broad original exception strips')

if __name__=='__main__':main()
