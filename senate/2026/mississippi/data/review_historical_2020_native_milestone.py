"""Validate immutable source-bound2020 native witnesses without new geography joins."""
from pathlib import Path
import argparse,collections,csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent;ROOT=DATA.parent
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--version',required=True);ap.add_argument('--sha256',required=True);args=ap.parse_args()
 path=DATA/'baselines/source'/f'native-2020-{args.version}'/'snapshot.json';raw=path.read_bytes();assert sha(raw)==args.sha256;snap=json.loads(raw);items={}
 for p in snap['pins']:
  stored=(ROOT/p['stored_path']).read_bytes();assert len(stored)==p['stored_bytes']and sha(stored)==p['stored_sha256'];b=gzip.decompress(stored);assert len(b)==p['original_bytes']and sha(b)==p['original_sha256'];items[Path(p['original_path']).name]=b
 coverage=json.loads(items['native-2020-coverage.json']);assert coverage['counts']==snap['counts']
 ss={}
 for name in ['coahoma-2020-amendment-readings.json','native-2020-additional-readings.json']:
  for s in json.loads(items[name])['sources']:assert s['source_id']not in ss;ss[s['source_id']]=s
 refs={r['id']:r for r in json.loads((DATA/'baselines/source/references.json').read_bytes())};totalsledger=json.loads(gzip.decompress((DATA/'coordinator-qa/county-2020-publication-controls.json.gz').read_bytes()));old={r['source_id']:r for r in totalsledger['readings']}
 assert len(old)==104;allstatus=coverage['all104_publication_status'];assert len(allstatus)==104 and {r['source_id']for r in allstatus}==set(old)
 assert sum(r['selected_for_82_county_amended_where_explicit_control']for r in allstatus)==82
 counts=collections.Counter();findings=[];rasterpins={};allfields={}
 for sid,s in ss.items():
  ref=refs[sid];b=(ROOT/ref['path']).read_bytes();assert sha(b)==ref['stored_sha256'];original=gzip.decompress(b);assert sha(original)==s['raw_sha256']==old[sid]['raw_sha256'];assert original.startswith(b'%PDF-')
  sums={n:0 for n in NAMES};totals={};c=collections.Counter();bounds_status=[];administrative_values={}
  for p in s['pages']:
   assert [f['candidate']for f in p['fields']]==NAMES
   rp=p.get('full_original_render_path',p.get('evidence_path'));rh=p.get('render_sha256',p.get('evidence_sha256'))
   if sid.startswith('sos-2020-county-coahoma')and rp.startswith('qa/'):rp='data/baselines/'+rp
   assert pin(ROOT/rp)['sha256']==rh;rasterpins[rp]=pin(ROOT/rp)
   if p.get('row_window_status')is not None:bounds_status.append(dict(actual_PDFpage=p['page'],status=p['row_window_status']))
   for col in p['columns']:
    role=col['role'];assert role in ['source_native_reporting_constituent','source_TOTAL','unused_template_column','source_administrative_reporting_column'];c[{'source_native_reporting_constituent':'native_constituents','source_TOTAL':'TOTAL_columns','unused_template_column':'unused_columns','source_administrative_reporting_column':'administrative_columns'}[role]]+=1
    if role=='source_administrative_reporting_column':assert sid=='sos-2020-county-harrison'and p['page']==4 and col['source_column']==4 and col['label_literal']=='Invalid Addresses\n9999'and col['literal_printed_id']=='9999'
   for f in p['fields']:
    assert len(f['values'])==len(p['columns'])
    for col,v in zip(p['columns'],f['values']):
     key=(sid,p['page'],col['source_column'],f['candidate']);assert key not in allfields;allfields[key]=(col,v,rp,rh)
     if col['role']=='unused_template_column':assert v is None;c['unused_null_positions']+=1
     else:
      assert type(v)is int and v>=0;c['numeric_positions']+=1
      if col['role']=='source_native_reporting_constituent':sums[f['candidate']]+=v
      elif col['role']=='source_administrative_reporting_column':assert v==0;administrative_values[f['candidate']]=v
      else:assert f['candidate']not in totals;totals[f['candidate']]=v
  assert sums==totals==old[sid]['candidate_values']
  rec=next(r for r in coverage['reviewed_sources']if r['source_id']==sid);assert rec['candidate_sums']==sums
  assert all(rec[k]==v for k,v in c.items());counts.update(c)
  finding=dict(source_id=sid,raw_sha256=s['raw_sha256'],actual_PDFpages=[p['page']for p in s['pages']],counts=dict(c),source_candidate_sums_and_printed_TOTALs=sums,row_window_statuses=bounds_status)
  if administrative_values:finding['separate_administrative_candidate_values']=administrative_values
  findings.append(finding)
 flat=list(csv.DictReader(io.StringIO(items['native-2020-additional-candidate-votes.csv'].decode())))
 for r in flat:
  col,v,rp,rh=allfields[(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate'])]
  assert (None if r['votes']==''else int(r['votes']))==v
  assert r['role']==col['role']and r['literal_native_label']==col['label_literal']
  assert r['source_raw_sha256']==ss[r['source_id']]['raw_sha256']and r['full_original_render_path']==rp and r['render_sha256']==rh
 assert len(flat)==sum(1 for key in allfields if not key[0].startswith('sos-2020-county-coahoma'))
 counts['reviewed_source_publications']=len(ss);counts['total_source_publications']=104
 selected=[r for r in allstatus if r['selected_for_82_county_amended_where_explicit_control']and r['source_id']in ss]
 counts['reviewed_selected82_publications']=len(selected);counts['selected82_reviewed_native_constituents']=sum(r['reviewed_native_constituents']for r in selected)
 assert dict(counts)==snap['counts']
 assert {r['source_id']for r in allstatus if r['native_three_candidate_original_review_complete']}==set(ss)
 for r in allstatus:
  if r['source_id']not in ss:assert r['reviewed_native_constituents']is None
 out=dict(status='pass_bounded_immutable2020_native_source_pins_roles_and_original_controls',snapshot_pin=pin(path),lossless_pins=snap['pins'],counts=dict(counts),flat_additional_positions_checked=len(flat),source_findings=findings,complete_original_raster_pins=list(rasterpins.values()),
 qualification='All four lossless snapshot pins, raw PDF originals, complete render evidence and source-position roles/candidate sums match the prior104-publication controls. Alternative publications remain separate, selected82 is explicitly amended-where-linked, not a same-vintage or physical/name/2024/current join. Broad faint-source reading bands and exact-cell windows are distinct, not approved numeric polygons. Unreviewed publication native counts remain null. This source/pin/arithmetic/basis check is not a fresh coordinator visual reading of every new glyph, independent statewide peer completion, historical method completeness or dispatch acceptance.',historical_native_complete=False,formal_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/f'coordinator-historical-native-2020-{args.version}-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable review changed'
 else:p.write_bytes(b)
 print(json.dumps(dict(status=out['status'],counts=dict(counts),output_pin=pin(p))))
if __name__=='__main__':main()
