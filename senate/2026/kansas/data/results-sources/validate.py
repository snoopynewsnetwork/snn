#!/usr/bin/env python3
"""Offline validation. Exit nonzero on changed bytes, missing scope or controls.
--check-only verifies deterministic validation output without rewriting it.
"""
import collections,csv,datetime,gzip,hashlib,json,pathlib,re,sys,urllib.parse
R=pathlib.Path(__file__).resolve().parent;D=R.parent;S=D.parent
J=lambda p:json.loads(p.read_text())
H=lambda b:hashlib.sha256(b).hexdigest()
checks=[]
def check(name,condition,detail=None):
 if not condition:raise AssertionError((name,detail))
 checks.append({'check':name,'pass':True,**({'detail':detail} if detail is not None else {})})
a=J(R/'acquisition.json');meta={x['id']:x for x in a};contract=J(D/'turnout/priority-set.json');keys=contract['ordered_priority_keys']
check('unique captured request identities',len(meta)==len(a)==422)
check('all acquisitions preserve UTC and exact requested URLs',all(datetime.datetime.fromisoformat(x['retrieved_at_utc']).utcoffset().total_seconds()==0 and x.get('url','').startswith('https://') or datetime.datetime.fromisoformat(x['retrieved_at_utc']).utcoffset().total_seconds()==0 and x.get('url','').startswith('http://') for x in a))
bodies=0;reused=0;ownedhash=[]
for x in a:
 if not x.get('body_path'):
  assert x.get('error') and x.get('status') is None,x['id'];continue
 p=(R/x['body_path']).resolve();assert p.is_relative_to(S),x['id'];z=p.read_bytes();b=gzip.decompress(z)
 assert H(z)==x['stored_sha256'] and len(z)==x['stored_bytes'] and H(b)==x['original_sha256'] and len(b)==x['original_bytes'],x['id']
 assert len(z)<40000000 and isinstance(x['headers'],dict) and isinstance(x['redirects'],list) and x.get('requested_url')==x['url'] and x.get('final_url'),x['id']
 bodies+=1;reused+=not p.is_relative_to(R)
 if p.is_relative_to(R):ownedhash.append((H(b),str(p)))
check('all complete HTTP originals/stored hashes/sizes/headers/redirects',bodies==417,{'body_records':bodies,'external_reuse_records':reused,'transport_failures':len(a)-bodies})
byhash=collections.defaultdict(set)
for h,p in ownedhash:byhash[h].add(p)
check('exact owned original bodies deduplicated without dropping request records',all(len(p)==1 for p in byhash.values()))
check('failed response originals retained separately',collections.Counter(x.get('status','transport') for x in a)=={200:380,403:22,404:9,202:6,'transport':5})
freeze=J(R/'frozen-inputs.json')
for x in freeze['assets']:
 p=(R/x['path']).resolve();assert p.is_relative_to(S.parent) and not p.is_relative_to(R);b=p.read_bytes();assert H(b)==x['sha256'] and len(b)==x['bytes'] and len(b)<40000000,x['path']
check('immutable external source/coordinator pins',len(freeze['assets'])==41)
check('final accepted priority contract bytes',H((D/'turnout/priority-set.json').read_bytes())=='dcdc1457a5b08851ef76b5372435d56788f647708da5ff9a6ef35435f92fa6a7' and (D/'turnout/priority-set.json').stat().st_size==20297853)
check('latest turnout manifest pin',H((D/'turnout/asset-manifest.json').read_bytes())=='ffa25d2d8e1f9d7f8463cf60e007c580c51ac052b4653171d764be11aa679290')
check('final county turnout CSV pin',H((D/'county-turnout.csv').read_bytes())=='44ff0242c75a5c310a15ff705138cd93a86365bcc622301fc49c05c9133a8993')
accept=J(D/'coordinator-priority-acceptance.json')
check('external coordinator acceptance, no worker self-approval',accept['accepted'] is True and accept['contract_sha256']==H((D/'turnout/priority-set.json').read_bytes()))
expected=['20091','20173','20177','20045','20209','20103','20015','20155','20161','20169','20121','20037','20079','20113','20051','20035','20149','20111','20059','20125','20055','20009','20191']
check('exact ordered 23 priority keys',keys==['US-KS-'+x for x in expected])
allkeys=[x['county_key'] for x in contract['all_geography_coverage']]
check('whole-state 105 county identity/order',len(allkeys)==len(set(allkeys))==105)
rows=list(csv.DictReader((D/'official-results-sources.csv').open()));cr=rows[1:]
check('state and all105 CSV rows in full accepted order',len(rows)==106 and rows[0]['row_type']=='state' and [x['county_key'] for x in cr]==allkeys)
check('priority depth exactly23 and other82 discovery-level',[(x['county_key'],int(x['priority_rank'])) for x in cr if x['priority_rank']]==list(zip(keys,range(1,24))) and sum(x['research_depth']=='discoverylevel' for x in cr)==82)
contacts=J(R/'county-contact-evidence.json')
check('all105 literal manual contact blocks',len(contacts)==105 and {x['county_key'] for x in contacts}==set(allkeys) and all(x['phone'] and x['literal_block'] and x['page']==2 for x in contacts))
inv=J(R/'county-inventory.json')
check('full county inventory preserves all525 family contexts',len(inv)==105 and sum(len(x['full_historical_native_families']) for x in inv)==525)
check('no fabricated November IDs/outstanding/cadence/crosswalk',all(not x['november_election_id'] and not x['november_contest_id'] and not x['outstanding_valid_senate_votes'] and 'no guaranteed' in x['cadence_status'] and 'crosswalk' in x['missing_fields'] for x in cr))
counts=collections.Counter();unknown=collections.Counter();ids=[]
for c in contract['all_geography_coverage']:
 for f in c['source_native_families']:
  for u in f['constituents']:
   counts[f['source_id']]+=1;unknown[f['source_id']]+=u['named_candidate_total'] is None;ids.append(u['unit_key'])
check('all22031 native constituents preserved with no cross-family sum',len(ids)==len(set(ids))==22031 and list(counts.values())==[4567,4566,4535,3867,4496],dict(counts))
check('unavailable native counts remain unavailable',list(unknown.values())==[0,13,12,19,31],dict(unknown))
audit=J(R/'historical-native-audit.json')
check('independent original broader2024 allcounty/candidate controls',audit['all_105_broad2024_candidate_cells_checked']==420 and audit['state_four_named_total']==1327591)
check('independent original priority native/candidate/ID samples',audit['original_ooxml_sample_units']==115 and audit['original_ooxml_sample_candidate_cells']==625 and audit['original_ooxml_sample_identity_fields']>0 and audit['no_residual_allocation'] is True,{'unit_samples':115,'candidate_cells':625,'identity_fields':audit['original_ooxml_sample_identity_fields']})
votes={x['county_key']:int(x['president_2024_total']) for x in csv.DictReader((D/'county-turnout.csv').open())}
check('exact23/top15/previous22/Sumner/remainder named controls',sum(votes.values())==1327591 and sum(votes[k] for k in keys)==1067659 and sum(votes[k] for k in keys[:15])==970376 and sum(votes[k] for k in keys[:-1])==1057110 and votes[keys[-1]]==10549 and sum(v for k,v in votes.items() if k not in keys)==259932)
graph=J(R/'authority-graph.json')
check('actual authority links preserve source positions/repeats',graph['literal_parent_link_checks']==278 and len(graph['nodes'])==422)
for x in graph['nodes']:
 if x['full_parent_link_object']:
  p=x['parent'];link=x['full_parent_link_object'];saved=J(R/'extracts'/f'{p}.links.json');assert link in saved and link['position']==x['parent_link_position'] and urllib.parse.unquote(link['url'])==urllib.parse.unquote(x['requested_url'])
check('all278 exact literal parent links independently checked',True)
vc=J(R/'vendor-checks.json');ve=J(R/'vendor-extracts.json')
check('six Clarity contest detail row/column and named control checks',len(vc)==9 and sum(x.get('row_and_column_sums_match',False) for x in vc)==6)
check('three full native XML/CSV extractions retain1708 rows',sum(x.get('native_csv_rows',0) for x in vc)==1708 and len(ve)==9)
check('Butler primary source difference deliberately retained',next(x for x in vc if x['source_id']=='butler-primary')['named_county_controls_match'] is False)
check('Miami reported-count disagreement deliberately retained',all(x['summary_PR']==54 and x['sum_PR']==57 for x in vc if x['source_id']=='miami-vendor'))
manual=J(R/'manual-visual-checks.json')['checks']
check('scanned original visual evidence and page renders exist',len(manual)==8 and all((R/p).exists() for x in manual for p in x['render_paths']))
ocr=J(R/'notice-ocr-inventory.json')['records'];ocrwords=0
for x in ocr:
 p=R/x['render_path'];b=p.read_bytes();assert H(b)==x['render_sha256'] and meta[x['source_id']]['original_sha256']==x['source_original_sha256']
 width=int.from_bytes(b[16:20],'big');height=int.from_bytes(b[20:24],'big')
 assert (R/x['full_text_path']).exists()
 for word in csv.DictReader((R/x['full_word_positions_path']).open(),delimiter='\t',quoting=csv.QUOTE_NONE):
  assert int(word['page_num'])==1 and int(word['left'])>=0 and int(word['top'])>=0 and int(word['left'])+int(word['width'])<=width and int(word['top'])+int(word['height'])<=height
  ocrwords+=word['level']=='5'
check('all10 fullnotice OCR page/word positions and source hashes retained',len(ocr)==10 and ocrwords>1500,{'full_word_records':ocrwords})
f=next(x for x in manual if x.get('county')=='Franklin')
check('Franklin printed official primary difference retained',sum(f['visual_named_vector'].values())==5153 and sum(x['county_minus_state'] for x in f['comparisons'].values())==-52 and f['matches_accepted_county_control'] is False)
r=J(R/'riley-2024-source-reconciliation.json')
check('Riley summary named/generic/ballot scopes and signed alternative preserved',sum(r['county_minus_state'].values())==-393 and r['county_summary_named_total']+r['county_summary_generic_writeins']==24120 and r['county_summary_ballots']==24266 and next(x for x in manual if x.get('source_id')=='riley-2024-abstract')['matches_accepted_county_control'] is True)
b=next(x for x in manual if x.get('county')=='Barton')
check('Barton repeated generic child is overlapping not additive',b['observations']['generic_writein']==b['observations']['not_assigned_child']==47 and b['observations']['child_overlaps_generic'] is True)
polls=J(R/'poll-hours-evidence.json')
check('105 timezone/default/local scope distinctions',len(polls)==105 and {x['county'] for x in polls if x['timezone']=='Mountain'}=={'Sherman','Wallace','Greeley','Hamilton'})
sherman=next(x for x in polls if x['county']=='Sherman')
check('Sherman actual generic7–7 Mountain extension retained with Nov gap',sherman['local_notice']['close']=='19:00' and sherman['local_notice']['election_date'] is None and sherman['statutory_default']=='06:00–18:00')
check('Riley actual signed November canvass is not empty scan text',next(x for x in cr if x['county']=='Riley')['county_canvass_observation'].startswith('2026-11-12 10:00'))
report=(S/'official-results.md').read_text()
check('actual printed3Senate candidate universe and writein gap',all(x in report for x in ['David C. Graham','Adam Hamilton','Roger Marshall','affidavit roster','unavailable, not zero']))
check('signed court chronology and later-disposition limitation',all(x in report for x in ['July 16, 2026','October 2','November 24','Later-disposition limitation','last USPS delivery','not a final merits']))
admin=J(R/'administrative-observations.json')
check('actual observed administrative fields remain separate from valid Senate outstanding',admin['literal_fields'][0]['value']==18293 and admin['literal_fields'][1]['value']==107 and admin['source_update_or_asof_clock'] is None and 'no valid Senate' in admin['admission'])
check('current writein statute distinguished from outdated SOS guidance', 'superseded on this point' in report and '25-1216(b)' in report and 'Chapter 155' in report)
check('plurality/recount/requested versus validvotes distinctions',all(x in report for x in ['KSA 25-702','5 p.m. the day after','not trigger an automatic recount','administration, not a result publication schedule']))
for doc in [S/'official-results.md',R/'SCHEMA.md']:
 for target in re.findall(r'\]\(([^\n)]+)\)',doc.read_text()):
  if target.startswith(('https://','http://','#')):continue
  target=target.split('#')[0];p=(doc.parent/urllib.parse.unquote(target)).resolve()
  assert p.is_relative_to(S.parent) and (p.exists() or p==R/'validation.json'),(doc,target)
check('all relative report/schema links resolve in allowed read-only source tree',True)
files=[p for p in R.rglob('*') if p.is_file()]+[S/'official-results.md',D/'official-results-sources.csv']
check('every stored artifact strictly below40million bytes',all(p.stat().st_size<40000000 for p in files))
check('no dependency/cache/transient trees or PDFs retained accidentally',not any('__pycache__' in p.parts or p.suffix=='.pyc' or p.name.endswith('.temporary.pdf') or 'node_modules' in p.parts for p in files))
manifest=J(R/'artifact-manifest.json');listed=set()
for x in manifest['assets']:
 p=(R/x['path']).resolve();assert p.is_relative_to(R) or p in [S/'official-results.md',D/'official-results-sources.csv'];b=p.read_bytes();assert len(b)==x['bytes'] and H(b)==x['sha256'],x['path'];listed.add(p)
expectedfiles={p.resolve() for p in files if p.name!='artifact-manifest.json'}
check('manifest exact owned file/hash/size coverage',listed==expectedfiles or ('--check-only' not in sys.argv and listed==expectedfiles-{R/'validation.json'}))
check('manifest totals and exclusive bounds',manifest['asset_count']==len(manifest['assets']) and manifest['stored_bytes']==sum(x['bytes'] for x in manifest['assets']) and all(x['bytes']<40000000 for x in manifest['assets']))
out={'status':'PASS','scope':'offline source/scope/conservation/hash/control checks; no current boundary, November feed, cadence, outstanding-count or operational approval','check_count':len(checks),'checks':checks,'material_gaps':['November3Senate feed/election/contest/candidate IDs and current unit crosswalk for all105','guaranteed result cadence and valid outstanding Senate votes for all105','complete current statewide valid write-in affidavit roster and subsequent withdrawals','complete later court docket/disposition after retrieved signed orders; official November24 merits setting retained','county-specific November poll hours/local extensions/canvass appointments as explicitly enumerated','Saline local historical counts inaccessible; McPherson historical county export and other precise county-source gaps in report; accepted SOS historical families retained']}
b=(json.dumps(out,indent=2)+'\n').encode();p=R/'validation.json'
if '--check-only' in sys.argv:assert p.read_bytes()==b,'validation output changed; rerun documented cycle'
else:p.write_bytes(b)
print('PASS',len(checks),'checks;',len(a),'requests;',len(allkeys),'counties;',len(keys),'priority;',len(ids),'native identities')
