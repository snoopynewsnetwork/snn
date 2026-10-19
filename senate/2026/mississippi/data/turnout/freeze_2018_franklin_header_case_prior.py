"""Keep the exact earlier Franklin2018 M-c-C-a-l-l transcription bytes."""
import gzip
from acquire_sources import OUT,sha,savejson

EXPECTED={
 '2018-franklin-two-stage-native-original-readings.json':(120405,'51b419b793137505aa0a4c434fd41bb5a2c6f159edf69e2d1e72ef0ec419f187'),
 '2018-franklin-two-stage-native-original-cells.csv':(49689,'f59aa74ad7210f49084bbd07497f5d7947dc52219687c4a117f1e7d72933f296'),
}

def main():
    directory=OUT/'source/2018-franklin-header-case-correction-v1'
    directory.mkdir(parents=True,exist_ok=True)
    pins=[]
    for name,(length,digest) in EXPECTED.items():
        original=OUT/name
        stored=directory/(name+'.gz')
        if not stored.exists():
            raw=original.read_bytes()
            assert len(raw)==length and sha(raw)==digest,(name,'initial earlier reading changed')
            stored.write_bytes(gzip.compress(raw,mtime=0))
        data=stored.read_bytes();raw=gzip.decompress(data)
        assert len(raw)==length and sha(raw)==digest,(name,'earlier lossless archive changed')
        pins.append(dict(earlier_original_path=str(original.relative_to(OUT.parent.parent)),
                         stored_path=str(stored.relative_to(OUT.parent.parent)),
                         original_bytes=length,original_sha256=digest,
                         stored_bytes=len(data),stored_sha256=sha(data)))
    savejson(directory/'prior-ledger-pin.json',
             dict(scope='Exact pre-correction Franklin 2018 two-stage source-reading bodies. Physical column9 header was previously transcribed McCall; candidate values, source positions and original bytes are retained. No earlier witness is overwritten.',pins=pins))
    print('Franklin2018 prior case ledgers pinned')

if __name__=='__main__':main()
