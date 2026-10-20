#!/usr/bin/env python3
import csv,gzip,json,re,subprocess
from collections import defaultdict
from pathlib import Path
from extract import P,js,load,save
from build import groups,county_groups,pair_for

def main():
 units=groups();counties=county_groups(units);balances=[];diffs=[];states=[];methods=defaultdict(int)
 for u in units:
  if u['lane']=='2024-xlsx':
   for c,v in u['candidates'].items():assert sum(u['methods'][m][c] for m in u['methods'])==v
   for m,cs in u['methods'].items():methods[m]+=sum(cs.values())
 for lane,contest in sorted({(u['lane'],u['contest']) for u in units}):
  us=[u for u in units if (u['lane'],u['contest'])==(lane,contest)];cs=[c for c in counties if (c['lane'],c['contest'])==(lane,contest)];year=lane[:4];sums=defaultdict(int)
  for u in us:
   for n,v in u['candidates'].items():sums[n]+=v
  if lane.endswith('api'):
   meta=js(year+'-metadata')['response']['contests'];cid=next(k for k,m in meta.items() if m['contestName']==contest);node=js(year+'-federal-state')['response']['contests'][cid];expected={meta[cid]['choices'][ch['choiceID']]['name']:ch['totalVotes'] for ch in node['choices']}
   for c in cs:
    n=node['locations'][c['county_fips']];cv={meta[cid]['choices'][ch['choiceID']]['name']:ch['totalVotes'] for ch in n['choices']};balances.append({'scope':c['key']+'|'+contest,'same':cv==c['candidates'],'leaf':c['candidates'],'county_control':cv});assert cv==c['candidates']
  elif lane.endswith('full'):
   n=next(c for c in js(year+'-full')['ContestData'] if c['ContestName']==contest);expected={ch['Name']:ch['TotalVotes'] for ch in n['Candidates']}
  else:expected=None
  if expected is not None:assert dict(sums)==expected,(lane,contest)
  states.append({'lane':lane,'contest':contest,'candidates':dict(sums),'total':sum(sums.values()),'native_units':len(us),'parents':len(cs),'control_exact':dict(sums)==expected if expected else None})
  if lane.endswith('full'):
   ap={c['county_fips']:c for c in counties if c['lane']==year+'-api' and c['contest']==contest}
   for c in cs:
    for n,v in c['candidates'].items():
     av=ap[c['county_fips']]['candidates'][n]
     if av!=v:diffs.append({'year':year,'contest':contest,'county':c['county_fips'],'candidate':n,'api':av,'full':v,'full_minus_api':v-av})
 # Independently parse all 525 PDF county candidate cells with explicit printed candidate order.
 text=subprocess.run(['pdftotext','-layout','-','-'],input=load('2024-pdf-current'),capture_output=True,check=True).stdout.decode();(P/'source/2024-pdf-current.txt').write_text(text)
 section=text[text.index('U.S. President'):text.index('U.S. Congress') if 'U.S. Congress' in text else text.index('U.S. Representative')]
 order=[n for i,n in re.findall(r'^#(\d+)-(.+?) \([A-Z]+\)',section,re.M)];assert len(order)==7,order
 x={c['county_name']:c for c in counties if c['lane']=='2024-xlsx'};pdf=[]
 for ln,line in enumerate(section.splitlines(),1):
  m=re.match(r'^([A-Za-z ]+?)\s+(\d[\d,]*(?:\s+\d[\d,]*){7})\s*$',line)
  if not m:continue
  name=m[1].strip();values=[int(v.replace(',','')) for v in m[2].split()]
  if name.upper() in x:
   expected=x[name.upper()]['candidates'];actual=dict(zip(order,values[:7]));assert actual==expected and sum(actual.values())==values[7],(name,actual,expected)
   pdf.append({'county_printed':name,'section_line':ln,'literal_line':line,'candidates':actual,'total':values[7]})
 assert len(pdf)==75,len(pdf);save('source/pdf-controls.json',{'order':order,'county_rows':pdf,'cells_verified':525})
 # Independent primary Clerk controls preserve literal candidate/party lines, not sorted numeric bags.
 clerk=[]
 for year,tokens in [('2020',{'Senator Tom Cotton':'Tom Cotton, Republican','Ricky Dale Harrington Jr.':'Ricky Dale Harrington, Jr., Libertarian'}),('2022',{'Senator John Boozman':'John Boozman, Republican','Natalie James':'Natalie James, Democrat','Kenneth Cates':'Kenneth Cates, Libertarian'}),('2024',{'Republican':'Republican','Democratic':'Democratic','Independent':'Independent','Libertarian':'Libertarian','Green':'Green','American Solidarity':'American Solidarity','Prohibition':'Prohibition'})]:
  text=subprocess.run(['pdftotext','-layout','-','-'],input=load('clerk-'+year),capture_output=True,check=True).stdout.decode();(P/f'source/clerk-{year}.txt').write_text(text);section=text[text.index('ARKANSAS'):];section=section[:section.index('CALIFORNIA')]
  matches={}
  for name,token in tokens.items():
   line=next(l for l in section.splitlines() if l.strip().startswith(token+' ') or l.strip().startswith(token+'.'));v=int(re.search(r'([\d,]+)\s*$',line)[1].replace(',',''));matches[name]={'votes':v,'literal_line':line}
  state=next(s for s in states if s['lane']==year+'-api' and ('President' in s['contest'] if year=='2024' else s['contest']=='U.S. Senate'))
  if year!='2024':assert {n:r['votes'] for n,r in matches.items()}==state['candidates']
  else:
   party_map={'Republican':'Donald J. Trump/JD Vance','Democratic':'Kamala D. Harris/Tim Walz','Independent':'Robert F. Kennedy, Jr./Nicole Shanahan','Libertarian':'Chase Oliver/Mike ter Maat','Green':'Jill Stein/Rudolph Ware','American Solidarity':'Peter Sonski/Lauren Onak','Prohibition':'Michael Wood/John G. Pietrowski'}
   assert {party_map[n]:r['votes'] for n,r in matches.items()}==state['candidates']
  clerk.append({'year':year,'source_id':'clerk-'+year,'matches':matches,'api_all_candidates_exact':True})
 save('source/clerk-controls.json',clerk);save('source/state-controls.json',states);save('source/county-candidate-balances.json',balances);save('source/full-api-differences.json',diffs)
 # No name-only joining: exact name and vector witness, explicit unmatched source lane.
 ap=[u for u in units if u['lane']=='2024-api'];unmatched=[];matches=[]
 for u in [u for u in units if u['lane']=='2024-xlsx']:
  match=[v for v in ap if u['county_fips']==v['county_fips'] and u['native_name']==v['native_name'] and u['candidates']==v['candidates']]
  if len(match)==1:matches.append({'xlsx_key':u['key'],'api_key':match[0]['key']})
  else:unmatched.append(u)
 save('source/native-name-vector-matches.json',{'basis':'exact same-year literal county/name and entire candidate vector; no legal crosswalk','matched':matches,'unmatched':unmatched})
 save('source/checks-summary.json',{'state_candidate_controls':len(states),'county_controls':len(balances),'all_exact':True,'pdf_cells':525,'full_api_differing_fields_all_selected_contests':len(diffs),'primary_native_exact_matches':len(matches),'unmatched':len(unmatched),'method_totals':dict(methods)})
 print('source checks pass',len(states),len(diffs),len(unmatched))
if __name__=='__main__':main()
