"""Losslessly freeze the superseded Lincoln ballot glyph reading before repair."""
import gzip
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / 'data/turnout'
DEST = OUT / 'source/2024-lincoln-ballots-original-correction-v1'


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    items = {
        'initial_reading': OUT/'2024-lincoln-original-panel-readings.json',
        'summary_ledger': OUT/'canvass-summary-readings.json',
        'statistics_ledger': OUT/'canvass-statistics-readings.json',
        'source_script': OUT/'record_lincoln_2024_panels.py',
        'summary_controls': OUT/'canvass-summary-controls.csv',
        'control_checks': OUT/'canvass-control-checks.json',
        'report_script': OUT/'build_report.py',
        'report': BASE/'turnout.md',
        'schema': OUT/'source/SCHEMA.md',
        'validator': OUT/'validate_turnout.py',
        'validation': OUT/'validation.json',
    }
    initial = json.loads(items['initial_reading'].read_text())
    assert initial['statistics']['ballots_cast_total'] == 15909
    assert initial['source_arithmetic']['statistics_ballots_minus_contest_total'] == 11
    pins = {}
    for name, src in items.items():
        raw = src.read_bytes()
        target = DEST/(name+'.gz')
        stored = gzip.compress(raw, compresslevel=9, mtime=0)
        if target.exists():
            assert target.read_bytes() == stored, name
        else:
            target.write_bytes(stored)
        pins[name] = {
            'original_path': str(src.relative_to(BASE)),
            'stored_path': str(target.relative_to(BASE)),
            'raw_sha256': digest(raw), 'raw_bytes': len(raw),
            'stored_sha256': digest(stored), 'stored_bytes': len(stored),
        }
    for name in ('2024-lincoln-panels-original-p9.png',
                 '2024-lincoln-stats-own-original-4x.png'):
        src = OUT/'qa'/name
        blob = src.read_bytes()
        pins[name] = {'original_path': str(src.relative_to(BASE)),
                      'raw_sha256': digest(blob), 'raw_bytes': len(blob)}
    history = {
        'source': 'sos-2024-county-lincoln PDF page 9, Statistics, Ballots Cast - Total',
        'correction': {'initial_reading':15909, 'direct_original_glyph_reading':15898,
                       'field':'ballots_cast_total',
                       'reason':'The initial transcription misread the original final two digits. The separately enlarged unaltered original crop visibly prints 15,898; this is a glyph correction, not a residual allocation.'},
        'unchanged_printed_contest_total':15898,
        'initial_statistics_minus_contest':11,
        'corrected_statistics_minus_contest':0,
        'frozen_initial_artifacts': pins,
    }
    target=DEST/'correction-history.json'
    payload=json.dumps(history,indent=2,ensure_ascii=False).encode()+b'\n'
    if target.exists():
        assert target.read_bytes()==payload
    else:
        target.write_bytes(payload)
    print(target, len(payload), digest(payload))


if __name__=='__main__': main()
