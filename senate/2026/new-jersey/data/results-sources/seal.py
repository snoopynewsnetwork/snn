"""Final seal then exact manifest membership; manifest excludes only itself, no reverse cycle."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def pin(p):
 b=p.read_bytes();assert len(b)<40000000;return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
 validation=json.loads((P/'validation.json').read_bytes());assert validation['status']=='pass_complete_owned_source_research'
 repro=json.loads((P/'reproduction.json').read_bytes());assert repro['status']=='pass_independent_owned_offline_reproduction'
 core=[P/n for n in ['historical-reconstruction.json','original-page-replay.json','validation.json','reproduction.json','all575-investigations.json.gz','priority233-investigations.json.gz','remainder342-investigations.json.gz','full21-hierarchy.json.gz','authorities.json','request-index.json','structure-index.json','complete-dom-index.json','payload-assessments.json']]
 seal={'status':'complete_bounded_original_official_source_research','authority_path':'data/coordinator-priority-acceptance.json','stable_core':[pin(p) for p in core],'source_scope':{'all':575,'priority':233,'remainder':342,'county_parents':21},'current_reporting_choice_leaf_or_geography_approved':False,'genuine_November_counts_admitted':False,'eligible_writein_exhaustiveness_approved':False,'exhaustive_later_law_order_ballot_coverage_claimed':False,'measured_cadence_or_exact_remaining_approved':False,'collector_or_probability_approved':False,'coordinator_acceptance_or_publication_claimed':False,'bounded_research_completed_without_future_external_gate':True,'manifest_cycle_policy':'manifest includes this seal; seal does not hash manifest'}
 (P/'final-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
 files=[ROOT/'official-results.md',ROOT/'data/official-results-sources.csv']+[p for p in P.rglob('*') if p.is_file() and p.name!='asset-manifest.json'];manifest={'excludes_only':'data/results-sources/asset-manifest.json','files':[pin(p) for p in sorted(files)]};(P/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('sealed',len(files),'listedfiles;max',max(r['bytes'] for r in manifest['files']))
if __name__=='__main__':main()
