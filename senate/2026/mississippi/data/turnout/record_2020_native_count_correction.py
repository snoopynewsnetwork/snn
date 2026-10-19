"""Retain the 23-publication coverage-count correction without touching votes."""
import json
from acquire_sources import OUT,savejson

def main():
    prior19=241
    additions={}
    for tag in ('newton','jasper-original','jasper-amended','george'):
        path=OUT/f'{tag}-2020-native-original-readings.json'
        reading=json.loads(path.read_text())
        additions[reading['source_id']]=dict(path=str(path.relative_to(OUT.parent.parent)),native_constituents=reading['native_constituents'])
    actual=prior19+sum(x['native_constituents'] for x in additions.values())
    assert sorted(x['native_constituents'] for x in additions.values())==[16,17,17,22]
    assert actual==313
    savejson(OUT/'source/2020-native-count-correction.json',dict(
        earlier_draft_23_publication_native_count=279,
        corrected_23_publication_native_count=actual,
        source_publications=23,
        prior_19_publication_native_count=prior19,
        new_publication_native_counts=additions,
        arithmetic_difference=actual-279,
        explanation='Earlier report/SCHEMA prose omitted both distinct Jasper 17-column publications from the 23-publication count. All original source rows, candidate values, source hashes, and source positions are unchanged.',
    ))
    print('2020 23-publication coverage count corrected from279 to313; no vote change')

if __name__=='__main__':main()
