#!/usr/bin/env python3
"""Build research inventory and ordered source-reference indices offline."""
import sys
sys.dont_write_bytecode=True
from common import *
from dependencies import semantic
from inspect_sources import workbook
import re,csv,io,collections

def clean(b):
 s=b.decode('utf-8','replace') if isinstance(b,bytes) else b
 return ' '.join(' '.join(HTML(re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',s,flags=re.S|re.I).encode()).text).split())
def reference(c,pointer,value):return {'file':c,'JSON_pointer':pointer,'recursive_semantic_sha256':semantic(value),'resolution':'Complete object, every nested candidate/source/method/null/admin field; never a vote-only projection.'}
def main():
 c=json.loads((STATE/'data/turnout/priority-set.json').read_text());parents=c['county_parents'];priority=set(c['ordered_priority_parent_keys']);receipt={p.name.removesuffix('.receipt.json'):json.loads(p.read_text()) for p in (ROOT/'raw').glob('*.receipt.json')}
 r,b=load('county-directory');html=b.decode();rows=[]
 for m in re.finditer(r'<tr\b[^>]*class="rg(?:Alt)?Row"[^>]*>(.*?)</tr>',html,re.S):
  cells=re.findall(r'<td\b[^>]*>(.*?)</td>',m[1],re.S);fields=[{'column_ordinal':i,'raw_cell_HTML':s,'literal_text':''.join(HTML(s.encode()).text),'links':HTML(s.encode()).resolved(r['final_url'])} for i,s in enumerate(cells)]
  rows.append({'source_row_ordinal':len(rows),'source_row_HTML':m[0],'fields':fields})
 assert len(rows)==66
 headers=[''.join(HTML(m.encode()).text) for m in re.findall(r'<th\b[^>]*>(.*?)</th>',html,re.S)][-9:]
 directory={'source_receipt':'raw/county-directory.receipt.json','headers':headers,'rows':rows,'scope':'All66 literal public directory records. Mailing addresses are not presumed polling places. Obfuscated email links and blanks retained; no outreach.'};dump('authority-directory.json',directory)
 rd,bd=load('state-counties');state_links={a['text'].strip():a for a in HTML(bd).resolved(rd['final_url']) if 'cty=' in a['url']}
 sr,sb=load('sdaco-counties');local_links={a['text'].strip():a for a in HTML(sb).resolved(sr['final_url'])}
 unitindex=[];investigations=[];inventory=[]
 inventory.append({'authority_key':'SD','authority_name':'South Dakota Secretary of State','county_fips':'','priority_native_count':'304','historical_native_count':'691','official_directory':'https://sdsos.gov/elections-voting/default.aspx','original_directory_fields_json':'','state_county_route':load('state-results-media')[0]['url'],'state_native_county_id':'','local_directory_link':'','investigated_receipts_json':json.dumps(['raw/state-results-media.receipt.json','raw/state-csv.receipt.json','raw/state-races-native-xlsx.receipt.json','raw/state-candidate-service.receipt.json','raw/state-turnout-service.receipt.json']),'depth':'Current setup/schema/download inspected; no November votes admitted','limitations':'673 overall;656 Senate banner;654 native/65 county workbook; no timestamped genuine vote sequence.'})
 for pi,p in enumerate(parents):
  f=p['parent_key'];name=p['county'];d=next(x for x in rows if x['fields'][0]['literal_text'].strip()==name);a=state_links[name];ids=['county-'+f,'county-'+f+'-native-xlsx','local-'+f,'local-detail-'+f,'local-election-'+f]
  related=[id for id in ids if id in receipt]
  paths=['raw/'+id+'.receipt.json' for id in related]
  # Supplement deep local chains already investigated through exact links.
  extras={'46011':['brookings-results','brookings-runoff'],'46083':['lincoln-archive','lincoln-2024','lincoln-2022','lincoln-ballot','lincoln-state-route'],'46061':['hanson-ballot'],'46079':['lake-2022'],'46103':['pennington-history','pennington-ballot']}.get(f,[])
  paths+=['raw/'+id+'.receipt.json' for id in extras if id in receipt]
  allfound=[]
  for id in related+extras:
   if id not in receipt:continue
   rr,bb=load(id)
   if rr['status']==200 and b'<html' in bb[:1000].lower():
    for link in HTML(bb).resolved(rr['final_url']):
     if any(w in (link['text']+' '+(link['href'] or '')).lower() for w in ['election','result','auditor','vote','absentee','canvass','ballot']):allfound.append({'parent_receipt':'raw/'+id+'.receipt.json',**link})
  if f in priority:
   rr,bb=load('county-'+f);h=HTML(bb);controls=[a for t,a in h.tags if t=='input' and a.get('raceid')=='14412'];note='State county page contains Senate setup controls; values remain zero/test. Individual Precinct Level POST returns statewide scope, not county-only scope.' if controls else 'State county page has no Senate contest or export control; Charles Mix absent from returned statewide Senate workbook.'
   localstatus=[{'receipt':'raw/'+id+'.receipt.json','url':receipt[id]['url'],'final_url':receipt[id]['final_url'],'status':receipt[id]['status'],'error':receipt[id]['error']} for id in related if id.startswith('local')]
   gap='No numeric source-native ID in historical workbook; original sheet/row is the key. No proven historical/current native join, method split, physical board/polygon allocation, final current identity or feed approval. Shared state ancestry is investigated, not304 independently verified current feeds.'
   investigations.append({'id':'parent-'+f,'county_fips':f,'county':name,'historical_parent':reference('data/turnout/priority-set.json','/county_parents/'+str(pi),p),'priority_keys_ordered':p['ordered_priority_native_keys'],'all_keys_ordered':p['ordered_all_native_keys'],'actual_state_route':a,'state_receipt':'raw/county-'+f+'.receipt.json','state_control_attributes':controls,'state_observation':note,'authority_chain':['raw/sos-election-root.receipt.json','raw/county-directory.receipt.json','raw/state-counties.receipt.json']+paths,'local_authority_chain':['raw/sos-auditor-resources.receipt.json','raw/sdaco.receipt.json','raw/sdaco-counties.receipt.json'],'local_observations':localstatus,'selected_local_links':allfound,'current_native_join':None,'voting_method_dimension':None,'source_version':None,'observed_cadence':None,'exact_remaining_senate_votes':None,'finer_gap':gap})
  inventory.append({'authority_key':f,'authority_name':name+' County election authority (public auditor directory)','county_fips':f,'priority_native_count':str(len(p['ordered_priority_native_keys'])),'historical_native_count':str(p['source_native_rows']),'official_directory':r['url'],'original_directory_fields_json':json.dumps(d['fields'],ensure_ascii=False),'state_county_route':a['url'],'state_native_county_id':re.search(r'[?&]cty=([^&]+)',a['url'])[1],'local_directory_link':local_links.get(name,{}).get('url',''),'investigated_receipts_json':json.dumps(paths),'depth':'Individually requested state parent + available officially linked local chains/downloads' if f in priority else 'Directory/state route inventoried only; local result chain not individually requested','limitations':'Current native join/method/cadence/remainder unknown; historical parent and leaves preserved in frozen full contract.'})
 dump('county-investigations.json',{'priority_parent_order':c['ordered_priority_parent_keys'],'investigations':sorted(investigations,key=lambda o:c['ordered_priority_parent_keys'].index(o['county_fips']))})
 for i,u in enumerate(c['all_units']):
  unitindex.append({'historical_key':u['key'],'rank':u['rank'],'priority80':u['priority80'],'county_parent_key':u['county_parent_key'],'complete_historical_object':reference('data/turnout/priority-set.json','/all_units/'+str(i),u),'investigation':'parent-'+u['county_parent_key'] if u['priority80'] else None,'finer_historical_locator':u['source_native_constituents'],'current_native_identifier':None,'current_join_status':'unverified; same literal label/number/count is insufficient','discovery_depth':'Actual shared parent chain investigated; exact row/current gap retained' if u['priority80'] else 'Remainder retained; directory/state-parent route inventory, not equally deep local investigation'})
 dump('ordered-priority-records.json',unitindex[:304]);dump('ordered-remainder-records.json',unitindex[304:]);dump('complete-historical-graph.json',{'authority_path_only':'data/coordinator-priority-acceptance.json','contract_pin':pin(STATE/'data/turnout/priority-set.json'),'complete_recursive_contract':reference('data/turnout/priority-set.json','',c),'historical_alternatives':[reference('data/turnout/priority-set.json','/separate_historical_native_universes/'+y,v) for y,v in c['separate_historical_native_universes'].items()],'all_frozen_companion_and_raw_objects':'dependency-verification.json','complete_object_policy':'Resolve exact full originals read-only; no huge original duplicated. All691 full leaves/66 full parents/304 priorities/387 remainder,687/693 historical alternatives,679 PDF companion and unavailable fields accessible.'})
 out=STATE/'data/official-results-sources.csv'
 with out.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(inventory[0]));writer.writeheader();writer.writerows(inventory)
 # Current setup workbook reconciliation, with every source row available in complete transcript.
 w=workbook(load('state-races-native-xlsx')[1]);counts=[];allvotes=[]
 for s in w['sheets']:
  leaves=[];foot=[]
  for row in s['rows']:
   d={x['attributes']['r'].rstrip('0123456789'):x['value_resolved'] for x in row['cells']}
   if d.get('B') and str(d.get('C','')).isdigit():
    if d['B']=='TOTALS':foot.append(d)
    else:leaves.append(d);allvotes.append([int(d['C']),int(d['D'])])
  counts.append({'county_literal':s['attributes']['name'],'numeric_native_rows':len(leaves),'numeric_footer_rows':len(foot),'heading_rows':s['rows'][:5]})
 turnout=json.loads(load('state-turnout-service')[1])['d'];dump('current-setup-scope.json',{'status':'test_setup_only','overall_header':673,'Senate_banner_denominator':656,'native_workbook_rows':len(allvotes),'native_county_worksheets':len(counts),'county_scopes':counts,'missing_counties':sorted(set(p['county'] for p in parents)-set(x['county_literal'] for x in counts)),'all_numeric_candidate_sums':[sum(x[i] for x in allvotes) for i in range(2)],'complete_county_turnout_service':turnout,'turnout_TotalPrecincts_sum':sum(x['TotalPrecincts'] for x in turnout),'turnout_Voters_sum':sum(x['Voters'] for x in turnout),'scope_differences':[{'county':x['CountyName'],'turnout_TotalPrecincts':x['TotalPrecincts'],'workbook_rows':next((y['numeric_native_rows'] for y in counts if y['county_literal']==x['CountyName'].replace(' (Vote Center)','')),None)} for x in turnout if x['TotalPrecincts']!=next((y['numeric_native_rows'] for y in counts if y['county_literal']==x['CountyName'].replace(' (Vote Center)','')),None)],'interpretation':'Source-specific displayed scopes; not forced equal. Missing11 Charles Mix plus5 Brookings and3 Hughes account arithmetically for673-654=19, but do not explain656 banner. No current join or exact remaining votes inferred.'})
 print('built67authorities/39investigations/304ordered priorities/387remainder; current',len(allvotes),'native rows')
if __name__=='__main__':main()
