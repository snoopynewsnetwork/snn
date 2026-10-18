"""Read-only comparison to actual independent peer's stable schema and bytes."""
import csv, gzip, json
from pathlib import Path
from extract import HERE, dump, sha
from build import readcsv, rank

PEER=HERE.parent/'baselines'
PEER_ID='21fc8593-07df-4386-9edf-ac5edb32c57b'

def main():
    files={};audits=[];cells=0
    def load(p):
        b=p.read_bytes();files[str(p.relative_to(HERE.parent.parent))]=dict(sha256=sha(b),bytes=len(b))
        text=gzip.decompress(b).decode() if p.suffix=='.gz' else b.decode()
        return list(csv.DictReader(text.splitlines()))
    def compare(a,b,keys,fields,label):
        nonlocal cells
        ak={tuple(r[k] for k in keys):r for r in a};bk={tuple(r[k] for k in keys):r for r in b}
        assert len(ak)==len(a) and len(bk)==len(b)
        assert set(ak)==set(bk),(label,'geography mismatch')
        n=0
        for key in ak:
            for field in fields:
                assert ak[key][field]==bk[key][field],(label,key,field,ak[key][field],bk[key][field])
                n+=1
        cells+=n;audits.append(dict(label=label,rows=len(ak),fields=fields,compared_cells=n,differences=0))
    meta=json.loads((HERE/'source/workbook-context.json').read_text());pm=PEER/'source/workbook-context.json';b=pm.read_bytes();files[str(pm.relative_to(HERE.parent.parent))]=dict(sha256=sha(b),bytes=len(b));pmeta=json.loads(b)
    raw_context_cells=0
    for year in [2024,2022,2020]:
        ours=readcsv(f'native-{year}.csv.gz');peer=load(PEER/f'native-{year}.csv.gz')
        # Compare every retained original field, including literal blanks/no data,
        # and source positions. Derived warning prose is intentionally not a key.
        fields=[k for k in ours[0] if k in peer[0]]
        compare(ours,peer,['native_key'],fields,f'native-{year}')
        a=readcsv(f'county-controls-{year}.csv');b=load(PEER/f'county-controls-{year}.csv')
        compare(a,b,['county_key'],list(a[0]),f'county-{year}')
        a=readcsv(f'municipal-controls-{year}.csv');b=load(PEER/f'municipal-controls-{year}.csv.gz')
        fields=[k for k in a[0] if k in b[0]]
        compare(a,b,['county_fips','MCDNAME'],fields,f'municipal-{year}')
        assert meta[str(year)]['source_sha256']==pmeta[str(year)]['source_sha256']
        assert meta[str(year)]['columns']==pmeta[str(year)]['columns']
        for sheet in ['Notes','Fields','Counties']:
            a=meta[str(year)]['metadata'][sheet];b=pmeta[str(year)]['metadata'][sheet]
            def rawcells(s):
                return {(r['source_row'],c.get('cell',col)):{k:c.get(k) for k in ['value','type','formula']} for r in s['rows'] for col,c in r['cells'].items()}
            aa=rawcells(a);bb=rawcells(b)
            assert a['zip_path']==b['zip_path'] and aa==bb,(year,sheet)
            raw_context_cells+=len(aa)
        field='MNGOVTOTAL' if year==2022 else 'USSENTOTAL'
        for level in ['county','native']:
            rows=readcsv(f'{"county-controls" if level=="county" else "native"}-{year}.csv'+('.gz' if level=='native' else ''))
            key='county_key' if level=='county' else 'native_key'
            ranking=rank(rows,field,key)
            peer_rank=load(PEER/f'{level}-{year}-ranked.csv.gz')
            for r,p in zip(ranking['order'],peer_rank):
                assert r['key']==p['unit_key'] and r['votes']==int(p['contest_votes']) and r['cumulative_votes']==int(p['cumulative_votes'])
                assert r['rank']==int(p['rank']) and ranking['denominator']==int(p['all_state_contest_votes'])
            assert len(peer_rank)==len(rows)
            audits.append(dict(label=f'full-order-{year}-{level}',rows=len(rows),differences=0))
    pcontract=PEER/'priority-contract.json';pb=pcontract.read_bytes();files[str(pcontract.relative_to(HERE.parent.parent))]=dict(sha256=sha(pb),bytes=len(pb));pc=json.loads(pb)
    ours=json.loads((HERE/'priority-set.json').read_text());p=pc['2024-county']
    assert ours['complete_ordered_county_keys']==p['order']
    assert ours['ordered_priority_keys']==p['priority_keys']
    for own,other in [('minimum80_count','minimum80_count'),('minimum80_votes','minimum80_votes'),('previous_votes','previous_votes'),('crossing_key','crossing_key'),('remainder_votes','outside_votes')]: assert ours['minimum80'][own]==p[other]
    # Each peer candidate row must equal the independently extracted source value.
    candidate=load(PEER/'candidate-votes.csv.gz');required={'2024-senate':(2024,'USSEN'),'2024-president':(2024,'USPRS'),'2022-governor':(2022,'MNGOV'),'2020-senate':(2020,'USSEN')}
    sources={(y,l):{r['native_key' if l=='native' else 'county_key']:r for r in readcsv(f'{"native" if l=="native" else "county-controls"}-{y}.csv'+('.gz' if l=='native' else ''))} for y in [2024,2022,2020] for l in ['native','county']}
    n=0
    for r in candidate:
        if r['contest'] not in required or r['level'] not in ['county','native']: continue
        y,_=required[r['contest']];a=sources[y,r['level']][r['unit_key']]
        assert r['votes']==a[r['source_field']]
        n+=1
    controls=json.loads((HERE/'source/primary-controls.json').read_text())
    expected=sum((len(sources[int(y),'native'])+87)*sum(len(cs) for cs in c['contests'].values()) for y,c in controls.items() if y.isdigit())
    assert n==expected,(n,expected)
    peer_named=load(PEER/'source/named-writeins-2020.csv')
    own_named=list(csv.DictReader((HERE/'source/named-writeins-2020.csv').open()))
    pi={(r['county_fips'],r['candidate_name']):r for r in peer_named}
    assert len(own_named)==len(pi)==522
    for r in own_named:assert r['votes']==pi[r['county_fips'],r['source_candidate_label']]['votes']
    # Detect concurrent changes, rather than blessing a moving peer extract.
    for path,record in files.items():assert sha((HERE.parent.parent/path).read_bytes())==record['sha256']
    dump(HERE/'peer-reconciliation.json',dict(status='pass',peer_actual_id=PEER_ID,shared_source_cells_compared=cells,candidate_vote_rows_compared=n,
        raw_context_sheets_compared=['Notes','Fields','Counties'],raw_context_cells_compared=raw_context_cells,source_column_maps_equal=True,complete_orders_and_minimum80_equal=True,
        separate_2020_named_writein_county_cells_compared=522,separate_2020_named_writein_difference=0,
        audits=audits,peer_readonly_files=files,acceptance='Independent historical arithmetic agreement only; coordinator owns dispatch/geographic approval'))
    print(f'PASS: {cells} shared cells, {n} candidate rows; all county/native orders and priority agree')

if __name__=='__main__':main()
