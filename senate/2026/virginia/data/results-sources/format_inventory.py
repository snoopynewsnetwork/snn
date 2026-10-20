"""Complete local PDF extraction and full CSV decoding; no network or renderer claims."""
import csv,gzip,hashlib,io,json,subprocess,tempfile
from pathlib import Path
from acquire import ROOT
from replay import canonical,strict

def run(destination=None):
    out=Path(destination) if destination else ROOT
    target=out/'inspections/full-formats';target.mkdir(parents=True,exist_ok=True)
    entities={};products=[]
    def write(name,b):
        p=target/name
        if not isinstance(b,bytes):b=json.dumps(b,ensure_ascii=False,indent=2).encode()+b'\n'
        assert len(b)<40000000
        p.write_bytes(b);products.append(str(p.relative_to(out)))
    for p in sorted((ROOT/'requests').glob('*.json')):
        r=strict(p.read_bytes())
        for h in r['hops']:
            e=h['body'];v=entities.setdefault(e['raw_sha256'],{'entity':e,'requests':[],'headers':[]})
            v['requests'].append(p.stem);v['headers'].extend(h['response_headers'])
    inventory=[]
    for digest,v in sorted(entities.items()):
        b=gzip.decompress((ROOT/v['entity']['path']).read_bytes());assert hashlib.sha256(b).hexdigest()==digest
        row={'complete_original':v['entity'],'request_keys':list(dict.fromkeys(v['requests']))}
        if b.startswith(b'%PDF'):
            row['format']='PDF';row['manual_review']='No manual review implied; see manual-review-scope.json'
            with tempfile.TemporaryDirectory(prefix='va-pdf-') as tmp:
                p=Path(tmp)/'original.pdf';p.write_bytes(b)
                text=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True)
                info=subprocess.run(['pdfinfo',str(p)],capture_output=True)
            write(digest+'.text.gz',gzip.compress(text.stdout,mtime=0))
            write(digest+'.pdfinfo.gz',gzip.compress(info.stdout,mtime=0))
            row.update({'full_text_path':str((target/(digest+'.text.gz')).relative_to(out)),
                'metadata_path':str((target/(digest+'.pdfinfo.gz')).relative_to(out)),
                'text_returncode':text.returncode,'text_stderr':text.stderr.decode(errors='replace'),
                'metadata_returncode':info.returncode,'metadata_stderr':info.stderr.decode(errors='replace'),
                'full_text_bytes':len(text.stdout),'full_text_sha256':hashlib.sha256(text.stdout).hexdigest()})
        elif any(k in v['requests'] for k in ['november-complete-export-results','november-complete-export-absentee']) or (b and any('csv' in value.lower() for key,value in v['headers'] if key.lower()=='content-type')):
            row['format']='CSV';records=list(csv.reader(io.StringIO(b.decode('utf-8-sig'),newline='')))
            row.update({'whole_header':records[0] if records else None,'complete_logical_records_including_header':len(records),
                'complete_ordered_all_cell_arrays_sha256':hashlib.sha256(canonical(records)).hexdigest(),
                'record_widths':sorted(set(map(len,records))),
                'reconstruction':'csv.reader UTF-8-sig newline="" over complete original; includes headers, blanks and all rows; no field normalization'})
        else:continue
        inventory.append(row)
    write('inventory.json',inventory)
    return products
if __name__=='__main__':print(json.dumps(run()))
