#!/usr/bin/env python3
"""Retain public response bodies losslessly; one immutable capture per id.

Usage: python3 acquire.py ID URL [PARENT_SOURCE_ID]
Original shared assets are referenced by exact hashes rather than copied.
"""
import datetime
import gzip
import hashlib
import json
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fetch(sid, url, parent=None):
    dest = ROOT / 'source'
    dest.mkdir(parents=True, exist_ok=True)
    meta = dest / (sid + '.json')
    if meta.exists():
        return json.loads(meta.read_text())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with tempfile.TemporaryDirectory() as td:
        body, hdr = pathlib.Path(td)/'body', pathlib.Path(td)/'headers'
        p = subprocess.run(['curl', '--silent', '--show-error', '--location',
                            '--max-time', '50', '--connect-timeout', '15',
                            '--header', 'Accept-Encoding: identity',
                            '--dump-header', str(hdr), '--output', str(body),
                            '--write-out', '%{json}', url], capture_output=True)
        raw = body.read_bytes() if body.exists() else b''
        headers = hdr.read_bytes() if hdr.exists() else b''
        try:
            info = json.loads(p.stdout)
        except ValueError:
            info = {'unparsed_stdout': p.stdout.decode(errors='replace')}
        stored = gzip.compress(raw, mtime=0)
        assert len(stored) < 40_000_000
        (dest/(sid+'.body.gz')).write_bytes(stored)
        (dest/(sid+'.headers.txt')).write_bytes(headers)
        decoded = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') and b'content-encoding: gzip' in headers.lower() else raw
        m = dict(id=sid, requested_url=url, final_url=info.get('url_effective'),
                 parent_source_id=parent, retrieved_utc=now,
                 status=info.get('http_code'), curl_exit=p.returncode,
                 curl_stderr=p.stderr.decode(errors='replace'), curl=info,
                 body_path=sid+'.body.gz', original_bytes=len(raw),
                 original_sha256=sha(raw), stored_bytes=len(stored),
                 decoded_original_bytes=len(decoded), decoded_original_sha256=sha(decoded),
                 http_content_decoding='gzip' if decoded != raw else 'identity',
                 stored_sha256=sha(stored), headers_path=sid+'.headers.txt',
                 headers_sha256=sha(headers),
                 body_encoding='gzip of unmodified response entity; request Accept-Encoding identity',
                 source_time_status='See complete response/redirect headers; retrieval, archive capture, Last-Modified and election dates are separate clocks.')
        meta.write_text(json.dumps(m, indent=2)+'\n')
        return m


if __name__ == '__main__':
    m = fetch(*sys.argv[1:])
    print(json.dumps({k:m[k] for k in ['id','status','original_bytes','original_sha256','final_url']}))
