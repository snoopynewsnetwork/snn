"""Assessment previews never replace whole original bodies or complete recursive structure assets."""
from pathlib import Path
import json,gzip,re,sys
sys.dont_write_bytecode=True
from inspect_pages import body
P=Path(__file__).resolve().parent
def plain(s):return re.sub(r'\s+',' ',re.sub('<[^>]*>',' ',str(s))).strip()
def main():
 req={f.stem:json.loads(f.read_bytes()) for f in (P/'requests').glob('*.json')};out=[]
 for n,r in req.items():
  if not n.endswith('en-electionsettings-json'):continue
  v=json.loads(body(r));web=v.get('pagesettings',{}).get('web',{});base=r['final_url'].rsplit('/en/',1)[0];summ=next((q for q in req.values() if q.get('final_url')==base+'/en/summary.json'),None);sv=json.loads(body(summ)) if summ else None
  vt=next((q for q in req.values() if q.get('final_url')==base+'/vt.json'),None);vto=json.loads(body(vt)) if vt else None
  a={'request_id':n,'county_literal':v.get('entityname'),'whole_settings_receipt':'requests/'+n+'.json','title_raw':web.get('pagetitle'),'subtitle_raw':web.get('pagesubtitle'),'website_updated_at_literal':v.get('websiteupdatedat'),'timezoneoffset_raw':v.get('settings',{}).get('timezoneoffset'),'isdaylightsaving_raw':v.get('settings',{}).get('isdaylightsaving'),'source_timezone_policy':'preserve explicit websiteupdatedat zone; raw config offset is not independently applied to local deadline conversions','methods_actual_order':vto.get('Types') if vto else None,'whole_summary_receipt':('requests/'+summ['id']+'.json') if summ else None,'whole_method_receipt':('requests/'+vt['id']+'.json') if vt else None,'all_contest_count':len(sv) if isinstance(sv,list) else None,'full_Senate_contest_objects_preview':[x for x in sv if 'senat' in str(x.get('C','')).lower()] if isinstance(sv,list) else None,'completion_legends':{k:x for k,x in web.items() if 'legend_' in k and any(y in k for y in ['certified','complete','reporting'])},'genuine_November_counts_admitted':False,'exact_eligible_remaining_pool':None,'measured_publication_cadence':None}
  if 'primary' in plain(str(a['title_raw'])+' '+str(a['subtitle_raw'])).lower():a['stage_assessment']='2026-06-02 primary; excluded from November returns'
  elif 'General' in plain(a['title_raw']) and 'November 3, 2026' in plain(a['subtitle_raw']):a['stage_assessment']='actual explicitly dated November3 general template; all retrieved candidate counts zero; not genuine returns'
  else:a['stage_assessment']='source identity requires review; not admitted'
  out.append(a)
 (P/'payload-assessments.json').write_text(json.dumps(sorted(out,key=lambda a:(str(a['county_literal']),a['request_id'])),indent=2,ensure_ascii=False)+'\n')
 print([(a['county_literal'],a['stage_assessment'],a['website_updated_at_literal']) for a in out])
if __name__=='__main__':main()
