"""Offline deterministic rebuild; defaults to no writes, including after sealing."""
from common import *
from validate import run as validate
from build import raw_receipts,entity
import tempfile,subprocess,sys
def run(preseal=False):
    validation=validate(preseal=preseal);compared=[]
    for rec in raw_receipts():
        if not rec.get('stored_path'):continue
        raw=entity(rec)
        if not raw.startswith(b'%PDF'):continue
        with tempfile.TemporaryDirectory(prefix='ri-official-reproduce-') as td:
            pdf=Path(td)/'source.pdf';pdf.write_bytes(raw)
            for args,suffix in [(['pdftotext','-layout',str(pdf),'-'],'pdf-layout.txt'),(['pdfinfo',str(pdf)],'pdfinfo.txt')]:
                p=R/'derived'/f"{rec['id']}.{suffix}"
                assert p.exists(),('Full PDF extraction missing',rec['id'])
                result=subprocess.run(args,capture_output=True,check=True).stdout
                assert result==p.read_bytes(),p
                compared.append(str(p.relative_to(S)))
    return dict(status='pass',generated_outputs=validation['counts']['deterministic_generated_outputs'],whole_PDF_extractions_and_metadata_compared=len(compared),files=compared,
        scope='Entire frozen-input build regenerated in memory and compared byte-for-byte; every acquired PDF full text/metadata independently regenerated in temporary directories. No network, producer writer, mutable aggregate, peer/map dependency or production output writes in default mode.')
if __name__=='__main__':
    result=run(preseal='--write' in sys.argv)
    if '--write' in sys.argv:write(R/'qa/reproduction.json',dump(result))
    print(json.dumps(result))
