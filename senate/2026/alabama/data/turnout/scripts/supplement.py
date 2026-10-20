#!/usr/bin/env python3
"""Source link-chain and exact rate witnesses, separate from candidate ranking."""
import pathlib,json,gzip,hashlib,urllib.parse
from html.parser import HTMLParser
from fractions import Fraction
from decimal import Decimal,ROUND_HALF_UP
from freeze import write
R=pathlib.Path(__file__).resolve().parents[1]
receipts=[json.loads(p.read_text()) for p in (R/'source/http').glob('*.receipt.json')];shared=json.loads((R/'source/original-receipts.json').read_text());htmls=[]
for r in receipts:
 b=gzip.decompress(b''.join((R/p['path']).read_bytes() for p in r['parts']))
 if 'text/html' in r['headers'].get('Content-Type',''):htmls.append((r['final_url'],r['original_sha256'],b))
for r in shared:
 b=gzip.decompress(pathlib.Path(r['shared_path']).read_bytes())
 if not b.startswith(b'%PDF'):htmls.append((r['final_url'],r['raw_sha256'],b))
class Links(HTMLParser):
 def __init__(self,url):super().__init__();self.url=url;self.links=[]
 def handle_starttag(self,t,attrs):
  if t=='a':
   for k,v in attrs:
    if k=='href':self.links.append({'href_literal':v,'resolved_url':urllib.parse.urljoin(self.url,v),'html_line_1based':self.getpos()[0],'html_column_0based':self.getpos()[1],'start_tag':self.get_starttag_text()})
links=[]
for url,h,b in htmls:
 parser=Links(url);parser.feed(b.decode('utf-8',errors='replace'))
 for x in parser.links:links.append({'parent_url':url,'parent_original_sha256':h,**x})
chains=[]
for r in receipts:
 chain=[l for l in links if l['resolved_url']==r['requested_url']]
 chains.append({'requested_url':r['requested_url'],'final_url':r['final_url'],'original_sha256':r['original_sha256'],'status':r['status'],'observed_parent_links':chain,'route_qualification':'verified exact parent href' if chain else ('direct Census alternative/API recovery; no SOS hyperlink asserted' if 'census.gov' in r['requested_url'] else 'direct official authority entry page')})
write(R/'source/download-chains.json',json.dumps(chains,indent=2)+'\n')
bc=json.loads((R/'ballot-registration-controls.json').read_text());rates=[]
for r in bc['county_rows']+bc['statewide']:
 reg=r['registered_voters'];ballots=r['ballots_cast'];absentee=r['absentee_ballots'];out={'year':r['year'],'county':r['county'],'county_fips':r['county_fips'],'denominator_scope':r['registration_status_scope'],'report_ballots':ballots,'report_registered_voters':reg,'report_absentee_ballots':absentee,'turnout_exact':str(Fraction(ballots,reg)),'absentee_fraction_exact':str(Fraction(absentee,ballots)),'source_text':r['source_text'],'source_line_1based':r['source_line_1based']}
 for name,num,den,printed in [('turnout',ballots,reg,r['printed_turnout_pct']),('absentee',absentee,ballots,r['printed_absentee_pct'])]:
  d=Decimal(printed.rstrip('%'));precision=-d.as_tuple().exponent;computed=(Decimal(num)*100/Decimal(den)).quantize(Decimal(1).scaleb(-precision),rounding=ROUND_HALF_UP)
  out[name+'_printed_pct']=printed;out[name+'_recomputed_pct_at_printed_precision']=str(computed)+'%';out[name+'_printed_matches_integer_ratio']=computed==d
 rates.append(out)
write(R/'turnout-rates.json',json.dumps({'rows':rates,'scope':'Ratios use separate official ballot reports only; no eligible-population rate, exact registration extract date, candidate participation allocation or 2026 forecast is inferred.'},indent=2)+'\n')
print('observed child chains',sum(bool(c['observed_parent_links']) for c in chains),'rate rows',len(rates),'printed rate mismatches',[(r['year'],r['county'],r['turnout_printed_matches_integer_ratio'],r['absentee_printed_matches_integer_ratio']) for r in rates if not r['turnout_printed_matches_integer_ratio'] or not r['absentee_printed_matches_integer_ratio']])
