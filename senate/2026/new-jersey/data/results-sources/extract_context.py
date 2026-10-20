from pathlib import Path
import json,gzip,re
P=Path(__file__).resolve().parent
def main():
 out=[]
 for n in ['law-context-66','law-context-67','law-context-68','law-context-69','law-context-70','law-context-71','mail-law-context-public']:
  s=json.loads(gzip.decompress((P/'inspection'/f'{n}.json.gz').read_bytes()))['full_text'];ms=list(re.finditer(r'NJSA\s+(19:\d+[A-Z]?-\d+(?:\.\d+)?)(?![\d.])',s))
  for i,m in enumerate(ms):
   end=ms[i+1].start() if i+1<len(ms) else len(s);out.append({'section':m[1],'text':s[m.start():end],'start_text_offset':m.start(),'end_text_offset':end,'source_request_id':n})
 assert len(out)==999;(P/'legal-sections.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 idx=json.loads((P/'structure-index.json').read_bytes());out=[]
 for x in idx:
  if x['request_id'].startswith('periodic') and x.get('structure_asset'):
   o=json.loads(gzip.decompress((P/x['structure_asset']).read_bytes()));t='\n'.join(pg['text'] for pg in o.get('pages',[]));out.append({'request_id':x['request_id'],'whole_original_receipt':'requests/'+x['request_id']+'.json','complete_all_page_structure':x['structure_asset'],'literal_full_page_text':t,'stage_policy':'read literal report election/date; original link grouping or request purpose not authoritative; never admitted November counts'})
 (P/'periodic-report-assessments.json.gz').write_bytes(gzip.compress((json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0))
 extra=[]
 for f in sorted(P.glob('jobs-*.json')):
  for job in json.loads(f.read_bytes()):
   if any(k in job for k in ['constructor_evidence','constructor_inputs','constructor_parameters','observed_filename_constant','actual_version']) or 'constructor' in (job.get('literal_href','')+' '+str(job.get('purpose',''))):extra.append({'job_file':f.name,'complete_job':job})
 (P/'constructor-evidence-complete.json').write_text(json.dumps(extra,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
