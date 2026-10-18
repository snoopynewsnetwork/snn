#!/usr/bin/env python3
"""Independent original-source membership proof without allocating write-ins."""
import csv,datetime,gzip,hashlib,json,re
from pathlib import Path
import fitz
D=Path(__file__).resolve().parent;ROOT=D.parent;NEWS=D/'news';W=D/'turnout/source'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 manifest={x['id']:x for x in json.loads((NEWS/'manifest.json').read_text())}
 def news(sid):
  m=manifest[sid];s=(NEWS/m['asset']).read_bytes();b=gzip.decompress(s);assert sha(s)==m['stored_sha256'] and sha(b)==m['raw_sha256'] and len(b)==m['bytes'];return b
 source=news('sos-2024-general-api-data-selected');d=json.loads(source);x=d['ballotItemWithBreakdown'];text=lambda arr:' | '.join(n['text'] for n in arr)
 ranked=sorted(x['breakdownResults'],key=lambda c:(-c['voteTotal'],text(c['locality']['name'])))
 assert len(ranked)==159 and sum(c['voteTotal'] for c in ranked)==5250047
 sums={text(a['name']):a['voteCount'] for a in x['summaryResults']['ballotOptions']}
 assert sorted(sums.values())==[18229,20684,2548017,2663117]
 fec=news('fec-2024-presidential-original');assert sha(fec)=='c99a431e08cb779002ebecb373cee54745c3b691df2f0b322f36688364f6d823'
 doc=fitz.open(stream=fec,filetype='pdf');assert len(doc)==9
 def ga(n):
  t=doc[n-1].get_text();m=re.search(r'(?ms)^GA\s*\n(.*?)^HI\s*$',t);assert m,n;return [int(v.replace(',','')) for v in re.findall(r'\d[\d,]*',m[1])]
 assert ga(2)==[37,30] and ga(3)==[2548017] and ga(4)==[20684,730,18229] and ga(5)==[2663117] and ga(6)==[61,5250905]
 named=sum(sums.values());extra=37+30+730+61;total=named+extra;assert extra==858 and total==5250905
 # The separately rendered SOS final qualified-writein list gives9names/sum858;
 # FEC is an independently retained complete federal compilation/state control.
 sources=[]
 for sid in ['liberty-archive-search','liberty-2024-summary-page','liberty-2024-summary-image-1','2024NovGen--liberty-county-ga']:
  m=json.loads((W/(sid+'.http.json')).read_text());s=(W/m['asset']).read_bytes() if (W/m['asset']).exists() else (W/(sid+'.body.gz')).read_bytes();b=gzip.decompress(s)
  assert sha(s)==m['stored_sha256'] and sha(b)==m['raw_sha256'] and len(b)==m['entity_bytes'];assert m['status']==200
  sources.append(dict(id=sid,metadata=str((W/(sid+'.http.json')).relative_to(ROOT)),sha256=sha(b),bytes=len(b),requested_url=m['url'],final_url=m['final_url']))
  if sid=='liberty-archive-search':assert '/m/newsflash/Archive/Item/359?arcId=712' in b.decode()
  if sid=='liberty-2024-summary-page':assert 'https://www.libertycountyga.com/ImageRepository/Document?documentId=2269' in b.decode()
  if sid=='liberty-2024-summary-image-1':assert sha(b)=='8e8d624d07a151a77cd1435bacc8fbb1a3cc0fe3163458129dfe2bb0b70171b3' and b==(D/'turnout/qa/liberty-2024-summary-p1.jpg').read_bytes()
  if sid=='2024NovGen--liberty-county-ga':
   local=json.loads(b);assert local['election']['ballotsCast']==23258 and local['election']['totalVoters']==36269;assert local['ballotItemWithBreakdown']['voteTotal']==23028
 liberty=next(c for c in ranked if text(c['locality']['name'])=='Liberty County');assert liberty['voteTotal']==9441+13459+75+53==23028
 membership=[text(c['locality']['name']) for c in ranked[:44]];threshold=(total*4+4)//5;previous=sum(c['voteTotal'] for c in ranked[:43]);fixed=sum(c['voteTotal'] for c in ranked[:44])
 assert threshold==4200724 and previous+extra==4200150<threshold and fixed==4222572>=threshold
 minimum_selected=min(c['voteTotal'] for c in ranked[:44]);other_outsiders=[c for c in ranked[44:] if text(c['locality']['name'])!='Liberty County'];outside_max=max(c['voteTotal'] for c in other_outsiders)+extra
 assert minimum_selected==23280 and 23258<minimum_selected and outside_max==23211<minimum_selected
 top15=sum(c['voteTotal'] for c in ranked[:15]);top15_gap=ranked[14]['voteTotal']-ranked[15]['voteTotal']
 evidence=D/'coordinator-evidence';evidence.mkdir(exist_ok=True);previews=[]
 for n in [2,4,6]:
  p=evidence/f'fec-2024-page{n}.png'
  if not p.exists():doc[n-1].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(str(p))
  previews.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes()),bytes=p.stat().st_size))
 result=dict(status='pass_exact44_membership_without_imputed_allocation',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),dispatch_acceptance=False,coordinator_visual_review='Actual Liberty original JPEG and complete FEC pages2/4/6 viewed; printed headers/counts and page bounds confirmed, not OCR-only inference.',scope='This proves the minimum cardinality and unique county membership under the retained final5250905 state control and compatible Liberty ballot ceiling. Final contract/native/peer review and coordinator acceptance remain separate.',named_four_total=named,complete_state_total=total,separate_qualified_writein_pool=extra,FEC_original_sha256=sha(fec),FEC_GA_rows={str(n):ga(n) for n in [2,3,4,5,6]},Liberty_source_chain=sources,Liberty_visual_controls=dict(source_status='Official and Complete',source_clock_literal='11/8/2024 5:19:49 PM',source_timezone=None,ballots=23258,registration=36269,named_four=23028,maximum_extra_valid_votes=230,additional_printed_DeLaCruz_West=[46,75],Sonski=1,Andre_McNeil_absent='unknown, not zero',scope='Ballot ceiling includes void/blank/unresolved/unknown; no category allocation or valid-zero inference.'),minimum80_integer_threshold=threshold,maximum_any43=previous+extra,minimum_fixed44=fixed,minimum_selected_named=minimum_selected,maximum_other_outsider=outside_max,maximum_Liberty_all_valid=23258,proven_membership=membership,dispatch_order_rule='Deterministic named-four descending source order within the proven44 set; full-candidate order remains unknown.',full_candidate_county_allocations_known=False,full_candidate_order_known=False,top15_named_votes=top15,top15_membership_proved=top15_gap>extra,top15_boundary_named_gap=top15_gap,top15_full_share_bounds=[top15/total,(top15+extra)/total],priority_full_votes_bounds=[fixed,fixed+extra],priority_full_share_bounds=[fixed/total,(fixed+extra)/total],previews=previews,november_geographic_or_reporting_crosswalk_approved=False)
 out=D/'coordinator-priority-membership-review.json'
 if out.exists():
  old=json.loads(out.read_text())
  if {k:v for k,v in old.items() if k!='checked_utc'}=={k:v for k,v in result.items() if k!='checked_utc'}:result['checked_utc']=old['checked_utc']
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['Liberty_source_chain','proven_membership','previews']},indent=2))
if __name__=='__main__':main()
