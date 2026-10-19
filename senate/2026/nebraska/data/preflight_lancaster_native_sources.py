"""Read the complete actual Lancaster PDF, retaining source method partitions."""
from pathlib import Path
import collections,gzip,hashlib,json,re,subprocess,tempfile

DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
METHODS=['TOTAL','Election Day','Early Voting','Provisional']
CONTESTS={'US President':['Rep Trump/Vance','Dem Harris/Walz','Lib Oliver/ter Maat','Lmn West/Abdullah','Pet Stein/Kpadenou'],
          'US Senator 6 YR':['Rep Deb Fischer','Pet Dan Osborn'],
          'US Senator 2 YR':['Rep Pete Ricketts','Dem Preston Love Jr.']}
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(DATA.parent)),'bytes':len(b),'sha256':sha(b)}
def row(line):
 m=re.fullmatch(r'\s*(.*?)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s*',line)
 return None if not m else {'label_literal':m[1],'counts':[int(m[i].replace(',',''))for i in range(2,6)],'raw_line':line}
def main():
 manifest=json.loads((NEWS/'manifest.json').read_bytes())
 source=next(r for r in manifest if r['id']=='county-lancaster-2024-final-precinct-pdf-actual-archive')
 stored=(NEWS/source['asset']).read_bytes();raw=gzip.decompress(stored)
 assert sha(stored)==source['stored_sha256']and sha(raw)==source['raw_sha256']
 assert raw.startswith(b'%PDF-')and raw.rstrip().endswith(b'%%EOF')
 with tempfile.NamedTemporaryFile(suffix='.pdf')as pdf:
  pdf.write(raw);pdf.flush();info=subprocess.run(['pdfinfo',pdf.name],check=True,capture_output=True).stdout.decode()
  assert re.search(r'^Pages:\s+1431$',info,re.M)
  text=subprocess.run(['pdftotext','-layout',pdf.name,'-'],check=True,capture_output=True).stdout
  previews=[]
  for page in [1,1431]:
   target=NEWS/'previews'/f'county-lancaster-2024-actual-original-p{page}'
   target.parent.mkdir(exist_ok=True)
   subprocess.run(['pdftoppm','-f',str(page),'-singlefile','-r','100','-png',pdf.name,str(target)],check=True,capture_output=True)
   previews.append(pin(target.with_suffix('.png')))
 txt=NEWS/'extracts/county-lancaster-2024-final-precinct-pdf.txt.gz'
 if txt.exists():assert gzip.decompress(txt.read_bytes())==text
 else:txt.write_bytes(gzip.compress(text,mtime=0))
 pp=text.decode().split('\f');assert not pp[-1].strip();pages=pp[:-1];assert len(pages)==1431
 contexts=[];stats=[];alllabels=[];clocks=collections.Counter()
 for index,page in enumerate(pages,1):
  label=re.search(r'Lancaster County, Nebraska\s*\n\s*\n([^\n]+)',page)[1].strip();alllabels.append(label)
  foot=re.search(r'Precinct Summary - (.+?)\s+([\d,]+) of 1,431',page);assert foot and int(foot[2].replace(',',''))==index
  clocks[foot[1].strip()]+=1
  lines=page.splitlines()
  if re.search(r'^Statistics\s+TOTAL',page,re.M):
   block=page.split('Statistics',1)[1].split('US President',1)[0]
   counted={v['label_literal']:v for line in block.splitlines()if(v:=row(line))}
   assert set(counted)=={'Ballots Cast - Total','Ballots Cast - Blank'}
   reg=re.search(r'^Registered Voters - Total\s+(\d[\d,]*)\s*$',page,re.M)
   rate=re.search(r'^Voter Turnout - Total\s+([\d.]+%)\s*$',page,re.M)
   assert reg and rate
   for v in counted.values():assert v['counts'][0]==sum(v['counts'][1:])
   stats.append({'literal_source_unit':label,'actual_pdf_page':index,'source_rows':counted,
    'registered_total':int(reg[1].replace(',','')),'registration_method_counts':None,
    'source_printed_turnout_percent':rate[1],'raw_statistics_block':block})
  starts=[i for i,line in enumerate(lines)if line.strip()in CONTESTS]
  for start in starts:
   name=lines[start].strip();end=next((i for i in range(start+1,len(lines))if re.match(r'^\s*Contest Totals\s+',lines[i])),None)
   assert end is not None
   block=lines[start:end+1];parsed=[v for line in block if(v:=row(line))]
   fields={v['label_literal']:v for v in parsed};assert len(fields)==len(parsed)
   required=CONTESTS[name]+['Write-In Totals','Not Assigned','Total Votes Cast','Overvotes','Undervotes','Contest Totals']
   assert set(fields)==set(required),(index,name,set(fields)-set(required),set(required)-set(fields))
   for field in fields.values():assert field['counts'][0]==sum(field['counts'][1:]),(index,field)
   for j in range(4):
    assert sum(fields[c]['counts'][j]for c in CONTESTS[name]+['Write-In Totals'])==fields['Total Votes Cast']['counts'][j]
    assert fields['Not Assigned']['counts'][j]==fields['Write-In Totals']['counts'][j]
    assert sum(fields[c]['counts'][j]for c in ['Total Votes Cast','Overvotes','Undervotes'])==fields['Contest Totals']['counts'][j]
   contexts.append({'source_id':source['id'],'raw_source_sha256':source['raw_sha256'],
     'actual_pdf_page':index,'literal_source_unit':label,'literal_contest_name':name,
     'method_columns_as_printed':METHODS,'fields':fields,'raw_original_contest_block':'\n'.join(block),
     'source_footer_clock_literal':foot[1].strip(),'source_footer_clock_zone':None})
 assert len(set(alllabels))==199 and len(stats)==199 and len({s['literal_source_unit']for s in stats})==199
 assert collections.Counter(c['literal_contest_name']for c in contexts)=={'US President':199,'US Senator 6 YR':198,'US Senator 2 YR':198}
 totals={}
 for contest in CONTESTS:
  selected=[c for c in contexts if c['literal_contest_name']==contest]
  totals[contest]={field:[sum(c['fields'][field]['counts'][j]for c in selected)for j in range(4)]for field in selected[0]['fields']}
 expected=json.loads((DATA/'coordinator-primary-preflight.json').read_bytes())['tables']
 for contest,table in [('US Senator 2 YR','2024_Senate_ClassII_two_year'),('US Senator 6 YR','2024_Senate_ClassI_six_year')]:
  actual=[totals[contest][n][0]for n in CONTESTS[contest]]
  if contest=='US Senator 6 YR':actual.append(totals[contest]['Write-In Totals'][0])
  assert actual==expected[table]['county_rows']['Lancaster']['votes']
 specialonly=set(c['literal_source_unit']for c in contexts if c['literal_contest_name']=='US President')-set(c['literal_source_unit']for c in contexts if c['literal_contest_name']=='US Senator 2 YR')
 assert specialonly=={'New or Former Resident'}
 nr=next(c for c in contexts if c['literal_source_unit']=='New or Former Resident')
 assert nr['fields']['Contest Totals']['counts']==[1,0,1,0]
 stats_index={s['literal_source_unit']:s for s in stats}
 for c in contexts:assert c['fields']['Contest Totals']['counts']==stats_index[c['literal_source_unit']]['source_rows']['Ballots Cast - Total']['counts']
 target=NEWS/'extracts/lancaster-2024-selected-native-original-positions.jsonl.gz'
 target.write_bytes(gzip.compress(b''.join((json.dumps(c,separators=(',',':'))+'\n').encode()for c in contexts),mtime=0))
 output={'status':'pass_complete_actual_Lancaster_original_with_source_scoped_native_method_controls',
  'source':source,'actual_PDF_pages':1431,'complete_text':pin(txt),'preview_pages':previews,
  'selected_native_contest_contexts':len(contexts),'source_unit_labels':list(dict.fromkeys(alllabels)),
  'method_column_labels':METHODS,'source_footer_clocks':dict(clocks),'county_source_candidate_method_totals':totals,
  'state_canvass_Senate_candidate_controls_checked':5,'selected_native_original_positions':pin(target),
  'unit_statistics':stats,'presidential_only_source_observation':nr,
  'qualification':'Complete actual final1431-page county PDF recovered from its observed archived URL; current direct403 and old state-app archive truncation remain separate evidence.198 two-year Senate,198 six-year Senate and199 presidential source contexts retain all original TOTAL/ElectionDay/EarlyVoting/Provisional counts. A separate New or Former Resident row has one EarlyVoting presidential ballot and no Senate section; no Senate zero is invented. All method/native/contest arithmetic closes, and five Senate candidate controls match retained state canvass. Generic Write-In Totals and nested Not Assigned are overlapping scopes, never added. Registration is sourceTOTAL only, not method-allocated. Literal unit names are not approved ENR, BIFF, map, cross-year or current reporting IDs. Printed3:34PM and PDF metadata clocks stay distinct; no cadence/correction chronology or current geographic/dispatch approval follows.'}
 p=DATA/'coordinator-lancaster-native-preflight.json';p.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'actual_pages':1431,'native_contexts':len(contexts),'source_labels':199,'Senate_candidate_controls':5,'Senate2_named':[totals['US Senator 2 YR'][n][0]for n in CONTESTS['US Senator 2 YR']], 'presidential_only':nr['fields']['Contest Totals']['counts'],'output_pin':pin(p)}))

if __name__=='__main__':main()
