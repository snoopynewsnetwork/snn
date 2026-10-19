"""Extend immutable first-ten-stage peer evidence with original-read Yalobusha.

Earlier ten exact bodies are reused by hash, without refreshing their metadata.
Only the two explicitly announced Yalobusha derivatives are newly captured.
"""
import argparse,csv,gzip,io,json
from collections import Counter
from sources import OUT,BASE,sha,save,original

def readpin(pin):
    z=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(z)
    assert len(z)==pin['stored_bytes']<40000000 and sha(z)==pin['stored_sha256']
    assert len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
    return raw

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture',action='store_true');a=ap.parse_args()
    folder=OUT/'source/native-2018-peer-12views-v2';sp=folder/'snapshot.json'
    priorpath=OUT/'source/native-2018-peer-10views-v1/snapshot.json';prior=json.loads(priorpath.read_text())
    ownsp=OUT/'source/native-2018-78views-v1/snapshot.json';own=json.loads(ownsp.read_text())
    flatpin=next(p for p in own['pins'] if p['original_path'].endswith('/native-2018-original-candidate-votes.csv'))
    if a.capture and not sp.exists():
        folder.mkdir(exist_ok=True);pins=[]
        for pin in prior['pins']:readpin(pin);pins.append(pin)
        for suffix in ['readings.json','cells.csv']:
            path=BASE/'data/turnout'/('2018-yalobusha-two-stage-native-original-'+suffix);body=path.read_bytes();z=gzip.compress(body,mtime=0);p=folder/(path.name+'.gz');assert len(z)<40000000;p.write_bytes(z)
            pins.append(dict(original_path=str(path.relative_to(BASE)),original_bytes=len(body),original_sha256=sha(body),stored_path=str(p.relative_to(BASE)),stored_bytes=len(z),stored_sha256=sha(z)))
        save(sp,dict(scope='Twelve distinct original-read county-stage scopes; prior ten bodies reused exactly, only Yalobusha two derivatives newly frozen after own original reading. No vote import.',prior_witness=dict(path=str(priorpath.relative_to(BASE)),bytes=priorpath.stat().st_size,sha256=sha(priorpath.read_bytes())),own_witness=dict(path=str(ownsp.relative_to(BASE)),bytes=ownsp.stat().st_size,sha256=sha(ownsp.read_bytes())),own_flat=flatpin,pins=pins))
    snap=json.loads(sp.read_text());assert snap['own_flat']==flatpin and snap['own_witness']['sha256']==sha(ownsp.read_bytes())
    assert snap['prior_witness']['sha256']==sha(priorpath.read_bytes()) and snap['pins'][:10]==prior['pins'] and len(snap['pins'])==12
    ownrows=list(csv.DictReader(io.StringIO(readpin(flatpin).decode())));ownby={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r for r in ownrows};assert len(ownby)==len(ownrows)
    roles={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused'}
    seen=set();units=set();counts=Counter();sources={};pages={};differences=[]
    for pin in snap['pins']:
        raw=readpin(pin)
        if not pin['original_path'].endswith('.csv'):continue
        for p in csv.DictReader(io.StringIO(raw.decode())):
            key=(p['source_id'],int(p['source_pdf_page']),int(p['physical_source_column']),p['candidate']);assert key not in seen;seen.add(key);o=ownby[key];role=roles[p['role']]
            assert p['county_fips']==o['county_fips'] and p['source_raw_sha256']==o['source_raw_sha256']
            assert p['source_native_key']==o['county_fips']+':'+o['source_key'] and p['party_field_literal']==o['party_literal']==''
            counts[role]+=1
            if p['votes']!=o['votes'] or role!=o['role'] or ' '.join(p['literal_source_header'].split())!=' '.join(o['literal_native_label'].split()):differences.append(dict(key=key,own=o,peer=p))
            if role=='native':units.add(key[:3])
            sid=key[0];sources[sid]=p['source_raw_sha256'];pair=pages.setdefault((sid,key[1]),dict(source_id=sid,PDFpage=key[1],own_raster=o['full_original_render_path'],peer_raster=p['original_raster']))
            assert pair['own_raster']==o['full_original_render_path'] and pair['peer_raster']==p['original_raster']
    assert len(seen)==660 and len(sources)==12 and len(units)==136 and counts==Counter(native=408,TOTAL=36,unused=216);assert not differences,differences
    for sid,h in sources.items():assert sha(original(sid))==h
    for q in pages.values():q.update(own_raster_sha256=sha((BASE/q['own_raster']).read_bytes()),peer_raster_sha256=sha((BASE/q['peer_raster']).read_bytes()))
    path=OUT/'native-2018-peer-12views-v2-reconciliation.json'
    save(path,dict(status='pass_bounded_post_original_twelve_stage_replay',peer_snapshot=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),own_original_witness=snap['own_witness'],prior_witness=snap['prior_witness'],prior_ten_bodies_reused_byte_exact=True,source_stage_views=12,source_native_observations=136,source_candidate_positions=660,numeric_positions=444,unused_null_positions=216,candidate_positions_by_role=dict(counts),source_hashes=sources,source_page_render_pairs=list(pages.values()),differences=differences,qualification='Exact rawsource/FIPS/PDFpage/physicalcolumn/candidate/value/role and whitespace-folded literal headers agree after independent original readings. First ten frozen peer bodies keep their earlier metadata declarations; only Yalobusha bodies newly captured. Source keys compare explicit FIPS-prefix components, not byte-identical keys/current IDs. Both render hashes remain separately recorded; no raster/reading-box/current-geometry/cross-stage equivalence inferred. Unprinted party fields remain blank, not party pooling.',complete2018_native=False,current2026_geography_approved=False))
    frozen=folder/'reconciliation.json'
    if frozen.exists():assert frozen.read_bytes()==path.read_bytes(),'Changed evidence requires a new immutable version'
    else:frozen.write_bytes(path.read_bytes())
    print('PASS2018 twelve separate stages/136native/660positions:444numeric216null')

if __name__=='__main__':main()
