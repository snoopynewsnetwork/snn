"""Bounded coordinator primary-metadata preparation, not approved map joins."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import re
import requests

D = Path(__file__).resolve().parent / 'coordinator-map-preparation'
URLS = [
    ('wards-metadata', 'https://www.mass.gov/info-details/massgis-data-2022-wards-and-precincts'),
    ('subprecincts-metadata', 'https://www.mass.gov/info-details/massgis-data-2022-subprecincts'),
    ('wards-official-hub', 'https://gis.data.mass.gov/datasets/massgis%3A%3Awards-and-precincts-2022-feature-service/explore'),
]


def digest(b):
    return hashlib.sha256(b).hexdigest()


def response(r):
    raw = r.content
    stored = gzip.compress(raw, mtime=0)
    assert len(stored) < 40000000
    name = digest(raw) + '.body.gz'
    path = D / name
    if path.exists():
        assert path.read_bytes() == stored
    else:
        path.write_bytes(stored)
    return dict(url=r.url, status=r.status_code, full_headers=dict(r.headers),
                complete_entity=name, raw_bytes=len(raw), raw_sha256=digest(raw),
                stored_bytes=len(stored), stored_sha256=digest(stored))


def main():
    D.mkdir(exist_ok=True)
    receipts = []
    for key, url in URLS:
        receipt_path = D / (key + '.receipt.json')
        if receipt_path.exists():
            receipts.append(json.loads(receipt_path.read_bytes()))
            continue
        entry = dict(id=key, requested_url=url, method='GET',
                     request_headers={'User-Agent': 'SNN election research (+public-source archival audit)'},
                     requested_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     source_link_scope='Actual official MassGIS metadata or official catalog result; no guessed service endpoint or identity join.')
        try:
            r = requests.get(url, headers=entry['request_headers'], timeout=(10, 35))
            entry['redirects'] = [response(v) for v in r.history]
            entry['response'] = response(r)
            if r.status_code == 200:
                text = r.text
                entry['literal_map_link_candidates_not_approved'] = sorted(set(re.findall(r'https?[^\s<>"\\]+(?:FeatureServer|MapServer|\.zip)[^\s<>"\\]*', text)))
        except requests.RequestException as e:
            entry['transport_error'] = dict(type=type(e).__name__, detail=str(e))
        entry['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        receipt_path.write_text(json.dumps(entry, indent=2)+'\n')
        receipts.append(entry)
    out = dict(status='bounded_official_metadata_preparation_only', receipts=receipts,
               independent_native_acquisition_or_join_approval=False,
               qualifications='No map worker launch implied. Only exact request/redirect/body evidence; catalog labels and published source vintage do not establish current result-leaf compatibility or legal completeness.')
    p = D / 'acquisition-complete-v1.json'
    raw = (json.dumps(out, indent=2)+'\n').encode()
    if p.exists():
        assert p.read_bytes() == raw
    else:
        p.write_bytes(raw)
    print(json.dumps({'requests': len(receipts), 'outcomes': [(r['id'], r.get('response', {}).get('status', 'transport_error')) for r in receipts], 'inventory': str(p), 'bytes': len(raw), 'sha256': digest(raw)}))


if __name__ == '__main__':
    main()
