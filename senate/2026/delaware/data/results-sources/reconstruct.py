"""Output one exact complete pinned file/body, never external acceptance.
Usage: reconstruct.py STATE_RELATIVE_PATH OUTPUT [--decode] [--pointer /path]
"""
import argparse,gzip,json
from pathlib import Path
from freeze import S,R,load,pin,pointer
def main():
    p=argparse.ArgumentParser();p.add_argument('path');p.add_argument('output');p.add_argument('--decode',action='store_true');p.add_argument('--pointer');a=p.parse_args()
    assert a.path!='data/coordinator-priority-acceptance.json'
    f=load(R/'frozen-references.json.gz');pins={x['path']:x for x in f['full_asset_references']+f['complete_companions']+[f['contract']]}
    for x in load(R/'source-index.json'):
        pins[x['receipt']['path']]=x['receipt'];pins[x['body']['path']]=x['body']
    expected=pins[a.path];source=S/a.path;actual=pin(source);assert all(actual[k]==expected[k]for k in actual)
    if a.pointer is not None:b=(json.dumps(pointer(load(source),a.pointer),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    else:
        b=source.read_bytes()
        if a.decode and source.suffix=='.gz':b=gzip.decompress(b)
    Path(a.output).write_bytes(b);print('Reconstructed full body',len(b),'bytes')
if __name__=='__main__':main()
