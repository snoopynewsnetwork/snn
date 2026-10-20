"""Write final seal FIRST, whole owned manifest LAST; no digest cycles."""
import json
from replay import HERE,STATE,digest,loads
from validate import owned
def main():
    proof=loads((HERE/'validation.json').read_bytes());assert proof['status']=='pass'
    seal={'status':'bounded research sealed; coordinator acceptance pending','authority_path_only':'data/coordinator-priority-acceptance.json','scope':proof['scope'],'graph_counts':proof['graph'],'original_counts':proof['originals'],'negative_count':proof['negative']['negative_count'],'offline_outputs':proof['offline_output_count'],'current_matches':None,'all_current_legal_geography_reporting_November_cadence_pool_collector_forecast_calibration_approvals':False,'final_step':'read-only validate.py --sealed; no owned writes after pass'}
    (HERE/'final-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
    mf=HERE/'asset-manifest.json';assets=[]
    for path in owned():
        if path==mf:continue
        b=path.read_bytes();assert len(b)<40000000;assets.append({'path':path.relative_to(STATE).as_posix(),'bytes':len(b),'sha256':digest(b)})
    mf.write_text(json.dumps({'schema':'arkansas-question3-complete-owned-manifest-v1','only_exclusion':'data/results-sources/asset-manifest.json','assets':assets},indent=2)+'\n')
    print(json.dumps({'manifest_assets':len(assets),'seal_before_manifest':True}))
if __name__=='__main__':main()
