"""Check producer history without relabelling earlier peer hashes."""
from pathlib import Path
import gzip,hashlib,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/2020-peer-comparison-metadata-history'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def frozen(p,expected):
 q=QA/(p.name+'.gz');QA.mkdir(exist_ok=True)
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();assert sha(b)==expected;q.write_bytes(gzip.compress(b,mtime=0))
 assert sha(b)==expected;return b,pin(q)
def main():
 hp=DATA/'turnout/2020-native-peer-metadata-update-history.json';raw,hcopy=frozen(hp,'0afa1ca1fedef59f8ec54881704ef367b0a550406cd9cda24a981a5c56453371');h=json.loads(raw);allowed=set(h['permitted_metadata_fields']);assert allowed=={'scope','peer_file_sha256','peer_snapshot_sha256','accepted_source_literal_label_differences'}
 proof=DATA/'coordinator-historical-native-2020-peer38v2-review.json';p=json.loads(proof.read_bytes());assert pin(proof)['sha256']=='ff8c31f17ae0fd4b21d035b57c66f89c1151ebac2db0be0e79cbcb65baedff4d';changed={r['peer_original_derivative']:r for r in p['later_metadata_only_JSON_changes']};records=[];seen=set();positions=0;changes=0
 for r in h['records']:
  oldpath=ROOT/r['archive_path'];stored=oldpath.read_bytes();old=gzip.decompress(stored);assert len(stored)==r['archive_stored_bytes']and sha(stored)==r['archive_stored_sha256'];assert len(old)==r['earlier_raw_bytes']and sha(old)==r['earlier_raw_sha256']
  new,newcopy=frozen(ROOT/r['current_path'],r['later_raw_sha256']);assert len(new)==r['later_raw_bytes'];a=json.loads(old);b=json.loads(new);assert a['source_id']==b['source_id']==r['source_id']and r['source_id']not in seen;seen.add(r['source_id'])
  core=lambda d:{k:v for k,v in d.items()if k not in allowed};assert core(a)==core(b);digest=sha(json.dumps(core(a),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode());assert digest==r['unchanged_source_semantics_sha256']
  delta={k:dict(earlier_present=k in a,earlier_value=a.get(k),later_present=k in b,later_value=b.get(k))for k in sorted(a.keys()|b.keys())if a.get(k)!=b.get(k)or(k in a)!=(k in b)};assert delta==r['comparison_metadata_changes']and set(delta)<=allowed;assert len(a['rows'])==len(b['rows'])==r['source_positions'];positions+=len(a['rows'])
  if delta:
   changes+=1;coor=changed[Path(r['current_path']).name];assert coor['previous_original_sha256']==sha(old)and coor['new_frozen_original_sha256']==sha(new)
  records.append(dict(source_id=r['source_id'],earlier_original_copy=pin(oldpath),later_original_copy=newcopy,source_positions=r['source_positions'],metadata_differences=delta,unchanged_source_semantics_sha256=digest))
 assert len(records)==h['archived_reading_count']==39 and changes==h['metadata_changed_count']==17 and positions==h['candidate_or_null_positions']==2343 and h['unchanged_count']==22
 out=dict(status='pass_explicit_later_comparison_metadata_history_without_source_changes',history_original_path=str(hp.relative_to(ROOT)),history_original_bytes=len(raw),history_original_sha256=sha(raw),history_lossless_copy=hcopy,prior_coordinator38_comparison=pin(proof),reading_JSONs=39,later_metadata_changes=17,unchanged_JSONs=22,candidate_or_null_positions=2343,per_source=records,qualification='Earlier source-reading bodies and their original peer-hash declarations survive exactly. Later bodies are separately pinned and differ only in the four explicit peer-comparison fields; all source rows/votes/headers/roles/raw/raster/physical fields remain identical. The history records repeated later comparisons, not a retrospective initial transcription reference. Earlier first7v1 and later38v2 remain immutable. This closes the bounded provenance-accounting repair, not independent whole104 native/method or current-geography/dispatch acceptance.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 target=DATA/'coordinator-2020-peer-metadata-history-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if target.exists():assert target.read_bytes()==b
 else:target.write_bytes(b)
 print(json.dumps(pin(target)))
if __name__=='__main__':main()
