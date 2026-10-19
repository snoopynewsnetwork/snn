"""Immutable combined named-candidate publication witness; broader gates stay open."""
import gzip,json
from sources import OUT,BASE,save,sha
def main():
    folder=OUT/'source/native-2024-named-v1';snapshot=folder/'snapshot.json'
    if snapshot.exists():
        x=json.loads(snapshot.read_text())
        for p in x['pins']:
            stored=(BASE/p['stored_path']).read_bytes();raw=gzip.decompress(stored);assert len(stored)==p['stored_bytes'] and sha(stored)==p['stored_sha256'] and len(raw)==p['original_bytes'] and sha(raw)==p['original_sha256']
        pref=BASE/x['preferred82_snapshot']['path'];assert sha(pref.read_bytes())==x['preferred82_snapshot']['sha256'];print('Verified immutable named2024v1');return
    folder.mkdir();pins=[]
    for name in ['native-alternative-allfield-readings.json','native-alternative-allfield-candidate-votes.csv','native-2024-candidate-controls.json','native-2024-candidate-controls.csv','native-presidential-peer-batches-reconciliation.json']:
        p=OUT/name;raw=p.read_bytes();stored=gzip.compress(raw,mtime=0);q=folder/(name+'.gz');assert len(stored)<40000000;q.write_bytes(stored);pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(raw),original_sha256=sha(raw),stored_path=str(q.relative_to(BASE)),stored_bytes=len(stored),stored_sha256=sha(stored)))
    pref=OUT/'source/native-allfield-82views/snapshot.json';save(snapshot,dict(version=1,qualification='Every named9Pres/2Sen candidate position in84 separately scoped2024SEMSpublication views. Preferred82and2alternatives distinct; each source closes printedTOTAL. Generic/method/vendor/ballot/registration/history/currentgeometry and fullpeer gates remainOPEN. Bounded52viewPres peer witness plus separately retained2viewall11proof, not fullpeer acceptance.',preferred82_snapshot=dict(path=str(pref.relative_to(BASE)),bytes=pref.stat().st_size,sha256=sha(pref.read_bytes())),pins=pins,preferred82=dict(source_views=82,native_constituents=1736,source_pages=206,TOTAL_columns=82,unused_columns=437,parallel_columns=11,numeric_positions=20119,null_positions=4807),nonadditive_alternatives=dict(source_views=2,native_constituents=43,source_pages=5,TOTAL_columns=2,unused_columns=10,numeric_positions=495,null_positions=110),all84_separate_source_scopes=dict(source_views=84,source_pages=211,source_column_objects=2321,all11_candidate_positions=25531,numeric_positions=20614,null_positions=4917),whole_question_complete=False,current2026_geography_approved=False));print('Frozen named2024v1',len(pins),'new complete byte pins plus immutable82view snapshot')
if __name__=='__main__':main()
