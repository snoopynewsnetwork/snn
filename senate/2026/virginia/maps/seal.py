"""Seal once, manifest last. No reverse manifest digest or self-approval."""
import json
from acquire import HERE,sha

def pin(path):
    b=path.read_bytes();assert len(b)<40000000
    return {'path':str(path.relative_to(HERE.parent)),'bytes':len(b),'sha256':sha(b)}

if __name__=='__main__':
    assert not (HERE/'final-seal.json').exists(),'already sealed'
    checks=['authority-replay.json','original-reconstruction.json','acquisition-audit.json','binary-audit.json','pdf-audit.json','negative-fixtures.json','validation.json']
    for name in checks:
        v=json.loads((HERE/name).read_bytes())
        if 'status' in v:assert v['status']=='pass'
    seal={'schema':'VA-maps-immutable-worker-handoff-v1','status':'bounded_research_complete_for_external_coordinator_review','owned_scope':['precinct-maps.md','maps/**'],'authority_path':'data/coordinator-priority-acceptance.json','authority_body_or_hash_stored':False,'proofs':[pin(HERE/n) for n in checks],'all_parents':133,'priority_parent_chains':108,'priority_source_objects':1538,'all_source_objects':2669,'remainder_source_objects':1131,'official_state_ZIPs':133,'official_state_PDFs':133,'Census2020_VTD_ZIPs':1,'all_actual_native_ZIPs':134,'all_PDF_pages_automatically_rendered':912,'actually_manually_viewed_whole_pages':10,'approved_leaf_joins':0,'current_geography_approved':False,'legal_or_eligible_writein_approval':False,'November_choice_reporting_feed_approval':False,'cadence_outstanding_collector_probability_approval':False,'external_qualifications':'Source update lag, mixed vintage, unknown adoption/effective/current physical identity, virtual/unmapped units, bounded local access gaps; none reopens completed bounded research.','coordinator_acceptance':None,'coordinator_publication':None,'final_sequence':['seal written first','complete owned manifest written last; exclude only itself','run replay_authority.py --check','run audit_originals.py --check','run audit_acquisition.py --check','run validate.py --sealed; exact membership/hash/original/geometry/DOM/link reconstruction','no owned writes after all final checks pass'],'manifest_digest_in_seal':None}
    (HERE/'final-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
    paths=sorted([p for p in HERE.rglob('*') if p.is_file() and p!=HERE/'asset-manifest.json']+[HERE.parent/'precinct-maps.md'])
    rows=[pin(p) for p in paths]
    (HERE/'asset-manifest.json').write_text(json.dumps({'schema':'VA-maps-complete-owned-manifest-v1','excludes_only':'maps/asset-manifest.json','files':rows},indent=2)+'\n')
    print(json.dumps({'sealed_targets':len(rows),'bytes':sum(r['bytes'] for r in rows),'largest_stored_file':max(r['bytes'] for r in rows),'manifest_written_last':True}))
