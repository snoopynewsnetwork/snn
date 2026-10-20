"""Finite public current search from observed PD43 form and exact links.
This is research acquisition preparation, not a live collector.
"""
from pathlib import Path
from urllib.parse import urljoin,urlencode
import gzip,json
from bs4 import BeautifulSoup
O=Path(__file__).resolve().parent
def main():
 r=json.loads((O/'source/http/pd43-current-root.json').read_text());b=gzip.decompress((O/r['body']['path']).read_bytes());s=BeautifulSoup(b,'html.parser');form=s.select_one('#search_form_elections form');assert form and form.get('method','get').lower()=='get'
 opt=[o for o in form.select('select[name=office_id] option') if o.get_text(' ',strip=True)=='U.S. Senate'];assert len(opt)==1
 stage_select=next(x for x in form.select('select[name=stage]')if x.get('id')=='stageListForOffice'+opt[0]['value']);general=next(o for o in stage_select.select('option') if o.get('value')=='General')
 fields=dict(year_from='2026',year_to='2026',office_id=opt[0]['value'],stage=general['value']);assert form.select_one('[name=year_from]')and form.select_one('[name=year_to]')
 u=urljoin(r['final_url'],form['action'])+'?'+urlencode(fields)
 assert all(form.select_one('select[name='+n+'] option[value="2026"]')for n in ['year_from','year_to'])
 constructor=dict(parent=r['requested_url'],form_html=str(form),method='GET',action_literal=form['action'],query_fields=fields,office_option_raw=str(opt[0]),stage_select_raw=str(stage_select),stage_option_raw=str(general),year_selection='2026 selected from both observed year dropdowns',November_date_in_observed_dropdown=bool(form.select_one('select[name=date] option[value="2026-11-03"]')),current_contest_id=None,current_choices=None,November_returns_admitted=False)
 (O/'current-form-constructor.json').write_text(json.dumps(constructor,indent=2)+'\n')
 jobs=[dict(id='pd43-current-general-search',url=u,parent=r['requested_url'],literal_href=None,reason='actual observed GET form constructor; not an ENR endpoint')]
 for x in s.select('script[src]'):
  if 'electionstats.state.ma.us/js/'in x['src']:jobs.append(dict(id='pd43-current-script',url=urljoin(r['final_url'],x['src']),parent=r['requested_url'],literal_href=x['src'],reason='actual linked PD43 application script'))
 jobs += [dict(id='scotus-opinions-index',url='https://www.supremecourt.gov/opinions/slipopinions.aspx?Term=09',reason='actual official search result index link'),dict(id='law4-9',url='https://malegislature.gov/Laws/GeneralLaws/PartI/TitleI/Chapter4/Section9',reason='actual official search result'),dict(id='law50-2',url='https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter50/Section2',reason='actual official search result'),dict(id='senate-contests',url='https://www.senate.gov/about/origins-foundations/electing-appointing-senators/contested-senate-elections/',reason='actual Senate constitutional authority search result'),dict(id='regulation47',url='https://www.mass.gov/doc/950-cmr-47-early-voting-procedures/download',reason='actual official search result; 2020 version must not override later act')]
 (O/'current-probe-requests.json').write_text(json.dumps(jobs,indent=2)+'\n');print(dict(requests=len(jobs),form_fields=fields))
if __name__=='__main__':main()
