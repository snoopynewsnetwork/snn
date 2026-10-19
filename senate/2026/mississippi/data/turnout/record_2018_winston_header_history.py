"""Lossless original-only correction history for Winston 2018 physical p2c8."""
import argparse,csv,gzip,io,json
from pathlib import Path
from PIL import Image
from acquire_sources import BASE,OUT,sha,savejson

FILES=('2018-winston-two-stage-native-original-readings.json',
       '2018-winston-two-stage-native-original-cells.csv')
ARCH=OUT/'source/2018-winston-header-correction-v1'
SOURCES=('sos-2018-county-winston','sos-2018-runoff-county-winston')

def archive():
    ARCH.mkdir(parents=True,exist_ok=True)
    pins=[]
    for name in FILES:
        raw=(OUT/name).read_bytes();stored=gzip.compress(raw,mtime=0)
        path=ARCH/(name+'.gz')
        if path.exists():assert path.read_bytes()==stored
        else:path.write_bytes(stored)
        pins.append(dict(original_path=str((OUT/name).relative_to(BASE)),
                         archive_path=str(path.relative_to(BASE)),
                         raw_sha256=sha(raw),raw_bytes=len(raw),
                         stored_sha256=sha(stored),stored_bytes=len(stored)))
    manifest=dict(scope='Pre-correction direct-original Winston 2018 stage ledgers; first p2c8 label was read Nann Waiya before enlarged original crop. Six candidate labels only; votes/roles were already source-read.',pins=pins)
    path=ARCH/'prior-ledger-pins.json'
    if path.exists():assert json.loads(path.read_text())==manifest
    else:savejson(path,manifest)
    print('Archived exact prior Winston header reading',sha(path.read_bytes()))

def read_rows(raw,kind):
    if kind=='json':return [r for s in json.loads(raw)['sources'] for r in s['rows']]
    return list(csv.DictReader(io.StringIO(raw.decode())))

def finalize():
    manifest=json.loads((ARCH/'prior-ledger-pins.json').read_text())
    diff=[];source=[]
    for pin in manifest['pins']:
        stored=(BASE/pin['archive_path']).read_bytes();old=gzip.decompress(stored)
        new=(BASE/pin['original_path']).read_bytes()
        assert sha(stored)==pin['stored_sha256'] and sha(old)==pin['raw_sha256']
        kind='json' if pin['original_path'].endswith('.json') else 'csv'
        earlier=read_rows(old,kind);later=read_rows(new,kind)
        assert len(earlier)==len(later)==132
        changes=[]
        for a,b in zip(earlier,later):
            assert a.keys()==b.keys()
            different={k:(a[k],b[k]) for k in a if a[k]!=b[k]}
            if different:
                assert set(different)=={'literal_source_header'},different
                assert different['literal_source_header']==('Nann Waiya','Nanih Waiya')
                assert a['source_id'] in SOURCES and int(a['source_pdf_page'])==2 and int(a['physical_source_column'])==8
                changes.append(dict(source_id=a['source_id'],source_pdf_page=2,physical_source_column=8,
                                    candidate=a['candidate'],old='Nann Waiya',new='Nanih Waiya'))
        assert len(changes)==6
        if kind=='json':
            old_doc=json.loads(old);new_doc=json.loads(new)
            for s in old_doc['sources']:
                for r in s['rows']:
                    if r['source_pdf_page']==2 and r['physical_source_column']==8:r['literal_source_header']='Nanih Waiya'
            assert old_doc==new_doc
        diff.append(dict(derivative=kind,current_sha256=sha(new),changed_candidate_label_positions=len(changes),changes=changes))
    for sid in SOURCES:
        page=OUT/f'qa/2018-frozen78-original-pixels/{sid}/p0002-original.png'
        assert page.exists()
        im=Image.open(page);crop=im.crop((1500,245,1680,510)).rotate(270,expand=True)
        buf=io.BytesIO();crop.save(buf,format='PNG')
        crop_path=OUT/f'qa/2018-winston-header-original/{sid}-p2-c8-original-pixels.png'
        assert sha(buf.getvalue())==sha(crop_path.read_bytes())
        source.append(dict(source_id=sid,full_original_raster=str(page.relative_to(BASE)),
                           full_original_raster_sha256=sha(page.read_bytes()),
                           crop_from_original_pixels=[1500,245,1680,510],rotation_clockwise_degrees=90,
                           crop_path=str(crop_path.relative_to(BASE)),crop_sha256=sha(crop_path.read_bytes()),
                           original_literal='Nanih Waiya'))
    output=dict(scope='Literal Winston 2018 Nov6/Nov27 source header correction, six candidate labels; original complete-page rasters and exact prior derivatives preserved. No vote, role, source position or precinct identity change.',
                prior_manifest=str((ARCH/'prior-ledger-pins.json').relative_to(BASE)),
                prior_manifest_sha256=sha((ARCH/'prior-ledger-pins.json').read_bytes()),
                derivative_comparisons=diff,original_crops=source)
    savejson(OUT/'2018-winston-header-original-correction-history.json',output)
    print('Verified six label-only Winston original-pixel corrections')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',action='store_true');args=p.parse_args()
    archive() if args.archive else finalize()
