#!/usr/bin/env python3
"""Independent original-cell and source-coverage integration; no worker code imported."""
from pathlib import Path
import collections
import contextlib
import csv
import datetime
import gzip
import hashlib
import html
import io
import json
import re
import runpy
import subprocess

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'
S=D/'results-sources'
load=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 mf_bytes=(S/'asset-manifest.json').read_bytes();mf=json.loads(mf_bytes)
 assert len(mf['owned_assets'])==2994 and len(mf['read_only_references'])==360
 for r in mf['owned_assets']+mf['read_only_references']:
  b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes']<40000000 and sha(b)==r['sha256'],r['path']
 # Reuse the coordinator's separately authored original BIFF/OOXML/PDF parser,
 # freshly rereading every original cell before comparing the official package.
 with contextlib.redirect_stdout(io.StringIO()):ns=runpy.run_path(str(D/'review_priority.py'),run_name='coordinator_originals')
 records=ns['records'];books=ns['books'];pages=ns['pdf_pages']
 rows=[json.loads(x)for x in gzip.decompress((S/'historical-native-records.jsonl.gz').read_bytes()).decode().splitlines()]
 assert len(rows)==7360
 seen=set();fields=0;types=0;full_rows=0
 for r in rows:
  key=(r['source_id'],r['source_roster_position_zero_based']);assert key not in seen;seen.add(key)
  original=records[key[0]][key[1]]
  for k in ['county','native_label','raw_fields','fields','source_locator']:
   assert r[k]==original[k],(key,k)
  assert r['source_native_id']is None
  pos=r['original_position']
  if 'sheet'in pos:
   book=books[key[0]]
   if isinstance(book,dict):
    actual=book[pos['sheet']][pos['source_row']]
    assert actual[:len(pos['values'])]==pos['values']
    assert all(v==''for v in actual[len(pos['values']):])
   else:
    sheet=book.sheet_by_name(pos['sheet']);assert sheet.row_values(pos['source_row']-1)==pos['values']
    assert list(sheet.row_types(pos['source_row']-1))==pos['types'];types+=len(pos['types'])
   full_rows+=1
  else:
   actual=pages[key[0]][pos['page']-1].splitlines()[pos['line']-1]
   assert actual==pos['text']
  fields+=len(r['fields'])
 assert len(seen)==7360 and fields==34880
 receipts={}
 for p in (S/'source').glob('*.json'):
  r=load(p)
  if isinstance(r,dict)and 'source_id'in r and 'body_path'in r:
   receipts[r['source_id']]=r
 assert len(receipts)==705
 entities={};statuses=collections.Counter()
 for id,r in receipts.items():
  b=(S/r['body_path']).read_bytes();assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256']
  b=gzip.decompress(b);assert len(b)==r['original_bytes'] and sha(b)==r['original_sha256']
  assert sha((S/r['headers_path']).read_bytes())==r['headers_sha256']
  assert r['requested_url'] and r['retrieved_utc'] and r['finished_utc']
  statuses[str(r['http_status'])]+=1
  entities[id]=gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b
 inventory=list(csv.DictReader((D/'official-results-sources.csv').open()))
 assert len(inventory)==321 and inventory[0]['record_type']=='state_authority'
 contract=load(D/'turnout/priority-set.json');native=inventory[1:]
 assert [r['source_geography_key']for r in native]==contract['full_ordered_keys']
 assert sum(r['priority']=='true'for r in native)==143
 assert all(not r[k]for r in native for k in ['current_election_id','current_numeric_native_id','current_senate_contest_id','verified_live_cadence_seconds','exact_remaining_votes'])
 investigations=load(S/'priority-investigations.json')
 assert [r['source_geography_key']for r in investigations]==contract['ordered_priority_keys']
 basis={r['source_roster_position_zero_based']:r for r in rows if r['source_id']=='sos-2024-president-archived-original'}
 for r in investigations:
  x=r['native_source_record'];assert x==basis[x['source_roster_position_zero_based']]
 parents=load(S/'municipal-inspections.json');assert len(parents)==98
 assert len({r['municipality']for r in parents})==98
 captured=0
 for r in parents:
  channel=r['selected_current_channel']
  if channel:
   id=channel['source_id'];assert receipts[id]['http_status']==200 and channel['url']==receipts[id]['final_url'];captured+=1
 assert captured==79
 assert len(load(S/'inventory-coverage.json')['direct_current_access_gaps'])==19
 def text(id):
  b=entities[id]
  if b.startswith(b'%PDF-'):
   return subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True).stdout.decode()
  return ' '.join(html.unescape(re.sub('<[^>]+>',' ',b.decode(errors='replace'))).split())
 samples=load(S/'sample-audits.json');port=samples[0];pt=text(port['source_id'])
 for r in port['raw_positions']:assert r['text']in pt
 for values in port['fields'].values():assert sum(values[:5])==values[5]
 assert port['candidate_field_checks']==20
 # Read the current primary statute text, preserving exceptions and request scope.
 ordinary=text('rsa-657-chapter');recount=text('rsa-660-chapter');cert=text('rsa-659-chapter')
 assert 'after 5:00 p.m. on election day except as provided in RSA 657:21-a, V and RSA 659:20-a'in ordinary
 assert 'less than 20 percent of the total ballots cast'in recount and 'no later than the Friday following the election'in recount
 assert 'The governor shall issue certificates of election'in cert and 'United States senator'in cert
 # Fresh primary PDF text, independently read pages in the separate court-scope review.
 appendix=entities['court-scotus-appendix'];ap=' '.join(subprocess.run(['pdftotext','-f','67','-l','75','-layout','-','-'],input=appendix,capture_output=True,check=True).stdout.decode().split())
 assert 'student identification cards are no longer expressly valid'in ap
 assert 'Entered: October 14, 2026'in ap and 'The motion is denied'in ap
 docket=text('court-scotus-docket');assert '11 a.m. (EDT) on October 19, 2026'in docket
 hours=load(S/'poll-hours-evidence.json');assert hours['utc_offset_seconds']==-18000
 assert {r['closing_local']for r in hours['local_hours']}=={'19:00','20:00'}
 for r in hours['local_hours']:
  local=datetime.datetime.fromisoformat('2026-11-03T'+r['closing_local']).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
  assert local.astimezone(datetime.timezone.utc).isoformat()==r['closing_utc']
 assert (S/'asset-manifest.json').read_bytes()==mf_bytes
 out={'status':'pass_with_explicit_source_access_and_operational_gaps','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'independence':'Fresh coordinator original BIFF/OOXML/PDF parser; direct full source rows/types, every retained response hash, exact-key authority coverage and primary PDF/statute checks; imports no worker code.',
      'owned_asset_hashes':2994,'read_only_reference_hashes':360,'source_scoped_native_records':7360,'original_fields':fields,
      'full_workbook_rows_compared':full_rows,'original_biff_cell_types_compared':types,
      'http_receipts':705,'http_status_counts':dict(statuses),'native_leaves':320,'exact_priority_investigations':143,'priority_parent_inspections':98,
      'current_primary_municipal_channels':79,'direct_municipal_access_gaps':19,'november_feed_or_id_admissions':0,
      'portsmouth_ward_candidate_controls':20,'poll_hour_examples':len(hours['local_hours']),
      'legal_scope':'Primary5pmordinaryabsentee exception text, candidate-request recount threshold/deadline and governor certificate scope independently checked; narrow student-ID court chronology preserved, future SupremeCourt action unverified.',
      'official_manifest_sha256':sha(mf_bytes),'official_report_sha256':sha((ROOT/'official-results.md').read_bytes()),
      'scope':'Source research/integrity only; no current legal geography, clerical delegation, live-feed cadence, exact outstanding-vote count, collector or calibrated probability approval.'}
 p=D/'coordinator-results-review.json'
 if p.exists():
  prev=load(p)
  if {k:v for k,v in prev.items()if k!='reviewed_utc'}=={k:v for k,v in out.items()if k!='reviewed_utc'}:out['reviewed_utc']=prev['reviewed_utc']
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
