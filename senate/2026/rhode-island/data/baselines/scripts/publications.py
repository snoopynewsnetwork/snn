"""Parse original municipality HTML and Board cells independently of peer tables."""
import collections,gzip,html,io,json,re,xml.etree.ElementTree as ET,zipfile
from common import *
TITLES=['Presidential Electors For:','Senator in Congress','Governor']
def text(s):return html.unescape(re.sub(r'<[^>]*>','',s)).strip()
def columns(r):return {re.sub(r'\d','',c['cell']):c['value'] for c in r['cells']}
def html_parse(ident):
    b=body(ident);s=b.decode('utf-8');out=[]
    for tb in re.finditer(r'<table\b[^>]*summary="([^"]+)"[^>]*>.*?</table>',s,re.S):
        title=html.unescape(tb[1])
        if title not in TITLES:continue
        for rm in re.finditer(r'<tr\b[^>]*>.*?</tr>',tb[0],re.S):
            cells=re.findall(r'<td\b[^>]*>(.*?)</td>',rm[0],re.S)
            if not cells:continue
            assert len(cells)==4
            methods=[text(v) for v in re.findall(r'<li>(.*?)</li>',cells[1],re.S)]
            start=len(s[:tb.start()+rm.start()].encode())
            out.append({'input':ident,'raw_sha256':sha(b),'contest':title,'candidate_literal':text(cells[0]),
                'party_literal':next(iter(re.findall(r'\(([^()]+)\)',text(cells[0]))),None),
                'votes':int(text(cells[2]).replace(',','')),'display_pct':text(cells[3]),'method_literals':methods,
                'method_votes':[int(v.rsplit(':',1)[1].replace(',','').strip()) for v in methods],
                'byte_start':start,'byte_end':start+len(rm[0].encode()),'line':s[:tb.start()+rm.start()].count('\n')+1})
    hierarchy=[]
    for m in re.finditer(r'<a\b[^>]*href="([^"]+/general_election/([^/]+)/([0-9]{4})/)"[^>]*>(.*?)</a>',s,re.S):
        label=text(m[4]);hierarchy.append({'input':ident,'url':'https://www.ri.gov'+m[1],
            'municipality_slug':m[2],'source_code':m[3],'label_literal':label,
            'byte_start':len(s[:m.start()].encode()),'byte_end':len(s[:m.end()].encode())})
    return out,hierarchy
def candidate_without_party(s):
    return re.sub(r'\s*\([^()]*\)\s*$','',s).strip()
def main():
    roots=read_gz('witness/root-selected.jsonl.gz');hrows=[];hier=[]
    selected_ids=[r['id'] for r in inputs().values() if '-town-' in r['id']]+['ri-2024-general-old-authority','ri-2020-observed-state-summary','ri-2022-observed-historical-seed']
    for ident in selected_ids:
        a,b=html_parse(ident);hrows+=a;hier+=b
    write_gz('witness/html-selected-rows.jsonl.gz',hrows)
    write_json('witness/municipal-child-links.json',hier)
    maps={};checks=[];native=[];board=[];stats=[]
    for y in [2020,2022,2024]:
        mapping={}
        for h in hier:
            if h['input'].startswith(str(y)+'-town-'):
                assert h['source_code'] not in mapping
                mapping[h['source_code']]=h
        maps[y]=mapping
        rs=[r for r in roots if r['year']==y]
        # Code identity is only within this source/year, corroborated by original child links.
        codes=list(dict.fromkeys(r['source_code'] for r in rs))
        for c in codes:
            cr=[r for r in rs if r['source_code']==c];names=list(dict.fromkeys(r['source_name'].strip() for r in cr));assert len(names)==1
            h=mapping.get(c)
            if h:
                parent=h['municipality_slug'];parent_kind='municipality'
            else:
                assert all(n.startswith('Federal Precinct #') for n in names),(y,c,names)
                parent='state-admin-'+c;parent_kind='state_administrative_federal'
            native.append({'year':y,'source_code':c,'source_name':names[0],'parent_key':parent,'parent_kind':parent_kind,
                'child_html':h,'roles_literal': {'limited':'Limited' in names[0], 'presidential':'Presidential' in names[0],
                'federal':'Federal Precinct' in names[0], 'central':'CENTRAL' in (h['label_literal'] if h else '').upper()},
                'physical_precinct_approved':False,'current_2026_equivalence':None,
                'contests':{t:({'observed':True,'votes':sum(r['votes'] for r in cr if r['contest_title'].strip()==t),
                    'first_source_byte':min(r['byte_start'] for r in cr if r['contest_title'].strip()==t)})
                    if any(r['contest_title'].strip()==t for r in cr) else {'observed':False,'votes':None,'first_source_byte':None}
                    for t in (['Governor'] if y==2022 else TITLES[:2])}})
        wb=read_gz(f'witness/board{y}-xlsx-selected-cells.jsonl.gz')
        for row in wb:
            d=columns(row)
            if d.get('H') in TITLES:
                c=str(d['B']).zfill(4);matches=[r for r in rs if r['source_code']==c and r['contest_title'].strip()==d['H'] and r['candidate_name'].strip()==d.get('I')]
                assert len(matches)==1,(y,c,d)
                root=matches[0];nums=[int(d[v]) for v in ['C','D','E','F']]
                equal=nums==[root['votes']]+root['methods'][:3]
                board.append({'year':y,'member':row['member'],'row':row['row'],'source_code':c,'contest':d['H'],
                    'candidate':d['I'],'party':d.get('G'),'source_name':d.get('A'),'numbers':nums,
                    'root_byte':root['byte_start'],'votes_first3_equal':equal,'party_equal':d.get('G')==root['party'].strip(),
                    'district_name_xlsx':d.get('J'),'district_name_root':root['district_name']})
            elif d.get('H','').startswith(('REGISTERED VOTERS','BALLOTS CAST','VOTER TURNOUT')):
                stats.append({'year':y,'source_code':str(d['B']).zfill(4),'source_name':d.get('A'),'statistic':d['H'],
                    'total':int(d['C']) if d.get('C') is not None else None,
                    'methods':[int(d[x]) if d.get(x) is not None else None for x in ['D','E','F']],
                    'member':row['member'],'row':row['row'],'candidate_field':d.get('I'),'party_field':d.get('G')})
        for slug in dict.fromkeys(h['municipality_slug'] for h in mapping.values()):
            children=[c for c,h in mapping.items() if h['municipality_slug']==slug]
            for t in (['Governor'] if y==2022 else TITLES[:2]):
                rr=[r for r in rs if r['source_code'] in children and r['contest_title'].strip()==t]
                for name in dict.fromkeys(r['candidate_name'].strip() for r in rr):
                    rrs=[r for r in rr if r['candidate_name'].strip()==name]
                    hh=[r for r in hrows if r['input']==f'{y}-town-{slug}' and r['contest']==t and candidate_without_party(r['candidate_literal'])==name]
                    assert len(hh)==1,(y,slug,t,name)
                    v=[sum(r['votes'] for r in rrs)]+[sum(r['methods'][i] for r in rrs) for i in range(3)]
                    checks.append({'year':y,'municipality':slug,'contest':t,'candidate':name,'root_numbers':v,
                        'html_numbers':[hh[0]['votes']]+hh[0]['method_votes'],'equal':v==[hh[0]['votes']]+hh[0]['method_votes']})
    # The Board retains statistics for four federal contexts in 2022 without Governor rows.
    # These are observed statistics and an unavailable contest, never invented zero votes.
    for s in stats:
        if not any(n['year']==s['year'] and n['source_code']==s['source_code'] for n in native):
            assert s['source_name'].startswith('Federal Precinct #'),s
            native.append({'year':s['year'],'source_code':s['source_code'],'source_name':s['source_name'],
                'parent_key':'state-admin-'+s['source_code'],'parent_kind':'state_administrative_federal','child_html':None,
                'roles_literal':{'limited':False,'presidential':False,'federal':True,'central':False},
                'physical_precinct_approved':False,'current_2026_equivalence':None,
                'source_scope':'Board statistic-only context; selected contest absent from fixed-width root',
                'contests':{'Governor':{'observed':False,'votes':None,'first_source_byte':None}}})
    write_json('extracts/native-inventory.json',native)
    write_json('extracts/municipal-html-reconciliation.json',checks)
    write_gz('extracts/board-root-reconciliation.jsonl.gz',board)
    write_json('extracts/native-statistics.json',stats)
    write_json('extracts/publication-controls.json',{'hierarchy_links':{str(y):len(maps[y]) for y in maps},
        'html_candidate_method_checks':len(checks),'html_disagreements':[c for c in checks if not c['equal']],
        'board_candidate_method_checks':len(board),'board_disagreements':[c for c in board if not c['votes_first3_equal'] or not c['party_equal']],
        'statistic_controls':[{'year':y,'statistic':t,'rows':len([s for s in stats if s['year']==y and s['statistic']==t]),
            'sum':sum(s['total'] for s in stats if s['year']==y and s['statistic']==t),'source_scope':'native XLSX observed rows only, not missing zeros'}
            for y in [2020,2022,2024] for t in dict.fromkeys(s['statistic'] for s in stats if s['year']==y)]})
    print('native contexts',len(native),'Board records',len(board),'municipal candidate/method checks',len(checks))
if __name__=='__main__':main()
