#!/usr/bin/env python3
"""Deterministic offline research build. Writes only official-results owned data.
External acceptance is PATH ONLY. No producer mutation, network or live collector.
"""
import csv,gzip,hashlib,io,json,re,sys,zlib,zipfile
from pathlib import Path
from inspect_sources import read_receipt
ROOT=Path(__file__).resolve().parent;STATE=ROOT.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def semantic(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
def write(name,x):
 b=(json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode();p=ROOT/name;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(gzip.compress(b,mtime=0) if str(name).endswith('.gz') else b)
def pin(path):
 p=STATE/path;b=p.read_bytes();return {'path':path,'bytes':len(b),'sha256':sha(b)}
def decoded(r):
 b=read_receipt(r);e=next((v for k,v in r['headers'].items() if k.lower()=='content-encoding'),'').lower()
 return gzip.decompress(b) if e=='gzip' else zlib.decompress(b) if e=='deflate' else b
class Files:
 def __init__(self):self.cache={}
 def get(self,name):
  if name not in self.cache:
   b=(STATE/name).read_bytes();b=gzip.decompress(b) if name.endswith('.gz') else b
   if '.jsonl' in name:x=[json.loads(line) for line in b.splitlines()]
   elif '.csv' in name:x=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
   else:x=json.loads(b)
   self.cache[name]=x
  return self.cache[name]
def resolve(x,pointer):
 for piece in pointer.strip('/').split('/'):
  piece=piece.replace('~1','/').replace('~0','~');x=x[int(piece)] if isinstance(x,list) else x[piece]
 return x

def main():
 acceptance=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text());contract_name='data/turnout/priority-set.json';f=Files();c=f.get(contract_name)
 assert pin(contract_name)==acceptance['frozen_contract']
 originals=[];external={contract_name}
 # Individually immutable originals, complete receipt bodies, no mutable aggregate news ledger.
 for r in json.loads((STATE/'data/turnout/source/shared-source-pins.json').read_text()):
  p=(STATE/'data/turnout/source'/r['reference_path']).resolve();q=dict(r,source_path=p.relative_to(STATE).as_posix());originals.append(q);external.add(q['source_path'])
 for r in json.loads((STATE/'data/baselines/source/acquisition.json').read_text()):
  path='data/baselines/'+r['path'];originals.append(dict(r,source_path=path));external.add(path)
 # Required complete companion files, preserving raw reconstructed bytes and all full semantics.
 companions=[]
 for expected in acceptance['complete_source_companion_files']:
  path=expected['path'];actual=pin(path);assert all(actual[k]==expected[k] for k in actual);b=(STATE/path).read_bytes();raw=gzip.decompress(b) if path.endswith('.gz') else b
  x=f.get(path);q=dict(actual,full_semantic_sha256=semantic(x),complete_body_required=True,projection_or_subset_substitution=False)
  if path.endswith('.gz'):q.update(complete_reconstructed_bytes=len(raw),complete_reconstructed_sha256=sha(raw))
  if isinstance(x,(list,dict)):q['complete_length']=len(x)
  if '.jsonl' in path:q['complete_rows']=len(x)
  if '.csv' in path:q.update(complete_rows=len(x)-1,complete_header=x[0])
  assert q['full_semantic_sha256']==expected['full_semantic_sha256'];companions.append(q);external.add(path)
 roots=[]
 for key,value in c.items():roots.append({'pointer':'/'+key,'full_recursive_semantic_sha256':semantic(value)})
 assert roots==acceptance['complete_root_field_semantics']
 refs=[]
 for r in acceptance['complete_source_object_references']:
  value=resolve(f.get(r['file']),r['pointer']) if 'pointer' in r else f.get(r['file'])[r['JSONL_record']-1]
  q=dict(r,full_recursive_semantic_sha256=semantic(value));assert q==r;refs.append(q)
 write('historical-conservation.json.gz',{'schema':'CO-full-frozen-source-reference-conservation-v1','external_authority_path':'data/coordinator-priority-acceptance.json','contract':pin(contract_name),'root_fields':roots,'complete_companions':companions,'complete_source_object_references':refs,'complete_native_universe':3199,'complete_parent_universe':64,'control_key_null_presentations':'195 county/state representations are explicit; native keys exact','current_geography_approved':False,'current_November_returns_admitted':False})
 write('historical-original-receipts.json',originals)
 # All current response objects and all SSR payloads are complete, alongside immutable originals.
 rs=json.loads((ROOT/'acquisition.json').read_text());by={r['id']:r for r in rs};pages=json.loads(gzip.decompress((ROOT/'observed-pages.json.gz').read_bytes()));objects={};schemas={};zip_exports={}
 def schema(value,at='$',out=None):
  if out is None:out={}
  typ=type(value).__name__;out.setdefault(at,set()).add(typ)
  if isinstance(value,dict):
   for k,v in value.items():schema(v,at+'/'+k,out)
  elif isinstance(value,list):
   for v in value:schema(v,at+'/*',out)
  return out
 for r in rs:
  b=decoded(r)
  try:
   x=json.loads(b);objects[r['id']]=x;schemas[r['id']]={k:sorted(v) for k,v in sorted(schema(x).items())}
  except (ValueError,UnicodeDecodeError):pass
  if r['body_path'] and not r['body_path'].startswith('data/results-sources/'):external.add(r['body_path'])
  v=pages.get(r['id'])
  if v:
   for sc in v['scripts']:
    if dict(sc['attributes']).get('id')=='__NEXT_DATA__':
     x=json.loads(sc['body']);objects[r['id']+'#__NEXT_DATA__']=x;schemas[r['id']+'#__NEXT_DATA__']={k:sorted(v) for k,v in sorted(schema(x).items())}
  if b.startswith(b'PK'):
   with zipfile.ZipFile(io.BytesIO(b)) as z:
    if any(a.filename.endswith('.csv') for a in z.infolist()):
     members=[]
     for a in z.infolist():
      raw=z.read(a.filename);members.append({'name':a.filename,'bytes':len(raw),'sha256':sha(raw),'CRC':a.CRC,'rows':list(csv.reader(io.StringIO(raw.decode('utf-8-sig')))) if a.filename.endswith('.csv') else None})
     zip_exports[r['id']]={'source_receipt':r['id'],'members':members,'scope':'complete ZIP members; aggregate administrative return categories overlap and never allocate Senate votes'}
 write('response-objects.json.gz',objects);write('response-schemas.json.gz',schemas);write('aggregate-exports.json',zip_exports)
 # Full statewide primary hierarchy and exact45 parent packets from actual source tuples.
 state_settings=objects['feed-535-54'];tuples=state_settings['settings']['electiondetails']['participatingcounties'];monitor=[];packets={}
 contacts=json.loads((ROOT/'directory-contacts.json').read_text());directory=json.loads((ROOT/'directory-rows.json').read_text());dmap={d['county_literal']:d for d in directory};contact={d['county_literal']:d for d in contacts}
 primary={}
 for literal in tuples:
  name,eid,version,clock,status=literal.split('|');county=name.replace('_',' ');base=f'https://results.enr.clarityelections.com/CO/{name}/{eid}/{version}/json';monitor.append({'county_literal':county,'published_county_slug':name,'complete_tuple_literal':literal,'EID_literal':eid,'version_literal':version,'clock_literal':clock,'status_literal':status,'source_receipt':'feed-535-54','scope':'June 2026 primary only; no November or historical child equivalence'})
  if county not in acceptance['ordered_priority_parent_literals']:continue
  config=next(r for r in rs if r['url']==base+'/config.json');config_obj=objects[config['id']];lang=config_obj['lang'];source={}
  for fname in ['electionsettings','summary','status','details']:
   url=base+('/'+lang if fname in ['electionsettings','summary'] else '')+'/'+fname+'.json';receipt=next(r for r in rs if r['url']==url);assert receipt['status']==200
   source[fname]={'receipt':receipt['id'],'url':url,'complete_object_pointer':'/'+receipt['id'],'full_recursive_semantic_sha256':semantic(objects[receipt['id']])}
  settings=objects[source['electionsettings']['receipt']];summary=objects[source['summary']['receipt']];status_obj=objects[source['status']['receipt']];details=objects[source['details']['receipt']]
  relevant=[{'source_array_position':i,'full_object':o} for i,o in enumerate(summary) if 'senat' in str(o.get('C','')).lower() and not 'state senator' in str(o.get('C','')).lower()]
  primary[county]={'source_tuple_literal':literal,'config_receipt':config['id'],'complete_config':config_obj,'complete_responses':source,'source_clock_literal':settings.get('websiteupdatedat'),'raw_timezoneoffset':settings.get('settings',{}).get('timezoneoffset'),'raw_isdaylightsaving':settings.get('settings',{}).get('isdaylightsaving'),'clock_qualification':'literal source strings; timezoneoffset is not treated as an absolute UTC offset','source_native_status_keys':list(status_obj) if isinstance(status_obj,dict) else None,'observed_primary_reporting_labels':status_obj.get('P') if isinstance(status_obj,dict) else None,'Senate_primary_objects':relevant,'method_schema_qualification':'retain every source status/details/settings/summary field including nulls; source vote-type labels are not November method coverage','current_November_choice_keys_approved':False,'historical_current_child_join':None}
 write('all64-primary-monitoring.json',monitor);write('priority-parent-primary-packets.json.gz',primary)
 notes=json.loads((ROOT/'parent-findings.json').read_text())
 contact_observations={}
 for d in directory:
  page=pages.get(d['landing_id'],{});literal=page.get('text','')
  contact_observations[d['county_literal']]={'source_receipt':d['landing_id'],'contact_anchors':[a for a in page.get('links',[]) if (a.get('href') or '').lower().startswith(('mailto:','tel:'))],'phone_literals':list(dict.fromkeys(re.findall(r'(?:\([0-9]{3}\)|[0-9]{3})[ .-]*[0-9]{3}[ .-][0-9]{4}(?:[^A-Za-z0-9]{0,3}(?:ext\.?|option)[ .:]*[0-9]+)?',literal,re.I))),'qualification':'literal county-page observations, not a replacement for dated SOS roster; entire page retained, absence after access error is unknown'}
 write('authority-contact-observations.json',contact_observations)
 for county in acceptance['ordered_priority_parent_literals']:
  ownedrs=[r['id'] for r in rs if r['county']==county];leaf=primary[county]['complete_responses'];eligible=[]
  for id in ownedrs:
   v=pages.get(id)
   if v:
    s=v['text'];snips=[]
    for m in re.finditer(r'result|november|unofficial|canvass|counting|7.?p\.?m',s,re.I):
     piece=s[max(0,m.start()-80):m.start()+280]
     if piece not in snips:snips.append(piece)
    eligible.append({'receipt':id,'literal_text_evidence':snips[:30]})
  packets[county]={'county_literal':county,'directory_source':dmap[county],'directory_contact':contact[county],'acquired_receipts':ownedrs,'actual_county_findings':notes[county],'qualified_shared_parent_primary_packet':{'path':'priority-parent-primary-packets.json.gz','pointer':'/'+county},'current_leaf':leaf,'current_November_result_identity':{'Denver':{'ElectionId_literal':'20261103','RaceID_literal':1,'source_receipt':'denver-november-payload','candidate_IDs':None,'setup_zero_only':True},'Logan':{'linked_EID_literal':'127446','status':403,'source_receipt':'county-logan-follow-1'},'Pitkin':{'linked_EID_literal':'127457','status':403,'source_receipt':'county-pitkin-follow-1'}}.get(county,None),'county_page_evidence':eligible,'gap':{'current_November_counts_admitted':False,'current_November_candidate_mapping_approved':False,'physical_child_crosswalk':None,'method_child_crosswalk':None,'measured_cadence':None,'exact_remaining_Senate_votes':None,'access_or_scope':notes[county]}}
 write('priority-parent-investigations.json.gz',packets)
 # Every entry carries a reference to the COMPLETE source object and an acquired shared-parent investigation.
 investigations=[]
 for i,key in enumerate(c['ordered_priority_keys']):
  o=c['full_order'][i];assert key==o['key'];county=o['county_literal'];investigations.append({'rank':i+1,'key':key,'complete_source_object':{'file':contract_name,'pointer':'/full_order/'+str(i),'full_recursive_semantic_sha256':semantic(o)},'shared_parent_investigation':{'file':'priority-parent-investigations.json.gz','pointer':'/'+county},'qualified_primary_responses':primary[county]['complete_responses'],'current_November_native_id':None,'current_method_mapping':None,'physical_precinct_mapping':None,'current_admission':False,'qualification':'shared parent is an authority/sample investigation; no identity asserted between historical native child and current primary/November reporting unit'})
 raw=b''.join((json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode() for x in investigations);(ROOT/'priority-investigations.jsonl.gz').write_bytes(gzip.compress(raw,mtime=0))
 # Remainder and all64 hierarchy are exact source-key derivations with full objects available by immutable contract reference.
 hierarchy=[]
 for i,h in enumerate(c['county_native_hierarchy']):
  keys=[o['key'] for o in c['full_order'] if o['county_literal']==h['county']];rem=[k for k in c['ordered_remainder_keys'] if k in set(keys)];assert rem==acceptance['derived_ordered_remainder_child_keys_by_parent'][h['county']]
  hierarchy.append({'county_literal':h['county'],'complete_hierarchy_ref':{'file':contract_name,'pointer':'/county_native_hierarchy/'+str(i),'full_recursive_semantic_sha256':semantic(h)},'ordered_full_child_keys':keys,'ordered_priority_child_keys':[k for k in c['ordered_priority_keys'] if k in set(keys)],'independently_derived_remainder_child_keys':rem,'remainder_attribution':'derived from full/priority/global remainder source keys, not an original parent remainder field'})
 write('all64-hierarchy-and-remainder.json.gz',{'contract':pin(contract_name),'all64':hierarchy,'ordered_remainder_keys':c['ordered_remainder_keys'],'remainder_count':1207,'remainder_votes':638512})
 # Exactly65 whole-state authority rows; deep packets cover45 historical priority parents, other19 remain monitored.
 fields=['jurisdiction','authority_scope','directory_label_literal','directory_county_id_literal','clerk_literal','address_literal_lines','phone_literal','fax_literal_lines','email_literal_lines','directory_revision_literal','directory_url','landing_requested_url','landing_final_url','landing_status','landing_receipt','priority_parent','deep_investigation','primary_EID_literal','primary_version_literal','primary_clock_literal','November_identity_status','current_admission','source_gaps']
 monitor_by={m['county_literal']:m for m in monitor};rows=[dict.fromkeys(fields,'')];rows[0].update(jurisdiction='Colorado',authority_scope='state',directory_label_literal='Colorado Secretary of State',phone_literal='303-894-2200',directory_url=by['sos-directory']['final_url'],landing_requested_url=by['sos-results']['url'],landing_final_url=by['sos-results']['final_url'],landing_status=by['sos-results']['status'],landing_receipt='sos-results',priority_parent='false',primary_EID_literal='126592',primary_version_literal='377440',primary_clock_literal=state_settings['websiteupdatedat'],current_admission='false',November_identity_status='No statewide November result configuration acquired',source_gaps='Observed state product is primary; whole64 directory/primary monitoring separate from45 deep samples')
 for d in directory:
  name=d['county_literal'];ct=contact[name];m=monitor_by[name];r=by[d['landing_id']];row=dict.fromkeys(fields,'');row.update(jurisdiction=name,authority_scope='county',directory_label_literal=d['directory_anchor_text'],directory_county_id_literal=ct['roster_county_id_literal'],clerk_literal=ct['clerk_literal'],address_literal_lines=json.dumps(ct['address_literal_lines'],ensure_ascii=False),phone_literal=ct['phone_literal'],fax_literal_lines=json.dumps(ct['fax_literal_lines'],ensure_ascii=False),email_literal_lines=json.dumps(ct['email_literal_lines'],ensure_ascii=False),directory_revision_literal=ct['directory_revision_literal'],directory_url=by['sos-directory']['final_url'],landing_requested_url=r['url'],landing_final_url=r['final_url'],landing_status=r['status'],landing_receipt=r['id'],priority_parent=str(name in primary).lower(),deep_investigation=('data/results-sources/priority-parent-investigations.json.gz#'+name) if name in primary else '',primary_EID_literal=m['EID_literal'],primary_version_literal=m['version_literal'],primary_clock_literal=m['clock_literal'],November_identity_status='Denver acquired zero setup' if name=='Denver' else 'Actual linked November endpoint 403' if name in ['Logan','Pitkin','Cheyenne'] else 'Not established by bounded investigation',current_admission='false',source_gaps=notes.get(name,'Directory/current authority landing and full-state primary participation monitored; no deep-priority membership, no November native mapping'))
  rows.append(row)
 with (STATE/'data/official-results-sources.csv').open('w',newline='') as stream:w=csv.DictWriter(stream,fieldnames=fields);w.writeheader();w.writerows(rows)
 write('immutable-external-files.json',[pin(name) for name in sorted(external)])
 print('Built',len(investigations),'ordered investigations;',len(packets),'parents;',len(rows),'authority rows;',len(objects),'complete JSON/SSR objects;',len(external),'immutable external files')
if __name__=='__main__':main()
