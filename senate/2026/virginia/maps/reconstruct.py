"""Reconstruct any complete acquired response, validating stored and raw hashes.

python3 -B maps/reconstruct.py REQUEST_KEY /private/tmp/output.pdf
The output path must be outside the sealed owned package.
"""
import gzip,hashlib,io,json,sys,tarfile
from pathlib import Path
from acquire import HERE,entity
if __name__=='__main__':
    historical=sys.argv[1]=='--historical'
    key=sys.argv[2] if historical else sys.argv[1]
    out=Path(sys.argv[4] if historical else sys.argv[2]).resolve()
    assert HERE not in out.parents and out!=HERE
    if historical:
        authority=json.loads((HERE.parent/'data/coordinator-priority-acceptance.json').read_bytes())
        rows=[r for r in authority['historical_full_body_resolvers'] if r['path']==key and r['sha256']==sys.argv[3]]
        assert rows,'exact historical path plus SHA not found'
        row=rows[0];storage=row['storage'];pin=storage.get('archive',storage.get('file'));stored=(HERE.parent/pin['path']).read_bytes()
        assert len(stored)==pin['bytes'] and hashlib.sha256(stored).hexdigest()==pin['sha256']
        if storage['kind']=='tar_gzip_member':
            with tarfile.open(fileobj=io.BytesIO(gzip.decompress(stored))) as archive:body=archive.extractfile(storage['member']).read()
        else:body=stored
        assert len(body)==row['bytes'] and hashlib.sha256(body).hexdigest()==row['sha256']
    else:
        receipt=json.loads((HERE/'requests'/f'{key}.json').read_bytes());body=entity(receipt)
    assert body is not None
    out.write_bytes(body)
    print(json.dumps({'request':key,'output':str(out),'bytes':len(body),'complete_original':True}))
