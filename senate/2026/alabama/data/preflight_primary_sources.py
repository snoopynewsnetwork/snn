"""Original PDF county controls with explicit visual OCR repairs and missing literals."""
from pathlib import Path
import gzip,hashlib,json,re,subprocess,tempfile
DATA=Path(__file__).resolve().parent;NEWS=DATA/'news'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 manifest=json.loads((NEWS/'manifest.json').read_bytes());tables={};pins=[]
 specs={2024:([5,6],6,[772412,1462616,12075,4319,4930,8738]),2022:([4,5],7,[957534,178660,8103,436746,942154,32879,2459]),2020:([3,4],7,[849624,1441170,25176,7312,920478,1392076,3891])}
 for year,(pages,width,state) in specs.items():
  source=next(r for r in manifest if r['id']==f'sos-{year}-canvass-original');stored=(NEWS/source['asset']).read_bytes();raw=gzip.decompress(stored)
  assert sha(raw)==source['raw_sha256'] and sha(stored)==source['stored_sha256'] and len(stored)<40000000
  pins.append({'id':source['id'],'url':source['url'],'original_bytes':len(raw),'raw_sha256':sha(raw),'stored_bytes':len(stored),'stored_sha256':sha(stored)})
  rows=[];repairs=[];texts=[]
  with tempfile.TemporaryDirectory() as tmp:
   pdf=Path(tmp)/'source.pdf';pdf.write_bytes(raw)
   info=subprocess.check_output(['pdfinfo',str(pdf)],stderr=subprocess.PIPE).decode();pagecount=int(re.search(r'Pages:\s+(\d+)',info)[1])
   assert pagecount=={2024:207,2022:353,2020:102}[year]
   for page in pages:
    result=subprocess.run(['pdftotext','-layout','-f',str(page),'-l',str(page),str(pdf),'-'],capture_output=True,check=True)
    text=result.stdout.decode();texts.append({'page_1based':page,'text':text,'parser_stderr':result.stderr.decode()})
    for line_num,line in enumerate(text.splitlines(),1):
     mm=re.match(r'^\s*(.*?)\s{2,}([\d,]+(?:\s+(?:[\d,]+|[-‐]))*)\s*$',line)
     if not mm:continue
     words=mm[2].split()
     if any(s not in ['-','‐'] and not re.fullmatch(r'\d[\d,]*',s) for s in words):continue
     name=mm[1];values=[None if s in ['-','‐'] else int(s.replace(',','')) for s in words]
     if len(values)<width-1:continue
     if name in ['Total','!Total'] and (year,page)==(2022,5):name='Henry';repairs.append({'page':page,'line_1based':line_num,'kind':'visual_label','raw_label':'Total with detached preceding Henry','verified_printed_label':'Henry','values_unchanged':True})
     elif name in ['Total','!Total']:assert values==state;continue
     alias={'Uefferson':'Jefferson','ilalladega':'Talladega','!Tallapoosa':'Tallapoosa','il uscaloosa':'Tuscaloosa','1walker':'Walker','1wilcox':'Wilcox','St_ Clair':'St. Clair'}
     raw_name=name
     if name in alias:name=alias[name];repairs.append({'page':page,'line_1based':line_num,'kind':'visual_county_label','raw_label':raw_name,'verified_printed_label':name})
     if year==2024 and name=='Wilcox':assert values==[3449,1793,15,3,3];values.insert(3,None);repairs.append({'page':page,'line_1based':line_num,'kind':'blank_column_alignment','county':'Wilcox','field':'Jill Stein','value':None,'source_literal':'blank; not0'})
     if year==2022 and name=='Washington':assert len(values)==6;values.append(None);repairs.append({'page':page,'line_1based':line_num,'kind':'trailing_blank','county':'Washington','field':'Senate Write-In','value':None,'source_literal':'blank; not0'})
     assert len(values)==width,(year,name,values)
     rows.append({'county_literal':name,'embedded_text_label':raw_name,'PDF_page_1based':page,'text_line_1based':line_num,'raw_text_line':line,'counts':values,'value_status':['missing_source_literal' if v is None else 'numeric' for v in values]})
  if year==2024:
   for name,page,values in [('Hale',5,[3868,3369,30,10,13,15]),('Winston',6,[884,10191,36,8,10,20])]:
    assert not any(r['county_literal']==name for r in rows)
    rows.append({'county_literal':name,'embedded_text_label':None,'PDF_page_1based':page,'text_line_1based':None,'raw_text_line':None,'counts':values,'value_status':['visual_numeric']*6})
    repairs.append({'page':page,'kind':'full_visual_row','county':name,'counts':values,'reason':'Embedded PDF OCR damaged; complete original page visually inspected, no residual-derived value.'})
  assert len(rows)==67 and len({r['county_literal']for r in rows})==67,(year,len(rows))
  known=[sum(r['counts'][i]for r in rows if r['counts'][i] is not None)for i in range(width)]
  assert known==state,(year,known,state)
  tables[str(year)]={'source_id':source['id'],'page_count':pagecount,'candidate_column_scope':{2024:['Kamala D. Harris (D)','Donald J. Trump (R)','Robert F. Kennedy Jr. (I)','Jill Stein (I)','Chase Oliver (I)','Write-In'],2022:['Will Ainsworth (R) LieutenantGovernor','Ruth Page-Nelson (L) LieutenantGovernor','Write-In LieutenantGovernor','Will Boyd (D) Senate','Katie Britt (R) Senate','John Sophocleus (L) Senate','Write-In Senate'],2020:['Joseph R. Biden (D) President','Donald J. Trump (R) President','Jo Jorgensen (I) President','Write-In President','Doug Jones (D) Senate','Tommy Tuberville (R) Senate','Write-In Senate']}[year],'state_controls':state,'known_county_sums':known,'missing_numeric_cells':sum(v is None for r in rows for v in r['counts']),'county_rows':rows,'explicit_visual_repairs':repairs,'complete_relevant_page_texts':texts}
 out={'status':'pass_county_preflight_with_explicit_visual_repairs_and_missing_values_not_priority_acceptance','source_pins':pins,'tables':tables,'scope':'2024president priority (no2024Senate);2022other-seat Senate midterm;2020same-seat Senate. All67county controls; no native/current geography or candidate-method coverage established.','qualification':'Full PDF originals preserved once. Missing blank/dash cells stayNone even when known sums equal printed footer; no inferred0 or valid/named write-in allocation. Embedded OCR and printed source labels are distinct. Actual question workers must independently verify all original candidate/scope/county/native/statistical fields, current ballot/rules and exact priority.'}
 previews=[]
 for p in sorted((NEWS/'previews').glob('*.png')):previews.append({'path':str(p.relative_to(DATA)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size})
 out['visually_inspected_page_previews']=previews
 (DATA/'coordinator-primary-preflight.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:{'county_rows':len(t['county_rows']),'state':t['state_controls'],'missing_cells':t['missing_numeric_cells'],'visual_repairs':len(t['explicit_visual_repairs'])}for k,t in tables.items()}))
if __name__=='__main__':main()
