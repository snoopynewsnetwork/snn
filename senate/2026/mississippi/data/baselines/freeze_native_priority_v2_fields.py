"""Immutable companion evidence for the unchangedv2 complete-field proposal."""
import gzip,json
from sources import OUT,BASE,sha,save
FILES=['source/native-priority-v2/snapshot.json','native-priority-v2-validation.json','native-priority-v2-independent-validation.json','canvass-readings.json','canvass-statistics-readings.json','canvass-validation.json','union-native-profile-readings.json','union-native-profile-fields.csv','pike-native-profile-readings.json','pike-native-profile-fields.csv','supplemental-2024-summary-readings.json','union-split-ballot-style-readings.json','union-split-ballot-style-fields.csv','source/2024-lincoln-independent-controls.json','source/2024-montgomery-independent-controls.json','native-2018-peer-41views-v3-reconciliation.json','native-2020-peer-41views-v3-reconciliation.json']
def main():
 folder=OUT/'source/native-priority-v2-field-evidence-v1';folder.mkdir(exist_ok=True);pins=[]
 for name in FILES:
  p=OUT/name;r=p.read_bytes();z=gzip.compress(r,mtime=0);t=folder/(name.replace('/','--')+'.gz');assert len(z)<40000000
  if t.exists():assert t.read_bytes()==z,'Evidence revision requires a new immutable version'
  else:t.write_bytes(z)
  pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(r),original_sha256=sha(r),stored_path=str(t.relative_to(BASE)),stored_bytes=len(z),stored_sha256=sha(z)))
 d=dict(status='complete_source_field_companion_not_external_acceptance',proposal='data/baselines/source/native-priority-v2/snapshot.json',pins=pins,qualification='Exact derivative field/source/peer bodies accompanying unchangedv2 named-field887proposal. Whole originalbytes/page rasters reused by embedded original hashes and mainassetmanifest, no huge raw duplication. Complete located required panels; unprinted fields/source differences remain explicit. Neither companion norproposal self-approves current2026 ordispatch.')
 sp=folder/'snapshot.json'
 if sp.exists():assert json.loads(sp.read_text())==d
 else:save(sp,d)
 print('PASSv2fieldcompanion',len(pins),'immutablepins')
if __name__=='__main__':main()
