"""Reciprocal read-only historical native replay after both original readings.

Exact peer derivative bodies are frozen as new38-view v2; first7v1 stays unchanged. Own values come from an immutable
original-reading witness, never from peer fields or a cross-year/name join.
"""
import argparse,csv,gzip,io,json
from collections import Counter
from sources import OUT,BASE,original,sha,save

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture',action='store_true');a=ap.parse_args()
    folder=OUT/'source/native-2020-peer-38views-v2';sp=folder/'snapshot.json'
    ownsp=OUT/'source/native-2020-104views-v1/snapshot.json';ownsnapshot=json.loads(ownsp.read_text())
    ownpin=next(p for p in ownsnapshot['pins'] if p['original_path'].endswith('native-2020-additional-candidate-votes.csv'))
    if a.capture and not sp.exists():
        folder.mkdir(exist_ok=True);files=['2020-native-alcorn-original-readings.json', '2020-native-alcorn-original-candidate-votes.csv', 'amite-2020-native-original-readings.json', 'amite-2020-native-original-cells.csv', 'attala-2020-native-original-readings.json', 'attala-2020-native-original-cells.csv', 'benton-2020-native-original-readings.json', 'benton-2020-native-original-cells.csv', 'benton-amended-2020-native-original-readings.json', 'benton-amended-2020-native-original-cells.csv', 'calhoun-2020-native-original-readings.json', 'calhoun-2020-native-original-cells.csv', 'carroll-2020-native-original-readings.json', 'carroll-2020-native-original-cells.csv', 'choctaw-amended-2020-native-original-readings.json', 'choctaw-amended-2020-native-original-cells.csv', 'choctaw-original-2020-native-original-readings.json', 'choctaw-original-2020-native-original-cells.csv', 'claiborne-2020-native-original-readings.json', 'claiborne-2020-native-original-cells.csv', 'clarke-2020-native-original-readings.json', 'clarke-2020-native-original-cells.csv', 'clay-2020-native-original-readings.json', 'clay-2020-native-original-cells.csv', 'clay-amended-2020-native-original-readings.json', 'clay-amended-2020-native-original-cells.csv', 'franklin-2020-native-original-readings.json', 'franklin-2020-native-original-cells.csv', 'george-2020-native-original-readings.json', 'george-2020-native-original-cells.csv', 'greene-2020-native-original-readings.json', 'greene-2020-native-original-cells.csv', 'grenada-2020-native-original-readings.json', 'grenada-2020-native-original-cells.csv', 'issaquena-2020-native-original-readings.json', 'issaquena-2020-native-original-cells.csv', 'jasper-amended-2020-native-original-readings.json', 'jasper-amended-2020-native-original-cells.csv', 'jasper-original-2020-native-original-readings.json', 'jasper-original-2020-native-original-cells.csv', 'jefferson-2020-native-original-readings.json', 'jefferson-2020-native-original-cells.csv', 'kemper-2020-native-original-readings.json', 'kemper-2020-native-original-cells.csv', 'newton-2020-native-original-readings.json', 'newton-2020-native-original-cells.csv', 'noxubee-2020-native-original-readings.json', 'noxubee-2020-native-original-cells.csv', 'perry-2020-native-original-readings.json', 'perry-2020-native-original-cells.csv', 'quitman-2020-native-original-readings.json', 'quitman-2020-native-original-cells.csv', 'sharkey-amended-2020-native-original-readings.json', 'sharkey-amended-2020-native-original-cells.csv', 'sharkey-original-2020-native-original-readings.json', 'sharkey-original-2020-native-original-cells.csv', 'smith-2020-native-original-readings.json', 'smith-2020-native-original-cells.csv', 'stone-2020-native-original-readings.json', 'stone-2020-native-original-cells.csv', 'tishomingo-2020-native-original-readings.json', 'tishomingo-2020-native-original-cells.csv', 'tunica-2020-native-original-readings.json', 'tunica-2020-native-original-cells.csv', 'washington-amended-2020-native-original-readings.json', 'washington-amended-2020-native-original-cells.csv', 'washington-original-2020-native-original-readings.json', 'washington-original-2020-native-original-cells.csv', 'wilkinson-2020-native-original-readings.json', 'wilkinson-2020-native-original-cells.csv', 'winston-2020-native-original-readings.json', 'winston-2020-native-original-cells.csv', 'yalobusha-amended-2020-native-original-readings.json', 'yalobusha-amended-2020-native-original-cells.csv', 'yalobusha-original-2020-native-original-readings.json', 'yalobusha-original-2020-native-original-cells.csv']
        pins=[]
        for filename in files:
            p=BASE/'data/turnout'/filename;raw=p.read_bytes();stored=gzip.compress(raw,mtime=0);q=folder/(filename+'.gz');assert len(stored)<40000000;q.write_bytes(stored)
            pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(raw),original_sha256=sha(raw),stored_path=str(q.relative_to(BASE)),stored_bytes=len(stored),stored_sha256=sha(stored)))
        save(sp,dict(qualification='Thirty-eight source-publication peer original3Senatecandidate readings, exact bodies captured read-only after own original review. No peer vote import to own ledger.',own_original_witness=dict(path=str(ownsp.relative_to(BASE)),bytes=ownsp.stat().st_size,sha256=sha(ownsp.read_bytes())),own_flat_input=ownpin,pins=pins))
    snap=json.loads(sp.read_text());assert sha(ownsp.read_bytes())==snap['own_original_witness']['sha256'];assert ownpin==snap['own_flat_input']
    stored=(BASE/ownpin['stored_path']).read_bytes();raw=gzip.decompress(stored);assert len(raw)==ownpin['original_bytes'] and sha(raw)==ownpin['original_sha256'] and sha(stored)==ownpin['stored_sha256']
    key=lambda r:(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate'])
    ownrows=list(csv.DictReader(io.StringIO(raw.decode())));own={key(r):r for r in ownrows};assert len(own)==len(ownrows)
    seen=set();diffs=[];labels=[];counts=Counter();sources={};page_pairs={};peer_bodies={}
    for pin in snap['pins']:
        stored=(BASE/pin['stored_path']).read_bytes();body=gzip.decompress(stored);assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256'] and len(body)==pin['original_bytes'] and sha(body)==pin['original_sha256'];peer_bodies[pin['original_path']]=body
        if not pin['original_path'].endswith('.csv'):continue
        for r in csv.DictReader(io.StringIO(body.decode())):
            k=key(r);assert k not in seen;seen.add(k);o=own[k];assert r['native_source_key']==o['source_key'];assert r['source_raw_sha256']==o['source_raw_sha256'];sources[k[0]]=o['source_raw_sha256'];counts[o['role']]+=1
            if r['votes']!=o['votes'] or r['role']!=o['role']:diffs.append(dict(key=k,own_votes=o['votes'],peer_votes=r['votes'],own_role=o['role'],peer_role=r['role']))
            pl=r.get('literal_native_label',r.get('label_literal'));ol=o['literal_native_label']
            if ' '.join(pl.split())!=' '.join(ol.split()):labels.append(dict(key=k,own=ol,peer=pl))
            pr=r.get('full_original_raster',r.get('original_full_page_raster'));op=o['full_original_render_path'];q=page_pairs.setdefault((k[0],k[1]),dict(source_id=k[0],PDFpage=k[1],own_raster=op,peer_raster=pr));assert q['own_raster']==op and q['peer_raster']==pr
    for sid,h in sources.items():assert sha(original(sid))==h
    pages=[]
    for q in page_pairs.values():
        p=BASE/q['own_raster'];peer=BASE/q['peer_raster'];q.update(own_raster_sha256=sha(p.read_bytes()),peer_raster_sha256=sha(peer.read_bytes()),same_raster_bytes=p.read_bytes()==peer.read_bytes());pages.append(q)
    assert len(seen)==2277 and len(sources)==38 and counts==Counter(source_native_reporting_constituent=1554,source_TOTAL=114,unused_template_column=609)
    assert not diffs and not labels,(diffs,labels)
    result=dict(status='pass_bounded_post_original_38_publication_replay',peer_snapshot=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),own_original_witness=snap['own_original_witness'],compared_positions=len(seen),source_publications=len(sources),native_constituents=518,candidate_positions_by_role=dict(counts),source_raw_hashes=sources,source_page_render_pairs=pages,value_role_differences=diffs,label_differences_after_whitespace_only=labels,qualification='Source raw hash/PDFpage/physical column/candidate/source key/role and literal header jointly checked only after original source readings. Both full-page raster hashes retained, no identical raster, exact numeric/header polygon, parsed-ID, unavailable peer party field, source-vintage/year identity or current geography agreement inferred. All blanks retain explicit own/peer null scope; no invented zero or residual allocation.',complete2020_native=False,complete_historical_methods=False,current2026_geography_approved=False)
    save(OUT/'native-2020-peer-38views-v2-reconciliation.json',result);body=(OUT/'native-2020-peer-38views-v2-reconciliation.json').read_bytes();frozen=folder/'reconciliation.json'
    if frozen.exists():assert frozen.read_bytes()==body,'A changed witness needs a new version'
    else:frozen.write_bytes(body)
    print('PASS38 separate2020publications/518native/2277positions; all values/roles/whitespace-only labels agree; source/render scope qualified')
if __name__=='__main__':main()
