"""One-time authoring freeze; no network, producer import or producer write."""
from common import *
def main():
    target=R/'inputs.json';assert not target.exists(),'Freeze exists; create a new version, never replace it'
    receipts=[pin(p) for p in sorted((R/'acquired').glob('*.receipt.json'))]
    write(target,dump(dict(schema='ri-official-inputs-v1',authority_path=AUTHORITY,receipts=receipts,
        reader_representations=[pin(p) for p in sorted((R/'acquired').glob('*.web-reader.json'))],
        qualification='Exact individual immutable receipt/body inputs, including failures. No mutable news manifest or producer writer. Missing prior duplicate-request metadata remains explicitly unavailable in history/acquisition-issues.json.')))
    a=parsed(S/AUTHORITY);paths={r['path'] for r in a['frozen_file_pins']}
    paths|={r['path'] for r in a['complete_source_object_reference_bodies']}
    for p in a['historical_full_body_resolvers']:
        st=p['storage']
        if st['kind']=='tar_gzip_member':paths.add(st['archive']['path'])
        elif st['kind']=='ordered_tar_gzip_member':paths|={r['path'] for r in st['parts']}
        else:paths.add(st['file']['path'])
    originals={}
    for mf in ['data/turnout/asset-manifest.json','data/baselines/asset-manifest.json']:
        for r in parsed(S/mf)['external_original_references']:
            paths.add(r['path']);originals[r['path'],r['stored_sha256']]=r
    assert AUTHORITY not in paths
    write(R/'external-inputs.json',dump(dict(authority_path=AUTHORITY,
        complete_files=[pin(S/p) for p in sorted(paths)],
        whole_original_entities=list(originals.values()),
        qualifications='Whole underlying files/ordered ledger partitions and original entities, referenced once rather than copied. Acceptance authority itself is PATH ONLY. Exact historical bodies resolve by path+SHA through replay/reconstruct, never a newer current body. All original scenarios/outcomes remain complete referenced data without new model/equality assignments.')))
    print('frozen receipts',len(receipts),'external files',len(paths),'original entities',len(originals))
if __name__=='__main__':main()
