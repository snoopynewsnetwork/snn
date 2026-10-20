#!/usr/bin/env python3
"""Original-first extraction. Reads pinned complete CSV/HTML entities, never helper/peer tables."""
import base64,csv,gzip,hashlib,io,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
STATE=HERE.parents[1]
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def gzjsonl(p,rs): p.write_bytes(gzip.compress((''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in rs)).encode(),mtime=0))
def load_original(id):
 ref=next(x for x in json.loads((HERE/'source/pinned-originals.json').read_text()) if x['id']==id)
 rp=HERE/ref['receipt_path'];assert sha(rp.read_bytes())==ref['receipt_sha256']
 replay=ref.get('offline_replay')
 if replay:
  assert sha((HERE/replay['receipt_path']).read_bytes())==replay['receipt_sha256'];b=(HERE/replay['body_path']).read_bytes();assert sha(b)==replay['stored_sha256']
 else:
  b=(STATE/ref['body_path']).read_bytes();assert sha(b)==ref['stored_sha256']
 raw=gzip.decompress(b);assert sha(raw)==ref['raw_sha256'];return raw,ref

def rank(rs):
 ordered=sorted(rs,key=lambda x:(-x['reported_candidate_writein_votes'],x['source_record']))
 total=sum(x['reported_candidate_writein_votes'] for x in ordered);cum=0
 for i,r in enumerate(ordered,1):
  cum+=r['reported_candidate_writein_votes'];r.update(rank=i,cumulative_votes=cum,weight_numerator=r['reported_candidate_writein_votes'],weight_denominator=total)
 k=next(i for i,r in enumerate(ordered,1) if 5*r['cumulative_votes']>=4*total)
 def stat(n): return {'count':n,'votes':ordered[n-1]['cumulative_votes'] if n else 0,'denominator':total}
 return {'total':total,'count':len(rs),'top15':stat(min(15,len(rs))),'minimum80':dict(stat(k),preceding=stat(k-1),crossing_key=ordered[k-1]['key'],crossing_label=ordered[k-1]['label'],crossing_parent=ordered[k-1].get('parent_label'),remainder_count=len(rs)-k,remainder_votes=total-ordered[k-1]['cumulative_votes']), 'order':ordered}

def extract(year):
 raw,ref=load_original(f'elect-{year}-senate-linked-csv')
 html,href=load_original(f'elect-{year}-senate-historical')
 h=html.decode('utf-8');m=re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',h)
 obj=json.loads(m.group(1));dump(HERE/f'extracts/{year}-complete-next-data.json',obj)
 contest=obj['props']['pageProps']['contest'];cid=contest['id']
 text=raw.decode('utf-8-sig');lines=text.splitlines(keepends=True);reader=csv.reader(io.StringIO(text,newline=''))
 rows=[];previous=0;offset=len(raw)-len(text.encode('utf-8'));parent=None
 for pos,cells in enumerate(reader,1):
  endline=reader.line_num;chunk=''.join(lines[previous:endline]).encode();start=offset;offset+=len(chunk)
  r={'source_id':ref['id'],'source_record':pos,'physical_line_start':previous+1,'physical_line_end':endline,'byte_start':start,'byte_end_exclusive':offset,'raw_row_utf8':chunk.decode(),'cells':cells}
  previous=endline
  if pos<=2: r['level']='header' if pos==1 else 'party_header'
  else:
   level,label=cells[:2];assert level in ['State','Locality','Precinct']
   r.update(level=level,label=label,key=f'va:{cid}:csv-record:{pos:04d}')
   if level=='Locality': parent=r
   if level=='Precinct':
    assert parent is not None
    code=re.match(r'^(.*?) - ',label)
    prov=bool(re.search(r'\bprovisional[s]?\b',label,re.I));absentee='absentee' in label.lower()
    r.update(parent_key=parent['key'],parent_label=parent['label'],source_native_id=None,literal_label_code=code.group(1) if code else None,method_id=None,method_scope='not separately published in CSV',administrative_case='provisional label' if prov else 'central absentee label' if absentee else 'unresolved precinct/reporting label',geometry_status='not established',current_2026_identity='unavailable')
   r['counts']={str(j):int(v) if re.fullmatch(r'\d+',v) else None for j,v in enumerate(cells[2:],2)}
  rows.append(r)
 assert offset==len(raw)
 header=rows[0]['cells'];party=rows[1]['cells'];cols=[]
 for j,name in enumerate(header[2:],2):
  matches=[c for c in contest['candidates'] if c['displayName']==name]
  assert len(matches)==1,(year,name)
  c=matches[0];role='contest_total' if name=='Total Votes Cast' else 'under_vote_literal_unproved' if name=='Undervotes' else 'generic_writeins' if c['candidate']['pseudocandidate']=='ALL_OTHER_CANDIDATES' else 'named_candidate'
  cols.append({'column_index':j,'csv_label':name,'csv_party_label':party[j],'role':role,'full_original_candidate_object':c})
 vote_cols=[c['column_index'] for c in cols if c['role'] in ['named_candidate','generic_writeins']]
 for r in rows[2:]:
  assert all(v is not None for v in r['counts'].values())
  r['candidate_votes']={str(j):r['counts'][str(j)] for j in vote_cols}
  r['reported_candidate_writein_votes']=sum(r['candidate_votes'].values())
  assert r['reported_candidate_writein_votes']==r['counts'][str(header.index('Total Votes Cast'))]
  r.update(ballots_cast=None,registered_voters=None,blank_votes=None,over_votes=None,under_votes_literal=r['counts'].get(str(header.index('Undervotes'))) if 'Undervotes' in header else None,under_votes_semantics='unproved; not inferred from arithmetic',named_valid_writein_allocation=None)
 state=[r for r in rows if r['level']=='State'];parents=[r for r in rows if r['level']=='Locality'];native=[r for r in rows if r['level']=='Precinct'];assert len(state)==1 and len(parents)==133
 assert len({r['label'] for r in parents})==133
 balances=[]
 for p in parents:
  children=[r for r in native if r['parent_key']==p['key']];assert children
  for col in cols:
   j=str(col['column_index']);s=sum(r['counts'][j] for r in children);v=p['counts'][j]
   balances.append({'parent_key':p['key'],'parent_label':p['label'],'column_index':int(j),'label':col['csv_label'],'native_sum':s,'locality_value':v,'native_minus_locality':s-v})
 statewide=[]
 for col in cols:
  j=str(col['column_index']);s=sum(r['counts'][j] for r in native);ps=sum(r['counts'][j] for r in parents);v=state[0]['counts'][j]
  statewide.append({'column_index':int(j),'label':col['csv_label'],'role':col['role'],'native_sum':s,'locality_sum':ps,'csv_state':v,'html_nVotes':col['full_original_candidate_object']['nVotes'],'html_nVotesParty1':col['full_original_candidate_object']['nVotesParty1'],'native_minus_state':s-v,'locality_minus_state':ps-v})
 gzjsonl(HERE/f'extracts/{year}-all-original-rows.jsonl.gz',rows)
 result={'year':year,'contest_id':cid,'event':contest['event'],'full_original_source_ref':ref,'header':header,'party_header':party,'columns':cols,'page_status':{k:contest.get(k) for k in ['verifiedAt','publicNote','disclaimer','hasVoteChannels','isHideTotalBallots','ballotsCount','files']},'row_count_including_headers':len(rows),'native_count':len(native),'locality_count':len(parents),'city_count':sum(r['label'].endswith(' City') for r in parents),'state_controls':statewide,'locality_balances':balances,'nonzero_locality_residuals':[x for x in balances if x['native_minus_locality']],'native_ranking':rank(native),'locality_summary_ranking':rank(parents)}
 dump(HERE/f'extracts/{year}-contest.json',result)
 return result
if __name__=='__main__':
 for y in [2024,2020,2018]:
  r=extract(y);p=r['native_ranking'];print(y,r['native_count'],r['locality_count'],p['total'],p['top15'],p['minimum80'],'residuals',r['nonzero_locality_residuals'])
