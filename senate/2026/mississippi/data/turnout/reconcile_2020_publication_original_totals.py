"""Reconcile independently read 2020 county publication TOTALs.

The peer ledger is opened only after the original readings exist, and is used
solely for a reciprocal comparison. Candidate values are never imported from it.
Original and amended publications are distinct; the original county set is not
asserted to have the same release vintage as the original state certificate.
"""
import csv,json,re
from acquire_sources import BASE,OUT,receipts,sha,savejson

NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
AMENDED={'Mike Espy':578691,'Cindy Hyde-Smith':709511,'Jimmy L. Edwards':23152}
ORIGINAL_STATE={'Mike Espy':578806,'Cindy Hyde-Smith':709539,'Jimmy L. Edwards':23152}

def main():
    ownpath=OUT/'2020-publication-original-total-readings.json'
    own=json.loads(ownpath.read_text())['sources']
    peerpath=BASE/'data/baselines/county-2020-publication-controls.json'
    peer={x['source_id']:x for x in json.loads(peerpath.read_text())['readings']}
    receipt={r['id']:r for r in receipts}
    assert len(own)==len(peer)==104 and len({x['source_id'] for x in own})==104
    differences=[]
    byslug={}
    for x in own:
        sid=x['source_id'];p=peer[sid]
        slug=sid.removeprefix('sos-2020-county-');county=slug.removesuffix('-amended')
        assert sid.startswith('sos-2020-county-')
        assert x['source_raw_sha256']==receipt[sid]['raw_sha256']
        assert sha((BASE/x['original_evidence']).read_bytes())==x['original_evidence_sha256']
        assert sha((BASE/x['original_card']).read_bytes())==x['original_card_sha256']
        byslug.setdefault(county,{})['amended' if slug.endswith('-amended') else 'original']=x
        for n in NAMES:
            if x['candidate_values'][n]!=p['candidate_values'][n]:
                differences.append(dict(source_id=sid,field=n,own=x['candidate_values'][n],peer=p['candidate_values'][n]))
        if x['source_page']!=p['source_page'] or x['source_raw_sha256']!=p['raw_sha256']:
            differences.append(dict(source_id=sid,field='page_or_source_hash'))
    assert len(byslug)==82 and sum('amended' in v for v in byslug.values())==22
    rows=list(csv.DictReader((OUT/'candidate-votes.csv').open()))
    csvcounty={}
    for r in rows:
        if r['election_date']!='2020-11-03' or r['office_literal'].strip()!='United States-Senate':continue
        slug=re.sub(r'[^a-z0-9]+','-',r['county'].lower()).strip('-')
        if slug=='jeff-davis':slug='jefferson-davis' # literal CSV abbreviation versus county PDF index
        csvcounty.setdefault(slug,{})[r['candidate_literal']]=int(r['votes'])
    assert set(csvcounty)==set(byslug) and all(set(v)==set(NAMES) for v in csvcounty.values())
    original={n:sum(v['original']['candidate_values'][n] for v in byslug.values()) for n in NAMES}
    selected={n:sum(v.get('amended',v['original'])['candidate_values'][n] for v in byslug.values()) for n in NAMES}
    county_differences=[];amendments=[]
    for slug,v in sorted(byslug.items()):
        s=v.get('amended',v['original']);expected=csvcounty[slug]
        for n in NAMES:
            if s['candidate_values'][n]!=expected[n]:county_differences.append(dict(county=slug,candidate=n,selected_source=s['candidate_values'][n],official_csv=expected[n]))
        if 'amended' in v:
            change={n:v['amended']['candidate_values'][n]-v['original']['candidate_values'][n] for n in NAMES}
            amendments.append(dict(county=slug,original_source_id=v['original']['source_id'],amended_source_id=v['amended']['source_id'],change=change,any_change=any(change.values())))
    assert not differences and not county_differences
    assert original=={'Mike Espy':578332,'Cindy Hyde-Smith':709491,'Jimmy L. Edwards':23150}
    assert selected==AMENDED and len(amendments)==22
    assert {x['county'] for x in amendments if x['any_change']}=={'adams','coahoma','prentiss'}
    out=dict(scope='All104 distinct actual 2020 county publication Senate printed TOTAL vectors, three candidates. Original-only readings compared post-extraction to independent peer; amended-where-published selection reconciled to official82-county CSV and amended state certificate. No common-vintage original-state inference or historical native/method acceptance.',original_readings_sha256=sha(ownpath.read_bytes()),peer_readings_sha256=sha(peerpath.read_bytes()),source_count=len(own),county_count=len(byslug),amended_publication_count=len(amendments),compared_candidate_fields=312,source_value_page_hash_differences=differences,selected_county_CSV_differences=county_differences,all_original_publications_candidate_sum=original,original_state_certificate=ORIGINAL_STATE,all_original_publications_minus_original_state_certificate={n:original[n]-ORIGINAL_STATE[n] for n in NAMES},amended_where_explicit_otherwise_original_candidate_sum=selected,amended_state_certificate=AMENDED,selected_minus_amended_state_certificate={n:selected[n]-AMENDED[n] for n in NAMES},amendment_comparisons=amendments,changed_amendment_count=sum(x['any_change'] for x in amendments),qualification='Numeric county TOTAL and primary statewide controls only. Printed source ordinals for many publications remain position hints and 2020 native units/method fields are not reconciled.')
    savejson(OUT/'2020-publication-original-peer-reconciliation.json',out)
    print('2020 original publications',len(own),'candidate positions',312,'peer differences',len(differences),'selected county CSV differences',len(county_differences),'changed amendments',out['changed_amendment_count'])

if __name__=='__main__':main()
