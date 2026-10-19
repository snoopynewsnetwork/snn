"""Compare earlier Franklin literal header with new original-only crop read."""
import csv
import copy
import gzip
import io
import json
from PIL import Image
from acquire_sources import BASE,OUT,receipts,savejson,sha

DIR=OUT/'source/2018-franklin-header-case-correction-v1'
OLD='McCall'
NEW='Mccall'

def main():
    pin=json.loads((DIR/'prior-ledger-pin.json').read_text())
    assert len(pin['pins'])==2
    prior={}
    for p in pin['pins']:
        stored=(BASE/p['stored_path']).read_bytes();raw=gzip.decompress(stored)
        assert len(stored)==p['stored_bytes'] and sha(stored)==p['stored_sha256']
        assert len(raw)==p['original_bytes'] and sha(raw)==p['original_sha256']
        prior[p['earlier_original_path'].rsplit('/',1)[-1]]=raw
    old=json.loads(prior['2018-franklin-two-stage-native-original-readings.json'])
    current_path=OUT/'2018-franklin-two-stage-native-original-readings.json'
    current=json.loads(current_path.read_text())
    corrected=copy.deepcopy(old)
    changes=[];crops=[]
    for source in corrected['sources']:
        sid=source['source_id']
        receipt=next(r for r in receipts if r['id']==sid)
        assert source['source_raw_sha256']==receipt['raw_sha256']
        raster=BASE/next(p['original_raster'] for p in source['pages'] if p['source_pdf_page']==2)
        original=Image.open(raster)
        assert original.size==(1743,1347)
        crop=OUT/f'qa/2018-franklin-header-case/{sid}-physical9-upright.png'
        crop.parent.mkdir(parents=True,exist_ok=True)
        original.crop((1330,190,1450,410)).rotate(270,expand=True).resize((1320,720)).save(crop)
        crops.append(dict(source_id=sid,source_pdf_page=2,physical_column=9,
                          source_raw_sha256=receipt['raw_sha256'],
                          original_raster=str(raster.relative_to(BASE)),
                          original_raster_sha256=sha(raster.read_bytes()),
                          source_pixel_crop=[1330,190,1450,410],rotation_clockwise_degrees=90,
                          rendered_crop=str(crop.relative_to(BASE)),
                          rendered_crop_sha256=sha(crop.read_bytes())))
        for row in source['rows']:
            if row['source_pdf_page']==2 and row['physical_source_column']==9:
                assert row['literal_source_header']==OLD
                row['literal_source_header']=NEW
                changes.append(dict(source_id=sid,candidate=row['candidate'],
                                    source_pdf_page=2,physical_column=9,
                                    earlier_literal=OLD,corrected_source_literal=NEW,
                                    votes=row['votes']))
    assert corrected==current
    assert len(changes)==6 and len(crops)==2
    old_flat=list(csv.DictReader(io.StringIO(prior['2018-franklin-two-stage-native-original-cells.csv'].decode())))
    new_path=OUT/'2018-franklin-two-stage-native-original-cells.csv'
    new_flat=list(csv.DictReader(new_path.open()))
    assert len(old_flat)==len(new_flat)==132
    for a,b in zip(old_flat,new_flat):
        if a['source_pdf_page']=='2' and a['physical_source_column']=='9':
            assert a['literal_source_header']==OLD and b['literal_source_header']==NEW
            a['literal_source_header']=NEW
        assert a==b
    savejson(OUT/'2018-franklin-header-case-correction-history.json',
             dict(scope='Both Franklin2018 special-stage PDFpage2 physical column9 labels directly re-read from owned original rasters. Earlier McCall derivative retained losslessly; printed Mccall replaces only six literal header fields, with all votes/roles/source positions/hashes and source controls unchanged. This is not a cross-stage or current-precinct identity join.',
                  prior_pin=str((DIR/'prior-ledger-pin.json').relative_to(BASE)),
                  prior_pin_sha256=sha((DIR/'prior-ledger-pin.json').read_bytes()),
                  new_readings_path=str(current_path.relative_to(BASE)),
                  new_readings_sha256=sha(current_path.read_bytes()),
                  new_flat_path=str(new_path.relative_to(BASE)),
                  new_flat_sha256=sha(new_path.read_bytes()),
                  changed_position_count=len(changes),changes=changes,crops=crops))
    print('Franklin2018 original-case correction:',len(changes),'labels, no votes')

if __name__=='__main__':main()
