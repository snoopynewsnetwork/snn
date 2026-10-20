#!/usr/bin/env python3
"""Read the immutable captured actual turnout peer, never modify its package."""
import gzip, hashlib, json, pathlib, tarfile
BASE=pathlib.Path(__file__).resolve().parent
def read(p): return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def main():
    t=tarfile.open(BASE/'source/frozen-turnout-peer.tar.gz')
    def peer(p):
        b=t.extractfile('data/turnout/'+p).read()
        return json.loads(gzip.decompress(b) if p.endswith('.gz') else b)
    own=read(BASE/'source/native-observations.json.gz');inv=read(BASE/'source/independent-inventory.json');books=read(BASE/'source/typed-workbooks.json.gz')
    differences=[]; checks={}; cells=0
    for year in [2024,2022,2020]:
        pb={b['member']['name']:b for b in peer(f'source/workbooks-{year}.json.gz')}
        for b in [x for x in books if x['year']==year]:
            other=pb[b['member']]
            assert b['member_sha256']==other['member']['sha256']
            for s in b['sheets']:
                ps=next(x for x in other['sheets'] if x['name']==s['name']); rows={r['row_1based']:r for r in ps['rows']}
                for r in s['selected_rows']:
                    pr=rows[r['row']]
                    for c,(typ,val) in enumerate(r['cells']):
                        cells+=1
                        if [typ,val]!=[pr['types'][c],pr['values'][c]]:differences.append({'scope':'typed-cell','year':year,'member':b['member'],'row':r['row'],'column':c+1,'own':[typ,val],'peer':[pr['types'][c],pr['values'][c]]})
                for r in s['row_descriptors']:
                    assert r['cells']==[[rows[r['row']]['types'][c],rows[r['row']]['values'][c]] for c in range(3)]
        pn=peer(f'native-units-{year}.json'); pm={x['key']:x for x in pn}; on=[x for x in own if x['year']==year]
        assert len(pm)==len(pn);checks[str(year)]={'same_keys':set(pm)=={x['key'] for x in on},'native_count':len(on),'candidate_disagreements':0,'administrative_disagreements':0}
        for u in on:
            p=pm[u['key']]
            assert (u['source_column'],u['native_header_literal'],u['county_fips'],u['member_sha256'])==(p['column_1based'],p['native_label'],p['county_fips'],p['member_sha256'])
            for a,b in zip(u['candidate_rows'],p['candidate_votes']):
                expected=[a['source_row'],u['source_column'],a['contest_literal'],a['party_literal'],a['candidate_literal'],a['cell'][0],a['cell'][1],a['votes']]
                actual=[b['row_1based'],b['column_1based'],b['contest_literal'],b['party_literal'],b['candidate_literal'],b['xls_type'],b['raw_value'],b['value']]
                if expected!=actual:
                    differences.append({'scope':'native-candidate','key':u['key'],'own':expected,'peer':actual});checks[str(year)]['candidate_disagreements']+=1
            pa=p['administrative_fields']+p['contest_other_fields']
            assert len(pa)==len(u['administrative_rows'])
            pa={x['row_1based']:x for x in pa}
            for a in u['administrative_rows']:
                b=pa[a['source_row']]
                if [a['cell'][0],a['cell'][1],a['value'],a['field_literal'],a['contest_literal']] != [b['xls_type'],b['raw_value'],b['value'],b['candidate_literal'],b['contest_literal']]:
                    differences.append({'scope':'native-admin','key':u['key'],'own':a,'peer':b});checks[str(year)]['administrative_disagreements']+=1
        oi=next(x for x in inv if x['year']==year)['native']
        independently_sorted=sorted(pn,key=lambda u:(-sum(c['value'] for c in u['candidate_votes'] if c['value'] is not None),u['key']))
        checks[str(year)]['full_raw_candidate_order_equal']=[x['key'] for x in independently_sorted]==[x['key'] for x in oi['full_order']]
        # Contract values are compared only after independent ordering of both raw count sets.
        if year==2024:
            contract=peer('priority-set.json');checks[str(year)]['contract']={
              'full_order_equal':contract['full_order']==[x['key'] for x in oi['full_order']],
              'priority_equal':contract['priority_keys']==oi['priority_keys'],
              'ordered_priority_equal':contract['ordered_priority_keys']==oi['priority_keys'],
              'remainder_equal':contract['remainder_keys']==oi['remainder_keys'],
              'parents_count':len(contract['parents']),
              'coverage':contract['coverage']}
            (BASE/'source/peer-contract-field-witness.json.gz').write_bytes(gzip.compress(json.dumps(contract,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    result={'peer_agent_id':'5b42c895-68ea-40c4-9b7c-534e46d14d7a','peer_frozen_manifest_sha256':'4e2a1f5ab3c66508444c112f9e6430006dce94f795a172837c7b95eaee557207','own_original_first_v1_sha256':'941f8c78065a55966c2514b6e99bc1e148ec200d9cc1b269cf461146e83b940d','typed_cells_compared':cells,'checks':checks,'differences':differences,'coordinator_acceptance':False,'legal_geographic_approval':False,'scope':'Original typed/raw equality distinct from corrected/derived candidate or legal claims. Own initial witness retained; v2 admin expansion includes straight-party fields.'}
    (BASE/'peer-reconciliation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'typed_cells_compared':cells,'differences':len(differences),'all_year_raw_orders_equal':all(v['full_raw_candidate_order_equal'] for v in checks.values()),'contract_arrays_equal':all(checks['2024']['contract'][k] for k in ['full_order_equal','priority_equal','ordered_priority_equal','remainder_equal'])},indent=2))
if __name__=='__main__':main()
