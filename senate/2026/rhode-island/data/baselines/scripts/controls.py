"""Board PDF state controls, native statistic coverage, and literal write-in sheets."""
import collections,gzip,html,json,re,subprocess
from common import *
from publications import columns
def main():
    roots=read_gz('witness/root-selected.jsonl.gz');out=[];state=[]
    for year,ident in [(2020,'board2020-pdf'),(2022,'board2022-pdf'),(2024,'boe-2024-summary')]:
        s=gzip.decompress((BASE/'witness'/f'{ident}.layout.txt.gz').read_bytes()).decode()
        panels={};pages=s.split('\f');active=None
        for pi,page in enumerate(pages[:2],1):
            for li,line in enumerate(page.splitlines(),1):
                title=line.strip()
                if title in ['Senator in Congress','Presidential Electors For:','Governor']:
                    active=title;panels.setdefault(title,[])
                elif title.startswith(('Representative in Congress','Senator in General Assembly','Lieutenant Governor')):active=None
                if active:
                    m=re.match(r'^(.*?)\s{2,}([\d,]+)\s+(?:(\d*\.\d+%?)\s+)?([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$',line)
                    if m:
                        row={'input':ident,'year':year,'page':pi,'line':li,'raw_line':line,'label':m[1].strip(),
                             'total':int(m[2].replace(',','')),'pct':m[3],
                             'methods':[int(m[i].replace(',','')) for i in [4,5,6]],'contest':active}
                        panels[active].append(row);out.append(row)
        for title,rs in panels.items():
            if year==2022 and title!='Governor':continue
            rr=[r for r in roots if r['year']==year and r['contest_title'].strip()==title]
            if not rr:continue
            checks=[]
            for name in dict.fromkeys(r['candidate_name'].strip() for r in rr):
                if name.lower()=='write-in':matches=[r for r in rs if r['label'].upper().startswith('WRITE-IN')]
                else:matches=[r for r in rs if r['label'].startswith(name)]
                assert len(matches)==1,(year,title,name,matches)
                c=[r for r in rr if r['candidate_name'].strip()==name];v=[sum(r['votes'] for r in c)]+[sum(r['methods'][i] for r in c) for i in range(3)]
                p=matches[0];checks.append({'candidate':name,'root':v,'pdf':[p['total']]+p['methods'],'equal':v==[p['total']]+p['methods'],'page':p['page'],'line':p['line']})
            def stat(prefix):
                rows=[r for r in rs if r['label'].replace(' ','').lower().startswith(prefix.replace(' ','').lower())]
                assert len(rows)<=1
                return rows[0] if rows else None
            over=stat('Over');under=stat('Under');published=stat('Contest Totals');fv=sum(r['votes'] for r in rr)
            denominator=published['total'] if published else fv+over['total']+under['total']
            assert denominator==fv+over['total']+under['total']
            state.append({'year':year,'contest':title,'input':ident,'candidate_generic_total':fv,'candidate_checks':checks,
                'overvotes':over,'undervotes':under,'contest_ballots':denominator,
                'denominator_basis':'published Contest Totals' if published else 'derived from published candidate votes + over + under',
                'certification_status':'OFFICIAL RESULTS' if year in [2022,2024] else 'Board-published summary; separate signed certification not acquired',
                'signed_certification_acquired':False})
    write_json('extracts/board-pdf-selected-lines.json',out);write_json('extracts/state-denominator-controls.json',state)
    stats=json.loads((BASE/'extracts/native-statistics.json').read_text());inventory=json.loads((BASE/'extracts/native-inventory.json').read_text());coverage=[]
    for year in [2020,2022,2024]:
        codes={r['source_code'] for r in inventory if r['year']==year}
        for title in ['REGISTERED VOTERS - TOTAL','BALLOTS CAST - TOTAL','BALLOTS CAST - BLANK']:
            rr=[r for r in stats if r['year']==year and r['statistic']==title];present={r['source_code'] for r in rr}
            coverage.append({'year':year,'statistic':title,'rows':len(rr),'sum_observed':sum(r['total'] for r in rr) if rr else None,
                'missing_native_codes':sorted(codes-present),'extra_statistic_only_codes':sorted(present-codes),
                'definition':'Source historical election statistic; no active/inactive breakdown or registration snapshot date beyond publication clock is asserted'})
    write_json('extracts/statistic-coverage.json',coverage)
    # Each original workbook sheet is a municipality. Keep all literal D/E Senate rows, not a cleaned candidate universe.
    wi=read_gz('witness/board2024-writeins-xlsx-selected-cells.jsonl.gz');sheets=collections.defaultdict(list)
    for r in wi:sheets[r['member']].append(r)
    details=[];totals=[]
    for member,rs in sheets.items():
        names=[columns(r).get('A') for r in rs if r['row']==1];assert len(names)==1
        town=names[0];h=[columns(r) for r in rs if r['row']==3];assert len(h)==1
        assert 'Senator' in str(h[0].get('D')),(town,h)
        cells=[]
        for r in rs:
            d=columns(r)
            if 'D' in d or 'E' in d:
                cells.append({'member':member,'row':r['row'],'municipality_literal':town,'name_cell':f"D{r['row']}",
                    'votes_cell':f"E{r['row']}",'name_literal':d.get('D'),'votes_literal':d.get('E'),
                    'name_cell_present':'D' in d,'votes_cell_present':'E' in d})
        details+=cells
        header=next((c for c in cells if c['row']==4),None)
        printed=[c for c in cells if c['name_literal'] and c['name_literal'].strip().lower()=='total']
        ds=[c for c in cells if c['row']>4 and c['name_literal'] and c['name_literal'].strip().lower()!='total' and c['votes_literal'] is not None]
        nums=[int(c['votes_literal']) for c in ds]
        generic=[]
        for x in json.loads((BASE/'extracts/parent-baselines.json').read_text()):
            if x['election']=='2024-senate' and x['parent_key'].replace('_',' ').lower()==town.lower():
                generic=[c['votes'] for c in x['candidates'] if c['party_raw'].strip()=='NON']
        assert len(generic)==1,(town,generic)
        totals.append({'municipality_literal':town,'member':member,'header_total':int(header['votes_literal']) if header and header['votes_literal'] else None,
            'printed_footer_totals':[int(c['votes_literal']) for c in printed],'literal_detail_sum':sum(nums),
            'literal_detail_rows':len(ds),'generic_municipal':generic[0],
            'detail_minus_generic':sum(nums)-generic[0],
            'interpretation':'Literal strings and counts; no deduplication, legal eligibility, generic-to-named equivalence, or native allocation'})
    write_json('extracts/2024-senate-writein-literal-cells.json',details)
    write_json('extracts/2024-senate-writein-reconciliation.json',{'municipalities':totals,
        'header_sum':sum(x['header_total'] or 0 for x in totals),'detail_sum':sum(x['literal_detail_sum'] for x in totals),
        'municipal_generic_sum':sum(x['generic_municipal'] for x in totals),'disagreements':[x for x in totals if x['detail_minus_generic']],
        'state_generic':sum(r['votes'] for r in roots if r['year']==2024 and r['contest_title'].strip()=='Senator in Congress' and r['party'].strip()=='NON'),
        'missing_eligible_named_writein_universe':True})
    print('PDF state controls',len(state),'candidate checks',sum(len(x['candidate_checks']) for x in state),'writein municipality sheets',len(totals))
if __name__=='__main__':main()
