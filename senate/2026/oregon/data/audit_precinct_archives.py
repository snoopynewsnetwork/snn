"""Restore and validate the exact observed public-form ZIP response streams.

No request is repeated. ZIP member inventories are not candidate extractions.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import io
import json
import shutil
import sys
import tempfile
import zipfile

DATA = Path(__file__).resolve().parent
NEWS = DATA / 'news'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def restore(source, destination):
    stored_hash = hashlib.sha256()
    stored_size = 0
    with tempfile.TemporaryFile() as compressed:
        for part in source['asset_parts']:
            path = NEWS / part['asset']
            assert path.stat().st_size == part['bytes'] < 40000000
            assert digest(path) == part['sha256']
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    stored_hash.update(block)
                    stored_size += len(block)
                    compressed.write(block)
        assert stored_hash.hexdigest() == source['stored_sha256']
        assert stored_size == source['stored_bytes']
        compressed.seek(0)
        raw_hash = hashlib.sha256()
        raw_size = 0
        with gzip.GzipFile(fileobj=compressed, mode='rb') as decoded:
            for block in iter(lambda: decoded.read(1024 * 1024), b''):
                destination.write(block)
                raw_hash.update(block)
                raw_size += len(block)
        assert raw_hash.hexdigest() == source['raw_sha256']
        assert raw_size == source['bytes'] == int(source['headers']['Content-Length'])
    request = (NEWS / source['request_body_asset']).read_bytes()
    assert hashlib.sha256(request).hexdigest() == source['request_body_stored_sha256']
    assert hashlib.sha256(gzip.decompress(request)).hexdigest() == source['request_body_sha256']
    return raw_size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('year', choices=['2020', '2022'])
    parser.add_argument('--restore-stdout', action='store_true',
                        help='Write exact original ZIP bytes to stdout after verification.')
    args = parser.parse_args()
    source = next(r for r in json.loads((NEWS / 'manifest.json').read_bytes())
                  if r['id'] == f'sos-{args.year}-precinct-zip-observed-download')
    assert source['status'] == 200 and not source.get('error')
    with tempfile.TemporaryFile() as raw:
        restore(source, raw)
        raw.seek(0)
        members = []
        with zipfile.ZipFile(raw) as archive:
            assert archive.testzip() is None
            names = archive.namelist()
            assert len(names) == len(set(names))
            for info in archive.infolist():
                member_hash = hashlib.sha256()
                size = 0
                prefix = b''
                with archive.open(info) as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        if not prefix:
                            prefix = block[:16]
                        size += len(block)
                        member_hash.update(block)
                assert size == info.file_size
                members.append({'filename': info.filename, 'bytes': size,
                                'CRC': info.CRC, 'compressed_bytes': info.compress_size,
                                'sha256': member_hash.hexdigest(), 'first16_hex': prefix.hex(),
                                'PDF_magic': prefix.startswith(b'%PDF-')})
        if args.restore_stdout:
            raw.seek(0)
            shutil.copyfileobj(raw, sys.stdout.buffer)
            return
    output = {
        'status': 'complete_HTTP200_ZIP_CRC_and_all_member_hashes_verified_not_candidate_extracted',
        'source_pin': source, 'ZIP_members': members,
        'ZIP_member_count': len(members),
        'uncompressed_member_bytes': sum(r['bytes'] for r in members),
        'qualification': 'Literal member filenames, CRCs, bytes, hashes and PDF magic only. '
                         'County completeness and native candidate/method fields require independent '
                         'content extraction. No source-vintage, current geometry or reporting join is approved.'}
    (DATA / f'coordinator-{args.year}-native-archive-audit.json').write_text(
        json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: output[k] for k in ['status', 'ZIP_member_count', 'uncompressed_member_bytes']}))


if __name__ == '__main__':
    main()
