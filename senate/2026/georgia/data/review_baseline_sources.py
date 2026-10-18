#!/usr/bin/env python3
"""Coordinator independently checks serialized A/B rows against original JSON pointers."""
from pathlib import Path
import collections,csv,datetime,gzip,hashlib,io,json,math
D=Path(__file__).resolve().parent;B=D/'baselines';S=D/'turnout/source'
def rows(p):
 b=p.read_bytes();return list(csv.DictReader(io.StringIO((gzip.decompress(b) if p.suffix=='.gz' else b).decode())))
def label(v):return next((x['text'] for x in v or [] if x.get('languageId')=='en'),' | '.join(x['text'] for x in v or []))
def ptr(o,p):
 for k in p.strip('/').split('/'):o=o[int(k)] if isinstance(o,list) else o[k]
 return o
def value(v):return '' if v is None else str(v)
def main():
 cache={};source_hashes={};checks=0
 def source(sid):
  if sid not in cache:
   m=json.loads((S/(sid+'.http.json')).read_text());z=(D/'turnout'/m['asset']).read_bytes();b=gzip.decompress(z);assert hashlib.sha256(b).hexdigest()==m['raw_sha256'] and hashlib.sha256(z).hexdigest()==m['stored_sha256'];cache[sid]=json.loads(b);source_hashes[sid]=m['raw_sha256']
  return cache[sid]
 county=rows(D/'county-baselines.csv');native=rows(B/'native-baselines.csv.gz');method=rows(B/'method-baselines.csv.gz');assert len(county)==795 and len(native)==2701 and len(method)==13984;totals=collections.defaultdict(collections.Counter)
 for r in county+native:
  o=source(r['source_id']);x=ptr(o,r['source_pointer']);opts=x['summaryResults']['ballotOptions'] if r['unit_level']=='county' else x['ballotOptions'];a=next(c for c in opts if label(c['name'])==r['A_name']);b=next(c for c in opts if label(c['name'])==r['B_name']);assert label(a['name']).endswith('(Dem)') and label(b['name']).endswith('(Rep)');assert value(a['voteCount'])==r['A'] and value(b['voteCount'])==r['B'];assert r['A_party']=='Dem' and r['B_party']=='Rep';checks+=4
  pair=None if a['voteCount'] is None or b['voteCount'] is None else a['voteCount']+b['voteCount'];assert value(pair)==r['pair_votes'];checks+=1
  named=[v['voteCount'] for v in opts if r['election_key']!='2024NovGen' or label(v['name']) in ['Donald J. Trump (Rep)','Kamala D. Harris (Dem)','Chase Oliver (Lib)','Jill Stein (Grn)']];nv=None if None in named else sum(named);allv=None if any(v['voteCount'] is None for v in opts) else sum(v['voteCount'] for v in opts);assert value(nv)==r['named_valid_option_votes'] and value(allv)==r['source_alloption_votes'];checks+=2
  if r['unit_level']=='county':
   assert r['additional_qualified_writeins']=='' if r['election_key']=='2024NovGen' else True
   totals[r['election_key']]['A']+=a['voteCount'];totals[r['election_key']]['B']+=b['voteCount'];totals[r['election_key']]['named']+=nv
 for r in method:
  o=source(r['source_id']);a=ptr(o,r['A_pointer']);b=ptr(o,r['B_pointer']);assert value(a['voteCount'])==r['A'] and value(b['voteCount'])==r['B'];assert a['groupId']==b['groupId']==r['group_GUID'] and label(a['groupName'])==label(b['groupName'])==r['group_name'];checks+=4
  pair=None if a['voteCount'] is None or b['voteCount'] is None else a['voteCount']+b['voteCount'];assert value(pair)==r['pair_votes'];checks+=1
 assert dict(totals)=={'2024NovGen':{'A':2548017,'B':2663117,'named':5250047},'2020NovGen':{'A':2374519,'B':2462617,'named':4952175},'2021JanFedRun':{'A':2269923,'B':2214979,'named':4484902},'2022NovGen':{'A':1946117,'B':1908442,'named':3935924},'2022DecGenRun':{'A':1820633,'B':1721244,'named':3541877}}
 result={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_county_entities':len(cache),'county_rows':795,'native_rows':2701,'method_rows':13984,'direct_original_field_checks':checks,'state_controls':totals,'scope':'A/B party identities are verified display-name semantics; raw party IDs/abbreviations remain in original long rows. Direct pointers preserve source differences and nulls; complete qualified write-ins remain separate858 statewide, never allocated.'}
 p=D/'coordinator-baseline-source-review.json'
 if p.exists():
  old=json.loads(p.read_text())
  if {k:v for k,v in old.items() if k!='checked_utc'}=={k:v for k,v in result.items() if k!='checked_utc'}:result['checked_utc']=old['checked_utc']
 p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
