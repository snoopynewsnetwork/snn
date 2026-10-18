#!/usr/bin/env python3
"""Independently reconcile source candidate, native and method scopes; no native-name joins."""
import collections,functools,gzip,hashlib,io,json,zipfile,xml.etree.ElementTree as ET
from acquire import ROOT
T=ROOT.parent/'turnout';c=json.loads((T/'priority-set.json').read_text());ids=json.loads((ROOT/'historical-identities.json').read_text())
def ptr(d,p):
 for k in p.strip('/').split('/'):d=d[int(k)] if isinstance(d,list) else d[k]
 return d
@functools.lru_cache(12)
def doc(sid,group):
 o=c[group][sid];b=gzip.decompress((T/o['body_path']).read_bytes())
 if 'zip_member' in o:return ET.fromstring(zipfile.ZipFile(io.BytesIO(b)).read(o['zip_member']))
 return json.loads(b)
maps={
 '2024-pres':{'CON Randall A Terry/Stephen E Broden':8261,'UNC Cornel West/Melina Abdulla':8260,'GRN Jill Stein/Rudolph Butch Ware':6882,'REP Donald J Trump/JD Vance':27,'LIB Chase Oliver/Mike ter Maat':8258,'DEM Kamala D Harris/Tim Walz':7553,'WRK Claudia De La Cruz/Karina Garcia':8259},
 '2020-senate':{'CON Bill Bledsoe':2268,'REP Lindsey Graham':3254,'DEM Jaime Harrison':3255,'Write-In':6},
 '2022-senate':{'REP Tim Scott':3536,'DEM Krystle Matthews':870,'Write-In':6},
 '2022-governor':{'REP Henry McMaster/Pamela Evette':3471,'LIB Bruce Reeves/Jessica Ethridge':3472,'DEM Joe Cunningham/Tally Parham Casey':3473,'Write-In':6}}
aliases={'2020-senate': {'Write-in': 6}, '2022-governor': {'DEM Joe Cunningham': 3473, 'DEM Joe Cunningham/Tally Parham': 3473, 'DEM Joe Cunningham/Tlly Parham Casey': 3473, 'Dem Joe Cunningham/Tally Parham Casey': 3473, 'LIB Bruce Reeves': 3472, 'LIB Bruce Reeves/ Jessica Ethridge': 3472, 'REP Henry McMaster': 3471}, '2024-pres': {'CON Randall A Terry': 8261, 'CON Randall A Terry /Stephen E Broden': 8261, 'CON Randall A Terry/ Stephen E Broden': 8261, 'DEM Kamala D Harris': 7553, 'DEM Kamala D Harris/  Tim Walz': 7553, 'DEM Kamala D Harris/ Tim Walz': 7553, 'GRN Jill Stein': 6882, 'GRN Jill Stein/ Rudolph Butch Ware': 6882, 'LIB Chase Oliver': 8258, 'LIB Chase Oliver/ Mike ter Maat': 8258, 'LIB Chase Oliver/Miket ter Maat': 8258, 'REP Donald J Trump': 27, 'REP Donald J Trump/ JD Vance': 27, 'UNC Cornel Wes/ Melina Abdullat': 8260, 'UNC Cornel West': 8260, 'UNC Cornel West / Melina Abdulla': 8260, 'UNC Cornel West/ Melina Abdulla': 8260, 'UNC Cornel West/Melina Abdula': 8260, 'UNC Cornel Westt/ Melina Abdulla': 8260, 'WRK Claudia De La Cruz': 8259, 'WRK Claudia De La Cruz/ Karina Garcia': 8259}}
literal_variants=[]
summary=[];unmatched=[];method_checks=[];jsonchecks=[];source_clock=[];state_objects={};candidate_differences=[]
for label,direct_mapping in maps.items():
 mapping={**direct_mapping,**aliases.get(label,{})}
 year=label[:4];sr=doc('legacy'+year+'-detailxml','legacy_source_observations');title={'2024-pres':'President and Vice President','2020-senate':'U.S. Senate','2022-senate':'U.S. Senate','2022-governor':'Governor and Lieutenant Governor'}[label];sn=next(x for x in sr.findall('Contest') if x.attrib['text']==title)
 db=doc(label+'-combined','source_observations')['data']['contestGranularData'];dbrow={x['candidateId']:x for x in db['divisions']['granularRow']}
 state_objects[label]={'source_id':'legacy'+year+'-detailxml','contest_attributes':dict(sn.attrib),'choice_attributes':[dict(x.attrib) for x in sn.findall('Choice')],'election_turnout':dict(sr.find('ElectionVoterTurnout').attrib),'clock':sr.findtext('Timestamp'),'DB_state_combined_rows':db['divisions']['granularRow'],'DB_method_state_rows':doc(label+'-methods','source_observations')['data']['contestGranularData']['divisions']['granularRow']}
 for choice in sn.findall('Choice'):
  raw=dict(choice.attrib);cid=mapping[raw['text']];assert int(raw['totalVotes'])==dbrow[cid]['votes'];summary.append({'contest':label,'original_source_id':'legacy'+year+'-detailxml','original_choice':raw,'DB_candidate':next(x for x in db['candidates'] if x['candidateId']==cid),'DB_parties':db['parties'],'identity_scope':'explicit candidate/slate comparison only; DB and ENR identifiers remain distinct'})
 for county in c['counties']:
  units=county['original_enr_combined_json_constituents'][label];first=units[0];ss=first['summary_source_id'];s=ptr(doc(ss,'original_combined_json_observations'),first['summary_source_pointer']);detail=ptr(doc(first['source_id'],'original_combined_json_observations'),first['source_pointer']);vectors=detail['V'];assert len(vectors)==len(detail['P'])
  if 'T' in detail:assert len(vectors)==len(detail['T'])
  for i,v in enumerate(vectors):
   if 'T' in detail:assert sum(v)==detail['T'][i]
  assert [sum(v[i] for v in vectors) for i in range(len(s['V']))]==s['V'];assert 'T' not in s or sum(s['V'])==s['T'];assert len(s['CH'])==len(s['V'])==len(s['P'])
  dbcounty=next(x for x in db['divisions']['children'] if x['division']['id']==county['native_county_id']);rawdb={x['candidateId']:x for x in dbcounty['granularRow']}
  for name,value in zip(s['CH'],s['V']):
   if name not in direct_mapping:literal_variants.append({'contest':label,'source_id':ss,'county':county['name'],'raw_label':name,'votes':value,'explicit_equivalence_to_DB_candidate':mapping.get(name)})
   if name not in mapping:unmatched.append({'contest':label,'county':county['name'],'summary_source_id':ss,'raw_name':name,'raw_votes':value})
   else:assert value==rawdb[mapping[name]]['votes']
  jsonchecks.append({'contest':label,'county':county['name'],'summary_source_id':ss,'detail_source_id':first['source_id'],'summary_pointer':first['summary_source_pointer'],'detail_pointer':first['source_pointer'],'native_rows':len(vectors),'candidate_cells':sum(len(v) for v in vectors),'total':sum(s['V']),'source_total':s.get('T'),'source_total_present':'T' in s,'raw_Eid':detail['Eid'],'raw_Cid':detail['Cid'],'summary_PR':s.get('PR'),'summary_TP':s.get('TP')})
  xmlsid='legacy'+year+'-county-'+county['name'].lower();o=c['legacy_source_observations'].get(xmlsid)
  if not o or 'body_path' not in o:continue
  xr=doc(xmlsid,'legacy_source_observations');key=county['original_enr_constituents'][label][0]['contest_key'];xn=next(x for x in xr.findall('Contest') if x.attrib['key']==key)
  for ch in xn.findall('Choice'):
   labelraw=ch.attrib['text'];vt=[]
   if labelraw not in direct_mapping:literal_variants.append({'contest':label,'source_id':xmlsid,'county':county['name'],'raw_choice':dict(ch.attrib),'explicit_equivalence_to_DB_candidate':mapping.get(labelraw)})
   for typ in ch.findall('VoteType'):
    vals=[int(n.attrib['votes']) for n in typ.findall('Precinct')];v=int(typ.attrib['votes']);assert v==sum(vals);vt.append({'raw_attributes':dict(typ.attrib),'native_sum':sum(vals),'native_positions':len(vals)})
   total=sum(x['native_sum'] for x in vt);assert total==int(ch.attrib['totalVotes'])
   method_checks.append({'contest':label,'county':county['name'],'source_id':xmlsid,'raw_contest_attributes':dict(xn.attrib),'raw_choice_attributes':dict(ch.attrib),'method_controls':vt,'total':total})
   if labelraw not in mapping:unmatched.append({'contest':label,'county':county['name'],'XML_source_id':xmlsid,'raw_choice':dict(ch.attrib)})
   else:assert total==rawdb[mapping[labelraw]]['votes']
# VHM and election-wide controls: retain known2022 registration residual independently.
reg=[]
for year in ['2024','2020','2022']:
 sr=doc('legacy'+year+'-detailxml','legacy_source_observations');state=dict(sr.find('ElectionVoterTurnout').attrib);state_counties=[dict(x.attrib) for x in sr.find('ElectionVoterTurnout').find('Counties').findall('County')];assert len(state_counties)==46;reg_delta=sum(int(x['totalVoters']) for x in state_counties)-int(state['totalVoters']);ballot_delta=sum(int(x['ballotsCast']) for x in state_counties)-int(state['ballotsCast']);assert ballot_delta==0
 if year=='2022':assert reg_delta==40
 rows=[]
 for county in c['counties']:
  sid='legacy'+year+'-county-'+county['name'].lower();o=c['legacy_source_observations'].get(sid)
  if o and 'body_path' in o:
   r=doc(sid,'legacy_source_observations');rows.append({'county':county['name'],'source_id':sid,'raw_control':dict(r.find('VoterTurnout').attrib),'timestamp':r.findtext('Timestamp')})
 reg.append({'year':year,'state_source_id':'legacy'+year+'-detailxml','state_control':state,'state_original_all46_county_controls':state_counties,'state_county_registration_residual':reg_delta,'state_county_ballot_residual':ballot_delta,'county_XML_controls':rows,'county_XML_coverage':len(rows),'incomplete_XML_scope_no_fill':len(rows)!=46})
for n,d in [('original-candidate-reconciliation.json',summary),('original-json-reconciliation.json',jsonchecks),('original-method-reconciliation.json',method_checks),('original-state-controls.json',state_objects),('original-registration-controls.json',reg),('unmatched-source-candidate-labels.json',unmatched),('literal-candidate-variants.json',literal_variants),('explicit-candidate-equivalences.json',{'by_contest':aliases,'scope':'Manually reviewed literal candidate/slate variants within the pinned contest/county/party; all raw objects retained; no precinct/method/cross-year/November equivalence'})]: (ROOT/n).write_text(json.dumps(d,indent=2)+'\n')
print('JSON groups',len(jsonchecks),'XML candidate-method groups',len(method_checks),'unmatched exact candidate labels',len(unmatched))
