"""Independent whole-field check against original source character slices."""
from pathlib import Path
import collections,gzip,html,json,re
from freeze import S,R,load,sha
from extract import text,write
def main():
    receipts={x['id']:x['receipt'] for x in load(R/'historical-source-receipts.json')}
    originals={k:gzip.decompress((S/'data/news'/v['asset']).read_bytes()).decode('utf-8-sig') for k,v in receipts.items() if '.html' in v['url']}
    rows=load(S/'data/turnout/extracts/candidate-rows.jsonl.gz');tables=load(S/'data/turnout/extracts/tables.json');checks=0
    table_headers={(v['source_id'],v['table_start']):v['headers'] for v in tables}
    for row in rows:
        t=originals[row['source_id']];raw=t[row['row_start']:row['row_end']]
        assert raw.startswith('<tr') and raw.endswith('</tr>');checks+=1
        cs=re.findall(r'<td\b[^>]*>.*?</td>',raw,re.S)
        assert len(cs)==len(row['cells']);checks+=1
        fields={}
        for i,(c,v) in enumerate(zip(cs,row['cells'])):
            lm=re.search(r'data-label="([^"]+)"',c)
            label=lm[1] if lm else table_headers[row['source_id'],row['table_start']][i]
            value=html.unescape(re.sub('<[^>]+>','',c)).strip()
            assert v['raw_cell_html']==c and v['column']==i and v['key']==label and v['text']==value;checks+=4
            fields[label]=value
        assert fields==row['raw_fields'];checks+=1
        assert fields.get('Candidate',fields.get('Candidate Name'))==row['candidate'] and fields.get('Party',fields.get('Party Name'))==row['party'];checks+=2
        for k,v in row['numeric'].items():
            expected=int(fields[k].replace(',','')) if k in fields else None
            assert v==expected;checks+=1
    for table in tables:
        t=originals[table['source_id']];raw=t[table['table_start']:table['table_end']]
        assert raw.startswith('<table') and raw.rstrip().endswith('</table>');checks+=1
        hs=[html.unescape(re.sub('<[^>]+>','',x)).strip() for x in re.findall(r'<th\b[^>]*>.*?</th>',raw,re.S)]
        assert hs==table['headers'];checks+=1
        assert len(re.findall(r'<tr>\s*<td',raw,re.S))==table['rows'];checks+=1
    scopes=[]
    for sid,year,off,n,total in [('sos-2024-general-report',2024,'USSenator',530,500606),('sos-2024-general-report',2024,'PresidentandVicePresident',533,511697),('sos-observed-2020-general-report',2020,'USSenator',436,490935),('sos-observed-2020-general-report',2020,'PresidentandVicePresident',439,504010),('official-2022-report',2022,'RepresentativeinCongress',516,321649)]:
        t=originals[sid];found=[];sums=collections.Counter()
        pat=r'<h4 class="electiondistrict-title '+off+r' ([^"]+)">(.*?)</h4>\s*<table[^>]*>(.*?)</table>'
        for m in re.finditer(pat,t,re.S):
            found.append(m[1]);ff=[]
            for rm in re.finditer(r'<tr>(.*?)</tr>',m[3],re.S):
                fields={k:html.unescape(re.sub('<[^>]+>','',v)).strip() for k,v in re.findall(r'<td data-label="([^"]+)">(.*?)</td>',rm[1],re.S)}
                if fields:sums[fields.get('Candidate',fields.get('Candidate Name'))]+=int(fields['Total Votes'].replace(',',''));ff.append(fields)
            assert ff
        assert len(found)==len(set(found))==n and sum(sums.values())==total;checks+=3
        frozen=[x['native_key'] for x in tables if x['source_id']==sid and x['office_key']==off and x['view']=='byelectiondist']
        assert found==frozen;checks+=1
        scopes.append(dict(source=sid,year=year,office=off,native_count=n,named_total=total,candidate_totals=dict(sums),ordered_keys=found))
    # No guessed year-to-year or DOM/current ID joins.
    write('original-field-audit.json',dict(status='pass',checks=checks,tables=len(tables),candidate_rows=len(rows),source_partitions=scopes,all_original_raw_cells_headers_parties_nulls_positions_checked=True,current_joins_approved=False))
    print('PASS',checks,'independent whole-field original checks')
if __name__=='__main__':main()
