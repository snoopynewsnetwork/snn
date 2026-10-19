"""Preserve original peer-comparison metadata beside later replay metadata.

The coordinator's read-only lossless archives precede the independent
38-publication replay. This compares exact bodies; source readings never
take candidate data from either peer publication.
"""
import gzip
import json
from pathlib import Path

from acquire_sources import BASE, OUT, savejson, sha

PINPATH=OUT/'source/2020-native-peer-metadata-history-inputs-v1.json'
PIN_SHA='02b3c394af61b9e5ecc05a4217bc27fdfc42d5b61a1b4405c75ff99e8731ebec'
METADATA = frozenset(('scope', 'peer_file_sha256',
                      'peer_snapshot_sha256',
                      'accepted_source_literal_label_differences'))

def semantic_digest(doc):
    core={k:v for k,v in doc.items() if k not in METADATA}
    return sha(json.dumps(core,sort_keys=True,ensure_ascii=False,
                          separators=(',',':')).encode())

def main():
    assert sha(PINPATH.read_bytes())==PIN_SHA
    pinned=json.loads(PINPATH.read_text())['archived_readings']
    assert len(pinned)==39
    records=[]
    for pin in pinned:
        archived=BASE/pin['archive_path']
        current=OUT/archived.name.removesuffix('.gz')
        assert current.is_file(), current
        stored=archived.read_bytes()
        earlier=gzip.decompress(stored)
        assert sha(stored)==pin['archive_stored_sha256'] and len(stored)==pin['archive_stored_bytes']
        assert sha(earlier)==pin['earlier_raw_sha256'] and len(earlier)==pin['earlier_raw_bytes']
        later=current.read_bytes()
        first=json.loads(earlier)
        second=json.loads(later)
        assert first['source_id']==second['source_id']==pin['source_id']
        assert semantic_digest(first)==semantic_digest(second),(archived,current)
        changed={key:dict(earlier_present=key in first,
                          earlier_value=first.get(key),
                          later_present=key in second,
                          later_value=second.get(key))
                 for key in sorted(set(first)|set(second))
                 if first.get(key)!=second.get(key) or (key in first)!=(key in second)}
        assert set(changed)<=METADATA,(archived,changed)
        records.append(dict(source_id=first['source_id'],
                            archive_path=str(archived.relative_to(BASE)),
                            archive_stored_sha256=sha(stored),
                            archive_stored_bytes=len(stored),
                            earlier_raw_sha256=sha(earlier),
                            earlier_raw_bytes=len(earlier),
                            current_path=str(current.relative_to(BASE)),
                            later_raw_sha256=sha(later),
                            later_raw_bytes=len(later),
                            unchanged_source_semantics_sha256=semantic_digest(first),
                            source_positions=len(first['rows']),
                            comparison_metadata_changes=changed))
    assert len(records)==39
    assert len({r['source_id'] for r in records})==39
    changed=[r for r in records if r['comparison_metadata_changes']]
    assert len(changed)==17
    assert sum(r['source_positions'] for r in records)==2343
    assert all(set(r['comparison_metadata_changes'])<=METADATA for r in records)
    out=dict(scope='Original-reading witness bodies versus later 38-publication peer replay. Seventeen JSON bodies differ only in peer-comparison metadata; exact original source rows, votes, labels, roles, physical positions, source/raster hashes and source controls are unchanged. Earlier peer hashes remain attached to earlier witness bytes. Read-only coordinator archives are external references, never modified.',
             archived_reading_count=len(records),
             metadata_changed_count=len(changed),
             unchanged_count=len(records)-len(changed),
             candidate_or_null_positions=sum(r['source_positions'] for r in records),
             permitted_metadata_fields=sorted(METADATA),
             changed_sources=[r['source_id'] for r in changed],
             records=records)
    savejson(OUT/'2020-native-peer-metadata-update-history.json',out)
    print('2020 peer metadata history:',len(records),'archived readings,',
          len(changed),'later metadata comparisons, no source-field changes')

if __name__=='__main__': main()
