"""Final READ-ONLY full byte/membership/link/coverage/original audit."""
from pathlib import Path
from replay_inputs import R,S,sha,read
from packaging import owned,audit_members
import json,gzip,re,io,collections

def source_audit():
 index=json.loads((R/'acquisition-index.json').read_bytes());keys=[r['key'] for r in index];assert len(set(keys))==len(keys)==235
 assert {p.stem for p in (R/'requests').glob('*.json')}==set(keys)
 assert {p.name.removesuffix('.json.gz') for p in (R/'structures').glob('*.json.gz')}==set(keys)
 entities=0;errors=0;status=collections.Counter();raw_unique=set();body_parts=set()
 for r in index:
  req=json.loads(read(r['request']));struct=json.loads(gzip.decompress(read(r['structure'])));assert req['key']==struct['key']==r['key'];assert struct['source_request']==r['request']['path']
  errors+=bool(req.get('error'))
  objects=[e['body'] for e in req['entities']]
  if 'request_body' in req:objects.append(req['request_body'])
  for b in objects:
   z=b''
   for p in b['parts']:
    part=read(p);assert len(part)<40000000;z+=part;body_parts.add(p['path'])
   assert sha(z)==b['stored_sha256'] and len(z)==b['stored_bytes'];raw=gzip.decompress(z);assert sha(raw)==b['raw_sha256'] and len(raw)==b['raw_bytes'];raw_unique.add((b['raw_sha256'],b['raw_bytes']))
  for e in req['entities']:
   entities+=1;status[e['status']]+=1;assert e['retrieved_utc'] and isinstance(e['headers'],dict) and e['url']
  if not req['entities']:assert req['error'] is not None
  if req['entities']:assert struct['status']==req['entities'][-1]['status']
  if struct['format']=='pdf':assert struct['pdf_final_EOF'] and not struct['extraction_error'].strip() and 'Pages:' in struct['pdfinfo']
 actual_parts={str(x.relative_to(S)) for x in (R/'bodies').glob('*') if x.is_file()};assert actual_parts==body_parts,'no unindexed retained response part'
 return {'status':'pass','requests':len(keys),'complete_received_response_entities':entities,'request_errors':errors,'statuses':{str(k):v for k,v in sorted(status.items())},'distinct_retained_raw_entities_and_request_bodies':len(raw_unique),'individual_stored_body_parts':len(body_parts),'routine_GET_implicit_outgoing_header_gap':True,'current_November_counts_admitted':False}

def link_audit():
 count=0
 for path in [S/'official-results.md',R/'report-body.md',R/'SCHEMA.md']:
  base=S if path.name in ['official-results.md','report-body.md'] else R
  for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
   if target.startswith(('http:','https:','mailto:','#')):continue
   target=target.split('#')[0].split('?')[0].strip('<>');assert (base/target).exists(),('broken Markdown local link',path,target);count+=1
 return count

def preseal():
 import build,check_coverage,fixtures
 out=build.derive()
 for p,b in out.items():assert (S/p).read_bytes()==b,'offline derivative '+p
 coverage=check_coverage.main();assert coverage==json.loads((R/'coverage-validation.json').read_bytes())
 fi=fixtures.main();assert fi==json.loads((R/'fixtures.json').read_bytes())
 sources=source_audit();links=link_audit()
 for p in owned().values():
  assert p.stat().st_size<40000000 and '__pycache__' not in p.parts and 'node_modules' not in p.parts
 return {'status':'pass','deterministic_derivatives':len(out),'source_audit':sources,'coverage':coverage,'fixture_cases':fi['case_count'],'negative_fixtures':fi['negative_count'],'local_markdown_links':links,'producer_writes':False,'coordinator_acceptance':False}

def main():
 rows=audit_members();v=preseal();assert v==json.loads((R/'validation.json').read_bytes())
 import replay_inputs,replay_originals
 entire=replay_inputs.main();assert entire==json.loads((R/'input-replay.json').read_bytes())
 originals=replay_originals.main();assert originals==json.loads((R/'original-replay.json').read_bytes())
 # No writes at any point in this verifier. Seal/manifest are validated again
 # after complete shared-source reconstruction to catch membership/hash changes.
 assert audit_members()==rows
 manifest=(R/'asset-manifest.json').read_bytes()
 return {'status':'pass_final_read_only_full_audit','owned_manifest_targets':rows,'owned_files_including_manifest':rows+1,'manifest_bytes':len(manifest),'manifest_sha256':sha(manifest),'source_requests':v['source_audit']['requests'],'complete_source_roots':entire['complete_roots'],'whole_companions':entire['whole_companions'],'complete_recursive_objects':entire['recursive_complete_objects'],'frozen_file_pins':entire['frozen_current_file_pins'],'historical_bodies':entire['historical_virtual_bodies'],'whole_originals':originals['whole_original_entities'],'zip_members':originals['all_zip_members'],'all_county_candidate_positions':v['coverage']['all_county_candidate_positions'],'full_source_object_bindings':v['coverage']['full_native_and_raw_object_bindings'],'parents':36,'known_contexts':510,'unavailable_parent_cases':31,'canonical_native_priority':None,'coordinator_acceptance':False,'writes_after_seal':False}
if __name__=='__main__':print(json.dumps(main(),indent=2))
