"""Freeze the first complete-original Neshoba reading before literal repair."""
import gzip
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'data/turnout'
DEST=OUT/'source/2018-neshoba-original-header-correction-v1'

def sha(x):return hashlib.sha256(x).hexdigest()

def main():
    DEST.mkdir(parents=True,exist_ok=True)
    files={
      'initial_reading':OUT/'2018-neshoba-two-stage-native-original-readings.json',
      'initial_flat':OUT/'2018-neshoba-two-stage-native-original-cells.csv',
      'initial_script':OUT/'record_2018_native_neshoba.py',
      'initial_peer_comparison':OUT/'2018-neshoba-native-peer-reconciliation.json',
    }
    reading=json.loads(files['initial_reading'].read_text())
    assert len(reading['sources'])==2
    assert all(s['rows'][0]['literal_source_header']=='Arrington' for s in reading['sources'])
    pins={}
    for k,p in files.items():
        raw=p.read_bytes();stored=gzip.compress(raw,compresslevel=9,mtime=0)
        dest=DEST/(k+'.gz')
        if dest.exists():assert dest.read_bytes()==stored
        else:dest.write_bytes(stored)
        pins[k]={'original_path':str(p.relative_to(BASE)),
                 'stored_path':str(dest.relative_to(BASE)),
                 'raw_sha256':sha(raw),'raw_bytes':len(raw),
                 'stored_sha256':sha(stored),'stored_bytes':len(stored)}
    for stage in ('county','runoff-county'):
        sid=f'sos-2018-{stage}-neshoba'
        p=OUT/f'qa/2018-peer142-original-tsv/{sid}/p0002-original.png'
        assert p.exists();raw=p.read_bytes()
        pins[sid+'-complete-original-p2']={'path':str(p.relative_to(BASE)),
                                           'raw_sha256':sha(raw),'raw_bytes':len(raw)}
    for n in ('special','runoff'):
        p=OUT/f'qa/2018-neshoba-{n}-first-header-own-original-upright.png'
        raw=p.read_bytes()
        pins[n+'-unaltered-original-header-crop']={'path':str(p.relative_to(BASE)),
                                                     'raw_sha256':sha(raw),'raw_bytes':len(raw)}
    payload={'scope':'Direct-original literal header correction, independent of unchanged candidate votes and county arithmetic.',
             'initial_literal':'Arrington','corrected_literal':'Arlington',
             'source_position':'PDF page2 physical column1 in both distinct stages',
             'correction_basis':'Both separately rendered original source header glyphs visibly print Arlington (single r and l), confirmed from enlarged unaltered pixels after initial transcription. Peer comparison was subsequent and did not supply vote values.',
             'line_wrap_difference':'Other five per-stage header mismatches are only line-break representation of visibly wrapped original words; not silently asserted as byte-identical.',
             'candidate_field_difference_count':0,'pins':pins}
    blob=json.dumps(payload,ensure_ascii=False,indent=2).encode()+b'\n'
    target=DEST/'correction-history.json'
    if target.exists():assert target.read_bytes()==blob
    else:target.write_bytes(blob)
    print(target,len(blob),sha(blob))

if __name__=='__main__':main()
