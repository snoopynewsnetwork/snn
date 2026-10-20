"""Read-only independent reconstruction of the complete dispatch reference ledger."""
from collections import Counter
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

S=Path(__file__).resolve().parent.parent
D=S/'data'


def sha(b):return hashlib.sha256(b).hexdigest()
def sem(value):return sha(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())


def exact(pin):
    b=(S/pin['path']).read_bytes()
    assert len(b)==pin['bytes']<40_000_000 and sha(b)==pin['sha256']
    return b


def parsed(file):
    raw=(S/file).read_bytes()
    if file.endswith('.gz'):raw=gzip.decompress(raw)
    name=file.removesuffix('.gz')
    if name.endswith('.jsonl'):return [json.loads(line) for line in raw.splitlines() if line]
    if name.endswith('.csv'):return list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
    return json.loads(raw)


def resolve(root,pointer):
    if pointer=='':return root
    for part in pointer.removeprefix('/').split('/'):
        part=part.replace('~1','/').replace('~0','~')
        root=root[int(part)] if isinstance(root,list) else root[part]
    return root


def main():
    path=D/'coordinator-priority-acceptance.json'
    raw=path.read_bytes();accept=json.loads(raw)
    assert len(raw)==2796725 and sha(raw)=='efa18335d5660e811aa5c7bfe6ef86b2855412f5c22ab2adce88fc38fe535323'
    contract=json.loads(exact(accept['frozen_contract']))
    for field in accept['complete_root_field_semantics']:
        assert sem(resolve(contract,field['pointer']))==field['full_recursive_semantic_sha256']
    assert len(accept['complete_root_field_semantics'])==len(contract)==31
    for group in ['frozen_first_pair_assets','independent_coordinator_reviews']:
        for pin in accept[group]:exact(pin)
    for p in accept['producer_seals']:exact(p)
    for pin in accept['complete_source_companion_files']:
        b=exact(pin)
        if pin['path'].endswith('.gz'):
            b=gzip.decompress(b)
            assert len(b)==pin['complete_reconstructed_bytes'] and sha(b)==pin['complete_reconstructed_sha256']
        if 'full_semantic_sha256' in pin:
            assert sem(parsed(pin['path']))==pin['full_semantic_sha256']
    total=0;seen=Counter()
    for pin in accept['complete_source_object_reference_bodies']:
        exact(pin)
        digest=hashlib.sha256();byte_count=0;current_file=None;current=None
        with gzip.open(S/pin['path'],'rb') as f:
            for line in f:
                digest.update(line);byte_count+=len(line)
                row=json.loads(line)
                if row['file']!=current_file:
                    current_file=row['file'];current=parsed(current_file)
                if 'pointer' in row:value=resolve(current,row['pointer'])
                elif 'JSONL_record_1based' in row:value=current[row['JSONL_record_1based']-1]
                else:value=current[row['CSV_row_1based_including_header']-1]
                assert sem(value)==row['full_recursive_semantic_sha256'],row
                total+=1;seen[current_file]+=1
        assert byte_count==pin['complete_reconstructed_bytes']
        assert digest.hexdigest()==pin['complete_reconstructed_sha256']
        assert dict(seen)==pin['source_objects_by_file']
    assert total==accept['complete_source_object_count']==554096
    assert accept['current_geography_approved'] is False
    assert accept['legal_native_80_robustness_approved'] is False
    out=dict(status='pass_complete_read_only_dispatch_ledger_reconstruction',
             acceptance=dict(path=str(path.relative_to(S)),bytes=len(raw),sha256=sha(raw)),
             complete_root_fields=31,complete_companions=len(accept['complete_source_companion_files']),
             complete_full_source_objects=total,source_files_with_objects=len(seen),
             current_geography_approved=False,legal_native_80_robustness_approved=False,
             no_producer_or_acceptance_writes=True)
    p=D/'coordinator-acceptance-validation.json';b=(json.dumps(out,indent=2)+'\n').encode();p.write_bytes(b)
    print(json.dumps(dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b),objects=total)))


if __name__=='__main__':main()
