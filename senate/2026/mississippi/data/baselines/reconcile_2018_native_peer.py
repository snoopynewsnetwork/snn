"""Freeze/replay ten actual2018 source-stage native scopes after original reads.

Explicit five-county whitelist; no expanding mutable glob, peer vote import,
name-only join, or alteration of a peer/frozen reading.
"""
import argparse,csv,gzip,io,json
from collections import Counter
from sources import OUT,BASE,sha,save,original

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture',action='store_true');a=ap.parse_args();folder=OUT/'source/native-2018-peer-10views-v1';sp=folder/'snapshot.json';ownsp=OUT/'source/native-2018-58views-v1/snapshot.json';own=json.loads(ownsp.read_text());flatpin=next(p for p in own['pins'] if p['original_path'].endswith('/native-2018-original-candidate-votes.csv'))
    if a.capture and not sp.exists():
        folder.mkdir(exist_ok=True);pins=[]
        for county in ['issaquena','benton','franklin','smith','montgomery']:
            for suffix in ['readings.json','cells.csv']:
                path=BASE/'data/turnout'/f'2018-{county}-two-stage-native-original-{suffix}';body=path.read_bytes();z=gzip.compress(body,mtime=0);p=folder/(path.name+'.gz');assert len(z)<40000000;p.write_bytes(z);pins.append(dict(original_path=str(path.relative_to(BASE)),original_bytes=len(body),original_sha256=sha(body),stored_path=str(p.relative_to(BASE)),stored_bytes=len(z),stored_sha256=sha(z)))
        save(sp,dict(scope='Five independently original-read counties, two separate2018stages each; exact peer bodies frozen read-only after own source extraction, not peer vote import.',own_witness=dict(path=str(ownsp.relative_to(BASE)),bytes=ownsp.stat().st_size,sha256=sha(ownsp.read_bytes())),own_flat=flatpin,pins=pins))
    snap=json.loads(sp.read_text());assert snap['own_flat']==flatpin and snap['own_witness']['sha256']==sha(ownsp.read_bytes());z=(BASE/flatpin['stored_path']).read_bytes();r=gzip.decompress(z);assert len(z)==flatpin['stored_bytes'] and sha(z)==flatpin['stored_sha256'] and len(r)==flatpin['original_bytes'] and sha(r)==flatpin['original_sha256']
    ownrows=list(csv.DictReader(io.StringIO(r.decode())));ownkey=lambda r:(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']);ownby={ownkey(r):r for r in ownrows};assert len(ownby)==len(ownrows);roles={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused'};seen=set();units=set();counts=Counter();sources={};pages={};differences=[]
    for pin in snap['pins']:
        z=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(z);assert len(z)==pin['stored_bytes'] and sha(z)==pin['stored_sha256'] and len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
        if not pin['original_path'].endswith('.csv'):continue
        for p in csv.DictReader(io.StringIO(raw.decode())):
            key=(p['source_id'],int(p['source_pdf_page']),int(p['physical_source_column']),p['candidate']);assert key not in seen;seen.add(key);o=ownby[key];role=roles[p['role']];assert p['county_fips']==o['county_fips'] and p['source_raw_sha256']==o['source_raw_sha256'];assert p['source_native_key']==o['county_fips']+':'+o['source_key'];assert p['party_field_literal']==o['party_literal']=='';counts[role]+=1
            if p['votes']!=o['votes'] or role!=o['role'] or ' '.join(p['literal_source_header'].split())!=' '.join(o['literal_native_label'].split()):differences.append(dict(key=key,own=o,peer=p))
            if role=='native':units.add(key[:3])
            sid=key[0];sources[sid]=p['source_raw_sha256'];pair=pages.setdefault((sid,key[1]),dict(source_id=sid,PDFpage=key[1],own_raster=o['full_original_render_path'],peer_raster=p['original_raster']));assert pair['own_raster']==o['full_original_render_path'] and pair['peer_raster']==p['original_raster']
    assert len(seen)==528 and len(sources)==10 and len(units)==114 and counts==Counter(native=342,TOTAL=30,unused=156);assert not differences,differences
    for sid,h in sources.items():assert sha(original(sid))==h
    for q in pages.values():q.update(own_raster_sha256=sha((BASE/q['own_raster']).read_bytes()),peer_raster_sha256=sha((BASE/q['peer_raster']).read_bytes()))
    path=OUT/'native-2018-peer-10views-v1-reconciliation.json';save(path,dict(status='pass_bounded_post_original_ten_stage_replay',peer_snapshot=dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes())),own_original_witness=snap['own_witness'],source_stage_views=10,source_native_observations=114,source_candidate_positions=528,numeric_positions=372,unused_null_positions=156,candidate_positions_by_role=dict(counts),source_hashes=sources,source_page_render_pairs=list(pages.values()),differences=differences,qualification='Exact rawsource/FIPS/PDFpage/physicalcolumn/candidate/value/role and whitespace-folded literal headers agree only after independent original readings. Source keys have explicitly different FIPS-prefix representations and are compared by components, not byte-identical keys. Blank party fields mean unprinted, not inferred party or pool union. Both raster hashes retained separately; no identical raster, reading-box/crop/current-ID/geography/cross-stage equivalence claimed. Current FranklinMccall bytes checked, priorMcCall frozen witness unchanged.',complete2018_native=False,current2026_geography_approved=False));frozen=folder/'reconciliation.json'
    if frozen.exists():assert frozen.read_bytes()==path.read_bytes(),'Changed evidence requires a new immutable version'
    else:frozen.write_bytes(path.read_bytes())
    print('PASS2018ten separate stages/114native/528positions:372numeric156null; source/role/whitespace-only labels agree')

if __name__=='__main__':main()
