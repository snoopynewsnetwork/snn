"""Read-only integrity audit of still-unlaunched states' retained originals.

This checks source preparation, not completed questions or admitted feeds.
It never invokes an acquisition/producer writer or changes the queue itself.
"""
from pathlib import Path
import collections
import datetime
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    queue = json.loads((ROOT/'research-queue.json').read_bytes())
    statuses = collections.Counter()
    reports = []
    captures = objects = entities = stored_bytes = split_entities = shared_entities = 0
    for state in queue['states']:
        if state['status'] != 'queued':
            continue
        folder = ROOT/state['slug']/'data/news'
        manifest_path = folder/'manifest.json'
        manifest_raw = manifest_path.read_bytes()
        rows = json.loads(manifest_raw)
        assert len({row['id'] for row in rows}) == len(rows)
        expected = set()
        local_status = collections.Counter()
        local_files = set()
        local_bytes = 0
        raw_count = 0
        for row in rows:
            assert row['retrieved_at_utc'] and row['url']
            captures += 1
            if 'asset_parts' in row:
                pieces = []
                split_entities += 1
                for part in row['asset_parts']:
                    p = folder/part['asset']
                    z = p.read_bytes()
                    assert len(z) == part['bytes'] < 40000000 and sha(z) == part['sha256']
                    pieces.append(z)
                    expected.add(p.name)
                    local_files.add(str(p))
                    local_bytes += len(z)
                    stored_bytes += len(z)
                    objects += 1
                stored = b''.join(pieces)
                assert len(stored) == row['stored_bytes']
            elif 'asset' in row:
                p = folder/row['asset']
                stored = p.read_bytes()
                assert len(stored) < 40000000
                objects += 1
                stored_bytes += len(stored)
                local_bytes += len(stored)
                local_files.add(str(p))
                if p.parent.resolve() == folder.resolve():
                    expected.add(p.name)
                else:
                    shared_entities += 1
                    reference = row['shared_original_reference']
                    expected_path = ROOT.parents[1]/reference['repository_path']
                    assert p.resolve().is_relative_to(ROOT.resolve()) and p.resolve() == expected_path.resolve()
                    assert len(stored) == reference['stored_bytes'] and sha(stored) == reference['stored_sha256']
                    assert reference['raw_sha256'] == row['raw_sha256']
            else:
                assert row.get('error')
                statuses['transport_failure'] += 1
                local_status['transport_failure'] += 1
                continue
            raw = gzip.decompress(stored)
            assert sha(stored) == row['stored_sha256']
            assert sha(raw) == row['raw_sha256'] and len(raw) == row['bytes']
            assert row.get('headers') or row.get('raw_headers')
            entities += 1
            raw_count += 1
            statuses[str(row['status'])] += 1
            local_status[str(row['status'])] += 1
        assert {p.name for p in folder.glob('*.html.gz*')} == expected, state['slug']
        reports.append(dict(state=state['slug'], source_response_records=len(rows), verified_complete_entities=raw_count,
                            stored_reference_files=len(local_files), bytes_over_reference_entries=local_bytes,
                            status_counts=dict(local_status), original_manifest=dict(path=str(manifest_path.relative_to(ROOT)),
                            bytes=len(manifest_raw), sha256=sha(manifest_raw)),
                            original_manifest_snapshot=rows))
    result = dict(status='pass_complete_retained_source_integrity_for_unlaunched_states_only',
                  checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  states=len(reports), response_captures=captures, stored_reference_entries=objects,
                  verified_original_entities=entities, stored_bytes_over_reference_entries=stored_bytes,
                  retained_transport_failures=statuses['transport_failure'], split_original_entities=split_entities,
                  shared_original_reference_entries=shared_entities, http_status_counts=dict(statuses),
                  complete_per_state_original_manifest_snapshots=reports,
                  checks='All IDs unique; every original/stored raw-byte SHA256/size; ordered-part reconstruction; UTC/URL/full headers or explicit transport error; strict stored-file bounds; no orphan response assets.',
                  qualifications='Queued preparation only. Complete entity means the complete retained HTTP response body, not necessarily an entire dataset:206 responses are exact response ranges only unless separately reconstructed. No first-pair extraction, accepted priority, genuine November source, current geographic identity, legal completeness or worker launch inferred. HTTP200 may be shell/old/primary/test; numerical source assertions require later independent original extraction. Original snapshots preserve all errors and stages.')
    out = ROOT/'coordinator-queued-preparation-audit.json'
    body = (json.dumps(result, indent=2)+'\n').encode()
    assert len(body) < 40000000
    out.write_bytes(body)
    print(json.dumps({k:v for k,v in result.items() if k != 'complete_per_state_original_manifest_snapshots'}, indent=2))
    print(json.dumps(dict(proof=str(out.relative_to(ROOT)), bytes=len(body), sha256=sha(body))))


if __name__ == '__main__':
    main()
