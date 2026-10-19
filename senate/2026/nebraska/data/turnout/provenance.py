"""Pin owned artifacts and exact shared original entities, without mutable ledger dependency."""
from source_io import *
import html,re,urllib.parse

def pin(p):return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
def main():
    shared=[];errors=[]
    for r in LEDGER:
        if not r.get('asset'):
            errors.append(r);continue
        p=NEWS/r['asset'];stored=p.read_bytes();raw=gzip.decompress(stored)
        assert sha(stored)==r['stored_sha256']and sha(raw)==r['raw_sha256']and len(raw)==r['bytes'],r['id']
        shared.append({'receipt':r,'original_reference':pin(p),'raw_bytes':len(raw),'raw_sha256':sha(raw),
          'role':'Immutable shared evidence; count authority only if selected by source-scoped extract/build. Newsroom/failed/old/test observations are not admitted votes.'})
    own=[]
    for p in sorted((OUT/'source').glob('*.receipt.json')):
        r=json.loads(p.read_text());body=p.with_name(r['asset']);stored=body.read_bytes();raw=gzip.decompress(stored)
        assert len(raw)==r['raw_bytes']and sha(raw)==r['raw_sha256']and sha(stored)==r['stored_sha256']
        own.append({'receipt':r,'receipt_pin':pin(p),'original_reference':pin(body)})
    # Exact parent href checks; no guessed URL or candidate ID chain.
    chains=[]
    for parent,sids in [('sos-previous-elections',['sos-2024-canvass','sos-2022-canvass','sos-2020-canvass']),
      ('county-douglas-results-archive',[f'county-douglas-{y}-{kind}'for y in [2024,2022,2020]for kind in ['native-xls','summary-pdf']]),
      ('sos-2026-election-parent',['sos-final-general-candidate-pdf']),
      ('sos-2026-general-certification-notice-parent',['sos-2026-general-certification-notice-pdf'])]:
        t=original(parent).decode('utf-8-sig');hrefs=[html.unescape(h)for h in re.findall(r'href\s*=\s*[\'\"]([^\'\"]+)',t,re.I)]
        urls={urllib.parse.urljoin(SOURCES[parent]['url'],h):h for h in hrefs}
        for sid in sids:
            url=SOURCES[sid]['url'];assert url in urls,(parent,sid,url)
            chains.append({'parent_source_id':parent,'literal_href':urls[url],'resolved_url':url,'child_source_id':sid})
    # Archive CDX returned each exact original URL/timestamp; preserve all records,
    # original county navigation and actual archive URLs in the source receipts.
    for r in LEDGER:
        if r.get('archive_record')and r.get('status')==200:
            chains.append({'discovery_source_id':'county-lancaster-observed-final-pdf-cdx'if r['id'].startswith('county-lancaster-2024-final')else 'sos-2024-observed-native-special-pages-cdx',
              'child_source_id':r['id'],'archive_record':r['archive_record'],'requested_archive_url':r['url'],
              'qualification':'Exact returned CDX original/timestamp. Archive original capture clocks are separate from retrieval and result update clocks.'})
    index={'scope':'Immutable individual original references; frozen shared233row ledger snapshot is provenance, mutable coordinator ledger is not an input.',
      'shared_entity_references':shared,'shared_transport_errors_without_entity':errors,'fresh_own_receipts':own,'verified_primary_parent_links':chains,
      'source_gaps':['Seven SOS-hosted county PDFs were recovered through actual primary indexed URLs; a separate complete original historical portal parent is not retained for each PDF. Discovery_basis and primary domain/status remain explicit.',
        'Lancaster direct403 and archived state-app1MiB partials remain separate from complete1431p county original. No repaired failure receipt.',
        'Missing redirect/source timezone/registration status information is unavailable, not inferred.'],
      'reconstruction':'gzip.decompress retains original ordered entity bytes; no split/truncation/simplification is performed by this worker.'}
    jwrite(OUT/'source/source-index.json',index)
    files=[ROOT/'turnout.md',ROOT/'data/county-turnout.csv']+[p for p in OUT.rglob('*')if p.is_file()and p.name not in ['asset-manifest.json','validation.json']and '__pycache__'not in p.parts]
    assert all(p.stat().st_size<40_000_000 for p in files)
    manifest={'schema_version':'NE-turnout-assets-v1','hash_algorithm':'SHA256','owned_artifacts':[pin(p)for p in sorted(set(files))],
      'shared_original_references':[r['original_reference']|{'raw_bytes':r['raw_bytes'],'raw_sha256':r['raw_sha256'],'source_id':r['receipt']['id']}for r in shared],
      'peer_primary_original_references':json.loads((OUT/'source/peer-primary-original-references.json').read_text()),
      'excluded_self_referential_outputs':['data/turnout/asset-manifest.json','data/turnout/validation.json'],
      'qualification':'Manifest and validation are excluded from owned_artifact hash list to avoid cycles; validator pins manifest separately. No dependency/cache directory retained.'}
    jwrite(OUT/'asset-manifest.json',manifest);print('owned artifacts',len(files),'shared original entities',len(shared),'transport errors',len(errors),'verified parent/archive links',len(chains))
if __name__=='__main__':main()
