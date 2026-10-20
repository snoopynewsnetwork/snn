#!/usr/bin/env python3
from pathlib import Path
import csv,json
P=Path(__file__).resolve().parent;F=P/'peer/supplement'

def main():
 checks=[]
 def test(n,b):assert b,n;checks.append(n)
 own=list(csv.DictReader((P/'extracted/participation-totals.csv').open()));peer=json.loads((F/'participation-totals.json').read_text());test('total-only rows1631',len(own)==len(peer)==1631)
 om={(int(r['year']),r['source_line']):r for r in own}
 for r in peer:
  o=om[(r['year'],str(r['source_line']))];test('party-group participation '+str((r['year'],r['source_line'])),all(int(o[p+'_'+f])==r['values'][q][f] for p,q in [('democrat_registration','Democrat'),('republican_registration','Republican'),('all_other_registration','All Others'),('total','Total')] for f in ['registered','voted']) and all(o[p+'_percentage_raw']==r['values'][q]['percentage_raw'] for p,q in [('democrat_registration','Democrat'),('republican_registration','Republican'),('all_other_registration','All Others'),('total','Total')]) and o['raw_line']==r['raw_line'].rstrip('\r\n') and int(o['source_char_start'])==r['source_char_start'] and int(o['source_char_end'])==r['source_char_end'])
 ownh=json.loads((P/'extracted/participation-hierarchy.json').read_text());ph=json.loads((F/'historical-hierarchy.json').read_text());test('1491 explicit native hierarchy keys and parents',sorted((r['year'],r['geo_key'],r['county'].upper(),r['representative_district'].zfill(2)) for r in ownh)==sorted((r['year'],r['native_key'],r['county'],r['rd'].zfill(2)) for r in ph))
 wi=list(csv.DictReader((P/'extracted/writeins.csv').open()));pw=json.loads((F/'writein-rows.json').read_text());wm={(int(r['year']),r['office_key'],r['geo_key'].upper(),r['candidate']):r for r in wi}
 test('43 writein rows',len(wi)==len(pw)==43)
 for r in pw:
  c=(r.get('county') or 'State').upper();o=wm[(r['year'],r['office_key'],c,r['candidate'])]
  test('writein methods/nulls '+str((r['year'],c,r['candidate'])),all((None if o[a]=='' else int(o[a]))==r['values'][b] for a,b in [('machine','Machine'),('absentee','Absentee'),('early','Early Voting'),('provisional','Provisional'),('total','Grand Total')] if b in r['values']))
 st=json.loads((P/'extracted/district-structure.json').read_text());ps=json.loads((F/'structure-2024.json').read_text());test('537 structure exact parents and footnotes',len(st)==len(ps)==537 and all(r['county'].upper()==ps[r['geo_key']]['county'] and r['footnote']==ps[r['geo_key']]['footnote'] for r in st))
 mn=list(csv.DictReader((P/'extracted/monthly-registration-native.csv').open()));pn=json.loads((F/'registration-november.json').read_text());nm={(int(r['year']),r['geo_key']):r for r in mn if r['kind']=='RD'};test('1477 Nov1 RD rows',len(nm)==len(pn)==1477)
 for r in pn:
  o=nm[(r['year'],r['native_key'])];v=None if o['registered_total']=='' else int(o['registered_total']);test('monthly exact printed native total/null '+str((r['year'],r['native_key'])),v==r['registered'] and o['county'].upper()==r['county'] and all((None if o[a]=='' else int(o[a]))==(None if r['raw_fields'][b]=='' else int(r['raw_fields'][b].replace(',',''))) for a,b in [('registered_democratic','DEMOCRATIC'),('registered_republican','REPUBLICAN'),('registered_others','OTHERS')]))
 mc=list(csv.DictReader((P/'extracted/monthly-registration-controls.csv').open()));pc=json.loads((F/'monthly-registration-controls.json').read_text());mapped={(int(r['year']),r['geo_key'].upper()):int(r['registered']) for r in mc if r['kind']=='RD'}
 for r in pc:
  geo=r['geography'].upper();geo='STATE' if geo in ['GRAND TOTAL','STATEWIDE','STATE'] else geo
  if (r['year'],geo) in mapped:test('monthly printed control '+str((r['year'],geo)),mapped[(r['year'],geo)]==r['values']['Grand Total'])
 out=dict(status='pass',checks_count=len(checks),checks=checks,scope='Independent shared numeric fields and nulls compared across original participation1631 rows/1491EDs,43 writeins,537structure identities,1477Nov1RD rows and printed county/state controls. Different raster/text engines source positions are not equated; original report10699 row/table positions compared separately.')
 (P/'peer/supplement-reconciliation.json').write_text(json.dumps(out,indent=2)+'\n');print(len(checks),'supplemental checks pass')
if __name__=='__main__':main()
