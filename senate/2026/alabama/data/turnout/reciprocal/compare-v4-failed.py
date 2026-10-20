#!/usr/bin/env python3
"""Compare captured historical evidence only. Never execute/import peer writers or calculators."""
import pathlib,tarfile,json,gzip,hashlib,collections,csv,io,math
from fractions import Fraction
R=pathlib.Path(__file__).resolve().parents[1];D=R/'reciprocal'
def sha(b):return hashlib.sha256(b).hexdigest()
class Capture:
 def __init__(self,name):self.tf=tarfile.open(D/name)
 def raw(self,path):return self.tf.extractfile(path).read()
 def j(self,path):
  b=self.raw(path);return json.loads(gzip.decompress(b) if path.endswith('.gz') else b)
o=Capture('turnout-original-phase.tar.gz');p=Capture('baseline-actual-final.tar.gz')
def own(path):return o.j('data/turnout/'+path)
def peer(path):return p.j('data/baselines/'+path)
def eq(a,b,scope):
 if a!=b:raise AssertionError({'scope':scope,'own':a,'peer':b})
counts=collections.Counter();notes=[];results=[]
# All selected raw source fields, headers, positions, full descriptors and member provenance.
pbooks=peer('source/typed-workbooks.json.gz');eq(len(pbooks),201,'peer201members');rawmaps={};zips={x['year']:x['zip_sha256'] for x in pbooks}
for year in [2024,2022,2020]:
 books=own(f'source/workbooks-{year}.json.gz');bm={b['member']['name']:b for b in books}
 eq(set(bm),{b['member'] for b in pbooks if b['year']==year},f'{year} member universe')
 for b in [b for b in pbooks if b['year']==year]:
  ob=bm[b['member']];eq((ob['member']['sha256'],ob['member']['bytes'],ob['member']['zip_crc32'],ob['member']['zip_date_time']),(b['member_sha256'],b['member_bytes'],b['zip_crc32'],b['zip_timestamp']),'member byte/CRC/time')
  eq(len(ob['sheets']),len(b['sheets']),'sheets')
  for s,os in zip(b['sheets'],ob['sheets']):
   eq((os['name'],os['nrows'],os['ncols'],os['merged_cells']),(s['name'],s['nrows'],s['ncols'],s['merged_cells']),'sheet metadata')
   rows={r['row_1based']:r for r in os['rows']};rawmaps[(year,b['member'],s['name'])]=rows
   eq(s['native_columns_1based'],[i+1 for i,v in enumerate(rows[1]['values']) if i>=3 and str(v).strip()],'literal native columns')
   for row in s['selected_rows']:
    ro=rows[row['row']];eq(row['cells'],[[typ,val] for typ,val in zip(ro['types'],ro['values'])],'complete selected typed source row');counts['selected_raw_cells']+=len(row['cells']);counts['selected_raw_rows']+=1
   for row in s['row_descriptors']:
    ro=rows[row['row']];eq(row['cells'],[[ro['types'][c],ro['values'][c]] for c in range(3)],'all row descriptors');counts['row_descriptor_cells']+=3
  counts['members']+=1
results.append('All201 rawselected/header/candidate/admin/party/type/value/null/position/member/ZIP metadata agree; complete original rows remain retained, peer selected-row representation differs only in storage shape.')
# Raw native and final vector records, no scenario/outcome adoption.
pnative=peer('source/native-observations.json.gz');pvectors=peer('native-baselines.json.gz');vectors={u['key']:u for u in pvectors};eq(len(vectors),6270,'unique vector keys');eq(len(pnative),6270,'native count');eq(len({u['key'] for u in pnative}),6270,'unique raw native keys');byown={};county_groups=collections.defaultdict(list)
for year in [2024,2022,2020]:
 for u in own(f'native-units-{year}.json'):byown[u['key']]=u;county_groups[(year,u['county_fips'])].append(u)
eq(set(byown),{u['key'] for u in pnative},'all6270 native keys')
for u in pnative:
 v=byown[u['key']];eq((v['year'],v['county_fips'],v['native_label'],v['native_id'],v['source_member'],v['member_sha256'],v['source_sheet'],v['column_1based']),(u['year'],u['county_fips'],u['native_header_literal'],u['native_header_literal'],u['member'],u['member_sha256'],u['sheet'],u['source_column']),'native identity/source context')
 eq(u['county'],v['source_member'].split('-General-')[1].removesuffix('.xls'),'peer raw member county literal')
 eq(u['zip_sha256'],zips[u['year']],'nativeZIP context');eq((v['reported_candidate_votes'],v['reported_candidate_votes'],0),(u['reported_contest_votes'],u['complete_contest_votes'],u['unknown_candidate_cells']),'native total/missing candidate cells')
 eq(len(v['candidate_votes']),len(u['candidate_rows']),'candidate row count');vec=vectors[u['key']];eq(vec['all_candidate_votes'],v['reported_candidate_votes'],'vector full total');eq(len(vec['candidate_votes']),len(v['candidate_votes']),'vector length')
 vmap={c['candidate']['id']:c for c in vec['candidate_votes']};eq(len(vmap),len(vec['candidate_votes']),'distinct vector candidate identities')
 for c,pc in zip(v['candidate_votes'],u['candidate_rows']):
  vc=vmap[c['candidate_literal'].strip()]
  eq((c['row_1based'],c['contest_literal'],c['party_literal'],c['candidate_literal'],[c['xls_type'],c['raw_value']],c['value']),(pc['source_row'],pc['contest_literal'],pc['party_literal'],pc['candidate_literal'],pc['cell'],pc['votes']),'native candidate raw row')
  eq((c['candidate_literal'].strip(),c['party_literal'],c['value']),(vc['candidate']['name'],vc['candidate']['party'],vc['votes']),'vector identity/count');eq(vc['candidate']['id'],vc['candidate']['name'],'vector candidate id');eq(vc['candidate']['scope'],'generic_write_in' if c['candidate_literal'].strip()=='Write-In' else 'named','vector write-in scope');counts['native_candidate_cells']+=1
 ad=sorted(v['administrative_fields']+v['contest_other_fields'],key=lambda x:x['row_1based']);eq(len(ad),len(u['administrative_rows']),'complete native admin set')
 rows=rawmaps[(u['year'],u['member'],u['sheet'])]
 for c,pc in zip(ad,u['administrative_rows']):
  eq((c['row_1based'],c['contest_literal'],c['candidate_literal'],[c['xls_type'],c['raw_value']],c['value']),(pc['source_row'],pc['contest_literal'],pc['field_literal'],pc['cell'],pc['value']),'native admin typed context')
  eq(c['party_literal'],rows[c['row_1based']]['values'][1],'admin party literal source companion');counts['native_admin_cells']+=1
 counts['native_units']+=1
results.append('All6270 exact native identities, ordered candidate rows/vectors and administrative cells agree. Raw administrative party strings survive in typed rows even where peer administrative observation objects omit a party property.')
# All county/year source candidates/admin aggregates, no imputed unknowns.
for c in peer('source/county-observations.json'):
 year,cf=c['year'],c['county_fips'];us=county_groups[(year,cf)];eq(c['key'],f'AL:{year}:general:{cf}:county','peer parent key presentation');eq(c['native_count'],len(us),'county source native count');eq(c['reported_contest_votes'],sum(u['reported_candidate_votes'] for u in us),'county total');eq(c['complete_contest_votes'],c['reported_contest_votes'],'county known completeness');eq((c['member'],c['member_sha256']),(us[0]['source_member'],us[0]['member_sha256']),'county source member')
 for pc in c['candidate_rows']:
  selected=[next(x for x in u['candidate_votes'] if x['row_1based']==pc['source_row']) for u in us];eq([(x['candidate_literal'],x['party_literal']) for x in selected],[(pc['candidate_literal'],pc['party_literal'])]*len(us),'parent candidate source identity');eq(sum(x['value'] for x in selected),pc['reported_sum'],'parent candidate sum');eq(pc['votes'],pc['reported_sum'],'parent known candidate total');eq(pc['unknown_cells'],0,'parent candidate unknown');counts['parent_candidate_controls']+=1
 for pc in c['administrative_rows']:
  selected=[next(x for x in u['administrative_fields']+u['contest_other_fields'] if x['row_1based']==pc['source_row']) for u in us];eq([(x['contest_literal'],x['candidate_literal']) for x in selected],[(pc['contest_literal'],pc['field_literal'])]*len(us),'parent admin source identity');unknown=sum(x['value'] is None for x in selected);total=sum(x['value'] for x in selected if x['value'] is not None);eq((total,unknown,total if not unknown else None),(pc['reported_sum'],pc['unknown_cells'],pc['complete_sum']),'parent admin known/null sums');counts['parent_admin_controls']+=1
 counts['parent_year_controls']+=1
notes.append('Parent label representation differs for St. Clair: turnout uses the verified Census display name, peer raw observations retain ZIP member literal StClair. Same exact FIPS/member/header/column/native key; no native normalization. Initial overbroad parent display equality adapter failure/input retained.')
notes.append('Final peer vectors use a consistent candidate identity order while raw rows preserve each source order; explicit one-to-one literal candidate mapping compares vector values without changing native identities. Initial positional adapter failure and complete input are retained.')
notes.append('Parent key representation differs: turnout AL:YEAR:general:FIPS versus peer explicit :county suffix. Comparison matches exact election/FIPS parent identity; no native key is changed or normalized.')
# Independent full rank evidence and every all67/full/priority/remainder contract array.
inv=peer('source/independent-inventory.json');ns=own('native-rank-summary.json');cs=own('county-rank-sensitivity.json');owncsv=list(csv.DictReader(io.StringIO(o.raw('data/county-turnout.csv').decode())))
for yr in inv:
 year=yr['year'];eq({r['candidate']:r['sum'] for r in yr['candidate_controls']},own('statewide-controls.json')[str(year)],'label-keyed statewide inventory');eq(sum(c['unknown_cells'] for c in yr['candidate_controls']),0,'state unknown candidate cells')
 for layer,summary in [('native',ns[str(year)]),('county',cs[str(year)])]:
  pi=yr[layer];oo=own(f'native-units-{year}.json') if layer=='native' else [r for r in owncsv if int(r['year'])==year]
  eq(len(oo),len(pi['full_order']),'full order length');eq(pi['total'],summary['denominator'],'rank denominator');eq(pi['top15_votes'],summary['top15_votes'],'top15');eq(pi['minimum80_count'],summary['minimum80_count'],'min80count');eq(pi['threshold_integer'],(4*summary['denominator']+4)//5,'integer80threshold')
  for r,pr in zip(oo,pi['full_order']):
   votes=r['reported_candidate_votes'] if layer=='native' else int(r['candidate_votes']);cum=r['cumulative_votes'] if layer=='native' else int(r['candidate_cumulative_votes']);key=r['key'] if layer=='native' else f"AL:{year}:general:{r['county_fips']}:county";rank=r['rank'] if layer=='native' else int(r['rank_candidate_volume']);eq((key,rank,votes,cum),(pr['key'],pr['rank'],pr['votes'],pr['cumulative_votes']),'every full rank/count/cumulative');counts[layer+'_ordered_positions']+=1
  pk=summary['priority_keys'] if layer=='native' else [k+':county' for k in summary['priority_keys']];rk=summary['remainder_keys'] if layer=='native' else [k+':county' for k in summary['remainder_keys']];eq(pk,pi['priority_keys'],'ordered priority');eq(rk,pi['remainder_keys'],'ordered remainder');k=pi['minimum80_count'];eq(pi['full_order'][k-2]['cumulative_votes'],summary['preceding_votes'],'preceding cumulative');eq(pi['full_order'][k-1]['cumulative_votes'],summary['minimum80_votes'],'cross cumulative');eq(sum(r['votes'] for r in pi['full_order'][k:]),summary['remainder_votes'],'remainder total');counts['full_rank_universes']+=1
contract=own('priority-set.json');parents={r['county_fips']:r for r in contract['parents']};pc=peer('all67-parent-contract.json');eq(set(parents),{r['county_fips'] for r in pc},'all67parent set')
for c in pc:
 q=parents[c['county_fips']];eq((q['constituent_keys'],q['priority_constituent_keys'],q['remainder_constituent_keys']),(c['full_keys'],c['priority_keys'],c['remainder_keys']),'all parent source constituent/priority/remainder arrays');eq(sum(byown[k]['reported_candidate_votes'] for k in c['full_keys']),c['votes'],'parent full vote total');counts['primary_parent_arrays']+=3
notes.append('Parent container order differs only where original ZIP-member order differs from FIPS order (notably Shelby/St. Clair); each exact parent and every ordered constituent array agree. Native full/priority/remainder orders are identical.')
# All original ballot/registration rows, five integer fields/printed rates/source lines.
ob=own('ballot-registration-controls.json');br={ (r['year'],r['county']):r for r in ob['county_rows']+ob['statewide']};bp=peer('source/ballot-registration-controls.json');eq(set(br),{(r['year'],r['county']) for r in bp},'204ballot rows')
for row in bp:
 v=br[(row['year'],row['county'])];eq((v['county_fips'],v['source_line_1based'],v['raw_line'],v['printed_turnout_pct'],v['printed_absentee_pct']),(row['county_fips'],row['source_line_1based'],row['raw_line'],row['turnout_printed'],row['absentee_pct_printed']),'ballot row rawposition/rates')
 for of,pf in [('registered_voters','registered_voters'),('ballots_cast','ballots_cast'),('absentee_ballots','absentee_ballots'),('democrat_ballots','democrat_ballots_or_straight_party'),('republican_ballots','republican_ballots_or_straight_party')]:eq(v[of],row[pf],'ballot numeric cell');counts['ballot_numeric_positions']+=1
 counts['ballot_rows']+=1
# Every field sensitivity order is independently derived from captured peer raw observations.
for file in ['ballot-registration-sensitivity.json','native-ballot-registration-sensitivity.json']:
 for name,obj in own(file).items():
  year=int(name[:4]);s=obj['summary'];rows=obj['ordered_rows'];metric=next(k for k in rows[0] if k in name and k not in ['key','year']);source=[]
  if file.startswith('ballot-'):
   pf={'ballots_cast_report':'ballots_cast','registered_voters_report':'registered_voters','absentee_ballots_report':'absentee_ballots'}[metric]
   for row in bp:
    if row['year']==year and row['county']!='Total':source.append((f"AL:{year}:general:{row['county_fips']}",row[pf]))
  else:
   field={'ballots_cast_source':'Ballots Cast - Total','registration_source':'Registered Voters - Total'}[metric]
   for row in pnative:
    if row['year']==year:
     fields=[c for c in row['administrative_rows'] if c['field_literal'].strip()==field];eq(len(fields),1,'sensitivity source field');assert fields[0]['value'] is not None;source.append((row['key'],fields[0]['value']))
  source.sort(key=lambda x:(-x[1],x[0]));eq([r['key'] for r in rows],[r[0] for r in source],'full sensitivity order');den=sum(r[1] for r in source);eq(den,s['denominator'],'sensitivityden');cum=0
  for actual,derived in zip(rows,source):cum+=derived[1];eq((actual[metric],actual['cumulative_votes'],Fraction(actual['weight_exact'])),(derived[1],cum,Fraction(derived[1],den)),'sensitivity every value/cum/weight')
  k=s['minimum80_count'];assert 5*sum(r[1] for r in source[:k-1])<4*den<=5*sum(r[1] for r in source[:k]);eq(s['full_order'],[r[0] for r in source],'sensitivity allkeys');eq(s['priority_keys'],[r[0] for r in source[:max(k,15)]],'sensitivitypriority');eq(s['remainder_keys'],[r[0] for r in source[max(k,15):]],'sensitivityremainder');eq(s['remainder_votes'],sum(r[1] for r in source[max(k,15):]),'sensitivityremainingvotes');counts['sensitivity_universes']+=1;counts['sensitivity_ordered_positions']+=len(source)
notes.append('Peer does not publish separate ballot/registration/absentee ranking files. All13 turnout field-sensitivity universes were compared to independently sorted captured peer raw field observations; incomplete native registration remains qualified, not a full statewide priority.')
# Canvass raw evidence: same pages/line/literal counts/nulls; interval representation differs.
oc={(2024 if r['source'].startswith('sos-2024') else 2022 if r['source'].startswith('sos-2022') else 2020,r['county'] or 'Total'):r for r in own('canvass-cells.json')}
for row in peer('source/canvass-county-cells.json')+peer('source/canvass-state-controls.json'):
 a=oc[(row['year'],row['county'])];eq((a['county_fips'],a['pdf_page_1based'],a['extracted_line_1based'],a['raw_label'],a['raw_line']),(row['county_fips'],row['pdf_page_1based'],row['text_line_1based_on_page'],row['raw_label'],row['raw_line']),'canvass raw page/line/label')
 for name,c,pcell in zip(a['candidate_names_in_order'],a['cells'],row['candidate_cells']):
  eq((name,c['value']),(pcell['candidate'],pcell['value']),'canvass candidate/nullvalue');eq(c['cell_type']=='blank',pcell['cell_type']=='blank','canvass blank semantics');eq(c['cell_type']=='dash',pcell['cell_type']=='dash','canvass dash semantics');counts['canvass_candidate_controls']+=1
  if c['value'] is None:counts['PDF_null_dash_cells']+=1
 counts['canvass_rows']+=1
notes.append('Canvass intervals are representationally different: turnout retains numeric-token spans and raw complete lines; peer retains full column regions and token text. Explicit visual-number labels differ. Both pin the same PDF/page/line, printed values and three PDF blank/dash nulls; raw native zeros remain separate.')
# Exact shared original receipt/body contexts, plus capture-only additional original receipt checks.
owned_http={json.loads(o.raw(n))['original_sha256']:json.loads(o.raw(n)) for n in o.tf.getnames() if n.startswith('data/turnout/source/http/') and n.endswith('.receipt.json')}
for ref in peer('source/original-references.json')+peer('source/supplementary-original-references.json'):
 meta=ref['metadata'];eq(meta,owned_http[ref['original_sha256']],'complete shared original receipt scope');eq(sha(p.raw('data/baselines/'+ref['receipt'])),ref['receipt_sha256'],'captured receipt hash');counts['identical_full_HTTP_receipts']+=1
shared={r['id']:r for r in own('source/original-receipts.json')}
for y in [2024,2022,2020]:
 pr=peer(f'source/canvass-{y}.receipt.json');orr=shared[f'sos-{y}-canvass-original'];eq({k:orr[k] for k in pr},pr,'complete canvass individual receipt');counts['identical_shared_PDF_receipts']+=1
pr=peer('source/ballots-2020.receipt.json');orr=shared['sos-2020-ballots-original'];eq({k:orr[k] for k in pr},pr,'complete2020ballotreceipt');counts['identical_shared_PDF_receipts']+=1
# Prove Jefferson's corrected inventory matches already-correct raw candidate identity, not global row ordinals.
jeff=[u for u in pnative if u['year']==2024 and u['county_fips']=='01073'];sv=collections.Counter()
for u in jeff:
 for c in u['candidate_rows']:sv[(c['source_row'],c['candidate_literal'].strip())]+=c['votes']
eq(sv[(12,'Jill Stein')],994,'JeffersonliteralStein');eq(sv[(13,'Chase Oliver')],731,'JeffersonliteralOliver')
notes.append('Baseline source-discovered correction was its statewide ordinal aggregation only. Final label-keyed inventory now agrees all6/4/3 controls. Jefferson literal row12 Stein994 / row13 Oliver731 reverse Autauga order. Raw per-native/county candidate data and all turnout counts/keys/orders were already correct; no false publication conflict or residual correction is adopted.')
proof={'status':'PASS','peer_agent_id':'f2db457b-3e3c-47d0-a65c-7d6be8bbe5c7','scope':'Only captured final historical source evidence, native/county candidate/admin/ballot controls, identities and complete volume rankings/priority/remainders. No future/whole peer-report/model/scenario/outcome/current-legal equality.','own_original_manifest_sha256':'4e2a1f5ab3c66508444c112f9e6430006dce94f795a172837c7b95eaee557207','peer_captured_final_manifest_sha256':'13ec2553cbeafdbf4111f1decd6c686e14d5fbfb8c196c70d3e95836f7016254','counts':dict(counts),'results':results,'representational_differences_and_scope_notes':notes,'primary':{k:v for k,v in ns['2024'].items() if k not in ['full_order','priority_keys','remainder_keys']},'independent_peer_agreement':True,'coordinator_acceptance':False,'current_2026_geographic_admission':False,'legal_eligible_writein_completeness':False,'collector_cadence_pool_probability_admission':False}
(D/'comparison.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'status':'PASS','counts':dict(counts),'scope':proof['scope']},indent=2))
