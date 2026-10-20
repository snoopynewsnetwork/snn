"""Self-only owned seal; no reverse manifest cycle or external authority pin."""
from acquire import *
ROOT=BASE.parent

def entry(p):
 b=p.read_bytes();assert len(b)<40000000;return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}
def paths():return sorted([ROOT/'precinct-maps.md']+[p for p in BASE.rglob('*') if p.is_file()],key=lambda p:str(p))
def main():
 validation=json.loads((BASE/'qa/validation.json').read_bytes());repro=json.loads((BASE/'qa/reproduction.json').read_bytes());assert validation['status']==repro['status']=='pass'
 critical=['qa/validation.json','qa/reproduction.json','qa/historical-reconstruction.json','qa/negative-fixtures.json','qa/atlas-js-tests.json','qa/census-vtd-audit.json','qa/state-election-service-native-contract.json','qa/burlington-election-service-native-contract.json','qa/visual-review.json','inventory.json','parents.json','atlas-data.js','historical-contract.json.gz','original-dependencies.json.gz']
 out={'schema':'NJmaps-bounded-original-source-seal-v1','status':'bounded_owned_research_complete_external_current_legal_qualifications_remain','authority_path':'data/coordinator-priority-acceptance.json','owned_paths':['precinct-maps.md','maps/**'],'critical_products':[entry(BASE/f) for f in critical],'observations':575,'priority':233,'remainder':342,'county_parents':21,'source_inventory_complete':True,'current_legal_or_physical_leaf_crosswalk_approved':False,'current_choice_reporting_IDs_approved':False,'genuineNovember_returns_admitted':False,'measured_cadence_exact_outstanding_pool_approved':False,'collector_forecast_probability_approved':False,'browser_test_claimed':False,'optional_coordinator_proof_dependency':False,'external_source_exhaustion_is_owned_completion_gate':False,'manifest_reverse_pin':False,'manifest_excludes_only_itself':True}
 write(BASE/'final-seal.json',out)
 files=[entry(p) for p in paths() if p!=BASE/'asset-manifest.json'];write(BASE/'asset-manifest.json',{'schema':'NJmaps-exact-owned-byte-manifest-v1','only_exclusion':'maps/asset-manifest.json','files':files,'file_count_excluding_self':len(files),'includes_validation_reproduction_and_finalseal':True});print({'sealed_files_excluding_only_manifest':len(files)})
if __name__=='__main__':main()
