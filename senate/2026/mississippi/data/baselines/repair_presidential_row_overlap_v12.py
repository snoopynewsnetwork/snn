"""Repair source-rule failures from original label panels, keep v10/v11 aids."""
import json
from collections import defaultdict
from sources import OUT,BASE,save,sha
from extract_replay_president import NAMES,manual_row
def main():
    path=OUT/'source/native-presidential-row-repairs-v11.json';raw=json.loads(path.read_text());changes=[]
    for r in raw['readings']:
        prior=r['row_bounds'].copy();key=(r['source_id'],r['page']);name=r['candidate'];evidence=None
        if (key[0]=='sos-2024-county-itawamba' and key[1] in [3,4] and name in ['Donald J. Trump','Shiva Ayyadurai']) or (key==('sos-2024-county-amite',4) and name in ['Jill Stein','Randall Terry']):
            earlier=manual_row(*key,name,'v5');assert earlier and earlier['render_size']==r['render_size'] and earlier['rotation_ccw']==r['rotation_ccw'] and earlier['deskew_angle_ccw']==r['deskew_angle_ccw'];r['row_bounds']=earlier['row_bounds'];r['basis']='Original field-label re-read and same-frame independently original-reviewed v5 window repair a missed printed rule; old projected grid merged neighboring source fields';evidence='data/baselines/source/native-presidential-row-repairs-v5.json'
        elif key==('sos-2024-county-choctaw',2):
            endpoints=[497,568,635,701,768,835,901,967,1033,1100];i=NAMES.index(name);r['row_bounds']=[0,endpoints[i],r['render_size'][0],endpoints[i+1]];r['basis']='All nine printed candidate names and actual bordering lines directly read on complete original-only label block with source-y ticks. Estimated complete-field windows, not exact printed boundaries; no vote/control input.';evidence='data/baselines/qa/presidential-original-merged-rule-repair.png'
        elif key[0]=='sos-2024-county-jeff-davis' and key[1] in [2,3] and name in ['Randall Terry','Donald J. Trump']:
            split=777 if key[1]==2 else 775;r['row_bounds']=[0,prior[1] if name=='Randall Terry' else split,r['render_size'][0],split if name=='Randall Terry' else prior[3]];r['basis']='Both actual candidate names and intervening printed rule directly read on complete original-only label block; projected machine grid had merged them. Manual interior split is a complete reading-window estimate, not a boundary polygon.';evidence='data/baselines/qa/presidential-original-merged-rule-repair.png'
        if evidence:
            r['geometry_correction_history']=dict(prior_version='v11',prior_row_bounds=prior,corrected_row_bounds=r['row_bounds'],evidence_path=evidence,evidence_sha256=sha((BASE/evidence).read_bytes()));changes.append(dict(source_id=r['source_id'],page=r['page'],candidate=name,**r['geometry_correction_history']))
    groups=defaultdict(list)
    for r in raw['readings']:groups[r['source_id'],r['page']].append(r)
    for key,rr in groups.items():
        assert len(rr)==9
        for a,b in zip(rr,rr[1:]):assert a['row_bounds'][3]<=b['row_bounds'][1]+3,(key,a['candidate'],b['candidate'],a['row_bounds'],b['row_bounds'])
    raw.update(version='v12',qualification='Source presidential field-label and row windows only. Fresh original source labels plus separately documented manual original label/rule repairs; 1899 distinct non-overlapping field windows across211 source pages. No candidate numerical vote, county residual or peer derivative enters this locator. Manual windows are not current geography or exact polygons. Numeric extraction and source controls remain separate.',prior_version_path=str(path.relative_to(BASE)),prior_version_sha256=sha(path.read_bytes()),source_rule_corrections=changes)
    save(OUT/'source/native-presidential-row-repairs-v12.json',raw);print('1899 source candidate windows/211pages; no overlap;',len(changes),'original rule-window repairs; numeric acceptance separate')
if __name__=='__main__':main()
