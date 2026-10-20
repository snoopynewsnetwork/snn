#!/usr/bin/env python3
"""Hash check owned acquisition entities, extract complete PDFs only."""
from pathlib import Path
import gzip,hashlib,json,subprocess
OUT=Path(__file__).resolve().parents[1];SRC=OUT/'source/acquired'
def main():
    inventory=[]
    for path in sorted(SRC.glob('*.receipt.json')):
        r=json.loads(path.read_bytes())
        for e in r['response_entities']:
            z=(SRC/e['asset']).read_bytes();raw=gzip.decompress(z)
            assert len(z)==e['stored_bytes']and hashlib.sha256(z).hexdigest()==e['stored_sha256']
            assert len(raw)==e['raw_bytes']and hashlib.sha256(raw).hexdigest()==e['raw_sha256']
        if not r['response_entities']:continue
        e=r['response_entities'][-1];raw=gzip.decompress((SRC/e['asset']).read_bytes())
        if not raw.startswith(b'%PDF'):continue
        complete=b'%%EOF'in raw[-1024:]
        assert complete,(r['key'],'PDF prefix is not a complete original')
        p=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True)
        (SRC/(r['key']+'.layout.txt.gz')).write_bytes(gzip.compress(p.stdout,mtime=0))
        inventory.append(dict(source_key=r['key'],receipt=path.name,original_sha256=e['raw_sha256'],original_bytes=len(raw),
            complete_EOF=True,PDF_pages=p.stdout.count(b'\x0c'),text_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr=p.stderr.decode()))
    (SRC/'pdf-text-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    print('Complete owned PDF originals:',len(inventory))
if __name__=='__main__':main()
