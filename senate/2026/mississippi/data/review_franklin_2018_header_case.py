"""Correct a coordinator case transcription while retaining its prior witness."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/franklin-2018-header-case-correction'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 prior=DATA/'coordinator-franklin-2018-original-native-review.json';assert pin(prior)['sha256']=='c39e7ccc9f4e4a2b8c3be7df4768cf3b6e1560c8cd3492dec58c1a8a0c7dde19';a=json.loads(prior.read_bytes());QA.mkdir(exist_ok=True);findings=[]
 for sid,top,left in [('sos-2018-county-franklin',165,1095),('sos-2018-runoff-county-franklin',155,1090)]:
  r=next(r for r in a['original_findings']if r['source_id']==sid);assert r['literal_headers'][8]=='McCall';original=DATA/f'coordinator-qa/franklin-2018-original-native/{sid}-p2.png';crop=QA/(sid+'-physical9-upright.png')
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)/'crop.png';subprocess.run(['sips','--cropToHeightWidth','180','75','--cropOffset',str(top),str(left),str(original),'--out',str(p)],check=True,stdout=subprocess.DEVNULL);subprocess.run(['sips','--rotate','90',str(p),'--out',str(p)],check=True,stdout=subprocess.DEVNULL);body=p.read_bytes()
  if crop.exists():assert crop.read_bytes()==body
  else:crop.write_bytes(body)
  findings.append(dict(source_id=sid,raw_PDF_sha256=r['raw_PDF_sha256'],actual_PDFpage=2,physical_column=9,full_original_coordinator_render=pin(original),pixel_crop=dict(top=top,left=left,height=180,width=75),rotation_clockwise_degrees=90,resize_or_enhancement='none',upright_original_crop=pin(crop),earlier_coordinator_header='McCall',direct_upright_original_header='Mccall',source_counts_changed=False))
 out=dict(status='original_header_case_correction_Mccall_both_Franklin2018_stages',prior_immutable_coordinator_witness=pin(prior),findings=findings,qualification='The earlier coordinator full-page transcription used McCall. Unchanged-pixel upright crops visibly show Mccall, lower-case second c, in each exact original. The prior witness remains intact with this explicit correction; all candidate vectors, source/raw/render hashes and physical positions remain unchanged. This is not case-fold normalization, a source publication change, cross-stage/current identity or dispatch approval.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-franklin-2018-header-case-correction.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
