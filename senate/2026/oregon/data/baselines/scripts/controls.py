"""Independent nonadditive presentation/control bindings and raw source method lanes."""
import json,csv,gzip,re
from county import R,js,csvout,text

def main():
 u=json.loads((R/'native-units.json').read_text());ix={(r['source_key'],r['unit_label']):r for r in u if r['contest']=='2024-president'};bindings=[];controls=[]
 for r in u:
  if r['contest']!='2024-president' or r['source_key']=='multnomah-2024-president':continue
  source=r
  if r['source_key']=='multnomah-2024-sovc2':
   source=ix['multnomah-2024-president','Precinct '+r['unit_label']];assert r['candidates']==source['candidates']
   bindings.append({'native_source_key':r['unit_key'],'alternative_source_key':source['unit_key'],'candidate_vectors_equal':True,'additive':False,'ballot_nonvote_controls_from':'PDF alternative; candidate-specific CSV overvote lanes are not ballot overvote counts'})
  c=source['controls'];pick=lambda *ks:next((c[k] for k in ks if k in c),None)
  ballot=pick('ballots_source','Total Ballots Cast');reg=pick('registered_voters_source','Registered Voters');over=pick('Overvotes');under=pick('Undervotes');votes=sum(r['candidates'].values())
  controls.append({'key':r['unit_key'],'county':r['county'],'unit':r['unit_label'],'candidate_source':r['source_key'],'control_source':source['source_key'],'reported_choices':votes,'ballots_source':ballot,'registration_source':reg,'overvotes_source':over,'undervotes_source':under,'balance':None if None in [ballot,over,under] else votes+over+under-ballot})
 assert len(controls)==510 and all(r['balance']==0 for r in controls)
 csvout('known-native-controls.csv',controls);js('source/nonadditive-presentation-bindings.json',bindings)
 methods=[]
 with gzip.open(R/'source/raw-native-rows.jsonl.gz','rt') as f:
  for l in f:
   r=json.loads(l);raw=r['raw'];source=r['source_key']
   if isinstance(raw,dict) and 'rows' in raw:
    for choice in raw['rows']:
     line=choice['raw_line'];pcts=list(re.finditer(r'\d+(?:\.\d+)?%',line));pos=choice['position'];page=text(source).split('\f')[pos['page']-1]
     lanes=[]
     if re.search(r'Vote %\s+AB\s+ED\s+EV',page):
      values=re.findall(r'\d[\d,]*',line[pcts[0].end():]) if pcts else []
      if len(values)==3:lanes=[{'method_literal':m,'votes':int(v.replace(',',''))} for m,v in zip(['AB','ED','EV'],values)]
     elif 'Absentee Voting' in page:
      pair=re.findall(r'(\d[\d,]*)\s+\d+(?:\.\d+)?%',line)
      if len(pair)==2:lanes=[{'method_literal':m,'votes':int(v.replace(',',''))} for m,v in zip(['Absentee Voting','Total'],pair)]
     if lanes:methods.append({'source_key':source,'contest':r['contest'],'unit':r['unit'],'candidate_label_source':choice['label_source'],'position':pos,'lanes':lanes,'additive':False,'raw_line':line})
   elif isinstance(raw,dict) and 'Vote by Mail Votes' in raw:
    methods.append({'source_key':source,'contest':r['contest'],'unit':r['unit'],'candidate_label_source':raw['Choice Name'],'position':r['position'],'lanes':[{'method_literal':m,'votes_literal':raw[k]} for m,k in [('Total','Total Votes'),('Vote by Mail','Vote by Mail Votes')]],'additive':False,'raw_fields':raw})
 js('native-method-lanes.json',methods)
 js('source/control-gaps.json',{'all_statewide_county_candidate_controls':True,'statewide_county_canvass_ballots_cast_under_over_blank_series':None,'reason':'Source-specific native/control scopes are incomplete; statistical returned ballots never substituted for canvass ballots cast. No native allocation of registration or unexplained residuals.','known2024_controls_complete_510':True,'all_other_native_scopes':'Consult every source/county/contest reconciliation and whole-original-page index; OCR/native identity/candidate/method gaps remain unknown.'})
 print(json.dumps({'known_native_controls':len(controls),'balances_zero':True,'alternative_presentations':len(bindings),'parsed_nonadditive_method_records':len(methods)}))
if __name__=='__main__':main()
