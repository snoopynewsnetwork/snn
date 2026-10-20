"""Freeze complete own proof bodies before any reciprocal derivative read."""
import datetime,tarfile
from common import *
def main():
    target=BASE/'witness/pre-peer-bodies.tar.gz'
    if target.exists():raise SystemExit('Already immutable')
    paths=sorted(p for p in BASE.rglob('*') if p.is_file() and p!=target)
    with tarfile.open(target,'w:gz') as tar:
        for p in paths:tar.add(p,arcname=str(p.relative_to(BASE)),recursive=False)
    write_json('witness/pre-peer-body-witness.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'Complete owned bodies before peer numerical derivative access; original bodies referenced by fixed receipts, raw/stored hashes in source/inputs.json',
        'archive':str(target.relative_to(BASE)),'sha256':sha(target.read_bytes()),'bytes':target.stat().st_size,
        'bodies':[{'path':str(p.relative_to(BASE)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in paths]})
    print('Own pre-peer witness',sha(target.read_bytes()),len(paths))
if __name__=='__main__':main()
