#!/usr/bin/env python3
"""Original-first extraction. Shared original assets are read-only and hash checked.

No coordinator candidate derivatives are inputs. PDF layout text is a locator
derivative; original bytes remain reconstructible in the shared ZIPs/receipts.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import csv, gzip, hashlib, importlib.util, io, json, subprocess, tempfile, zipfile

OUT = Path(__file__).resolve().parents[1]
DATA = OUT.parent
NEWS = DATA/'news'
sha = lambda b: hashlib.sha256(b).hexdigest()

def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def body(source):
    b = (NEWS/source['asset']).read_bytes()
    assert sha(b) == source['stored_sha256']
    raw = gzip.decompress(b)
    assert sha(raw) == source['raw_sha256'] and len(raw) == source['bytes']
    return raw

def text_pdf(raw):
    assert raw.startswith(b'%PDF-') and b'%%EOF' in raw[-1024:]
    p = subprocess.run(['pdftotext', '-layout', '-', '-'], input=raw, capture_output=True, check=True)
    return p.stdout, p.stderr.decode(errors='replace')

def main():
    manifest = json.loads((NEWS/'manifest.json').read_bytes())
    byid = {x['id']:x for x in manifest}
    sources = []
    inventory = []
    abstracts = [
        ('2024-abstract', ['sos-2024-results-archived-20241212']),
        ('2020-abstract', ['sos-2020-actual-abstract-stream13735450']),
        ('2022-abstract', ['sos-2022-record13735454-range0-163839',
                           'sos-2022-record13735454-range163840-327679',
                           'sos-2022-record13735454-byte-range-tail']),
        ('2024-Wasco', ['sos-observed-2024-wasco-native-original']),
        ('2024-registration', ['sos-2024-abstract-original']),
        ('2022-registration', ['sos-2022-abstract-original']),
        ('2020-registration', ['sos-2020-abstract-original']),
    ]
    for key, ids in abstracts:
        pins = [byid[s] for s in ids]
        raw = b''.join(body(s) for s in pins)
        if key == '2022-abstract':
            pos = 0
            for s in pins:
                n = s['bytes']
                assert s['headers']['Content-Range'] == f'bytes {pos}-{pos+n-1}/462872'
                pos += n
            assert len(raw) == 462872
        txt, warnings = text_pdf(raw)
        path = OUT/'source'/f'{key}.layout.txt.gz'
        path.write_bytes(gzip.compress(txt, mtime=0))
        inventory.append(dict(source_key=key, original_sha256=sha(raw), original_bytes=len(raw),
            original_source_ids=ids, text_path=str(path.relative_to(OUT)), text_sha256=sha(txt),
            pages=txt.count(b'\x0c'), extraction_warnings=warnings))
        sources.extend(pins)
        (Path('/tmp/oregon-turnout-originals')/f'{key}.pdf').write_bytes(raw)
    # Use only the shared byte restoration routine; never run its main, which
    # writes coordinator audit paths. Each member is hashed independently here.
    spec = importlib.util.spec_from_file_location('original_zip_restore', DATA/'audit_precinct_archives.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for year in ('2020','2022'):
        s = byid[f'sos-{year}-precinct-zip-observed-download']
        sources.append(s)
        with tempfile.TemporaryFile() as f:
            mod.restore(s, f)
            f.seek(0)
            with zipfile.ZipFile(f) as z:
                assert z.testzip() is None
                for i, info in enumerate(z.infolist()):
                    raw = z.read(info)
                    assert len(raw) == info.file_size
                    county = Path(info.filename).stem
                    # Literal member name remains the authoritative locator.
                    key = f'{year}-{i:02d}'
                    if raw.startswith(b'%PDF-'):
                        txt, warnings = text_pdf(raw)
                        kind = 'PDF'
                    else:
                        txt, warnings, kind = raw, '', 'CSV'
                    path = OUT/'source'/f'{key}.layout.txt.gz'
                    path.write_bytes(gzip.compress(txt, mtime=0))
                    inventory.append(dict(source_key=key, year=int(year), archive_source_id=s['id'],
                        member_name=info.filename, ZIP_member_ordinal=i, CRC32=info.CRC,
                        original_sha256=sha(raw), original_bytes=len(raw), original_kind=kind,
                        text_path=str(path.relative_to(OUT)), text_sha256=sha(txt),
                        pages=txt.count(b'\x0c') if kind == 'PDF' else None,
                        extraction_warnings=warnings))
                    print(year, i, info.filename, len(txt), flush=True)
    save_json(OUT/'source'/'original-inventory.json', inventory)
    sources = list({s['id']:s for s in sources}.values())
    save_json(OUT/'source'/'shared-original-pins.json', sources)

if __name__ == '__main__':
    main()
