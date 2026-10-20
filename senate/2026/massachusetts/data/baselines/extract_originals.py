#!/usr/bin/env python3
"""Independent original-first CSV/HTML extraction. No peer/coordinator derivatives."""
import collections, csv, gzip, hashlib, io, json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
TAGS = ['2024-senate', '2020-senate', '2022-governor', '2024-president']
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(path, value):
    b=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress(b,mtime=0) if path.suffix=='.gz' else b)
def originals():
    pins=json.loads((ROOT/'source/shared-originals.json').read_text())['sources']
    result={}
    for p in pins:
        z=(ROOT/p['shared_path']).resolve().read_bytes(); b=gzip.decompress(z)
        assert sha(z)==p['stored_sha256'] and sha(b)==p['raw_sha256'] and len(b)==p['bytes']
        result[p['id']]=(p,b)
    return result
def sid(tag, suffix):
    return ('sos-' if tag=='2024-senate' else 'sos-observed-')+tag+'-'+suffix
def main():
    sources=originals(); controls={}; baseline=[]; municipal_baseline=[]; priority={}
    for tag in TAGS:
        tables={scope:list(csv.reader(io.StringIO(sources[sid(tag,scope+'-csv')][1].decode('utf-8-sig'),newline=''))) for scope in ['municipal','precinct']}
        m,n=tables['municipal'],tables['precinct']; heads=m[0][3:]
        assert heads==n[0][3:] and m[1]==n[1] and m[-1]==n[-1]
        assert heads[-3:]==['All Others','Blanks','Total Votes Cast']
        assert len(set(heads))==len(heads) # Do not silently deduplicate candidate keys.
        width=len(heads); positions=[]; objects={}; totals={}
        for scope,rows in tables.items():
            obs=[]
            for ordinal,row in enumerate(rows[2:],3):
                assert len(row)==width+3
                vals=[]
                for col,raw in enumerate(row[3:],4):
                    v=None if raw=='' else int(raw.replace(',',''))
                    assert v is None or v>=0
                    positions.append(dict(scope=scope,record_ordinal=ordinal,column_ordinal=col,header=heads[col-4],raw=raw,value=v))
                    vals.append(v)
                assert all(v is not None for v in vals), (tag,scope,ordinal)
                assert sum(vals[:-1])==vals[-1],(tag,scope,ordinal,vals)
                key=json.dumps(row[:3],ensure_ascii=False,separators=(',',':'))
                o=dict(source_id=sid(tag,scope+'-csv'),record_ordinal=ordinal,key=key,city_town=row[0],ward=row[1],pct=row[2],raw_row=row,values=vals,method=None,numeric_unit_id=None,registration=None,overvotes=None,undervotes=None)
                if ordinal==len(rows):
                    assert row[:3]==['TOTALS','','']; totals[scope]=o
                else: obs.append(o)
            assert len({o['key'] for o in obs})==len(obs)
            assert [sum(o['values'][i] for o in obs) for i in range(width)]==totals[scope]['values']
            objects[scope]=obs
        assert len(objects['municipal'])==351
        by={o['city_town']:o for o in objects['municipal']}; agg=collections.defaultdict(lambda:[0]*width)
        for o in objects['precinct']:
            for i,v in enumerate(o['values']): agg[o['city_town']][i]+=v
        assert set(agg)==set(by)
        assert all(agg[k]==by[k]['values'] for k in by)
        doc=BeautifulSoup(sources[sid(tag,'view')][1],'html.parser'); table=doc.select_one('#precinct_data'); assert table
        county=[]
        for tr in table.select('tr.m_item'):
            raw=[c.get_text(' ',strip=True) for c in tr.find_all(['th','td'],recursive=False)]
            if len(raw)==width+1: county.append(dict(raw=raw,values=[int(x.replace(',','')) for x in raw[1:]]))
        assert len(county)==14
        footer=[x.get_text(' ',strip=True) for x in table.select_one('tr.total').find_all(['th','td'],recursive=False)]
        assert [int(x.replace(',','')) for x in footer[1:]]==totals['municipal']['values']
        candidates=[]
        for c in doc.select('div.candidate'):
            party=c.select_one('.party')
            candidates.append(dict(raw_text=c.get_text(' ',strip=True),html_party=party.get_text(' ',strip=True) if party else None))
        assert len(candidates)==width-3
        v=totals['municipal']['values']; pair=v[0]+v[1]; named=sum(v[:-3]); reported=named+v[-3]
        ctl=dict(columns=heads,parties_ragged=m[1],state_values=v,named_pair=pair,named_candidate_total=named,reported_including_generic=reported,blanks=v[-2],total_votes_cast=v[-1],municipal_count=351,native_count=len(objects['precinct']),municipal_native_fields_compared=351*width,html_county_sums=[sum(x['values'][i] for x in county) for i in range(width)],html_county_minus_csv=[sum(x['values'][i] for x in county)-v[i] for i in range(width)],source_url=sources[sid(tag,'view')][0]['url'])
        controls[tag]=ctl
        extraction=dict(contest=tag,original_rows=tables,headers=m[:2],source_native_headers=n[:2],candidates_html=candidates,html_county_rows=county,html_footer=footer,objects=objects,state=totals,numeric_positions=positions,controls=ctl,source_pins={k:sources[sid(tag,k)][0] for k in ['municipal-csv','precinct-csv','view']},coverage={'voting_method':'not printed; null, no Election Day/early/mail allocation','native_type':'literal source context, not approved physical precinct or November2026 ID','generic_writeins':'All Others unallocated; eligibility/named scope unknown','registration':'not printed in contest exports','blank_semantics':'source Blanks; no separately published under/over split in these exports'})
        dump(ROOT/'extract'/f'{tag}-original-extraction.json.gz',extraction)
        for scope in objects:
            output=baseline if scope=='precinct' else municipal_baseline
            for o in objects[scope]:
                vs=o['values']; T=vs[0]+vs[1]; F=sum(vs[:-2]); N=sum(vs[:-3]); s=vs[0]/T if T else None
                output.append(dict(contest=tag,source_id=o['source_id'],source_url=sources[o['source_id']][0]['url'],record_ordinal=o['record_ordinal'],source_unit_key=o['key'],city_town=o['city_town'],ward=o['ward'],pct=o['pct'],scope=scope,A=heads[0],B=heads[1],A_votes=vs[0],B_votes=vs[1],other_named_votes=N-T,All_Others=vs[-3],named_candidate_total=N,reported_generic_total=F,Blanks=vs[-2],Total_Votes_Cast=vs[-1],pair_total=T,pair_participation_reported=T/F if F else None,pair_participation_ballots=T/vs[-1] if vs[-1] else None,A_pair_share=s,pair_margin=(vs[0]-vs[1])/T if T else None,A_reported_share=vs[0]/F if F else None,pair_weight=T/pair,baseline_net_votes=vs[0]-vs[1],gain_net_per_A_share_pp=.02*T,method='',numeric_unit_id='',registration='',undervotes='',overvotes='',candidate_values_json=json.dumps(dict(zip(heads[:-3],vs[:-3])),ensure_ascii=False,separators=(',',':'))))
            for basis in ['named_pair','all_named','reported_generic','ballots']:
                def count(o):
                    x=o['values']
                    return x[0]+x[1] if basis=='named_pair' else sum(x[:-3]) if basis=='all_named' else sum(x[:-2]) if basis=='reported_generic' else x[-1]
                ordered=sorted(objects[scope],key=lambda o:(-count(o),o['city_town'],o['ward'],o['pct'],o['record_ordinal']))
                total=sum(count(o) for o in ordered); cum=0; order=[]; k=None
                for rank,o in enumerate(ordered,1):
                    cum+=count(o)
                    if k is None and 5*cum>=4*total: k=rank
                    order.append(dict(rank=rank,source_unit_key=o['key'],city_town=o['city_town'],ward=o['ward'],pct=o['pct'],record_ordinal=o['record_ordinal'],votes=count(o),cumulative=cum,total=total))
                for o in order:o['minimum80_member']=o['rank']<=k
                write_csv(ROOT/'orders'/f'{tag}-{scope}-{basis}.csv',order)
                if tag=='2024-senate': priority[scope+'-'+basis]=dict(basis=basis,scope=scope,total=total,minimum80_count=k,previous_cumulative=order[k-2]['cumulative'] if k>1 else 0,crossing_cumulative=order[k-1]['cumulative'],top15_cumulative=order[14]['cumulative'],membership=[o['source_unit_key'] for o in order[:k]],full_order_file=f'orders/{tag}-{scope}-{basis}.csv',accepted_by_coordinator=False)
    write_csv(ROOT.parent/'county-baselines.csv',baseline)
    write_csv(ROOT/'municipal-baselines.csv',municipal_baseline)
    dump(ROOT/'controls.json',controls); dump(ROOT/'priority-set.json',priority)
    freeze=[]
    for p in sorted(list((ROOT/'extract').glob('*'))+list((ROOT/'orders').glob('*'))+[ROOT/'controls.json',ROOT/'priority-set.json',ROOT.parent/'county-baselines.csv',ROOT/'municipal-baselines.csv',ROOT/'source/shared-originals.json',Path(__file__)]):
        freeze.append(dict(path=str(p.relative_to(ROOT.parent.parent)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
    dump(ROOT/'source/original-first-freeze.json',dict(description='Independent original-source extraction and complete orders frozen before peer derivative access.',assets=freeze))
    print(json.dumps({'controls':controls,'priority':{k:{a:b for a,b in v.items() if a!='membership'} for k,v in priority.items()}},indent=2))
def write_csv(path, rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
if __name__=='__main__': main()
