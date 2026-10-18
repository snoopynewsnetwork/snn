#!/usr/bin/env python3
"""Coordinator independent complete bytes/inventory and primary scope review."""
import collections,csv,datetime,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
R=ROOT/'data/results-sources'
def sha(b):return hashlib.sha256(b).hexdigest()
def j(p):return json.loads(p.read_text())
def main():
 manifest=j(R/'artifact-manifest.json');assert manifest['asset_count']==1607
 for a in manifest['assets']:
  b=(R/a['path']).read_bytes();assert len(b)==a['bytes']<40000000 and sha(b)==a['sha256'],a['path']
 acquisitions=j(R/'acquisition.json');assert len(acquisitions)==len({a['id'] for a in acquisitions})==422
 bodies=0;status=collections.Counter()
 for a in acquisitions:
  status[str(a.get('status','transport'))]+=1
  if not a.get('body_path'):assert a.get('error');continue
  z=(R/a['body_path']).read_bytes();b=gzip.decompress(z)
  assert len(z)==a['stored_bytes'] and sha(z)==a['stored_sha256'] and len(b)==a['original_bytes'] and sha(b)==a['original_sha256']
  assert a['requested_url']==a['url'] and a['retrieved_at_utc'] and isinstance(a['headers'],dict) and isinstance(a['redirects'],list);bodies+=1
 contract=j(ROOT/'data/turnout/priority-set.json');keys=contract['ordered_priority_keys'];allkeys=contract['full_all_unit_order']
 inv=j(R/'county-inventory.json');rows=list(csv.DictReader((ROOT/'data/official-results-sources.csv').open()));counties=rows[1:]
 assert len(inv)==len(counties)==105 and rows[0]['row_type']=='state'
 assert [c['county_key'] for c in inv]==[c['county_key'] for c in counties]==allkeys
 assert [c['county_key'] for c in counties if c['priority_rank']]==keys
 assert all(not c['november_election_id'] and not c['november_contest_id'] and not c['outstanding_valid_senate_votes'] for c in counties)
 manual=j(R/'manual-visual-checks.json')['checks'];franklin=next(x for x in manual if x['source_id']=='franklin-primary')
 assert list(franklin['visual_named_vector'].values())==[77,31,51,103,98,86,36,165,36,279,427,3051,713]
 assert sum(franklin['visual_named_vector'].values())==5153 and sum(x['county_minus_state'] for x in franklin['comparisons'].values())==-52
 riley=j(R/'riley-2024-source-reconciliation.json');assert riley['county_summary_named_total']==23920 and sum(riley['county_minus_state'].values())==-393
 admin=j(R/'administrative-observations.json');assert admin['source_update_or_asof_clock'] is None and [r.get('value') for r in admin['literal_fields'][:2]]==[18293,107]
 assert sha((R/'extracts/sedgwick-dashboard-image.png').read_bytes())==admin['original_sha256']
 audit=j(R/'historical-native-audit.json')
 source_scope=j(R/'native-source-scopes.json');assert source_scope['ordered_priority_keys']==keys and source_scope['full_all_county_order']==allkeys
 reviewed=['data/results-sources/extracts/sedgwick-dashboard-image.png','data/results-sources/extracts/franklin-primary-page1.png','data/results-sources/extracts/franklin-primary-page2.png','maps/previews/pdf-contact-00.jpg','maps/previews/pdf-contact-06.jpg']
 evidence=[dict(path=p,bytes=(ROOT/p).stat().st_size,sha256=sha((ROOT/p).read_bytes())) for p in reviewed]
 result=dict(status='pass_with_documented_source_gaps',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_assets=1607,acquisition_requests=422,complete_entities=bodies,http_statuses=dict(status),counties=105,priority_counties=23,native_historical_identities=22031,current_november_count_endpoint_approved=False,current_geographic_crosswalk_approved=False,exact_remaining_senate_votes_available=False,visual_evidence=evidence,visual_findings=['Franklin original visibly OFFICIAL RESULTS: all13 candidate cells visually checked,5153vs5205; no state vector changed.','Sedgwick actual dashboard:18293sent/107returned and future voting-start labels; no printed count asof; no remaining-vote subtraction.','Original map contact sheets show precinct maps,parts,2018Cowley,2025/2026Leavenworth and wrong-scope Pottawatomie legislative reference; labels agree with qualified coverage.'],previous_primary_visual_review=['coordinator-evidence/court-preview-inventory.json','coordinator-riley-primary-review.json'],official_artifact_manifest_sha256=sha((R/'artifact-manifest.json').read_bytes()))
 out=ROOT/'data/coordinator-results-review.json'
 if out.exists():
  old=j(out)
  if {k:v for k,v in old.items() if k!='checked_utc'}=={k:v for k,v in result.items() if k!='checked_utc'}:result['checked_utc']=old['checked_utc']
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
