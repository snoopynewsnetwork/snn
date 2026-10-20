#!/usr/bin/env python3
"""Independent peer agreement on required supplemental field scopes; read-only captures."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import csv,json,hashlib,collections
D=Path(__file__).resolve().parent;X=D/'extracts';P=D/'peer/supplement-v1/extracted'
def read(n):return json.loads((X/n).read_text())
def csvread(n):return list(csv.DictReader((P/n).open()))
def n(v):return int(str(v).replace(',','')) if v not in ['',None] else None
def main():
 checks=[];diff=[]
 def eq(scope,key,a,b):
  if a!=b:diff.append({'scope':scope,'key':key,'own':a,'peer':b})
 scopes={'ed':'election_district','rd':'representative_district','county':'county','state':'statewide'}
 own=read('participation-totals.json');peer=csvread('participation-totals.csv')
 def okey(r):return (r['year'],scopes[r['level']],(r['county'] or '').upper(),r['native_key'].upper())
 def pkey(r):return(int(r['year']),r['scope'],r['county'].upper(),r['geo_key'].upper())
 a={okey(r):r for r in own};b={pkey(r):r for r in peer};eq('participation keys','all',set(a),set(b));shared=set(a)&set(b)
 for k in shared:
  o=a[k];p=b[k]
  for group,prefix in [('Democrat','democrat_registration'),('Republican','republican_registration'),('All Others','all_other_registration'),('Total','total')]:
   for field in ['registered','voted','percentage_raw']:eq('participation '+group+' '+field,k,o['values'][group][field],p[prefix+'_'+field] if field=='percentage_raw' else n(p[prefix+'_'+field]))
  eq('participation raw line',k,o['raw_line'].rstrip('\r\n'),p['raw_line']);eq('participation start',k,o['source_char_start'],int(p['source_char_start']));eq('participation end exclusive including newline',k,o['source_char_end'],int(p['source_char_end']));eq('participation source line',k,o['source_line'],int(p['source_line']))
 checks.append({'scope':'four party-group Registered/Voted/percentage + exact raw line, start and end including newline, line number; all county/RD/ED/state total rows','matched_rows':len(shared)})
 own=read('registration-november.json');peer=[r for r in csvread('monthly-registration-native.csv') if r['kind']=='RD'];a={(r['year'],r['native_key']):r for r in own};b={(int(r['year']),r['geo_key']):r for r in peer};eq('monthly RD native keys','all',set(a),set(b))
 for k in set(a)&set(b):
  o=a[k];p=b[k];eq('monthly county',k,o['county'],p['county'].upper());eq('monthly total (missing preserved)',k,o['registered'],n(p['registered_total']))
  for field,pk in [('DEMOCRATIC','registered_democratic'),('REPUBLICAN','registered_republican'),('OTHERS','registered_others')]:eq('monthly party '+field,k,n(o['raw_fields'][field]),n(p[pk]))
 checks.append({'scope':'monthly RD-native registration totals, all party counts and null fields; county identity','matched_rows':len(a)})
 own=read('monthly-registration-controls.json');peer=[r for r in csvread('monthly-registration-controls.csv') if r['kind']=='RD']
 def canon(k):return 'STATE' if k in ['Grand Total','Statewide','State'] else k.upper()
 a={(r['year'],canon(r['geography'])):r for r in own};b={(int(r['year']),canon(r['geo_key'])):r for r in peer};eq('monthly county/state keys','all',set(a),set(b))
 for k in set(a)&set(b):eq('monthly county/state counts',k,a[k]['values']['Grand Total'],int(b[k]['registered']))
 checks.append({'scope':'monthly RD county/state registered stock controls','matched_rows':len(a)})
 own=read('writein-rows.json');peer=csvread('writeins.csv')
 def wk(y,office,geo,candidate):return (int(y),office,geo.upper(),candidate)
 a={wk(r['year'],r['office_key'],r['county'],r['candidate']):r for r in own};b={wk(r['year'],r['office_key'],r['geo_key'],r['candidate']):r for r in peer};eq('WI identity set','all',set(a),set(b))
 for k in set(a)&set(b):
  for f,pf in [('Machine','machine'),('Absentee','absentee'),('Early Voting','early'),('Provisional','provisional'),('Grand Total','total')]:eq('WI '+f,k,a[k]['values'][f],n(b[k][pf]))
  eq('WI page',k,a[k]['page'],int(b[k]['page']))
 checks.append({'scope':'every required named WI identity/county/method/page/total, blank cells null','matched_rows':len(a)})
 cov=read('native-coverage.json');a={(r['year'],r['native_key']):(r['parent']['county'] if r['parent'] else None) for r in cov};rp=json.loads((P/'resolved-parent-evidence.json').read_text());count=0
 for r in rp:
  k=(r['year'],r['geo_key']);county=r.get('county');eq('resolved same-year county parent',k,a[k],county.upper() if county else None);count+=1
 checks.append({'scope':'resolved same-year native county parent per required contest, including null president-only2020','matched_rows':count})
 # JSON supports deterministic serializable errors, including key sets.
 if diff:
  for d in diff:
   for k in ['own','peer']:
    if isinstance(d[k],set):d[k]=sorted(d[k])
 out={'peer_actual_id':'4724b2aa-c338-4708-8044-c4b606bfaaeb','pass':not diff,'checks':checks,'differences':diff,'capture_manifest_sha256':hashlib.sha256((P.parent/'capture-manifest.json').read_bytes()).hexdigest(),'boundary_scope':'historical literal identities only; no geometry/current approval'}
 (D/'peer/supplement-reconciliation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':checks,'differences':diff[:3]}));assert not diff
if __name__=='__main__':main()
